import json

import pytest

from lab.runstore import RunStore, RunExistsError, Run


def test_run_dirs_are_never_overwritten(tmp_path):
    store = RunStore(tmp_path / "runs")
    store.create_run("s", run_id="fixed-id")
    with pytest.raises(RunExistsError):
        store.create_run("s", run_id="fixed-id")


def test_manifest_hashes_verify(tmp_path):
    store = RunStore(tmp_path / "runs")
    run = store.create_run("s")
    run.set_request("dataforseo", "e", {"k": "v"})
    run.write_raw("dataforseo", "e", {"cost": 0.01}, cache_hit=False)
    manifest_path = run.finalize()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["run_id"] == run.run_id
    assert run.verify()


def test_verify_catches_tampering(tmp_path):
    store = RunStore(tmp_path / "runs")
    run = store.create_run("s")
    run.set_request("dataforseo", "e", {"k": "v"})
    raw = run.write_raw("dataforseo", "e", {"cost": 0.01}, cache_hit=False)
    run.finalize()
    raw.write_text('{"cost": 999}')
    assert not run.verify()


def test_manifest_matches_schema(tmp_path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        (__import__("pathlib").Path(__file__).resolve().parents[1]
         / "schemas" / "run-manifest.schema.json").read_text())
    store = RunStore(tmp_path / "runs")
    run = store.create_run("s")
    run.set_request("dataforseo", "e", {"k": "v"})
    run.write_raw("dataforseo", "e", {"x": 1}, cache_hit=False)
    manifest = json.loads(run.finalize().read_text())
    jsonschema.validate(manifest, schema)
