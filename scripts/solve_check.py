"""
Independent solve-check, formalized. For every problem in a raw generated_batch
file, this asks the model to solve it FRESH (no access to the generation-time
answer), compares the result to the stated answer, and only appends matches to
data/verified_pool.jsonl -- which build_dataset.py also pulls into training data.

This is the automated version of what we did by hand throughout the pilot
(13/13 on real problems, 5/5 and 20/20 on generated batches). It raises the
floor, it doesn't replace human review -- paid-tier content still needs a
person to sign off before deployment, and formula-answer physics problems
always need human review since they can't be auto-graded reliably.

Usage:
    python scripts/solve_check.py data/raw/generated_batch_20260815_140203.txt
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

MODEL = "gemini-3.1-pro-preview"
BLOCK_RE = re.compile(r"<subject>.*?</answer>", re.DOTALL)
TAG_RE = re.compile(r"<(\w+)>(.*?)</\1>", re.DOTALL)


def parse_blocks(raw_text: str) -> list[dict]:
    blocks = []
    for match in BLOCK_RE.finditer(raw_text):
        block_text = match.group(0)
        tags = {tag: content.strip() for tag, content in TAG_RE.findall(block_text)}
        if "problem" in tags and "answer" in tags:
            blocks.append(tags)
    return blocks


def solve_fresh(client, problem: str, choices: str | None) -> str:
    prompt = (
        "Solve this competition problem step by step. Give ONLY the final answer "
        "on the last line, prefixed with 'FINAL:'.\n\n"
        f"Problem: {problem}"
    )
    if choices:
        prompt += f"\nChoices: {choices}"
    response = client.models.generate_content(model=MODEL, contents=prompt)
    text = response.text.strip()
    for line in reversed(text.splitlines()):
        if "FINAL:" in line:
            return line.split("FINAL:", 1)[1].strip()
    return text.splitlines()[-1].strip() if text else ""


def answers_match(stated: str, fresh: str) -> bool:
    s, f = stated.strip().lower(), fresh.strip().lower()
    if s == f:
        return True
    try:
        return abs(float(s.replace(",", ".")) - float(f.replace(",", "."))) < 0.01
    except ValueError:
        return s in f or f in s  # loose fallback for mcq letters / short strings


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/solve_check.py <path to raw generated_batch file>")
        sys.exit(1)

    raw_path = Path(sys.argv[1])
    raw_text = raw_path.read_text(encoding="utf-8")
    blocks = parse_blocks(raw_text)
    print(f"Parsed {len(blocks)} problems from {raw_path.name}")

    client = genai.Client()
    verified_path = Path(__file__).resolve().parent.parent / "data" / "verified_pool.jsonl"
    verified_path.parent.mkdir(parents=True, exist_ok=True)

    passed, flagged = 0, 0
    with verified_path.open("a", encoding="utf-8") as out:
        for i, block in enumerate(blocks, 1):
            is_formula = "format" in block and block.get("format") == "open" and not block["answer"].replace(".", "").replace("-", "").isdigit()
            if is_formula:
                print(f"[{i}/{len(blocks)}] SKIPPED (formula answer, needs human review): {block['problem'][:60]}...")
                flagged += 1
                continue

            fresh = solve_fresh(client, block["problem"], block.get("choices"))
            if answers_match(block["answer"], fresh):
                out.write(json.dumps(block, ensure_ascii=False) + "\n")
                passed += 1
                print(f"[{i}/{len(blocks)}] PASS")
            else:
                flagged += 1
                print(f"[{i}/{len(blocks)}] MISMATCH -- stated={block['answer']!r} fresh_solve={fresh!r} -- flagged for human review, not added")

    print(f"\n{passed} passed and appended to {verified_path}")
    print(f"{flagged} flagged for human review (mismatch or formula-answer)")
    print("Run scripts/build_dataset.py next to fold these into train.jsonl")


if __name__ == "__main__":
    main()
