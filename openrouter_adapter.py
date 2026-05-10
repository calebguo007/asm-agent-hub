#!/usr/bin/env python3
"""OpenRouter-to-ASM ephemeral manifest adapter.

This adapter is intentionally opportunistic: it maps OpenRouter model metadata
into temporary ASM manifests so the normal ASM scorer can rank LLM APIs without
requiring providers to publish manifests first.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
OPENROUTER_RANKINGS_URL = "https://openrouter.ai/rankings"
DEFAULT_RANKINGS_JSON = ROOT / "experiments" / "results" / "external_validation" / "openrouter_rankings.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_openrouter_models(models_json: str | Path | None = None, timeout: int = 20) -> tuple[list[dict], str, str]:
    """Load OpenRouter model records from a JSON cache or the public API."""
    retrieved_at = utc_now()
    if models_json:
        path = Path(models_json)
        data = json.loads(path.read_text(encoding="utf-8"))
        source = f"file:{path}"
    else:
        req = Request(OPENROUTER_MODELS_URL, headers={"User-Agent": "asm-openrouter-adapter/0.1"})
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        source = OPENROUTER_MODELS_URL

    if isinstance(data, dict):
        models = data.get("data", [])
    elif isinstance(data, list):
        models = data
    else:
        raise ValueError("OpenRouter models payload must be an object with data[] or a model list")

    return list(models), source, retrieved_at


def load_openrouter_rankings(rankings_json: str | Path | None = None) -> tuple[dict[str, dict], int, str | None]:
    """Load cached OpenRouter usage rankings keyed by normalized model id."""
    path = Path(rankings_json) if rankings_json else DEFAULT_RANKINGS_JSON
    if not path.exists():
        return {}, 0, None

    data = json.loads(path.read_text(encoding="utf-8"))
    models = data.get("models", [])
    by_slug: dict[str, dict] = {}
    for model in models:
        for key in _ranking_keys(model):
            if key and key not in by_slug:
                by_slug[key] = model
    return by_slug, int(data.get("n_models") or len(models)), data.get("generated_at")


def openrouter_models_to_manifests(
    models: list[dict],
    *,
    models_source: str,
    retrieved_at: str,
    ranking_by_slug: dict[str, dict] | None = None,
    ranking_count: int = 0,
    ranking_generated_at: str | None = None,
) -> list[dict]:
    """Convert OpenRouter model records into ephemeral ASM manifests."""
    ranking_by_slug = ranking_by_slug or {}
    manifests: list[dict] = []
    for model in models:
        manifest = openrouter_model_to_manifest(
            model,
            models_source=models_source,
            retrieved_at=retrieved_at,
            ranking_by_slug=ranking_by_slug,
            ranking_count=ranking_count,
            ranking_generated_at=ranking_generated_at,
        )
        if manifest is not None:
            manifests.append(manifest)
    return manifests


def openrouter_model_to_manifest(
    model: dict,
    *,
    models_source: str,
    retrieved_at: str,
    ranking_by_slug: dict[str, dict],
    ranking_count: int,
    ranking_generated_at: str | None,
) -> dict | None:
    model_id = str(model.get("id") or "").strip()
    if not model_id:
        return None

    pricing = model.get("pricing") or {}
    prompt_cost = _parse_float(pricing.get("prompt"))
    completion_cost = _parse_float(pricing.get("completion"))
    if prompt_cost is None and completion_cost is None:
        return None

    dims = []
    if prompt_cost is not None:
        dims.append({
            "dimension": "input_token",
            "unit": "per_1M",
            "cost_per_unit": prompt_cost * 1_000_000,
            "currency": "USD",
        })
    if completion_cost is not None:
        dims.append({
            "dimension": "output_token",
            "unit": "per_1M",
            "cost_per_unit": completion_cost * 1_000_000,
            "currency": "USD",
        })

    ranking = _find_ranking(model_id, ranking_by_slug)
    quality_metric, leaderboard = _usage_quality(model_id, ranking, ranking_count, ranking_generated_at)
    architecture = model.get("architecture") or {}
    top_provider = model.get("top_provider") or {}
    context_length = model.get("context_length") or top_provider.get("context_length")

    notes = [
        "Ephemeral manifest generated from OpenRouter model metadata.",
        "Pricing is OpenRouter-reported and may change.",
        "OpenRouter does not expose per-model latency or uptime in /api/v1/models.",
        "Quality metric is a usage signal, not benchmark quality.",
    ]
    if ranking_generated_at:
        notes.append(f"Usage ranking snapshot: {ranking_generated_at}.")
    else:
        notes.append("No cached usage ranking snapshot was available; neutral usage score used.")

    manifest = {
        "asm_version": "0.3",
        "service_id": f"openrouter/{model_id}@current",
        "taxonomy": "ai.llm.chat",
        "display_name": str(model.get("name") or model_id),
        "provider": {
            "name": "OpenRouter",
            "url": "https://openrouter.ai",
            "verified_by": ["openrouter-public-api"],
        },
        "capabilities": {
            "description": f"OpenRouter model endpoint for {model_id}",
            "input_modalities": _schema_modalities(architecture.get("input_modalities")),
            "output_modalities": _schema_modalities(architecture.get("output_modalities")),
        },
        "pricing": {
            "billing_dimensions": dims,
            "estimated": False,
        },
        "quality": {
            "metrics": [quality_metric],
        },
        "provenance": {
            "source_url": models_source if models_source.startswith("http") else OPENROUTER_MODELS_URL,
            "retrieved_at": retrieved_at,
            "last_verified_at": retrieved_at,
            "verification_status": "self_reported",
            "notes": " ".join(notes),
        },
        "updated_at": retrieved_at,
        "ttl": 300,
    }
    if context_length:
        manifest["capabilities"]["context_window"] = int(context_length)
    if leaderboard:
        manifest["quality"]["leaderboard_rank"] = leaderboard
    return manifest


def load_openrouter_manifests(
    *,
    models_json: str | Path | None = None,
    rankings_json: str | Path | None = None,
    timeout: int = 20,
) -> tuple[list[dict], dict]:
    models, source, retrieved_at = load_openrouter_models(models_json=models_json, timeout=timeout)
    rankings, ranking_count, ranking_generated_at = load_openrouter_rankings(rankings_json=rankings_json)
    manifests = openrouter_models_to_manifests(
        models,
        models_source=source,
        retrieved_at=retrieved_at,
        ranking_by_slug=rankings,
        ranking_count=ranking_count,
        ranking_generated_at=ranking_generated_at,
    )
    metadata = {
        "source": source,
        "retrieved_at": retrieved_at,
        "n_models": len(models),
        "n_manifests": len(manifests),
        "ranking_snapshot": ranking_generated_at,
        "ranking_count": ranking_count,
    }
    return manifests, metadata


def _usage_quality(
    model_id: str,
    ranking: dict | None,
    ranking_count: int,
    ranking_generated_at: str | None,
) -> tuple[dict, dict | None]:
    if ranking and ranking_count > 1:
        rank = int(ranking.get("rank_by_prompt_tokens") or ranking_count)
        score = max(0.0, min(1.0, 1 - ((rank - 1) / (ranking_count - 1))))
        metric = {
            "name": "openrouter_usage_signal",
            "score": score,
            "scale": "0-1",
            "benchmark": "OpenRouter 7-day prompt-token usage rank",
            "benchmark_url": OPENROUTER_RANKINGS_URL,
            "self_reported": False,
        }
        leaderboard = {
            "name": "OpenRouter 7-day prompt-token usage",
            "rank": rank,
            "total": ranking_count,
            "url": OPENROUTER_RANKINGS_URL,
        }
        if ranking_generated_at:
            leaderboard["snapshot_date"] = ranking_generated_at[:10]
        return metric, leaderboard

    return {
        "name": "openrouter_usage_signal",
        "score": 0.5,
        "scale": "0-1",
        "benchmark": "No cached OpenRouter ranking match; neutral usage placeholder",
        "benchmark_url": OPENROUTER_RANKINGS_URL,
        "self_reported": True,
    }, None


def _find_ranking(model_id: str, ranking_by_slug: dict[str, dict]) -> dict | None:
    for key in _model_keys(model_id):
        if key in ranking_by_slug:
            return ranking_by_slug[key]
    return None


def _model_keys(model_id: str) -> list[str]:
    normalized = model_id.lower()
    keys = [normalized]
    if ":" in normalized:
        keys.append(normalized.split(":", 1)[0])
    return list(dict.fromkeys(keys))


def _ranking_keys(model: dict) -> list[str]:
    keys = []
    for field in ("slug", "permaslug"):
        value = str(model.get(field) or "").lower()
        if value:
            keys.append(value)
    return list(dict.fromkeys(keys))


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed < 0:
        return None
    return parsed


def _schema_modalities(values: Any) -> list[str]:
    allowed = {"text", "image", "audio", "video", "file"}
    if not isinstance(values, list):
        return ["text"]
    result = [str(v) for v in values if str(v) in allowed]
    return result or ["text"]
