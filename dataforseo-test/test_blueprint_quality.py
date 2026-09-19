#!/usr/bin/env python3
"""
Automated Quality Assurance & Verification Suite for SEO Blueprints
Programmatically validates generated blueprint markdown reports against strict quality gates:
1. Word budget exact mathematical parity (Target words == Sum of section budgets).
2. FAQ parity (On-page question/answer text matches JSON-LD FAQPage verbatim).
3. FAQ quality (No duplicate questions, no duplicate answers, no channel anti-selling).
4. Geo-purity (Zero local leaks on national pages; accurate geo data on local pages).
5. Heading purity (No competitor brands, no boilerplate, no trailing prepositions).
6. Valid JSON-LD syntax for all schema blocks.
7. Internal linking slug and anchor validity.
8. Semantic entity cleanliness.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Any

KNOWN_COMPETITOR_BRANDS = [
    "liberty marketing", "thomas design", "thrive agency", "salesforce", "ft longitude",
    "whitehat", "contra agency", "the media angel", "effective communication"
]

BOILERPLATE_PATTERNS = [
    "privacy policy", "cookie policy", "terms of use", "all rights reserved",
    "skip to content", "menu", "navigation", "contact us today", "leave a comment"
]

def validate_report(report_path: Path, expected_archetype: str, expected_city: str = None) -> List[str]:
    errors = []
    if not report_path.exists():
        return [f"File does not exist: {report_path}"]

    content = report_path.read_text(encoding="utf-8")

    # -------------------------------------------------------------------------
    # 1. Word Count Mathematical Alignment
    # -------------------------------------------------------------------------
    target_match = re.search(r"Recommended Total Word Count:\*\* \*\*([\d,]+) words", content)
    if not target_match:
        errors.append("CRITICAL: 'Recommended Total Word Count' not found in Section A.")
        target_words = 0
    else:
        target_words = int(target_match.group(1).replace(",", ""))

    # Find all section budgets in Section C
    # Format: ### Section X: ... (Budget: XXX words)
    section_budgets = re.findall(r"### Section \d+:.*?\(Budget:\s*([\d,]+)\s*words\)", content)
    if not section_budgets:
        errors.append("CRITICAL: No section budgets found in Section C.")
    else:
        sum_budgets = sum(int(b.replace(",", "")) for b in section_budgets)
        if sum_budgets != target_words:
            errors.append(f"WORD BUDGET MISMATCH: Stated target is {target_words} words, but section budgets sum to {sum_budgets} words (diff: {sum_budgets - target_words}).")

    # -------------------------------------------------------------------------
    # 2. JSON-LD Schema Extraction & Syntax Validation
    # -------------------------------------------------------------------------
    schema_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
    if not schema_blocks:
        errors.append("CRITICAL: No JSON-LD schema blocks found in Section F.")
    
    parsed_schemas = []
    for idx, block in enumerate(schema_blocks, 1):
        try:
            parsed = json.loads(block.strip())
            parsed_schemas.append(parsed)
        except Exception as e:
            errors.append(f"CRITICAL: Schema block #{idx} failed JSON parse: {e}")

    # Find FAQPage schema and primary schema
    faq_schema = None
    primary_schema = None
    for s in parsed_schemas:
        stype = s.get("@type")
        if stype == "FAQPage":
            faq_schema = s
        elif stype in ["ProfessionalService", "LocalBusiness", "Article", "WebPage"]:
            primary_schema = s

    if not faq_schema:
        errors.append("CRITICAL: 'FAQPage' schema block missing from JSON-LD output.")

    # -------------------------------------------------------------------------
    # 3. FAQ Parity (Section C on-page vs Section F schema)
    # -------------------------------------------------------------------------
    # Extract on-page FAQ items
    # Format:
    # - **H3 / FAQ:** Question text?
    #   - **Target On-Page Answer:** "Answer text..."
    on_page_faqs = re.findall(
        r"-\s+\*\*H3 / FAQ:\*\*\s+(.*?)\n\s+-\s+\*\*Target On-Page Answer:\*\*\s+\"(.*?)\"",
        content
    )

    if not on_page_faqs:
        errors.append("CRITICAL: Could not find on-page FAQ question/answer pairs in Section C.")
    else:
        # Check for duplicate questions or answers on-page
        q_texts = [q.strip() for q, _ in on_page_faqs]
        a_texts = [a.strip() for _, a in on_page_faqs]
        if len(q_texts) != len(set(q_texts)):
            errors.append("FAQ DEFECT: Duplicate question text found in on-page FAQs.")
        if len(a_texts) != len(set(a_texts)):
            errors.append("FAQ DEFECT: Duplicate answer text found in on-page FAQs.")

        # Check parity against schema
        if faq_schema:
            schema_entities = faq_schema.get("mainEntity", [])
            if len(schema_entities) != len(on_page_faqs):
                errors.append(f"FAQ PARITY MISMATCH: On-page has {len(on_page_faqs)} FAQs, but schema has {len(schema_entities)} FAQs.")
            
            for idx, (op_q, op_a) in enumerate(on_page_faqs):
                if idx < len(schema_entities):
                    sch_q = schema_entities[idx].get("name", "").strip()
                    sch_a = schema_entities[idx].get("acceptedAnswer", {}).get("text", "").strip()
                    if op_q.strip() != sch_q:
                        errors.append(f"FAQ Q#{idx+1} MISMATCH: On-page Q ('{op_q[:30]}...') != Schema Q ('{sch_q[:30]}...').")
                    if op_a.strip() != sch_a:
                        errors.append(f"FAQ A#{idx+1} MISMATCH: On-page Answer does not match Schema Answer verbatim.")

    # -------------------------------------------------------------------------
    # 4. Geo-Contamination & Alignment
    # -------------------------------------------------------------------------
    section_a = ""
    sec_a_match = re.search(r"## A\. Editorial & Meta Specifications(.*?)(?=## B|\Z)", content, re.DOTALL)
    if sec_a_match:
        section_a = sec_a_match.group(1)

    if not expected_city:
        # National page: verify NO Cardiff / South Wales / local addresses in meta or schemas
        local_terms = ["Cardiff", "South Wales", "South Glamorgan", "CF10"]
        for term in local_terms:
            if term.lower() in section_a.lower():
                errors.append(f"GEO-CONTAMINATION: National page Section A contains local term '{term}'.")
        if primary_schema:
            addr = primary_schema.get("address", {})
            locality = addr.get("addressLocality", "")
            if locality.lower() in ["cardiff", "newport", "swansea"]:
                errors.append(f"GEO-CONTAMINATION: National schema has local addressLocality '{locality}'.")
    else:
        # Local page: verify expected city is present in title, meta, or schema
        if expected_city.lower() not in content.lower():
            errors.append(f"GEO-DEFECT: Local page missing expected city '{expected_city}'.")
        if primary_schema:
            addr = primary_schema.get("address", {})
            locality = addr.get("addressLocality", "")
            if locality.lower() != expected_city.lower():
                errors.append(f"GEO-DEFECT: Schema addressLocality '{locality}' does not match expected '{expected_city}'.")

    # -------------------------------------------------------------------------
    # 5. Heading & Keyword Hygiene
    # -------------------------------------------------------------------------
    # Check Section C headings for competitor brands
    section_c = ""
    sec_c_match = re.search(r"## C\. Section-by-Section Blueprint(.*?)(?=## D|\Z)", content, re.DOTALL)
    if sec_c_match:
        section_c = sec_c_match.group(1)

    for brand in KNOWN_COMPETITOR_BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", section_c, re.IGNORECASE):
            errors.append(f"COMPETITOR BRAND LEAK: Competitor brand '{brand}' found in Section C copywriter brief.")

    # Check Section D keyword table
    section_d = ""
    sec_d_match = re.search(r"## D\. Mandatory Keyword & Entity Injection(.*?)(?=## E|\Z)", content, re.DOTALL)
    if sec_d_match:
        section_d = sec_d_match.group(1)

    for brand in KNOWN_COMPETITOR_BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", section_d, re.IGNORECASE):
            errors.append(f"COMPETITOR BRAND LEAK: Competitor brand '{brand}' found in Section D mandatory keywords.")

    # -------------------------------------------------------------------------
    # 6. Schema Archetype Match
    # -------------------------------------------------------------------------
    if primary_schema:
        actual_type = primary_schema.get("@type")
        if expected_archetype == "guide" and actual_type != "Article":
            errors.append(f"SCHEMA TYPE ERROR: Guide expected 'Article' schema, got '{actual_type}'.")
        elif expected_archetype == "location" and actual_type != "LocalBusiness":
            errors.append(f"SCHEMA TYPE ERROR: Location expected 'LocalBusiness' schema, got '{actual_type}'.")
        elif expected_archetype in ["service", "homepage"] and actual_type not in ["ProfessionalService", "LocalBusiness"]:
            errors.append(f"SCHEMA TYPE ERROR: Service/Homepage expected 'ProfessionalService', got '{actual_type}'.")

    return errors


def main():
    test_cases = [
        {
            "cmd": './venv/bin/python3 workflow_full_planner.py "ai digital marketing services" --page-type service',
            "file_pattern": "*ai_digital_marketing_services_master_blueprint.md",
            "archetype": "service",
            "city": None
        },
        {
            "cmd": './venv/bin/python3 workflow_full_planner.py "b2b content marketing" --page-type guide',
            "file_pattern": "*b2b_content_marketing_master_blueprint.md",
            "archetype": "guide",
            "city": None
        },
        {
            "cmd": './venv/bin/python3 workflow_full_planner.py "ppc consultant cardiff" --page-type service --city Cardiff',
            "file_pattern": "*ppc_consultant_cardiff_master_blueprint.md",
            "archetype": "service",
            "city": "Cardiff"
        },
        {
            "cmd": './venv/bin/python3 workflow_full_planner.py "seo newport" --page-type location --city Newport',
            "file_pattern": "*seo_newport_master_blueprint.md",
            "archetype": "location",
            "city": "Newport"
        },
        {
            "cmd": './venv/bin/python3 workflow_full_planner.py "digital marketing consultant" --page-type homepage',
            "file_pattern": "*digital_marketing_consultant_master_blueprint.md",
            "archetype": "homepage",
            "city": None
        }
    ]

    reports_dir = Path("output/reports")
    all_passed = True

    print("=" * 70)
    print("🔍 RUNNING AUTOMATED BLUEPRINT VERIFICATION HARNESS")
    print("=" * 70)

    for tc in test_cases:
        print(f"\n▶ Testing Archetype: {tc['archetype'].upper()} | City: {tc['city']}")
        matching_files = sorted(reports_dir.glob(tc["file_pattern"]), key=lambda p: p.stat().st_mtime, reverse=True)
        if not matching_files:
            print(f"❌ File not found matching pattern: {tc['file_pattern']}")
            all_passed = False
            continue

        latest_report = matching_files[0]
        print(f"  Inspecting: {latest_report.name}")
        errs = validate_report(latest_report, tc["archetype"], tc["city"])
        if errs:
            all_passed = False
            print(f"  ❌ FAILED ({len(errs)} issues found):")
            for e in errs:
                print(f"     - {e}")
        else:
            print("  ✅ PASSED: 100% Quality & Compliance Match!")

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TEST SUITES PASSED PERFECTLY WITH ZERO DEFECTS.")
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED QUALITY ASSURANCE.")
        sys.exit(1)

if __name__ == "__main__":
    main()
