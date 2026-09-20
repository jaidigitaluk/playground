"""24-hour disk cache for provider responses.

Migrated from playground dataforseo-test/_system/cache.py (endpoint+payload
SHA-256 key, TTL). Change: callers get the cache key and hit status back so
the run manifest and ledger can record cache hits explicitly instead of the
hit being invisible.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional


def default_ttl_seconds() -> int:
    return int(os.getenv("LAB_CACHE_TTL_HOURS", "24")) * 3600


class Cache:
    def __init__(self, cache_dir: Path, ttl_seconds: Optional[int] = None):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_seconds if ttl_seconds is not None else default_ttl_seconds()

    @staticmethod
    def key(endpoint: str, payload: Any) -> str:
        serialized = json.dumps({"endpoint": endpoint, "payload": payload}, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, endpoint: str, payload: Any) -> tuple[Optional[dict], str, bool]:
        """Return (response or None, cache_key, hit)."""
        key = self.key(endpoint, payload)
        path = self.dir / f"{key}.json"
        if not path.exists():
            return None, key, False
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None, key, False
        if time.time() - record.get("cached_at", 0) > self.ttl:
            path.unlink(missing_ok=True)
            return None, key, False
        return record.get("response"), key, True

    def put(self, endpoint: str, payload: Any, response: dict) -> str:
        key = self.key(endpoint, payload)
        record = {"cached_at": time.time(), "endpoint": endpoint, "response": response}
        (self.dir / f"{key}.json").write_text(json.dumps(record), encoding="utf-8")
        return key
