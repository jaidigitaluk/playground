#!/usr/bin/env python3
"""Free location lookup. Resolve city names before any paid keyword pull."""
import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lab.providers.dataforseo import DataForSEOProvider
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("name",choices=["Cardiff","Newport","Swansea"]); a=p.parse_args()
    provider=DataForSEOProvider()
    response=provider.call("dataforseo_labs/locations_and_languages", {"country_iso_code":"GB"})
    matches=[]
    for task in response.get("tasks",[]):
        for result in task.get("result") or []:
            if a.name.lower() in str(result.get("location_name","")).lower(): matches.append(result)
    print(json.dumps(matches,indent=2)); raise SystemExit(0 if matches else 1)
