# Live Execution: 5-candidate (naive) vs 4-candidate (same-benchmark) comparison

Naive run: 2026-05-03T06:49:05Z
Clean run: 2026-05-03T14:58:23Z

## Per-selector aggregate (judge mean is the single most informative metric)

| Selector | Naive (5 cands) judge | Clean (4 cands) judge | Delta judge | Naive execution cost (USD) | Clean execution cost (USD) |
|---|---:|---:|---:|---:|---:|
| asm_topsis | 7.93 | 9.27 | +1.33 | $0.0149 | $0.0064 |
| cheapest_first | 9.50 | 9.65 | +0.15 | $0.0054 | $0.0064 |
| llm_picker_description | 9.97 | 9.23 | -0.73 | $0.0068 | $0.0087 |
| llm_picker_manifest | 9.60 | 9.21 | -0.39 | $0.0411 | $0.0275 |
| random | 9.28 | 9.21 | -0.07 | $0.0392 | $0.0459 |
| weighted_average | 7.40 | 9.31 | +1.91 | $0.0145 | $0.0370 |

**Interpretation.** When MiniMax M2.7 is in the candidate set, its manifest-declared MMLU 78 normalises to a higher quality score than peers' AA Intelligence 53-60, so TOPSIS over-selects MiniMax. Live judge scores show MiniMax averages only ~6.0 vs 9.8+ for the other 4 models; the result is that ASM-TOPSIS under-performs the heuristics. After enforcing the §6.7 same-benchmark constraint (drop MiniMax), ASM-TOPSIS performance restores. This is a real-world demonstration of the §7.1 quality-normalisation limitation: cross-benchmark scaling fails. The fix is methodological, not algorithmic — manifests must report quality on the same benchmark to be commensurable.
