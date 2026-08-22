import getpass
import os
import re
import time
from pathlib import Path

from google import genai
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = getpass.getpass("GEMINI API KEY: ")

# --- adjust these for whatever slice you're testing ---
N = 10
SUBJECTS = os.environ.get("EDUX_SUBJECTS", "Matematika, Informatika")
GRADE = 7
DIFFICULTY_MIX = "spread across 0.9, 1.5, and 2.6 — don't cluster on one tier"
FORMAT_MIX = "mostly mcq, but include 2-3 open format"
TOPIC_VARIETY = "algebra, number theory, combinatorics, geometry (with diagram_spec), logic gates, number systems, basic Excel/Scratch"
# Pro is the default (better creative/reasoning quality for novel problem generation).
# Override to gemini-3.6-flash for ~3x cheaper generation -- worth testing on one
# small batch first, since a higher solve_check reject rate could offset some of
# the savings (more rounds needed to reach the same verified count).
MODEL = os.environ.get("EDUX_GEN_MODEL", "gemini-3.6-flash")
# --------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

client = genai.Client()

template = (REPO_ROOT / "prompts" / "generation_prompt_v1.md").read_text(encoding="utf-8")

request = f"""
Generate {N} new problems, mixing subjects/formats/difficulty as specified:
- subjects to draw from: {SUBJECTS}
- grade: {GRADE}
- difficulty mix: {DIFFICULTY_MIX}
- format mix: {FORMAT_MIX}
- topic variety: {TOPIC_VARIETY}
"""

full_prompt = template + "\n\n" + request

response = client.models.generate_content(
    model=MODEL,
    contents=full_prompt,
)

print(response.text)

subjects_slug = re.sub(r"[^A-Za-z0-9]+", "-", SUBJECTS).strip("-")
pending_dir = REPO_ROOT / "data" / "raw" / "pending"
pending_dir.mkdir(parents=True, exist_ok=True)

timestamp = time.strftime("%Y%m%d_%H%M%S")
out_path = pending_dir / f"gen_{subjects_slug}_g{GRADE}_{timestamp}.txt"
out_path.write_text(response.text, encoding="utf-8")

print(f"\nSaved to {out_path}")
print("Next: run scripts/solve_check.py on this file to independently verify each problem")
print("before it's eligible to join the training set.")