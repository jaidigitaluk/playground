#!/usr/bin/env python3
"""
06_entity_semantic_clustering.py
--------------------------------
Gap 3 Fix: Entity & Semantic Intent Depth Engine.
Transforms raw keywords and competitor heading hierarchies into an authoritative Semantic Entity Footprint.
Categorizes topical entities into 4 strategic pillars:
1. Brand & Product Entities (Top Competitors that Google expects to be evaluated)
2. Feature & Functional Entities (Core CRM capabilities required for topical breadth)
3. Target Persona & Segment Entities (Who the software is for: small business, enterprise, startups)
4. Evaluation & Decision Criteria (Ease of use, pricing tiers, workflow automation, AI capabilities)
"""

import sys
import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Pre-defined known category concept patterns for entity classification
KNOWN_FEATURE_PATTERNS = [
    r"automation", r"pipeline", r"workflow", r"reporting", r"analytics", r"forecasting",
    r"lead\s+scoring", r"contact\s+management", r"email", r"customis", r"customiz",
    r"integration", r"single\s+source\s+of\s+truth", r"api", r"tracking", r"sales\s+cloud",
    r"mobile", r"inbox", r"ai\s+features", r"ambient\s+ai"
]

KNOWN_PERSONA_PATTERNS = [
    r"small\s+business", r"enterprise", r"startup", r"one\s+person", r"solopreneur",
    r"companies", r"sales\s+team", r"business\s+size"
]

KNOWN_CRITERIA_PATTERNS = [
    r"pricing", r"free", r"freeware", r"cost", r"pros\s+&\s+cons", r"ease\s+of\s+use",
    r"at\s+a\s+glance", r"versatility", r"extensibility", r"specs", r"configuration",
    r"value", r"reviews", r"testing", r"support"
]

def clean_entity_text(text: str) -> str:
    """Cleans punctuation, numbering, and trailing noise."""
    t = re.sub(r"^\d+[\.\-\)]\s*", "", text)
    t = re.sub(r"\(.*?\)", "", t)
    return t.strip()

def extract_entities_from_audit(audit_file: Path, kw_file: Path) -> Dict[str, Any]:
    """Extracts entities from competitor on-page headings, AI overview text, and multi-source keywords."""
    competitor_headings = []
    competitors_crawled = []
    
    if audit_file.exists():
        with open(audit_file, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
            for comp in audit_data.get("competitors", []):
                domain = comp.get("domain", "")
                competitors_crawled.append(domain)
                for h in comp.get("h2", []) + comp.get("h3", []):
                    cleaned = clean_entity_text(h)
                    if len(cleaned) > 2:
                        competitor_headings.append((cleaned, domain))

    expanded_keywords = []
    if kw_file.exists():
        with open(kw_file, "r", encoding="utf-8") as f:
            kw_data = json.load(f)
            for item in kw_data.get("keywords", []):
                expanded_keywords.append(item["keyword"])

    # 1. Mine Brand / Product Entities
    # Look for known CRM brand names and capitalized product phrases
    brand_counter = Counter()
    feature_counter = Counter()
    persona_counter = Counter()
    criteria_counter = Counter()

    # Common CRM brands dictionary for high-precision detection
    COMMON_CRM_BRANDS = [
        "Salesforce", "HubSpot", "Zoho", "Monday", "Monday.com", "Pipedrive",
        "Creatio", "Apptivo", "Insightly", "SugarCRM", "Ontraport", "Nimble",
        "Microsoft Dynamics", "Act!", "Freshsales", "Oracle", "ClickUp"
    ]

    all_text_corpus = " ".join([h[0] for h in competitor_headings] + expanded_keywords)

    for brand in COMMON_CRM_BRANDS:
        pattern = re.compile(rf"\b{re.escape(brand)}\b", re.IGNORECASE)
        matches = len(pattern.findall(all_text_corpus))
        if matches > 0:
            brand_counter[brand] = matches

    # 2. Mine Feature & Functional Entities
    for h_text, _ in competitor_headings:
        for feat in KNOWN_FEATURE_PATTERNS:
            if re.search(feat, h_text, re.IGNORECASE):
                feature_counter[clean_entity_text(h_text)] += 1

    # 3. Mine Persona Entities
    for h_text, _ in competitor_headings:
        for pers in KNOWN_PERSONA_PATTERNS:
            if re.search(pers, h_text, re.IGNORECASE):
                persona_counter[clean_entity_text(h_text)] += 1
    for kw in expanded_keywords:
        for pers in KNOWN_PERSONA_PATTERNS:
            if re.search(pers, kw, re.IGNORECASE):
                persona_counter[kw] += 1

    # 4. Mine Decision Criteria Entities
    for h_text, _ in competitor_headings:
        for crit in KNOWN_CRITERIA_PATTERNS:
            if re.search(crit, h_text, re.IGNORECASE):
                criteria_counter[clean_entity_text(h_text)] += 1

    return {
        "competitors_crawled": competitors_crawled,
        "brands": brand_counter.most_common(12),
        "features": feature_counter.most_common(8),
        "personas": persona_counter.most_common(6),
        "criteria": criteria_counter.most_common(8)
    }

def run_entity_clustering(keyword: str):
    debug_dir = Path(__file__).resolve().parent / "output" / "debug"
    audit_file = debug_dir / "competitor_audit.json"
    kw_file = debug_dir / "multisource_keywords.json"

    console.print(Panel(
        f"[bold cyan]🧠 Entity & Semantic Intent Depth Engine[/bold cyan]\n"
        f"Target Topic: [bold white]'{keyword}'[/bold white]\n"
        f"Input Sources: Competitor On-Page DOM + 4-Way Multi-Source Keyword Graph",
        border_style="cyan"
    ))

    if not audit_file.exists() or not kw_file.exists():
        console.print("[yellow]⚠️ Warning: audit files not found. Run 04_competitor_onpage.py and 05_multisource_keyword_expansion.py first.[/yellow]")
        return

    entities = extract_entities_from_audit(audit_file, kw_file)

    # Display Brand Entities Table
    brand_table = Table(title="1. Mandatory Brand / Vendor Entities (Expected by Google)", header_style="bold green")
    brand_table.add_column("Entity / Product", style="bold white")
    brand_table.add_column("SERP & Content Salience (Mentions)", justify="right")
    brand_table.add_column("Strategic Role", style="dim")

    for brand, count in entities["brands"][:8]:
        brand_table.add_row(
            brand,
            str(count),
            "Core Competitor / Mandatory Benchmark" if count >= 3 else "High-Salience Alternative"
        )
    console.print(brand_table)
    console.print()

    # Display Functional Feature Entities Table
    feat_table = Table(title="2. Core Functional Feature Entities (Topical Breadth)", header_style="bold cyan")
    feat_table.add_column("Feature Entity / Capability", style="bold white")
    feat_table.add_column("Frequency", justify="right")
    feat_table.add_column("Required On-Page Placement", style="dim")

    for feat, count in entities["features"][:6]:
        feat_table.add_row(
            feat,
            str(count),
            "Dedicated H2 / H3 Section" if count >= 2 else "Evaluation Matrix Row"
        )
    console.print(feat_table)
    console.print()

    # Display Persona & Segment Entities Table
    pers_table = Table(title="3. Target Persona & Market Segments (Commercial Alignment)", header_style="bold yellow")
    pers_table.add_column("Target Persona / Segment", style="bold white")
    pers_table.add_column("SERP Frequency", justify="right")
    pers_table.add_column("Content Architecture Alignment", style="dim")

    for pers, count in entities["personas"][:5]:
        pers_table.add_row(
            pers,
            str(count),
            "Filter Category ('Best for [X]')"
        )
    console.print(pers_table)
    console.print()

    # Display Evaluation Criteria Table
    crit_table = Table(title="4. Decision Criteria & GEO Triggers (AI Overview Salience)", header_style="bold magenta")
    crit_table.add_column("Decision Criteria", style="bold white")
    crit_table.add_column("Frequency", justify="right")
    crit_table.add_column("GEO Format", style="dim")

    for crit, count in entities["criteria"][:6]:
        crit_table.add_row(
            crit,
            str(count),
            "Comparison Table / Bulleted List"
        )
    console.print(crit_table)

    # Save to Debug Output
    output_path = debug_dir / "semantic_entities.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "target_topic": keyword,
            "entities": {
                "brands": entities["brands"],
                "features": entities["features"],
                "personas": entities["personas"],
                "criteria": entities["criteria"]
            }
        }, f, indent=2)

    console.print(f"\n💾 Full semantic entity graph saved to: [dim]{output_path}[/dim]\n")

def main():
    parser = argparse.ArgumentParser(description="Extract and cluster semantic entities from competitor on-page and keyword graphs.")
    parser.add_argument("keyword", nargs="?", default="best crm software", help="Target topic")
    args = parser.parse_args()

    run_entity_clustering(args.keyword)

if __name__ == "__main__":
    main()
