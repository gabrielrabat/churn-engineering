from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from slowapi.errors import RateLimitExceeded

from src.api.rate_limit import get_client_identifier, rate_limit_exceeded_handler


def _make_request(headers: dict, client_host: str = "10.0.0.1"):
    request = MagicMock()
    request.headers = headers
    request.client.host = client_host
    request.url.path = "/predict"
    return request


def test_get_client_identifier_prefers_x_forwarded_for():
    request = _make_request({"X-Forwarded-For": "203.0.113.5, 10.0.0.1"})

    assert get_client_identifier(request) == "203.0.113.5"


def test_get_client_identifier_falls_back_to_remote_address(monkeypatch):
    request = _make_request({})
    monkeypatch.setattr(
        "src.api.rate_limit.get_remote_address", lambda req: "192.168.0.9"
    )

    assert get_client_identifier(request) == "192.168.0.9"


def test_rate_limit_exceeded_handler_returns_429_with_retry_after():
    request = _make_request({})
    exc = RateLimitExceeded(MagicMock(error_message="30 per 1 minute"))

    response = asyncio.run(rate_limit_exceeded_handler(request, exc))

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
