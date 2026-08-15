"""
Converts data/verified_examples.py into data/processed/train.jsonl, in the
chat-message format expected by trl's SFTTrainer (and compatible with most
managed fine-tuning APIs too, if you change your mind later).

Each training example is a (system, user, assistant) triple:
  - system: the same generation rules used in prompts/generation_prompt_v1.md
  - user:   a synthetic generation request matching this example's subject/
            grade/difficulty/format/topic
  - assistant: the tagged problem+solution output -- this is what we want the
            fine-tuned model to learn to produce

Run: python scripts/build_dataset.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.verified_examples import VERIFIED_EXAMPLES

SYSTEM_PROMPT = """You are an expert problem-setter for Uzbekistan district-stage subject \
olympiads (Fan Olimpiadalari Markazi style). Generate a NEW, ORIGINAL problem in Uzbek \
that matches the style, structure, and difficulty of real olympiad problems for the \
requested subject/grade/difficulty/format.

Rules:
- Never reuse, lightly reword, or reproduce any known/published olympiad problem.
- Match the requested subject, grade, and difficulty tier exactly.
- Provide a complete, step-by-step, mathematically/scientifically rigorous solution.
- format=mcq: exactly 4 choices (A-D), one correct. format=open: no choices, <answer> \
is the exact expected value (numeric, or a clearly-marked formula for physics).
- If a diagram is genuinely needed, describe it structurally, not as an image.
- Output using the exact tag format shown in examples: <subject> <grade> <difficulty> \
<format> <problem> <choices> (if mcq) <solution> <answer>"""


def build_request(ex: dict) -> str:
    return (
        f"Generate 1 new problem for:\n"
        f"- subject: {ex['subject']}\n"
        f"- grade: {ex['grade']}\n"
        f"- difficulty tier: {ex['difficulty']}\n"
        f"- format: {ex['format']}\n"
        f"- topic: {ex['topic']}"
    )


def build_output(ex: dict) -> str:
    lines = [
        f"<subject>{ex['subject']}</subject>",
        f"<grade>{ex['grade']}</grade>",
        f"<difficulty>{ex['difficulty']}</difficulty>",
        f"<format>{ex['format']}</format>",
        f"<has_diagram>{'true' if ex.get('has_diagram') else 'false'}</has_diagram>",
        f"<problem>{ex['problem']}</problem>",
    ]
    if ex["format"] == "mcq":
        letters = ["A", "B", "C", "D"]
        choices_str = "  ".join(f"{letters[i]}) {c}" for i, c in enumerate(ex["choices"]))
        lines.append(f"<choices>{choices_str}</choices>")
    lines.append(f"<solution>{ex['solution']}</solution>")
    if ex["format"] == "mcq":
        lines.append(f"<answer>{['A','B','C','D'][ex['correct_index']]}</answer>")
    else:
        lines.append(f"<answer>{ex['answer']}</answer>")
    return "\n".join(lines)


def load_verified_pool() -> list[dict]:
    """Auto-verified examples from scripts/solve_check.py, if any exist yet."""
    pool_path = Path(__file__).resolve().parent.parent / "data" / "verified_pool.jsonl"
    if not pool_path.exists():
        return []
    rows = []
    with pool_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tags = json.loads(line)
            # normalize solve_check.py's raw tag dict into the same shape as
            # verified_examples.py entries
            ex = {
                "subject": tags.get("subject", "Matematika"),
                "grade": int(tags.get("grade", 7)),
                "difficulty": tags.get("difficulty", "0.9"),
                "format": tags.get("format", "mcq"),
                "topic": tags.get("topic", "general"),
                "problem": tags["problem"],
                "solution": tags.get("solution", ""),
                "has_diagram": tags.get("has_diagram") == "true",
            }
            if ex["format"] == "mcq" and "choices" in tags:
                letters_pattern = re.findall(r"[A-D]\)\s*([^A-D]+?)(?=\s*[A-D]\)|$)", tags["choices"])
                ex["choices"] = [c.strip() for c in letters_pattern] if letters_pattern else [tags["choices"]]
                answer_letter = tags.get("answer", "A").strip()
                ex["correct_index"] = "ABCD".find(answer_letter) if answer_letter in "ABCD" else 0
            else:
                ex["answer"] = tags.get("answer", "")
            rows.append(ex)
    return rows


def main():
    out_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "train.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    all_examples = list(VERIFIED_EXAMPLES) + load_verified_pool()

    rows = []
    for ex in all_examples:
        rows.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_request(ex)},
                {"role": "assistant", "content": build_output(ex)},
            ]
        })

    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_subject = {}
    for ex in all_examples:
        by_subject[ex["subject"]] = by_subject.get(ex["subject"], 0) + 1

    print(f"Wrote {len(rows)} examples to {out_path}")
    print(f"  ({len(VERIFIED_EXAMPLES)} hand-curated + {len(all_examples) - len(VERIFIED_EXAMPLES)} from auto solve-check pool)")
    print("By subject:", by_subject)
    if len(rows) < 300:
        print(
            f"\nWARNING: {len(rows)} examples is well below the ~300-500/subject floor "
            "for a fine-tune to reliably beat prompting. This file is a real starting "
            "point, not yet a production training set -- keep feeding it verified "
            "generations from generate_batch.py + solve_check.py."
        )


if __name__ == "__main__":
    main()
