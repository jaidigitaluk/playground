#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_endpoint import run
ENDPOINT = "keywords_data/google_ads/search_volume/live"
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("keywords",nargs="+"); p.add_argument("--location-code",type=int,default=2826); p.add_argument("--language-code",default="en"); a=p.parse_args()
    raise SystemExit(run(ENDPOINT,{"keywords":a.keywords[:1000],"location_code":a.location_code,"language_code":a.language_code},"search-volume",Path(__file__).resolve().parents[1]))
