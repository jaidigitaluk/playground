# Lab contract (Phase 0 - contract before code)

Agreed direction, from James's steering 19 Sep 2026: data pull first, using
DataForSEO's out-of-the-box integrations/templates where they exist; separate
scripts for synthesis and content writing. This file is the contract the code
answers to. It contains no business claims; identity, offer, location, proof
and pricing facts only ever enter through a reviewed project config at Phase 5,
which is not built.

## Supported use cases

1. **Keyword research (first and only v1 use case).** Bounded pull of keyword
   suggestions for one seed + one location, preserved as replayable evidence.
2. Later candidates (not built): competitor gap, one-page research brief.

Explicitly not supported: a universal SEO engine, autonomous copywriting,
anything that feeds live site copy.

## Provider choice

- DataForSEO calls go through the official client library
  (`dataforseo-client`, https://github.com/dataforseo/PythonClient, pinned in
  requirements.txt). Custom HTTP wrapping is allowed only where the official
  client does not cover a need, and must say why in a comment.
- Keywords Everywhere is reached through its MCP server. That path cannot be
  priced from inside this repo, so the adapter (src/lab/providers/
  keywords_everywhere.py) requires an explicit declared cost per call and
  **fails closed on unknown cost** unless James explicitly allows it
  (`LAB_ALLOW_UNKNOWN_COST=1`, his go-ahead, off by default).

## Schemas

`schemas/` defines the JSON contracts: pull request records, run manifests,
ledger entries. Tests validate produced artefacts against them.

## Two fixes landed first

### 1. Ledger versus Git

The old QA graded whichever report files it found locally by pattern and
modification time, while reports were git-ignored - so it could grade stale
files. Here a pull creates a run ID up front; manifest, raw evidence and
ledger entries all carry that run ID, and QA takes a run ID and verifies
hashes. Git history is for code and safe fixtures, never for guessing which
report is current. Raw responses stay git-ignored by default (open question 5
in the plan); the append-only ledger summary is safe to commit.

### 2. Keywords Everywhere shares the cap

KE MCP calls previously bypassed the guardrail entirely. Now every provider
goes through `SpendGuard` before execution: estimated or declared cost is
checked against per-run and per-day caps, and the actual/declared cost is
written to the same `runs/ledger.jsonl`. A run stops when either a
provider-specific cap or the total cap would be exceeded. Unknown cost fails
closed.

## Guardrail defaults (env-overridable)

| Setting | Default | Note |
|---|---|---|
| LAB_MAX_USD_PER_RUN | 0.25 | same stop as the old guard |
| LAB_MAX_USD_PER_DAY | 1.00 | new; the old guard reset per process |
| LAB_MAX_CALLS_PER_RUN | 6 | same as old guard |
| LAB_MAX_KE_CREDITS_PER_RUN | 50 | new; KE shares the cap |
| LAB_MAX_KE_CREDITS_PER_DAY | 200 | new |
| LAB_CACHE_TTL_HOURS | 24 | migrated pattern, hits now recorded |
| LAB_ALLOW_UNKNOWN_COST | unset (fail closed) | James's explicit go-ahead only |

Final per-run and per-day limits are open question 4 in the plan; these
defaults are placeholders for his decision, not a ruling.

## Definition of done for the first useful release

- A fresh checkout can authenticate, run one bounded keyword-research pull and
  reproduce analysis from stored evidence. (Pull + evidence store: this PR.
  Analysis: Phase 3, not built.)
- No paid call without a visible estimate and cap check.
- DataForSEO and Keywords Everywhere usage in one run ledger.
- CI passes on fixtures without network access.
- A synthesis claim can be traced to a run, response and transformation
  (Phase 4 gate, not built).
- No James, JAi, pricing, address, proof or schema claim exists unless a
  reviewed project config supplies it (Phase 5 gate, not built).
