# dataforseo-blueprint-lab

Evidence-first rebuild of the DataForSEO keyword-research pipeline.

The old `playground/dataforseo-test` planner grew into one 1,770-line script that
pulled data, interpreted it, applied business assumptions and wrote a finished
brief in a single pass. Raw DataForSEO data quality was good; the synthesis
overreach is where it broke. This lab resets around one rule: **pull first,
prove each layer separately, one script per job.**

Status: Phase 0-2 scaffold (contract, safe pull, evidence store, shared spend
ledger). Analysis (Phase 3), synthesis (Phase 4) and optional writing (Phase 5)
are deliberately absent. Proposed home for promotion to a dedicated
`jaidigitaluk` repository once the name is confirmed; until then it lives here
under the playground's test-break-promote rule.

Provenance: patterns migrated from `jaidigitaluk/playground/dataforseo-test`
(audited 19 Sep 2026). Reused ideas are labelled in module docstrings.
Nothing here is lifted wholesale.

## The five stages (docs/CONTRACT.md is the authority)

| Stage | Job | Output | Rule |
|---|---|---|---|
| 1. Pull | Call DataForSEO via official client patterns | Raw provider responses + request metadata | No strategy or prose |
| 2. Evidence store | Normalise and retain immutable run evidence | Run manifest, raw JSON, hashes, cache state, cost ledger | Never overwrite a prior run |
| 3. Analysis | Evidence to metrics, clusters, gaps | Structured JSON/tables | Label observed vs inferred vs heuristic (not built yet) |
| 4. Synthesis | Selected analyses to research brief | Traceable brief | Every conclusion cites evidence (not built yet) |
| 5. Optional writing | Brief to draft | Human-review draft | Off by default; no hardcoded identity or claims (not built yet) |

## Quickstart

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # add DataForSEO credentials
python pulls/preflight.py                     # free auth + balance check
python pulls/keyword_suggestions.py "seo newport" --location-code 2826
pytest                                       # offline, fixture-based
```

Every paid call is estimated and capped before it fires, and recorded in one
append-only ledger shared by DataForSEO and Keywords Everywhere. See
`docs/CONTRACT.md` sections "Ledger versus Git" and "Shared cap".
