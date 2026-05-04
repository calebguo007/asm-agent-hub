#!/usr/bin/env python3
"""Fetch OpenRouter usage rankings (revealed-preference signal at scale).

OpenRouter (https://openrouter.ai/rankings) reports per-model production
traffic across all paying customers — token counts and request counts over
the last 7 days. This is the closest publicly-observable revealed preference
signal for LLM choice: actual production agents and applications voting
with their wallets.

The page is Next.js with embedded RSC payload; the data is in escaped JSON
inside <script> tags (`self.__next_f.push([1, "..."])`). We unescape, then
extract model records {author, slug, variant, prompt_tokens, completion_tokens,
count}. Sort by total tokens (or count) for the ranking.

Usage:
    python experiments/external_validation/fetch_openrouter_rankings.py \
        --output-dir experiments/results/external_validation/

Output:
    openrouter_rankings.json
    openrouter_rankings.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT / "experiments" / "results" / "external_validation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://openrouter.ai/rankings"


def fetch_page() -> str:
    req = Request(URL, headers={"User-Agent": "Mozilla/5.0 (asm-validation)"})
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_records(html: str) -> list[dict]:
    """Find OpenRouter model records inside the RSC payload.

    The actual fields are `model_permaslug`, `variant`, `total_prompt_tokens`,
    `total_completion_tokens`, `count`, `change`. Inner quotes are escaped as
    `\\"`; we unescape once then scan with a relaxed regex.
    """
    text = html.replace('\\"', '"')

    # Each ranking record is a flat object (no nested {}). The shape per Aug 2025:
    # {"date":"YYYY-MM-DD","model_permaslug":"author/slug-yyyy","variant":"...",
    #  "total_completion_tokens":N,"total_prompt_tokens":N,
    #  "total_native_tokens_reasoning":N,"count":N, ...}
    pattern = re.compile(
        r'\{"date":"[^"]+",'
        r'"model_permaslug":"(?P<permaslug>[^"]+)",'
        r'"variant":"(?P<variant>[^"]*)",'
        r'"total_completion_tokens":(?P<ct>\d+),'
        r'"total_prompt_tokens":(?P<pt>\d+)'
        r'[^{}]*?"count":(?P<count>\d+)',
        re.DOTALL,
    )
    rows: list[dict] = []
    for m in pattern.finditer(text):
        permaslug = m.group("permaslug")
        author = permaslug.split("/", 1)[0] if "/" in permaslug else ""
        # Strip the dated suffix from slug (e.g. "qwen3-max-20260101" -> "qwen3-max").
        slug = re.sub(r"-\d{8}$|-\d{4}-\d{2}-\d{2}$", "", permaslug)
        rows.append({
            "permaslug": permaslug,
            "slug": slug,
            "author": author,
            "variant": m.group("variant"),
            "prompt_tokens": int(m.group("pt")),
            "completion_tokens": int(m.group("ct")),
            "total_tokens": int(m.group("pt")) + int(m.group("ct")),
            "count": int(m.group("count")),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--input-html", type=Path, default=None,
                        help="Cached HTML to parse instead of re-fetching.")
    args = parser.parse_args()

    if args.input_html:
        html = args.input_html.read_text(encoding="utf-8", errors="replace")
        source = f"file:{args.input_html.name}"
    else:
        print(f"Fetching {URL} ...", file=sys.stderr)
        html = fetch_page()
        source = URL

    rows = extract_records(html)
    print(f"  extracted {len(rows)} model records", file=sys.stderr)

    # Aggregate by slug (one slug may appear with multiple variant rows).
    aggregated: dict[str, dict] = {}
    for r in rows:
        slug = r["slug"]
        if slug not in aggregated:
            aggregated[slug] = dict(r)
        else:
            agg = aggregated[slug]
            agg["prompt_tokens"] = max(agg["prompt_tokens"], r["prompt_tokens"])
            agg["count"] = max(agg["count"], r["count"])

    sorted_rows = sorted(aggregated.values(), key=lambda r: -(r["prompt_tokens"] or 0))
    for i, r in enumerate(sorted_rows, 1):
        r["rank_by_prompt_tokens"] = i

    args.output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "n_models": len(sorted_rows),
        "models": sorted_rows,
    }
    (args.output_dir / "openrouter_rankings.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    if sorted_rows:
        with (args.output_dir / "openrouter_rankings.csv").open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=list(sorted_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sorted_rows)

    print(f"Top 12 by prompt_tokens (last 7 days):")
    for r in sorted_rows[:12]:
        print(f"  {r['rank_by_prompt_tokens']:>3}. {r['slug']:<55}  pt={r['prompt_tokens']/1e9:>6.2f}B  reqs={r['count']:>10,}")


if __name__ == "__main__":
    main()
