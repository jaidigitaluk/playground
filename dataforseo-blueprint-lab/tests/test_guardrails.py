import pytest

from lab.ledger import Ledger, USD, KE_CREDITS
from lab.guardrails import SpendGuard, CapExceeded, UnknownCost


def make_guard(tmp_path, **kw):
    return SpendGuard(Ledger(tmp_path / "ledger.jsonl"), run_id="run-1", **kw)


def test_unknown_cost_fails_closed_and_is_logged(tmp_path):
    guard = make_guard(tmp_path)
    with pytest.raises(UnknownCost):
        guard.preflight("keywords_everywhere", "get_pasf_keywords", None)
    entries = guard.ledger.entries()
    assert entries[0].status == "blocked_unknown_cost"


def test_unknown_cost_allowed_only_with_explicit_flag(tmp_path):
    guard = make_guard(tmp_path, allow_unknown_cost=True)
    guard.preflight("keywords_everywhere", "get_pasf_keywords", None)  # no raise


def test_per_run_cap_blocks_and_logs(tmp_path):
    guard = make_guard(tmp_path, max_usd_per_run=0.015, max_usd_per_day=10)
    guard.preflight("dataforseo", "e", 0.01)
    guard.record("dataforseo", "e", 0.01, 0.01, "catalog_estimate")
    with pytest.raises(CapExceeded):
        guard.preflight("dataforseo", "e", 0.01)
    assert guard.ledger.entries()[-1].status == "blocked_cap"


def test_per_day_cap_spans_runs(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    g1 = SpendGuard(ledger, run_id="run-1", max_usd_per_run=10, max_usd_per_day=0.015)
    g1.preflight("dataforseo", "e", 0.01)
    g1.record("dataforseo", "e", 0.01, 0.01, "catalog_estimate")
    g2 = SpendGuard(ledger, run_id="run-2", max_usd_per_run=10, max_usd_per_day=0.015)
    with pytest.raises(CapExceeded):
        g2.preflight("dataforseo", "e", 0.01)


def test_ke_credits_have_their_own_caps(tmp_path):
    guard = make_guard(tmp_path, max_ke_per_run=3, max_ke_per_day=1000)
    guard.preflight("keywords_everywhere", "get_keyword_data", 2)
    guard.record("keywords_everywhere", "get_keyword_data", 2, 2, "declared")
    with pytest.raises(CapExceeded):
        guard.preflight("keywords_everywhere", "get_keyword_data", 2)
    assert guard.ledger.spend_for_run("run-1", KE_CREDITS) == 2


def test_call_cap_counts_only_paid_completed_calls(tmp_path):
    guard = make_guard(tmp_path, max_calls_per_run=1, max_usd_per_run=10, max_usd_per_day=10)
    guard.preflight("dataforseo", "e", 0.01)
    guard.record("dataforseo", "e", 0.01, 0.01, "catalog_estimate")
    guard.record("dataforseo", "e", 0.01, 0.0, "catalog_estimate", cache_hit=True)
    with pytest.raises(CapExceeded):
        guard.preflight("dataforseo", "e", 0.01)
