#!/usr/bin/env python3
"""
05_multisource_keyword_expansion.py
-----------------------------------
Gap 2 Fix: Multi-Source Keyword Expansion Engine.
Fuses 4 distinct intelligence sources into a unified, intent-clustered candidate pool:
1. Seed Variations (DataForSEO Labs Keyword Suggestions)
2. Searcher Journey Queries (Google Live SERP People Also Ask)
3. Lateral Search Branches (Keywords Everywhere People Also Search For - PASF)
4. Competitor URL Keywords (Keywords Everywhere URL Ranking Hijacking)
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Any, Set
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from _system.client import DataForSEOClient, DataForSEOAPIError
from _system.guardrails import guard

load_dotenv()

console = Console()
LOCATIONS_PATH = Path(__file__).resolve().parent / "_config" / "locations.json"

def load_location(geo_code: str = "UK") -> tuple:
    if LOCATIONS_PATH.exists():
        with open(LOCATIONS_PATH, "r", encoding="utf-8") as f:
            locs = json.load(f)
            geo = locs.get(geo_code.upper(), locs.get("UK"))
            return geo["location_code"], geo["language_code"], geo["name"]
    return 2826, "en", "United Kingdom"

# -----------------------------------------------------------------------------
# Source 1: DataForSEO Labs Keyword Suggestions
# -----------------------------------------------------------------------------
def get_dataforseo_suggestions(client: DataForSEOClient, keyword: str, location_code: int, language_code: str, limit: int = 15, force_refresh: bool = False) -> List[Dict[str, Any]]:
    payload = {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "include_seed_keyword": True,
        "limit": limit
    }
    try:
        res = client.request("POST", "/v3/dataforseo_labs/google/keyword_suggestions/live", payload, force_refresh=force_refresh)
        items = res["data"]["tasks"][0]["result"][0].get("items", [])
    except Exception as e:
        console.print(f"[yellow]⚠️ DataForSEO Suggestions error: {e}[/yellow]")
        return []

    results = []
    for item in items:
        kw_data = item.get("keyword_data") if isinstance(item.get("keyword_data"), dict) else item
        kw = kw_data.get("keyword") or item.get("keyword")
        info = kw_data.get("keyword_info", {}) or item.get("keyword_info", {})
        intent_info = kw_data.get("search_intent_info", {}) or item.get("search_intent_info", {})
        props = kw_data.get("keyword_properties", {}) or item.get("keyword_properties", {})

        if kw:
            results.append({
                "keyword": kw,
                "volume": info.get("search_volume", 0),
                "cpc": info.get("cpc", 0.0),
                "intent": (intent_info.get("main_intent") or "commercial").lower(),
                "kd": props.get("keyword_difficulty", "N/A"),
                "source": "DataForSEO Labs (Seed Suggestion)"
            })
    return results

# -----------------------------------------------------------------------------
# Source 2: Google SERP People Also Ask & Top Competitor URLs
# -----------------------------------------------------------------------------
def get_serp_signals(client: DataForSEOClient, keyword: str, location_code: int, language_code: str, force_refresh: bool = False) -> tuple:
    payload = {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": "desktop",
        "depth": 20
    }
    try:
        res = client.request("POST", "/v3/serp/google/organic/live/advanced", payload, force_refresh=force_refresh)
        items = res["data"]["tasks"][0]["result"][0].get("items", [])
    except Exception as e:
        console.print(f"[yellow]⚠️ SERP retrieval error: {e}[/yellow]")
        return [], []

    paa_keywords = []
    top_competitors = []

    for item in items:
        itype = item.get("type")
        if itype == "people_also_ask":
            for q_item in item.get("items", []):
                q = q_item.get("title")
                if q:
                    paa_keywords.append({
                        "keyword": q,
                        "volume": 0,
                        "cpc": 0.0,
                        "intent": "informational",
                        "kd": "N/A",
                        "source": "Google Live SERP (PAA Question)"
                    })
        elif itype == "organic" and len(top_competitors) < 3:
            domain = item.get("domain", "")
            if "reddit" not in domain and "youtube" not in domain and "quora" not in domain:
                top_competitors.append(item.get("url"))

    return paa_keywords, top_competitors

# -----------------------------------------------------------------------------
# Source 3: Keywords Everywhere PASF (People Also Search For)
# -----------------------------------------------------------------------------
def get_ke_pasf(keyword: str, ke_api_key: str, limit: int = 10) -> List[Dict[str, Any]]:
    if not ke_api_key:
        return []

    headers = {"Authorization": f"Bearer {ke_api_key}", "Accept": "application/json"}
    data = {"keyword": keyword, "num": limit}
    try:
        res = requests.post("https://api.keywordseverywhere.com/v1/get_pasf_keywords", headers=headers, data=data, timeout=15)
        if res.status_code == 200:
            kws = res.json().get("data", [])
            return [{
                "keyword": kw,
                "volume": 0,
                "cpc": 0.0,
                "intent": "commercial" if any(w in kw.lower() for w in ["best", "vs", "review", "free"]) else "informational",
                "kd": "N/A",
                "source": "Keywords Everywhere (PASF Lateral Branch)"
            } for kw in kws]
    except Exception as e:
        console.print(f"[yellow]⚠️ KE PASF error: {e}[/yellow]")
    return []

# -----------------------------------------------------------------------------
# Source 4: Keywords Everywhere Competitor URL Ranking Hijacking
# -----------------------------------------------------------------------------
def get_ke_competitor_keywords(competitor_url: str, ke_api_key: str, country: str = "uk", limit: int = 10) -> List[Dict[str, Any]]:
    if not ke_api_key or not competitor_url:
        return []

    headers = {"Authorization": f"Bearer {ke_api_key}", "Accept": "application/json"}
    data = {"url": competitor_url, "country": country.lower(), "num": limit}
    try:
        res = requests.post("https://api.keywordseverywhere.com/v1/get_url_keywords", headers=headers, data=data, timeout=15)
        if res.status_code == 200:
            items = res.json().get("data", [])
            domain_name = competitor_url.split("/")[2].replace("www.", "")
            return [{
                "keyword": item.get("keyword"),
                "volume": item.get("estimated_monthly_traffic", 0),
                "cpc": 0.0,
                "intent": "commercial" if any(w in item.get("keyword", "").lower() for w in ["best", "top", "platform", "system"]) else "informational",
                "kd": "N/A",
                "source": f"Keywords Everywhere (Hijacked from #{domain_name})"
            } for item in items if item.get("keyword")]
    except Exception as e:
        console.print(f"[yellow]⚠️ KE Competitor Keywords error: {e}[/yellow]")
    return []

# -----------------------------------------------------------------------------
# Master Multi-Source Expansion Workflow
# -----------------------------------------------------------------------------
def run_multisource_expansion(keyword: str, geo: str = "UK", force_refresh: bool = False):
    location_code, language_code, location_name = load_location(geo)
    client = DataForSEOClient()
    ke_api_key = os.getenv("KEYWORDS_EVERYWHERE_API_KEY")

    console.print(Panel(
        f"[bold cyan]🚀 Multi-Source 4-Way Keyword Expansion Engine[/bold cyan]\n"
        f"Seed Keyword: [bold white]'{keyword}'[/bold white]\n"
        f"Target Market: [bold white]{location_name} (code: {location_code})[/bold white]\n"
        f"KE API Engine: [bold green]{'Active & Authenticated' if ke_api_key else 'Disabled (No Key)'}[/bold green]",
        border_style="cyan"
    ))

    # 1. Pull Source 1: DataForSEO Suggestions
    console.print("⏳ [1/4] Pulling Seed Suggestions from DataForSEO Labs...")
    dfs_suggestions = get_dataforseo_suggestions(client, keyword, location_code, language_code, limit=15, force_refresh=force_refresh)
    console.print(f"  ✓ Retrieved [bold]{len(dfs_suggestions)}[/bold] suggestions with Volume & CPC")

    # 2. Pull Source 2: Google SERP PAA Questions
    console.print("⏳ [2/4] Extracting Searcher Journey PAA Questions from Google SERP...")
    paa_questions, top_competitors = get_serp_signals(client, keyword, location_code, language_code, force_refresh=force_refresh)
    console.print(f"  ✓ Retrieved [bold]{len(paa_questions)}[/bold] PAA questions and identified top competitors")

    # 3. Pull Source 3: Keywords Everywhere PASF
    console.print("⏳ [3/4] Pulling Lateral Search Branches from Keywords Everywhere (PASF)...")
    pasf_keywords = get_ke_pasf(keyword, ke_api_key, limit=10)
    console.print(f"  ✓ Retrieved [bold]{len(pasf_keywords)}[/bold] PASF keywords")

    # 4. Pull Source 4: Keywords Everywhere Competitor URL Hijack
    competitor_keywords = []
    if top_competitors:
        primary_comp = top_competitors[0]
        console.print(f"⏳ [4/4] Hijacking Ranking Keywords from Competitor #1: [bold]{primary_comp}[/bold]...")
        competitor_keywords = get_ke_competitor_keywords(primary_comp, ke_api_key, country=geo, limit=10)
        console.print(f"  ✓ Hijacked [bold]{len(competitor_keywords)}[/bold] ranked queries driving competitor traffic")

    # 5. Deduplicate and Fuse into Master Candidate Pool
    master_pool = {}
    
    # Priority order for deduplication metadata
    all_batches = [dfs_suggestions, competitor_keywords, pasf_keywords, paa_questions]
    for batch in all_batches:
        for item in batch:
            kw_clean = item["keyword"].strip().lower()
            if kw_clean not in master_pool:
                master_pool[kw_clean] = item
            else:
                # Merge sources
                existing = master_pool[kw_clean]
                if item["source"] not in existing["source"]:
                    existing["source"] += f", {item['source']}"
                if item["volume"] > existing["volume"]:
                    existing["volume"] = item["volume"]
                if item["cpc"] > existing["cpc"]:
                    existing["cpc"] = item["cpc"]

    # 6. Display Multi-Source Breakdown by Intent
    console.print(f"\n[bold green]✨ Total Unique Keywords Expanded:[/bold green] [bold white]{len(master_pool)} keywords[/bold white] (across 4 sources)\n")

    # Group by Intent
    intent_groups = {"commercial": [], "informational": []}
    for kw_entry in master_pool.values():
        intent = kw_entry.get("intent", "informational")
        if intent in intent_groups:
            intent_groups[intent].append(kw_entry)
        else:
            intent_groups["informational"].append(kw_entry)

    # Sort commercial by volume/traffic descending
    for intent, items in intent_groups.items():
        table = Table(title=f"Intent Cluster: {intent.upper()} ({len(items)} keywords)", header_style="bold magenta")
        table.add_column("Keyword", style="bold white")
        table.add_column("Vol / Est. Traffic", justify="right")
        table.add_column("CPC", justify="right")
        table.add_column("Sourced From", style="dim")

        # Sort: items with volume first, then alphabetical
        sorted_items = sorted(items, key=lambda x: -x["volume"])
        for k in sorted_items[:12]:
            vol_display = f"{k['volume']:,}" if k['volume'] > 0 else "N/A"
            cpc_display = f"${k['cpc']:.2f}" if k['cpc'] > 0 else "-"
            table.add_row(k["keyword"], vol_display, cpc_display, k["source"])

        console.print(table)
        console.print()

    # 7. Save to Debug Output
    output_path = Path(__file__).resolve().parent / "output" / "debug" / "multisource_keywords.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "seed_keyword": keyword,
            "geo": geo,
            "total_expanded": len(master_pool),
            "sources": {
                "dataforseo_suggestions_count": len(dfs_suggestions),
                "serp_paa_count": len(paa_questions),
                "ke_pasf_count": len(pasf_keywords),
                "ke_competitor_hijack_count": len(competitor_keywords)
            },
            "keywords": list(master_pool.values())
        }, f, indent=2)

    console.print(f"💾 Multi-source keyword pool saved to: [dim]{output_path}[/dim]")
    console.print(f"\n[bold cyan]{guard.summary()}[/bold cyan]\n")

def main():
    parser = argparse.ArgumentParser(description="Multi-Source 4-Way Keyword Expansion Engine.")
    parser.add_argument("keyword", nargs="?", default="best crm software", help="Seed keyword")
    parser.add_argument("--geo", default="UK", choices=["UK", "US", "CA", "AU"], help="Target country code")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass local cache")
    args = parser.parse_args()

    run_multisource_expansion(args.keyword, args.geo, args.force_refresh)

if __name__ == "__main__":
    main()
