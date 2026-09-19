#!/usr/bin/env python3
"""
workflow_full_planner.py
------------------------
Master Enterprise SEO & AI Overview Blueprint Generator (Fully Upgraded).
Fuses all 4 intelligence layers:
1. Live SERP & Generative Engine Optimization (GEO / AI Overviews & PAA).
2. Competitor On-Page Extraction (UGC filter, target word count benchmarks, heading superset).
3. 4-Way Multi-Source Keyword Expansion (DataForSEO Labs + SERP PAA + KE PASF + Competitor Hijack).
4. Semantic Entity & Topical Depth Footprint (Brands, Features, Personas, Decision Criteria).
5. Production-grade Markdown Deliverable Synthesis.
"""

import os
import sys
from pathlib import Path

# Auto-reexecute using local virtual environment if not already active
_venv_python = Path(__file__).resolve().parent / "venv" / "bin" / "python3"
if _venv_python.exists() and sys.executable != str(_venv_python) and "VIRTUAL_ENV" not in os.environ:
    os.execv(str(_venv_python), [str(_venv_python)] + sys.argv)

import json
import re
import argparse
from datetime import datetime
from typing import List, Dict, Any, Tuple
from collections import Counter
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from _system.client import DataForSEOClient, DataForSEOAPIError
from _system.guardrails import guard

load_dotenv(override=True)
console = Console()

LOCATIONS_PATH = Path(__file__).resolve().parent / "_config" / "locations.json"

EXCLUDED_DOMAINS = {
    "reddit.com", "www.reddit.com",
    "quora.com", "www.quora.com",
    "youtube.com", "www.youtube.com",
    "pinterest.com", "www.pinterest.com",
    "twitter.com", "x.com",
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com",
    "linkedin.com", "www.linkedin.com",
    "indeed.com", "uk.indeed.com", "www.indeed.com",
    "glassdoor.com", "www.glassdoor.com", "glassdoor.co.uk", "www.glassdoor.co.uk",
    "reed.co.uk", "www.reed.co.uk",
    "totaljobs.com", "www.totaljobs.com",
    "upwork.com", "www.upwork.com",
    "fiverr.com", "www.fiverr.com"
}

BOILERPLATE_HEADINGS = {
    "share this", "share this article", "newsletter", "sign up", "related articles",
    "related posts", "comments", "leave a reply", "table of contents", "navigation",
    "search", "popular posts", "subscribe", "footer", "author", "about the author",
    "recent posts", "more from", "advertiser disclosure", "methodology", "faq", "frequently asked questions",
    "our clients", "our work", "our services", "services", "elevate", "contact us", "get in touch",
    "testimonials", "client reviews", "case studies", "meet the team", "about us", "why choose us"
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

US_GEO_COLLISIONS = {
    "beach", "california", "ca", "florida", "fl", "texas", "tx", "oregon", "or",
    "usa", "nyc", "york", "chicago", "los angeles", "la", "miami", "atlanta",
    "australia", "sydney", "melbourne", "toronto", "canada",
    "rhode island", "ri", "newport beach", "costa mesa", "orange county"
}

CITY_CENTROIDS = {
    "cardiff": {"lat": 51.4816, "lng": -3.1791, "region": "South Glamorgan", "postcode": "CF24 0EB"},
    "newport": {"lat": 51.5842, "lng": -2.9977, "region": "South Wales", "postcode": None},
    "swansea": {"lat": 51.6214, "lng": -3.9436, "region": "South Wales", "postcode": None},
    "bristol": {"lat": 51.4545, "lng": -2.5879, "region": "South West", "postcode": None},
    "london": {"lat": 51.5074, "lng": -0.1278, "region": "Greater London", "postcode": None},
    "birmingham": {"lat": 52.4862, "lng": -1.8904, "region": "West Midlands", "postcode": None},
    "manchester": {"lat": 53.4808, "lng": -2.2426, "region": "Greater Manchester", "postcode": None}
}

def format_keyword_title(keyword: str) -> str:
    """Format keyword to title case while respecting common SEO/marketing acronyms."""
    acronyms = {
        "seo": "SEO", "ppc": "PPC", "cro": "CRO", "b2b": "B2B", "b2c": "B2C",
        "ai": "AI", "cmo": "CMO", "roi": "ROI", "uk": "UK", "usa": "USA", "sem": "SEM"
    }
    words = keyword.strip().split()
    return " ".join(acronyms.get(w.lower(), w.capitalize()) for w in words)

def get_service_role_title(keyword: str, city: str = None) -> str:
    """Derive a natural role title from a keyword, stripping city duplication and ensuring a professional role noun."""
    k = keyword
    if city:
        k = re.sub(rf"\b{re.escape(city)}\b", "", k, flags=re.IGNORECASE).strip()
    for known_city in CITY_CENTROIDS:
        k = re.sub(rf"\b{re.escape(known_city)}\b", "", k, flags=re.IGNORECASE).strip()

    k_lower = k.lower()
    k_fmt = format_keyword_title(k)

    if any(k_lower.endswith(role) for role in ["consultant", "specialist", "expert", "advisor", "agency", "strategist", "manager", "partner"]):
        return k_fmt

    if "seo" in k_lower:
        return f"{k_fmt} Specialist" if k_fmt else "SEO Specialist"
    elif "ppc" in k_lower:
        return f"{k_fmt} Specialist" if k_fmt else "PPC Specialist"
    elif "marketing" in k_lower or "digital" in k_lower:
        return f"{k_fmt} Consultant" if k_fmt else "Marketing Consultant"
    elif "design" in k_lower:
        return f"{k_fmt} Partner" if k_fmt else "Design Partner"
    else:
        return f"{k_fmt} Specialist" if k_fmt else "Specialist"

def is_geo_mismatch(query: str, seed_keyword: str, target_geo: str = "UK") -> bool:
    """Filter out cross-Atlantic/foreign queries (e.g. Newport Beach, CA) unless explicitly in the seed."""
    if target_geo.upper() == "UK":
        q_lower = query.lower()
        seed_lower = seed_keyword.lower()
        for noise in US_GEO_COLLISIONS:
            pattern = rf"\b{re.escape(noise)}\b"
            if re.search(pattern, q_lower) and not re.search(pattern, seed_lower):
                return True
    return False

def clean_heading_text(heading: str) -> str:
    """Sanitize scraped headings: strip bullet points, trailing symbols/prepositions, and normalize case."""
    if not heading:
        return ""
    h = heading
    for _ in range(3):
        # Strip leading numbers/bullets/symbols/separators
        h = re.sub(r"^[\s\d\.\-\)\(\[\]•▪▫◆✓✔★☆*|—–:;]+", "", h)
        # Strip trailing symbols/bullets/separators
        h = re.sub(r"[\s\.\-\)\(\[\]•▪▫◆✓✔★☆*|—–:;]+$", "", h)
        h = h.strip()
        # Normalize excessive internal whitespace
        h = re.sub(r"\s+", " ", h)
        # Strip dangling trailing prepositions often left by split tags
        h = re.sub(r"\s+(for|with|of|by|and|in|at|on)$", "", h, flags=re.IGNORECASE).strip()

    # If heading is entirely uppercase and longer than 4 chars, convert to proper Title Case preserving acronyms
    if h.isupper() and len(h) > 4:
        acronyms = {"SEO", "PPC", "ROI", "B2B", "B2C", "AI", "CRO", "SEM", "UK", "USA", "GBP"}
        words = h.split()
        h = " ".join(w if w in acronyms else w.capitalize() for w in words)
    return h

def is_boilerplate_heading(heading: str) -> bool:
    norm = clean_heading_text(heading).lower()
    if len(norm) < 3:
        return True
    if norm in BOILERPLATE_HEADINGS:
        return True
    if any(norm.startswith(b + " ") or norm.endswith(" " + b) for b in BOILERPLATE_HEADINGS):
        return True
    if "frequently asked questions" in norm or "faq" in norm.split() or "faqs" in norm.split():
        return True
    return False

CROSS_SELL_PATTERNS = [
    r"web\s+design", r"website\s+design", r"graphic\s+design", r"branding\b", r"logo\b",
    r"app\s+development", r"it\s+support", r"from\s+[£$€]\d+", r"hosting\b", r"cyber\s+security",
    r"commercial\s+photography", r"video\s+production", r"signage", r"mobile-responsive"
]

GENERIC_CONVERSION_PATTERNS = [
    r"trusted\s+by", r"our\s+clients", r"meet\s+the\s+team",
    r"client\s+testimonials", r"what\s+our\s+clients\s+say", r"recent\s+work",
    r"our\s+portfolio", r"ready\s+to\s+get\s+started", r"request\s+a\s+quote",
    r"contact\s+our\s+team", r"stay\s+up\s+to\s+date", r"subscribe\s+to",
    r"follow\s+us\s+on", r"a\s+final\s+word\s+on", r"more\s+on\s+",
    r"get\s+my\s+free", r"free\s+proposal", r"our\s+services", r"our\s+approach",
    r"let['’]?s\s+talk", r"prosper\s+online", r"open\s+garden", r"global\s+team"
]

def is_topically_relevant(heading: str, seed_keyword: str) -> bool:
    """Filter out competitor cross-sell headings (e.g. web design on a PPC page) and generic conversion fluff."""
    cleaned = clean_heading_text(heading)
    h_lower = cleaned.lower()
    words = h_lower.split()
    
    # Exclude single-word headings unless recognized acronym
    if len(words) < 2 and h_lower not in {"seo", "ppc", "cro", "b2b", "b2c", "ai"}:
        return False

    seed_lower = seed_keyword.lower()
    
    for pat in CROSS_SELL_PATTERNS:
        if re.search(pat, h_lower) and not re.search(pat, seed_lower):
            return False
            
    for pat in GENERIC_CONVERSION_PATTERNS:
        if re.search(pat, h_lower):
            return False

    return True

GENERIC_INDUSTRY_TOKENS = {
    "seo", "ppc", "cro", "digital", "marketing", "agency", "agencies", "consultant",
    "consultancy", "consulting", "services", "service", "management", "specialist",
    "expert", "experts", "company", "companies", "group", "ltd", "uk", "cardiff",
    "newport", "swansea", "bristol", "london", "birmingham", "manchester", "wales",
    "content", "advertising", "media", "strategy", "solutions", "search", "google", "ads"
}

KNOWN_REGIONAL_BRANDS = {
    "liberty", "libertymarketing", "thomas design", "thrive", "spindogs",
    "we are boutique", "climb online", "bluefrog", "whitehat"
}

def is_competitor_brand_query(query: str, competitor_domains: List[str] = None) -> bool:
    """Detect competitor brand names and domain artifacts while strictly preserving generic commercial queries."""
    q_lower = query.lower().strip()
    
    # Check domain syntax artifacts
    if any(ext in q_lower for ext in [".co.uk", "co uk", ".com", ".org", ".net", " ltd", " limited"]):
        return True

    # Check known agency brand names
    for brand in KNOWN_REGIONAL_BRANDS:
        if brand in q_lower:
            return True

    if competitor_domains:
        for domain in competitor_domains:
            clean_d = re.sub(r"^(www\.)?", "", domain.lower())
            stem = clean_d.split(".")[0]
            parts = re.split(r"[-_]", stem)
            
            # Identify non-generic proprietary parts
            proprietary_parts = [p for p in parts if p not in GENERIC_INDUSTRY_TOKENS and len(p) >= 4]
            if not proprietary_parts:
                continue # Exact Match Domain composed only of generic terms (e.g. seo-agency-cardiff)
                
            for prop in proprietary_parts:
                pattern = rf"\b{re.escape(prop)}\b"
                if re.search(pattern, q_lower):
                    return True
                    
    return False

def format_cost_heading(title: str, city: str = None) -> str:
    """Format cost heading grammatically for both countable roles and uncountable services."""
    detected_city = city
    if not detected_city:
        for c in CITY_CENTROIDS:
            if re.search(rf"\b{re.escape(c)}\b", title, re.IGNORECASE):
                detected_city = c.capitalize()
                break

    base = title
    if detected_city:
        base = re.sub(rf"\b{re.escape(detected_city)}\b", "", base, flags=re.IGNORECASE).strip()
    
    base_fmt = format_keyword_title(base) if base else format_keyword_title(title)
    t_lower = base_fmt.lower()
    loc_suffix = f" in {detected_city}" if detected_city else ""
    
    person_nouns = ["consultant", "specialist", "expert", "advisor", "manager", "strategist", "agency"]
    if t_lower.endswith("services"):
        return f"How Much Do {base_fmt}{loc_suffix} Cost? (Rates & Pricing)"
    elif any(t_lower.endswith(p) for p in person_nouns):
        article = "an" if base_fmt.lower().startswith(('a', 'e', 'i', 'o', 'u')) or base_fmt.upper().startswith(('SEO', 'AI')) else "a"
        return f"How Much Does {article} {base_fmt}{loc_suffix} Cost? (Rates & Retainers)"
    else:
        return f"How Much Does {base_fmt}{loc_suffix} Cost? (Rates & Pricing)"

def format_service_headline(keyword: str, city: str = None) -> Dict[str, str]:
    """Format natural service headlines, H1s, and titles with proper prepositions."""
    detected_city = city
    if not detected_city:
        for c in CITY_CENTROIDS:
            if re.search(rf"\b{re.escape(c)}\b", keyword, re.IGNORECASE):
                detected_city = c.capitalize()
                break

    if detected_city:
        base_kw = re.sub(rf"\b{re.escape(detected_city)}\b", "", keyword, flags=re.IGNORECASE).strip()
        base_title = format_keyword_title(base_kw) if base_kw else format_keyword_title(keyword)
        
        if base_title.lower().endswith("consultant"):
            service_phrase = base_title[:-10].strip() + " Consultancy Services"
        elif base_title.lower().endswith("specialist"):
            service_phrase = base_title[:-10].strip() + " Services"
        elif not base_title.lower().endswith("services"):
            service_phrase = f"{base_title} Services"
        else:
            service_phrase = base_title
            
        h1 = f"{service_phrase} in {detected_city}"
        title_tag = f"{service_phrase} in {detected_city} | Senior Strategic Advisory"
        meta_desc = f"Looking for proven {service_phrase.lower()} in {detected_city}? Senior audits, strategic roadmaps, and measurable B2B pipeline growth across South Wales."
    else:
        base_title = format_keyword_title(keyword)
        if not base_title.lower().endswith("services") and not any(base_title.lower().endswith(r) for r in ["consultant", "specialist", "advisor"]):
            service_phrase = f"{base_title} Services"
        else:
            service_phrase = base_title
        h1 = f"{service_phrase} Built for Sustainable Revenue Growth"
        title_tag = f"{service_phrase} | B2B Growth Strategy & Audits"
        meta_desc = f"Senior {base_title.lower()} delivering measurable ROI. Comprehensive audits, search acquisition, and high-impact B2B pipeline acceleration."

    return {
        "h1": h1,
        "title_tag": title_tag,
        "meta_desc": meta_desc,
        "base_title": base_title if detected_city else format_keyword_title(keyword),
        "city": detected_city
    }

# -----------------------------------------------------------------------------
# Stage 1: Google Live Advanced SERP & AI Overviews
# -----------------------------------------------------------------------------
def fetch_serp_data(client: DataForSEOClient, keyword: str, location_code: int, language_code: str, force_refresh: bool = False) -> Dict[str, Any]:
    payload = {
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": "desktop",
        "depth": 20
    }
    res = client.request("POST", "/v3/serp/google/organic/live/advanced", payload, force_refresh=force_refresh)
    items = res["data"]["tasks"][0]["result"][0].get("items", [])

    ai_overview = None
    paa_questions = []
    organic_competitors = []

    for item in items:
        itype = item.get("type")
        if itype == "ai_overview":
            is_async = bool(item.get("asynchronous_ai_overview"))
            raw_text = item.get("markdown") or item.get("text") or ""
            if not raw_text and item.get("items"):
                raw_text = "\n".join(elem.get("text", "") for elem in (item.get("items") or []) if elem.get("text"))
            sources = []
            for ref in (item.get("references") or item.get("sources") or []):
                url = ref.get("url")
                if url:
                    sources.append(url)
            ai_overview = {
                "text": raw_text.strip(),
                "sources": sources,
                "is_async": is_async
            }
        elif itype == "people_also_ask":
            for q_item in item.get("items", []):
                q = q_item.get("title")
                if q:
                    paa_questions.append(q)
        elif itype == "organic":
            domain = item.get("domain", "")
            url = item.get("url", "")
            rank = item.get("rank_group")
            if not is_excluded_domain(domain):
                organic_competitors.append({
                    "rank": rank,
                    "domain": domain,
                    "title": item.get("title", ""),
                    "url": url
                })

    return {
        "ai_overview": ai_overview,
        "paa_questions": paa_questions,
        "competitors": organic_competitors
    }

# -----------------------------------------------------------------------------
# Stage 2: Competitor On-Page Extraction & Heading Superset
# -----------------------------------------------------------------------------
def audit_competitor_pages(client: DataForSEOClient, competitors: List[Dict[str, Any]], limit: int = 3, keyword: str = "", force_refresh: bool = False) -> Dict[str, Any]:
    crawled_pages = []
    target_competitors = competitors[:limit]

    for comp in target_competitors:
        try:
            res = client.request("POST", "/v3/on_page/instant_pages", {"url": comp["url"]}, force_refresh=force_refresh)
            task_items = res["data"]["tasks"][0].get("result", [{}])[0].get("items", []) or []
            if task_items and task_items[0]:
                item = task_items[0]
                meta = item.get("meta", {}) or {}
                content = meta.get("content", {}) or {}
                htags = meta.get("htags", {}) or {}

                h1_list = [clean_heading_text(h) for h in htags.get("h1", []) or [] if clean_heading_text(h) and len(clean_heading_text(h)) >= 3 and not is_boilerplate_heading(h) and (not keyword or is_topically_relevant(h, keyword))]
                h2_list = [clean_heading_text(h) for h in htags.get("h2", []) or [] if clean_heading_text(h) and len(clean_heading_text(h)) >= 3 and not is_boilerplate_heading(h) and (not keyword or is_topically_relevant(h, keyword))]
                h3_list = [clean_heading_text(h) for h in htags.get("h3", []) or [] if clean_heading_text(h) and len(clean_heading_text(h)) >= 3 and not is_boilerplate_heading(h) and (not keyword or is_topically_relevant(h, keyword))]

                crawled_pages.append({
                    "rank": comp["rank"],
                    "domain": comp["domain"],
                    "url": comp["url"],
                    "title": meta.get("title", comp["title"]),
                    "word_count": content.get("plain_text_word_count", 0),
                    "readability": content.get("flesch_kincaid_readability_index", 0.0),
                    "h1": h1_list,
                    "h2": h2_list,
                    "h3": h3_list
                })
        except Exception as e:
            console.print(f"[yellow]⚠️ Failed to crawl {comp['domain']}: {e}[/yellow]")

    valid_pages = [p for p in crawled_pages if p.get("word_count", 0) > 0]
    word_counts = [p["word_count"] for p in valid_pages]
    avg_words = int(sum(word_counts) / len(word_counts)) if word_counts else 0
    min_words = min(word_counts) if word_counts else 0
    max_words = max(word_counts) if word_counts else 0
    target_words = int(avg_words * 1.10) if avg_words > 0 else 1500

    # Superset headings builder
    all_h2_map = {}
    for p in valid_pages:
        d = p["domain"]
        for h in p["h2"]:
            norm = h.lower()
            if norm not in all_h2_map:
                all_h2_map[norm] = {"original": h, "competitors": [d]}
            elif d not in all_h2_map[norm]["competitors"]:
                all_h2_map[norm]["competitors"].append(d)

    core_h2s = [v for v in all_h2_map.values() if len(v["competitors"]) >= 2]
    unique_h2s = [v for v in all_h2_map.values() if len(v["competitors"]) == 1]

    return {
        "pages": valid_pages,
        "word_count_benchmarks": {
            "min": min_words,
            "avg": avg_words,
            "max": max_words,
            "target": target_words
        },
        "core_headings": core_h2s,
        "unique_headings": unique_h2s
    }

# -----------------------------------------------------------------------------
# Stage 3: Multi-Source 4-Way Keyword Expansion
# -----------------------------------------------------------------------------
def expand_keywords_multisource(
    client: DataForSEOClient,
    keyword: str,
    location_code: int,
    language_code: str,
    paa_questions: List[str],
    top_competitor_url: str,
    geo_code: str = "UK",
    competitor_domains: List[str] = None,
    force_refresh: bool = False
) -> Dict[str, Any]:
    ke_api_key = os.getenv("KEYWORDS_EVERYWHERE_API_KEY")
    master_pool = {}

    # 1. DataForSEO Suggestions
    try:
        kw_res = client.request(
            "POST",
            "/v3/dataforseo_labs/google/keyword_suggestions/live",
            {
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "include_seed_keyword": True,
                "limit": 15
            },
            force_refresh=force_refresh
        )
        items = kw_res["data"]["tasks"][0]["result"][0].get("items") or []

        # Intelligent relaxation fallback if ultra-specific multi-word query returns 0 items
        if not items and len(keyword.split()) >= 3:
            for known_city in CITY_CENTROIDS:
                if re.search(rf"\b{re.escape(known_city)}\b", keyword, re.IGNORECASE):
                    base_k = re.sub(rf"\b{re.escape(known_city)}\b", "", keyword, flags=re.IGNORECASE).strip()
                    if base_k:
                        relaxed_seed = f"{base_k.split()[0]} {known_city.capitalize()}"
                        try:
                            rel_res = client.request(
                                "POST",
                                "/v3/dataforseo_labs/google/keyword_suggestions/live",
                                {
                                    "keyword": relaxed_seed,
                                    "location_code": location_code,
                                    "language_code": language_code,
                                    "include_seed_keyword": True,
                                    "limit": 10
                                },
                                force_refresh=force_refresh
                            )
                            items = rel_res["data"]["tasks"][0]["result"][0].get("items") or []
                            if items:
                                break
                        except Exception:
                            pass

        for item in items:
            if not item:
                continue
            kw_data = item.get("keyword_data") if isinstance(item.get("keyword_data"), dict) else item
            kw = kw_data.get("keyword") or item.get("keyword")
            info = kw_data.get("keyword_info", {}) or item.get("keyword_info", {})
            intent_info = kw_data.get("search_intent_info", {}) or item.get("search_intent_info", {})
            if kw and not is_geo_mismatch(kw, keyword, geo_code):
                clean_k = kw.lower().strip()
                master_pool[clean_k] = {
                    "keyword": kw,
                    "volume": info.get("search_volume") or 0,
                    "cpc": float(info.get("cpc") or 0.0),
                    "intent": (intent_info.get("main_intent") or "commercial").lower(),
                    "source": "DataForSEO Labs",
                    "is_competitor_brand": is_competitor_brand_query(kw, competitor_domains)
                }
    except Exception as e:
        console.print(f"[yellow]⚠️ DataForSEO Suggestions failed: {e}[/yellow]")

    # 2. SERP PAA
    for q in paa_questions:
        clean_q = q.lower().strip()
        if clean_q not in master_pool and not is_geo_mismatch(q, keyword, geo_code):
            master_pool[clean_q] = {
                "keyword": q,
                "volume": 0,
                "cpc": 0.0,
                "intent": "informational",
                "source": "SERP People Also Ask",
                "is_competitor_brand": is_competitor_brand_query(q, competitor_domains)
            }

    # 3. Keywords Everywhere PASF
    ke_country = "uk" if geo_code.upper() in ["UK", "GB"] else geo_code.lower()
    if ke_api_key:
        try:
            r = requests.post(
                "https://api.keywordseverywhere.com/v1/get_pasf_keywords",
                headers={"Authorization": f"Bearer {ke_api_key}", "Accept": "application/json"},
                data={"keyword": keyword, "num": 10},
                timeout=15
            )
            pasf_items = []
            if r.status_code == 200:
                pasf_items = r.json().get("data", []) or []

            # Fallback relaxation for PASF
            if not pasf_items and len(keyword.split()) >= 3:
                for known_city in CITY_CENTROIDS:
                    if re.search(rf"\b{re.escape(known_city)}\b", keyword, re.IGNORECASE):
                        base_k = re.sub(rf"\b{re.escape(known_city)}\b", "", keyword, flags=re.IGNORECASE).strip()
                        if base_k:
                            relaxed_seed = f"{base_k.split()[0]} {known_city.capitalize()}"
                            r_rel = requests.post(
                                "https://api.keywordseverywhere.com/v1/get_pasf_keywords",
                                headers={"Authorization": f"Bearer {ke_api_key}", "Accept": "application/json"},
                                data={"keyword": relaxed_seed, "num": 8},
                                timeout=15
                            )
                            if r_rel.status_code == 200:
                                pasf_items = r_rel.json().get("data", []) or []
                                if pasf_items:
                                    break

            for kw in pasf_items:
                clean_kw = kw.lower().strip()
                if clean_kw not in master_pool and not is_geo_mismatch(kw, keyword, geo_code):
                    master_pool[clean_kw] = {
                        "keyword": kw,
                        "volume": 0,
                        "cpc": 0.0,
                        "intent": "commercial" if any(w in kw.lower() for w in ["best", "vs", "rate", "cost", "hire", "service", "freelance", "agency", "management"]) else "informational",
                        "source": "Keywords Everywhere (PASF)",
                        "is_competitor_brand": is_competitor_brand_query(kw, competitor_domains)
                    }
        except Exception:
            pass

    # 4. Keywords Everywhere Competitor Hijack
    if ke_api_key and top_competitor_url:
        try:
            r = requests.post(
                "https://api.keywordseverywhere.com/v1/get_url_keywords",
                headers={"Authorization": f"Bearer {ke_api_key}", "Accept": "application/json"},
                data={"url": top_competitor_url, "country": ke_country, "num": 8},
                timeout=15
            )
            if r.status_code == 200:
                for item in (r.json().get("data") or []):
                    kw = item.get("keyword")
                    if kw:
                        clean_kw = kw.lower().strip()
                        if clean_kw not in master_pool and not is_geo_mismatch(kw, keyword, geo_code):
                            master_pool[clean_kw] = {
                                "keyword": kw,
                                "volume": item.get("estimated_monthly_traffic", 0),
                                "cpc": 0.0,
                                "intent": "commercial" if any(w in kw.lower() for w in ["consultant", "agency", "services", "expert", "specialist"]) else "informational",
                                "source": "Keywords Everywhere (Competitor #1 Hijack)",
                                "is_competitor_brand": is_competitor_brand_query(kw, competitor_domains)
                            }
        except Exception:
            pass

    # 5. Sprint 3 (Gap 7): Batch Metric Enrichment for PAA & PASF via Keywords Everywhere
    unhydrated_kws = [v["keyword"] for v in master_pool.values() if v.get("volume", 0) == 0][:30]
    if ke_api_key and unhydrated_kws:
        try:
            enrich_resp = requests.post(
                "https://api.keywordseverywhere.com/v1/get_keyword_data",
                headers={"Authorization": f"Bearer {ke_api_key}", "Accept": "application/json"},
                data={
                    "country": ke_country,
                    "currency": "usd",
                    "dataSource": "cli",
                    "kw[]": unhydrated_kws
                },
                timeout=20
            )
            if enrich_resp.status_code == 200:
                enrich_data = enrich_resp.json().get("data", [])
                for metric in enrich_data:
                    m_kw = metric.get("keyword", "").lower().strip()
                    if m_kw in master_pool:
                        master_pool[m_kw]["volume"] = metric.get("vol", 0)
                        cpc_val = metric.get("cpc", {}).get("value", "0.00") if isinstance(metric.get("cpc"), dict) else 0.0
                        try:
                            master_pool[m_kw]["cpc"] = float(cpc_val)
                        except (ValueError, TypeError):
                            pass
        except Exception as e:
            console.print(f"[yellow]⚠️ KE Batch Metric Enrichment failed: {e}[/yellow]")

    return master_pool

# -----------------------------------------------------------------------------
# Stage 4: Semantic Entity & Topical Depth Engine
# -----------------------------------------------------------------------------
def mine_semantic_entities(audit_pages: List[Dict[str, Any]], keywords: List[Dict[str, Any]], keyword: str = "") -> Dict[str, List[Tuple[str, int]]]:
    all_headings = []
    for p in audit_pages:
        all_headings.extend(p.get("h1", []) + p.get("h2", []) + p.get("h3", []))

    all_kw_texts = [k["keyword"] for k in keywords if not k.get("is_competitor_brand")]

    # Curated deliverable patterns to extract clean concept nouns
    DELIVERABLE_PATTERNS = [
        (r"\b(paid search|ppc|google ads|adwords)\b", "Paid Search & Google Ads Management"),
        (r"\b(seo|search engine optimi[sz]ation|organic search)\b", "B2B SEO & Organic Search Architecture"),
        (r"\b(cro|conversion rate optimi[sz]ation|conversion optimi[sz]ation)\b", "Conversion Rate Optimization (CRO)"),
        (r"\b(analytics|tracking|attribution|ga4)\b", "Full-Funnel Pipeline Analytics & Attribution"),
        (r"\b(content marketing|content strategy)\b", "Authoritative B2B Content Strategy"),
        (r"\b(audit|discovery sprint)\b", "30-Day Commercial Diagnostic Audit"),
        (r"\b(b2b growth|commercial roadmap|strategy)\b", "B2B Commercial Acquisition Strategy"),
        (r"\b(negative match|search term audit)\b", "Negative Match Governance & Search Term Audits"),
        (r"\b(topical authority|topic clustering)\b", "Semantic Topic Clustering & Entity Authority"),
        (r"\b(fractional cmo|marketing advisory)\b", "Fractional CMO & Strategic Advisory")
    ]

    PERSONA_PATTERNS = [
        (r"\b(b2b|business to business)\b", "B2B Founders & Marketing Leaders"),
        (r"\b(sme|smes|small business)\b", "High-Growth SMEs & Mid-Market Enterprises"),
        (r"\b(enterprise|corporate)\b", "Enterprise Marketing Directors"),
        (r"\b(startup|startups|scaleup|scaleups)\b", "Funded Tech & B2B Startups"),
        (r"\b(founder|managing director|md|cmo)\b", "Founders, MDs & Executive Leadership")
    ]

    CRITERIA_PATTERNS = [
        (r"\b(cost|pricing|rates|hourly|day rate|retainer)\b", "Transparent Retainer & Day Rates"),
        (r"\b(roi|return on investment|pipeline)\b", "Measurable Pipeline ROI & Attribution"),
        (r"\b(results|case stud(y|ies)|portfolio)\b", "Verified Commercial Case Studies"),
        (r"\b(cac|acquisition cost)\b", "Lower Customer Acquisition Costs (CAC)"),
        (r"\b(consultant vs agency|agency vs)\b", "Direct Senior Advisory vs Agency Delegation")
    ]

    deliverables_counter = Counter()
    persona_counter = Counter()
    criteria_counter = Counter()

    corpus_items = [clean_heading_text(h) for h in all_headings if is_topically_relevant(h, keyword) and not is_boilerplate_heading(h)]
    corpus_items.extend(all_kw_texts)

    for item in corpus_items:
        item_lower = item.lower()
        for pat, clean_label in DELIVERABLE_PATTERNS:
            if re.search(pat, item_lower):
                deliverables_counter[clean_label] += 1
        for pat, clean_label in PERSONA_PATTERNS:
            if re.search(pat, item_lower):
                persona_counter[clean_label] += 1
        for pat, clean_label in CRITERIA_PATTERNS:
            if re.search(pat, item_lower):
                criteria_counter[clean_label] += 1

    top_delivs = deliverables_counter.most_common(5)
    if not top_delivs:
        top_delivs = [
            ("B2B Search Acquisition & Commercial Strategy", 1),
            ("30-Day Diagnostic Discovery Sprint", 1)
        ]

    top_personas = persona_counter.most_common(4)
    if not top_personas:
        top_personas = [
            ("High-Growth SMEs & Startups", 1),
            ("B2B Founders & Marketing Directors", 1)
        ]

    top_criteria = criteria_counter.most_common(4)
    if not top_criteria:
        top_criteria = [
            ("Transparent Retainer & Day Rates", 1),
            ("Proven Pipeline ROI & Attribution", 1)
        ]

    return {
        "deliverables": top_delivs,
        "personas": top_personas,
        "criteria": top_criteria
    }

# -----------------------------------------------------------------------------
# Stage 5: Master Synthesis & Markdown Blueprint Generation
# -----------------------------------------------------------------------------
def run_workflow(
    keyword: str,
    geo: str = "UK",
    target_domain: str = None,
    page_type: str = "homepage",
    city: str = None,
    address: str = None,
    postcode: str = None,
    force_refresh: bool = False
):
    # Resolve city context cleanly
    if page_type == "location" and not city:
        city = "Cardiff"
    elif not city:
        for c in CITY_CENTROIDS:
            if re.search(rf"\b{re.escape(c)}\b", keyword, re.IGNORECASE):
                city = c.capitalize()
                break

    location_code, language_code, location_name = load_location(geo)
    client = DataForSEOClient()

    console.print(Panel(
        f"[bold cyan]🎯 Target Keyword:[/bold cyan] '{keyword}'\n"
        f"[bold cyan]📍 Market:[/bold cyan] {location_name} (code: {location_code}) | Lang: {language_code}\n"
        f"[bold cyan]🏢 Target Domain:[/bold cyan] {target_domain or 'General On-Page Blueprint'}\n"
        f"[bold cyan]🛡️ Safety Guardrails:[/bold cyan] Max ${guard.max_budget:.2f} | Max {guard.max_calls} API calls",
        title="🚀 Master Enterprise SEO & AI Overview Workflow",
        border_style="cyan"
    ))

    # 1. SERP & AIO
    console.print("\n[bold yellow]Stage 1: Live SERP & AI Overview Analysis...[/bold yellow]")
    serp_data = fetch_serp_data(client, keyword, location_code, language_code, force_refresh)
    ai_overview = serp_data["ai_overview"]
    paa_questions = serp_data["paa_questions"]
    competitors = serp_data["competitors"]
    console.print(f"  ✓ Found {len(competitors)} organic competitors | {len(paa_questions)} PAA questions")

    # 2. Competitor On-Page Audits
    console.print("\n[bold yellow]Stage 2: Crawling Top Competitor On-Page DOMs...[/bold yellow]")
    audit_data = audit_competitor_pages(client, competitors, limit=3, keyword=keyword, force_refresh=force_refresh)
    benchmarks = audit_data["word_count_benchmarks"]

    # Enforce realistic B2B editorial word count floors
    raw_target = benchmarks.get("target", 1800)
    if page_type == "guide":
        target_words = max(raw_target, 2500)
    elif page_type == "service":
        target_words = max(raw_target, 1800)
    elif page_type == "location":
        target_words = max(raw_target, 1600)
    else:
        target_words = max(raw_target, 1800)
    benchmarks["target"] = target_words

    console.print(f"  ✓ Crawled {len(audit_data['pages'])} competitor pages")
    console.print(f"  ✓ Target Word Count Benchmark: [bold green]{benchmarks['target']:,} words[/bold green] (Avg: {benchmarks['avg']:,})")

    # 3. Multi-Source Keyword Expansion
    top_comp_url = competitors[0]["url"] if competitors else ""
    competitor_domains = [c["domain"] for c in competitors]
    console.print("\n[bold yellow]Stage 3: 4-Way Multi-Source Keyword Expansion...[/bold yellow]")
    keyword_pool = expand_keywords_multisource(
        client, keyword, location_code, language_code, paa_questions, top_comp_url, geo, competitor_domains, force_refresh
    )
    console.print(f"  ✓ Expanded into [bold green]{len(keyword_pool)}[/bold green] unique, deduplicated search queries")

    # 4. Semantic Entity Mining
    console.print("\n[bold yellow]Stage 4: Mining Semantic Entities & Topical Depth...[/bold yellow]")
    entities = mine_semantic_entities(audit_data["pages"], list(keyword_pool.values()), keyword=keyword)
    console.print(f"  ✓ Mined {len(entities['deliverables'])} service deliverables, {len(entities['personas'])} persona segments, {len(entities['criteria'])} decision criteria")

    # 5. Synthesize Client-Ready Deliverable
    console.print("\n[bold yellow]Stage 5: Synthesizing Master On-Page SEO Blueprint...[/bold yellow]")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_slug = "".join([c if c.isalnum() else "_" for c in keyword.lower()]).strip("_")
    report_filename = f"{timestamp}_{clean_slug}_master_blueprint.md"
    report_path = Path(__file__).resolve().parent / "output" / "reports" / report_filename
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(f"# Strategic On-Page SEO & AI Overview Blueprint: {format_keyword_title(keyword)}")
    lines.append(f"\n- **Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- **Target Market:** {location_name} ({language_code})")
    lines.append(f"- **Target URL / Domain:** {target_domain or 'Strategic Blueprint'}")
    lines.append(f"- **Recommended Word Count Target:** **{benchmarks['target']:,} words** (Competitor Avg: {benchmarks['avg']:,} | Min: {benchmarks['min']:,} | Max: {benchmarks['max']:,})")
    lines.append("\n---\n")

    # Section 1: GEO & AI Overview Strategy
    lines.append("## 1. Generative Engine Optimization (GEO) & AI Overviews")
    if ai_overview:
        lines.append("\n> [!IMPORTANT]\n> **Google AI Overview Triggered for this Query.** Content must be engineered to satisfy LLM citation criteria.")
        if ai_overview.get("text"):
            lines.append(f"\n### Existing AI Summary Snapshot:\n_{ai_overview['text'][:450]}..._\n")
        elif ai_overview.get("is_async"):
            lines.append("\n_Note: Google actively triggered an asynchronous AI Overview module on this SERP. Summary text was served via dynamic client-side rendering._\n")

        if ai_overview.get("sources"):
            lines.append("### Cited Sources by Google's LLM:")
            for s in ai_overview["sources"][:6]:
                lines.append(f"- `{s}`")
        lines.append("\n### How to Win AI Overview Citations:")
        lines.append("1. **Direct Definition Answer Block**: Place a 45–55 word direct definition immediately under the primary H1.")
        lines.append("2. **Structured Service Deliverables**: Use concise bulleted lists outlining exact core responsibilities and deliverable milestones.")
        lines.append("3. **Pricing Transparency**: AI models heavily cite pages that provide clear hourly rates, day rates, and retainer brackets.")
    else:
        lines.append("\n> [!NOTE]\n> **No AI Overview currently triggered.** Direct search displays traditional organic links and People Also Ask.")

    # Section 2: Superset Heading Blueprint
    lines.append("\n## 2. On-Page Heading Architecture (Superset Blueprint)")
    lines.append("Synthesized from top-ranking editorial competitors + searcher journey questions to guarantee superior topical coverage:\n")
    
    lines.append("### Mandatory Table-Stakes Headings (Covered by Multiple Competitors)")
    if audit_data["core_headings"]:
        for h in audit_data["core_headings"][:6]:
            lines.append(f"- **H2:** {clean_heading_text(h['original'])}")
    else:
        role = get_service_role_title(keyword, city if page_type == "location" else None)
        article = "an" if role.lower().startswith(('a', 'e', 'i', 'o', 'u')) or role.upper().startswith(('SEO', 'AI')) else "a"
        if page_type == "location":
            if city.lower() in keyword.lower():
                base_kw = re.sub(rf"\b{re.escape(city)}\b", "", keyword, flags=re.IGNORECASE).strip()
                base_title = format_keyword_title(base_kw) if base_kw else format_keyword_title(keyword)
            else:
                base_title = format_keyword_title(keyword)
            lines.append(f"- **H2:** What Does {article} {role} in {city} Do?")
            lines.append(f"- **H2:** Core {base_title} Services & Deliverables in {city}")
            lines.append(f"- **H2:** {format_cost_heading(base_title, city)}")
        elif page_type == "guide":
            formatted_kw = format_keyword_title(keyword)
            lines.append(f"- **H2:** What is {formatted_kw}? Definition & Strategic Scope")
            lines.append(f"- **H2:** Core Pillars & Strategic Frameworks of {formatted_kw}")
            lines.append(f"- **H2:** Step-by-Step Implementation & Execution Roadmap")
            lines.append(f"- **H2:** Measuring Commercial ROI & Pipeline Attribution")
        else:
            formatted_kw = format_keyword_title(keyword)
            lines.append(f"- **H2:** What Does {article} {role} Do?")
            lines.append(f"- **H2:** Core Services & Deliverables Offered")
            lines.append(f"- **H2:** {format_cost_heading(formatted_kw)}")

    lines.append("\n### High-Value Content Gap Gems (To Outrank Competitors)")
    for h in audit_data["unique_headings"][:6]:
        lines.append(f"- **H2 / H3:** {clean_heading_text(h['original'])} *(from {h['competitors'][0]})*")

    lines.append("\n### Searcher Mental Models (Mandatory FAQ Headings from Google PAA)")
    for q in paa_questions[:5]:
        lines.append(f"- **H3 / FAQ:** {q}")

    # Section 3: Semantic Entity Checklist
    lines.append("\n## 3. Semantic Entity & Topical Depth Requirements")
    lines.append("Google's semantic indexing algorithms require natural coverage of these topical entities to establish domain authority:\n")
    
    if entities["deliverables"]:
        lines.append("### Core Service Deliverable Entities:")
        for d, count in entities["deliverables"][:6]:
            lines.append(f"- `[Feature]` **{d}**")

    if entities["personas"]:
        lines.append("\n### Target Client Persona Entities:")
        for p, count in entities["personas"][:5]:
            lines.append(f"- `[Persona]` **{p}**")

    if entities["criteria"]:
        lines.append("\n### Client Decision & Evaluation Triggers:")
        for c, count in entities["criteria"][:5]:
            lines.append(f"- `[Criteria]` **{c}**")

    # Section 4: Multi-Source Keyword Clusters
    lines.append("\n## 4. Multi-Source Keyword Strategy (DataForSEO + Keywords Everywhere)")
    commercial_kws = [k for k in keyword_pool.values() if k.get("intent") == "commercial" and not k.get("is_competitor_brand")]
    informational_kws = [k for k in keyword_pool.values() if k.get("intent") == "informational" and not k.get("is_competitor_brand")]
    brand_kws = [k for k in keyword_pool.values() if k.get("is_competitor_brand")]

    lines.append("\n### High-Intent Commercial Queries (Conversion Anchors)")
    lines.append("| Keyword | Monthly Vol / Traffic | CPC ($) | Source |")
    lines.append("| :--- | :---: | :---: | :--- |")
    sorted_comm = sorted(commercial_kws, key=lambda x: -(x.get("volume") or 0))
    for k in sorted_comm[:10]:
        vol = k.get("volume") or 0
        cpc = k.get("cpc") or 0.0
        vol_str = f"{vol:,}" if vol > 0 else "N/A"
        cpc_str = f"${cpc:.2f}" if cpc > 0 else "-"
        lines.append(f"| **{k['keyword']}** | {vol_str} | {cpc_str} | {k['source']} |")

    lines.append("\n### Top Informational Search Queries (Supporting Topical Depth)")
    lines.append("| Query | Monthly Vol | CPC ($) | Sourced From |")
    lines.append("| :--- | :---: | :---: | :--- |")
    sorted_info = sorted(informational_kws, key=lambda x: -(x.get("volume") or 0))
    for k in sorted_info[:10]:
        vol = k.get("volume") or 0
        cpc = k.get("cpc") or 0.0
        vol_str = f"{vol:,}" if vol > 0 else "Long-Tail (0)"
        cpc_str = f"${cpc:.2f}" if cpc > 0 else "-"
        lines.append(f"| {k['keyword']} | {vol_str} | {cpc_str} | {k['source']} |")

    if brand_kws:
        lines.append("\n### Competitor Brand Share & Mentions (Empirical Intelligence - Do NOT Target in Copy)")
        lines.append("> [!NOTE]\n> These branded search terms represent competitor search share in the target market. Documented for strategic benchmarking only—the copywriter and AI writing agent must NOT target these competitor brand names in page copy or headings.")
        lines.append("| Competitor Query | Monthly Vol | CPC ($) | Sourced From |")
        lines.append("| :--- | :---: | :---: | :--- |")
        sorted_brand = sorted(brand_kws, key=lambda x: -(x.get("volume") or 0))
        for k in sorted_brand[:8]:
            vol = k.get("volume") or 0
            cpc = k.get("cpc") or 0.0
            vol_str = f"{vol:,}" if vol > 0 else "Long-Tail (0)"
            cpc_str = f"${cpc:.2f}" if cpc > 0 else "-"
            lines.append(f"| {k['keyword']} | {vol_str} | {cpc_str} | {k['source']} |")

    # Section 5: Competitor Benchmark Matrix
    lines.append("\n## 5. Live Competitor Benchmark Matrix")
    lines.append("| Rank | Competitor Domain | Word Count | Readability (FK) | Page Title |")
    lines.append("| :---: | :--- | :---: | :---: | :--- |")
    for p in audit_data["pages"]:
        lines.append(f"| #{p['rank']} | **{p['domain']}** | {p['word_count']:,} | {p['readability']:.1f} | {p['title']} |")

    # =========================================================================
    # PART II: TURNKEY COPYWRITER HANDOVER BRIEF (Gaps 4 & 5)
    # =========================================================================
    brief_lines = generate_copywriter_brief(
        keyword=keyword,
        page_type=page_type,
        city=city,
        benchmarks=benchmarks,
        paa_questions=paa_questions,
        entities=entities,
        keyword_pool=keyword_pool,
        geo=geo,
        address=address,
        postcode=postcode
    )
    lines.extend(brief_lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    console.print(Panel(
        f"[bold green]✨ Master Blueprint & Copywriter Brief Generated![/bold green]\n\n"
        f"📄 Saved to: [bold white]{report_path}[/bold white]\n"
        f"🏷️ Page Archetype: [bold cyan]{page_type.upper()}[/bold cyan] ({f'City: {city}' if city else 'National UK'})\n"
        f"{guard.summary()}",
        title="Workflow Execution Complete",
        border_style="green"
    ))

def generate_contextual_faq_answer(
    question: str,
    keyword: str,
    page_type: str = "service",
    city: str = None,
    used_answers: set = None
) -> str:
    """Generate channel-aware, commercially accurate answers for FAQs with zero channel inversion and no duplicate answers."""
    q = question.lower()
    role = get_service_role_title(keyword, city if page_type == "location" else None)
    
    first_role_token = role.strip().split()[0].upper()
    role_article = "an" if first_role_token in {"SEO", "AI", "MBA"} or role.strip()[0].lower() in "aeiou" else "a"
    
    base_kw = re.sub(rf"\b{re.escape(city)}\b", "", keyword, flags=re.IGNORECASE).strip() if city else keyword
    base_title = format_keyword_title(base_kw) if base_kw else format_keyword_title(keyword)
    loc_context = f" in {city} and across South Wales" if city and page_type == "location" else " in the UK"

    # Identify core marketing channel
    k_lower = keyword.lower()
    if any(p in k_lower for p in ["ppc", "google ads", "paid search", "paid media", "adwords"]):
        channel = "ppc"
    elif any(p in k_lower for p in ["seo", "organic search", "search engine"]):
        channel = "seo"
    elif any(p in k_lower for p in ["content marketing", "content strategy", "b2b content"]):
        channel = "content"
    elif any(p in k_lower for p in ["ai", "artificial intelligence"]):
        channel = "ai"
    elif any(p in k_lower for p in ["cro", "conversion rate", "funnel"]):
        channel = "cro"
    else:
        channel = "general"

    ans = None

    if any(w in q for w in ["expect to pay", "pay for", "hourly", "day rate"]):
        ans = (
            f"Senior {base_title} consultants and specialists typically charge day rates between £650 and £1,200. "
            f"For dedicated monthly retainers{loc_context}, businesses can expect to invest £2,500 to £7,500+ per month "
            f"depending on channel scope, account scale, and technical complexity."
        )
    elif any(w in q for w in ["cost in the uk", "typically cost", "average cost", "pricing", "rates", "cost", "how much"]):
        ans = (
            f"Professional B2B {base_title} advisory retainers{loc_context} typically range from £2,500 to £7,500 "
            f"per month based on strategic scope. Comprehensive diagnostic discovery sprints usually "
            f"range between £6,500 and £10,500."
        )
    elif any(w in q for w in ["agency actually do", "agency do", "what does an agency", "what does a"]):
        if channel == "ppc":
            ans = (
                f"A dedicated {base_title} specialist structures high-intent campaigns, conducts search term audits, "
                f"establishes negative match governance, and connects offline CRM conversion tracking to drive qualified sales pipeline."
            )
        elif channel == "seo":
            ans = (
                f"A dedicated {base_title} specialist eliminates technical crawl barriers, builds semantic topic clusters, "
                f"aligns content with generative search algorithms (GEO), and acquires high-authority links to compound organic pipeline."
            )
        elif channel == "ai":
            ans = (
                f"An {base_title} specialist deploys machine intelligence into market research, automated site auditing, "
                f"and CRM attribution modeling while providing senior strategic direction to ensure marketing spend produces measurable pipeline."
            )
        elif channel == "content":
            ans = (
                f"A {base_title} practitioner plans, produces, and distributes authoritative, research-backed educational assets "
                f"engineered to address customer evaluation hurdles and accelerate complex B2B sales cycles."
            )
        else:
            ans = (
                f"A dedicated {base_title} practitioner audits acquisition funnels, eliminates wasted spend, and executes "
                f"90-day sprints across core growth channels to drive predictable B2B revenue."
            )
    elif any(w in q for w in ["difference", "agency vs", "consultant vs", "freelance vs", "in-house vs", "versus"]):
        ans = (
            f"A dedicated senior {role} provides direct strategic steering, custom execution roadmaps, and commercial accountability "
            f"without agency overhead. Traditional agencies often delegate accounts to junior coordinators, whereas a dedicated "
            f"consultant works directly with executive leadership."
        )
    elif any(w in q for w in ["80/20", "pareto", "rule"]):
        ans = (
            f"The 80/20 rule in marketing dictates that roughly 80% of pipeline and revenue originates from 20% of your highest-intent "
            f"campaigns, queries, or assets. Senior strategy focuses aggressively on identifying and scaling that high-leverage 20%."
        )
    elif any(w in q for w in ["who is", "who are"]):
        if channel == "ppc":
            ans = (
                f"A {role} is a specialised digital growth practitioner responsible for structuring, "
                f"executing, and scaling high-intent paid search campaigns to maximise sales pipeline and lower customer acquisition costs."
            )
        elif channel == "seo":
            ans = (
                f"A {role} is a specialised digital growth practitioner responsible for planning, "
                f"executing, and optimizing high-impact organic search and acquisition strategies tailored to commercial business goals."
            )
        elif channel == "ai":
            ans = (
                f"An {role} is a senior marketing strategist who combines machine-assisted analytics, "
                f"automated research, and generative tools with executive decision-making to scale commercial pipeline."
            )
        elif channel == "content":
            ans = (
                f"A {role} is a strategic marketing specialist who designs and distributes authoritative, "
                f"research-backed educational assets engineered to guide decision-makers through complex B2B buying journeys."
            )
        else:
            ans = (
                f"A {role} is a senior commercial growth specialist who audits marketing funnels, "
                f"eliminates wasted spend, and leads 90-day execution sprints to drive qualified B2B pipeline."
            )
    elif any(w in q for w in ["2026", "still worth", "still work", "future", "modern"]):
        ans = (
            f"In 2026, {base_title} is more critical than ever, but the playbook has evolved from vanity volume to commercial intent, "
            f"Generative Engine Optimization (GEO), and first-party data attribution. Companies investing in high-intent search and automated intelligence "
            f"continue to see compounding pipeline advantages."
        )
    elif any(w in q for w in ["in demand", "demand", "job market", "career"]):
        if channel == "ppc":
            ans = (
                f"Demand for experienced {base_title} specialists remains exceptionally high across the UK, as businesses "
                f"increasingly require senior expertise to eliminate ad budget waste and scale paid media profitably."
            )
        else:
            ans = (
                f"Demand for experienced {base_title} specialists remains exceptionally high across the UK, as enterprise brands "
                f"and SMEs prioritize high-efficiency, measurable acquisition channels to navigate competitive markets."
            )
    elif any(w in q for w in ["startup", "small business", "sme"]):
        ans = (
            f"For startups and SMEs, investing early in structured {base_title} ensures technical and commercial foundations "
            f"are built correctly, avoiding wasted spend and establishing predictable customer acquisition early."
        )
    elif any(w in q for w in ["tools", "software", "stack", "technology", "platform"]):
        if channel == "ai":
            ans = (
                f"Leading practitioners employ a modular stack of specialized AI tools for keyword intelligence, automated crawling, "
                f"predictive modeling, and CRM attribution rather than relying on a single monolithic software seat."
            )
        elif channel == "ppc":
            ans = (
                f"Leading {base_title} professionals utilize Google Ads Editor, advanced bidding scripts, offline CRM connectors, "
                f"and search-term intelligence suites to maintain strict account governance."
            )
        elif channel == "seo":
            ans = (
                f"Leading {base_title} professionals utilize Google Search Console, enterprise crawlers, keyword intelligence APIs, "
                f"and log file analysis tools to guide data-driven decisions."
            )
        else:
            ans = (
                f"Leading practitioners utilize industry-standard analytics suites, CRM attribution connectors, and competitive "
                f"intelligence APIs to guide data-driven growth."
            )
    elif any(w in q for w in ["types of", "types in", "forms of", "models of"]):
        ans = (
            f"The primary models of {base_title} include educational thought leadership, technical documentation, "
            f"commercial bottom-of-funnel proof assets, and strategic campaigns designed to guide multi-stakeholder decisions."
        )
    elif any(w in q for w in ["example", "examples", "case studies"]):
        ans = (
            f"High-performing {base_title} examples include proprietary industry benchmark reports, interactive ROI calculators, "
            f"detailed customer transformation tear-downs, and actionable workflow blueprints that solve acute problems for buyers."
        )
    elif any(w in q for w in ["7 p", "4 p", "principles", "framework"]):
        ans = (
            f"In complex B2B environments, traditional marketing principles are adapted to support extended consensus-driven "
            f"sales cycles, technical due diligence, and recurring enterprise lifetime value."
        )
    elif any(w in q for w in ["what does", "what is", "mean", "definition"]):
        if channel == "content":
            ans = (
                f"B2B Content Marketing represents the strategic creation and distribution of high-value, problem-solving material engineered "
                f"to establish domain authority, engage decision-makers, and systematically guide commercial pipeline through complex purchase journeys."
            )
        elif channel == "ai":
            ans = (
                f"AI Digital Marketing Services combine senior marketing strategy with machine-assisted research, predictive analytics, "
                f"and workflow automation to find, qualify, and convert B2B buyers with maximum efficiency."
            )
        elif channel == "ppc":
            ans = (
                f"PPC Management is the strategic creation, governance, and optimization of auction-based paid search and display campaigns "
                f"engineered to capture high-intent commercial demand and generate qualified sales opportunities."
            )
        elif channel == "seo":
            ans = (
                f"B2B SEO is the strategic optimization of technical website architecture, topical authority clusters, and digital brand signals "
                f"to capture compounding organic search demand from enterprise decision-makers."
            )
        else:
            ans = (
                f"{base_title} represents the strategic implementation of commercial marketing initiatives engineered "
                f"to generate qualified pipeline, reduce customer acquisition costs, and drive predictable revenue growth."
            )
    elif any(w in q for w in ["how long", "time", "take", "timeline", "months", "fast"]):
        if channel == "ppc":
            ans = (
                f"Search-term waste reduction and campaign restructuring typically yield lower cost-per-qualified-lead within 30 to 60 days. "
                f"Bid automation fed by offline CRM data reaches optimal efficiency within the first quarter."
            )
        elif channel == "seo":
            ans = (
                f"Initial technical crawl fixes and indexing improvements appear within 4 to 8 weeks. Compounding organic traffic "
                f"and ranking gains on commercial keywords typically mature between months 3 and 6."
            )
        else:
            ans = (
                f"Diagnostic sprint findings and critical fixes surface within 30 days. Fast-cycle paid and conversion improvements "
                f"show measurable impact within 60 days, while compounding strategic initiatives mature over 3 to 6 months."
            )
    elif any(w in q for w in ["worth it", "roi", "value", "good investment"]):
        if channel == "ppc":
            ans = (
                f"Yes. Senior paid search advisory delivers an immediate commercial feedback loop. Reallocating budget away from "
                f"non-converting search terms and aligning bid algorithms with CRM revenue data typically yields significant CAC reductions within 60 to 90 days."
            )
        elif channel == "seo":
            ans = (
                f"Yes. Strategic B2B SEO delivers one of the highest compounding ROIs in marketing because high-intent organic "
                f"search assets continue capturing qualified pipeline indefinitely without recurring per-click media fees."
            )
        elif channel == "ai":
            ans = (
                f"Yes. Applying AI tooling to commercial marketing cuts routine data analysis and keyword clustering time by 60% to 80%, "
                f"freeing budget and senior focus for high-leverage strategic decisions and pipeline acceleration."
            )
        else:
            ans = (
                f"Yes. Engaging senior growth expertise to eliminate funnel leaks and prioritize high-intent acquisition channels "
                f"typically pays for itself within the first two quarters through reduced acquisition costs and faster sales cycles."
            )

    # Fallback pool ensuring distinct, senior answers for every question
    fallback_pool = [
        f"Partnering with a proven {role}{loc_context} provides businesses with senior strategic direction, measurable pipeline visibility, and actionable growth frameworks engineered to drive sustainable revenue growth.",
        f"Engaging senior {base_title} expertise{loc_context} bridges the gap between high-level business goals and technical execution, delivering structured 90-day sprints focused on commercial pipeline.",
        f"Working with a dedicated {role}{loc_context} gives growing businesses direct, senior-level marketing steering without the multi-layered overhead or junior account managers of traditional agencies.",
        f"Investing in strategic {base_title}{loc_context} ensures acquisition funnels and campaigns are rigorously audited, eliminating wasted spend and establishing predictable revenue generation.",
        f"A dedicated {base_title} engagement{loc_context} establishes clear commercial attribution, aligns sales and marketing, and systematically captures high-intent market demand."
    ]

    used = used_answers or set()
    if ans and ans not in used:
        return ans

    # Pick first unused fallback
    for fb in fallback_pool:
        if fb not in used:
            return fb

    # Ultimate fallback if pool exhausted
    return fallback_pool[0]

def generate_copywriter_brief(
    keyword: str,
    page_type: str,
    city: str,
    benchmarks: Dict[str, Any],
    paa_questions: List[str],
    entities: Dict[str, Any],
    keyword_pool: Dict[str, Any],
    geo: str = "UK",
    address: str = None,
    postcode: str = None
) -> List[str]:
    lines = []
    lines.append("\n\n---\n")
    lines.append("# ✍️ PART II: AUTONOMOUS AI COPYWRITER PRODUCTION BRIEF")
    lines.append(
        "\n> [!IMPORTANT]\n"
        "> **AI WRITING AGENT SYSTEM INSTRUCTIONS:**\n"
        "> You are an autonomous Senior B2B Copywriter & Technical SEO Content Specialist. Your objective is to produce publish-ready, authoritative copy for this exact URL based on the specifications, section word budgets, heading hierarchy, and entity requirements detailed below.\n"
        ">\n"
        "> **Execution Directives for the AI Agent:**\n"
        "> 1. Write the FULL text for all sections, adhering strictly to the word allocations.\n"
        "> 2. Implement the exact heading hierarchy (H1, H2, H3) provided without altering tags.\n"
        "> 3. Naturally inject the required semantic entities and secondary keywords into their designated sections.\n"
        "> 4. Strictly obey all negative constraints (ban fluff, ban competitor brands, ban cross-sell dilution, zero passive voice).\n"
        "> 5. Embed the turnkey HTML JSON-LD schema blocks in `<head>` at the conclusion of the output."
    )

    kw_title = format_keyword_title(keyword)
    target_words = benchmarks.get("target", 2100)
    
    # Enforce minimum editorial floors for B2B rigor
    if page_type == "guide":
        target_words = max(target_words, 2500)
    elif page_type == "service":
        target_words = max(target_words, 1800)
    elif page_type == "location":
        target_words = max(target_words, 1600)
    else:
        target_words = max(target_words, 1800)

    city_clean = clean_heading_text(city) if city else ""
    city_in_kw = bool(city and city.lower() in keyword.lower())

    if city_in_kw:
        base_kw = re.sub(rf"\b{re.escape(city)}\b", "", keyword, flags=re.IGNORECASE).strip()
        base_title = format_keyword_title(base_kw) if base_kw else kw_title
    else:
        base_title = kw_title

    role = get_service_role_title(keyword, city if page_type == "location" else None)
    article = "an" if role.lower().startswith(('a', 'e', 'i', 'o', 'u')) or role.upper().startswith(('SEO', 'AI')) else "a"

    # Dynamic metadata depending on archetype
    if page_type == "location":
        if city_in_kw:
            local_anchor_title = f"{base_title} in {city} & South Wales"
            title_tag = f"{kw_title} & South Wales | Senior {role}"
            meta_desc = f"Looking for proven {base_title.lower()} services in {city}? Senior search advisory, technical audits, and high-impact B2B pipeline growth across South Wales. Book a consultation."
            local_faq_h2 = f"Frequently Asked Questions About {base_title} in {city}"
        else:
            local_anchor_title = f"{kw_title} in {city} & South Wales"
            title_tag = f"{kw_title} in {city} & South Wales | Senior B2B Strategy"
            meta_desc = f"Looking for a proven {kw_title.lower()} in {city}? Strategic growth advisory, SEO, PPC audits, and high-impact B2B pipeline generation across South Wales. Book a discovery call."
            local_faq_h2 = f"Frequently Asked Questions About Hiring a {kw_title} in {city}"

        slug = f"/{city_clean.lower()}/"
        archetype_label = f"Location Page ({city} Hub)"
    elif page_type == "service":
        svc_hd = format_service_headline(keyword, city)
        title_tag = svc_hd["title_tag"]
        meta_desc = svc_hd["meta_desc"]
        slug = f"/{clean_heading_text(keyword).lower().replace(' ', '-')}/"
        archetype_label = "Service Money Page"
    elif page_type == "guide":
        title_tag = f"{kw_title}: Strategic Implementation Guide (2026)"
        meta_desc = f"Master {keyword.lower()} with proven strategic frameworks, tactical implementation roadmaps, ROI metrics, and practical execution playbooks."
        slug = f"/guides/{clean_heading_text(keyword).lower().replace(' ', '-')}/"
        archetype_label = "Pillar Guide / Playbook"
    else: # homepage
        title_tag = f"{kw_title} | Senior B2B Growth & Marketing Strategy UK"
        meta_desc = f"Independent {keyword} helping ambitious UK businesses scale revenue. Senior B2B strategy, search acquisition, and pipeline growth without agency fluff."
        slug = "/"
        archetype_label = "Homepage (National UK Authority Hub)"

    lines.append("\n## A. Editorial & Meta Specifications")
    lines.append(f"- **Page Archetype:** **{archetype_label}**")
    lines.append(f"- **Target URL Slug:** `{slug}`")
    lines.append(f"- **Recommended Total Word Count:** **{target_words:,} words (±10%)**")
    lines.append(f"- **Recommended `<title>` Tag:** `{title_tag}` *({len(title_tag)} characters)*")
    lines.append(f"- **Recommended Meta Description:** `{meta_desc}` *({len(meta_desc)} characters)*")
    lines.append(f"- **Target Audience:** B2B Founders, Managing Directors, Heads of Marketing, High-Growth Leadership.")
    lines.append(f"- **Tone of Voice:** Senior, pragmatic, direct, commercially focused. Zero corporate jargon.")

    lines.append("\n## B. Absolute AI Guardrails & Negative Constraints")
    lines.append("- 🚫 **NO CLICHÉ OPENERS:** Never open with *\"In today's fast-paced digital world...\"*, *\"In the modern business landscape...\"*, or *\"Marketing is more important than ever.\"* Open immediately with the commercial stakes, technical friction, or revenue impact.")
    lines.append("- 🚫 **BAN VAGUE FLUFF:** Ban words like *\"synergy\"*, *\"holistic solutions\"*, *\"bespoke marketing\"* (without defining specifics), *\"game-changer\"*, and *\"seamlessly\"*.")
    lines.append("- 🚫 **NO PASSIVE VOICE:** Write in active, direct voice (*\"We audit your acquisition funnel\"* not *\"Audits are performed on funnels\"*).")
    lines.append("- 🚫 **NO COMPETITOR BRAND NAMES:** Strictly do NOT mention or target competitor brand names (e.g. Liberty Marketing, Thomas Design, Thrive Agency, Salesforce, FT) anywhere in headings or copy.")
    lines.append("- 🚫 **NO UNRELATED SERVICE CROSS-SELLS:** Strictly maintain topical purity. Never pitch unrelated service disciplines (e.g. web design, graphic design, branding, hosting, or logo packages) on dedicated PPC or SEO pages.")
    lines.append("- ✅ **CONCRETE EVIDENCE:** Frame every claim around measurable commercial outcomes (*\"90-day execution sprints\"*, *\"pipeline acceleration\"*, *\"CAC reduction\"*).")

    # Build Unified Synchronized FAQ List (ensures 100% parity between on-page copy and JSON-LD schema)
    faq_unified = []
    if not paa_questions:
        if page_type == "location":
            faq_source = [
                f"What does {article} {role} in {city} do?",
                f"How much does {base_title} in {city} cost?",
                f"What is the difference between an independent consultant and an agency?",
                f"How long does it take to see results in {city}?"
            ]
        elif page_type == "guide":
            faq_source = [
                f"What is {base_title}?",
                f"Why is {base_title} critical for B2B companies?",
                f"How do you measure the ROI of {base_title}?",
                f"How long does it take to see results from {base_title}?"
            ]
        else:
            faq_source = [
                f"What does {article} {role} do?",
                f"How much do {base_title} cost?",
                f"What is the difference between a dedicated consultant and a traditional agency?",
                f"How long does it take to see results?"
            ]
    else:
        faq_source = paa_questions[:5]

    seen_q = set()
    deduped_faqs = []
    for q in faq_source:
        q_norm = q.strip().lower()
        if q_norm not in seen_q:
            seen_q.add(q_norm)
            deduped_faqs.append(q.strip())

    used_answers = set()
    for q in deduped_faqs:
        ans = generate_contextual_faq_answer(
            q, keyword, page_type, city if page_type == "location" else None, used_answers=used_answers
        )
        used_answers.add(ans)
        faq_unified.append((q, ans))

    lines.append("\n## C. Section-by-Section Blueprint & Word Budget")

    if page_type == "location":
        b_hero = int(round(target_words * 0.10 / 25.0) * 25)
        b_regional = int(round(target_words * 0.15 / 25.0) * 25)
        b_deliv = int(round(target_words * 0.35 / 25.0) * 25)
        b_cases = int(round(target_words * 0.20 / 25.0) * 25)
        b_faq = int(round(target_words * 0.15 / 25.0) * 25)
        b_cta = target_words - (b_hero + b_regional + b_deliv + b_cases + b_faq)

        lines.append(f"### Section 1: Hero & Local Authority Anchor (Budget: {b_hero} words)\n- **H1:** {local_anchor_title}\n- **Goal:** Establish immediate local credibility and executive presence.\n- **Content Direction:** Emphasize physical presence in {city} while delivering national-calibre B2B marketing strategy. Address the pain of local businesses outgrowing generalist local agencies.")
        lines.append(f"### Section 2: Why Local Businesses in {city} Need Senior Strategy (Budget: {b_regional} words)\n- **H2:** Breaking Past Regional Growth Plateaus\n- **Goal:** Highlight why businesses in South Wales struggle with junior marketing hires or generic retainers.")
        lines.append(f"### Section 3: Core Consultancy Deliverables (Budget: {b_deliv} words)\n- **H2:** Strategic {base_title} & Marketing Consultancy Services in {city}\n- **H3:** B2B Search Engine Optimization (SEO)\n- **H3:** Paid Search & Performance Acquisition (Google Ads)\n- **H3:** Conversion Rate Optimization & Analytics Audits")
        lines.append(f"### Section 4: Local Impact & Welsh Business Case Studies (Budget: {b_cases} words)\n- **H2:** Proven Results for Growing Businesses\n- **Goal:** Reference real Welsh / UK business growth stories, measurable ROI, and pipeline numbers.")
        lines.append(f"### Section 5: Local Engagement FAQs (Budget: {b_faq} words)\n- **H2:** {local_faq_h2}\n- **Mandatory FAQ Accordion & Schema Parity (Exact text required):**")
        for q, ans in faq_unified:
            lines.append(f"- **H3 / FAQ:** {q}\n  - **Target On-Page Answer:** \"{ans}\"")
        lines.append(f"### Section 6: Local Conversion CTA (Budget: {b_cta} words)\n- **H2:** Let's Discuss Your Growth Strategy in {city}\n- **CTA:** Book a 30-minute discovery consultation at our {city} office or via video call.")

    elif page_type == "service":
        svc_hd = format_service_headline(keyword, city)
        b_hero = int(round(target_words * 0.10 / 25.0) * 25)
        b_audit = int(round(target_words * 0.20 / 25.0) * 25)
        b_pillars = int(round(target_words * 0.35 / 25.0) * 25)
        b_rates = int(round(target_words * 0.15 / 25.0) * 25)
        b_faq = int(round(target_words * 0.15 / 25.0) * 25)
        b_cta = target_words - (b_hero + b_audit + b_pillars + b_rates + b_faq)
        b_h3 = int(round(b_pillars / 4.0 / 25.0) * 25)

        lines.append(f"### Section 1: Hero & Strategic Proposition (Budget: {b_hero} words)\n- **H1:** {svc_hd['h1']}\n- **Goal:** Define the exact scope of engagement and expected commercial impact for prospective clients.\n- **Direct Definition Block:** Place a 45–55 word direct definition immediately under the primary H1 for AI Overview / snippet extraction.")
        lines.append(f"### Section 2: The Assessment & Audit Framework (Budget: {b_audit} words)\n- **H2:** What Our Discovery Sprint & Audit Uncovers\n- Breakdown the 30-day discovery sprint: funnel leaks, technical debt, and wasted spend.")
        
        k_lower = keyword.lower()
        if "ppc" in k_lower or "google ads" in k_lower or "paid" in k_lower:
            h3_deliverables = [
                "Paid Search Account Architecture & Negative Match Governance",
                "Conversion Tracking & First-Party Offline Attribution",
                "High-Intent Search & Performance Max Campaign Optimization",
                "Landing Page CRO & Inbound Pipeline Alignment"
            ]
        elif "seo" in k_lower:
            h3_deliverables = [
                "Technical Crawl & Indexation Infrastructure",
                "Semantic Topic Clustering & Entity Authority",
                "Digital PR & High-Authority Backlink Acquisition",
                "Conversion-Focused Content Architecture"
            ]
        else:
            h3_deliverables = [
                "B2B Growth Strategy & Commercial Acquisition Roadmaps",
                "Search Engine Optimization (SEO) & Topical Authority",
                "Paid Acquisition & Google Ads Performance",
                "Conversion Rate Optimization (CRO) & Funnel Analytics"
            ]
        
        lines.append(f"### Section 3: Core Service Pillars & Implementation (Budget: {b_pillars} words)\n- **H2:** Full-Spectrum Strategic Execution\n- Break into specialized H3s:")
        for h3_item in h3_deliverables:
            lines.append(f"  - **H3:** {h3_item} ({b_h3}w)")

        lines.append(f"### Section 4: Engagement Models & Day Rates (Budget: {b_rates} words)\n- **H2:** {format_cost_heading(svc_hd['base_title'], svc_hd['city'])}\n- Outline day rate brackets (£650–£1,200/day) and monthly advisory retainers.")
        lines.append(f"### Section 5: FAQs & Risk Reversal (Budget: {b_faq} words)\n- **H2:** Frequently Asked Questions\n- **Mandatory FAQ Accordion & Schema Parity (Exact text required):**")
        for q, ans in faq_unified:
            lines.append(f"- **H3 / FAQ:** {q}\n  - **Target On-Page Answer:** \"{ans}\"")
        lines.append(f"### Section 6: Consultation CTA (Budget: {b_cta} words)\n- **H2:** Request a Strategic Marketing Audit\n- **CTA:** Schedule an exploratory consultation.")

    elif page_type == "guide":
        b_summary = int(round(target_words * 0.10 / 25.0) * 25)
        b_framework = int(round(target_words * 0.20 / 25.0) * 25)
        b_playbook = int(round(target_words * 0.30 / 25.0) * 25)
        b_pitfalls = int(round(target_words * 0.15 / 25.0) * 25)
        b_roi = int(round(target_words * 0.10 / 25.0) * 25)
        b_faq = int(round(target_words * 0.10 / 25.0) * 25)
        b_cta = target_words - (b_summary + b_framework + b_playbook + b_pitfalls + b_roi + b_faq)

        lines.append(f"### Section 1: Executive Summary & Definition (Budget: {b_summary} words)\n- **H1:** {kw_title}: Strategic Implementation Guide (2026)\n- **Goal:** Direct 45–55 word definition answer block for AI Overview / featured snippet extraction, followed by strategic context and executive target audience.")
        lines.append(f"### Section 2: Core Strategic Framework & Methodology (Budget: {b_framework} words)\n- **H2:** The Core Pillars of a High-Impact {base_title} Strategy\n- Breakdown into actionable components: audience profiling, content architecture, distribution channels, and conversion alignment.")
        lines.append(f"### Section 3: Step-by-Step Execution Playbook (Budget: {b_playbook} words)\n- **H2:** Step-by-Step Implementation Roadmap\n- Practical milestones: technical content audits, entity optimization, editorial calendars, and subject-matter expert interviews.")
        lines.append(f"### Section 4: Critical Pitfalls & Budget Wasters (Budget: {b_pitfalls} words)\n- **H2:** 5 Critical Mistakes That Stall Growth\n- Detail the failure modes: vanity metrics over commercial pipeline, lack of distribution, ignoring search intent depth.")
        lines.append(f"### Section 5: Measuring ROI & Commercial Impact (Budget: {b_roi} words)\n- **H2:** Measuring ROI: Leading vs Lagging Indicators\n- Breakdown pipeline attribution, SQL generation, CAC reduction, and assisted conversions.")
        lines.append(f"### Section 6: Searcher Question Accordion (Budget: {b_faq} words)\n- **H2:** Frequently Asked Questions About {base_title}\n- **Mandatory FAQ Accordion & Schema Parity (Exact text required):**")
        for q, ans in faq_unified:
            lines.append(f"- **H3 / FAQ:** {q}\n  - **Target On-Page Answer:** \"{ans}\"")
        lines.append(f"### Section 7: Strategic Steering & Advisory CTA (Budget: {b_cta} words)\n- **H2:** Need Senior Steering for Your Growth Engine?\n- **CTA:** Book a 30-Minute Strategy Session or request an architectural audit.")

    else: # homepage
        b_hero = int(round(target_words * 0.10 / 25.0) * 25)
        b_problem = int(round(target_words * 0.15 / 25.0) * 25)
        b_capabilities = int(round(target_words * 0.30 / 25.0) * 25)
        b_cases = int(round(target_words * 0.20 / 25.0) * 25)
        b_retainers = int(round(target_words * 0.12 / 25.0) * 25)
        b_faq = int(round(target_words * 0.08 / 25.0) * 25)
        b_cta = target_words - (b_hero + b_problem + b_capabilities + b_cases + b_retainers + b_faq)
        b_h3 = int(round(b_capabilities / 4.0 / 25.0) * 25)

        lines.append(f"### Section 1: Hero & Executive Positioning (Budget: {b_hero} words)\n- **H1:** {kw_title} & Growth Strategy Advisor\n- **Goal:** Clear national positioning: senior commercial direction for ambitious businesses.\n- **Crucial Anchor:** State national reach with clean headquarters trust: *'Partnering with high-growth B2B and enterprise brands across the UK.'*")
        lines.append(f"### Section 2: The Core Problem / Market Reality (Budget: {b_problem} words)\n- **H2:** Why Most Marketing Fails (And Why Retainers Get Wasted)\n- **Goal:** Agitate the pain of disconnected channels, vanity metrics, and junior agency staff.")
        lines.append(f"### Section 3: Strategic Services & Core Deliverables (Budget: {b_capabilities} words)\n- **H2:** Strategic Marketing Consultancy Capabilities\n- Breakdown into high-salience H3s:\n  - **H3:** B2B Marketing Strategy & Growth Roadmaps ({b_h3}w)\n  - **H3:** Search Engine Optimization (SEO) & Topical Authority ({b_h3}w)\n  - **H3:** Paid Acquisition & Google Ads Performance ({b_h3}w)\n  - **H3:** Conversion Rate Optimization (CRO) & Funnel Analytics ({b_h3}w)")
        lines.append(f"### Section 4: Measurable Outcomes & Case Proof (Budget: {b_cases} words)\n- **H2:** Real-World Impact: How We Drive Measurable Growth\n- Showcase verified metrics (+140% Qualified Pipeline, -35% CAC, 4x Organic Revenue).")
        lines.append(f"### Section 5: Transparent Engagement Models (Budget: {b_retainers} words)\n- **H2:** How We Work: Advisory Retainers & Strategic Sprints\n- Explain one-off 30-day diagnostic audits, monthly fractional CMO retainers, and executive coaching.")
        lines.append(f"### Section 6: Searcher Question Accordion (Budget: {b_faq} words)\n- **H2:** Frequently Asked Questions\n- **Mandatory FAQ Accordion & Schema Parity (Exact text required):**")
        for q, ans in faq_unified:
            lines.append(f"- **H3 / FAQ:** {q}\n  - **Target On-Page Answer:** \"{ans}\"")
        lines.append(f"### Section 7: Final Conversion Hook & Action (Budget: {b_cta} words)\n- **H2:** Ready to Scale Your Marketing with Confidence?\n- **CTA:** Book a 30-Minute Growth Strategy Session.")

    lines.append("\n## D. Mandatory Keyword & Entity Injection Checklist")
    lines.append("| Keyword / Entity | Target Density | Mandatory Location |")
    lines.append("| :--- | :---: | :--- |")
    lines.append(f"| **{kw_title}** | 3 - 5x | H1, Intro Paragraph, H2, Body Text |")
    
    # Dynamic deliverables/features from mined entities
    top_delivs = [e[0] for e in entities.get("deliverables", []) if e[0].lower() != keyword.lower()][:2]
    if top_delivs:
        for d in top_delivs:
            lines.append(f"| **{d}** | 3 - 4x | Section 2, Section 3 Capabilities |")
    else:
        lines.append(f"| **B2B Commercial Acquisition Strategy** | 4 - 6x | H2, Section 2, Section 3 |")
        lines.append(f"| **30-Day Commercial Diagnostic Audit** | 3 - 4x | Section 2, Section 3 |")

    # Dynamic personas from mined entities
    top_personas = [p[0] for p in entities.get("personas", []) if p[0].lower() != keyword.lower()][:1]
    if top_personas:
        lines.append(f"| **{top_personas[0]}** | 2 - 3x | Section 1, Section 2 Target Audience |")
    else:
        lines.append(f"| **High-Growth SMEs & Startups** | 2 - 3x | Section 1, Target Audience |")

    # Dynamic decision criteria
    top_crit = [c[0] for c in entities.get("criteria", []) if c[0].lower() != keyword.lower()][:1]
    if top_crit:
        lines.append(f"| **{top_crit[0]}** | 2 - 3x | Section 4, Section 5 ROI Analysis |")
    elif page_type in ["service", "homepage"]:
        lines.append(f"| **Transparent Retainer & Day Rates** | 2 - 3x | Section 4/5 & FAQ Block |")

    if page_type == "location" and city:
        lines.append(f"| **{city} & South Wales** | 4 - 6x | H1, Intro, Local Context, Footer |")
    elif city:
        lines.append(f"| **{city} & UK-wide** | 1 - 2x | Intro anchor & Footer trust badge |")
    else:
        lines.append(f"| **UK-wide / National B2B** | 1 - 2x | Intro context & strategic examples |")

    lines.append("\n## E. Technical Internal Linking Architecture")
    lines.append("Strategic internal link flows establish topic cluster hierarchy, pass PageRank, and prevent doorway page penalties:\n")
    
    if page_type == "homepage":
        lines.append("### Outbound Links from Homepage (Authority Passing)")
        lines.append("| Target Destination | Anchor Text Strategy | Context / Section |")
        lines.append("| :--- | :--- | :--- |")
        if city_clean:
            lines.append(f"| `/{city_clean.lower()}/` | *\"{city} Digital Marketing Consultancy\"* or *\"{city} & Regional Advisory\"* | Section 1 (Hero intro) or Section 5 (Regional Presence) |")
        lines.append("| `/services/b2b-seo-consultancy/` | *\"B2B SEO Strategy & Topical Authority\"* | Section 3 (Capabilities) |")
        lines.append("| `/services/ppc-performance-marketing/` | *\"Paid Media & Google Ads Acquisition\"* | Section 3 (Capabilities) |")
        lines.append("| `/services/cro-funnel-analytics/` | *\"Conversion Rate Optimization & Funnel Audits\"* | Section 3 (Capabilities) |")
        lines.append("| `/case-studies/` | *\"verified client growth case studies\"* | Section 4 (Case Proof) |")
        lines.append("| `/contact/` | *\"Book a 30-Minute Growth Strategy Session\"* | Hero CTA & Section 7 Footer CTA |")

        lines.append("\n### Inbound Link Directives (Pages that must point back to `/`)")
        if city_clean:
            lines.append(f"- **From `/{city_clean.lower()}/`:** Header breadcrumb *Home* and editorial anchor: *\"national B2B marketing consultancy\"*.")
        lines.append("- **From All Service Pages:** Breadcrumb root and inline references to *\"James Watkins Strategic Advisory\"*.")

    elif page_type == "location":
        lines.append(f"### Outbound Links from {city} Location Hub")
        lines.append("| Target Destination | Anchor Text Strategy | Context / Section |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| `/` | *\"national digital marketing consultancy\"* or *\"senior B2B marketing advisor\"* | Section 1 (Hero anchor) & Section 4 |")
        lines.append(f"| `/services/b2b-seo-consultancy/` | *\"SEO consultancy services\"* | Section 3 (Deliverables) |")
        lines.append(f"| `/services/ppc-performance-marketing/` | *\"paid media and Google Ads management\"* | Section 3 (Deliverables) |")
        lines.append(f"| `/case-studies/` | *\"explore our Welsh & UK client case studies\"* | Section 4 (Case Studies) |")
        lines.append(f"| `/contact/` | *\"Schedule a discovery session in {city}\"* | Section 6 (Local CTA) |")

        lines.append(f"\n### Inbound Link Directives (Pages that must point to `/{city_clean.lower()}/`)")
        lines.append(f"- **From Homepage (`/`):** Footer regional office list and Hero trust note: *\"Visit our [{city} Marketing Consultant](/{city_clean.lower()}/) hub for South Wales engagements.\"*")
        lines.append(f"- **From Google Business Profile:** Primary website link or location appointment link pointing directly to `https://jameswatkins.co.uk/{city_clean.lower()}/`.")

    elif page_type == "service":
        lines.append("### Outbound Links from Service Page")
        lines.append("| Target Destination | Anchor Text Strategy | Context / Section |")
        lines.append("| :--- | :--- | :--- |")
        lines.append("| `/` | *\"senior marketing consultancy\"* | Hero intro breadcrumb & Section 1 |")
        if city_clean:
            lines.append(f"| `/{city_clean.lower()}/` | *\"{city} & Regional office\"* | Contact & consultation block |")
        lines.append("| `/case-studies/` | *\"relevant B2B campaign results\"* | Case study proof block |")
        lines.append("| `/contact/` | *\"Request a 30-day marketing audit\"* | Primary CTA |")

    elif page_type == "guide":
        lines.append("### Outbound Links from Guide / Pillar Article")
        lines.append("| Target Destination | Anchor Text Strategy | Context / Section |")
        lines.append("| :--- | :--- | :--- |")
        lines.append("| `/` | *\"senior marketing consultancy\"* or *\"James Watkins Strategic Advisory\"* | Author bio & executive summary |")
        lines.append("| `/services/b2b-seo-consultancy/` | *\"B2B SEO strategy & technical audits\"* | Section 2 / Section 3 Execution |")
        lines.append("| `/case-studies/` | *\"explore our B2B client case studies\"* | Section 5 (ROI Proof) |")
        lines.append("| `/contact/` | *\"request a comprehensive marketing audit\"* | Section 7 (Final CTA) |")

        lines.append(f"\n### Inbound Link Directives (Pages that must point to `{slug}`)")
        lines.append(f"- **From Knowledge Hub (`/guides/`):** Primary pillar card featuring `{title_tag}`.")
        lines.append("- **From Core Service Pages:** Contextual in-content reference in 'Deep Dive Guides & Frameworks'.")
        lines.append("- **From Homepage (`/`):** Featured resource link in 'Latest Strategic Insights & Research'.")

    # Section F: Technical JSON-LD Schema Markup
    lines.append("\n## F. Turnkey Technical JSON-LD Schema Markup")
    lines.append("Paste this valid JSON-LD directly into the `<head>` of this page to secure rich snippet eligibility and entity graph disambiguation:\n")
    
    # 1. Main Business / Service Schema
    if page_type == "location":
        city_key = city.lower()
        centroid = CITY_CENTROIDS.get(city_key, {"lat": 51.4816, "lng": -3.1791, "region": "South Wales"})
        is_cardiff = city_key == "cardiff"
        region_name = centroid.get("region", "South Wales" if geo.upper() == "UK" else city)

        if address and postcode:
            postal_address = {
                "@type": "PostalAddress",
                "streetAddress": address,
                "addressLocality": city,
                "addressRegion": region_name,
                "postalCode": postcode,
                "addressCountry": "GB" if geo.upper() == "UK" else geo
            }
        elif is_cardiff:
            postal_address = {
                "@type": "PostalAddress",
                "streetAddress": "Brunel House, 2 Fitzalan Rd",
                "addressLocality": "Cardiff",
                "addressRegion": "South Glamorgan",
                "postalCode": "CF24 0EB",
                "addressCountry": "GB"
            }
        else:
            postal_address = {
                "@type": "PostalAddress",
                "addressLocality": city,
                "addressRegion": region_name,
                "addressCountry": "GB" if geo.upper() == "UK" else geo
            }

        schema_business = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"James Watkins - {role} {city}",
            "description": meta_desc,
            "url": f"https://jameswatkins.co.uk/{city_clean.lower()}/",
            "telephone": "+44-29-2000-0000",
            "priceRange": "£££",
            "address": postal_address,
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": centroid["lat"],
                "longitude": centroid["lng"]
            },
            "areaServed": [
                {"@type": "City", "name": city},
                {"@type": "AdministrativeArea", "name": region_name},
                {"@type": "Country", "name": "United Kingdom" if geo.upper() == "UK" else geo}
            ],
            "makesOffer": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"B2B {base_title} Strategy {city}"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "PPC & Performance Acquisition"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Conversion Rate Optimization"}}
            ]
        }
    elif page_type == "guide":
        schema_business = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title_tag,
            "description": meta_desc,
            "url": f"https://jameswatkins.co.uk{slug}",
            "inLanguage": "en-GB",
            "author": {
                "@type": "Person",
                "name": "James Watkins",
                "jobTitle": "Senior Marketing Strategist & B2B Consultant",
                "url": "https://jameswatkins.co.uk/about/"
            },
            "publisher": {
                "@type": "Organization",
                "name": "James Watkins Consultancy",
                "url": "https://jameswatkins.co.uk/",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://jameswatkins.co.uk/assets/logo.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"https://jameswatkins.co.uk{slug}"
            }
        }
    else:
        addr_block = {
            "@type": "PostalAddress",
            "addressCountry": "GB"
        }
        if city:
            addr_block["addressLocality"] = city.capitalize()
            centroid = CITY_CENTROIDS.get(city.lower(), {})
            if centroid.get("region"):
                addr_block["addressRegion"] = centroid["region"]

        schema_business = {
            "@context": "https://schema.org",
            "@type": "ProfessionalService",
            "name": "James Watkins - Strategic Digital Marketing Consultant",
            "description": meta_desc,
            "url": "https://jameswatkins.co.uk/",
            "priceRange": "£££",
            "address": addr_block,
            "areaServed": {
                "@type": "Country",
                "name": "United Kingdom"
            },
            "founder": {
                "@type": "Person",
                "name": "James Watkins",
                "jobTitle": "Senior Marketing Strategist & B2B Consultant",
                "url": "https://jameswatkins.co.uk/about/"
            },
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "Consulting Services",
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "B2B SEO & Search Advisory"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Paid Acquisition & Google Ads Management"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Fractional CMO & Marketing Strategy Audits"}}
                ]
            }
        }

    # 2. Synchronized FAQPage Schema (Exact Match to On-Page Text)
    faq_schema_items = []
    for q, ans in faq_unified:
        faq_schema_items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": ans
            }
        })

    schema_faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_schema_items
    }

    lines.append("```html")
    lines.append("<!-- Primary Entity Schema -->")
    lines.append("<script type=\"application/ld+json\">")
    lines.append(json.dumps(schema_business, indent=2))
    lines.append("</script>")
    lines.append("\n<!-- FAQ Accordion Schema -->")
    lines.append("<script type=\"application/ld+json\">")
    lines.append(json.dumps(schema_faq, indent=2))
    lines.append("</script>")
    lines.append("```")

    return lines

def main():
    parser = argparse.ArgumentParser(description="Run enterprise end-to-end SEO & AI Overview workflow.")
    parser.add_argument("keyword", nargs="?", default="digital marketing consultant", help="Target keyword")
    parser.add_argument("--geo", default="UK", choices=["UK", "US", "CA", "AU"], help="Target country code")
    parser.add_argument("--domain", default=None, help="Target website domain")
    parser.add_argument("--page-type", default="homepage", choices=["homepage", "location", "service", "guide"], help="Target page archetype")
    parser.add_argument("--city", default=None, help="Target city for location pages or local anchors")
    parser.add_argument("--address", default=None, help="Optional physical street address for LocalBusiness schema")
    parser.add_argument("--postcode", default=None, help="Optional postal code for LocalBusiness schema")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass cache")
    args = parser.parse_args()

    run_workflow(
        keyword=args.keyword,
        geo=args.geo,
        target_domain=args.domain,
        page_type=args.page_type,
        city=args.city,
        address=args.address,
        postcode=args.postcode,
        force_refresh=args.force_refresh
    )

if __name__ == "__main__":
    main()
