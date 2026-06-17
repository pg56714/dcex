# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import msgspec
import pytest
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

from tests.unit.native_http_helpers import _http_server


def test_native_okx_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        client = native.OkxHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            flag="1",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "GET",
            "/api/v5/account/balance",
            [("ccy", "BTC")],
            None,
            True,
        )

    request = received.get_nowait()
    timestamp = request["OK-ACCESS-TIMESTAMP"]
    canonical = f"{timestamp}GET/api/v5/account/balance?ccy=BTC"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", canonical.encode(), hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"code": "0", "data": []}
    assert request["OK-ACCESS-KEY"] == "api-key"
    assert request["OK-ACCESS-PASSPHRASE"] == "passphrase"
    assert request["OK-ACCESS-SIGN"] == expected_signature
    assert request["x-simulated-trading"] == "1"


def test_sync_okx_manager_uses_native_transport() -> None:
    from dcex.okx._http_manager import HTTPManager

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        manager = HTTPManager(
            base_api=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v5/public/time",
            {"source": "native"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "0", "data": []}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v5/public/time?source=native"


@pytest.mark.asyncio
async def test_async_okx_manager_uses_native_transport() -> None:
    from dcex.async_support.okx._http_manager import HTTPManager

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        manager = HTTPManager(
            base_api=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v5/public/time",
            {"source": "native"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"code": "0", "data": []}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v5/public/time?source=native"


def test_native_kucoin_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "200000", "data": {}}) as (base_url, received):
        client = native.KucoinHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "GET",
            "spot",
            "/api/v1/accounts",
            [("currency", "BTC USDT"), ("type", "trade")],
            None,
            True,
        )

    request = received.get_nowait()
    timestamp = request["KC-API-TIMESTAMP"]
    canonical = f"{timestamp}GET/api/v1/accounts?currency=BTC+USDT&type=trade"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", canonical.encode(), hashlib.sha256).digest()
    ).decode()
    expected_passphrase = base64.b64encode(
        hmac.new(b"secret", b"passphrase", hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"code": "200000", "data": {}}
    assert request["KC-API-KEY"] == "api-key"
    assert request["KC-API-SIGN"] == expected_signature
    assert request["KC-API-PASSPHRASE"] == expected_passphrase
    assert request["KC-API-KEY-VERSION"] == "2"


def test_sync_kucoin_manager_uses_native_transport() -> None:
    from dcex.kucoin._http_manager import HTTPManager

    with _http_server({"code": "200000", "data": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/timestamp",
            {"source": "native"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "200000", "data": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/timestamp?source=native"


@pytest.mark.asyncio
async def test_async_kucoin_manager_uses_native_transport() -> None:
    from dcex.async_support.kucoin._http_manager import HTTPManager

    with _http_server({"code": "200000", "data": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/timestamp",
            {"source": "native"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"code": "200000", "data": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/timestamp?source=native"


def test_native_kraken_spot_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_secret = base64.b64encode(b"secret").decode()

    with _http_server({"error": [], "result": {}}) as (base_url, received):
        client = native.KrakenHttpClient(
            spot_api_key="api-key",
            spot_api_secret=api_secret,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "spot",
            "/0/private/Balance",
            [("asset", "BTC USD")],
            None,
            True,
        )

    request = received.get_nowait()
    encoded_body = request["body"]
    nonce = dict(parse_qsl(encoded_body))["nonce"]
    digest = hashlib.sha256((nonce + encoded_body).encode()).digest()
    expected_signature = base64.b64encode(
        hmac.new(b"secret", b"/0/private/Balance" + digest, hashlib.sha512).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"error": [], "result": {}}
    assert request["kraken_api-key"] == "api-key"
    assert request["kraken_api-sign"] == expected_signature
    assert request["path"] == "/0/private/Balance"


def test_native_kraken_futures_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_secret = base64.b64encode(b"secret").decode()

    with _http_server({"result": "success"}) as (base_url, received):
        client = native.KrakenHttpClient(
            futures_api_key="api-key",
            futures_api_secret=api_secret,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "futures",
            "/derivatives/api/v3/sendorder",
            [("symbol", "PI_XBTUSD"), ("side", "buy")],
            None,
            True,
        )

    request = received.get_nowait()
    post_data = request["body"]
    nonce = request["kraken_nonce"]
    digest = hashlib.sha256((post_data + nonce + "/api/v3/sendorder").encode()).digest()
    expected_signature = base64.b64encode(
        hmac.new(b"secret", digest, hashlib.sha512).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"result": "success"}
    assert request["kraken_apikey"] == "api-key"
    assert request["kraken_authent"] == expected_signature


def test_sync_kraken_manager_uses_native_transport() -> None:
    from dcex.kraken._http_manager import HTTPManager

    with _http_server({"error": [], "result": {"unixtime": 1}}) as (
        base_url,
        received,
    ):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/0/public/Time",
            signed=False,
        )

    manager.close()
    assert result == {"error": [], "result": {"unixtime": 1}}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/0/public/Time"


@pytest.mark.asyncio
async def test_async_kraken_manager_uses_native_transport() -> None:
    from dcex.async_support.kraken._http_manager import HTTPManager

    with _http_server({"error": [], "result": {"unixtime": 1}}) as (
        base_url,
        received,
    ):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/0/public/Time",
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"error": [], "result": {"unixtime": 1}}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/0/public/Time"
