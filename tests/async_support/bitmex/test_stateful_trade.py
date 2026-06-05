# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import json
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bitmex.client import Client

load_dotenv()

BITMEX_API_KEY = os.getenv("BITMEX_API_KEY")
BITMEX_API_SECRET = os.getenv("BITMEX_API_SECRET")
SYMBOL = "XBT-USDT-SWAP"
EXCHANGE_SYMBOL = "XBTUSDT"
ORDER_QTY = 100
MARGIN_UNIT = Decimal("1000000")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real BitMEX order tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BITMEX_API_KEY,
        api_secret=BITMEX_API_SECRET,
        timeout=20,
    ) as client_instance:
        yield client_instance


def _dec(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _client_id() -> str:
    return f"dcx{uuid.uuid4().hex[:16]}"


def _filter(**kwargs: object) -> str:
    return json.dumps(kwargs, separators=(",", ":"))


async def _position(client: Client) -> dict:
    for item in await client.get_positions():
        if isinstance(item, dict) and item.get("symbol") == EXCHANGE_SYMBOL:
            return item
    return {}


async def _position_qty(client: Client) -> int:
    return int(_dec((await _position(client)).get("currentQty")))


async def _open_orders(client: Client) -> list[dict]:
    orders = await client.get_order(
        product_symbol=SYMBOL,
        filter=_filter(open=True),
        count=100,
        reverse=True,
    )
    return [item for item in orders if isinstance(item, dict)]


async def _skip_if_existing_state(client: Client) -> None:
    if await _open_orders(client):
        pytest.skip("BitMEX already has open orders; not touching unrelated orders.")
    if await _position_qty(client) != 0:
        pytest.skip("BitMEX already has a position; not changing exposure.")


async def _best_prices(client: Client) -> tuple[Decimal, Decimal]:
    bids: list[Decimal] = []
    asks: list[Decimal] = []
    for level in await client.get_orderbook(product_symbol=SYMBOL, depth=10):
        if not isinstance(level, dict):
            continue
        price = _dec(level.get("price"))
        if level.get("side") == "Buy":
            bids.append(price)
        elif level.get("side") == "Sell":
            asks.append(price)
    if not bids or not asks:
        pytest.skip("BitMEX orderbook did not return both bid and ask prices.")
    return max(bids), min(asks)


async def _tick_size(client: Client) -> Decimal:
    data = await client.get_instrument_info(product_symbol=SYMBOL)
    if not data:
        return Decimal("0.1")
    return _dec(data[0].get("tickSize"), "0.1")


def _round_to_tick(value: Decimal, tick: Decimal, rounding: str) -> Decimal:
    return (value / tick).to_integral_value(rounding=rounding) * tick


async def _post_only_buy_price(client: Client) -> float:
    best_bid, _ = await _best_prices(client)
    return float(
        _round_to_tick(best_bid * Decimal("0.50"), await _tick_size(client), ROUND_DOWN)
    )


async def _post_only_sell_price(client: Client) -> float:
    _, best_ask = await _best_prices(client)
    return float(
        _round_to_tick(best_ask * Decimal("1.50"), await _tick_size(client), ROUND_UP)
    )


async def _fillable_buy_price(client: Client) -> float:
    _, best_ask = await _best_prices(client)
    tick = await _tick_size(client)
    return float(_round_to_tick(best_ask + tick, tick, ROUND_UP))


async def _fillable_sell_price(client: Client) -> float:
    best_bid, _ = await _best_prices(client)
    tick = await _tick_size(client)
    return float(_round_to_tick(best_bid - tick, tick, ROUND_DOWN))


async def _available_margin(client: Client) -> Decimal:
    for item in await client.get_margin():
        if isinstance(item, dict) and item.get("currency") == "USDt":
            return _dec(item.get("availableMargin"))
    return Decimal("0")


async def _ensure_margin(client: Client) -> None:
    leverage = max(_dec((await _position(client)).get("leverage"), "1"), Decimal("1"))
    required_margin = Decimal(ORDER_QTY) / leverage * MARGIN_UNIT * Decimal("1.5")
    if await _available_margin(client) < required_margin:
        pytest.skip("Insufficient BitMEX available margin for stateful order test.")


async def _wait_for_position(client: Client, sign: int) -> int:
    for _ in range(10):
        qty = await _position_qty(client)
        if sign > 0 and qty > 0:
            return qty
        if sign < 0 and qty < 0:
            return qty
        await asyncio.sleep(1)
    return 0


async def _wait_until_flat(client: Client) -> None:
    for _ in range(10):
        if await _position_qty(client) == 0:
            return
        await asyncio.sleep(1)
    assert await _position_qty(client) == 0


async def _close_position(client: Client) -> None:
    qty = await _position_qty(client)
    if qty > 0:
        await client.place_market_sell_order(SYMBOL, orderQty=abs(qty), clOrdID=_client_id())
    elif qty < 0:
        await client.place_market_buy_order(SYMBOL, orderQty=abs(qty), clOrdID=_client_id())
    await asyncio.sleep(2)
    await _wait_until_flat(client)


async def _cleanup(client: Client) -> None:
    with suppress(Exception):
        if await _open_orders(client):
            await client.cancel_all_orders(product_symbol=SYMBOL, text="dcex cleanup")
            await asyncio.sleep(1)
    with suppress(Exception):
        await _close_position(client)


async def _assert_order_visible(client: Client, order_id: str) -> None:
    assert any(order.get("orderID") == order_id for order in await _open_orders(client))


async def test_async_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    await _ensure_margin(client)

    try:
        order_id = None
        try:
            price = await _post_only_buy_price(client)
            order = await client.place_order(
                SYMBOL,
                side="Buy",
                orderQty=ORDER_QTY,
                ordType="Limit",
                price=price,
                execInst="ParticipateDoNotInitiate",
                clOrdID=_client_id(),
                text="dcex stateful generic",
            )
            order_id = order["orderID"]
            await _assert_order_visible(client, order_id)
            assert await client.amend_order(orderID=order_id, price=price - 1.0) is not None
            assert (
                await client.cancel_order(orderID=order_id, text="dcex stateful cancel")
                is not None
            )
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_order(orderID=order_id)

        order_id = None
        try:
            order = await client.place_limit_order(
                SYMBOL,
                side="Buy",
                orderQty=ORDER_QTY,
                price=await _post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert (
                await client.cancel_all_orders(product_symbol=SYMBOL, text="dcex cancel all")
                is not None
            )
            order_id = None
            await asyncio.sleep(1)
        finally:
            if order_id is not None:
                await client.cancel_order(orderID=order_id)

        order_id = None
        try:
            order = await client.place_post_only_order(
                SYMBOL,
                side="Buy",
                orderQty=ORDER_QTY,
                price=await _post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert await client.cancel_order(orderID=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_order(orderID=order_id)

        order_id = None
        try:
            order = await client.place_post_only_buy_order(
                SYMBOL,
                orderQty=ORDER_QTY,
                price=await _post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert await client.cancel_order(orderID=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_order(orderID=order_id)

        order_id = None
        try:
            order = await client.place_post_only_sell_order(
                SYMBOL,
                orderQty=ORDER_QTY,
                price=await _post_only_sell_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert await client.cancel_order(orderID=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_order(orderID=order_id)

        assert (
            await client.place_market_buy_order(SYMBOL, ORDER_QTY, clOrdID=_client_id())
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await client.place_market_sell_order(SYMBOL, ORDER_QTY, clOrdID=_client_id())
            is not None
        )
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert (
            await client.place_market_order(SYMBOL, "Buy", ORDER_QTY, clOrdID=_client_id())
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await client.place_limit_buy_order(
                SYMBOL,
                ORDER_QTY,
                await _fillable_buy_price(client),
                clOrdID=_client_id(),
            )
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await client.place_limit_sell_order(
                SYMBOL,
                ORDER_QTY,
                await _fillable_sell_price(client),
                clOrdID=_client_id(),
            )
            is not None
        )
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert await client.get_order(product_symbol=SYMBOL, count=10, reverse=True) is not None
    finally:
        await _cleanup(client)

    assert not await _open_orders(client)
    assert await _position_qty(client) == 0
