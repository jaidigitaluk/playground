# DataForSEO Testing Sandbox (`dataforseo-test`)

This directory is an isolated test environment for DataForSEO v3 API integrations and AI workflows.

---

## 📁 File Structure & Taxonomy

### Working Files (What you run & edit)
- [`01_verify_auth.py`](./01_verify_auth.py): Pre-flight check. Confirms connection and prints account balance without consuming credits.
- [`02_test_aio_serp.py`](./02_test_aio_serp.py): Live Google SERP scraper. Detects AI Overviews, cited sources, PAA questions, and top 10 competitors.
- [`03_keyword_clustering.py`](./03_keyword_clustering.py): Pulls keyword suggestions and clusters them into Informational, Commercial, and Transactional buckets.
- [`workflow_full_planner.py`](./workflow_full_planner.py): Master workflow that chains SERP + AIO + Clustering and produces a client-ready markdown blueprint.

### System Infrastructure (`_system/` - setup once, rarely touch)
- `_system/client.py`: Resilient HTTP client (auto array-wrapping `[{...}]`, 60s timeout, error detection).
- `_system/cache.py`: 24-hour disk cache (stores API responses so repeated tests cost $0.00).
- `_system/guardrails.py`: Spend protector (stops execution if budget or call limits are exceeded).
- `_system/git_guard.py`: Pre-commit security check ensuring no API keys or `.env` files can be committed.

### Catalogs & Config (`_config/`)
- `_config/endpoints_catalog.json`: Indexed DataForSEO endpoints with costs and parameter requirements.
- `_config/locations.json`: ISO countries mapped to DataForSEO `location_code` (UK 2826, US 2840, etc.).
- `_config/field_filters.json`: Masks to strip 95% of JSON payload bloat before processing.

---

## 🚀 Quickstart

1. **Activate the Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```
2. **Configure your Credentials**:
   ```bash
   cp .env.example .env
   # Open .env and add your DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD
   ```
3. **Verify Auth (Free)**:
   ```bash
   python3 01_verify_auth.py
   ```
4. **Run a Test**:
   ```bash
   # Test Live SERP + AI Overview
   python3 02_test_aio_serp.py "best crm for small business" --geo UK

   # Run Full Workflow Plan
   python3 workflow_full_planner.py "commercial electrician" --geo UK
   ```
