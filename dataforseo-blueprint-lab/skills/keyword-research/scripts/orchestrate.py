#!/usr/bin/env python3
"""Create a typed dispatch plan. This never performs a paid call."""
import argparse, json
from pathlib import Path
JOBS=[("suggestions","pulls/keyword_suggestions.py"),("related","pulls/related_keywords.py"),("volume","pulls/search_volume.py"),("difficulty","pulls/bulk_keyword_difficulty.py"),("organic-serp","pulls/organic_serp.py"),("chatgpt-fanout","pulls/chatgpt_llm_scraper.py")]
p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("--out",required=True); a=p.parse_args()
spec=json.loads(Path(a.input).read_text()); seeds=spec.get("seed_keywords") or []
if not seeds: raise SystemExit("seed_keywords is required")
location=spec.get("location") or {}
if not isinstance(location.get("code"),int): raise SystemExit("location.code must be resolved before planning")
plan={"schema_version":"1.0","seed_keywords":seeds,"location":location,"jobs":[{"job":j,"script":s,"confidence":"Confirmed"} for j,s in JOBS]}
Path(a.out).write_text(json.dumps(plan,indent=2)+"\n")
