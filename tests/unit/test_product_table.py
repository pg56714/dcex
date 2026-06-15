"""
Offline unit tests for ProductTableManager query logic.

These build a manager from a hand-made DataFrame (no network, no fetch) and
exercise the pure query/index methods. They pin the lookup behaviour so the
query logic can be refactored (e.g. shared between sync and async) safely.
"""
# ruff: noqa: D103

import asyncio

import polars as pl
import pytest

from dcex.async_support.product_table import fetch as async_fetch
from dcex.async_support.product_table import manager as async_manager
from dcex.async_support.product_table.manager import (
    ProductTableManager as AsyncProductTableManager,
)
from dcex.product_table import fetch as sync_fetch
from dcex.product_table import manager as sync_manager
from dcex.product_table.manager import ProductTableError, ProductTableManager

# A tiny fixture table covering two exchanges and spot/swap rows.
_ROWS = [
    {
        "exchange": "binance",
        "product_symbol": "BTC-USDT-SPOT",
        "exchange_symbol": "BTCUSDT",
        "product_type": "spot",
        "exchange_type": "spot",
        "base_currency": "BTC",
        "quote_currency": "USDT",
        "price_precision": "0.01",
        "size_precision": "0.0001",
        "min_size": "0.0001",
        "min_notional": "10",
        "size_per_contract": "1",
    },
    {
        "exchange": "binance",
        "product_symbol": "BTC-USDT-SWAP",
        "exchange_symbol": "BTCUSDT",
        "product_type": "swap",
        "exchange_type": "PERPETUAL",
        "base_currency": "BTC",
        "quote_currency": "USDT",
        "price_precision": "0.1",
        "size_precision": "0.001",
        "min_size": "0.001",
        "min_notional": "5",
        "size_per_contract": "1",
    },
    {
        "exchange": "okx",
        "product_symbol": "ETH-USDT-SWAP",
        "exchange_symbol": "ETH-USDT-SWAP",
        "product_type": "swap",
        "exchange_type": "SWAP",
        "base_currency": "ETH",
        "quote_currency": "USDT",
        "price_precision": "0.01",
        "size_precision": "0.01",
        "min_size": "0.01",
        "min_notional": "1",
        "size_per_contract": "0.1",
    },
]


def _make_manager() -> ProductTableManager:
    """Build a manager from the fixture table without any network fetch."""
    manager = ProductTableManager()
    manager.product_table = pl.DataFrame(_ROWS)
    manager._build_indexes()
    return manager


def test_get_exchange_symbol() -> None:
    manager = _make_manager()
    assert manager.get_exchange_symbol("binance", "BTC-USDT-SPOT") == "BTCUSDT"
    assert manager.get_exchange_symbol("okx", "ETH-USDT-SWAP") == "ETH-USDT-SWAP"


def test_get_product_symbol_by_product_type() -> None:
    manager = _make_manager()
    # BTCUSDT exists as both spot and swap on binance; product_type disambiguates.
    assert manager.get_product_symbol("binance", "BTCUSDT", product_type="spot") == "BTC-USDT-SPOT"
    assert manager.get_product_symbol("binance", "BTCUSDT", product_type="swap") == "BTC-USDT-SWAP"


def test_get_product_symbol_by_exchange_type() -> None:
    manager = _make_manager()
    assert (
        manager.get_product_symbol("binance", "BTCUSDT", exchange_type="PERPETUAL")
        == "BTC-USDT-SWAP"
    )


def test_get_product_type() -> None:
    manager = _make_manager()
    assert manager.get_product_type("binance", product_symbol="BTC-USDT-SWAP") == "swap"
    assert manager.get_product_type("okx", product_symbol="ETH-USDT-SWAP") == "swap"


def test_get_exchange_type() -> None:
    manager = _make_manager()
    assert manager.get_exchange_type("binance", product_symbol="BTC-USDT-SWAP") == "PERPETUAL"


def test_get_base_and_quote_currency() -> None:
    manager = _make_manager()
    assert manager.get_base_currency("binance", "BTC-USDT-SPOT") == "BTC"
    assert manager.get_quote_currency("okx", "ETH-USDT-SWAP") == "USDT"


def test_get_trading_details() -> None:
    manager = _make_manager()
    details = manager.get_trading_details("binance", "BTC-USDT-SPOT")
    assert details["price_precision"] == "0.01"
    assert details["min_notional"] == "10"
    assert set(details) == {
        "price_precision",
        "size_precision",
        "min_size",
        "min_notional",
        "size_per_contract",
    }


def test_get_exchange_symbols_and_product_symbols() -> None:
    manager = _make_manager()
    assert set(manager.get_exchange_symbols("okx")) == {"ETH-USDT-SWAP"}
    assert set(manager.get_product_symbols("binance", product_type="spot")) == {"BTC-USDT-SPOT"}


def test_symbol_list_cache_cannot_be_modified_by_callers() -> None:
    manager = _make_manager()

    exchange_symbols = manager.get_exchange_symbols("binance")
    exchange_symbols.clear()
    assert set(manager.get_exchange_symbols("binance")) == {"BTCUSDT"}

    product_symbols = manager.get_product_symbols("binance")
    product_symbols.clear()
    assert set(manager.get_product_symbols("binance")) == {
        "BTC-USDT-SPOT",
        "BTC-USDT-SWAP",
    }


def test_missing_lookup_raises() -> None:
    manager = _make_manager()
    with pytest.raises(ProductTableError):
        manager.get_exchange_symbol("binance", "DOGE-USDT-SPOT")


def test_indexed_lookup_honors_all_filters() -> None:
    manager = _make_manager()

    with pytest.raises(ProductTableError):
        manager.get(
            "exchange_symbol",
            exchange="binance",
            product_symbol="BTC-USDT-SPOT",
            product_type="swap",
        )


def test_product_symbol_lookup_honors_product_and_exchange_types() -> None:
    manager = _make_manager()

    with pytest.raises(ProductTableError):
        manager.get_product_symbol(
            "binance",
            "BTCUSDT",
            product_type="spot",
            exchange_type="PERPETUAL",
        )


def test_indexed_lookup_preserves_ambiguous_results() -> None:
    manager = ProductTableManager()
    manager.product_table = pl.DataFrame(
        [
            {
                "exchange": "example",
                "product_symbol": "BTC-USD-2026-FUTURES",
                "exchange_symbol": "BTCUSD",
                "product_type": "futures",
                "exchange_type": "dated-2026",
            },
            {
                "exchange": "example",
                "product_symbol": "BTC-USD-2027-FUTURES",
                "exchange_symbol": "BTCUSD",
                "product_type": "futures",
                "exchange_type": "dated-2027",
            },
        ]
    )
    manager._build_indexes()

    with pytest.raises(ProductTableError, match="multiple"):
        manager.get_product_symbol(
            "example",
            "BTCUSD",
            product_type="futures",
        )

    assert (
        manager.get_product_symbol(
            "example",
            "BTCUSD",
            product_type="futures",
            exchange_type="dated-2026",
        )
        == "BTC-USD-2026-FUTURES"
    )


def test_all_product_fetches_match_the_registry() -> None:
    assert [function.__name__ for function in sync_manager.VALID_EXCHANGES] == [
        function.__name__ for function in async_manager.VALID_EXCHANGES
    ]
    assert {function.__name__ for function in sync_manager.VALID_EXCHANGES} == {
        "aster",
        "backpack",
        "binance",
        "bingx",
        "bitget",
        "bitmart",
        "bitmex",
        "bybit",
        "gateio",
        "hyperliquid",
        "kucoin",
        "kraken",
        "lighter",
        "mexc",
        "okx",
    }


def test_sync_fetch_delegates_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str | None] = []

    def fetch_product_table(exchange_name: str | None = None) -> list[dict[str, str]]:
        calls.append(exchange_name)
        return [_ROWS[0]]

    monkeypatch.setattr(sync_fetch._native, "fetch_product_table", fetch_product_table)

    assert sync_fetch.binance().to_dicts() == [_ROWS[0]]
    assert calls == ["binance"]


@pytest.mark.asyncio
async def test_async_fetch_delegates_to_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str | None] = []

    async def fetch_product_table_async(
        exchange_name: str | None = None,
    ) -> list[dict[str, str]]:
        calls.append(exchange_name)
        return [_ROWS[0]]

    monkeypatch.setattr(
        async_fetch._native,
        "fetch_product_table_async",
        fetch_product_table_async,
    )

    assert (await async_fetch.binance()).to_dicts() == [_ROWS[0]]
    assert calls == ["binance"]


def test_failed_sync_initialization_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    key = "binance"
    original = ProductTableManager._instance.pop(key, None)

    def fail_initialize(self: ProductTableManager, exchange_name: str | None = None) -> None:
        raise ProductTableError("boom")

    monkeypatch.setattr(ProductTableManager, "_initialize", fail_initialize)

    try:
        with pytest.raises(ProductTableError, match="boom"):
            ProductTableManager.get_instance(key)

        assert key not in ProductTableManager._instance
    finally:
        if original is not None:
            ProductTableManager._instance[key] = original


@pytest.mark.asyncio
async def test_failed_async_initialization_is_not_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    key = "binance"
    original = AsyncProductTableManager._instance.pop(key, None)

    async def fail_initialize(
        self: AsyncProductTableManager,
        exchange_name: str | None = None,
    ) -> None:
        raise ProductTableError("boom")

    monkeypatch.setattr(AsyncProductTableManager, "_initialize", fail_initialize)

    try:
        with pytest.raises(ProductTableError, match="boom"):
            await AsyncProductTableManager.get_instance(key)

        assert key not in AsyncProductTableManager._instance
    finally:
        if original is not None:
            AsyncProductTableManager._instance[key] = original


def test_sync_product_table_rejects_invalid_exchange_name() -> None:
    invalid_name = "invalid-exchange"

    with pytest.raises(ProductTableError, match="Invalid exchange_name"):
        ProductTableManager.get_instance(invalid_name)

    with pytest.raises(ProductTableError, match="Invalid exchange_name"):
        ProductTableManager().refresh(invalid_name)


@pytest.mark.asyncio
async def test_async_product_table_rejects_invalid_exchange_name() -> None:
    invalid_name = "invalid-exchange"

    with pytest.raises(ProductTableError, match="Invalid exchange_name"):
        await AsyncProductTableManager.get_instance(invalid_name)

    with pytest.raises(ProductTableError, match="Invalid exchange_name"):
        await AsyncProductTableManager().refresh(invalid_name)


def test_sync_manager_fetch_uses_rust_and_wraps_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str | None] = []

    def fetch_product_table(exchange_name: str | None = None) -> list[dict[str, str]]:
        calls.append(exchange_name)
        return [_ROWS[0]]

    monkeypatch.setattr(sync_manager._native, "fetch_product_table", fetch_product_table)
    result = ProductTableManager()._fetch_product_tables("binance")

    assert result.to_dicts() == [_ROWS[0]]
    assert calls == ["binance"]

    def fail_fetch(exchange_name: str | None = None) -> list[dict[str, str]]:
        raise RuntimeError(f"failed: {exchange_name}")

    monkeypatch.setattr(sync_manager._native, "fetch_product_table", fail_fetch)
    with pytest.raises(ProductTableError, match="failed: binance"):
        ProductTableManager()._fetch_product_tables("binance")


@pytest.mark.asyncio
async def test_async_manager_fetch_uses_rust_and_wraps_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str | None] = []

    async def fetch_product_table_async(
        exchange_name: str | None = None,
    ) -> list[dict[str, str]]:
        calls.append(exchange_name)
        return [_ROWS[0]]

    monkeypatch.setattr(
        async_manager._native,
        "fetch_product_table_async",
        fetch_product_table_async,
    )
    result = await AsyncProductTableManager()._fetch_product_tables("binance")

    assert result.to_dicts() == [_ROWS[0]]
    assert calls == ["binance"]

    async def fail_fetch(exchange_name: str | None = None) -> list[dict[str, str]]:
        raise RuntimeError(f"failed: {exchange_name}")

    monkeypatch.setattr(
        async_manager._native,
        "fetch_product_table_async",
        fail_fetch,
    )
    with pytest.raises(ProductTableError, match="failed: binance"):
        await AsyncProductTableManager()._fetch_product_tables("binance")


@pytest.mark.asyncio
async def test_async_product_table_propagates_exchange_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def cancelled(exchange_name: str | None = None) -> list[dict[str, str]]:
        raise asyncio.CancelledError

    monkeypatch.setattr(
        async_manager._native,
        "fetch_product_table_async",
        cancelled,
    )

    with pytest.raises(asyncio.CancelledError):
        await AsyncProductTableManager()._fetch_product_tables()
