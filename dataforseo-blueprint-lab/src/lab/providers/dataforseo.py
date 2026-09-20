"""DataForSEO adapter.

Live calls go through the official client library (dataforseo-client,
https://github.com/dataforseo/PythonClient) when installed; the import is lazy
so tests and CI run offline. Estimates come from config/endpoints_catalog.json
(planning estimates, not billing truth); when a response carries a `cost`
field it wins and is recorded as provider_returned.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Callable, Optional

from ..ledger import USD

DEFAULT_BASE = "https://api.dataforseo.com/v3"


class DataForSEOProvider:
    name = "dataforseo"
    currency = USD

    def __init__(self, catalog_path: Optional[Path] = None,
                 transport: Optional[Callable[[str, str, list], dict]] = None):
        self.catalog = self._load_catalog(catalog_path)
        self._transport = transport or self._official_transport

    @staticmethod
    def _load_catalog(catalog_path: Optional[Path]) -> dict:
        path = catalog_path or (
            Path(__file__).resolve().parents[3] / "config" / "endpoints_catalog.json"
        )
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data.get("dataforseo", {})

    def estimate_cost(self, endpoint: str, payload: dict) -> Optional[float]:
        endpoint = endpoint.lstrip("/").removeprefix("v3/")
        entry = self.catalog.get(endpoint)
        if entry is None:
            return None  # unknown endpoint: guard fails closed
        cost = entry.get("cost_usd")
        return None if cost is None else float(cost)

    def call(self, endpoint: str, payload: dict) -> dict:
        body = payload if isinstance(payload, list) else [payload]
        return self._transport("POST", endpoint.lstrip("/"), body)

    def extract_cost(self, response: dict) -> tuple[Optional[float], str]:
        cost = response.get("cost")
        if isinstance(cost, (int, float)):
            return float(cost), "provider_returned"
        return None, "none"

    # --- transports -----------------------------------------------------

    @staticmethod
    def _official_transport(method: str, endpoint: str, body: list) -> dict:
        """Official-client path. Lazy import keeps offline tests dependency-free."""
        try:
            from dataforseo_client import Configuration, ApiClient  # type: ignore
        except ImportError:
            return DataForSEOProvider._urllib_transport(method, endpoint, body)
        # The official generated client is endpoint-class based; for the lab's
        # generic POST shape we use its ApiClient REST layer with basic auth.
        login = os.environ["DATAFORSEO_LOGIN"]
        password = os.environ["DATAFORSEO_PASSWORD"]
        config = Configuration(username=login, password=password)
        with ApiClient(config) as client:
            data = json.dumps(body)
            resp = client.request(
                method, f"{DEFAULT_BASE}/{endpoint}",
                headers={"Content-Type": "application/json"}, body=data,
            )
            return json.loads(resp.data)

    @staticmethod
    def _urllib_transport(method: str, endpoint: str, body: list) -> dict:
        """Fallback when the official client is not installed.

        Justified custom wrapper: the lab only needs generic POST-with-basic-
        auth for a handful of endpoints, and the playground audit found the old
        hand-rolled client sound for this shape. Kept deliberately thin.
        """
        import urllib.request

        login = os.environ["DATAFORSEO_LOGIN"]
        password = os.environ["DATAFORSEO_PASSWORD"]
        token = base64.b64encode(f"{login}:{password}".encode()).decode()
        req = urllib.request.Request(
            f"{DEFAULT_BASE}/{endpoint}",
            data=json.dumps(body).encode("utf-8"),
            method=method,
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
