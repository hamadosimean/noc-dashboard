import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.core import rate_limit as rl


def make_request(ip: str = "10.0.0.1", real_ip: str | None = None) -> Request:
    headers = [(b"x-real-ip", real_ip.encode())] if real_ip else []
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": headers,
        "client": (ip, 12345),
        "query_string": b"",
    }
    return Request(scope)


class FakeRedis:
    def __init__(self):
        self.counts = {}
        self.expirations = {}

    def incr(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    def expire(self, key, ttl):
        self.expirations[key] = ttl


class BrokenRedis:
    def incr(self, key):
        raise ConnectionError("redis down")


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setattr(rl, "RATE_LIMIT_ENABLED", True)
    fake = FakeRedis()
    monkeypatch.setattr(rl, "redis_client", fake)
    return fake


def test_requests_within_limit_pass(enabled):
    dep = rl.rate_limit("test", 3)
    request = make_request()
    for _ in range(3):
        dep(request)  # no exception


def test_request_over_limit_rejected(enabled):
    dep = rl.rate_limit("test", 3)
    request = make_request()
    for _ in range(3):
        dep(request)
    with pytest.raises(HTTPException) as exc:
        dep(request)
    assert exc.value.status_code == 429


def test_limits_are_per_ip(enabled):
    dep = rl.rate_limit("test", 1)
    dep(make_request(ip="10.0.0.1"))
    dep(make_request(ip="10.0.0.2"))  # separate bucket, still allowed


def test_x_real_ip_takes_precedence(enabled):
    dep = rl.rate_limit("test", 1)
    dep(make_request(ip="172.18.0.5", real_ip="41.207.0.9"))
    with pytest.raises(HTTPException):
        # Same real client behind the proxy, even though the socket IP matches nginx
        dep(make_request(ip="172.18.0.5", real_ip="41.207.0.9"))


def test_fails_open_when_redis_down(monkeypatch):
    monkeypatch.setattr(rl, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(rl, "redis_client", BrokenRedis())
    dep = rl.rate_limit("test", 1)
    request = make_request()
    for _ in range(5):
        dep(request)  # never raises


def test_disabled_flag_bypasses(monkeypatch):
    monkeypatch.setattr(rl, "RATE_LIMIT_ENABLED", False)
    monkeypatch.setattr(rl, "redis_client", BrokenRedis())
    dep = rl.rate_limit("test", 0)
    dep(make_request())
