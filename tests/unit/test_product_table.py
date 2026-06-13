"""
Offline unit tests for ProductTableManager query logic.

These build a manager from a hand-made DataFrame (no network, no fetch) and
exercise the pure query/index methods. They pin the lookup behaviour so the
query logic can be refactored (e.g. shared between sync and async) safely.
"""
# ruff: noqa: D103

import asyncio
from typing import Any

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


def test_all_product_fetches_manage_market_clients() -> None:
    for fetch_function in sync_manager.VALID_EXCHANGES:
        assert hasattr(fetch_function, "__wrapped__"), fetch_function.__name__
    for fetch_function in async_manager.VALID_EXCHANGES:
        assert hasattr(fetch_function, "__wrapped__"), fetch_function.__name__


def test_market_http_rejects_unmanaged_creation_before_constructing_client() -> None:
    constructed = 0

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            nonlocal constructed
            constructed += 1

    with pytest.raises(RuntimeError, match="managed fetch"):
        sync_fetch._market_http(MarketHTTP)
    with pytest.raises(RuntimeError, match="managed fetch"):
        async_fetch._market_http(MarketHTTP)

    assert constructed == 0


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


def test_sync_product_fetch_closes_market_client_on_failure() -> None:
    created: list[Any] = []

    class Session:
        is_closed = False

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.session = Session()
            created.append(self)

        def close(self) -> None:
            self.session.is_closed = True

    @sync_fetch._manage_market_http
    def failing_fetch() -> pl.DataFrame:
        sync_fetch._market_http(MarketHTTP)
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        failing_fetch()

    assert len(created) == 1
    assert created[0].session.is_closed


@pytest.mark.asyncio
async def test_async_product_fetch_closes_market_client_on_failure() -> None:
    created: list[Any] = []

    class Session:
        is_closed = False

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.session = Session()
            created.append(self)

        async def close(self) -> None:
            self.session.is_closed = True

    @async_fetch._manage_market_http
    async def failing_fetch() -> pl.DataFrame:
        async_fetch._market_http(MarketHTTP)
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await failing_fetch()

    assert len(created) == 1
    assert created[0].session.is_closed


def test_sync_product_fetch_closes_session_without_client_close() -> None:
    created: list[Any] = []

    class Session:
        is_closed = False

        def close(self) -> None:
            self.is_closed = True

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.session = Session()
            created.append(self)

    @sync_fetch._manage_market_http
    def successful_fetch() -> pl.DataFrame:
        sync_fetch._market_http(MarketHTTP)
        return pl.DataFrame()

    successful_fetch()

    assert created[0].session.is_closed


@pytest.mark.asyncio
async def test_async_product_fetch_closes_session_without_client_close() -> None:
    created: list[Any] = []

    class Session:
        is_closed = False

        async def aclose(self) -> None:
            self.is_closed = True

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.session = Session()
            created.append(self)

    @async_fetch._manage_market_http
    async def successful_fetch() -> pl.DataFrame:
        async_fetch._market_http(MarketHTTP)
        return pl.DataFrame()

    await successful_fetch()

    assert created[0].session.is_closed


def test_sync_product_fetch_closes_auxiliary_resources_after_session_closed() -> None:
    created: list[Any] = []

    class Session:
        is_closed = True

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.session = Session()
            self.auxiliary_closed = False
            created.append(self)

        def close(self) -> None:
            self.auxiliary_closed = True

    @sync_fetch._manage_market_http
    def successful_fetch() -> pl.DataFrame:
        sync_fetch._market_http(MarketHTTP)
        return pl.DataFrame()

    successful_fetch()

    assert created[0].auxiliary_closed


@pytest.mark.asyncio
async def test_async_product_fetch_closes_auxiliary_resources_after_session_closed() -> None:
    created: list[Any] = []

    class Session:
        is_closed = True

    class MarketHTTP:
        def __init__(self, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.session = Session()
            self.auxiliary_closed = False
            created.append(self)

        async def close(self) -> None:
            self.auxiliary_closed = True

    @async_fetch._manage_market_http
    async def successful_fetch() -> pl.DataFrame:
        async_fetch._market_http(MarketHTTP)
        return pl.DataFrame()

    await successful_fetch()

    assert created[0].auxiliary_closed


def test_sync_product_fetch_preserves_primary_error_when_cleanup_fails() -> None:
    closed: list[str] = []

    class MarketHTTP:
        def __init__(self, name: str, *, fail_close: bool, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.name = name
            self.fail_close = fail_close

        def close(self) -> None:
            closed.append(self.name)
            if self.fail_close:
                raise RuntimeError(f"{self.name} cleanup failed")

    @sync_fetch._manage_market_http
    def failing_fetch() -> pl.DataFrame:
        sync_fetch._market_http(lambda **kwargs: MarketHTTP("first", fail_close=False, **kwargs))
        sync_fetch._market_http(lambda **kwargs: MarketHTTP("second", fail_close=True, **kwargs))
        raise ValueError("fetch failed")

    with pytest.raises(ValueError, match="fetch failed") as exc_info:
        failing_fetch()

    assert closed == ["second", "first"]
    assert exc_info.value.__notes__ == [
        "Market HTTP cleanup failed: RuntimeError('second cleanup failed')"
    ]


@pytest.mark.asyncio
async def test_async_product_fetch_preserves_primary_error_when_cleanup_fails() -> None:
    closed: list[str] = []

    class MarketHTTP:
        def __init__(self, name: str, *, fail_close: bool, preload_product_table: bool) -> None:
            assert not preload_product_table
            self.name = name
            self.fail_close = fail_close

        async def close(self) -> None:
            closed.append(self.name)
            if self.fail_close:
                raise RuntimeError(f"{self.name} cleanup failed")

    @async_fetch._manage_market_http
    async def failing_fetch() -> pl.DataFrame:
        async_fetch._market_http(lambda **kwargs: MarketHTTP("first", fail_close=False, **kwargs))
        async_fetch._market_http(lambda **kwargs: MarketHTTP("second", fail_close=True, **kwargs))
        raise ValueError("fetch failed")

    with pytest.raises(ValueError, match="fetch failed") as exc_info:
        await failing_fetch()

    assert closed == ["second", "first"]
    assert exc_info.value.__notes__ == [
        "Market HTTP cleanup failed: RuntimeError('second cleanup failed')"
    ]


@pytest.mark.asyncio
async def test_async_product_table_skips_failed_exchanges(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def working() -> pl.DataFrame:
        return pl.DataFrame({"exchange": ["working"]})

    async def broken() -> pl.DataFrame:
        raise RuntimeError("exchange unavailable")

    monkeypatch.setattr(async_manager, "VALID_EXCHANGES", [working, broken])

    result = await AsyncProductTableManager()._fetch_product_tables()

    assert result.to_dicts() == [{"exchange": "working"}]


@pytest.mark.asyncio
async def test_async_product_table_raises_when_all_exchanges_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def broken() -> pl.DataFrame:
        raise RuntimeError("exchange unavailable")

    monkeypatch.setattr(async_manager, "VALID_EXCHANGES", [broken])

    with pytest.raises(ProductTableError, match="Failed to fetch"):
        await AsyncProductTableManager()._fetch_product_tables()


@pytest.mark.asyncio
async def test_async_product_table_propagates_exchange_cancellation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def cancelled() -> pl.DataFrame:
        raise asyncio.CancelledError

    monkeypatch.setattr(async_manager, "VALID_EXCHANGES", [cancelled])

    with pytest.raises(asyncio.CancelledError):
        await AsyncProductTableManager()._fetch_product_tables()
