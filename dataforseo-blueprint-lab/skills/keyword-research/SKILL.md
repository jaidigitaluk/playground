---
name: keyword-research
description: Researches SEO keywords from seed terms, related terms, search volume, keyword difficulty, Google organic SERPs, AI Overviews, People Also Ask, ChatGPT citations and fan-out queries. Use whenever a user asks for keyword research, keyword opportunities, local South Wales search terms, AI-search keywords, or competitor-query evidence. Does not write content or strategy.
---

# Keyword research

Produce evidence-backed keyword research only. Do not write pages, briefs, campaigns or recommendations.

## Required input

Get seed terms, target market, and location. Default only to UK national (`2826`). Resolve Cardiff, Newport and Swansea through `pulls/location_lookup.py`; never guess a city code.

## Workflow

1. Run `scripts/orchestrate.py plan.json --out run-plan.json`.
2. Run `scripts/validate_artifact.py run-plan.json schemas/run-plan.schema.json`.
3. Dispatch only the pull scripts named in the validated plan. Every paid pull must pass the shared preflight, spend guard, cache, ledger and immutable evidence store.
4. Validate each run manifest before loading its raw response. Stop on any failed gate.
5. Build a `keyword-research.json` result that cites run IDs and evidence paths. Label every finding exactly `Confirmed`, `Likely` or `Hypothesis`.
6. Validate the final result before handing it off. Keep raw evidence separate.

## Endpoint jobs

- `keyword_suggestions.py`: seed expansion.
- `related_keywords.py`: semantically related terms. Do not call them Google-confirmed LSI terms.
- `search_volume.py`: volume, CPC, competition and monthly trend. This removes the required Keywords Everywhere dependency for these metrics.
- `bulk_keyword_difficulty.py`: difficulty for a bounded batch.
- `organic_serp.py`: rankings plus raw AI Overview and People Also Ask item blocks.
- `chatgpt_llm_scraper.py`: answer, cited sources and `fan_out_queries`.

## Confidence

- `Confirmed`: directly present in provider evidence from this run.
- `Likely`: repeatable pattern derived from at least two Confirmed observations. Cite both.
- `Hypothesis`: useful idea not established by the evidence. State the missing test.

Never promote a label. Missing, stale or contradictory evidence lowers confidence.

## Spend and safety

Default caps are placeholders: `$0.25/run`, `$1/day`, six paid calls per run. Unknown cost fails closed. Never set `LAB_ALLOW_UNKNOWN_COST=1` without James's explicit approval. Never make a live paid call during tests or skill authoring. Raw provider responses stay out of Git.

## Freshness

Read `references/methodology-2026-09-20.md`. Recheck endpoint shapes and pricing after 30 days, or immediately after a provider schema error. Record the checked date and source URL when refreshing.

## Output boundary

Return typed JSON and a short factual summary. No content synthesis, page writing, SEO strategy, client claims, invented business context or approval language.

## Eval checklist

1. UK seed: `seo consultant`, UK 2826. Six jobs plan correctly; unknown costs block before network; no prose is written.
2. Cardiff local: location code is resolved, not guessed. Search-volume batches stay under 1,000 keywords. Every output claim has a confidence label and run ID.
3. AI search: `chatgpt_llm_scraper` retains citations and `fan_out_queries`; organic SERP retains AI Overview and PAA item types; a missing field becomes Hypothesis or an explicit gap, never an invented value.
