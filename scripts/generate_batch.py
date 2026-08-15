import getpass
import os
from google import genai

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = getpass.getpass("GEMINI API KEY: ")

# --- adjust these for whatever slice you're testing ---
N = 10
SUBJECTS = "Matematika, Informatika"
GRADE = 7
DIFFICULTY_MIX = "spread across 0.9, 1.5, and 2.6 — don't cluster on one tier"
FORMAT_MIX = "mostly mcq, but include 2-3 open format"
TOPIC_VARIETY = "algebra, number theory, combinatorics, geometry (with diagram_spec), logic gates, number systems, basic Excel/Scratch"
MODEL = "gemini-3.1-pro-preview"
# --------------------------------------------------------

client = genai.Client()  # reads GEMINI_API_KEY from the environment automatically

with open("prompts/generation_prompt_v1.md", "r", encoding="utf-8") as f:
    template = f.read()

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

import pathlib
pathlib.Path("data/raw").mkdir(parents=True, exist_ok=True)
out_path = f"data/raw/generated_batch_{__import__('time').strftime('%Y%m%d_%H%M%S')}.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"\nSaved to {out_path}")
print("Next: run scripts/solve_check.py on this file to independently verify each problem")
print("before it's eligible to join the training set.")
