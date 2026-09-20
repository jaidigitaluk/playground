#!/usr/bin/env python3
"""Stage 1 pull: bounded keyword-suggestions call, preserved as evidence.

One script, one job. No analysis, no prose, no strategy: the raw response and
its request metadata land in the run store and the cost lands in the shared
ledger. Analysis reads the evidence later; nothing here interprets.

Usage:
    python pulls/keyword_suggestions.py "seo newport" --location-code 2826 --limit 50
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lab.cache import Cache
from lab.ledger import Ledger
from lab.guardrails import SpendGuard, CapExceeded, UnknownCost
from lab.providers.dataforseo import DataForSEOProvider
from lab.runstore import RunStore

ENDPOINT = "dataforseo_labs/google/keyword_suggestions/live"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keyword")
    parser.add_argument("--location-code", type=int, default=2826, help="DataForSEO location_code (2826 = UK)")
    parser.add_argument("--language-code", default="en")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    payload = {
        "keyword": args.keyword,
        "location_code": args.location_code,
        "language_code": args.language_code,
        "include_seed_keyword": True,
        "limit": args.limit,
    }

    store = RunStore(root / "runs")
    run = store.create_run("keyword-suggestions")
    run.set_request("dataforseo", ENDPOINT, payload)
    ledger = Ledger(root / "runs" / "ledger.jsonl")
    guard = SpendGuard(ledger, run.run_id)
    provider = DataForSEOProvider()
    cache = Cache(root / ".cache")

    estimate = provider.estimate_cost(ENDPOINT, payload)
    print(f"Estimated cost: ${estimate if estimate is not None else 'UNKNOWN'} "
          f"(cap ${guard.max_usd_per_run}/run, ${guard.max_usd_per_day}/day)")

    cached, key, hit = cache.get(ENDPOINT, payload)
    if hit:
        guard.record("dataforseo", ENDPOINT, estimated_cost=estimate,
                     actual_cost=0.0, cost_source="catalog_estimate", cache_hit=True)
        run.write_raw("dataforseo", ENDPOINT, cached, cache_hit=True)
        run.finalize(notes=f"cache hit {key}")
        print(f"Cache hit - $0.00 spent. Evidence: {run.dir}")
        return 0

    try:
        guard.preflight("dataforseo", ENDPOINT, estimate)
    except (CapExceeded, UnknownCost) as e:
        run.finalize(status="failed", notes=str(e))
        print(f"Blocked by spend guard: {e}")
        return 2

    response = provider.call(ENDPOINT, payload)
    actual, source = provider.extract_cost(response)
    guard.record("dataforseo", ENDPOINT, estimated_cost=estimate,
                 actual_cost=actual if actual is not None else estimate,
                 cost_source=source if actual is not None else "catalog_estimate")
    cache.put(ENDPOINT, payload, response)
    run.write_raw("dataforseo", ENDPOINT, response, cache_hit=False)
    run.finalize()

    items = ((response.get("tasks") or [{}])[0].get("result") or [{}])[0].get("total_count")
    print(f"Pulled {items if items is not None else '?'} suggestions for '{args.keyword}'. "
          f"Cost: ${actual if actual is not None else estimate}. Evidence: {run.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
