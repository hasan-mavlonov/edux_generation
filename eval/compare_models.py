"""
Compares the fine-tuned Qwen3 model against the Gemini baseline on the same
generation requests, so you can decide -- with evidence, not vibes -- whether
the fine-tune is actually good enough to take over production traffic.

This is a skeleton: it generates N problems from each model for a fixed set of
requests and saves them side by side for review. It does NOT auto-decide a
winner -- correctness on generated (not just retrieved) problems still needs
either an independent solve-check pass or human review, same as everything
else in this pipeline.

Fill in FT_MODEL_PATH once you have a trained checkpoint, then run:
    python eval/compare_models.py
"""
import json
from pathlib import Path

FT_MODEL_PATH = "./checkpoints/edux-qwen3-8b-v1"  # set after training

TEST_REQUESTS = [
    {"subject": "Matematika", "grade": 7, "difficulty": "0.9", "format": "mcq", "topic": "algebra"},
    {"subject": "Matematika", "grade": 7, "difficulty": "1.5", "format": "open", "topic": "geometry"},
    {"subject": "Informatika", "grade": 7, "difficulty": "0.9", "format": "mcq", "topic": "logic gates"},
    {"subject": "Fizika", "grade": 10, "difficulty": "1.5", "format": "open", "topic": "kinematics"},
]


def generate_with_gemini(request: dict) -> str:
    import getpass
    import os
    from dotenv import find_dotenv, load_dotenv
    from google import genai

    load_dotenv(find_dotenv())
    if not os.getenv("GEMINI_API_KEY"):
        os.environ["GEMINI_API_KEY"] = getpass.getpass("GEMINI API KEY: ")

    template = Path("prompts/generation_prompt_v1.md").read_text(encoding="utf-8")
    prompt = template + "\n\nGenerate 1 new problem for:\n" + "\n".join(
        f"- {k}: {v}" for k, v in request.items()
    )
    client = genai.Client()
    return client.models.generate_content(
        model="gemini-3.1-pro-preview", contents=prompt
    ).text


def generate_with_finetune(request: dict) -> str:
    # Load the LoRA adapter + base model and generate. Left as a stub until
    # a real checkpoint exists -- fill in with PeftModel.from_pretrained +
    # AutoModelForCausalLM once training/train_lora.py has produced output.
    raise NotImplementedError(
        "Point this at your trained checkpoint once training/train_lora.py finishes."
    )


def main():
    results = []
    for req in TEST_REQUESTS:
        gemini_out = generate_with_gemini(req)
        try:
            ft_out = generate_with_finetune(req)
        except NotImplementedError as e:
            print(f"Skipping fine-tune generation: {e}")
            ft_out = None
        results.append({"request": req, "gemini": gemini_out, "finetune": ft_out})

    out_path = Path("eval/comparison_results.json")
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(results)} comparisons to {out_path}")
    print("Review manually, or run scripts/solve_check.py against both sets of output.")


if __name__ == "__main__":
    main()
