"""Keywords Everywhere adapter (MCP path).

KE is reached through its MCP server, which this repo cannot price. So this
adapter never calls the network itself: it exists to (a) estimate/declare cost
before a call, (b) push the call through the shared SpendGuard, and (c) write
the same ledger entries as DataForSEO. Unknown cost fails closed unless James
explicitly allows it. That is the fix for "KE bypasses the guard".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

from ..ledger import KE_CREDITS
from ..guardrails import SpendGuard


class KeywordsEverywhereProvider:
    name = "keywords_everywhere"
    currency = KE_CREDITS

    def __init__(self, catalog_path: Optional[Path] = None,
                 mcp_caller: Optional[Callable[[str, dict], dict]] = None):
        self.catalog = self._load_catalog(catalog_path)
        self._mcp_caller = mcp_caller

    @staticmethod
    def _load_catalog(catalog_path: Optional[Path]) -> dict:
        import json
        path = catalog_path or (
            Path(__file__).resolve().parents[3] / "config" / "endpoints_catalog.json"
        )
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data.get("keywords_everywhere", {})

    def estimate_cost(self, endpoint: str, payload: dict) -> Optional[float]:
        """Catalog price if one is pinned (e.g. get_keyword_data: 1 credit/keyword),
        else None -> the guard fails closed."""
        entry = self.catalog.get(endpoint)
        if entry is None:
            return None
        per = entry.get("cost_credits")
        if per is None:
            return None
        if entry.get("per") == "keyword":
            keywords = payload.get("keywords") or []
            return float(per) * max(len(keywords), 1)
        return float(per)

    def metered_call(self, guard: SpendGuard, endpoint: str, payload: dict,
                     declared_cost: Optional[float] = None) -> dict:
        """Run one KE MCP call under the shared cap.

        declared_cost: credits the caller knows this call will spend (from the
        MCP tool's own reporting). Without it, and without a catalog price,
        the guard raises UnknownCost before anything fires.
        """
        estimate = self.estimate_cost(endpoint, payload)
        if estimate is None:
            estimate = declared_cost
        guard.preflight(self.name, endpoint, estimate)

        if self._mcp_caller is None:
            raise RuntimeError(
                "No MCP caller wired in. KE calls run from the agent host's MCP "
                "server; pass mcp_caller when constructing this adapter."
            )
        response = self._mcp_caller(endpoint, payload)
        actual = declared_cost if declared_cost is not None else estimate
        guard.record(
            self.name, endpoint, estimated_cost=estimate, actual_cost=actual,
            cost_source="declared" if declared_cost is not None else "catalog_estimate",
        )
        return response
