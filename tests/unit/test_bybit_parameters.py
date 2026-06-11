"""Offline tests for Bybit endpoint parameter handling."""
# ruff: noqa: D103

from typing import Any, Protocol

import pytest


class _RequestManager(Protocol):
    _request: Any


def _capture_sync_request(manager: _RequestManager) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def fake_request(
        method: str,
        path: object,
        query: dict[str, Any] | None = None,
        **kwargs: object,
    ) -> dict[str, Any]:
        captured.update({"method": method, "path": path, "query": query, **kwargs})
        return {}

    manager._request = fake_request
    return captured


def _capture_async_request(manager: _RequestManager) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    async def fake_request(
        method: str,
        path: object,
        query: dict[str, Any] | None = None,
        **kwargs: object,
    ) -> dict[str, Any]:
        captured.update({"method": method, "path": path, "query": query, **kwargs})
        return {}

    manager._request = fake_request
    return captured


def test_sync_bybit_risk_limit_sends_cursor() -> None:
    from dcex.bybit._market_http import MarketHTTP

    manager = MarketHTTP(preload_product_table=False)
    captured = _capture_sync_request(manager)

    manager.get_risk_limit(cursor="next-page")

    assert captured["query"] == {"category": "linear", "cursor": "next-page"}


@pytest.mark.asyncio
async def test_async_bybit_risk_limit_sends_cursor() -> None:
    from dcex.async_support.bybit._market_http import MarketHTTP

    manager = MarketHTTP(preload_product_table=False)
    captured = _capture_async_request(manager)

    await manager.get_risk_limit(cursor="next-page")

    assert captured["query"] == {"category": "linear", "cursor": "next-page"}


def test_sync_bybit_transferable_amount_validates_and_sends_coins() -> None:
    from dcex.bybit._account_http import AccountHTTP

    manager = AccountHTTP(preload_product_table=False)
    captured = _capture_sync_request(manager)

    manager.get_transferable_amount(["BTC", "ETH"])
    assert captured["query"] == {"coinName": "BTC,ETH"}

    with pytest.raises(ValueError, match="at least one"):
        manager.get_transferable_amount([])
    with pytest.raises(ValueError, match="no more than 20"):
        manager.get_transferable_amount(["BTC"] * 21)


@pytest.mark.asyncio
async def test_async_bybit_transferable_amount_validates_and_sends_coins() -> None:
    from dcex.async_support.bybit._account_http import AccountHTTP

    manager = AccountHTTP(preload_product_table=False)
    captured = _capture_async_request(manager)

    await manager.get_transferable_amount(["BTC", "ETH"])
    assert captured["query"] == {"coinName": "BTC,ETH"}

    with pytest.raises(ValueError, match="at least one"):
        await manager.get_transferable_amount([])
    with pytest.raises(ValueError, match="no more than 20"):
        await manager.get_transferable_amount(["BTC"] * 21)
