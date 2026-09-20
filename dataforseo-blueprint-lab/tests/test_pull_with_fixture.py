"""Offline proof of the raw-to-evidence path using a sanitised fixture.

No network. The provider's transport is replaced with the fixture, so this
tests cache, guard, ledger and run store end to end - the behaviour the old
test harness never proved (it graded report files by mtime instead).
"""

import json
import subprocess
import sys
from pathlib import Path

from lab.cache import Cache
from lab.ledger import Ledger, KE_CREDITS
from lab.guardrails import SpendGuard
from lab.providers.dataforseo import DataForSEOProvider
from lab.providers.keywords_everywhere import KeywordsEverywhereProvider
from lab.runstore import RunStore

ENDPOINT = "dataforseo_labs/google/keyword_suggestions/live"


def test_fixture_pull_produces_verifiable_evidence(tmp_path, fixture_response, fake_transport):
    store = RunStore(tmp_path / "runs")
    run = store.create_run("keyword-suggestions")
    payload = {"keyword": "example seed", "location_code": 2826, "limit": 50}
    run.set_request("dataforseo", ENDPOINT, payload)
    guard = SpendGuard(Ledger(tmp_path / "runs" / "ledger.jsonl"), run.run_id)
    provider = DataForSEOProvider(transport=fake_transport)

    estimate = provider.estimate_cost(ENDPOINT, payload)
    assert estimate == 0.01  # catalog price, not a guess

    guard.preflight("dataforseo", ENDPOINT, estimate)
    response = provider.call(ENDPOINT, payload)
    assert response == fixture_response

    actual, source = provider.extract_cost(response)
    assert (actual, source) == (0.01, "provider_returned")
    guard.record("dataforseo", ENDPOINT, estimate, actual, source)

    run.write_raw("dataforseo", ENDPOINT, response, cache_hit=False)
    run.finalize()
    assert run.verify()

    entries = guard.ledger.entries()
    assert len(entries) == 1 and entries[0].run_id == run.run_id
    assert entries[0].actual_cost == 0.01


def test_provider_returned_cost_beats_catalog_estimate(tmp_path, fixture_response, fake_transport):
    fixture_response["cost"] = 0.02
    provider = DataForSEOProvider(transport=fake_transport)
    actual, source = provider.extract_cost(provider.call(ENDPOINT, {}))
    assert (actual, source) == (0.02, "provider_returned")


def test_ke_keyword_data_is_priced_per_keyword(tmp_path):
    ke = KeywordsEverywhereProvider()
    estimate = ke.estimate_cost("get_keyword_data", {"keywords": ["a", "b", "c"]})
    assert estimate == 3.0  # 1 credit per keyword


def test_ke_unmetered_endpoint_shares_guard_and_fails_closed(tmp_path):
    ke = KeywordsEverywhereProvider()
    guard = SpendGuard(Ledger(tmp_path / "ledger.jsonl"), "run-1")
    import pytest
    from lab.guardrails import UnknownCost
    with pytest.raises(UnknownCost):
        ke.metered_call(guard, "get_pasf_keywords", {"keyword": "x"})


def test_ke_metered_call_with_declared_cost_lands_in_same_ledger(tmp_path):
    calls = []
    ke = KeywordsEverywhereProvider(mcp_caller=lambda ep, p: calls.append((ep, p)) or {"ok": True})
    guard = SpendGuard(Ledger(tmp_path / "ledger.jsonl"), "run-1")
    ke.metered_call(guard, "get_pasf_keywords", {"keyword": "x"}, declared_cost=2)
    entries = guard.ledger.entries()
    assert entries[-1].currency == KE_CREDITS and entries[-1].actual_cost == 2
    assert guard.ledger.spend_for_run("run-1", KE_CREDITS) == 2
