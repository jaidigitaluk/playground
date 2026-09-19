"""
cache.py
--------
Local disk cache for DataForSEO API responses.
Prevents burning duplicate credits during testing.
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Any, Dict

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TTL_SECONDS = int(os.getenv("DATAFORSEO_CACHE_TTL_HOURS", "24")) * 3600
CACHE_ENABLED = os.getenv("DATAFORSEO_ENABLE_CACHE", "true").lower() in ("true", "1", "yes")

def _compute_key(endpoint: str, payload: Any) -> str:
    serialized = json.dumps({"endpoint": endpoint, "payload": payload}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def get_cached_response(endpoint: str, payload: Any, ttl: int = DEFAULT_TTL_SECONDS) -> Optional[Dict[str, Any]]:
    if not CACHE_ENABLED:
        return None

    cache_key = _compute_key(endpoint, payload)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cached_at = data.get("_cached_at", 0)
        if time.time() - cached_at > ttl:
            cache_file.unlink(missing_ok=True)
            return None

        return data.get("response")
    except Exception:
        return None

def set_cached_response(endpoint: str, payload: Any, response_data: Dict[str, Any]) -> None:
    if not CACHE_ENABLED:
        return

    cache_key = _compute_key(endpoint, payload)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    try:
        record = {
            "_cached_at": time.time(),
            "endpoint": endpoint,
            "response": response_data
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
    except Exception as e:
        print(f"⚠️ Warning: Failed to write cache: {e}")

def clear_cache() -> int:
    """Clears all cached JSON responses."""
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink(missing_ok=True)
        count += 1
    return count
