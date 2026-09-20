"""Shared spend guard. Every provider call passes through here before firing.

Pattern migrated from playground dataforseo-test/_system/guardrails.py, with
the audit fixes: caps are enforced against the durable ledger (so they survive
process restarts) and both providers share the same guard. Unknown cost fails
closed unless LAB_ALLOW_UNKNOWN_COST=1 (James's explicit go-ahead only).
"""

from __future__ import annotations

import os
from typing import Optional

from .ledger import Ledger, LedgerEntry, USD, KE_CREDITS, utc_now


class CapExceeded(Exception):
    pass


class UnknownCost(Exception):
    pass


class SpendGuard:
    def __init__(self, ledger: Ledger, run_id: str,
                 max_usd_per_run: Optional[float] = None,
                 max_usd_per_day: Optional[float] = None,
                 max_calls_per_run: Optional[int] = None,
                 max_ke_per_run: Optional[float] = None,
                 max_ke_per_day: Optional[float] = None,
                 allow_unknown_cost: Optional[bool] = None):
        self.ledger = ledger
        self.run_id = run_id
        self.max_usd_per_run = _env_float("LAB_MAX_USD_PER_RUN", 0.25, max_usd_per_run)
        self.max_usd_per_day = _env_float("LAB_MAX_USD_PER_DAY", 1.00, max_usd_per_day)
        self.max_calls_per_run = _env_int("LAB_MAX_CALLS_PER_RUN", 6, max_calls_per_run)
        self.max_ke_per_run = _env_float("LAB_MAX_KE_CREDITS_PER_RUN", 50.0, max_ke_per_run)
        self.max_ke_per_day = _env_float("LAB_MAX_KE_CREDITS_PER_DAY", 200.0, max_ke_per_day)
        if allow_unknown_cost is None:
            allow_unknown_cost = os.getenv("LAB_ALLOW_UNKNOWN_COST", "0") == "1"
        self.allow_unknown_cost = allow_unknown_cost

    def _currency(self, provider: str) -> str:
        return KE_CREDITS if provider == "keywords_everywhere" else USD

    def preflight(self, provider: str, endpoint: str, estimated_cost: Optional[float]) -> None:
        """Raise before any paid call that would breach a cap or has unknown cost."""
        currency = self._currency(provider)

        if estimated_cost is None:
            status = "blocked_unknown_cost"
            self.ledger.append(LedgerEntry(
                ts=utc_now(), run_id=self.run_id, provider=provider, endpoint=endpoint,
                status=status, estimated_cost=None, actual_cost=None,
                cost_source="none", currency=currency, cache_hit=False,
                detail="unknown cost; fails closed (LAB_ALLOW_UNKNOWN_COST unset)",
            ))
            if not self.allow_unknown_cost:
                raise UnknownCost(
                    f"Cost of {provider}:{endpoint} is unknown and LAB_ALLOW_UNKNOWN_COST "
                    "is not set. Declare the cost or get James's explicit go-ahead."
                )
            return

        if currency == USD:
            if self.ledger.calls_for_run(self.run_id) >= self.max_calls_per_run:
                self._block(provider, endpoint, estimated_cost, currency,
                            f"call cap {self.max_calls_per_run}/run reached")
                raise CapExceeded(f"Call cap {self.max_calls_per_run} per run reached.")
            if self.ledger.spend_for_run(self.run_id, USD) + estimated_cost > self.max_usd_per_run:
                self._block(provider, endpoint, estimated_cost, currency, "per-run USD cap would be exceeded")
                raise CapExceeded(
                    f"${estimated_cost:.4f} would exceed per-run cap ${self.max_usd_per_run:.2f}.")
            day = utc_now()[:10]
            if self.ledger.spend_for_day(day, USD) + estimated_cost > self.max_usd_per_day:
                self._block(provider, endpoint, estimated_cost, currency, "per-day USD cap would be exceeded")
                raise CapExceeded(
                    f"${estimated_cost:.4f} would exceed per-day cap ${self.max_usd_per_day:.2f}.")
        else:
            if self.ledger.spend_for_run(self.run_id, KE_CREDITS) + estimated_cost > self.max_ke_per_run:
                self._block(provider, endpoint, estimated_cost, currency, "per-run KE credit cap would be exceeded")
                raise CapExceeded("KE per-run credit cap would be exceeded.")
            day = utc_now()[:10]
            if self.ledger.spend_for_day(day, KE_CREDITS) + estimated_cost > self.max_ke_per_day:
                self._block(provider, endpoint, estimated_cost, currency, "per-day KE credit cap would be exceeded")
                raise CapExceeded("KE per-day credit cap would be exceeded.")

    def record(self, provider: str, endpoint: str, estimated_cost: Optional[float],
               actual_cost: Optional[float], cost_source: str,
               cache_hit: bool = False, status: str = "completed", detail: str = "") -> None:
        self.ledger.append(LedgerEntry(
            ts=utc_now(), run_id=self.run_id, provider=provider, endpoint=endpoint,
            status="cache_hit" if cache_hit else status,
            estimated_cost=estimated_cost, actual_cost=0.0 if cache_hit else actual_cost,
            cost_source=cost_source, currency=self._currency(provider),
            cache_hit=cache_hit, detail=detail,
        ))

    def _block(self, provider: str, endpoint: str, est: float, currency: str, detail: str) -> None:
        self.ledger.append(LedgerEntry(
            ts=utc_now(), run_id=self.run_id, provider=provider, endpoint=endpoint,
            status="blocked_cap", estimated_cost=est, actual_cost=None,
            cost_source="catalog_estimate", currency=currency, cache_hit=False, detail=detail,
        ))


def _env_float(name: str, default: float, override: Optional[float]) -> float:
    if override is not None:
        return float(override)
    return float(os.getenv(name, str(default)))


def _env_int(name: str, default: int, override: Optional[int]) -> int:
    if override is not None:
        return int(override)
    return int(os.getenv(name, str(default)))
