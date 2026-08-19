"""
Repeatedly runs generate_batch.py -> solve_check.py, checking real counts
after every round, until Matematika and Informatika (hand-curated + verified
pool) both reach TARGET. Fizika is intentionally left out, matching
generate_batch.py's current SUBJECTS setting.

Safe to interrupt (Ctrl+C) at any point -- every round's results are already
saved to disk before the next round starts, nothing is lost.

This WILL spend real Gemini credits every round (1 generation call + up to
N solve-check calls). MAX_ROUNDS is a safety cap against runaway spend if
something goes wrong -- not a target estimate. Adjust it if you're
comfortable spending more before checking back in.

Usage: python scripts/grow_dataset.py
"""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

TARGET = 300
MAX_ROUNDS = 40  # safety valve, not an estimate -- re-run this script if it stops here

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from data.verified_examples import VERIFIED_EXAMPLES  # noqa: E402


def current_counts() -> Counter:
    counts = Counter(ex["subject"] for ex in VERIFIED_EXAMPLES)
    pool_path = REPO_ROOT / "data" / "verified_pool.jsonl"
    if pool_path.exists():
        for line in pool_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                counts[json.loads(line)["subject"]] += 1
    return counts


def run(cmd: list[str], env: dict | None = None) -> str:
    full_env = {**os.environ, **(env or {})}
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, env=full_env)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
    return result.stdout


def subjects_for_round(math_gap: int, info_gap: int) -> str:
    """Weight generation toward whichever subject is further behind."""
    if info_gap > math_gap * 1.5:
        return "Informatika (primary focus, most of this batch), Matematika (a couple, for variety)"
    if math_gap > info_gap * 1.5:
        return "Matematika (primary focus, most of this batch), Informatika (a couple, for variety)"
    return "Matematika, Informatika"


def main():
    for round_num in range(1, MAX_ROUNDS + 1):
        counts = current_counts()
        math_n = counts.get("Matematika", 0)
        info_n = counts.get("Informatika", 0)
        math_gap = max(TARGET - math_n, 0)
        info_gap = max(TARGET - info_n, 0)

        print(f"\n=== Round {round_num} === Matematika: {math_n}/{TARGET}  Informatika: {info_n}/{TARGET}")

        if math_gap == 0 and info_gap == 0:
            print("\nBoth subjects at target. Stopping.")
            break

        subjects_override = subjects_for_round(math_gap, info_gap)
        run([sys.executable, "scripts/generate_batch.py"], env={"EDUX_SUBJECTS": subjects_override})

        pending_dir = REPO_ROOT / "data" / "raw" / "pending"
        for f in sorted(pending_dir.glob("*.txt")):
            run([sys.executable, "scripts/solve_check.py", str(f)])
    else:
        print(
            f"\nHit MAX_ROUNDS={MAX_ROUNDS} safety limit before reaching target. "
            "Re-run this script to continue, or raise MAX_ROUNDS at the top of this "
            "file if you're comfortable spending more credits before checking back in."
        )

    print("\nRebuilding train.jsonl...")
    run([sys.executable, "scripts/build_dataset.py"])


if __name__ == "__main__":
    main()
