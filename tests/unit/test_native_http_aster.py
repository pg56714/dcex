"""Offline coverage for native http aster."""
# ruff: noqa: D100, D103, F401

import base64
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_aster_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"

    with _http_server({}) as (base_url, received):
        client = native.AsterHttpClient(
            signer_address=signer,
            private_key="0x" + "11" * 32,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "spot",
            "/api/v3/order",
            [("symbol", "BTCUSDT"), ("side", "BUY")],
            True,
        )

    request = received.get_nowait()
    pairs = parse_qsl(request["body"])
    signature = dict(pairs)["signature"]
    message = "&".join(f"{key}={value}" for key, value in pairs[:-1])
    from dcex.aster._http_manager import sign_message

    assert status == 200
    assert body == {"ok": True}
    assert signature == sign_message(message, "0x" + "11" * 32)


def test_sync_aster_public_wrapper_uses_native_dispatcher() -> None:
    pytest.importorskip("dcex._native")
    from dcex.aster.client import Client

    with _http_server({"serverTime": 1}) as (base_url, received):
        client = Client(
            spot_base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = client.get_spot_server_time()

    client.close()
    assert result == {"serverTime": 1}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v3/time"


@pytest.mark.asyncio
async def test_async_aster_public_wrapper_uses_native_dispatcher() -> None:
    pytest.importorskip("dcex._native")
    from dcex.async_support.aster.client import Client

    with _http_server({"serverTime": 1}) as (base_url, received):
        client = Client(
            spot_base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await client.async_init()
        result = await client.get_futures_server_time()

    await client.close()
    assert result == {"serverTime": 1}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/fapi/v3/time"
