# Expert Annotation Ranking Experiment

Generated: 2026-05-02T10:00:34Z
Tasks evaluated: 36 / 36
Provider/model: deepseek-v4-flash / deepseek-v4-flash
Ran LLM: True

## Rank correlation vs expert (mean ± 95% bootstrap CI, n=2000)

| Selector | n | Kendall's tau | Spearman's rho | Top-1 accuracy | Parse fails |
|---|---:|---|---|---:|---:|
| llm_manifest | 36 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 100.0% | 0 |
| asm_topsis | 36 | 0.630 [0.370, 0.852] | 0.639 [0.375, 0.861] | 77.8% | 0 |
| llm_raw_doc | 36 | 0.444 [0.130, 0.704] | 0.444 [0.125, 0.708] | 72.2% | 0 |
