# edux-model

Self-hosted olympiad problem generator for EduX. Goal: fine-tune Qwen3 on EduX's own verified problem+solution data, so generation runs on infrastructure EduX owns instead of a third-party API.

## Current status

- **309 training examples** were used in the completed v1 QLoRA run.
- **Qwen3-4B** was used as the base model for v1.
- **LoRA v1 training completed for 3 epochs** on a single RTX 3080 Ti.
- The resulting adapter was saved to `checkpoints/v1` on the training instance.
- Final logged training loss: **0.557**. This is a training metric, not an independent quality evaluation.
- The adapter must still be evaluated against the Gemini baseline with `eval/compare_models.py` and `solve_check.py` before production use.

## v1 training run

The completed run used:

```bash
EDUX_MODEL_NAME="/root/autodl-tmp/models/models/Qwen--Qwen3-4B/snapshots/master" \
python training/train_lora.py --epochs 3 --output_dir ./checkpoints/v1
```

The training log reports 309 examples tokenized, 33,030,144 trainable parameters out of 4,055,498,240 total parameters, and a completed 3-epoch run. The adapter was saved to `./checkpoints/v1`.

## Preserving the checkpoint

`checkpoints/` is intended to contain model artifacts and should be stored with Git LFS rather than normal Git objects.

Before pushing the checkpoint, make sure `adapter_config.json` points to the portable Hugging Face model ID `Qwen/Qwen3-4B`, not the temporary `/root/autodl-tmp/...` path from the training machine.

Example on the training instance:

```bash
cd ~/edux_generation
python - <<'PY'
import json
from pathlib import Path

p = Path("checkpoints/v1/adapter_config.json")
data = json.loads(p.read_text())
data["base_model_name_or_path"] = "Qwen/Qwen3-4B"
p.write_text(json.dumps(data, indent=2) + "\n")
PY
```

Then upload `checkpoints/v1` with Git LFS.

## Dataset / generation loop

```text
generate_batch.py  -->  raw generated problems (data/raw/*.txt)
        |
solve_check.py      -->  independently re-solves each one; only matches
        |                 get appended to data/verified_pool.jsonl
        v
build_dataset.py    -->  merges verified_examples.py + verified_pool.jsonl
                          into data/processed/train.jsonl
```

Every normal day of using the Gemini pipeline for real (daily/weekly/monthly tests) adds to `train.jsonl` for free, as long as `solve_check.py` runs on each batch. Formula-answer physics problems and anything that fails the solve-check get flagged for human review instead of silently entering the training set.

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

## Evaluation before production

Run `eval/compare_models.py` with the v1 adapter and compare its outputs against Gemini on the same requests. Run both sets through `solve_check.py` and/or human review. The completed training run alone does not establish that the fine-tuned model is better than the baseline.

## Repo layout

```text
prompts/generation_prompt_v1.md   generation system prompt + few-shot seeds
data/verified_examples.py         hand-curated verified problems (source of truth)
data/verified_pool.jsonl          auto-verified via solve_check.py (gitignored, grows locally)
data/processed/train.jsonl        final SFT-ready training file
scripts/generate_batch.py         Gemini generation (needs GEMINI_API_KEY)
scripts/solve_check.py            independent re-solve + verification gate
scripts/build_dataset.py          merges everything verified into train.jsonl
training/train_lora.py            QLoRA fine-tune of Qwen3
checkpoints/v1/                   completed QLoRA adapter + tokenizer artifacts
eval/compare_models.py            fine-tune vs Gemini comparison harness
```

## Known open problem

Physics olympiad problems sometimes expect a formula as the answer (e.g. `h = sigma/(rho*g*r)`), not a number. Nothing in this repo can auto-grade that yet -- `solve_check.py` skips these and flags them for human review rather than guessing. Worth solving properly (symbolic equivalence checking) before physics reaches real generation volume.
