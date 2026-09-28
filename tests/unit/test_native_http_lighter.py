"""Offline coverage for native http lighter."""
# ruff: noqa: D100, D103, F401

import base64
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_lighter_form_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0}) as (base_url, received):
        client = native.LighterHttpClient(timeout=2, base_url=base_url)
        status, _headers, body = client.request_raw_json(
            "POST",
            "/api/v1/sendTx",
            [("account_index", "1")],
            [("tx_type", "14"), ("tx_info", '{"Price":100}')],
            False,
            {"Authorization": "token"},
            "form",
        )

    request = received.get_nowait()
    assert status == 200
    assert body == {"code": 0}
    assert request["path"] == "/api/v1/sendTx?account_index=1"
    assert request["body"] == "tx_type=14&tx_info=%7B%22Price%22%3A100%7D"


def test_sync_lighter_manager_uses_native_transport() -> None:
    from dcex.lighter._http_manager import HTTPManager

    with _http_server({"code": 0, "status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/status",
            {"source": "native"},
        )

    manager.close()
    assert result == {"code": 0, "status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/status?source=native"


@pytest.mark.asyncio
async def test_async_lighter_manager_uses_native_transport() -> None:
    from dcex.async_support.lighter._http_manager import HTTPManager

    with _http_server({"code": 0, "status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/status",
            {"source": "native"},
        )

    assert result == {"code": 0, "status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/status?source=native"
