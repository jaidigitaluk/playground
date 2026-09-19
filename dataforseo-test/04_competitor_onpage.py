#!/usr/bin/env python3
"""
04_competitor_onpage.py
-----------------------
Extracts and synthesizes on-page content benchmarks from the top organic competitors.
Features:
1. UGC / Forum Exclusion Filter: Skips Reddit, Quora, YouTube, Pinterest, etc. to pick true editorial competitors.
2. Micro-crawl via DataForSEO `/v3/on_page/instant_pages` ($0.00015 per page).
3. Benchmark Metrics: Word count average, readability index, and link counts.
4. Content Gap / Superset Heading Synthesis: Merges table-stakes H2/H3s with unique competitor topics to build an objectively superior outline.
"""

import sys
import json
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from _system.client import DataForSEOClient, DataForSEOAPIError
from _system.guardrails import guard

console = Console()

LOCATIONS_PATH = Path(__file__).resolve().parent / "_config" / "locations.json"

# Domains that should NOT be crawled as editorial content competitors
EXCLUDED_DOMAINS = {
    "reddit.com", "www.reddit.com",
    "quora.com", "www.quora.com",
    "youtube.com", "www.youtube.com",
    "pinterest.com", "www.pinterest.com",
    "twitter.com", "x.com",
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com",
    "linkedin.com", "www.linkedin.com"
}

def load_location(geo_code: str = "UK") -> tuple:
    if LOCATIONS_PATH.exists():
        with open(LOCATIONS_PATH, "r", encoding="utf-8") as f:
            locs = json.load(f)
            geo = locs.get(geo_code.upper(), locs.get("UK"))
            return geo["location_code"], geo["language_code"], geo["name"]
    return 2826, "en", "United Kingdom"

def is_excluded_domain(domain: str) -> bool:
    if not domain:
        return True
    domain_clean = domain.lower().strip()
    for excl in EXCLUDED_DOMAINS:
        if domain_clean == excl or domain_clean.endswith("." + excl):
            return True
    return False

def get_top_organic_urls(keyword: str, geo: str = "UK", num_competitors: int = 3, force_refresh: bool = False) -> List[Dict[str, Any]]:
    """Runs or retrieves cached SERP to extract top non-UGC organic competitor URLs."""
    location_code, language_code, _ = load_location(geo)
    client = DataForSEOClient()

    payload = {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": "desktop",
        "depth": 20
    }

    res = client.request("POST", "/v3/serp/google/organic/live/advanced", payload, force_refresh=force_refresh)
    items = res["data"]["tasks"][0]["result"][0].get("items", [])

    candidates = []
    skipped = []

    for item in items:
        if item.get("type") == "organic":
            domain = item.get("domain", "")
            url = item.get("url", "")
            rank = item.get("rank_group")

            if is_excluded_domain(domain):
                skipped.append((rank, domain, "UGC/Social/Video domain"))
                continue

            candidates.append({
                "rank": rank,
                "domain": domain,
                "title": item.get("title", ""),
                "url": url
            })

            if len(candidates) >= num_competitors:
                break

    if skipped:
        console.print(f"[dim]ℹ️ Filtered out non-editorial domains:[/dim] " + ", ".join(f"#{r} {d} ({reason})" for r, d, reason in skipped))

    return candidates

def crawl_page_content(client: DataForSEOClient, url: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Calls /v3/on_page/instant_pages to get word count, headings, and readability."""
    payload = {"url": url}
    res = client.request("POST", "/v3/on_page/instant_pages", payload, force_refresh=force_refresh)
    task = res["data"]["tasks"][0]
    result_items = task.get("result", [{}])[0].get("items", [])
    
    if not result_items:
        return {"error": "No content returned"}

    item = result_items[0]
    meta = item.get("meta", {})
    content = meta.get("content", {})
    htags = meta.get("htags", {})

    # Clean headings: strip excessive whitespace and numbers like '1. ' for clustering
    h1_list = [h.strip() for h in htags.get("h1", []) if h and h.strip()]
    h2_list = [h.strip() for h in htags.get("h2", []) if h and h.strip()]
    h3_list = [h.strip() for h in htags.get("h3", []) if h and h.strip()]

    return {
        "url": url,
        "title": meta.get("title", ""),
        "word_count": content.get("plain_text_word_count", 0),
        "readability_index": content.get("flesch_kincaid_readability_index", 0.0),
        "internal_links": meta.get("internal_links_count", 0),
        "external_links": meta.get("external_links_count", 0),
        "images_count": meta.get("images_count", 0),
        "h1": h1_list,
        "h2": h2_list,
        "h3": h3_list
    }

BOILERPLATE_HEADINGS = {
    "share this", "share this article", "newsletter", "sign up", "related articles",
    "related posts", "comments", "leave a reply", "table of contents", "navigation",
    "search", "popular posts", "subscribe", "footer", "author", "about the author",
    "recent posts", "more from", "advertiser disclosure", "methodology", "faq", "frequently asked questions"
}

def clean_heading_text(heading: str) -> str:
    """Removes leading numbering and trims whitespace."""
    return re.sub(r"^\d+[\.\-\)]\s*", "", heading).strip()

def is_boilerplate_heading(heading: str) -> bool:
    norm = clean_heading_text(heading).lower()
    return norm in BOILERPLATE_HEADINGS or len(norm) < 3

def build_superset_headings(competitor_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identifies common core table-stakes H2s vs unique differentiator H2s."""
    all_h2_map = {}

    for page in competitor_pages:
        domain = page.get("domain", "Competitor")
        for h2 in page.get("h2", []):
            if is_boilerplate_heading(h2):
                continue
            norm = clean_heading_text(h2).lower()
            if norm not in all_h2_map:
                all_h2_map[norm] = {"original": h2, "competitors": [domain]}
            else:
                if domain not in all_h2_map[norm]["competitors"]:
                    all_h2_map[norm]["competitors"].append(domain)

    # Group into Core (present in 2+ competitors) and Unique Differentiators (present in 1)
    core_headings = []
    unique_headings = []

    for norm, data in all_h2_map.items():
        if len(data["competitors"]) >= 2:
            core_headings.append(data)
        else:
            unique_headings.append(data)

    return {
        "core": core_headings,
        "unique": unique_headings
    }

def run_competitor_audit(keyword: str, geo: str = "UK", num_competitors: int = 3, force_refresh: bool = False):
    location_code, language_code, location_name = load_location(geo)
    client = DataForSEOClient()

    console.print(Panel(
        f"[bold cyan]🔍 Competitor On-Page Extraction & Superset Synthesis[/bold cyan]\n"
        f"Target Keyword: [bold white]'{keyword}'[/bold white]\n"
        f"Market: [bold white]{location_name}[/bold white] | Analyzing Top [bold white]{num_competitors}[/bold white] Editorial Competitors",
        border_style="cyan"
    ))

    # 1. Get Top Qualified Competitors
    competitors = get_top_organic_urls(keyword, geo, num_competitors, force_refresh)
    if not competitors:
        console.print("[bold red]❌ No valid competitors found.[/bold red]")
        return

    console.print(f"\n[bold green]Selected Top {len(competitors)} Editorial Competitors:[/bold green]")
    for c in competitors:
        console.print(f"  • Rank #{c['rank']} [bold]{c['domain']}[/bold] -> {c['url']}")

    # 2. Crawl Content For Each Competitor
    crawled_pages = []
    console.print("\n⏳ Crawling competitor on-page content structures...")
    for comp in competitors:
        console.print(f"  • Crawling [bold]{comp['domain']}[/bold]...")
        page_data = crawl_page_content(client, comp["url"], force_refresh)
        page_data["rank"] = comp["rank"]
        page_data["domain"] = comp["domain"]
        crawled_pages.append(page_data)

    # 3. Calculate Benchmark Metrics
    valid_pages = [p for p in crawled_pages if p.get("word_count", 0) > 0]
    word_counts = [p["word_count"] for p in valid_pages]
    avg_words = int(sum(word_counts) / len(word_counts)) if word_counts else 0
    max_words = max(word_counts) if word_counts else 0
    min_words = min(word_counts) if word_counts else 0
    target_words = int(avg_words * 1.10) # 10% above average for superior topical coverage

    # 4. Display Benchmark Table
    bench_table = Table(title="Competitor On-Page Benchmarks", header_style="bold magenta")
    bench_table.add_column("Rank", style="dim", justify="center")
    bench_table.add_column("Domain", style="bold white")
    bench_table.add_column("Word Count", justify="right")
    bench_table.add_column("H2 Count", justify="right")
    bench_table.add_column("H3 Count", justify="right")
    bench_table.add_column("Readability (FK)", justify="center")

    for p in valid_pages:
        bench_table.add_row(
            f"#{p['rank']}",
            p["domain"],
            f"{p['word_count']:,}",
            str(len(p.get("h2", []))),
            str(len(p.get("h3", []))),
            f"{p.get('readability_index', 0.0):.1f}"
        )
    console.print(bench_table)

    console.print(f"\n🎯 [bold]Target Word Count Recommendation:[/bold] [bold green]{target_words:,} words[/bold green] (Min: {min_words:,}, Avg: {avg_words:,}, Max: {max_words:,})")

    # 5. Build and Display Superset Heading Architecture
    heading_analysis = build_superset_headings(valid_pages)
    
    console.print(Panel(
        f"[bold green]🏆 Table-Stakes H2 Themes (Present in Multiple Competitors):[/bold green]\n" +
        ("\n".join(f"  • [bold]{h['original']}[/bold] [dim]({', '.join(h['competitors'])})[/dim]" for h in heading_analysis["core"][:6]) if heading_analysis["core"] else "  (Headings differed significantly across competitors)") +
        f"\n\n[bold yellow]💎 Content Gap Gems / Unique Sub-Topics (To Outrank Competitors):[/bold yellow]\n" +
        "\n".join(f"  • {h['original']} [dim](from {h['competitors'][0]})[/dim]" for h in heading_analysis["unique"][:8]),
        title="Synthesized Superset Heading Blueprint",
        border_style="green"
    ))

    console.print(f"\n[bold cyan]{guard.summary()}[/bold cyan]\n")

    # 6. Save audit to output/debug
    output_path = Path(__file__).resolve().parent / "output" / "debug" / "competitor_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "keyword": keyword,
            "geo": geo,
            "target_word_count": target_words,
            "average_word_count": avg_words,
            "competitors": valid_pages,
            "superset_headings": heading_analysis
        }, f, indent=2)
    console.print(f"💾 Full competitor audit saved to: [dim]{output_path}[/dim]")

def main():
    parser = argparse.ArgumentParser(description="Extract and benchmark competitor on-page content structures.")
    parser.add_argument("keyword", nargs="?", default="best crm software", help="Target keyword")
    parser.add_argument("--geo", default="UK", choices=["UK", "US", "CA", "AU"], help="Target country code")
    parser.add_argument("--limit", type=int, default=3, help="Number of editorial competitors to crawl")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass local cache")
    args = parser.parse_args()

    run_competitor_audit(args.keyword, args.geo, args.limit, args.force_refresh)

if __name__ == "__main__":
    main()
