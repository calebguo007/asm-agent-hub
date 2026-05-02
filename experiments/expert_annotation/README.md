# Expert Annotation Experiment (P0-1)

**Goal**: produce a non-circular ground truth for the LLM-as-selector experiment, then measure rank-correlation between expert ranking, ASM-TOPSIS ranking, and LLM-on-raw-docs ranking.

## Methodology

1. **30 hand-curated tasks** across 5 categories (10 LLM-class, 5 search/scrape, 5 storage/DB/GPU, 5 communication/todo, 5 DevOps/productivity).
2. **Each task** specifies: realistic agent goal, 2–3 candidate services, primary preference axis (cost / latency / quality / trust).
3. **Expert (Caleb) ranks** all candidates 1..N (1 = best) and writes a one-line rationale. Rationale is for self-discipline; not used in the paper.
4. **Three selectors run on the same tasks**:
   - `expert` (ground truth) — from `tasks.yaml` after annotation.
   - `asm_topsis` — deterministic, derived from full ASM manifests.
   - `llm_raw_doc` — Chinese LLM (DeepSeek / Qwen / GLM-4 / Kimi) sees only public source snippets per `provenance.source_url`, must produce a full ranking.
   - `llm_manifest` — same LLM sees compact ASM manifest, must produce a full ranking.
5. **Metric**: Kendall's tau and Spearman's rho between each selector's ranking and the expert ranking, aggregated across the 30 tasks. Bootstrap 95% CIs (n=2000).

## Hypothesis

`tau(asm_topsis, expert)` ≥ `tau(llm_manifest, expert)` > `tau(llm_raw_doc, expert)` significantly.

If `tau(llm_raw_doc, expert)` is already high, the protocol's claimed value is weakened and we revise the paper's framing.

## Why ranks not picks

Picks (top-1 accuracy) collapse useful information. Ranks let us detect cases where the LLM is "almost right" (picks #2 instead of #1) versus "completely wrong" (picks #N), which matters for a settlement protocol where regret is continuous.

## Files

- `tasks.template.md` — generated task sheet. Fill in `expert_rank` and `rationale` columns.
- `tasks.yaml` — machine-readable version (you create this from the markdown after annotating).
- `run_ranking_experiment.py` — runs LLM and computes correlations.
- `results/` — output CSVs and report.

## Cost estimate

- 30 tasks × 2 surfaces (raw_doc + manifest) × 1 run = 60 LLM calls
- Avg prompt ~6k tokens (raw_doc), ~2k tokens (manifest). Output ~300 tokens.
- DeepSeek-V3: ¥1/M input, ¥2/M output → ~¥0.5 total
- Qwen-Max: ¥0.024/1k input, ¥0.096/1k output → ~¥30 total
- Kimi-K2: ¥0.6/M input, ¥2.5/M output → ~¥0.5 total

Recommend DeepSeek-V3 as primary (best quality/cost ratio for instruction-following).
