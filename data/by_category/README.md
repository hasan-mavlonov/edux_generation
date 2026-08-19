# data/by_category/

Every problem the pipeline has touched, split honestly by grade band and by
where it actually came from. Each record also carries `"source"` and
`"verified"` fields so you never have to guess.

| File | Count | What's in it |
|---|---|---|
| `grade7_real_verified.jsonl` | 20 | Real Al-Xorazmiy tuman-bosqichi problems (17 Matematika checked against the real answer key, 3 Informatika verified by direct reasoning since no key exists for that subject). Zero AI-invented content. |
| `grade7_ai_generated_verified.jsonl` | 287 | Genuinely new problems invented by an LLM (Gemini via `generate_batch.py`+`solve_check.py`, plus 3 early ones Claude hand-derived in chat before the pipeline existed) and independently solve-checked. None of these exist in any real exam. |
| `grade9-11_real.jsonl` | 92 | 90 Informatika problems pulled from the real Fan Olimpiadalari Markazi manual (**unverified** -- `"verified": false`, no answer key exists for these yet, needs a solve-check pass) + 2 Fizika problems from the licensed textbook (**verified** -- independently re-derived against the source). |
| `grade9-11_ai_generated.jsonl` | 0 | Empty on purpose. `generate_batch.py` has only ever been run with `GRADE = 7`. Nothing exists here yet. |

## Why generate synthetic data at all, given the real archive exists

Two different jobs, easy to conflate:

- **The live product** (daily/weekly/monthly tests for 50k+ students) needs
  content that keeps renewing. Reusing the same ~36 real exam questions
  repeatedly would get memorized/leaked across a user base that size. That's
  what `generate_batch.py` is actually for.
- **Fine-tuning training data** doesn't have that constraint the same way --
  real, already-correct archive problems are strictly better raw material
  than spending API credits generating synthetic ones, especially while
  credits are tight. Going forward, exhaust the real archive first per
  grade/subject before generating more synthetic content for training
  purposes specifically.

## Priority order for growing this, given the above

1. Solve-check the 90 unverified `grade9-11_real.jsonl` Informatika items --
   free-ish (only re-solve calls, no generation), and turns 90 unverified
   into up to 90 verified, without expanding scope to grades 9-11 in the
   live product.
2. Look for more real grade-7 archive material before generating more
   synthetic grade-7 content.
3. Only then lean on `generate_batch.py` again for grade 7, once real
   sources are actually exhausted.
