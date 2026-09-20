"""Shared safe runner for one DataForSEO pull.

Every paid endpoint uses the same cache, spend guard, ledger and immutable
run-store path. Callers pass only an endpoint, payload and job slug. There is
no interpretation, clustering, synthesis or writing here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lab.cache import Cache
from lab.guardrails import CapExceeded, SpendGuard, UnknownCost
from lab.ledger import Ledger
from lab.providers.dataforseo import DataForSEOProvider
from lab.runstore import RunStore


def run(endpoint: str, payload: dict[str, Any], slug: str, root: Path) -> int:
    store = RunStore(root / "runs")
    run_record = store.create_run(slug)
    run_record.set_request("dataforseo", endpoint, payload)
    guard = SpendGuard(Ledger(root / "runs" / "ledger.jsonl"), run_record.run_id)
    provider = DataForSEOProvider()
    cache = Cache(root / ".cache")
    estimate = provider.estimate_cost(endpoint, payload)

    cached, cache_key, hit = cache.get(endpoint, payload)
    if hit:
        guard.record("dataforseo", endpoint, estimate, 0.0, "catalog_estimate", cache_hit=True)
        run_record.write_raw("dataforseo", endpoint, cached, cache_hit=True)
        run_record.finalize(notes=f"cache hit {cache_key}")
        print(json.dumps({"run_id": run_record.run_id, "status": "completed", "cache_hit": True}))
        return 0

    try:
        guard.preflight("dataforseo", endpoint, estimate)
    except (CapExceeded, UnknownCost) as exc:
        run_record.finalize(status="failed", notes=str(exc))
        print(json.dumps({"run_id": run_record.run_id, "status": "blocked", "reason": str(exc)}))
        return 2

    response = provider.call(endpoint, payload)
    actual, source = provider.extract_cost(response)
    guard.record("dataforseo", endpoint, estimate, actual if actual is not None else estimate,
                 source if actual is not None else "catalog_estimate")
    cache.put(endpoint, payload, response)
    run_record.write_raw("dataforseo", endpoint, response, cache_hit=False)
    run_record.finalize()
    print(json.dumps({"run_id": run_record.run_id, "status": "completed", "cache_hit": False,
                      "cost_usd": actual if actual is not None else estimate}))
    return 0
