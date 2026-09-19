"""
guardrails.py
-------------
Spend and safety guardrails to protect against runaway agent credit consumption.
"""

import os
import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / "_config" / "endpoints_catalog.json"

class SpendGuardrailExceeded(Exception):
    """Raised when an operation would exceed budget limits."""
    pass

class CallLimitExceeded(Exception):
    """Raised when an operation would exceed the single-run call limit."""
    pass

class Guardrails:
    def __init__(self):
        self.max_budget = float(os.getenv("DATAFORSEO_MAX_BUDGET_USD_PER_RUN", "0.25"))
        self.max_calls = int(os.getenv("DATAFORSEO_MAX_CALLS_PER_RUN", "6"))
        self.current_spend = 0.0
        self.call_count = 0
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> dict:
        if CATALOG_PATH.exists():
            try:
                with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_estimated_cost(self, endpoint_path: str) -> float:
        """Looks up the estimated cost for a given endpoint path."""
        for module, endpoints in self.catalog.items():
            for ep_key, ep_data in endpoints.items():
                if ep_data.get("path") == endpoint_path:
                    return float(ep_data.get("cost_usd", 0.005))
        # Default fallback cost
        return 0.005

    def pre_flight_check(self, endpoint_path: str) -> None:
        """Validates that making this call will not breach budget or count limits."""
        if self.call_count >= self.max_calls:
            raise CallLimitExceeded(
                f"🛑 Guardrail Tripped: Maximum calls per run ({self.max_calls}) reached. "
                f"Halting execution to prevent runaway loop."
            )

        estimated_call_cost = self.get_estimated_cost(endpoint_path)
        projected_spend = self.current_spend + estimated_call_cost

        if projected_spend > self.max_budget:
            raise SpendGuardrailExceeded(
                f"🛑 Guardrail Tripped: Call to '{endpoint_path}' (${estimated_call_cost:.4f}) "
                f"would exceed maximum budget of ${self.max_budget:.2f} "
                f"(current accumulated: ${self.current_spend:.4f}). Halting execution."
            )

    def record_call(self, endpoint_path: str, actual_cost: float = None) -> None:
        """Records a successful network call."""
        cost = actual_cost if actual_cost is not None else self.get_estimated_cost(endpoint_path)
        self.current_spend += cost
        self.call_count += 1

    def summary(self) -> str:
        return (
            f"💰 Spend Tracker: {self.call_count}/{self.max_calls} calls made, "
            f"${self.current_spend:.4f}/${self.max_budget:.2f} USD consumed."
        )

# Global singleton for the process
guard = Guardrails()
