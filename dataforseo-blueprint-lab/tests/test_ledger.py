from pathlib import Path

from lab.ledger import Ledger, LedgerEntry, USD, KE_CREDITS


def entry(run_id="r1", ts="2026-09-20T10:00:00Z", cost=0.01, currency=USD,
          status="completed", cache_hit=False):
    return LedgerEntry(ts=ts, run_id=run_id, provider="dataforseo",
                       endpoint="e", status=status, estimated_cost=cost,
                       actual_cost=cost, cost_source="catalog_estimate",
                       currency=currency, cache_hit=cache_hit)


def test_append_and_read_roundtrip(tmp_path):
    ledger = Ledger(tmp_path / "runs" / "ledger.jsonl")
    ledger.append(entry())
    ledger.append(entry(run_id="r2", cost=0.02))
    entries = ledger.entries()
    assert len(entries) == 2
    assert entries[1].run_id == "r2"


def test_append_only_never_truncates(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.append(entry())
    Ledger(tmp_path / "ledger.jsonl").append(entry(run_id="r2"))
    assert len(ledger.entries()) == 2


def test_run_and_day_spend(tmp_path):
    ledger = Ledger(tmp_path / "ledger.jsonl")
    ledger.append(entry(run_id="r1", cost=0.01))
    ledger.append(entry(run_id="r1", cost=0.01, cache_hit=True, status="cache_hit"))
    ledger.append(entry(run_id="r2", cost=0.02))
    ledger.append(entry(run_id="r1", cost=5, currency=KE_CREDITS))
    assert ledger.spend_for_run("r1", USD) == 0.01          # cache hits are free
    assert ledger.spend_for_run("r1", KE_CREDITS) == 5
    assert ledger.spend_for_day("2026-09-20", USD) == 0.03  # across runs
    assert ledger.calls_for_run("r1") == 2  # the paid DFS call and the KE call; cache hits do not count
