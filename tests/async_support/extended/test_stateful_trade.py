"""Opt-in Extended asynchronous signed order lifecycle and fill tests."""

import asyncio
import os
from decimal import ROUND_CEILING, ROUND_DOWN, Decimal

import pytest
import pytest_asyncio

from dcex.async_support.extended.client import Client

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to send a real Extended order.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(preload_product_table=False, timeout=20) as instance:
        yield instance


def _data(response: object) -> object:
    assert isinstance(response, dict) and response.get("status") == "OK", response
    return response.get("data")


def _rows(response: object) -> list[dict]:
    data = _data(response)
    assert isinstance(data, list), response
    assert all(isinstance(row, dict) for row in data), response
    return data


async def _clean_account(client: Client) -> None:
    assert not _rows(await client.get_open_orders()), "Extended account has open orders"
    assert not _rows(await client.get_positions()), "Extended account has open positions"


async def _book(client: Client, market: str) -> tuple[Decimal, Decimal]:
    data = _data(await client.get_order_book(market))
    assert isinstance(data, dict) and data.get("bid") and data.get("ask"), data
    return Decimal(str(data["bid"][0]["price"])), Decimal(str(data["ask"][0]["price"]))


async def _market(client: Client) -> tuple[str, Decimal, Decimal, Decimal]:
    for row in _rows(await client.get_markets()):
        if (
            row.get("type") != "PERPETUAL"
            or row.get("status") != "ACTIVE"
            or row.get("isRfq")
            or row.get("isOffHours")
        ):
            continue
        name = row["name"]
        config = row["tradingConfig"]
        step = Decimal(str(config["minOrderSizeChange"]))
        tick = Decimal(str(config["minPriceChange"]))
        if step <= 0 or tick <= 0:
            continue
        qty = (Decimal(str(config["minOrderSize"])) / step).to_integral_value(
            rounding=ROUND_CEILING
        ) * step
        if qty <= 0:
            continue
        try:
            _, ask = await _book(client, name)
        except (AssertionError, KeyError, ValueError):
            continue
        if qty * ask * Decimal("1.005") <= Decimal("25"):
            return name, qty, step, tick
    pytest.fail("Extended has no liquid active perpetual with a minimum order at most 25 USD.")


def _order_id(response: object) -> str:
    data = _data(response)
    assert isinstance(data, dict) and data.get("id"), response
    return str(data["id"])


async def _cancel_if_open(client: Client, market: str, order_id: str) -> None:
    for _ in range(10):
        open_ids = {
            str(order["id"]) for order in _rows(await client.get_open_orders(market=market))
        }
        if order_id not in open_ids:
            return
        _data(await client.cancel_order(order_id))
        await asyncio.sleep(0.5)
    assert order_id not in {
        str(order["id"]) for order in _rows(await client.get_open_orders(market=market))
    }


async def _close_test_position(client: Client, market: str, step: Decimal, tick: Decimal) -> None:
    for _ in range(4):
        positions = _rows(await client.get_positions(market=market))
        if not positions:
            return
        bid, ask = await _book(client, market)
        for position in positions:
            qty = Decimal(str(position["size"]))
            assert qty >= step, position
            if position["side"] == "LONG":
                side = "SELL"
                price = (bid * Decimal("0.995") / tick).to_integral_value(
                    rounding=ROUND_DOWN
                ) * tick
            else:
                side = "BUY"
                price = (ask * Decimal("1.005") / tick).to_integral_value(
                    rounding=ROUND_CEILING
                ) * tick
            _order_id(
                await client.place_limit_order(
                    market=market,
                    side=side,
                    qty=str(qty),
                    price=str(price),
                    reduce_only=True,
                    time_in_force="IOC",
                )
            )
        await asyncio.sleep(1)
    assert not _rows(await client.get_positions(market=market)), "Extended position remains"


async def test_post_only_order_and_cancel(client: Client) -> None:
    await _clean_account(client)
    market, qty, step, tick = await _market(client)
    bid, _ = await _book(client, market)
    price = (bid * Decimal("0.99") / tick).to_integral_value(rounding=ROUND_DOWN) * tick
    order_id = None
    try:
        order_id = _order_id(
            await client.place_limit_order(
                market=market,
                side="BUY",
                qty=str(qty),
                price=str(price),
                post_only=True,
                time_in_force="GTT",
            )
        )
        _data(await client.cancel_order(order_id))
        await _cancel_if_open(client, market, order_id)
        order = _data(await client.get_order(order_id))
        assert isinstance(order, dict)
        if Decimal(str(order["filledQty"])) > 0:
            await _close_test_position(client, market, step, tick)
            pytest.fail("Extended post-only order filled unexpectedly.")
        assert order["status"] == "CANCELLED", order
    finally:
        if order_id:
            try:
                await _cancel_if_open(client, market, order_id)
            finally:
                await _close_test_position(client, market, step, tick)
    await _clean_account(client)


@pytest.mark.live_fill
async def test_ioc_fill_and_reduce_only_close(client: Client) -> None:
    await _clean_account(client)
    market, qty, step, tick = await _market(client)
    _, ask = await _book(client, market)
    price = (ask * Decimal("1.005") / tick).to_integral_value(rounding=ROUND_CEILING) * tick
    buy_sent = False
    try:
        response = await client.place_limit_order(
            market=market,
            side="BUY",
            qty=str(qty),
            price=str(price),
            post_only=False,
            time_in_force="IOC",
        )
        buy_sent = True
        _order_id(response)
        for _ in range(20):
            if _rows(await client.get_positions(market=market)):
                break
            await asyncio.sleep(0.5)
        assert _rows(await client.get_positions(market=market)), "Extended IOC buy did not fill"
        await _close_test_position(client, market, step, tick)
    finally:
        if buy_sent:
            await _close_test_position(client, market, step, tick)
    await _clean_account(client)
