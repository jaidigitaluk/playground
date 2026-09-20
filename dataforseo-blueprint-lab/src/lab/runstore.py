"""Stage 2: immutable run evidence store.

A pull creates a run directory up front and everything it produces - manifest,
raw provider responses, hashes - carries that run ID. QA takes a run ID and
verifies hashes; nothing infers "the latest report" from file mtimes (the old
QA failure). A completed run directory is never overwritten.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from .ledger import utc_now


class RunExistsError(Exception):
    pass


class RunStore:
    def __init__(self, runs_dir: Path):
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def create_run(self, slug: str, run_id: Optional[str] = None) -> "Run":
        run_id = run_id or f"{utc_now().replace(':', '').replace('-', '')}-{slug}"
        run_dir = self.runs_dir / run_id
        if run_dir.exists():
            raise RunExistsError(f"Run {run_id} already exists; runs are never overwritten.")
        (run_dir / "raw").mkdir(parents=True)
        return Run(run_id=run_id, run_dir=run_dir)


class Run:
    def __init__(self, run_id: str, run_dir: Path):
        self.run_id = run_id
        self.dir = Path(run_dir)
        self._seq = 0
        self._evidence: list[dict] = []
        self.request: Optional[dict] = None
        self.status = "open"

    def set_request(self, provider: str, endpoint: str, payload: dict) -> None:
        self.request = {"provider": provider, "endpoint": endpoint, "payload": payload}

    def write_raw(self, provider: str, endpoint: str, response: dict, cache_hit: bool) -> Path:
        self._seq += 1
        slug = endpoint.replace("/", "_").strip("_")[:60]
        path = self.dir / "raw" / f"{self._seq:03d}_{provider}_{slug}.json"
        path.write_text(json.dumps(response, indent=2, sort_keys=True), encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        self._evidence.append({
            "path": str(path.relative_to(self.dir)),
            "sha256": digest,
            "bytes": path.stat().st_size,
            "cache_hit": cache_hit,
        })
        return path

    def finalize(self, status: str = "completed", notes: str = "") -> Path:
        self.status = status
        manifest = {
            "run_id": self.run_id,
            "created_at": utc_now(),
            "stage": "pull",
            "status": status,
            "code": {"git_commit": _git_commit(), "python_version": sys.version.split()[0]},
            "request": self.request,
            "evidence_files": self._evidence,
            "notes": notes,
        }
        if self.request is None:
            manifest.pop("request")
        path = self.dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return path

    def verify(self) -> bool:
        """Re-hash every evidence file against the manifest. QA entry point."""
        manifest = json.loads((self.dir / "manifest.json").read_text(encoding="utf-8"))
        for entry in manifest.get("evidence_files", []):
            path = self.dir / entry["path"]
            if not path.exists():
                return False
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                return False
        return True


def _git_commit() -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip() or None
    except Exception:
        return None
