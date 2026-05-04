#!/usr/bin/env python3
"""Correlate ASM-declared LLM quality with OpenRouter usage rankings.

OpenRouter publishes 7-day token-volume rankings by model variant — production
agents and applications voting with their wallets. This is "revealed
preference" at production scale, complementing LM Arena Elo (§6.8) which
measures pairwise human preference and Artificial Analysis (parked) which
measures benchmark suite performance.

For each LLM manifest we look up the closest OpenRouter slug and compute
Spearman / Kendall rank correlation between manifest declared quality and
OpenRouter prompt-token rank (lower rank number = more usage).

Usage:
    # First run the fetcher to produce openrouter_rankings.json
    python experiments/external_validation/fetch_openrouter_rankings.py \\
        --input-html /path/to/or_rank.html

    # Then this correlator
    python experiments/external_validation/correlate_openrouter.py
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCORER_DIR = str(ROOT / "scorer")
if SCORER_DIR not in sys.path:
    sys.path.insert(0, SCORER_DIR)

from scorer import load_manifests  # noqa: E402

OUTPUT_DIR = ROOT / "experiments" / "results" / "external_validation"
DEFAULT_OR_JSON = OUTPUT_DIR / "openrouter_rankings.json"


# Manifest service_id -> OpenRouter slug (most-recent dated variant).
# Multiple OR slugs may match a manifest; we pick the most-used.
ASM_TO_OR: dict[str, dict[str, object]] = {
    "openai/gpt-4o@2024-11-20": {
        "or_match": "openai/gpt-4o",
        "gap_note": "Closest GPT-4o family entry on OpenRouter; OR has multiple dated variants.",
    },
    "anthropic/claude-sonnet-4@4.0": {
        "or_match": "anthropic/claude-sonnet-4",
        "gap_note": "Sonnet 4 family match.",
    },
    "google/gemini-2.5-pro@2.5": {
        "or_match": "google/gemini-2.5-pro",
        "gap_note": "Direct match.",
    },
    "deepseek/deepseek-v4-flash@4.0": {
        "or_match": "deepseek/deepseek-v4-flash",
        "gap_note": "Direct match.",
    },
    "qwen/qwen3-max@3.0": {
        "or_match": "qwen/qwen3-max",
        "gap_note": "Direct match.",
    },
    "moonshot/kimi-k2.5@2.5": {
        "or_match": "moonshotai/kimi-k2.5",
        "gap_note": "Author rewritten moonshot -> moonshotai per OpenRouter convention.",
    },
    "zhipu/glm-5@5.0": {
        "or_match": "zhipu/glm-5",
        "gap_note": "May not appear on OpenRouter; falls back to closest GLM variant.",
    },
    "minimax/m2.7@2.7": {
        "or_match": "minimax/minimax-m2.7",
        "gap_note": "Direct match (with double-prefixed slug per OpenRouter convention).",
    },
}


def declared_quality(manifest: dict) -> tuple[float | None, str]:
    quality = manifest.get("quality") or {}
    metrics = quality.get("metrics") or []
    if not metrics:
        return None, "unknown"
    return float(metrics[0].get("score", 0)), str(metrics[0].get("name", "unknown"))


def find_or_record(slug_target: str, models: list[dict]) -> dict | None:
    """Find the most-used OpenRouter record matching the target slug.
    First try exact slug match; fall back to permaslug startswith; fall back
    to author-prefix match returning the highest-volume entry.
    """
    target = slug_target.lower()
    # 1. exact slug match
    for m in models:
        if m["slug"].lower() == target:
            return m
    # 2. permaslug starts with target
    for m in models:
        if m["permaslug"].lower().startswith(target):
            return m
    # 3. author prefix match → return highest-volume
    if "/" in target:
        author = target.split("/", 1)[0]
        candidates = [m for m in models if m["author"].lower() == author]
        if candidates:
            return max(candidates, key=lambda m: m["prompt_tokens"])
    return None


def spearman(x: list[float], y: list[float]) -> float:
    if len(x) < 2 or len(x) != len(y):
        return float("nan")
    n = len(x)
    rx = _rank(x)
    ry = _rank(y)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - (6 * d2) / (n * (n * n - 1))


def kendall_tau(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2 or n != len(y):
        return float("nan")
    c = d = 0
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            if dx * dy > 0:
                c += 1
            elif dx * dy < 0:
                d += 1
    total = n * (n - 1) // 2
    return (c - d) / total if total else float("nan")


def _rank(values: list[float]) -> list[float]:
    indexed = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and values[indexed[j + 1]] == values[indexed[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[indexed[k]] = avg
        i = j + 1
    return ranks


def bootstrap_ci(pairs, fn, n_boot=2000, alpha=0.05, seed=2026):
    rng = random.Random(seed)
    n = len(pairs)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    point = fn([p[0] for p in pairs], [p[1] for p in pairs])
    samples = []
    for _ in range(n_boot):
        s = [pairs[rng.randrange(n)] for _ in range(n)]
        v = fn([p[0] for p in s], [p[1] for p in s])
        if not math.isnan(v):
            samples.append(v)
    samples.sort()
    lo = samples[int(len(samples) * (alpha / 2))] if samples else float("nan")
    hi = samples[int(len(samples) * (1 - alpha / 2))] if samples else float("nan")
    return point, lo, hi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--openrouter-json", type=Path, default=DEFAULT_OR_JSON,
                        help="Path to openrouter_rankings.json from fetch_openrouter_rankings.py")
    parser.add_argument("--manifests", type=Path, default=ROOT / "manifests")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    if not args.openrouter_json.exists():
        sys.exit(f"Missing {args.openrouter_json}; run fetch_openrouter_rankings.py first.")

    or_data = json.loads(args.openrouter_json.read_text(encoding="utf-8"))
    models = or_data["models"]
    print(f"Loaded {len(models)} OpenRouter records (snapshot {or_data.get('generated_at')})", file=sys.stderr)

    manifest_map = {m["service_id"]: m for m in load_manifests(args.manifests)
                    if m.get("taxonomy") == "ai.llm.chat"}

    rows = []
    pairs_quality_vs_pt = []
    pairs_quality_vs_count = []
    for asm_id, mapping in ASM_TO_OR.items():
        manifest = manifest_map.get(asm_id)
        if manifest is None:
            print(f"  SKIP {asm_id}: manifest not found")
            continue
        q, metric = declared_quality(manifest)
        or_record = find_or_record(str(mapping["or_match"]), models)
        if or_record is None:
            print(f"  SKIP {asm_id}: no OpenRouter match for '{mapping['or_match']}'")
            continue
        rows.append({
            "asm_service_id": asm_id,
            "asm_quality_metric": metric,
            "asm_quality_score": q,
            "or_permaslug": or_record["permaslug"],
            "or_slug": or_record["slug"],
            "or_prompt_tokens": or_record["prompt_tokens"],
            "or_count": or_record["count"],
            "or_rank_by_prompt_tokens": or_record["rank_by_prompt_tokens"],
            "gap_note": mapping["gap_note"],
        })
        if q is not None:
            pairs_quality_vs_pt.append((q, float(or_record["prompt_tokens"])))
            pairs_quality_vs_count.append((q, float(or_record["count"])))

    rho_pt, lo_pt, hi_pt = bootstrap_ci(pairs_quality_vs_pt, spearman, seed=args.seed)
    tau_pt, _, _ = bootstrap_ci(pairs_quality_vs_pt, kendall_tau, seed=args.seed)
    rho_ct, lo_ct, hi_ct = bootstrap_ci(pairs_quality_vs_count, spearman, seed=args.seed)
    tau_ct, _, _ = bootstrap_ci(pairs_quality_vs_count, kendall_tau, seed=args.seed)

    summary = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "openrouter_snapshot": or_data.get("generated_at"),
        "n_manifests_attempted": len(ASM_TO_OR),
        "n_paired": len(pairs_quality_vs_pt),
        "quality_vs_prompt_tokens": {
            "spearman_rho": None if math.isnan(rho_pt) else round(rho_pt, 4),
            "spearman_ci95": None if math.isnan(lo_pt) else [round(lo_pt, 4), round(hi_pt, 4)],
            "kendall_tau": None if math.isnan(tau_pt) else round(tau_pt, 4),
        },
        "quality_vs_request_count": {
            "spearman_rho": None if math.isnan(rho_ct) else round(rho_ct, 4),
            "spearman_ci95": None if math.isnan(lo_ct) else [round(lo_ct, 4), round(hi_ct, 4)],
            "kendall_tau": None if math.isnan(tau_ct) else round(tau_ct, 4),
        },
        "rows": rows,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "openrouter_correlation.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    if rows:
        with (args.output_dir / "openrouter_correlation.csv").open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    lines = [
        "# ASM declared quality vs OpenRouter 7-day usage rankings",
        "",
        f"Generated: {summary['generated_at']}",
        f"OpenRouter snapshot: {summary['openrouter_snapshot']}",
        f"Paired: {len(pairs_quality_vs_pt)} / {len(ASM_TO_OR)} manifests matched",
        "",
        "## Headline correlations",
        "",
        f"- ASM quality vs OR prompt_tokens:  Spearman rho = **{summary['quality_vs_prompt_tokens']['spearman_rho']}** "
        f"(95% CI {summary['quality_vs_prompt_tokens']['spearman_ci95']}); Kendall tau = {summary['quality_vs_prompt_tokens']['kendall_tau']}",
        f"- ASM quality vs OR request_count: Spearman rho = **{summary['quality_vs_request_count']['spearman_rho']}** "
        f"(95% CI {summary['quality_vs_request_count']['spearman_ci95']}); Kendall tau = {summary['quality_vs_request_count']['kendall_tau']}",
        "",
        "## Per-pair detail",
        "",
        "| ASM service_id | ASM metric | ASM score | OR permaslug | Prompt-tokens | Requests | OR rank | Gap note |",
        "|---|---|---:|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['asm_service_id']}` | {r['asm_quality_metric']} | {r['asm_quality_score']} | "
            f"`{r['or_permaslug']}` | {r['or_prompt_tokens']/1e9:.2f}B | {r['or_count']:,} | {r['or_rank_by_prompt_tokens']} | "
            f"{r['gap_note']} |"
        )
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("- N = " + str(len(pairs_quality_vs_pt)) + " paired observations; CIs are wide. The headline ρ "
                 "is suggestive, not significant.")
    lines.append("- ASM-declared quality uses two different metrics across our 8 LLM manifests "
                 "(LMSYS_Elo for Western models, AA Intelligence for Chinese). The same heterogeneity "
                 "issue §6.5b/§6.8 surfaced applies; per-metric breakdown is omitted here because n per "
                 "metric is too small for OpenRouter rank correlation.")
    lines.append("- OpenRouter usage reflects production-traffic preference, which is jointly "
                 "determined by quality, price, latency, ecosystem fit, and ease of integration. A "
                 "weak correlation does not falsify ASM's quality dimension on its own; it would, "
                 "however, falsify a strong claim that 'quality is the only thing users vote on'.")
    (args.output_dir / "openrouter_correlation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
