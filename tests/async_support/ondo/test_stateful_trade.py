"""Opt-in Ondo order lifecycle and real-fill tests."""

import asyncio
import os
from decimal import ROUND_CEILING, Decimal
from uuid import uuid4

import pytest
import pytest_asyncio

from dcex.async_support.ondo.client import Client

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to send a real Ondo order.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(preload_product_table=False) as instance:
        yield instance


def _result(response: object) -> object:
    assert isinstance(response, dict) and response.get("success") is True, response
    return response.get("result")


def _rows(response: object) -> list[dict]:
    result = _result(response)
    assert isinstance(result, list), response
    assert all(isinstance(row, dict) for row in result), response
    return result


def _order_id(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in ("orderID", "orderId", "id"):
        identifier = value.get(key)
        if isinstance(identifier, str | int) and str(identifier):
            return str(identifier)
    for nested in ("order", "result"):
        found = _order_id(value.get(nested))
        if found:
            return found
    return None


async def _market_order_amounts(client: Client) -> tuple[str, str, str]:
    markets = _result(await client.get_markets())
    assert isinstance(markets, dict)
    pair = next(
        p
        for p in markets["perps"]["tradingPairs"]
        if p.get("market") == "BTC-USD.P" and not p.get("disabled")
    )
    market = pair["market"]
    depth = _result(await client.get_depth(market, 5))
    assert isinstance(depth, dict) and depth["bids"] and depth["asks"]
    bid = Decimal(str(depth["bids"][0][0]))
    ask = Decimal(str(depth["asks"][0][0]))
    tick = Decimal(str(pair["quoteIncrement"]))
    step = Decimal(str(pair["baseIncrement"]))
    post_price = (bid * Decimal("0.95") // tick) * tick
    assert post_price > 0
    post_size = (Decimal("10") / (post_price * step)).to_integral_value(
        rounding=ROUND_CEILING
    ) * step
    assert Decimal("10") <= post_price * post_size and ask * post_size <= Decimal("20")
    return market, str(post_size), str(post_price)


async def _test_open_order_id(client: Client, market: str, client_id: str) -> str | None:
    return next(
        (
            _order_id(order)
            for order in _rows(await client.get_open_orders(market=market))
            if order.get("clientOrderId") == client_id
        ),
        None,
    )


async def _cancel_test_order(client: Client, market: str, client_id: str) -> None:
    for _ in range(10):
        order_id = await _test_open_order_id(client, market, client_id)
        if order_id:
            _result(await client.cancel_order(order_id))
        await asyncio.sleep(0.5)
        if await _test_open_order_id(client, market, client_id) is None:
            return
    assert await _test_open_order_id(client, market, client_id) is None


async def _close_test_position(client: Client, market: str) -> None:
    for _ in range(4):
        positions = [p for p in _rows(await client.get_positions()) if p.get("market") == market]
        if not positions:
            return
        for position in positions:
            size = Decimal(str(position["netQuantity"]))
            assert size > 0, position
            side = "sell" if position["direction"] == "long" else "buy"
            _result(
                await client.place_order(
                    market=market,
                    side=side,
                    type="market",
                    size=str(size),
                    reduceOnly=True,
                )
            )
        await asyncio.sleep(1)
    assert not _rows(await client.get_positions())


async def test_post_only_limit_order_and_cancel(client: Client) -> None:
    if _rows(await client.get_positions()) or _rows(await client.get_open_orders()):
        pytest.skip("Ondo account must start without positions or open orders.")
    market, size, price = await _market_order_amounts(client)
    client_id = f"dcex-{uuid4().hex[:20]}"
    try:
        placed = _result(
            await client.place_order(
                market=market,
                side="buy",
                type="limit",
                price=price,
                size=size,
                timeInForce="GTC",
                postOnly=True,
                clientOrderId=client_id,
            )
        )
        order_id = _order_id(placed)
        for _ in range(10):
            order_id = order_id or await _test_open_order_id(client, market, client_id)
            if order_id:
                break
            await asyncio.sleep(0.5)
        assert order_id, f"Ondo post-only order has no cancellable ID: {placed}"
        _result(await client.cancel_order(order_id))
    finally:
        try:
            await _cancel_test_order(client, market, client_id)
        finally:
            await _close_test_position(client, market)

    final_order = _result(await client.get_order(order_id))
    assert isinstance(final_order, dict)
    if Decimal(str(final_order["filledSize"])) > 0:
        await _close_test_position(client, market)
        pytest.fail("Ondo post-only order filled unexpectedly and was closed reduce-only.")
    assert final_order["status"] == "canceled", final_order
    assert not _rows(await client.get_positions())


@pytest.mark.live_fill
async def test_market_fill_and_reduce_only_close(client: Client) -> None:
    if _rows(await client.get_positions()) or _rows(await client.get_open_orders()):
        pytest.skip("Ondo account must start without positions or open orders.")
    market, size, _ = await _market_order_amounts(client)
    buy_sent = False
    try:
        placed = _result(
            await client.place_order(
                market=market,
                side="buy",
                type="market",
                size=size,
                clientOrderId=f"dcex-{uuid4().hex[:20]}",
            )
        )
        buy_sent = True
        order_id = _order_id(placed)
        assert order_id, f"Ondo market buy has no order ID: {placed}"
        filled = Decimal("0")
        for _ in range(20):
            order = _result(await client.get_order(order_id))
            assert isinstance(order, dict)
            filled = Decimal(str(order.get("filledSize", "0")))
            if filled > 0:
                break
            await asyncio.sleep(0.5)
        assert filled > 0, "Ondo market buy did not report a fill"
        await _close_test_position(client, market)
    finally:
        if buy_sent:
            await _close_test_position(client, market)
