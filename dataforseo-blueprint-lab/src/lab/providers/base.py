"""Provider adapter contract.

One adapter per provider. The guard and ledger only ever see this surface, so
caps and records work identically no matter who supplied the data.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol


class ProviderAdapter(Protocol):
    name: str
    currency: str  # USD | KE_CREDITS

    def estimate_cost(self, endpoint: str, payload: dict) -> Optional[float]:
        """Best available pre-call cost. None means unknown (guard fails closed)."""
        ...

    def call(self, endpoint: str, payload: dict) -> dict:
        """Execute the provider call and return the raw response."""
        ...

    def extract_cost(self, response: dict) -> tuple[Optional[float], str]:
        """(actual cost, cost_source) from a response, if the provider returns one."""
        ...
