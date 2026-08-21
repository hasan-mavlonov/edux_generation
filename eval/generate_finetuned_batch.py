"""
Generates a batch of problems from the fine-tuned model (base + LoRA adapter),
saved in the exact same tagged format generate_batch.py produces. This means
you evaluate it with the SAME tool already used on Gemini's output:

    python eval/generate_finetuned_batch.py
    python scripts/solve_check.py data/raw/pending/<the file this just made>.txt

Whatever pass-rate solve_check.py reports is your real, comparable accuracy
number -- measured the same way, not a different yardstick.

Run this on the GPU box, where the base model + adapter both live.
"""
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

REPO_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(REPO_ROOT))
from scripts.build_dataset import SYSTEM_PROMPT

# --- adjust these ---
BASE_MODEL = "/root/autodl-tmp/models/models/Qwen--Qwen3-4B/snapshots/master"
ADAPTER_PATH = str(REPO_ROOT / "checkpoints" / "v1")  # match --output_dir from training
N_PER_REQUEST = 1
# ---------------------

# Spread across subject/grade/difficulty/format/topic, same spirit as generate_batch.py's mix
TEST_REQUESTS = [
    {"subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq", "topic": "algebra"},
    {"subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "open", "topic": "word problem"},
    {"subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "mcq", "topic": "geometry"},
    {"subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "open", "topic": "number theory"},
    {"subject": "Matematika", "grade": 7, "difficulty": "2.6", "format": "mcq", "topic": "combinatorics"},
    {"subject": "Matematika", "grade": 7, "difficulty": "2.6", "format": "open", "topic": "algebra, optimization"},
    {"subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq", "topic": "percentages"},
    {"subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "mcq", "topic": "algebraic identity"},
    {"subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "mcq", "topic": "logic gates"},
    {"subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "open", "topic": "number systems"},
    {"subject": "Informatika", "grade": 7, "difficulty": "1.5", "format": "mcq", "topic": "pseudocode, loops"},
    {"subject": "Informatika", "grade": 7, "difficulty": "1.5", "format": "open", "topic": "spreadsheet formulas"},
    {"subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "mcq", "topic": "color encoding"},
    {"subject": "Informatika", "grade": 7, "difficulty": "1.5", "format": "mcq", "topic": "bitwise operations"},
]


def build_request(req: dict) -> str:
    return (
        f"Generate {N_PER_REQUEST} new problem for:\n"
        f"- subject: {req['subject']}\n"
        f"- grade: {req['grade']}\n"
        f"- difficulty tier: {req['difficulty']}\n"
        f"- format: {req['format']}\n"
        f"- topic: {req['topic']}"
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

    outputs = []
    for i, req in enumerate(TEST_REQUESTS, 1):
        request_text = build_request(req)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": request_text},
        ]
        prompt_text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
            )
        generated = tokenizer.decode(
            out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
        )
        match = re.search(r"<subject>.*?</answer>", generated, re.DOTALL)
        clean = match.group(0) if match else generated
        outputs.append(clean)
        print(f"[{i}/{len(TEST_REQUESTS)}] {req['subject']} {req['difficulty']} {req['format']} -- generated")

    pending_dir = REPO_ROOT / "data" / "raw" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_path = pending_dir / f"finetuned_v1_{timestamp}.txt"
    out_path.write_text("\n\n".join(outputs), encoding="utf-8")

    print(f"\nSaved {len(outputs)} generations to {out_path}")
    print(f"Now run: python scripts/solve_check.py {out_path}")
    print("The pass rate it reports is your real accuracy number for this checkpoint.")


if __name__ == "__main__":
    main()
