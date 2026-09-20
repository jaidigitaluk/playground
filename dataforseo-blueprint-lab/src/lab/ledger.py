"""Append-only spend ledger shared by every provider.

Fixes the two gaps found in the playground audit (19 Sep 2026):
- the old guard was a process-local singleton, so spend reset every run and
  there was no per-day view;
- Keywords Everywhere MCP calls bypassed it entirely.

One JSONL file (`runs/ledger.jsonl`), one entry per attempted call, safe to
commit (it holds costs and endpoints, never response payloads). QA reads this
ledger by run ID; Git state is never used to guess which run is current.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

USD = "USD"
KE_CREDITS = "KE_CREDITS"


@dataclass
class LedgerEntry:
    ts: str
    run_id: str
    provider: str
    endpoint: str
    status: str  # completed | blocked_cap | blocked_unknown_cost | failed | cache_hit
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    cost_source: str  # provider_returned | catalog_estimate | declared | none
    currency: str
    cache_hit: bool
    detail: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: LedgerEntry) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")

    def entries(self) -> list[LedgerEntry]:
        if not self.path.exists():
            return []
        out = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(LedgerEntry(**json.loads(line)))
        return out

    def spend_for_run(self, run_id: str, currency: str = USD) -> float:
        return sum(
            e.actual_cost or 0.0
            for e in self.entries()
            if e.run_id == run_id and e.currency == currency and e.status in ("completed",)
        )

    def calls_for_run(self, run_id: str) -> int:
        return sum(
            1 for e in self.entries()
            if e.run_id == run_id and e.status == "completed" and not e.cache_hit
        )

    def spend_for_day(self, day: str, currency: str = USD) -> float:
        """day: YYYY-MM-DD (UTC)."""
        return sum(
            e.actual_cost or 0.0
            for e in self.entries()
            if e.ts.startswith(day) and e.currency == currency and e.status == "completed"
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
