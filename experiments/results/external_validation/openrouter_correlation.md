# ASM declared quality vs OpenRouter 7-day usage rankings

Generated: 2026-05-04T11:41:32Z
OpenRouter snapshot: 2026-05-04T11:41:31Z
Paired: 7 / 8 manifests matched

## Headline correlations

- ASM quality vs OR prompt_tokens:  Spearman rho = **0.1429** (95% CI [-0.5357, 1.0]); Kendall tau = 0.1429
- ASM quality vs OR request_count: Spearman rho = **-0.1429** (95% CI [-0.7857, 1.0]); Kendall tau = -0.0476

## Per-pair detail

| ASM service_id | ASM metric | ASM score | OR permaslug | Prompt-tokens | Requests | OR rank | Gap note |
|---|---|---:|---|---:|---:|---:|---|
| `openai/gpt-4o@2024-11-20` | LMSYS_Elo | 1285.0 | `openai/gpt-4o` | 16.34B | 6,572,541 | 95 | Closest GPT-4o family entry on OpenRouter; OR has multiple dated variants. |
| `anthropic/claude-sonnet-4@4.0` | LMSYS_Elo | 1290.0 | `anthropic/claude-4.6-sonnet-20260217` | 1324.64B | 37,214,202 | 3 | Sonnet 4 family match. |
| `google/gemini-2.5-pro@2.5` | LMSYS_Elo | 1300.0 | `google/gemini-2.5-pro` | 66.00B | 6,805,172 | 54 | Direct match. |
| `deepseek/deepseek-v4-flash@4.0` | Artificial_Analysis_Intelligence | 53.0 | `deepseek/deepseek-v4-flash-20260423` | 675.73B | 45,561,398 | 9 | Direct match. |
| `qwen/qwen3-max@3.0` | Artificial_Analysis_Intelligence | 56.0 | `qwen/qwen3-max` | 1.75B | 215,494 | 179 | Direct match. |
| `moonshot/kimi-k2.5@2.5` | Artificial_Analysis_Intelligence | 60.0 | `moonshotai/kimi-k2.5-0127` | 270.17B | 13,224,950 | 23 | Author rewritten moonshot -> moonshotai per OpenRouter convention. |
| `minimax/m2.7@2.7` | MMLU | 78.0 | `minimax/minimax-m2.7-20260318` | 711.69B | 25,796,726 | 8 | Direct match (with double-prefixed slug per OpenRouter convention). |

## Caveats

- N = 7 paired observations; CIs are wide. The headline ρ is suggestive, not significant.
- ASM-declared quality uses two different metrics across our 8 LLM manifests (LMSYS_Elo for Western models, AA Intelligence for Chinese). The same heterogeneity issue §6.5b/§6.8 surfaced applies; per-metric breakdown is omitted here because n per metric is too small for OpenRouter rank correlation.
- OpenRouter usage reflects production-traffic preference, which is jointly determined by quality, price, latency, ecosystem fit, and ease of integration. A weak correlation does not falsify ASM's quality dimension on its own; it would, however, falsify a strong claim that 'quality is the only thing users vote on'.
