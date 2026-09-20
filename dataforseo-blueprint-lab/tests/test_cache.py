import time

from lab.cache import Cache


def test_roundtrip_and_hit_flag(tmp_path):
    cache = Cache(tmp_path / ".cache")
    key = cache.put("e", {"a": 1}, {"ok": True})
    resp, key2, hit = cache.get("e", {"a": 1})
    assert hit and resp == {"ok": True} and key == key2


def test_payload_order_independent_key(tmp_path):
    cache = Cache(tmp_path / ".cache")
    assert Cache.key("e", {"a": 1, "b": 2}) == Cache.key("e", {"b": 2, "a": 1})


def test_expired_entry_is_a_miss(tmp_path):
    cache = Cache(tmp_path / ".cache", ttl_seconds=0)
    cache.put("e", {"a": 1}, {"ok": True})
    time.sleep(0.01)
    _, _, hit = cache.get("e", {"a": 1})
    assert not hit
