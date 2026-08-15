# edux-model

Self-hosted olympiad problem generator for EduX. Goal: fine-tune Qwen3 on
EduX's own verified problem+solution data, so generation runs on infrastructure
EduX owns instead of a third-party API.

## Current status

- **~25 hand-verified examples** across Matematika, Informatika, Fizika
  (`data/verified_examples.py`). This is a real starting point, not a
  production-ready training set -- see the target below.
- **Prompting on Gemini already works** (`prompts/generation_prompt_v1.md` +
  `scripts/generate_batch.py`) and is what should keep producing live content
  while the fine-tuning dataset grows in the background.
- **No fine-tuned checkpoint exists yet.** `training/train_lora.py` is ready
  to run once there's enough data to make it worthwhile.

## The loop that grows the dataset

```
generate_batch.py  -->  raw generated problems (data/raw/*.txt)
        |
solve_check.py      -->  independently re-solves each one; only matches
        |                 get appended to data/verified_pool.jsonl
        v
build_dataset.py    -->  merges verified_examples.py + verified_pool.jsonl
                          into data/processed/train.jsonl
```

Every normal day of using the Gemini pipeline for real (daily/weekly/monthly
tests) adds to `train.jsonl` for free, as long as `solve_check.py` runs on
each batch. Formula-answer physics problems and anything that fails the
solve-check get flagged for human review instead of silently entering the
training set.

**Target before the first real fine-tune attempt: 300-500+ verified examples
per subject.** Below that, a fine-tune is likely to underperform prompting.
`build_dataset.py` prints a warning while you're under this floor.

## Running the pipeline

```bash
pip install -r requirements.txt

# 1. Generate a batch (needs GEMINI_API_KEY)
python scripts/generate_batch.py

# 2. Independently verify it
python scripts/solve_check.py data/raw/generated_batch_<timestamp>.txt

# 3. Rebuild the training set
python scripts/build_dataset.py
```

## Training (once the data floor is hit)

Needs a CUDA GPU with >=24GB VRAM. Provider-agnostic -- tested against
RunPod/Vast.ai-style rented boxes, works the same on AutoDL or local hardware.

```bash
python training/train_lora.py \
    --data data/processed/train.jsonl \
    --output_dir ./checkpoints/edux-qwen3-8b-v1 \
    --epochs 3
```

Base model: `Qwen/Qwen3-8B` (Apache 2.0), chosen for its multilingual/Uzbek
coverage relative to other open-weight options at this size. QLoRA (4-bit +
LoRA adapters), not a full fine-tune -- realistic on a single rented GPU.

## Before switching any real traffic to the fine-tuned model

Run `eval/compare_models.py` (fill in your checkpoint path first) to generate
matched output from both Gemini and the fine-tune on the same requests, then
run both sets through `solve_check.py` and/or human review. Don't switch
production over on vibes -- compare accuracy directly, the same way we
validated the Gemini pipeline itself (13/13 on real problems before trusting
it for daily-tier content).

## Repo layout

```
prompts/generation_prompt_v1.md   generation system prompt + few-shot seeds
data/verified_examples.py         hand-curated verified problems (source of truth)
data/verified_pool.jsonl          auto-verified via solve_check.py (gitignored, grows locally)
data/processed/train.jsonl        final SFT-ready training file
scripts/generate_batch.py         Gemini generation (needs GEMINI_API_KEY)
scripts/solve_check.py            independent re-solve + verification gate
scripts/build_dataset.py          merges everything verified into train.jsonl
training/train_lora.py            QLoRA fine-tune of Qwen3-8B
eval/compare_models.py            fine-tune vs Gemini comparison harness
```

## Known open problem

Physics olympiad problems sometimes expect a **formula as the answer**
(e.g. `h = sigma/(rho*g*r)`), not a number. Nothing in this repo can
auto-grade that yet -- `solve_check.py` skips these and flags them for
human review rather than guessing. Worth solving properly (symbolic
equivalence checking) before physics reaches real generation volume.
