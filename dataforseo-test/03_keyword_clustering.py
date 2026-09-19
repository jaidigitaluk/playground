#!/usr/bin/env python3
"""
03_keyword_clustering.py
------------------------
Fetches keyword suggestions from DataForSEO Labs and groups them
by search intent (Informational, Commercial, Transactional, Navigational).
"""

import sys
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table

from _system.client import DataForSEOClient, DataForSEOAPIError
from _system.guardrails import guard

console = Console()
LOCATIONS_PATH = Path(__file__).resolve().parent / "_config" / "locations.json"

def load_location(geo_code: str = "UK") -> tuple:
    if LOCATIONS_PATH.exists():
        with open(LOCATIONS_PATH, "r", encoding="utf-8") as f:
            locs = json.load(f)
            geo = locs.get(geo_code.upper(), locs.get("UK"))
            return geo["location_code"], geo["language_code"], geo["name"]
    return 2826, "en", "United Kingdom"

def run_clustering(keyword: str, geo: str = "UK", limit: int = 15, force_refresh: bool = False):
    location_code, language_code, location_name = load_location(geo)
    client = DataForSEOClient()

    console.print(f"\n[bold cyan]📊 Keyword Suggestions & Intent Clustering for:[/bold cyan] '{keyword}'")
    console.print(f"📍 Location: [bold white]{location_name}[/bold white] | Limit: [bold white]{limit}[/bold white]")

    payload = {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "include_seed_keyword": True,
        "limit": limit
    }

    try:
        res = client.request(
            method="POST",
            path="/v3/dataforseo_labs/google/keyword_suggestions/live",
            payload=payload,
            force_refresh=force_refresh
        )

        from_cache = res.get("_from_cache", False)
        status_msg = "[yellow](from 24h cache - $0.00 spent)[/yellow]" if from_cache else "[green](live network call)[/green]"
        console.print(f"📦 Response Status: {status_msg}")

        data = res["data"]
        items = data["tasks"][0]["result"][0].get("items", [])

        if not items:
            console.print("[yellow]⚠️ No keyword suggestions returned for this query.[/yellow]")
            return

        # Cluster by Search Intent
        clusters = {
            "informational": [],
            "commercial": [],
            "transactional": [],
            "navigational": [],
            "unclassified": []
        }

        for item in items:
            kw_data = item.get("keyword_data") if isinstance(item.get("keyword_data"), dict) else item
            kw = kw_data.get("keyword") or item.get("keyword")
            kw_info = kw_data.get("keyword_info", {}) or item.get("keyword_info", {})
            search_intent = kw_data.get("search_intent_info", {}) or item.get("search_intent_info", {})
            props = kw_data.get("keyword_properties", {}) or item.get("keyword_properties", {})

            intent = (search_intent.get("main_intent") or "unclassified").lower()
            volume = kw_info.get("search_volume", 0)
            cpc = kw_info.get("cpc", 0.0)
            competition = kw_info.get("competition_level", "N/A")
            kd = props.get("keyword_difficulty", "N/A")

            entry = {
                "keyword": kw,
                "volume": volume,
                "cpc": cpc,
                "competition": competition,
                "kd": kd
            }

            if intent in clusters:
                clusters[intent].append(entry)
            else:
                clusters["unclassified"].append(entry)

        # Print Intent Tables
        for intent_type, kw_list in clusters.items():
            if not kw_list:
                continue

            color = "blue" if intent_type == "informational" else "yellow" if intent_type == "commercial" else "green"
            table = Table(
                title=f"\nIntent Cluster: {intent_type.upper()} ({len(kw_list)} keywords)",
                show_header=True,
                header_style=f"bold {color}"
            )
            table.add_column("Keyword", style="bold white")
            table.add_column("Search Volume", justify="right", style="cyan")
            table.add_column("CPC ($)", justify="right", style="green")
            table.add_column("Competition", justify="center", style="dim")

            for k in kw_list:
                table.add_row(
                    k["keyword"],
                    f"{k['volume']:,}" if k["volume"] else "0",
                    f"${k['cpc']:.2f}" if k["cpc"] else "$0.00",
                    str(k["competition"])
                )

            console.print(table)

        console.print(f"\n[bold cyan]{guard.summary()}[/bold cyan]\n")

    except DataForSEOAPIError as e:
        console.print(f"[bold red]❌ API Error [{e.code}]:[/bold red] {e.message}")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate keyword suggestions and cluster by search intent.")
    parser.add_argument("keyword", nargs="?", default="crm software", help="Seed keyword")
    parser.add_argument("--geo", default="UK", choices=["UK", "US", "CA", "AU"], help="Target country code")
    parser.add_argument("--limit", type=int, default=15, help="Max keywords to pull")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass cache")
    args = parser.parse_args()

    run_clustering(args.keyword, args.geo, args.limit, args.force_refresh)

if __name__ == "__main__":
    main()
