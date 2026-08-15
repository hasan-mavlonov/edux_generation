"""
QLoRA fine-tune of Qwen3-8B on data/processed/train.jsonl.

Runs on any single CUDA GPU with >=24GB VRAM (RTX 3090/4090, A100, etc.) --
provider-agnostic, works the same on RunPod, Vast.ai, AutoDL, or a local box.

Usage:
    python training/train_lora.py \
        --data data/processed/train.jsonl \
        --output_dir ./checkpoints/edux-qwen3-8b-v1 \
        --epochs 3

Note: with only ~25 examples right now, this is a smoke test to confirm the
pipeline works end to end -- not a production run. Re-run with a bigger
train.jsonl once scripts/build_dataset.py has more verified data behind it.
"""
import argparse

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
import torch

MODEL_NAME = "Qwen/Qwen3-8B"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed/train.jsonl")
    p.add_argument("--output_dir", default="./checkpoints/edux-qwen3-8b-v1")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch_size", type=int, default=2)
    p.add_argument("--grad_accum", type=int, default=8)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--max_seq_len", type=int, default=2048)
    return p.parse_args()


def main():
    args = parse_args()

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=args.data, split="train")

    def format_example(example):
        text = tokenizer.apply_chat_template(
            example["messages"], tokenize=False, add_generation_prompt=False
        )
        return {"text": text}

    dataset = dataset.map(format_example)

    sft_config = SFTConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_seq_length=args.max_seq_len,
        logging_steps=5,
        save_strategy="epoch",
        bf16=True,
        report_to="none",
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=dataset,
        processing_class=tokenizer,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"\nDone. LoRA adapter saved to {args.output_dir}")
    print("Merge with base model or load with PeftModel for inference.")


if __name__ == "__main__":
    main()
