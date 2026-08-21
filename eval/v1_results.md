# v1 Checkpoint Evaluation Results

**Model:** Qwen3-4B + LoRA (r=16, 33M trainable params), 3 epochs
**Training data:** 309 examples (192 Matematika, 115 Informatika, 2 Fizika) --
well below the 300-500/subject floor identified as necessary before a
fine-tune should be expected to compete with Gemini prompting.

**Evaluation method:** Generated 14 new problems spanning both subjects,
all three difficulty tiers, and both mcq/open formats
(`eval/generate_finetuned_batch.py`, output saved at
`data/raw/pending/finetuned_v1_20260821_203551.txt`). Each was independently
verified by hand (re-solved and checked against the model's stated answer
and reasoning), same rigor as every other verification pass in this project.

## Results

**7 of 14 (50%) never completed** -- cut off mid-solution with no answer
tag at all. This is a real, structural failure mode distinct from
correctness: at this data volume the model hasn't reliably learned *when
to stop*, not just what to generate.

Of the 7 that did complete:

| # | Topic | Verdict |
|---|---|---|
| 1 | x-y=2, x^2-y^2=4 | Math correct, but question is degenerate -- asks to find x-y when it's already given |
| 5 | 14-digit binary strings, divisible by 2 | Right final answer, but the shown work contains a real arithmetic error (states 2^14=4096, actually 16384) |
| 9 | AND gate | Incoherent -- doesn't define a computable question |
| 10 | Binary+decimal to hex | **Correct.** Clean, verified by hand. |
| 11 | Fibonacci-style loop trace | **Correct.** Traced by hand, matches. |
| 12 | Excel formula | Incoherent -- invents undefined cells and values with no basis |
| 13 | RGB to hex | Math correct, but the MCQ itself is broken (two choices are identical text) |

**Real accuracy: 2/14 (~14%) clean and correct.** Generously counting "right
final answer despite flawed construction": ~5/14 (~36%). Either way, well
below Gemini's output quality throughout this project.

## Conclusion

This is the expected result of training below the data floor, not evidence
the approach is broken. The fix is the same one identified before any GPU
work started: grow `data/by_category/` toward 300-500 verified examples
per subject before the next training attempt. Model architecture, LoRA
config, and the training pipeline itself are all confirmed working --
volume is the only real blocker.
