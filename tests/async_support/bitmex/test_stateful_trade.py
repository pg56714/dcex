# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import json
import os
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bitmex.client import Client
from dcex.utils.errors import FailedRequestError

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
        await _cleanup(client_instance)
        try:
            yield client_instance
        finally:
            await _cleanup(client_instance)


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
        pytest.fail("BitMEX orderbook did not return both bid and ask prices.")
    return max(bids), min(asks)


async def _tick_size(client: Client) -> Decimal:
    data = await client.get_instrument_info(product_symbol=SYMBOL)
    if not data:
        return Decimal("0.1")
    return _dec(data[0].get("tickSize"), "0.1")


async def _order_qty(client: Client) -> int:
    data = await client.get_instrument_info(product_symbol=SYMBOL)
    if not data:
        return ORDER_QTY
    lot_size = _dec(data[0].get("lotSize"), str(ORDER_QTY))
    return int(max(lot_size, Decimal("1")))


def _round_to_tick(value: Decimal, tick: Decimal, rounding: str) -> Decimal:
    return (value / tick).to_integral_value(rounding=rounding) * tick


async def _post_only_buy_price(client: Client) -> float:
    best_bid, _ = await _best_prices(client)
    tick = await _tick_size(client)
    return float(_round_to_tick(best_bid - tick, tick, ROUND_DOWN))


async def _post_only_sell_price(client: Client) -> float:
    _, best_ask = await _best_prices(client)
    tick = await _tick_size(client)
    return float(_round_to_tick(best_ask + tick, tick, ROUND_UP))


async def _fillable_buy_price(client: Client) -> float:
    _, best_ask = await _best_prices(client)
    tick = await _tick_size(client)
    price = max(best_ask + tick, best_ask * Decimal("1.002"))
    return float(_round_to_tick(price, tick, ROUND_UP))


async def _fillable_sell_price(client: Client) -> float:
    best_bid, _ = await _best_prices(client)
    tick = await _tick_size(client)
    price = min(best_bid - tick, best_bid * Decimal("0.998"))
    return float(_round_to_tick(price, tick, ROUND_DOWN))


async def _available_margin(client: Client) -> Decimal:
    for item in await client.get_margin():
        if isinstance(item, dict) and item.get("currency") == "USDt":
            return _dec(item.get("availableMargin"))
    return Decimal("0")


async def _ensure_margin(client: Client) -> None:
    leverage = max(_dec((await _position(client)).get("leverage"), "1"), Decimal("1"))
    required_margin = Decimal(await _order_qty(client)) / leverage * MARGIN_UNIT * Decimal("1.05")
    if await _available_margin(client) < required_margin:
        pytest.fail("Insufficient BitMEX available margin for stateful order test.")


async def _wait_for_position(client: Client, sign: int) -> int:
    for _ in range(10):
        qty = await _position_qty(client)
        if sign > 0 and qty > 0:
            return qty
        if sign < 0 and qty < 0:
            return qty
        await asyncio.sleep(1)
    return 0


async def _wait_for_position_or_skip(client: Client, sign: int, action: str) -> int:
    qty = await _wait_for_position(client, sign)
    if qty == 0:
        pytest.fail(f"BitMEX {action} did not fill before timeout.")
    return qty


async def _wait_until_flat(client: Client) -> None:
    for _ in range(10):
        if await _position_qty(client) == 0:
            return
        await asyncio.sleep(1)
    assert await _position_qty(client) == 0


async def _close_position(client: Client) -> None:
    qty = await _position_qty(client)
    if qty > 0:
        await client.place_order(
            SYMBOL,
            side="Sell",
            orderQty=abs(qty),
            ordType="Market",
            execInst="ReduceOnly",
            clOrdID=_client_id(),
        )
    elif qty < 0:
        await client.place_order(
            SYMBOL,
            side="Buy",
            orderQty=abs(qty),
            ordType="Market",
            execInst="ReduceOnly",
            clOrdID=_client_id(),
        )
    await asyncio.sleep(2)
    await _wait_until_flat(client)


async def _cleanup(client: Client) -> None:
    if await _open_orders(client):
        await client.cancel_all_orders(product_symbol=SYMBOL, text="dcex cleanup")
        await asyncio.sleep(1)
    await _close_position(client)
    assert not await _open_orders(client)
    assert await _position_qty(client) == 0


async def _assert_order_visible(client: Client, order_id: str) -> None:
    for _ in range(5):
        if any(order.get("orderID") == order_id for order in await _open_orders(client)):
            return
        orders = await client.get_order(
            product_symbol=SYMBOL,
            filter=_filter(orderID=order_id),
            count=1,
            reverse=True,
        )
        if any(isinstance(order, dict) and order.get("orderID") == order_id for order in orders):
            return
        await asyncio.sleep(1)
    pytest.fail(f"BitMEX order {order_id} was not visible before live assertion.")


def _is_invalid_order_id(exc: FailedRequestError) -> bool:
    return "invalid orderid" in str(exc).lower()


async def _amend_order_or_skip(client: Client, order_id: str, price: float) -> dict:
    try:
        return await client.amend_order(orderID=order_id, price=price)
    except FailedRequestError as exc:
        if _is_invalid_order_id(exc):
            pytest.fail(f"BitMEX order {order_id} was no longer amendable: {exc}")
        raise


async def _cancel_order_if_present(
    client: Client,
    order_id: str,
    text: str | None = None,
) -> object:
    try:
        if text is None:
            return await client.cancel_order(orderID=order_id)
        return await client.cancel_order(orderID=order_id, text=text)
    except FailedRequestError as exc:
        if _is_invalid_order_id(exc):
            return {}
        raise


async def test_async_stateful_order_lifecycle(client):
    await _cleanup(client)
    await _ensure_margin(client)
    qty = await _order_qty(client)

    try:
        order_id = None
        try:
            price = await _post_only_buy_price(client)
            order = await client.place_order(
                SYMBOL,
                side="Buy",
                orderQty=qty,
                ordType="Limit",
                price=price,
                execInst="ParticipateDoNotInitiate",
                clOrdID=_client_id(),
                text="dcex stateful generic",
            )
            order_id = order["orderID"]
            await _assert_order_visible(client, order_id)
            assert await _amend_order_or_skip(client, order_id, price - 1.0) is not None
            assert (
                await _cancel_order_if_present(
                    client,
                    order_id,
                    text="dcex stateful cancel",
                )
                is not None
            )
            order_id = None
        finally:
            if order_id is not None:
                await _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = await client.place_limit_order(
                SYMBOL,
                side="Buy",
                orderQty=qty,
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
                await _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = await client.place_post_only_order(
                SYMBOL,
                side="Buy",
                orderQty=qty,
                price=await _post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert await _cancel_order_if_present(client, order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = await client.place_post_only_buy_order(
                SYMBOL,
                orderQty=qty,
                price=await _post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert await _cancel_order_if_present(client, order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = await client.place_post_only_sell_order(
                SYMBOL,
                orderQty=qty,
                price=await _post_only_sell_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert await _cancel_order_if_present(client, order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await _cancel_order_if_present(client, order_id)

        assert await client.place_market_buy_order(SYMBOL, qty, clOrdID=_client_id()) is not None
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert await client.place_market_sell_order(SYMBOL, qty, clOrdID=_client_id()) is not None
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert await client.place_market_order(SYMBOL, "Buy", qty, clOrdID=_client_id()) is not None
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await client.place_limit_buy_order(
                SYMBOL,
                qty,
                await _fillable_buy_price(client),
                clOrdID=_client_id(),
            )
            is not None
        )
        assert await _wait_for_position_or_skip(client, sign=1, action="limit buy") > 0
        await _close_position(client)

        assert (
            await client.place_limit_sell_order(
                SYMBOL,
                qty,
                await _fillable_sell_price(client),
                clOrdID=_client_id(),
            )
            is not None
        )
        assert await _wait_for_position_or_skip(client, sign=-1, action="limit sell") < 0
        await _close_position(client)

        assert await client.get_order(product_symbol=SYMBOL, count=10, reverse=True) is not None
    finally:
        await _cleanup(client)

    assert not await _open_orders(client)
    assert await _position_qty(client) == 0


@pytest.mark.private
async def test_async_trading_read_endpoints(client):
    assert await client.get_executions(product_symbol=SYMBOL, count=5) is not None
    assert await client.get_trade_history(product_symbol=SYMBOL, count=5) is not None
    assert await client.get_trading_volume() is not None
