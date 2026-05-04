# Live Execution: Chinese-LLM gateway

Generated: 2026-05-03T14:58:23Z
Tasks: 30
Gateway: https://tokendance.space/gateway/v1
Judge model: glm-4.7
LLM-picker model: qwen3-max

## Aggregate by selector (lower cost / latency / violation rates better; higher judge score better)

| Selector | n | Judge mean | Total cost (USD) | Mean latency (s) | Cost-viol | Latency-viol | Quality-viol |
|---|---:|---:|---:|---:|---:|---:|---:|
| cheapest_first | 29 | 9.65 | $0.0064 | 9.80 | 0% | 10% | 0% |
| weighted_average | 29 | 9.31 | $0.0370 | 23.60 | 0% | 21% | 0% |
| asm_topsis | 30 | 9.27 | $0.0064 | 7.64 | 0% | 10% | 0% |
| llm_picker_raw_doc | 30 | 9.23 | $0.0087 | 10.53 | 0% | 10% | 0% |
| llm_picker_manifest | 28 | 9.21 | $0.0275 | 16.83 | 0% | 14% | 4% |
| random | 29 | 9.21 | $0.0459 | 25.92 | 0% | 14% | 0% |
