#!/usr/bin/env python3
"""
02_test_aio_serp.py
-------------------
Tests Google Live Advanced SERP scraping.
Detects:
- AI Overviews presence & cited sources
- People Also Ask (PAA) questions
- Featured Snippets
- Top 10 Organic Competitors
Prunes the 100KB+ raw JSON into a clean, high-signal data object.
"""

import sys
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
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

def run_serp_test(keyword: str, geo: str = "UK", force_refresh: bool = False):
    location_code, language_code, location_name = load_location(geo)
    client = DataForSEOClient()

    console.print(f"\n[bold cyan]🎯 Querying Live SERP & AI Overview for:[/bold cyan] '{keyword}'")
    console.print(f"📍 Location: [bold white]{location_name} (code: {location_code})[/bold white] | Lang: [bold white]{language_code}[/bold white]")

    payload = {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": "desktop",
        "os": "windows",
        "depth": 20
    }

    try:
        res = client.request(
            method="POST",
            path="/v3/serp/google/organic/live/advanced",
            payload=payload,
            force_refresh=force_refresh
        )

        from_cache = res.get("_from_cache", False)
        status_msg = "[yellow](from 24h local cache - $0.00 spent)[/yellow]" if from_cache else "[green](live network call)[/green]"
        console.print(f"📦 Response Status: {status_msg}")

        data = res["data"]
        items = data["tasks"][0]["result"][0].get("items", [])

        # Parse Key SEO Signals
        ai_overview = None
        paa_questions = []
        featured_snippet = None
        organic_results = []

        for item in items:
            itype = item.get("type")
            if itype == "ai_overview":
                raw_text = item.get("markdown") or item.get("text") or ""
                if not raw_text and item.get("items"):
                    raw_text = "\n".join(elem.get("text", "") for elem in item.get("items", []) if elem.get("text"))

                sources = []
                refs = item.get("references", []) or item.get("sources", [])
                for ref in refs:
                    url = ref.get("url")
                    title = ref.get("title") or ref.get("source") or ref.get("domain") or url
                    domain = ref.get("domain") or ""
                    if url:
                        sources.append({"domain": domain, "title": title, "url": url})

                ai_overview = {
                    "text": raw_text[:400] + ("..." if len(raw_text) > 400 else ""),
                    "full_markdown": raw_text,
                    "sources": sources
                }
            elif itype == "people_also_ask":
                for q_item in item.get("items", []):
                    if q_item.get("title"):
                        paa_questions.append(q_item.get("title"))
            elif itype == "featured_snippet":
                featured_snippet = {
                    "title": item.get("title"),
                    "domain": item.get("domain"),
                    "description": item.get("description")
                }
            elif itype == "organic" and len(organic_results) < 10:
                organic_results.append({
                    "rank": item.get("rank_group"),
                    "domain": item.get("domain"),
                    "title": item.get("title"),
                    "url": item.get("url")
                })

        # Display AI Overview Findings
        if ai_overview:
            source_lines = [f"  • [bold]{s['domain']}[/bold]: {s['title']}\n    [dim]{s['url']}[/dim]" for s in ai_overview['sources']]
            sources_display = "\n".join(source_lines) if source_lines else "  (None explicitly listed)"
            console.print(Panel(
                f"[bold green]✅ AI Overview Triggered![/bold green]\n\n"
                f"[italic white]{ai_overview['text']}[/italic white]\n\n"
                f"[bold cyan]Cited Sources ({len(ai_overview['sources'])}):[/bold cyan]\n"
                f"{sources_display}",
                title="Google AI Overview Detected",
                border_style="green"
            ))
        else:
            console.print(Panel(
                "[yellow]ℹ️ No AI Overview returned on this SERP. Search displays traditional blue links / SERP features.[/yellow]",
                title="AI Overview Status",
                border_style="yellow"
            ))

        # Display PAA Questions
        if paa_questions:
            console.print(f"\n[bold magenta]❓ People Also Ask ({len(paa_questions)} questions found):[/bold magenta]")
            for q in paa_questions[:5]:
                console.print(f"  • {q}")

        # Display Top 5 Organic Competitors
        table = Table(title="\nTop Organic Competitors", show_header=True, header_style="bold blue")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Domain", style="bold white", width=25)
        table.add_column("Title", style="italic")

        for org in organic_results[:5]:
            table.add_row(str(org["rank"]), org["domain"], org["title"])

        console.print(table)

        # Save clean debug file
        debug_output = {
            "keyword": keyword,
            "location": location_name,
            "ai_overview": ai_overview,
            "people_also_ask": paa_questions,
            "featured_snippet": featured_snippet,
            "organic_top_10": organic_results
        }
        debug_path = Path(__file__).resolve().parent / "output" / "debug" / "serp_summary.json"
        with open(debug_path, "w", encoding="utf-8") as f:
            json.dump(debug_output, f, indent=2)

        console.print(f"\n[dim]💾 Pruned summary saved to: {debug_path}[/dim]")
        console.print(f"[bold cyan]{guard.summary()}[/bold cyan]\n")

    except DataForSEOAPIError as e:
        console.print(f"[bold red]❌ API Error [{e.code}]:[/bold red] {e.message}")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

def main():
    parser = argparse.ArgumentParser(description="Test Google Live SERP and AI Overview extraction.")
    parser.add_argument("keyword", nargs="?", default="best crm for small business", help="Target keyword to search")
    parser.add_argument("--geo", default="UK", choices=["UK", "US", "CA", "AU"], help="Target country code")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass 24h cache and force live API call")
    args = parser.parse_args()

    run_serp_test(args.keyword, args.geo, args.force_refresh)

if __name__ == "__main__":
    main()
