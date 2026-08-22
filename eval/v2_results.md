# v2 Checkpoint Evaluation Results

**Model:** Qwen3-4B + LoRA (r=16, 33M trainable params), 3 epochs
**Training data:** 604 examples (302 Matematika, 300 Informatika, 2 Fizika) --
first run at the 300/subject floor (302/300 vs v1's 192/115).

**Generation config change from v1:** `max_new_tokens` raised from 400 to 700
to fix the truncation issue identified in v1's eval. **This means v1 vs v2
is not a clean, single-variable comparison** -- both data volume and token
budget changed at once. Improvements below can't be cleanly attributed to
data volume alone.

**Evaluation method:** Same as v1 -- 14 new problems spanning both subjects,
all three difficulty tiers, both mcq/open formats
(`data/raw/pending/finetuned_v1_20260822_231452.txt` -- filename says v1,
script's hardcoded prefix, actual checkpoint is v2). Each independently
verified by hand.

## Results, compared to v1

| | v1 (309 examples, 400 tok) | v2 (604 examples, 700 tok) |
|---|---|---|
| Incomplete (truncated) | 7/14 (50%) | 3/14 (21%) |
| Clean & correct | 2/14 (~14%) | 4/14 (~29%) |

Real improvement on both fronts. Genuinely still far from something to
ship or trust over Gemini prompting.

## New failure pattern in v2, distinct from v1's

v1's main problem was incompleteness. v2 completes more often, but surfaces
a different, specific issue: **the model does correct work in its solution
text, then states a final answer disconnected from that work.**

- Problem 1 (x^4+1/x^4 given x+1/x=5): correctly computes 527 in the
  solution -- but the MCQ choices are 23/26/30/25. The answer tag says
  "527," which isn't even among the offered choices.
- Problem 14 (binary addition to hex): correctly computes 356(10) = 164(16)
  in the solution -- then answers "C" (choices show C as 57(16), unrelated
  to the computed value).
- Problem 7 (percentage word problem): computes 26 kg in the solution,
  answers "A" (28 kg).

This isn't the same failure as v1's incompleteness -- it's the model
generating a correct derivation and an unrelated final answer, often paired
with badly-formed choice sets that don't include the correct value at all.
Not obviously fixed by more data alone; may need attention to how MCQ
choices get generated relative to the computed answer, separate from the
data-volume question.

## Conclusion

Real, measured progress: completion rate roughly doubled, correctness rate
roughly doubled. But the confound (data + token budget changed together)
means the next useful experiment is isolating variables -- e.g. re-run v1's
data at 700 tokens to see how much of the completion-rate gain was really
the token fix vs. the data. The new answer-disconnected-from-solution
pattern is worth tracking specifically in future evals, not just the
raw correctness percentage.
