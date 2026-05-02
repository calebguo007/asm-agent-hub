#!/usr/bin/env python3
"""Expert-annotated rank-correlation experiment.

Reads tasks.yaml with expert rankings, runs three selectors on each task
(asm_topsis, llm_raw_doc, llm_manifest), and computes Kendall's tau and
Spearman's rho versus the expert ranking.

LLM provider is OpenAI-compatible. Tested with DeepSeek, Qwen, Kimi, GLM-4.

Usage:
    # Dry run (no API call): generate prompts only, run TOPSIS only.
    python run_ranking_experiment.py

    # Live run with DeepSeek:
    export DEEPSEEK_API_KEY=sk-...
    python run_ranking_experiment.py \
        --provider deepseek \
        --model deepseek-chat \
        --base-url https://api.deepseek.com/v1 \
        --api-key-env DEEPSEEK_API_KEY
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import random
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_ROOT = Path(__file__).resolve().parent.parent.parent
_SCORER_DIR = str(_ROOT / "scorer")
if _SCORER_DIR not in sys.path:
    sys.path.insert(0, _SCORER_DIR)

from scorer import (  # noqa: E402
    Preferences,
    ServiceVector,
    load_manifests,
    parse_manifest,
    score_topsis,
)


# Map preference axis -> Preferences weights.
AXIS_TO_PREFS: dict[str, Preferences] = {
    "cost": Preferences(cost=0.55, quality=0.20, speed=0.15, reliability=0.10),
    "latency": Preferences(cost=0.15, quality=0.20, speed=0.55, reliability=0.10),
    "quality": Preferences(cost=0.15, quality=0.55, speed=0.15, reliability=0.15),
    "trust": Preferences(cost=0.15, quality=0.20, speed=0.15, reliability=0.50),
}


@dataclass
class Task:
    id: int
    taxonomy: str
    preference_axis: str
    candidates: list[str]
    expert_rank: list[str]
    rationale: str = ""


@dataclass
class Result:
    task_id: int
    taxonomy: str
    preference_axis: str
    selector: str
    predicted_rank: list[str]
    kendall_tau: float
    spearman_rho: float
    top1_match: bool
    parse_failure: bool
    prompt_chars: int
    completion_chars: int
    raw_response: str = ""


# ---------------------------------------------------------------------------
# Tiny YAML loader (no PyYAML dependency).

def _yaml_loads(text: str) -> dict[str, Any]:
    """Minimal YAML loader that handles the tasks.yaml shape we emit."""
    try:
        import yaml  # type: ignore[import-untyped]
        return yaml.safe_load(text)
    except ImportError:
        pass

    # Fallback: parse the well-defined shape:
    #   tasks:
    #     - id: 1
    #       taxonomy: ai.llm.chat
    #       preference_axis: quality
    #       candidates: [a, b, c]
    #       expert_rank: [c, a, b]
    #       rationale: "..."
    out: dict[str, Any] = {"tasks": []}
    current: dict[str, Any] | None = None
    in_tasks = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("tasks:"):
            in_tasks = True
            continue
        if not in_tasks:
            continue
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("- "):
            if current is not None:
                out["tasks"].append(current)
            current = {}
            stripped = stripped[2:]
            if ":" in stripped:
                k, _, v = stripped.partition(":")
                current[k.strip()] = _yaml_value(v.strip())
            continue
        if current is None:
            continue
        if ":" in stripped:
            k, _, v = stripped.partition(":")
            current[k.strip()] = _yaml_value(v.strip())
    if current is not None:
        out["tasks"].append(current)
    return out


def _yaml_value(text: str) -> Any:
    if text == "" or text == "~" or text == "null":
        return None
    if text.startswith("[") and text.endswith("]"):
        body = text[1:-1].strip()
        if not body:
            return []
        return [item.strip().strip('"').strip("'") for item in body.split(",")]
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


# ---------------------------------------------------------------------------
# Source fetching for raw_doc surface.

def _slug_for_url(url: str) -> str:
    parsed = urlparse(url)
    base = f"{parsed.netloc}{parsed.path}".strip("/") or "unknown"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", base)[:140]


def _strip_html(text: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_source_text(url: str, cache_dir: Path, max_chars: int) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{_slug_for_url(url or 'unknown')}.txt"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    text = ""
    if url:
        try:
            req = Request(url, headers={"User-Agent": "asm-ranking-baseline"})
            with urlopen(req, timeout=10) as response:
                raw = response.read(300_000).decode("utf-8", errors="replace")
                text = _strip_html(raw)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            text = f"[source unavailable: {type(exc).__name__}] {url}"
    if not text:
        text = f"[source unavailable] {url}"
    cache_path.write_text(text, encoding="utf-8")
    return text[:max_chars]


# ---------------------------------------------------------------------------
# Prompt construction.

_SYSTEM_PROMPT = (
    "You are a strict service ranker. Given a task and N candidates, return only "
    "JSON of the form {\"ranking\": [<service_id_best>, ..., <service_id_worst>]}. "
    "Do not include any other keys, prose, or markdown fencing."
)


def task_header(task: Task) -> str:
    return (
        f"Taxonomy: {task.taxonomy}\n"
        f"Preference axis: {task.preference_axis}\n"
        f"Candidates ({len(task.candidates)}): {', '.join(task.candidates)}\n"
        "Rank ALL candidates from best to worst under the stated preference axis. "
        "Use exactly the service_ids above."
    )


def compact_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "service_id",
        "taxonomy",
        "display_name",
        "provider",
        "capabilities",
        "pricing",
        "quality",
        "sla",
        "payment",
        "provenance",
    )
    return {key: manifest[key] for key in keys if key in manifest}


def candidate_source_url(manifest: dict[str, Any]) -> str:
    return (
        ((manifest.get("provenance") or {}).get("source_url"))
        or ((manifest.get("provider") or {}).get("url"))
        or ((manifest.get("payment") or {}).get("signup_url"))
        or ""
    )


def build_manifest_prompt(task: Task, manifests: dict[str, dict[str, Any]]) -> str:
    payload = [compact_manifest(manifests[c]) for c in task.candidates if c in manifests]
    return task_header(task) + "\n\nASM manifests:\n" + json.dumps(payload, indent=2)


def build_raw_doc_prompt(
    task: Task,
    manifests: dict[str, dict[str, Any]],
    cache_dir: Path,
    per_candidate_chars: int,
) -> str:
    parts = [task_header(task), "\nRaw public source snippets:"]
    for cid in task.candidates:
        manifest = manifests.get(cid, {})
        source_url = candidate_source_url(manifest)
        snippet = fetch_source_text(source_url, cache_dir, per_candidate_chars)
        parts.append(
            "\n---\n"
            f"service_id: {cid}\n"
            f"source_url: {source_url}\n"
            f"source_excerpt:\n{snippet}"
        )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# LLM call (OpenAI-compatible).

def call_llm(prompt: str, model: str, api_key: str, base_url: str, temperature: float) -> str:
    body = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(body).encode("utf-8")
    req = Request(
        base_url.rstrip("/") + "/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]


def parse_ranking(text: str, candidates: list[str]) -> tuple[list[str], bool]:
    """Extract ranking list. Returns ([], True) on parse failure."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        data = json.loads(cleaned)
        ranking = data.get("ranking") or data.get("rank") or []
        ranking = [str(x).strip() for x in ranking if str(x).strip()]
    except json.JSONDecodeError:
        # Fallback: scan for known service_ids in order of appearance.
        ranking = []
        seen: set[str] = set()
        for cid in sorted(candidates, key=len, reverse=True):
            for match in re.finditer(re.escape(cid), text):
                if cid not in seen:
                    ranking.append(cid)
                    seen.add(cid)
                break
    valid = [c for c in ranking if c in candidates]
    if len(set(valid)) != len(candidates):
        return valid, True
    return valid, False


# ---------------------------------------------------------------------------
# Rank correlation.

def kendall_tau(a: list[str], b: list[str]) -> float:
    """Kendall's tau-b between two rankings of the same items."""
    if len(a) != len(b) or sorted(a) != sorted(b):
        return float("nan")
    n = len(a)
    if n < 2:
        return float("nan")
    rank_a = {item: i for i, item in enumerate(a)}
    rank_b = {item: i for i, item in enumerate(b)}
    items = list(a)
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            x = rank_a[items[i]] - rank_a[items[j]]
            y = rank_b[items[i]] - rank_b[items[j]]
            if x * y > 0:
                concordant += 1
            elif x * y < 0:
                discordant += 1
    total = n * (n - 1) // 2
    if total == 0:
        return float("nan")
    return (concordant - discordant) / total


def spearman_rho(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or sorted(a) != sorted(b):
        return float("nan")
    n = len(a)
    if n < 2:
        return float("nan")
    rank_a = {item: i for i, item in enumerate(a)}
    rank_b = {item: i for i, item in enumerate(b)}
    d2 = sum((rank_a[item] - rank_b[item]) ** 2 for item in a)
    return 1 - (6 * d2) / (n * (n * n - 1))


def bootstrap_mean_ci(values: list[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 2024) -> tuple[float, float, float]:
    if not values:
        return float("nan"), float("nan"), float("nan")
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(sum(sample) / len(sample))
    means.sort()
    lo = means[int(n_boot * (alpha / 2))]
    hi = means[int(n_boot * (1 - alpha / 2))]
    return sum(values) / len(values), lo, hi


# ---------------------------------------------------------------------------
# Selector dispatch.

def topsis_ranking(task: Task, manifests: dict[str, dict[str, Any]]) -> list[str]:
    vectors = [parse_manifest(manifests[c]) for c in task.candidates if c in manifests]
    prefs = AXIS_TO_PREFS[task.preference_axis]
    return [r.service.service_id for r in score_topsis(vectors, prefs)]


def evaluate(predicted: list[str], expert: list[str]) -> tuple[float, float, bool, bool]:
    parse_failure = sorted(predicted) != sorted(expert)
    if parse_failure:
        return float("nan"), float("nan"), False, True
    return kendall_tau(predicted, expert), spearman_rho(predicted, expert), predicted[0] == expert[0], False


# ---------------------------------------------------------------------------
# Main.

def main() -> None:
    parser = argparse.ArgumentParser(description="Run rank-correlation experiment against expert annotations.")
    parser.add_argument("--tasks-file", type=Path, default=Path(__file__).resolve().parent / "tasks.yaml")
    parser.add_argument("--manifests", type=Path, default=_ROOT / "manifests")
    parser.add_argument("--cache-dir", type=Path, default=Path(__file__).resolve().parent / "cache" / "raw_docs")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "results")
    parser.add_argument("--max-source-chars", type=int, default=8000)
    parser.add_argument("--provider", default=None, help="Provider label (e.g. deepseek/qwen/kimi/glm). Used for output only.")
    parser.add_argument("--model", default=None, help="Model name passed to the API.")
    parser.add_argument("--base-url", default=None, help="OpenAI-compatible base URL.")
    parser.add_argument("--api-key-env", default="DEEPSEEK_API_KEY", help="Env var holding the API key.")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--surfaces", nargs="+", choices=["raw_doc", "manifest"], default=["raw_doc", "manifest"])
    parser.add_argument("--seed", type=int, default=2024)
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls; only TOPSIS evaluated.")
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env or "")
    run_llm = bool(args.provider and args.model and args.base_url and api_key) and not args.dry_run

    if not args.tasks_file.exists():
        sys.exit(f"tasks file not found: {args.tasks_file}\nFill in tasks.template.md and copy rankings into tasks.yaml first.")

    tasks_data = _yaml_loads(args.tasks_file.read_text(encoding="utf-8"))
    tasks: list[Task] = []
    for entry in tasks_data.get("tasks", []):
        tasks.append(Task(
            id=int(entry["id"]),
            taxonomy=str(entry["taxonomy"]),
            preference_axis=str(entry["preference_axis"]),
            candidates=list(entry["candidates"]),
            expert_rank=list(entry["expert_rank"]),
            rationale=str(entry.get("rationale") or ""),
        ))

    # Drop tasks the user has not yet annotated (placeholder ?s).
    annotated = [t for t in tasks if all(c and c != "?" for c in t.expert_rank) and sorted(t.expert_rank) == sorted(t.candidates)]
    if len(annotated) < len(tasks):
        print(f"Skipping {len(tasks) - len(annotated)} unannotated/inconsistent tasks.", file=sys.stderr)

    manifests_list = load_manifests(args.manifests)
    manifests_map = {m["service_id"]: m for m in manifests_list}

    results: list[Result] = []
    for task in annotated:
        # asm_topsis
        topsis_rank = topsis_ranking(task, manifests_map)
        tau, rho, top1, fail = evaluate(topsis_rank, task.expert_rank)
        results.append(Result(task.id, task.taxonomy, task.preference_axis, "asm_topsis",
                              topsis_rank, tau, rho, top1, fail, 0, 0, ""))

        if not run_llm:
            continue

        per_candidate_chars = max(500, args.max_source_chars // max(len(task.candidates), 1))
        for surface in args.surfaces:
            if surface == "manifest":
                prompt = build_manifest_prompt(task, manifests_map)
                selector_name = "llm_manifest"
            else:
                prompt = build_raw_doc_prompt(task, manifests_map, args.cache_dir, per_candidate_chars)
                selector_name = "llm_raw_doc"
            try:
                response = call_llm(prompt, args.model, api_key, args.base_url, args.temperature)
            except Exception as exc:
                print(f"  task {task.id} {selector_name}: LLM call failed: {exc}", file=sys.stderr)
                results.append(Result(task.id, task.taxonomy, task.preference_axis, selector_name,
                                      [], float("nan"), float("nan"), False, True,
                                      len(prompt), 0, str(exc)[:200]))
                continue
            ranking, parse_fail = parse_ranking(response, task.candidates)
            if parse_fail or sorted(ranking) != sorted(task.candidates):
                results.append(Result(task.id, task.taxonomy, task.preference_axis, selector_name,
                                      ranking, float("nan"), float("nan"), False, True,
                                      len(prompt), len(response), response[:300]))
            else:
                tau, rho, top1, _ = evaluate(ranking, task.expert_rank)
                results.append(Result(task.id, task.taxonomy, task.preference_axis, selector_name,
                                      ranking, tau, rho, top1, False,
                                      len(prompt), len(response), response[:300]))
            time.sleep(0.4)

    # Summarise.
    args.output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary: dict[str, Any] = {
        "generated_at": generated_at,
        "tasks_total": len(tasks),
        "tasks_evaluated": len(annotated),
        "provider": args.provider,
        "model": args.model,
        "ran_llm": run_llm,
        "selectors": {},
    }
    for selector in sorted({r.selector for r in results}):
        rows = [r for r in results if r.selector == selector and not r.parse_failure and not math.isnan(r.kendall_tau)]
        taus = [r.kendall_tau for r in rows]
        rhos = [r.spearman_rho for r in rows]
        top1 = [1 if r.top1_match else 0 for r in rows]
        tau_mean, tau_lo, tau_hi = bootstrap_mean_ci(taus, seed=args.seed)
        rho_mean, rho_lo, rho_hi = bootstrap_mean_ci(rhos, seed=args.seed)
        summary["selectors"][selector] = {
            "n": len(rows),
            "parse_failures": sum(1 for r in results if r.selector == selector and r.parse_failure),
            "kendall_tau_mean": round(tau_mean, 4),
            "kendall_tau_ci95": [round(tau_lo, 4), round(tau_hi, 4)],
            "spearman_rho_mean": round(rho_mean, 4),
            "spearman_rho_ci95": [round(rho_lo, 4), round(rho_hi, 4)],
            "top1_accuracy": round(sum(top1) / len(top1), 4) if top1 else float("nan"),
        }

    csv_path = args.output_dir / "ranking_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        if results:
            writer = csv.DictWriter(fp, fieldnames=list(asdict(results[0]).keys()))
            writer.writeheader()
            for r in results:
                row = asdict(r)
                row["predicted_rank"] = json.dumps(row["predicted_rank"])
                writer.writerow(row)

    (args.output_dir / "ranking_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Markdown report.
    lines = [
        "# Expert Annotation Ranking Experiment",
        "",
        f"Generated: {generated_at}",
        f"Tasks evaluated: {summary['tasks_evaluated']} / {summary['tasks_total']}",
        f"Provider/model: {args.provider or 'n/a'} / {args.model or 'n/a'}",
        f"Ran LLM: {run_llm}",
        "",
        "## Rank correlation vs expert (mean ± 95% bootstrap CI, n=2000)",
        "",
        "| Selector | n | Kendall's tau | Spearman's rho | Top-1 accuracy | Parse fails |",
        "|---|---:|---|---|---:|---:|",
    ]
    for selector, stats in sorted(summary["selectors"].items(), key=lambda kv: -kv[1]["kendall_tau_mean"]):
        tau_lo, tau_hi = stats["kendall_tau_ci95"]
        rho_lo, rho_hi = stats["spearman_rho_ci95"]
        lines.append(
            f"| {selector} | {stats['n']} | "
            f"{stats['kendall_tau_mean']:.3f} [{tau_lo:.3f}, {tau_hi:.3f}] | "
            f"{stats['spearman_rho_mean']:.3f} [{rho_lo:.3f}, {rho_hi:.3f}] | "
            f"{stats['top1_accuracy']*100:.1f}% | {stats['parse_failures']} |"
        )
    (args.output_dir / "ranking_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if not run_llm:
        print(
            f"\n[dry-run] LLM calls skipped. Set --provider/--model/--base-url and "
            f"export {args.api_key_env} to evaluate llm_raw_doc and llm_manifest.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
