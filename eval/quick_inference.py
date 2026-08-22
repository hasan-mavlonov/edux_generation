"""
Loads the base model + the smoke-test LoRA adapter and generates one sample
problem, so you can actually look at what it produces. Run this on the
AutoDL box, where both the base model and the adapter checkpoint live.

This is NOT an evaluation -- 309 examples / 1 epoch is nowhere near enough
to judge quality from. Use this to sanity-check the shape of the output
(does it follow the tag format, is it in Uzbek, does it look like a real
problem at all), not to judge correctness.

Usage: python eval/quick_inference.py
"""
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.build_dataset import SYSTEM_PROMPT  # reuse the exact same system prompt used in training

BASE_MODEL = "/root/autodl-tmp/models/models/Qwen--Qwen3-1.7B/snapshots/master"
ADAPTER_PATH = str(REPO_ROOT / "checkpoints" / "smoke-test")

TEST_REQUEST = (
    "Generate 1 new problem for:\n"
    "- subject: Matematika\n"
    "- grade: 7\n"
    "- difficulty tier: 0.9\n"
    "- format: mcq\n"
    "- topic: algebra"
)


def main():
    print(f"Loading base model from {BASE_MODEL} ...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, dtype=torch.bfloat16, device_map="auto"
    )

    print(f"Loading LoRA adapter from {ADAPTER_PATH} ...")
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TEST_REQUEST},
    ]
    prompt_text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

    print("\nGenerating...\n")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=400,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )

    generated = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )
    print("=" * 60)
    print("REQUEST:", TEST_REQUEST.splitlines()[-1])
    print("=" * 60)
    print(generated)
    print("=" * 60)


if __name__ == "__main__":
    main()
