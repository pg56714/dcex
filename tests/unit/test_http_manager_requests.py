"""Offline request-path regression tests for HTTP managers."""
# ruff: noqa: ANN401, D103

from __future__ import annotations

import base64
import hashlib
import hmac
from importlib import import_module
from typing import Any

import pytest
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

from dcex.utils.errors import FailedRequestError

API_KEY = "test_api_key_0000"
API_SECRET = "test_api_secret_0000"
TS_S = "1700000000"


class _FakeResponse:
    def __init__(
        self,
        payload: Any | None = None,  # noqa: ANN401
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._payload = payload or {}
        self.status_code = status_code
        self.headers: dict[str, str] = headers or {}
        self.text = str(self._payload)
        self.content = b"" if payload is None else b"{}"

    @property
    def ok(self) -> bool:
        return self.status_code // 100 == 2

    def json(self) -> dict[str, Any]:
        return self._payload


class _BadJsonResponse(_FakeResponse):
    def __init__(self, status_code: int = 200) -> None:
        super().__init__({}, status_code)
        self.text = "<html>"

    def json(self) -> dict[str, Any]:
        raise ValueError("bad json")


class _CaptureSession:
    def __init__(
        self,
        payload: Any | None = None,  # noqa: ANN401
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.payload = payload
        self.status_code = status_code
        self.headers = headers
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def _response(self) -> _FakeResponse:
        return _FakeResponse(self.payload, self.status_code, self.headers)

    def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("GET", url, kwargs))
        return self._response()

    def post(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("POST", url, kwargs))
        return self._response()

    def put(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("PUT", url, kwargs))
        return self._response()

    def delete(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("DELETE", url, kwargs))
        return self._response()

    def request(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append((method.upper(), url, kwargs))
        return self._response()


class _BadJsonSession(_CaptureSession):
    def _response(self) -> _FakeResponse:
        return _BadJsonResponse(self.status_code)


class _AsyncCaptureSession:
    is_closed = False

    def __init__(
        self,
        payload: Any | None = None,  # noqa: ANN401
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.payload = payload
        self.status_code = status_code
        self.headers = headers
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def _response(self) -> _FakeResponse:
        return _FakeResponse(self.payload, self.status_code, self.headers)

    async def get(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("GET", url, kwargs))
        return self._response()

    async def post(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("POST", url, kwargs))
        return self._response()

    async def put(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("PUT", url, kwargs))
        return self._response()

    async def delete(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("DELETE", url, kwargs))
        return self._response()

    async def patch(self, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append(("PATCH", url, kwargs))
        return self._response()

    async def request(self, method: str, url: str, **kwargs: Any) -> _FakeResponse:
        self.calls.append((method.upper(), url, kwargs))
        return self._response()


class _AsyncBadJsonSession(_AsyncCaptureSession):
    def _response(self) -> _FakeResponse:
        return _BadJsonResponse(self.status_code)


def test_sync_binance_signed_request_does_not_mutate_reused_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.binance._http_manager import HTTPManager
    from dcex.binance.endpoints.account import FuturesAccount

    binance_http = import_module("dcex.binance._http_manager")
    monkeypatch.setattr(binance_http.time, "time", lambda: int(TS_S))
    client = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    session = _CaptureSession(payload={"assets": []})
    client.session = session
    query = {"limit": 10}

    client._request("GET", FuturesAccount.ACCOUNT_INFO, query)
    client._request("GET", FuturesAccount.ACCOUNT_INFO, query)

    assert query == {"limit": 10}
    first_url = session.calls[0][1]
    second_url = session.calls[1][1]
    assert first_url == second_url


@pytest.mark.asyncio
async def test_async_binance_signed_request_does_not_mutate_reused_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.binance._http_manager import HTTPManager
    from dcex.async_support.binance.endpoints.account import FuturesAccount

    binance_http = import_module("dcex.async_support.binance._http_manager")
    monkeypatch.setattr(binance_http.time, "time", lambda: int(TS_S))
    client = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    session = _AsyncCaptureSession(payload={"assets": []})
    client.session = session
    query = {"limit": 10}

    await client._request("GET", FuturesAccount.ACCOUNT_INFO, query)
    await client._request("GET", FuturesAccount.ACCOUNT_INFO, query)

    assert query == {"limit": 10}
    first_url = session.calls[0][1]
    second_url = session.calls[1][1]
    assert first_url == second_url


@pytest.mark.asyncio
async def test_async_bitmart_unsigned_post_sends_json_body() -> None:
    from dcex.async_support.bitmart._http_manager import HTTPManager
    from dcex.async_support.bitmart.endpoints.trade import SpotTrade

    client = HTTPManager(preload_product_table=False)
    session = _AsyncCaptureSession(payload={"code": 1000})
    client.session = session

    await client._request(
        "POST",
        SpotTrade.SUBMIT_ORDER,
        {"symbol": "BTC_USDT", "side": "buy"},
        signed=False,
    )

    method, _, kwargs = session.calls[0]
    assert method == "POST"
    assert kwargs["content"] == '{"symbol":"BTC_USDT","side":"buy"}'


def test_sync_bitmart_get_preserves_falsy_query_values() -> None:
    from dcex.bitmart._http_manager import HTTPManager
    from dcex.bitmart.endpoints.market import SpotMarket

    client = HTTPManager(preload_product_table=False)
    session = _CaptureSession(payload={"code": 1000})
    client.session = session

    client._request(
        "GET",
        SpotMarket.GET_TICKER_OF_A_PAIR,
        {"needUsdValuation": False, "missing": None, "zero": 0},
        signed=False,
    )

    assert session.calls[0][1].endswith("?needUsdValuation=false&zero=0")


@pytest.mark.asyncio
async def test_async_bitmart_get_preserves_falsy_query_values() -> None:
    from dcex.async_support.bitmart._http_manager import HTTPManager
    from dcex.async_support.bitmart.endpoints.market import SpotMarket

    client = HTTPManager(preload_product_table=False)
    session = _AsyncCaptureSession(payload={"code": 1000})
    client.session = session

    await client._request(
        "GET",
        SpotMarket.GET_TICKER_OF_A_PAIR,
        {"needUsdValuation": False, "missing": None, "zero": 0},
        signed=False,
    )

    assert session.calls[0][1].endswith("?needUsdValuation=false&zero=0")


def test_bitmex_sync_and_async_defaults_use_same_timeout() -> None:
    from dcex.async_support.bitmex._http_manager import HTTPManager as AsyncHTTPManager
    from dcex.bitmex._http_manager import HTTPManager

    sync_client = HTTPManager(preload_product_table=False)
    async_client = AsyncHTTPManager(preload_product_table=False)

    assert sync_client.timeout == async_client.timeout == 10


@pytest.mark.asyncio
async def test_async_bybit_post_sends_exact_signed_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.bybit._http_manager import HTTPManager

    client = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
        sync_server_time=False,
    )
    client.endpoint = "https://api.bybit.com"
    session = _AsyncCaptureSession(payload={"retCode": 0})
    client.session = session
    bybit_http = import_module("dcex.async_support.bybit._http_manager")
    monkeypatch.setattr(bybit_http, "generate_timestamp", lambda: int(TS_S))
    query = {"symbol": "BTCUSDT", "note": "測試"}

    await client._request("POST", "/v5/order/create", query)

    _, _, kwargs = session.calls[0]
    payload = '{"symbol":"BTCUSDT","note":"測試"}'
    assert kwargs["content"] == payload
    assert kwargs["headers"]["X-BAPI-SIGN"] == client._auth(payload, int(TS_S))


def test_sync_bybit_get_preserves_falsy_query_values() -> None:
    from dcex.bybit._http_manager import HTTPManager

    client = HTTPManager(preload_product_table=False, sync_server_time=False)
    client.endpoint = "https://api.bybit.com"
    session = _CaptureSession(payload={"retCode": 0})
    client.session = session

    client._request(
        "GET",
        "/v5/test",
        {"missing": None, "zero": 0},
        signed=False,
    )

    assert session.calls[0][1].endswith("?zero=0")


@pytest.mark.asyncio
async def test_async_bybit_get_preserves_falsy_query_values() -> None:
    from dcex.async_support.bybit._http_manager import HTTPManager

    client = HTTPManager(preload_product_table=False, sync_server_time=False)
    client.endpoint = "https://api.bybit.com"
    session = _AsyncCaptureSession(payload={"retCode": 0})
    client.session = session

    await client._request(
        "GET",
        "/v5/test",
        {"missing": None, "zero": 0},
        signed=False,
    )

    assert session.calls[0][1].endswith("?zero=0")


def test_sync_hyperliquid_signed_request_does_not_mutate_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.hyperliquid._http_manager import HTTPManager

    hyperliquid_http = import_module("dcex.hyperliquid._http_manager")
    monkeypatch.setattr(hyperliquid_http, "generate_timestamp", lambda: int(TS_S))
    client = HTTPManager(
        wallet_address="0x0000000000000000000000000000000000000001",
        private_key="01" * 32,
        preload_product_table=False,
    )
    session = _CaptureSession(payload={"status": "ok"})
    client.session = session
    query = {"action": {"type": "cancel", "cancels": []}}

    client._request("POST", "/exchange", query)

    assert query == {"action": {"type": "cancel", "cancels": []}}


@pytest.mark.asyncio
async def test_async_hyperliquid_signed_request_does_not_mutate_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.hyperliquid._http_manager import HTTPManager

    hyperliquid_http = import_module("dcex.async_support.hyperliquid._http_manager")
    monkeypatch.setattr(hyperliquid_http, "generate_timestamp", lambda: int(TS_S))
    client = HTTPManager(
        wallet_address="0x0000000000000000000000000000000000000001",
        private_key="01" * 32,
        preload_product_table=False,
    )
    client.endpoint = "https://api.hyperliquid.xyz"
    session = _AsyncCaptureSession(payload={"status": "ok"})
    client.session = session
    query = {"action": {"type": "cancel", "cancels": []}}

    await client._request("POST", "/exchange", query)

    assert query == {"action": {"type": "cancel", "cancels": []}}


@pytest.mark.asyncio
async def test_async_hyperliquid_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.async_support.hyperliquid._market_http import MarketHTTP

    class _NativeClient:
        def __init__(self) -> None:
            self.calls: list[tuple[str, list[tuple[str, str]]]] = []

        async def public_request_async(
            self,
            method_name: str,
            params: list[tuple[str, str]],
        ) -> tuple[int, dict[str, str], bytes]:
            self.calls.append((method_name, params))
            return 200, {"x-response": "native"}, b'{"levels":[]}'

    native_client = _NativeClient()
    client = MarketHTTP(preload_product_table=False)
    client._native_client = native_client

    result = await client.get_l2book("BTC-USDC-SWAP")

    assert result == {"levels": []}
    assert native_client.calls == [("get_l2book", [("product_symbol", "BTC-USDC-SWAP")])]
    assert client.last_response_headers == {"x-response": "native"}


def test_bingx_listen_key_uses_managed_request_path() -> None:
    from dcex.bingx._account_http import AccountHTTP

    client = AccountHTTP(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    session = _CaptureSession(payload={"code": 0, "listenKey": "listen-key"})
    client.session = session

    assert client.get_listen_key() == "listen-key"
    method, _, kwargs = session.calls[0]
    assert method == "POST"
    assert kwargs["headers"] == {"X-BX-APIKEY": API_KEY}
    assert kwargs["timeout"] == client.timeout


def test_bingx_listen_key_raises_for_api_error() -> None:
    from dcex.bingx._account_http import AccountHTTP

    client = AccountHTTP(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    client.session = _CaptureSession(payload={"code": 100001, "msg": "invalid api key"})

    with pytest.raises(FailedRequestError, match="100001"):
        client.get_listen_key()


@pytest.mark.asyncio
async def test_async_bingx_listen_key_uses_managed_request_path() -> None:
    from dcex.async_support.bingx._account_http import AccountHTTP

    client = AccountHTTP(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    session = _AsyncCaptureSession(payload={"code": 0, "listenKey": "listen-key"})
    client.session = session

    assert await client.get_listen_key() == "listen-key"
    method, _, kwargs = session.calls[0]
    assert method == "POST"
    assert kwargs["headers"] == {"X-BX-APIKEY": API_KEY}


@pytest.mark.asyncio
async def test_async_bingx_listen_key_raises_for_api_error() -> None:
    from dcex.async_support.bingx._account_http import AccountHTTP

    client = AccountHTTP(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    client.session = _AsyncCaptureSession(payload={"code": 100001, "msg": "invalid api key"})

    with pytest.raises(FailedRequestError, match="100001"):
        await client.get_listen_key()


def _sync_header_cases() -> list[tuple[str, object, dict[str, Any]]]:
    from dcex.aster.endpoints.market import SpotMarket as AsterSpotMarket
    from dcex.binance.endpoints.market import SpotMarket
    from dcex.bitmart.endpoints.market import SpotMarket as BitmartSpotMarket

    return [
        (
            "dcex.aster._http_manager",
            AsterSpotMarket.SERVER_TIME,
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.backpack._http_manager",
            "/api/v1/time",
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.binance._http_manager",
            SpotMarket.SERVER_TIME,
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.bingx._http_manager",
            "/openApi/swap/v2/quote/ticker",
            {"payload": {"code": 0}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.bitget._http_manager",
            "/api/v2/spot/public/symbols",
            {"payload": {"code": "00000", "data": []}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.bitmart._http_manager",
            BitmartSpotMarket.GET_TRADING_PAIRS_DETAILS,
            {"payload": {"code": 1000}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.bitmex._http_manager",
            "/api/v1/instrument",
            {"payload": {"ok": True}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.bybit._http_manager",
            "/v5/market/time",
            {"payload": {"retCode": 0}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.gateio._http_manager",
            "/spot/currencies",
            {"payload": {"ok": True}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.hyperliquid._http_manager",
            "/info",
            {"method": "POST", "payload": {"ok": True}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.kucoin._http_manager",
            "/api/v1/timestamp",
            {"payload": {"code": "200000", "data": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.kraken._http_manager",
            "/0/public/Time",
            {"payload": {"error": [], "result": {"unixtime": 1}}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.mexc._http_manager",
            "/api/v3/time",
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.okx._http_manager",
            "/api/v5/public/time",
            {"payload": {"code": "0", "data": []}, "kwargs": {"signed": False}},
        ),
    ]


def _async_header_cases() -> list[tuple[str, object, dict[str, Any]]]:
    from dcex.async_support.aster.endpoints.market import (
        SpotMarket as AsyncAsterSpotMarket,
    )
    from dcex.async_support.binance.endpoints.market import SpotMarket
    from dcex.async_support.bitmart.endpoints.market import (
        SpotMarket as AsyncBitmartSpotMarket,
    )

    return [
        (
            "dcex.async_support.aster._http_manager",
            AsyncAsterSpotMarket.SERVER_TIME,
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.backpack._http_manager",
            "/api/v1/time",
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.binance._http_manager",
            SpotMarket.SERVER_TIME,
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.bingx._http_manager",
            "/openApi/swap/v2/quote/ticker",
            {"payload": {"code": 0}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.bitget._http_manager",
            "/api/v2/spot/public/symbols",
            {"payload": {"code": "00000", "data": []}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.bitmart._http_manager",
            AsyncBitmartSpotMarket.GET_TRADING_PAIRS_DETAILS,
            {"payload": {"code": 1000}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.bitmex._http_manager",
            "/api/v1/instrument",
            {"payload": {"ok": True}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.bybit._http_manager",
            "/v5/market/time",
            {
                "attrs": {"endpoint": "https://api.bybit.com"},
                "payload": {"retCode": 0},
                "kwargs": {"signed": False},
            },
        ),
        (
            "dcex.async_support.gateio._http_manager",
            "/spot/currencies",
            {"payload": {"ok": True}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.hyperliquid._http_manager",
            "/info",
            {
                "attrs": {"endpoint": "https://api.hyperliquid.xyz"},
                "method": "POST",
                "payload": {"ok": True},
                "kwargs": {"signed": False},
            },
        ),
        (
            "dcex.async_support.kucoin._http_manager",
            "/api/v1/timestamp",
            {"payload": {"code": "200000", "data": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.kraken._http_manager",
            "/0/public/Time",
            {"payload": {"error": [], "result": {"unixtime": 1}}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.mexc._http_manager",
            "/api/v3/time",
            {"payload": {"serverTime": 1}, "kwargs": {"signed": False}},
        ),
        (
            "dcex.async_support.okx._http_manager",
            "/api/v5/public/time",
            {"payload": {"code": "0", "data": []}, "kwargs": {"signed": False}},
        ),
    ]


@pytest.mark.parametrize(
    ("module_name", "path", "case"),
    _sync_header_cases(),
    ids=[
        case[0].removeprefix("dcex.").replace("._http_manager", "") for case in _sync_header_cases()
    ],
)
def test_sync_http_managers_store_last_response_headers(
    module_name: str,
    path: object,
    case: dict[str, Any],
) -> None:
    headers = {"x-test-rate-limit": "42"}
    module = import_module(module_name)
    manager = module.HTTPManager(preload_product_table=False)
    for name, value in case.get("attrs", {}).items():
        setattr(manager, name, value)
    manager.session = _CaptureSession(case["payload"], headers=headers)

    manager._request(case.get("method", "GET"), path, **case.get("kwargs", {}))

    assert manager.last_response_headers == headers


@pytest.mark.parametrize(
    ("module_name", "path", "case"),
    _async_header_cases(),
    ids=[
        case[0].removeprefix("dcex.async_support.").replace("._http_manager", "")
        for case in _async_header_cases()
    ],
)
@pytest.mark.asyncio
async def test_async_http_managers_store_last_response_headers(
    module_name: str,
    path: object,
    case: dict[str, Any],
) -> None:
    headers = {"x-test-rate-limit": "42"}
    module = import_module(module_name)
    manager = module.HTTPManager(preload_product_table=False)
    for name, value in case.get("attrs", {}).items():
        setattr(manager, name, value)
    manager.session = _AsyncCaptureSession(case["payload"], headers=headers)

    await manager._request(case.get("method", "GET"), path, **case.get("kwargs", {}))

    assert manager.last_response_headers == headers


def _gateio_expected_signature(query_string: str) -> str:
    hashed_payload = hashlib.sha512(b"").hexdigest()
    canonical = f"GET\n/api/v4/futures/orders\n{query_string}\n{hashed_payload}\n{TS_S}"
    return hmac.new(API_SECRET.encode(), canonical.encode(), hashlib.sha512).hexdigest()


def _gateio_expected_signature_for(
    method: str,
    path: str,
    query_string: str,
    payload: bytes = b"",
) -> str:
    hashed_payload = hashlib.sha512(payload).hexdigest()
    canonical = f"{method}\n{path}\n{query_string}\n{hashed_payload}\n{TS_S}"
    return hmac.new(API_SECRET.encode(), canonical.encode(), hashlib.sha512).hexdigest()


def _mexc_contract_expected_signature(request_time: str, payload: str) -> str:
    canonical = f"{API_KEY}{request_time}{payload}"
    return hmac.new(API_SECRET.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def _backpack_secret() -> str:
    return base64.b64encode(b"1" * 32).decode()


def _backpack_key() -> str:
    return base64.b64encode(b"2" * 32).decode()


def _backpack_expected_signature(message: str) -> str:
    key = ECC.construct(curve="Ed25519", seed=b"1" * 32)
    signature = eddsa.new(key, "rfc8032").sign(message.encode())
    return base64.b64encode(signature).decode()


__all__ = [name for name in globals() if not name.startswith("test_") and not name.startswith("__")]
