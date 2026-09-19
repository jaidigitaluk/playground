# Implementation & Test Ledger: `dataforseo-test`

## Objective
Build and verify a resilient, cost-controlled, client-ready workflow engine for DataForSEO v3:
1. Fix payload array gotchas, timeout issues, and embedded error status codes.
2. Integrate AI Overview (AIO) source extraction and Generative Engine Optimization (GEO).
3. Automate keyword clustering by search intent.
4. Synthesize client-facing On-Page SEO blueprints.

---

## 📋 Progress & Checklist

- [x] **Phase 1: Project Scaffolding & Safeguards**
  - [x] Clear taxonomy: `_system/` plumbing vs root working files (`01_...`, `02_...`).
  - [x] Bulletproof `.gitignore` and `git_guard.py` secret scanner.
  - [x] 24-hour local disk cache layer (`_system/cache.py`).
  - [x] Budget & runaway agent guardrails (`_system/guardrails.py`).
  - [x] Config catalogs (`endpoints_catalog.json`, `locations.json`, `field_filters.json`).
  - [x] Core resilient API client (`_system/client.py`).
  - [x] Virtual environment setup & dependency installation.

- [x] **Phase 2: Authentication & Healthcheck**
  - [x] Add real credentials to `.env`.
  - [x] Run `01_verify_auth.py` and confirm account balance retrieval ($50.73 verified).

- [x] **Phase 3: Working File Validation**
  - [x] Run `02_test_aio_serp.py` with sample query ("best crm software") to test AI Overview parser.
  - [x] Run `03_keyword_clustering.py` to test intent classification.
  - [x] Verify caching works (second run costs $0.00).

- [x] **Phase 4: Full Workflow & Deliverable Generation**
  - [x] Run `workflow_full_planner.py` to produce a complete markdown blueprint in `output/reports/`.
  - [x] Inspect report formatting and confirm client-readiness.

- [x] **Phase 4.5: Tightening the Engine (Closing the 3 Architectural Gaps)**
  - [x] **Gap 1: Competitor On-Page Extraction** — Extract word count, H1-H4 heading hierarchy, and schema markup from top-ranking organic & AIO cited URLs (`04_competitor_onpage.py`).
  - [x] **Gap 2: Multi-Source Keyword Expansion** — Aggregate seed suggestions, related searches, and PAA query strings into a unified candidate pool (`05_multisource_keyword_expansion.py`).
  - [x] **Gap 3: Entity & Semantic Intent Depth** — Identify key topical entities and secondary intents to eliminate intent mismatch (`06_entity_semantic_clustering.py`).

- [x] **Phase 4.6: The Production & Content Handover System (Gaps 4 - 7 - Fully Implemented)**
  - [x] **Gap 4: Page Archetype Engine** — Support `--page-type [homepage|location|service|guide]` so the blueprint adapts its structure dynamically.
  - [x] **Gap 5: Turnkey Copywriter Handover Brief** — Deliver section-by-section word count allocations, H2/H3 specs, negative constraints, and meta title/descriptions.
  - [x] **Gap 6: Technical JSON-LD Schema & Linking Architecture** — Auto-generate valid `ProfessionalService` / `LocalBusiness` + `FAQPage` schema code, plus explicit internal linking instructions.
  - [x] **Gap 7: Batch Keyword Metric Enrichment** — Enrich all PAA questions and PASF lateral queries with real search volume and CPC via Keywords Everywhere batch lookup (`get_keyword_data`).

- [x] **Phase 4.7: Additional Edge Validation**
  - [x] Local Term: `"SEO Newport"` (Dedicated Location Page - Newport, South Wales). Verified end-to-end; deliverable generated at `output/reports/20260917_202601_seo_newport_master_blueprint.md`.
  - [x] Fixed `.env` credential defect (`LOGIN ` suffix stripped from `DATAFORSEO_PASSWORD`).

- [x] **Phase 4.8: Polish & Defect Remediation (Completed & Verified)**
  - [x] **Bug 1: Title & Meta Tag Deduplication**: Smarter title and meta description synthesis detecting if `{city}` is already present in `{keyword}`, deriving natural base titles and roles (e.g. `SEO Newport & South Wales | Senior SEO Specialist` and `SEO in Newport & South Wales`).
  - [x] **Bug 2: Dynamic Local Business Schema Address**: Cleanly populates city/region from `CITY_CENTROIDS` without hardcoding Cardiff Brunel House into non-Cardiff pages; preserves accurate GPS coordinates and supports optional `--address` and `--postcode`.
  - [x] **Bug 3: Scraped Heading Sanitization**: Multi-pass cleaning stripping bullet symbols (`•`, `▪`, `▫`), trailing punctuation, dangling prepositions (`For`, `With`, `In`), and converting uppercase shouting to clean Title Case. Filters competitor FAQ wrappers from editorial headings.
  - [x] **Bug 4: US Geo-Disambiguation Filter**: Boundary-aware regex filtering foreign / cross-Atlantic counterparts (e.g. Newport Beach, CA, Newport, RI) when executing UK geo queries.
  - [x] **Bug 5: Contextual FAQ Schema Answers**: Unique, commercially authoritative draft answers generated for each FAQ question matching user intent (rates/pricing, agency deliverables, 80/20 rule, ROI, timelines).
  - [x] Re-run `"SEO Newport"` validation and confirmed all 5 defects are resolved (`output/reports/20260918_003323_seo_newport_master_blueprint.md`).

- [x] **Phase 4.9: Fresh-Session Hardening & Autonomous AI Copywriter Brief (Completed & Verified)**
  - [x] **Auto-Venv Execution**: System python (`/usr/bin/python3`) auto-reexecutes local `./venv/bin/python3`, eliminating `ModuleNotFoundError: No module named 'dotenv'` in clean sessions.
  - [x] **Keywords Everywhere UK Code Fix**: Hardened ISO code to `"uk"` (passing `"gb"` caused KE to silently return global metrics).
  - [x] **Environment Override**: Configured `load_dotenv(override=True)` to prevent stale exported shell variables from polluting API credentials.
  - [x] **Asynchronous AI Overview Handling**: Defensively parses `asynchronous_ai_overview: True` without throwing `TypeError: 'NoneType' object is not iterable`.
  - [x] **Niche Query Relaxation**: Automatic relaxation fallback for 3+ word queries with zero direct suggestions in Labs / PASF.
  - [x] **Dedicated Pillar Guide Archetype**: Custom 7-section pedagogical guide blueprint, knowledge hub internal links, and `Article` JSON-LD schema.
  - [x] **Two-Tier Architecture (Data Warehouse vs AI Copywriter Brief)**:
    - Part I: Strategic Data & Competitive Intelligence (SERP features, competitor benchmarks, full keyword tables, competitor brand share).
    - Part II: Autonomous AI Copywriter Production Brief (Zero-noise system prompt, strict word budgets, verified headings, and negative constraints).
  - [x] **Topical Cross-Sell Pruning**: `CROSS_SELL_PATTERNS` eliminates off-topic services (e.g. web design £599 on PPC pages).
  - [x] **EMD-Aware Competitor Brand Segregation**: Disables keyword pollution by moving agency brands (`Liberty Marketing`, `Thomas Design`, etc.) into an intelligence table.
  - [x] **Preposition & Syntax Smoothing**: Natural English formatting (`format_cost_heading`, `format_service_headline`) ensuring H1s and H2s read with proper prepositions.
  - [x] Verified on `"ppc consultant cardiff"` (`output/reports/20260918_005415_ppc_consultant_cardiff_master_blueprint.md`) and `"b2b content marketing"` (`output/reports/20260918_005426_b2b_content_marketing_master_blueprint.md`).
  - [x] Verified on `"ai digital marketing services"` (`output/reports/20260918_005846_ai_digital_marketing_services_master_blueprint.md`): National UK Service Archetype test. Confirmed AI Overview trigger, extracted 4 PAA journey questions, scraped ranking competitors (`aidigital.com`, `aimarketingservices.com`), generated 634-word target benchmark, mapped commercial demand to agency terms (`ai marketing agency` 480/mo £4.43 CPC, `ai seo services` 390/mo £7.14 CPC, `ai digital marketing` 390/mo £4.05 CPC).

- [x] **Phase 4.10: Automated Quality Assurance & Defect Remediation (Completed & Verified)**
  - [x] **Automated QA Verification Harness (`test_blueprint_quality.py`)**: Programmatic validation of word budget exact mathematical parity, JSON-LD syntax, 100% FAQ on-page vs schema text parity, zero duplicate questions or answers, geo-contamination prevention, and competitor brand exclusion.
  - [x] **Mathematical Word Budget Alignment**: Eliminated thin landing page contradiction (`avg * 1.1` vs fixed budgets) by introducing minimum B2B floors (Guide: 2,500w, Service/Homepage: 1,800w, Location: 1,600w) and dynamically proportioning section allocations to sum to exactly 100% of target.
  - [x] **100% FAQ Parity & Deduplication**: Unified `faq_unified` pipeline ensuring visible on-page text and JSON-LD `FAQPage` schema match character-for-character with zero duplicate answers across all questions (backed by a 5-tier fallback pool and year/2026 intent triggers).
  - [x] **National Geo-Contamination Elimination**: Removed CLI default `--city Cardiff`. National service, guide, and homepage archetypes are strictly national; location pages retain accurate `CITY_CENTROIDS` GPS and address blocks.
  - [x] **Full 5-Archetype Validation Matrix**: 100% passing across all test suites (`ai digital marketing services`, `b2b content marketing`, `ppc consultant cardiff`, `seo newport`, `digital marketing consultant`).
  - [x] Verified Reports Generated & Available in `output/reports/`:
    - `20260918_130731_ai_digital_marketing_services_master_blueprint.md` (National Service)
    - `20260918_130406_b2b_content_marketing_master_blueprint.md` (National Guide)
    - `20260918_130409_ppc_consultant_cardiff_master_blueprint.md` (Local Service)
    - `20260918_130744_seo_newport_master_blueprint.md` (Location Page)
    - `20260918_130815_digital_marketing_consultant_master_blueprint.md` (National Homepage Hub)

- [ ] **Phase 5: Packaging into Reusable Custom Skill (Next Focus Once Verified in Fresh Session)**
  - [ ] Package the verified Python pipeline into an Antigravity Custom Skill (`skills/seo-blueprint/` or `.gemini/antigravity-cli/skills/seo_planner/`) for on-demand slash command invocation.

---

## 📝 Discovered Quirks & Learnings
- *Keywords Everywhere API requires country code `"uk"`, NOT `"gb"`. If `"gb"` is passed, it silently defaults to Global metrics.*
- *DataForSEO Labs 3+ word queries with `include_seed_keyword=True` return 0 items if the exact phrase isn't indexed; intelligent relaxation to `base_service city` is required.*
- *Google SERP API returns `asynchronous_ai_overview: True` with `None` for text, markdown, and references; defensive parsing is required.*
- *Python `load_dotenv()` defaults to `override=False`; always use `override=True` to avoid shell variable leaks.*
- *Competitors often cross-sell secondary services on money pages (e.g. web design on PPC pages); topical domain filters are mandatory to protect AI writers from topical dilution.*
- *Exact Match Domains (EMDs) contain generic keywords; brand filtering must ignore generic tokens (`seo`, `ppc`, `agency`, `cardiff`) so legitimate commercial keywords aren't marked as competitor brands.*
