#!/usr/bin/env python3
"""Free pre-flight: verify DataForSEO credentials and print account balance.

Calls only /v3/appendix/user_data (free). Pattern migrated from playground
dataforseo-test/01_verify_auth.py. Run this before any paid pull.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lab.ledger import Ledger
from lab.guardrails import SpendGuard
from lab.providers.dataforseo import DataForSEOProvider
from lab.runstore import RunStore

ENDPOINT = "appendix/user_data"


def main() -> int:
    if not (os.getenv("DATAFORSEO_LOGIN") and os.getenv("DATAFORSEO_PASSWORD")):
        print("Missing DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD. Copy .env.example to .env.")
        return 1

    root = Path(__file__).resolve().parents[1]
    store = RunStore(root / "runs")
    run = store.create_run("preflight")
    run.set_request("dataforseo", ENDPOINT, {})
    guard = SpendGuard(Ledger(root / "runs" / "ledger.jsonl"), run.run_id)
    provider = DataForSEOProvider()

    guard.preflight("dataforseo", ENDPOINT, provider.estimate_cost(ENDPOINT, {}))
    response = provider.call(ENDPOINT, {})
    actual, source = provider.extract_cost(response)
    guard.record("dataforseo", ENDPOINT, estimated_cost=0.0,
                 actual_cost=actual or 0.0, cost_source=source if actual else "catalog_estimate")
    run.write_raw("dataforseo", ENDPOINT, response, cache_hit=False)
    run.finalize()

    result = (response.get("tasks") or [{}])[0].get("result") or [{}]
    money = result[0].get("money", {})
    balance = money.get("balance") if isinstance(money, dict) else money
    print(f"Authenticated as {result[0].get('login')}; balance ${float(balance or 0):.2f}")
    print(f"Run evidence: {run.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
