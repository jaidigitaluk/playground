import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture
def fixture_response() -> dict:
    path = ROOT / "tests" / "fixtures" / "keyword_suggestions_response.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def fake_transport(fixture_response):
    def transport(method: str, endpoint: str, body: list) -> dict:
        return fixture_response
    return transport
