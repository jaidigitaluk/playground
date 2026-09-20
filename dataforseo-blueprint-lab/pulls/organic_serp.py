#!/usr/bin/env python3
"""Organic advanced SERP pull. Raw items retain AI Overview and PAA blocks."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_endpoint import run
ENDPOINT = "serp/google/organic/live/advanced"
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("keyword"); p.add_argument("--location-code",type=int,default=2826); p.add_argument("--language-code",default="en"); p.add_argument("--depth",type=int,default=20); a=p.parse_args()
    raise SystemExit(run(ENDPOINT,{"keyword":a.keyword,"location_code":a.location_code,"language_code":a.language_code,"depth":a.depth},"organic-serp",Path(__file__).resolve().parents[1]))
