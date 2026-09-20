#!/usr/bin/env python3
"""ChatGPT scraper pull. Raw response retains cited sources and fan_out_queries."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_endpoint import run
ENDPOINT = "ai_optimization/chat_gpt/llm_scraper/live/advanced"
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("keyword"); a=p.parse_args()
    raise SystemExit(run(ENDPOINT,{"keyword":a.keyword},"chatgpt-llm-scraper",Path(__file__).resolve().parents[1]))
