"""Kraken native wrapper behavior tests."""

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def public_request(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append((method_name, params))
        return 200, {}, b'{"ok":true}'

    def private_request(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append((method_name, params))
        return 200, {}, b'{"ok":true}'


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def public_request_async(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append((method_name, params))
        return 200, {}, b'{"ok":true}'

    async def private_request_async(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append((method_name, params))
        return 200, {}, b'{"ok":true}'


def _params(params: list[tuple[str, str]]) -> dict[str, str]:
    return dict(params)


def test_sync_kraken_market_passes_product_symbol_to_native() -> None:
    """Sync market wrappers pass canonical product_symbol into Rust."""
    from dcex.kraken._market_http import MarketHTTP

    native = _SyncNative()
    client = MarketHTTP(preload_product_table=False)
    client._native_client = native

    try:
        client.get_futures_orderbook(product_symbol="BTC-USD-SWAP")
    finally:
        client.close()

    method_name, params = native.calls[-1]
    assert method_name == "get_futures_orderbook"
    assert _params(params) == {"product_symbol": "BTC-USD-SWAP"}


def test_sync_kraken_trade_passes_product_symbol_to_native() -> None:
    """Sync trade wrappers leave Kraken symbol conversion to Rust."""
    from dcex.kraken._trade_http import TradeHTTP

    native = _SyncNative()
    client = TradeHTTP(preload_product_table=False)
    client._native_client = native

    try:
        client.place_futures_limit_order(
            product_symbol="BTC-USD-SWAP",
            side="buy",
            size=1,
            price="100",
        )
    finally:
        client.close()

    method_name, params = native.calls[-1]
    payload = _params(params)
    assert method_name == "place_futures_limit_order"
    assert payload["product_symbol"] == "BTC-USD-SWAP"
    assert payload["price"] == "100"
    assert "symbol" not in payload


@pytest.mark.asyncio
async def test_async_kraken_market_passes_product_symbol_to_native() -> None:
    """Async market wrappers pass canonical product_symbol into Rust."""
    from dcex.async_support.kraken._market_http import MarketHTTP

    native = _AsyncNative()
    client = await MarketHTTP(preload_product_table=False).async_init()
    client._native_client = native

    try:
        await client.get_spot_orderbook(product_symbol="BTC-USD-SPOT")
    finally:
        await client.close()

    method_name, params = native.calls[-1]
    assert method_name == "get_spot_orderbook"
    assert _params(params) == {"product_symbol": "BTC-USD-SPOT"}


@pytest.mark.asyncio
async def test_async_kraken_trade_passes_product_symbol_to_native() -> None:
    """Async trade wrappers leave Kraken symbol conversion to Rust."""
    from dcex.async_support.kraken._trade_http import TradeHTTP

    native = _AsyncNative()
    client = await TradeHTTP(preload_product_table=False).async_init()
    client._native_client = native

    try:
        await client.place_spot_limit_order(
            product_symbol="BTC-USD-SPOT",
            side="buy",
            volume="0.01",
            price="100",
        )
    finally:
        await client.close()

    method_name, params = native.calls[-1]
    payload = _params(params)
    assert method_name == "place_spot_limit_order"
    assert payload["product_symbol"] == "BTC-USD-SPOT"
    assert payload["price"] == "100"
    assert "pair" not in payload
