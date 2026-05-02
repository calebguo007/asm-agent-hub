# GLM-3: io_ratio Sensitivity Analysis

Generated: 2026-05-02T10:22:52Z

| Pair | Tau mean | 95% CI | Comparisons |
|------|----------|--------|-------------|
| 0.1->0.2 | 1.0000 | [1.0000, 1.0000] | 80 |
| 0.2->0.3 | 1.0000 | [1.0000, 1.0000] | 80 |
| 0.3->0.5 | 1.0000 | [1.0000, 1.0000] | 80 |
| 0.5->0.8 | 0.9833 | [0.9583, 1.0000] | 80 |
| 0.8->1.0 | 0.9917 | [0.9750, 1.0000] | 80 |
| 1.0->2.0 | 0.9500 | [0.8833, 1.0000] | 80 |

**Interpretation:** Stable range [0.2, 0.5] would confirm chat-scenario default is safe; degradation outside this band would warrant user-facing io_ratio config

**Stability note:** Stable range detected: [0.1, 2.0] (adjacent tau >= 0.90)
