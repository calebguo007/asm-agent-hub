# Selection Baseline and Regret Evaluation

Generated at: 2026-05-04T10:43:59Z
Tasks: 200
Seed: 2024

Regret is computed as `utility(best feasible service) - utility(selected service)` under the task's preference vector. Lower is better; zero means the strategy selected a utility-optimal service for that candidate set.

| Strategy | Utility mean | Regret mean | Zero-regret rate | Cost mean | Latency mean | Quality mean |
|---|---:|---:|---:|---:|---:|---:|
| asm_topsis | 0.9265 | 0.0000 | 100.0% | 0.0058009512 | 6.8586 | 0.6215 |
| fastest_first | 0.8559 | 0.0706 | 82.5% | 0.0212650656 | 5.4904 | 0.6205 |
| weighted_average | 0.8545 | 0.0720 | 82.0% | 0.0178043594 | 5.8025 | 0.6272 |
| cheapest_first | 0.6724 | 0.2541 | 71.0% | 0.0057809406 | 6.8615 | 0.6149 |
| random | 0.5422 | 0.3843 | 51.0% | 0.0154391178 | 6.3242 | 0.5850 |
| highest_quality_first | 0.4270 | 0.4995 | 33.0% | 0.0216596447 | 5.9288 | 0.6564 |
| most_expensive_first | 0.2154 | 0.7112 | 15.0% | 0.0220168655 | 6.0715 | 0.5780 |
