# Expert Annotation Ranking Experiment

Generated: 2026-05-02T11:19:57Z
Tasks evaluated: 36 / 36
Provider/model: kimi-k2.5 / kimi-k2.5
Ran LLM: True

## Rank correlation vs expert (mean ± 95% bootstrap CI, n=2000)

| Selector | n | Kendall's tau | Spearman's rho | Top-1 accuracy | Parse fails |
|---|---:|---|---|---:|---:|
| llm_manifest | 36 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 100.0% | 0 |
| asm_topsis | 36 | 0.630 [0.370, 0.852] | 0.639 [0.375, 0.861] | 77.8% | 0 |
| llm_raw_doc | 36 | 0.370 [0.056, 0.648] | 0.375 [0.069, 0.653] | 69.4% | 0 |
