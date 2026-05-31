"""Offline tests that order placement converts the side to each venue's value.

Each sync/async trade client is built with a fake product-table manager and a
stubbed _request, then the side that would be sent in the payload is asserted.
Covers backward compatibility (legacy strings / hard-coded wrappers) and the
OrderSide enum, with no network and no API keys.

Also guards a known trap: BitMart *contract* orders use an integer side
(1=buy_open_long ... 4=sell_open_short), which must NOT be run through
OrderSide conversion.
"""

from typing import Any

import pytest

from dcex.enums import OrderSide


class _FakePTM:
    def get_exchange_symbol(self, *args: object, **kwargs: object) -> str:
        return "TESTSYMBOL"

    def get_product_type(self, *args: object, **kwargs: object) -> str:
        return "spot"

    def get_exchange_type(self, *args: object, **kwargs: object) -> str:
        return "linear"


def _wire(manager: Any) -> dict[str, Any]:
    """Attach a fake ptm and capture the payload _request would send."""
    captured: dict[str, Any] = {}
    manager.ptm = _FakePTM()

    def fake_request(
        method: str, path: object, query: Any = None, body: Any = None, **kwargs: object
    ) -> dict:
        captured.clear()
        # Different clients pass the order payload as `query` or `body`.
        if isinstance(query, dict):
            captured.update(query)
        if isinstance(body, dict):
            captured.update(body)
        return {}

    manager._request = fake_request
    return captured


def _wire_async(manager: Any) -> dict[str, Any]:
    """Attach a fake ptm and capture the payload async _request would send."""
    captured: dict[str, Any] = {}
    manager.ptm = _FakePTM()

    async def fake_request(
        method: str, path: object, query: Any = None, body: Any = None, **kwargs: object
    ) -> dict:
        captured.clear()
        if isinstance(query, dict):
            captured.update(query)
        if isinstance(body, dict):
            captured.update(body)
        return {}

    manager._request = fake_request
    return captured


def test_binance_side_conversion() -> None:
    from dcex.binance._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_market_buy_order(product_symbol="BTC-USDT-SPOT", quantity="1")
    assert cap["side"] == "BUY"
    m.place_order(product_symbol="BTC-USDT-SPOT", side=OrderSide.SELL, type_="MARKET", quantity="1")
    assert cap["side"] == "SELL"


def test_bybit_side_conversion() -> None:
    from dcex.bybit._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_order(product_symbol="BTC-USDT-SWAP", side="buy", orderType="Market", qty="1")
    assert cap["side"] == "Buy"
    m.place_order(product_symbol="BTC-USDT-SWAP", side=OrderSide.SELL, orderType="Market", qty="1")
    assert cap["side"] == "Sell"


def test_okx_side_conversion() -> None:
    from dcex.okx._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_order(
        product_symbol="BTC-USDT-SWAP", tdMode="cross", side="BUY", ordType="market", sz="1"
    )
    assert cap["side"] == "buy"


def test_bitmart_spot_side_conversion() -> None:
    from dcex.bitmart._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_spot_order(product_symbol="BTC-USDT-SPOT", side="BUY", type="limit", size="1")
    assert cap["side"] == "buy"


def test_bitmart_contract_int_side_is_untouched() -> None:
    """Contract orders use an integer side code; it must pass through as-is."""
    from dcex.bitmart._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_contract_order(product_symbol="BTC-USDT-SWAP", side=4, size=1)
    assert cap["side"] == 4


def test_bitmex_side_conversion() -> None:
    from dcex.bitmex._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_order(product_symbol="XBT-USD-SWAP", side=OrderSide.BUY, ordType="Market", orderQty=1)
    assert cap["side"] == "Buy"


def test_gateio_spot_side_conversion() -> None:
    from dcex.gateio._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire(m)
    m.place_spot_order(product_symbol="BTC-USDT-SPOT", side="sell", amount="1", price="100")
    assert cap["side"] == "sell"


@pytest.mark.asyncio
async def test_async_binance_side_conversion() -> None:
    from dcex.async_support.binance._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_order(
        product_symbol="BTC-USDT-SPOT", side=OrderSide.SELL, type_="MARKET", quantity="1"
    )
    assert cap["side"] == "SELL"


@pytest.mark.asyncio
async def test_async_bybit_side_conversion() -> None:
    from dcex.async_support.bybit._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_order(product_symbol="BTC-USDT-SWAP", side="buy", orderType="Market", qty="1")
    assert cap["side"] == "Buy"


@pytest.mark.asyncio
async def test_async_okx_side_conversion() -> None:
    from dcex.async_support.okx._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_order(
        product_symbol="BTC-USDT-SWAP",
        tdMode="cross",
        side=OrderSide.SELL,
        ordType="market",
        sz="1",
    )
    assert cap["side"] == "sell"


@pytest.mark.asyncio
async def test_async_bitmart_spot_side_conversion() -> None:
    from dcex.async_support.bitmart._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_spot_order(product_symbol="BTC-USDT-SPOT", side="BUY", type="limit", size="1")
    assert cap["side"] == "buy"


@pytest.mark.asyncio
async def test_async_bitmart_contract_int_side_is_untouched() -> None:
    from dcex.async_support.bitmart._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_contract_order(product_symbol="BTC-USDT-SWAP", side=4, size=1)
    assert cap["side"] == 4


@pytest.mark.asyncio
async def test_async_bitmex_side_conversion() -> None:
    from dcex.async_support.bitmex._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_order(product_symbol="XBT-USD-SWAP", side=OrderSide.BUY, ordType="Market")
    assert cap["side"] == "Buy"


@pytest.mark.asyncio
async def test_async_gateio_spot_side_conversion() -> None:
    from dcex.async_support.gateio._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    cap = _wire_async(m)
    await m.place_spot_order(product_symbol="BTC-USDT-SPOT", side="sell", amount="1", price="100")
    assert cap["side"] == "sell"


@pytest.mark.parametrize("bad", ["", "hodl", "long"])
def test_invalid_side_rejected(bad: str) -> None:
    from dcex.binance._trade_http import TradeHTTP

    m = TradeHTTP(preload_product_table=False)
    _wire(m)
    with pytest.raises(ValueError, match="Unknown order side"):
        m.place_order(product_symbol="BTC-USDT-SPOT", side=bad, type_="MARKET", quantity="1")
