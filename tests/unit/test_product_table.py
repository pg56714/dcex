"""Offline unit tests for ProductTableManager query logic.

These build a manager from a hand-made DataFrame (no network, no fetch) and
exercise the pure query/index methods. They pin the lookup behaviour so the
query logic can be refactored (e.g. shared between sync and async) safely.
"""

import polars as pl
import pytest

from dcex.product_table.manager import ProductTableManager, ProductTableError
from dcex.async_support.product_table.manager import (
    ProductTableManager as AsyncProductTableManager,
)

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


def test_failed_sync_initialization_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    key = "broken-sync"
    ProductTableManager._instance.pop(key, None)

    def fail_initialize(self: ProductTableManager, exchange_name: str | None = None) -> None:
        raise ProductTableError("boom")

    monkeypatch.setattr(ProductTableManager, "_initialize", fail_initialize)

    with pytest.raises(ProductTableError, match="boom"):
        ProductTableManager.get_instance(key)

    assert key not in ProductTableManager._instance


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
