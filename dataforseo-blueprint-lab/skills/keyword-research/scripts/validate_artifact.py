#!/usr/bin/env python3
"""Small dependency-free gate for run-plan artifacts."""
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument("artifact"); p.add_argument("schema"); a=p.parse_args()
data=json.loads(Path(a.artifact).read_text()); schema=json.loads(Path(a.schema).read_text())
missing=[k for k in schema.get("required",[]) if k not in data]
if missing: raise SystemExit("missing required fields: "+", ".join(missing))
if data.get("schema_version")!="1.0": raise SystemExit("unsupported schema_version")
if not data.get("seed_keywords") or not data.get("jobs"): raise SystemExit("empty seed_keywords/jobs")
if not isinstance((data.get("location") or {}).get("code"),int): raise SystemExit("unresolved location code")
allowed={"Confirmed","Likely","Hypothesis"}
if any(j.get("confidence") not in allowed for j in data["jobs"]): raise SystemExit("invalid confidence label")
print("valid")
