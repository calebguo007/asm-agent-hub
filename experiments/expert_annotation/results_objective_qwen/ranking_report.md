# Expert Annotation Ranking Experiment

Generated: 2026-05-02T10:35:49Z
Tasks evaluated: 36 / 36
Provider/model: qwen3-max / qwen3-max
Ran LLM: True

## Rank correlation vs expert (mean ± 95% bootstrap CI, n=2000)

| Selector | n | Kendall's tau | Spearman's rho | Top-1 accuracy | Parse fails |
|---|---:|---|---|---:|---:|
| llm_manifest | 36 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 100.0% | 0 |
| asm_topsis | 36 | 0.630 [0.370, 0.852] | 0.639 [0.375, 0.861] | 77.8% | 0 |
| llm_raw_doc | 36 | 0.315 [0.018, 0.611] | 0.319 [0.014, 0.611] | 63.9% | 0 |
