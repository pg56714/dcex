"""Offline tests for Bybit endpoint parameter handling."""
# ruff: noqa: D103

import inspect
from typing import Any, Protocol

import pytest


class _RequestManager(Protocol):
    _native_client: Any


def _capture_sync_public_request(manager: _RequestManager) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    class NativeClient:
        def public_request_json(
            self,
            method_name: str,
            params: list[tuple[str, str]],
        ) -> tuple[int, dict[str, str], object]:
            captured.update({"method_name": method_name, "params": params})
            return 200, {}, {}

    manager._native_client = NativeClient()
    return captured


def _capture_async_public_request(manager: _RequestManager) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    class NativeClient:
        async def public_request_json_async(
            self,
            method_name: str,
            params: list[tuple[str, str]],
        ) -> tuple[int, dict[str, str], object]:
            captured.update({"method_name": method_name, "params": params})
            return 200, {}, {}

    manager._native_client = NativeClient()
    return captured


def _capture_sync_private_request(manager: _RequestManager) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    class NativeClient:
        def private_request_json(
            self,
            method_name: str,
            params: list[tuple[str, str]],
        ) -> tuple[int, dict[str, str], object]:
            captured.update({"method_name": method_name, "params": params})
            return 200, {}, {}

    manager._native_client = NativeClient()
    return captured


def _capture_async_private_request(manager: _RequestManager) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    class NativeClient:
        async def private_request_json_async(
            self,
            method_name: str,
            params: list[tuple[str, str]],
        ) -> tuple[int, dict[str, str], object]:
            captured.update({"method_name": method_name, "params": params})
            return 200, {}, {}

    manager._native_client = NativeClient()
    return captured


def test_sync_bybit_risk_limit_sends_cursor() -> None:
    from dcex.bybit._market_http import MarketHTTP

    manager = MarketHTTP(preload_product_table=False)
    captured = _capture_sync_public_request(manager)

    manager.get_risk_limit(cursor="next-page")

    assert captured["method_name"] == "get_risk_limit"
    assert captured["params"] == [("category", "linear"), ("cursor", "next-page")]


@pytest.mark.asyncio
async def test_async_bybit_risk_limit_sends_cursor() -> None:
    from dcex.async_support.bybit._market_http import MarketHTTP

    manager = MarketHTTP(preload_product_table=False)
    captured = _capture_async_public_request(manager)

    await manager.get_risk_limit(cursor="next-page")

    assert captured["method_name"] == "get_risk_limit"
    assert captured["params"] == [("category", "linear"), ("cursor", "next-page")]


def test_sync_bybit_transferable_amount_validates_and_sends_coins() -> None:
    from dcex.bybit._account_http import AccountHTTP

    manager = AccountHTTP(preload_product_table=False)
    captured = _capture_sync_private_request(manager)

    manager.get_transferable_amount(["BTC", "ETH"])
    assert captured["method_name"] == "get_transferable_amount"
    assert captured["params"] == [("coins", "BTC,ETH")]

    with pytest.raises(ValueError, match="at least one"):
        manager.get_transferable_amount([])
    with pytest.raises(ValueError, match="no more than 20"):
        manager.get_transferable_amount(["BTC"] * 21)


@pytest.mark.asyncio
async def test_async_bybit_transferable_amount_validates_and_sends_coins() -> None:
    from dcex.async_support.bybit._account_http import AccountHTTP

    manager = AccountHTTP(preload_product_table=False)
    captured = _capture_async_private_request(manager)

    await manager.get_transferable_amount(["BTC", "ETH"])
    assert captured["method_name"] == "get_transferable_amount"
    assert captured["params"] == [("coins", "BTC,ETH")]

    with pytest.raises(ValueError, match="at least one"):
        await manager.get_transferable_amount([])
    with pytest.raises(ValueError, match="no more than 20"):
        await manager.get_transferable_amount(["BTC"] * 21)


def test_bybit_post_only_order_has_consistent_sync_and_async_parameters() -> None:
    from dcex.async_support.bybit._trade_http import TradeHTTP as AsyncTradeHTTP
    from dcex.bybit._trade_http import TradeHTTP

    sync_parameters = inspect.signature(TradeHTTP.place_post_only_limit_order).parameters
    async_parameters = inspect.signature(AsyncTradeHTTP.place_post_only_limit_order).parameters

    assert tuple(sync_parameters) == tuple(async_parameters)
    assert "timeInForce" not in sync_parameters


def test_sync_bybit_post_only_order_forces_post_only() -> None:
    from dcex.bybit._trade_http import TradeHTTP

    manager = TradeHTTP(preload_product_table=False)
    captured = _capture_sync_private_request(manager)
    manager.place_post_only_limit_order("BTC-USDT-SPOT", "Buy", "0.001", "100")

    assert captured["method_name"] == "place_post_only_limit_order"
    assert captured["params"] == [
        ("product_symbol", "BTC-USDT-SPOT"),
        ("side", "Buy"),
        ("qty", "0.001"),
        ("price", "100"),
    ]


@pytest.mark.parametrize(
    ("method_name", "expected_fields"),
    [
        (
            "place_order",
            {
                "rpiTakerAccess",
                "slippageToleranceType",
                "slippageTolerance",
                "orderLinkId",
                "smpType",
                "mmp",
                "bboSideType",
                "bboLevel",
            },
        ),
        (
            "get_open_orders",
            {"orderId", "orderLinkId", "openOnly", "orderFilter", "cursor"},
        ),
        (
            "get_order_history",
            {
                "baseCoin",
                "settleCoin",
                "orderLinkId",
                "orderFilter",
                "orderStatus",
                "endTime",
                "cursor",
            },
        ),
        (
            "get_execution_list",
            {
                "orderId",
                "orderLinkId",
                "baseCoin",
                "settleCoin",
                "endTime",
                "execType",
                "cursor",
            },
        ),
    ],
)
def test_bybit_trade_methods_expose_current_official_fields(
    method_name: str, expected_fields: set[str]
) -> None:
    from dcex.async_support.bybit._trade_http import TradeHTTP as AsyncTradeHTTP
    from dcex.bybit._trade_http import TradeHTTP

    sync_fields = set(inspect.signature(getattr(TradeHTTP, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(AsyncTradeHTTP, method_name)).parameters)

    assert expected_fields <= sync_fields
    assert sync_fields == async_fields


def test_sync_bybit_place_order_serializes_boolean_params_lowercase() -> None:
    from dcex.bybit._trade_http import TradeHTTP

    manager = TradeHTTP(preload_product_table=False)
    captured = _capture_sync_private_request(manager)
    manager.place_order(
        "BTC-USDT-SWAP",
        "Buy",
        "Market",
        "1",
        reduceOnly=True,
        closeOnTrigger=False,
        rpiTakerAccess=True,
        mmp=False,
        orderLinkId="client-order",
        bboLevel=3,
    )

    params = dict(captured["params"])
    assert params["reduceOnly"] == "true"
    assert params["closeOnTrigger"] == "false"
    assert params["rpiTakerAccess"] == "true"
    assert params["mmp"] == "false"
    assert params["orderLinkId"] == "client-order"
    assert params["bboLevel"] == "3"


def test_sync_bybit_current_market_and_asset_fields_are_forwarded() -> None:
    from dcex.bybit._asset_http import AssetHTTP
    from dcex.bybit._market_http import MarketHTTP

    market = MarketHTTP(preload_product_table=False)
    market_capture = _capture_sync_public_request(market)
    market.get_kline("BTC-USDT-SPOT", "1m", startTime=100, endTime=200)
    assert dict(market_capture["params"])["endTime"] == "200"

    asset = AssetHTTP(preload_product_table=False)
    asset_capture = _capture_sync_private_request(asset)
    asset.get_internal_transfer_records(
        transferId="transfer-id",
        status="SUCCESS",
        endTime=200,
        cursor="next-page",
    )
    assert dict(asset_capture["params"]) == {
        "transferId": "transfer-id",
        "status": "SUCCESS",
        "endTime": "200",
        "limit": "20",
        "cursor": "next-page",
    }
