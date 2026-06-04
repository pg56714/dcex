"""Offline request-path regression tests for HTTP managers."""

from __future__ import annotations

import hashlib
import hmac
from importlib import import_module
from typing import Any

import pytest

from dcex.utils.errors import FailedRequestError

API_KEY = "test_api_key_0000"
API_SECRET = "test_api_secret_0000"
TS_S = "1700000000"


class _FakeResponse:
    def __init__(self, payload: dict[str, Any] | None = None, status_code: int = 200) -> None:
        self._payload = payload or {}
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.text = str(self._payload)

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
    def __init__(self, payload: dict[str, Any] | None = None, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def _response(self) -> _FakeResponse:
        return _FakeResponse(self.payload, self.status_code)

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

    def __init__(self, payload: dict[str, Any] | None = None, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def _response(self) -> _FakeResponse:
        return _FakeResponse(self.payload, self.status_code)

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
