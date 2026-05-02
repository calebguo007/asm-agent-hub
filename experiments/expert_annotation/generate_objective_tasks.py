#!/usr/bin/env python3
"""Generate tasks_objective.yaml from manifests, no human annotation required.

Ground truth ranking is derived from objective fields:
  - cost axis: pricing.billing_dimensions[*].cost_per_unit (ascending)
  - latency axis: sla.latency_p50 normalised to ms (ascending)
  - quality axis: shared quality.metrics[].score per taxonomy (descending where
    higher-is-better; ascending for FID-like lower-is-better)

Trust axis is intentionally skipped — there is no objective public source.

For each (taxonomy, axis) pair where:
  - the taxonomy has >= 2 candidate manifests
  - all candidates contain the relevant field
  - quality requires a SHARED benchmark name across all candidates
the script emits one task entry.

The resulting YAML can be fed directly into run_ranking_experiment.py.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent.parent
_SCORER_DIR = str(_ROOT / "scorer")
if _SCORER_DIR not in sys.path:
    sys.path.insert(0, _SCORER_DIR)

from scorer import load_manifests  # noqa: E402


# ---- field extractors ------------------------------------------------------

def _latency_to_ms(text: str | None) -> float | None:
    if not text:
        return None
    s = str(text).strip().lower()
    m = re.match(r"([\d.]+)\s*(ms|s|sec|seconds?)?$", s)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2) or ""
    if unit in ("s", "sec", "second", "seconds"):
        val *= 1000
    return val


def _primary_cost(manifest: dict[str, Any]) -> tuple[float, str] | None:
    pricing = manifest.get("pricing") or {}
    dims = pricing.get("billing_dimensions") or []
    if not dims:
        return None
    # Primary dimension: prefer the first non-zero, fall back to the first.
    for dim in dims:
        cost = dim.get("cost_per_unit")
        if cost is not None and float(cost) > 0:
            return float(cost), dim.get("dimension", "")
    dim = dims[0]
    cost = dim.get("cost_per_unit")
    if cost is None:
        return None
    return float(cost), dim.get("dimension", "")


def _primary_quality(manifest: dict[str, Any]) -> tuple[str, float, bool] | None:
    """Return (benchmark_name, score, lower_is_better) for the first metric."""
    quality = manifest.get("quality") or {}
    metrics = quality.get("metrics") or []
    for metric in metrics:
        name = metric.get("name") or metric.get("benchmark")
        score = metric.get("score")
        if not name or score is None:
            continue
        scale = (metric.get("scale") or "").lower()
        lower_is_better = "lower" in scale or name.upper() == "FID"
        return str(name), float(score), lower_is_better
    return None


# ---- task builder ----------------------------------------------------------

def build_tasks(manifests: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    by_taxonomy: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for m in manifests:
        if "taxonomy" in m and "service_id" in m:
            by_taxonomy[m["taxonomy"]].append(m)

    tasks: list[dict[str, Any]] = []
    notes: list[str] = []
    task_id = 0

    for taxonomy in sorted(by_taxonomy):
        candidates = sorted(by_taxonomy[taxonomy], key=lambda m: m["service_id"])
        if len(candidates) < 2:
            continue

        # Cost-axis task -----------------------------------------------------
        cost_data = []
        common_dim: str | None = None
        skip_cost_reason: str | None = None
        for c in candidates:
            cd = _primary_cost(c)
            if cd is None:
                skip_cost_reason = f"  cost-skip {taxonomy}: {c['service_id']} has no cost_per_unit"
                break
            cost, dim = cd
            if common_dim is None:
                common_dim = dim
            elif dim != common_dim:
                skip_cost_reason = f"  cost-skip {taxonomy}: dimension mismatch ({common_dim} vs {dim})"
                break
            cost_data.append((c["service_id"], cost))
        if skip_cost_reason:
            notes.append(skip_cost_reason)
        elif cost_data and len({c for _, c in cost_data}) > 1:  # need spread
            cost_data.sort(key=lambda t: t[1])
            task_id += 1
            tasks.append({
                "id": task_id,
                "taxonomy": taxonomy,
                "preference_axis": "cost",
                "candidates": [sid for sid, _ in cost_data],
                "expert_rank": [sid for sid, _ in cost_data],  # ascending = cheapest first = best
                "rationale": f"objective: sort by cost_per_unit ({common_dim})",
                "ground_truth_source": "manifest.pricing.billing_dimensions",
            })
        else:
            notes.append(f"  cost-skip {taxonomy}: no spread (all candidates same price or zero)")

        # Latency-axis task --------------------------------------------------
        lat_data = []
        skip_lat = False
        for c in candidates:
            sla = c.get("sla") or {}
            ms = _latency_to_ms(sla.get("latency_p50"))
            if ms is None:
                notes.append(f"  latency-skip {taxonomy}: {c['service_id']} no latency_p50")
                skip_lat = True
                break
            lat_data.append((c["service_id"], ms))
        if not skip_lat and lat_data and len({m for _, m in lat_data}) > 1:
            lat_data.sort(key=lambda t: t[1])
            task_id += 1
            tasks.append({
                "id": task_id,
                "taxonomy": taxonomy,
                "preference_axis": "latency",
                "candidates": [sid for sid, _ in lat_data],
                "expert_rank": [sid for sid, _ in lat_data],
                "rationale": "objective: sort by sla.latency_p50 ascending",
                "ground_truth_source": "manifest.sla.latency_p50",
            })

        # Quality-axis task --------------------------------------------------
        quality_data = []
        common_bench: str | None = None
        common_lib: bool | None = None
        skip_q_reason: str | None = None
        for c in candidates:
            q = _primary_quality(c)
            if q is None:
                skip_q_reason = f"  quality-skip {taxonomy}: {c['service_id']} no quality.metrics"
                break
            name, score, lib = q
            if common_bench is None:
                common_bench, common_lib = name, lib
            elif name != common_bench:
                skip_q_reason = f"  quality-skip {taxonomy}: benchmark mismatch ({common_bench} vs {name})"
                break
            quality_data.append((c["service_id"], score))
        if skip_q_reason:
            notes.append(skip_q_reason)
        elif quality_data and len({s for _, s in quality_data}) > 1:
            # higher is better unless lower_is_better flag set
            quality_data.sort(key=lambda t: t[1], reverse=not common_lib)
            task_id += 1
            tasks.append({
                "id": task_id,
                "taxonomy": taxonomy,
                "preference_axis": "quality",
                "candidates": [sid for sid, _ in quality_data],
                "expert_rank": [sid for sid, _ in quality_data],
                "rationale": f"objective: sort by {common_bench} ({'lower better' if common_lib else 'higher better'})",
                "ground_truth_source": f"manifest.quality.metrics[name={common_bench}]",
            })
    return tasks, notes


def emit_yaml(tasks: list[dict[str, Any]], output_path: Path) -> None:
    lines = ["# tasks_objective.yaml", "# Auto-generated. Do not hand-edit; regenerate via generate_objective_tasks.py.", "tasks:"]
    for t in tasks:
        lines.append(f"  - id: {t['id']}")
        lines.append(f"    taxonomy: {t['taxonomy']}")
        lines.append(f"    preference_axis: {t['preference_axis']}")
        lines.append(f"    candidates: [{', '.join(t['candidates'])}]")
        lines.append(f"    expert_rank: [{', '.join(t['expert_rank'])}]")
        lines.append(f"    rationale: \"{t['rationale']}\"")
        lines.append(f"    ground_truth_source: \"{t['ground_truth_source']}\"")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    manifests = load_manifests(_ROOT / "manifests")
    tasks, notes = build_tasks(manifests)
    out_dir = Path(__file__).resolve().parent
    emit_yaml(tasks, out_dir / "tasks_objective.yaml")

    # Write a coverage report so we can defend the task selection in the paper.
    by_axis: dict[str, list[str]] = defaultdict(list)
    for t in tasks:
        by_axis[t["preference_axis"]].append(t["taxonomy"])

    report = ["# Objective tasks coverage", ""]
    report.append(f"Total tasks: **{len(tasks)}**")
    for axis in ("cost", "latency", "quality"):
        report.append(f"\n## {axis} axis ({len(by_axis[axis])} tasks)")
        for tax in by_axis[axis]:
            report.append(f"- {tax}")
    if notes:
        report.append("\n## Skipped (with reason)")
        for n in notes:
            report.append(n)
    (out_dir / "tasks_objective_coverage.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Generated {len(tasks)} tasks")
    print(f"  cost: {len(by_axis['cost'])}, latency: {len(by_axis['latency'])}, quality: {len(by_axis['quality'])}")
    print(f"  Skipped: {len(notes)} entries (see tasks_objective_coverage.md)")


if __name__ == "__main__":
    main()
