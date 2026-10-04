"""Public-endpoint fixes found by the live public smoke run (scripts/live/smoke_public.py)."""

# ruff: noqa: D103
from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server

native = pytest.importorskip("dcex._native")


def _requests(received: Any) -> list[dict[str, Any]]:  # noqa: ANN401
    requests = []
    while not received.empty():
        item = received.get_nowait()
        if not urlsplit(item["path"]).path.endswith("/time"):
            requests.append(item)
    return requests


def _binance(base: str, api_key: str | None = "api-key") -> Any:  # noqa: ANN401
    return native.BinanceHttpClient(
        api_key=api_key,
        api_secret="secret" if api_key else None,
        timeout=10,
        spot_base_url=base,
        futures_base_url=base,
    )


@pytest.mark.parametrize(
    "method",
    [
        "acquiring_algorithm",
        "acquiring_coinname",
        "prediction_list_prediction_categories",
        "prediction_list_prediction_markets",
    ],
)
def test_binance_market_data_catalog_sends_api_key_without_signature(method: str) -> None:
    # Live: these MARKET_DATA routes answer -2014 without the X-MBX-APIKEY header.
    with _http_server({"code": 0, "data": []}) as (base, received):
        _binance(base).public_request_json(method, [])
        requests = _requests(received)
    assert len(requests) == 1
    assert requests[0]["api_key"] == "api-key"
    assert "signature" not in dict(parse_qsl(urlsplit(requests[0]["path"]).query))


def test_binance_market_data_catalog_requires_api_key_before_sending() -> None:
    with _http_server() as (base, received):
        with pytest.raises(ValueError, match="API key is required"):
            _binance(base, api_key=None).public_request_json("acquiring_algorithm", [])
        assert _requests(received) == []


def _bitget(base: str) -> Any:  # noqa: ANN401
    return native.BitgetHttpClient(
        api_key="api-key", api_secret="secret", passphrase="pass", timeout=10, base_url=base
    )


KLINE = [("category", "USDT-FUTURES"), ("product_symbol", "BTCUSDT"), ("limit", "2")]


@pytest.mark.parametrize("method", ["get_uta_kline", "get_uta_history_kline"])
@pytest.mark.parametrize("interval", ["1h", "1d", "60"])
def test_bitget_uta_kline_rejects_intervals_the_exchange_refuses(
    method: str, interval: str
) -> None:
    with _http_server() as (base, received):
        with pytest.raises(ValueError, match="invalid Bitget UTA interval"):
            _bitget(base).public_request_json(method, [*KLINE, ("interval", interval)])
        assert _requests(received) == []


@pytest.mark.parametrize("interval", ["1m", "1H", "2H", "1D", "3D", "1W", "1M"])
def test_bitget_uta_kline_sends_live_verified_intervals(interval: str) -> None:
    with _http_server({"code": "00000", "data": []}) as (base, received):
        _bitget(base).public_request_json("get_uta_kline", [*KLINE, ("interval", interval)])
        requests = _requests(received)
    assert dict(parse_qsl(urlsplit(requests[0]["path"]).query))["interval"] == interval


@pytest.mark.parametrize("mode", ["dcex", "dcex.async_support"])
@pytest.mark.parametrize(
    "method", ["get_classic_convert_currencies", "get_classic_interest_rate_record"]
)
def test_bitget_classic_routes_rejected_for_uta_are_removed(mode: str, method: str) -> None:
    # Live: both answer 40085 for Unified Trading Accounts.
    client = pytest.importorskip(f"{mode}.bitget.client").Client
    assert not hasattr(client, method)


@pytest.mark.parametrize(
    ("factory", "method"),
    [
        (lambda base: _bitget(base), "get_classic_convert_currencies"),
        (
            lambda base: native.KucoinHttpClient(
                api_key="api-key", api_secret="secret", passphrase="pass", timeout=10, spot_base_url=base, futures_base_url=base
            ),
            "get_futures_24h_statistics",
        ),
        (
            lambda base: native.OkxHttpClient(
                api_key="api-key",
                api_secret="secret",
                passphrase="pass",
                flag="1",
                timeout=10,
                base_url=base,
            ),
            "get_economic_calendar",
        ),
    ],
)
def test_authenticated_routes_are_not_reachable_as_public(factory: Any, method: str) -> None:  # noqa: ANN401
    with _http_server() as (base, received):
        with pytest.raises(ValueError):
            factory(base).public_request_json(method, [])
        assert _requests(received) == []


@pytest.mark.parametrize("mode", ["dcex", "dcex.async_support"])
@pytest.mark.parametrize(
    ("exchange", "method"),
    [("kucoin", "get_futures_24h_statistics"), ("okx", "get_economic_calendar")],
)
def test_authenticated_routes_use_the_private_helper(mode: str, exchange: str, method: str) -> None:
    import inspect

    client = pytest.importorskip(f"{mode}.{exchange}.client").Client
    source = inspect.getsource(getattr(client, method))
    assert "_native_private(" in source and "_native_public(" not in source
