import asyncio
from decimal import Decimal, ROUND_DOWN, ROUND_UP
import os
import time

from dotenv import load_dotenv
import pytest
import pytest_asyncio

from dcex.async_support.binance.client import Client

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
SPOT_ROUND_TRIP_QUOTE = Decimal("12")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    ) as client_instance:
        yield client_instance


def _filters(exchange_info: dict) -> dict[str, dict]:
    return {item["filterType"]: item for item in exchange_info["symbols"][0]["filters"]}


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    return (value / step).to_integral_value(rounding=rounding) * step


def _format_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _minimum_notional(filters: dict[str, dict], default: Decimal) -> Decimal:
    if "NOTIONAL" in filters:
        return Decimal(str(filters["NOTIONAL"].get("minNotional", default)))
    if "MIN_NOTIONAL" in filters:
        return Decimal(str(filters["MIN_NOTIONAL"].get("minNotional", default)))
    return default


async def _symbol_exchange_info(client: Client, product_symbol: str, *, futures: bool) -> dict:
    exchange_info = (
        await client.get_futures_exchange_info()
        if futures
        else await client.get_spot_exchange_info(product_symbol=product_symbol)
    )
    if futures:
        symbol = client.ptm.get_exchange_symbol("binance", product_symbol)
        exchange_info["symbols"] = [
            item for item in exchange_info["symbols"] if item["symbol"] == symbol
        ]
    return exchange_info


async def _step_size(client: Client, product_symbol: str, *, futures: bool) -> Decimal:
    return Decimal(
        _filters(await _symbol_exchange_info(client, product_symbol, futures=futures))["LOT_SIZE"][
            "stepSize"
        ]
    )


async def _tick_size(client: Client, product_symbol: str, *, futures: bool) -> Decimal:
    return Decimal(
        _filters(await _symbol_exchange_info(client, product_symbol, futures=futures))[
            "PRICE_FILTER"
        ]["tickSize"]
    )


async def _safe_buy_order_params(
    client: Client, product_symbol: str, *, futures: bool
) -> tuple[str, str]:
    filters = _filters(await _symbol_exchange_info(client, product_symbol, futures=futures))
    price_filter = filters["PRICE_FILTER"]
    lot_filter = filters["LOT_SIZE"]
    tick_size = Decimal(price_filter["tickSize"])
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("10"))

    current_price = (
        Decimal((await client.get_futures_ticker(product_symbol=product_symbol))["bidPrice"])
        if futures
        else Decimal((await client.get_spot_price(product_symbol=product_symbol))["price"])
    )
    price = _round_to_step(current_price * Decimal("0.90"), tick_size, ROUND_DOWN)
    required_notional = max(min_notional * Decimal("1.10"), Decimal("11"))
    quantity = _round_to_step(required_notional / price, step_size, ROUND_UP)
    quantity = max(quantity, min_qty)

    return _format_decimal(quantity), _format_decimal(price)


async def _safe_market_quantity(client: Client, product_symbol: str) -> str:
    filters = _filters(await _symbol_exchange_info(client, product_symbol, futures=True))
    lot_filter = filters["LOT_SIZE"]
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("100"))
    price = Decimal((await client.get_futures_ticker(product_symbol=product_symbol))["askPrice"])
    required_notional = max(min_notional * Decimal("1.10"), Decimal("110"))
    quantity = _round_to_step(required_notional / price, step_size, ROUND_UP)
    return _format_decimal(max(quantity, min_qty))


async def _spot_free(client: Client, asset: str) -> Decimal:
    account = await client.get_account_balance(market_type="spot")
    for balance in account["balances"]:
        if balance["asset"] == asset:
            return Decimal(balance["free"])
    return Decimal("0")


async def _futures_position_amt(client: Client, product_symbol: str) -> Decimal:
    positions = await client.get_future_position(product_symbol=product_symbol)
    if not positions:
        return Decimal("0")
    return Decimal(positions[0]["positionAmt"])


async def _close_futures_position(client: Client, product_symbol: str) -> None:
    amount = await _futures_position_amt(client, product_symbol)
    if amount == 0:
        return
    await client.place_order(
        product_symbol=product_symbol,
        side="SELL" if amount > 0 else "BUY",
        type_="MARKET",
        quantity=_format_decimal(abs(amount)),
        reduceOnly="true",
    )


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_post_only_order_lifecycle(client):
    quantity, price = await _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    test_res = await client.test_order(
        product_symbol=SPOT_SYMBOL,
        side="BUY",
        type_="LIMIT_MAKER",
        quantity=quantity,
        price=price,
    )
    assert test_res is not None

    order = None
    try:
        order = await client.place_post_only_limit_buy_order(
            product_symbol=SPOT_SYMBOL,
            quantity=quantity,
            price=price,
        )
        order_id = int(order["orderId"])
        queried = await client.get_order(product_symbol=SPOT_SYMBOL, orderId=order_id)
        assert queried["orderId"] == order_id
        assert isinstance(await client.get_open_orders(product_symbol=SPOT_SYMBOL), list)
    finally:
        if order is not None:
            await client.cancel_order(product_symbol=SPOT_SYMBOL, orderId=int(order["orderId"]))

    assert isinstance(await client.get_all_orders(product_symbol=SPOT_SYMBOL, limit=1), list)
    assert isinstance(await client.get_account_trades(product_symbol=SPOT_SYMBOL, limit=1), list)


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_cancel_all_open_orders(client):
    if await client.get_open_orders(product_symbol=SPOT_SYMBOL):
        pytest.skip("BTCUSDT spot already has open orders; not canceling unrelated orders.")

    quantity, price = await _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    await client.place_post_only_limit_buy_order(
        product_symbol=SPOT_SYMBOL,
        quantity=quantity,
        price=price,
    )

    await client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)
    assert await client.get_open_orders(product_symbol=SPOT_SYMBOL) == []


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_market_order_round_trip(client):
    step_size = await _step_size(client, SPOT_SYMBOL, futures=False)
    btc_before = await _spot_free(client, "BTC")
    order = await client.place_order(
        product_symbol=SPOT_SYMBOL,
        side="BUY",
        type_="MARKET",
        quoteOrderQty=_format_decimal(SPOT_ROUND_TRIP_QUOTE),
        newOrderRespType="FULL",
    )
    assert order["status"] == "FILLED"

    btc_after = await _spot_free(client, "BTC")
    acquired = _round_to_step(btc_after - btc_before, step_size, ROUND_DOWN)
    assert acquired > 0

    sell = await client.place_market_sell_order(
        product_symbol=SPOT_SYMBOL,
        quantity=_format_decimal(acquired),
        newOrderRespType="FULL",
    )
    assert sell["status"] == "FILLED"


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_post_only_order_lifecycle(client):
    quantity, price = await _safe_buy_order_params(client, FUTURES_SYMBOL, futures=True)
    leverage = await client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)
    assert leverage["leverage"] == 20
    test_res = await client.test_order(
        product_symbol=FUTURES_SYMBOL,
        side="BUY",
        type_="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce="GTX",
    )
    assert test_res is not None

    order = None
    try:
        order = await client.place_post_only_limit_buy_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            price=price,
        )
        order_id = int(order["orderId"])
        queried = await client.get_order(product_symbol=FUTURES_SYMBOL, orderId=order_id)
        assert queried["orderId"] == order_id
        assert isinstance(await client.get_open_orders(product_symbol=FUTURES_SYMBOL), list)
        assert isinstance(await client.get_all_open_orders(product_symbol=FUTURES_SYMBOL), list)
    finally:
        if order is not None:
            await client.cancel_order(product_symbol=FUTURES_SYMBOL, orderId=int(order["orderId"]))

    assert isinstance(await client.get_all_orders(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(await client.get_account_trades(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(await client.get_future_position(product_symbol=FUTURES_SYMBOL), list)


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_cancel_all_open_orders(client):
    if await client.get_open_orders(product_symbol=FUTURES_SYMBOL):
        pytest.skip("BTCUSDT futures already has open orders; not canceling unrelated orders.")
    if await _futures_position_amt(client, FUTURES_SYMBOL) != 0:
        pytest.skip("BTCUSDT futures already has a position; not changing unrelated exposure.")

    quantity, price = await _safe_buy_order_params(client, FUTURES_SYMBOL, futures=True)
    await client.place_post_only_limit_buy_order(
        product_symbol=FUTURES_SYMBOL,
        quantity=quantity,
        price=price,
    )

    await client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
    assert await client.get_open_orders(product_symbol=FUTURES_SYMBOL) == []


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_market_long_round_trip(client):
    if await _futures_position_amt(client, FUTURES_SYMBOL) != 0:
        pytest.skip("BTCUSDT futures already has a position; not changing unrelated exposure.")

    quantity = await _safe_market_quantity(client, FUTURES_SYMBOL)
    try:
        open_order = await client.place_market_buy_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert open_order["status"] == "FILLED"
    finally:
        await _close_futures_position(client, FUTURES_SYMBOL)

    assert await _futures_position_amt(client, FUTURES_SYMBOL) == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_market_short_round_trip(client):
    if await _futures_position_amt(client, FUTURES_SYMBOL) != 0:
        pytest.skip("BTCUSDT futures already has a position; not changing unrelated exposure.")

    quantity = await _safe_market_quantity(client, FUTURES_SYMBOL)
    try:
        open_order = await client.place_market_sell_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert open_order["status"] == "FILLED"
    finally:
        await _close_futures_position(client, FUTURES_SYMBOL)

    assert await _futures_position_amt(client, FUTURES_SYMBOL) == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_advanced_order_validation(client):
    spot_quantity, spot_price = await _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    spot_tick = await _tick_size(client, SPOT_SYMBOL, futures=False)
    spot_stop = _format_decimal(
        _round_to_step(Decimal(spot_price) * Decimal("1.05"), spot_tick, ROUND_UP)
    )
    assert (
        await client.test_order(
            product_symbol=SPOT_SYMBOL,
            side="BUY",
            type_="STOP_LOSS_LIMIT",
            quantity=spot_quantity,
            price=spot_stop,
            stopPrice=spot_stop,
            timeInForce="GTC",
        )
        is not None
    )

    futures_quantity = await _safe_market_quantity(client, FUTURES_SYMBOL)
    futures_price = Decimal(
        (await client.get_futures_ticker(product_symbol=FUTURES_SYMBOL))["askPrice"]
    )
    futures_tick = await _tick_size(client, FUTURES_SYMBOL, futures=True)
    trigger_price = _format_decimal(
        _round_to_step(futures_price * Decimal("1.10"), futures_tick, ROUND_UP)
    )

    algo_order = None
    client_algo_id = f"dcx{int(time.time() * 1000)}"
    try:
        algo_order = await client.place_futures_algo_order(
            product_symbol=FUTURES_SYMBOL,
            side="BUY",
            type_="STOP_MARKET",
            quantity=futures_quantity,
            triggerPrice=trigger_price,
            clientAlgoId=client_algo_id,
            newOrderRespType="ACK",
        )
        await asyncio.sleep(0.5)
        queried = await client.get_futures_algo_order(clientAlgoId=client_algo_id)
        assert queried["clientAlgoId"] == client_algo_id
        assert isinstance(
            await client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL), list
        )
    finally:
        if algo_order is not None:
            await client.cancel_futures_algo_order(clientAlgoId=client_algo_id)

    assert isinstance(
        await client.get_all_futures_algo_orders(product_symbol=FUTURES_SYMBOL, limit=1), list
    )
