"""
Independent solve-check. For every problem in a raw generated_batch file, this
asks the model to solve it FRESH (no access to the generation-time answer),
compares the result to the stated answer, and only appends matches to
data/verified_pool.jsonl.

v2: fixes a bug where MCQ answers were compared as raw letters against the
fresh solve's computed value, causing near-constant false mismatches (e.g.
stated "B" vs fresh "45" when B literally IS 45). Now cross-references against
the parsed choices. Also fixes comma-decimal answers being misclassified as
"formula" answers and skipped.

Usage:
    python scripts/solve_check.py data/raw/pending/gen_Matematika-Informatika_g7_20260818_163325.txt
"""
import getpass
import json
import os
import re
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from google import genai

load_dotenv(find_dotenv())
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = getpass.getpass("GEMINI API KEY: ")

MODEL = "gemini-3.6-flash"
BLOCK_RE = re.compile(r"<subject>.*?</answer>", re.DOTALL)
TAG_RE = re.compile(r"<(\w+)>(.*?)</\1>", re.DOTALL)
CHOICE_RE = re.compile(r"([A-D])\)\s*([^A-D]+?)(?=\s*[A-D]\)|$)")


def parse_blocks(raw_text: str) -> list[dict]:
    blocks = []
    for match in BLOCK_RE.finditer(raw_text):
        block_text = match.group(0)
        tags = {tag: content.strip() for tag, content in TAG_RE.findall(block_text)}
        if "problem" in tags and "answer" in tags:
            blocks.append(tags)
    return blocks


def parse_choices_map(choices_str: str) -> dict:
    """'A) 37  B) 45  C) 53  D) 43' -> {'A': '37', 'B': '45', 'C': '53', 'D': '43'}"""
    return {letter: value.strip() for letter, value in CHOICE_RE.findall(choices_str)}


def solve_fresh(client, problem: str, choices: str | None, fmt: str) -> str:
    if fmt == "mcq" and choices:
        prompt = (
            "Solve this competition problem step by step, then identify which "
            "answer choice is correct. Give ONLY the letter (A, B, C, or D) on "
            "the last line, prefixed with 'FINAL:'.\n\n"
            f"Problem: {problem}\nChoices: {choices}"
        )
    else:
        prompt = (
            "Solve this competition problem step by step. Give ONLY the final "
            "numeric/short answer on the last line, prefixed with 'FINAL:'.\n\n"
            f"Problem: {problem}"
        )
    response = client.models.generate_content(model=MODEL, contents=prompt)
    text = response.text.strip()
    for line in reversed(text.splitlines()):
        if "FINAL:" in line:
            return line.split("FINAL:", 1)[1].strip()
    return text.splitlines()[-1].strip() if text else ""


def is_probably_numeric(answer: str) -> bool:
    try:
        float(answer.strip().replace(",", "."))
        return True
    except ValueError:
        return False


def answers_match(stated: str, fresh: str, fmt: str, choices_map: dict | None = None) -> bool:
    s, f = stated.strip(), fresh.strip()
    if fmt == "mcq" and choices_map:
        f_letter = f.upper().rstrip(").").strip()
        if f_letter in choices_map:
            return f_letter == s.upper()
        # fresh solve gave a raw value instead of a letter -- find which
        # choice that value actually corresponds to
        for letter, value in choices_map.items():
            if value.strip().lower() == f.strip().lower():
                return letter == s.upper()
            try:
                if abs(float(value.replace(",", ".")) - float(f.replace(",", "."))) < 0.01:
                    return letter == s.upper()
            except ValueError:
                continue
        return False
    s_l, f_l = s.lower(), f.lower()
    if s_l == f_l:
        return True
    try:
        return abs(float(s.replace(",", ".")) - float(f.replace(",", "."))) < 0.01
    except ValueError:
        return s_l in f_l or f_l in s_l


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/solve_check.py <path to raw generated_batch file>")
        sys.exit(1)

    raw_path = Path(sys.argv[1])
    raw_text = raw_path.read_text(encoding="utf-8")
    blocks = parse_blocks(raw_text)
    print(f"Parsed {len(blocks)} problems from {raw_path.name}")

    client = genai.Client()
    root = Path(__file__).resolve().parent.parent
    verified_path = root / "data" / "verified_pool.jsonl"
    flagged_path = root / "data" / "flagged_for_review.jsonl"
    verified_path.parent.mkdir(parents=True, exist_ok=True)

    passed, flagged = 0, 0
    with verified_path.open("a", encoding="utf-8") as out, flagged_path.open("a", encoding="utf-8") as flag_out:
        for i, block in enumerate(blocks, 1):
            fmt = block.get("format", "mcq")
            choices_map = parse_choices_map(block["choices"]) if fmt == "mcq" and "choices" in block else None

            if fmt == "open" and not is_probably_numeric(block["answer"]):
                print(f"[{i}/{len(blocks)}] SKIPPED (formula answer, needs human review): {block['problem'][:60]}...")
                flag_out.write(json.dumps({**block, "reason": "formula_answer", "fresh_solve": None}, ensure_ascii=False) + "\n")
                flagged += 1
                continue

            fresh = solve_fresh(client, block["problem"], block.get("choices"), fmt)
            if answers_match(block["answer"], fresh, fmt, choices_map):
                out.write(json.dumps(block, ensure_ascii=False) + "\n")
                passed += 1
                print(f"[{i}/{len(blocks)}] PASS")
            else:
                flagged += 1
                flag_out.write(json.dumps({**block, "reason": "mismatch", "fresh_solve": fresh}, ensure_ascii=False) + "\n")
                print(f"[{i}/{len(blocks)}] MISMATCH -- stated={block['answer']!r} fresh_solve={fresh!r} -- flagged for human review, not added")

    print(f"\n{passed} passed and appended to {verified_path}")
    print(f"{flagged} flagged for human review -- see {flagged_path}")
    print("Run scripts/build_dataset.py next to fold verified_pool.jsonl into train.jsonl")

    checked_dir = root / "data" / "raw" / "checked"
    checked_dir.mkdir(parents=True, exist_ok=True)
    dest = checked_dir / raw_path.name
    raw_path.replace(dest)
    print(f"\nMoved {raw_path.name} -> {dest} (marked as checked)")


if __name__ == "__main__":
    main()
