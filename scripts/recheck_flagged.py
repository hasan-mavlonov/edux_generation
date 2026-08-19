"""
Re-checks everything currently in data/flagged_for_review.jsonl using the
FIXED solve/match logic from the v2 solve_check.py. Most of what's in there
right now is a false mismatch caused by the letter-vs-value bug, not actually
bad content -- this recovers those without spending any new generation
credits (only re-solve calls, same cost as the original check).

Genuine formula-answer items and genuine mismatches (confirmed wrong) stay
flagged and are written back out for human review.

Usage: python scripts/recheck_flagged.py
"""
import getpass
import json
import os
import re
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from google import genai

load_dotenv(find_dotenv())
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = getpass.getpass("GEMINI API KEY: ")

MODEL = "gemini-3.6-flash"
CHOICE_RE = re.compile(r"([A-D])\)\s*([^A-D]+?)(?=\s*[A-D]\)|$)")


def parse_choices_map(choices_str: str) -> dict:
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
    client = genai.Client()
    root = Path(__file__).resolve().parent.parent
    flagged_path = root / "data" / "flagged_for_review.jsonl"
    verified_path = root / "data" / "verified_pool.jsonl"
    new_flagged_path = root / "data" / "flagged_for_review.jsonl.new"

    items = [json.loads(l) for l in flagged_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Re-checking {len(items)} flagged items with fixed logic...\n")

    recovered, still_bad = 0, 0
    with verified_path.open("a", encoding="utf-8") as vout, new_flagged_path.open("w", encoding="utf-8") as fout:
        for i, item in enumerate(items, 1):
            fmt = item.get("format", "mcq")
            choices_map = parse_choices_map(item["choices"]) if fmt == "mcq" and "choices" in item else None

            if fmt == "open" and not is_probably_numeric(item["answer"]):
                fout.write(json.dumps(item, ensure_ascii=False) + "\n")
                still_bad += 1
                print(f"[{i}/{len(items)}] SKIP (genuine formula answer, needs human review)")
                continue

            fresh = solve_fresh(client, item["problem"], item.get("choices"), fmt)
            if answers_match(item["answer"], fresh, fmt, choices_map):
                clean = {k: v for k, v in item.items() if k not in ("reason", "fresh_solve")}
                vout.write(json.dumps(clean, ensure_ascii=False) + "\n")
                recovered += 1
                print(f"[{i}/{len(items)}] RECOVERED (was a false mismatch)")
            else:
                item["fresh_solve"] = fresh
                fout.write(json.dumps(item, ensure_ascii=False) + "\n")
                still_bad += 1
                print(f"[{i}/{len(items)}] STILL MISMATCH -- stated={item['answer']!r} fresh={fresh!r} (genuinely worth a human look)")

    print(f"\nRecovered: {recovered}")
    print(f"Still genuinely flagged: {still_bad}")
    print(f"\nRun this to replace the old flagged file with the smaller, real one:")
    print(f"  mv {new_flagged_path} {flagged_path}")
    print("Then run scripts/build_dataset.py to fold the recovered items into train.jsonl")


if __name__ == "__main__":
    main()
