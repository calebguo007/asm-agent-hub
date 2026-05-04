# GLM-3: io_ratio Sensitivity Analysis

Generated: 2026-05-04T10:23:12Z

| Pair | Tau mean | 95% CI | Comparisons |
|------|----------|--------|-------------|
| 0.1->0.2 | 1.0000 | [1.0000, 1.0000] | 80 |
| 0.2->0.3 | 1.0000 | [1.0000, 1.0000] | 80 |
| 0.3->0.5 | 0.9991 | [0.9973, 1.0000] | 80 |
| 0.5->0.8 | 0.9955 | [0.9866, 1.0000] | 80 |
| 0.8->1.0 | 0.9964 | [0.9902, 1.0000] | 80 |

**Interpretation:** Rankings remain stable across the valid [0.1, 1.0] range; io_ratio is safe to expose as a task hint rather than a precomputed field

**Stability note:** Stable range detected: [0.1, 1.0] (adjacent tau >= 0.90)
