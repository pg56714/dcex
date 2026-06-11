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


class _AsyncBadJsonSession(_AsyncCaptureSession):
    def _response(self) -> _FakeResponse:
        return _BadJsonResponse(self.status_code)


def _sync_header_cases() -> list[tuple[str, object, dict[str, Any]]]:
    from dcex.binance.endpoints.market import SpotMarket
    from dcex.bitmart.endpoints.market import SpotMarket as BitmartSpotMarket

    return [
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
    from dcex.async_support.binance.endpoints.market import SpotMarket
    from dcex.async_support.bitmart.endpoints.market import (
        SpotMarket as AsyncBitmartSpotMarket,
    )

    return [
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


def test_sync_backpack_signed_query_matches_docs(monkeypatch: pytest.MonkeyPatch) -> None:
    from dcex.backpack._http_manager import HTTPManager

    backpack_http = import_module("dcex.backpack._http_manager")
    monkeypatch.setattr(backpack_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({})
    manager = HTTPManager(
        api_key=_backpack_key(),
        api_secret=_backpack_secret(),
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    manager._request(
        "GET",
        "/api/v1/order",
        {"symbol": "BTC_USDC", "orderId": "test-order-id"},
        signed=True,
        instruction="orderQuery",
    )

    method, url, kwargs = session.calls[0]
    message = (
        "instruction=orderQuery&orderId=test-order-id&symbol=BTC_USDC"
        f"&timestamp={int(TS_S) * 1000}&window=5000"
    )
    assert method == "GET"
    assert url == "https://api.backpack.exchange/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
    assert kwargs["headers"]["X-API-Key"] == _backpack_key()
    assert kwargs["headers"]["X-Timestamp"] == str(int(TS_S) * 1000)
    assert kwargs["headers"]["X-Window"] == "5000"
    assert kwargs["headers"]["X-Signature"] == _backpack_expected_signature(message)


@pytest.mark.asyncio
async def test_async_backpack_signed_query_matches_docs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.backpack._http_manager import HTTPManager

    backpack_http = import_module("dcex.async_support.backpack._http_manager")
    monkeypatch.setattr(backpack_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        api_key=_backpack_key(),
        api_secret=_backpack_secret(),
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    await manager._request(
        "GET",
        "/api/v1/order",
        {"symbol": "BTC_USDC", "orderId": "test-order-id"},
        signed=True,
        instruction="orderQuery",
    )

    method, url, kwargs = session.calls[0]
    message = (
        "instruction=orderQuery&orderId=test-order-id&symbol=BTC_USDC"
        f"&timestamp={int(TS_S) * 1000}&window=5000"
    )
    assert method == "GET"
    assert url == "https://api.backpack.exchange/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
    assert kwargs["headers"]["X-API-Key"] == _backpack_key()
    assert kwargs["headers"]["X-Timestamp"] == str(int(TS_S) * 1000)
    assert kwargs["headers"]["X-Window"] == "5000"
    assert kwargs["headers"]["X-Signature"] == _backpack_expected_signature(message)


def test_gateio_signed_query_order_matches_sent_params(monkeypatch: pytest.MonkeyPatch) -> None:
    from dcex.gateio._http_manager import HTTPManager

    gateio_http = import_module("dcex.gateio._http_manager")
    monkeypatch.setattr(gateio_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        timeout=7,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    query = {"contract": "BTC_USD", "status": "finished", "limit": 50}

    manager._request("GET", "/futures/orders", query=query, signed=True)

    method, _url, kwargs = session.calls[0]
    query_string = "contract=BTC_USD&status=finished&limit=50"
    assert method == "GET"
    assert kwargs["params"] == query_string
    assert kwargs["timeout"] == 7
    assert kwargs["headers"]["SIGN"] == _gateio_expected_signature(query_string)


def test_sync_gateio_json_decode_failure_is_failed_request() -> None:
    from dcex.gateio._http_manager import HTTPManager

    manager = HTTPManager(preload_product_table=False)
    manager.session = _BadJsonSession()  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Failed to decode JSON response") as exc_info:
        manager._request("GET", "/spot/currencies", signed=False)

    assert exc_info.value.status_code == 200
    assert exc_info.value.resp_headers == {}


def test_sync_mexc_contract_list_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.mexc._http_manager import HTTPManager

    mexc_http = import_module("dcex.mexc._http_manager")
    monkeypatch.setattr(mexc_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({"success": True, "code": 0})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    manager._request(
        "POST",
        "/api/v1/private/order/cancel",
        [{"orderId": "test-order-id"}],
        api="contract",
    )

    method, url, kwargs = session.calls[0]
    request_time = str(int(int(TS_S) * 1000))
    body = '[{"orderId":"test-order-id"}]'
    assert method == "POST"
    assert url == "https://api.mexc.com/api/v1/private/order/cancel"
    assert kwargs["data"] == body
    assert kwargs["headers"]["Request-Time"] == request_time
    assert kwargs["headers"]["Signature"] == _mexc_contract_expected_signature(
        request_time,
        body,
    )


@pytest.mark.asyncio
async def test_async_gateio_signed_query_order_matches_sent_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    gateio_http = import_module("dcex.async_support.gateio._http_manager")
    monkeypatch.setattr(gateio_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    query = {"contract": "BTC_USD", "status": "finished", "limit": 50}

    await manager._request("GET", "/futures/orders", query=query, signed=True)

    method, _url, kwargs = session.calls[0]
    query_string = "contract=BTC_USD&status=finished&limit=50"
    assert method == "GET"
    assert kwargs["params"] == query_string
    assert kwargs["headers"]["SIGN"] == _gateio_expected_signature(query_string)


@pytest.mark.asyncio
async def test_async_gateio_empty_post_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    gateio_http = import_module("dcex.async_support.gateio._http_manager")
    monkeypatch.setattr(gateio_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    query = {"leverage": "10"}

    await manager._request(
        "POST",
        "/futures/{settle}/positions/{contract}/leverage",
        path_params={"settle": "usdt", "contract": "BTC_USDT"},
        query=query,
        signed=True,
    )

    method, _url, kwargs = session.calls[0]
    query_string = "leverage=10"
    assert method == "POST"
    assert kwargs["params"] == query_string
    assert kwargs["content"] is None
    assert kwargs["headers"]["SIGN"] == _gateio_expected_signature_for(
        "POST",
        "/api/v4/futures/usdt/positions/BTC_USDT/leverage",
        query_string,
    )


@pytest.mark.asyncio
async def test_async_gateio_json_decode_failure_is_failed_request() -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    manager = HTTPManager(preload_product_table=False)
    manager.session = _AsyncBadJsonSession()  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Failed to decode JSON response") as exc_info:
        await manager._request("GET", "/spot/currencies", signed=False)

    assert exc_info.value.status_code == 200
    assert exc_info.value.resp_headers == {}


@pytest.mark.asyncio
async def test_async_mexc_contract_list_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.mexc._http_manager import HTTPManager

    mexc_http = import_module("dcex.async_support.mexc._http_manager")
    monkeypatch.setattr(mexc_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({"success": True, "code": 0})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    await manager._request(
        "POST",
        "/api/v1/private/order/cancel",
        [{"orderId": "test-order-id"}],
        api="contract",
    )

    method, url, kwargs = session.calls[0]
    request_time = str(int(int(TS_S) * 1000))
    body = '[{"orderId":"test-order-id"}]'
    assert method == "POST"
    assert url == "https://api.mexc.com/api/v1/private/order/cancel"
    assert kwargs["content"] == body
    assert kwargs["headers"]["Request-Time"] == request_time
    assert kwargs["headers"]["Signature"] == _mexc_contract_expected_signature(
        request_time,
        body,
    )


def test_sync_bitmex_passes_configured_timeout() -> None:
    from dcex.bitmex._http_manager import HTTPManager

    session = _CaptureSession({})
    manager = HTTPManager(timeout=7, preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    manager._request("GET", "/api/v1/instrument", signed=False)

    assert session.calls[0][2]["timeout"] == 7


def test_sync_okx_defaults_to_openapi_domain_and_passes_timeout() -> None:
    from dcex.okx._http_manager import HTTPManager

    session = _CaptureSession({"code": "0", "data": []})
    manager = HTTPManager(timeout=7, preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    manager._request("GET", "/api/v5/public/time", signed=False)

    method, url, kwargs = session.calls[0]
    assert method == "GET"
    assert url == "https://openapi.okx.com/api/v5/public/time"
    assert kwargs["timeout"] == 7


def test_sync_okx_error_with_empty_data_uses_top_level_message() -> None:
    from dcex.okx._http_manager import HTTPManager

    session = _CaptureSession(
        {"code": "51000", "msg": "Parameter error", "data": []},
        status_code=400,
    )
    manager = HTTPManager(preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Parameter error") as exc_info:
        manager._request("GET", "/api/v5/account/balance", {"ccy": "BTC"}, signed=False)

    assert "51000" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_okx_error_with_empty_data_uses_top_level_message() -> None:
    from dcex.async_support.okx._http_manager import HTTPManager

    session = _AsyncCaptureSession(
        {"code": "51000", "msg": "Parameter error", "data": []},
        status_code=400,
    )
    manager = HTTPManager(preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Parameter error") as exc_info:
        await manager._request("GET", "/api/v5/account/balance", {"ccy": "BTC"}, signed=False)

    assert manager.base_api == "https://openapi.okx.com"
    assert "51000" in str(exc_info.value)
