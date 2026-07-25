"""Regression coverage for the current Aster V3 REST surface."""

# ruff: noqa: D103

from __future__ import annotations

import inspect

import pytest

from tests.unit.native_http_helpers import _http_server


@pytest.mark.parametrize(
    ("method_name", "expected", "absent"),
    [
        ("get_futures_mmp", {"product_symbol"}, set()),
        (
            "place_futures_chase_order",
            {
                "product_symbol",
                "side",
                "quantityUnit",
                "quantity",
                "chaseOffset",
                "chaseOffsetType",
                "maxChaseOffset",
                "maxChaseOffsetType",
            },
            {"priceLimit"},
        ),
        (
            "place_futures_strategy_order",
            {"strategyType", "subOrderList", "clientStrategyId", "builder", "feeRate"},
            set(),
        ),
    ],
)
def test_aster_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str], absent: set[str]
) -> None:
    from dcex.aster.client import Client as SyncClient
    from dcex.async_support.aster.client import Client as AsyncClient

    sync_fields = set(inspect.signature(getattr(SyncClient, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(AsyncClient, method_name)).parameters)
    assert expected <= sync_fields
    assert absent.isdisjoint(sync_fields)
    assert sync_fields == async_fields


def test_aster_spot_exchange_info_has_no_documented_query_parameters() -> None:
    from dcex.aster.client import Client

    assert list(inspect.signature(Client.get_spot_exchange_info).parameters) == ["self"]


def _native_client(
    *, spot_url: str = "http://127.0.0.1:1", futures_url: str | None = None
) -> object:
    native = pytest.importorskip("dcex._native")
    return native.AsterHttpClient(
        timeout=2,
        spot_base_url=spot_url,
        futures_base_url=futures_url or spot_url,
    )


def test_aster_current_exchange_info_wire_format() -> None:
    with _http_server({"timezone": "UTC", "symbols": []}) as (base_url, received):
        client = _native_client(spot_url=base_url)
        client.public_request_json("get_spot_exchange_info", None)

    assert received.get_nowait()["path"] == "/api/v3/exchangeInfo"


def test_aster_rejects_stale_or_invalid_current_parameters_before_transport() -> None:
    public = _native_client()
    with pytest.raises(ValueError, match="unsupported Aster parameter"):
        public.public_request_json(
            "get_spot_exchange_info",
            [("symbol", "BTCUSDT")],
        )

    private = _native_client()
    with pytest.raises(ValueError, match="unsupported Aster parameter"):
        private.private_request_json(
            "place_futures_chase_order",
            [
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("quantityUnit", "COIN"),
                ("quantity", "0.001"),
                ("priceLimit", "100000"),
            ],
        )
    with pytest.raises(ValueError, match="exactly 2"):
        private.private_request_json(
            "place_futures_strategy_order",
            [("strategyType", "OTO"), ("subOrderList", "[]")],
        )
    with pytest.raises(ValueError, match="exactly one"):
        private.private_request_json(
            "get_futures_strategy_open_order",
            [
                ("strategyType", "GRID"),
                ("strategyId", "1"),
                ("clientStrategyId", "client-1"),
            ],
        )
