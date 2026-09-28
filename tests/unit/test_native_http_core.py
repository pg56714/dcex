"""Offline coverage for native http core."""
# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_sync_http_client() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.HttpClient(timeout=2)
        status, headers, body = client.request(
            "GET",
            base_url,
            "/test",
            [("symbol", "BTCUSDT")],
            {"X-Test": "sync"},
        )

    assert status == 200
    assert headers["x-response"] == "native"
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait() == {
        "method": "GET",
        "path": "/test?symbol=BTCUSDT",
        "header": "sync",
        "api_key": None,
        "authorization": None,
        "body": "",
    }


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 1e300])
def test_native_http_client_rejects_invalid_timeout(timeout: float) -> None:
    native = pytest.importorskip("dcex._native")

    with pytest.raises(ValueError, match="HTTP timeout must be a positive finite number"):
        native.HttpClient(timeout=timeout)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 1e300])
def test_native_websocket_client_rejects_invalid_timeout(timeout: float) -> None:
    native = pytest.importorskip("dcex._native")

    with pytest.raises(ValueError, match="WebSocket timeout must be a positive finite number"):
        native.BinancePublicWebSocketClient(timeout=timeout)


@pytest.mark.asyncio
async def test_native_async_http_client() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.HttpClient(timeout=2)
        status, headers, body = await client.request_async(
            "GET",
            base_url,
            "/test",
            [("symbol", "ETHUSDT")],
            {"X-Test": "async"},
        )

    assert status == 200
    assert headers["x-response"] == "native"
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait() == {
        "method": "GET",
        "path": "/test?symbol=ETHUSDT",
        "header": "async",
        "api_key": None,
        "authorization": None,
        "body": "",
    }
