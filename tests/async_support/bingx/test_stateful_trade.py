# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import logging
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bingx.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
SWAP_SYMBOL = "BTC-USDT-SWAP"
FUND_ACCOUNT = "fund"
SPOT_ACCOUNT = "spot"
SWAP_ACCOUNT = "USDTMPerp"
LOGGER = logging.getLogger(__name__)
SPOT_NOTIONAL_BUFFER = Decimal("1.15")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real BingX order tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BINGX_API_KEY,
        api_secret=BINGX_API_SECRET,
        timeout=20,
    ) as client_instance:
        yield client_instance


def _dec(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _client_order_id() -> str:
    return f"dcex{uuid.uuid4().hex[:16]}"


def _skip_if_rate_limited(exc: FailedRequestError) -> None:
    message = str(exc)
    if "100410" in message or "endpoint trigger frequency limit" in message:
        pytest.skip("BingX temporarily rate-limited this endpoint.")


async def _swap_available_usdt(client: Client) -> Decimal:
    data = (await client.get_swap_account_balance()).get("data", [])
    if isinstance(data, list):
        for item in data:
            if item.get("asset") == "USDT":
                return _dec(item.get("availableMargin"))
        return Decimal("0")
    balance = data.get("balance", {}) if isinstance(data, dict) else {}
    return _dec(balance.get("availableMargin"))


async def _spot_available(client: Client, asset: str) -> Decimal:
    try:
        balances = (await client.get_spot_account_balance()).get("data", {}).get("balances", [])
    except FailedRequestError as exc:
        _skip_if_rate_limited(exc)
        raise
    for item in balances:
        if item.get("asset") == asset:
            return _dec(item.get("free"))
    return Decimal("0")


async def _fund_available(client: Client, asset: str) -> Decimal:
    balances = (
        (await client.get_fund_account_balance(asset=asset)).get("data", {}).get("assets", [])
    )
    for item in balances:
        if item.get("asset") == asset:
            return _dec(item.get("free"))
    return Decimal("0")


async def _transferable(
    client: Client,
    from_account: str,
    to_account: str,
    asset: str,
) -> Decimal:
    data = (
        await client.get_transferable_coins(
            fromAccount=from_account,
            toAccount=to_account,
        )
    ).get("data", {})
    for item in data.get("coins", []):
        if item.get("asset") == asset:
            return _dec(item.get("availableTransferAmount", item.get("amount")))
    return Decimal("0")


async def _account_available_usdt(client: Client, account: str) -> Decimal:
    if account == FUND_ACCOUNT:
        return await _fund_available(client, "USDT")
    if account == SPOT_ACCOUNT:
        return await _spot_available(client, "USDT")
    if account == SWAP_ACCOUNT:
        return await _swap_available_usdt(client)
    return Decimal("0")


def _transfer_sources(to_account: str) -> tuple[str, ...]:
    if to_account == SPOT_ACCOUNT:
        return (FUND_ACCOUNT, SWAP_ACCOUNT)
    if to_account == SWAP_ACCOUNT:
        return (FUND_ACCOUNT, SPOT_ACCOUNT)
    return (FUND_ACCOUNT, SPOT_ACCOUNT, SWAP_ACCOUNT)


async def _spot_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = (await client.get_spot_orderbook(product_symbol=SPOT_SYMBOL, limit=5))["data"]
    return _dec(data["bids"][0][0]), _dec(data["asks"][0][0])


async def _swap_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = (await client.get_orderbook(product_symbol=SWAP_SYMBOL, limit=5))["data"]
    return _dec(data["bids"][0][0]), _dec(data["asks"][0][0])


async def _asset_transfer(
    client: Client,
    from_account: str,
    to_account: str,
    asset: str,
    amount: Decimal,
) -> None:
    assert (
        await client.asset_transfer(
            fromAccount=from_account,
            toAccount=to_account,
            asset=asset,
            amount=_fmt(amount),
        )
        is not None
    )
    await asyncio.sleep(2)


async def _ensure_usdt_for_account(
    client: Client,
    to_account: str,
    required: Decimal,
    current_available: Decimal,
) -> None:
    if current_available >= required:
        return

    for from_account in _transfer_sources(to_account):
        current_available = await _account_available_usdt(client, to_account)
        if current_available >= required:
            return
        amount = (required - current_available) * Decimal("1.01")
        try:
            transferable = await _transferable(client, from_account, to_account, "USDT")
            source_available = await _account_available_usdt(client, from_account)
        except Exception as error:
            LOGGER.info(
                "Skipping BingX transfer route %s->%s; transferable amount unavailable: %s",
                from_account,
                to_account,
                error,
            )
            continue
        available = min(transferable, source_available)
        if available <= 0:
            continue

        try:
            await _asset_transfer(client, from_account, to_account, "USDT", min(amount, available))
        except Exception as error:
            LOGGER.info(
                "Skipping BingX transfer route %s->%s; transfer failed: %s",
                from_account,
                to_account,
                error,
            )
            continue

    if await _account_available_usdt(client, to_account) < required:
        pytest.skip(f"Insufficient transferable BingX USDT to transfer into {to_account}.")


async def _swap_open_orders(client: Client) -> list[dict]:
    data = (await client.get_open_orders(product_symbol=SWAP_SYMBOL)).get("data", {})
    orders = data.get("orders", []) if isinstance(data, dict) else []
    return orders if isinstance(orders, list) else []


async def _spot_open_orders(client: Client) -> list[dict]:
    data = (await client.get_spot_open_orders(product_symbol=SPOT_SYMBOL)).get("data", {})
    orders = data.get("orders", []) if isinstance(data, dict) else []
    return orders if isinstance(orders, list) else []


def _is_missing_spot_order_error(exc: FailedRequestError) -> bool:
    message = str(exc).lower()
    return "100400" in message and (
        "order not exist" in message or "no any pending order" in message
    )


async def _cancel_spot_order(client: Client, order_id: str) -> object:
    for attempt in range(3):
        try:
            return await client.cancel_spot_order(
                product_symbol=SPOT_SYMBOL,
                orderId=order_id,
            )
        except FailedRequestError as exc:
            message = str(exc).lower()
            if _is_missing_spot_order_error(exc):
                return {"code": 0, "data": {}}
            if "same order can only be submitted once per second" not in message:
                raise
            if attempt == 2:
                raise
            await asyncio.sleep(1.2)
    raise AssertionError("unreachable")


async def _cancel_spot_batch_orders_if_present(client: Client, order_ids: list[str]) -> object:
    try:
        return await client.cancel_spot_batch_orders(
            product_symbol=SPOT_SYMBOL,
            orderIds=order_ids,
        )
    except FailedRequestError as exc:
        if _is_missing_spot_order_error(exc):
            return {"code": 0, "data": {}}
        raise


async def _positions(client: Client) -> list[dict]:
    data = (await client.get_open_positions(product_symbol=SWAP_SYMBOL)).get("data", [])
    return data if isinstance(data, list) else []


async def _skip_if_existing_state(client: Client) -> None:
    if await _spot_open_orders(client):
        pytest.skip("BTC-USDT spot already has open orders; not touching unrelated orders.")
    if await _swap_open_orders(client):
        pytest.skip("BTC-USDT swap already has open orders; not touching unrelated orders.")
    if await _positions(client):
        pytest.skip("BTC-USDT swap already has a position; not changing exposure.")


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("bingx", SPOT_SYMBOL)
    return (
        _dec(details["price_precision"], "0.01"),
        _dec(details["size_precision"], "0.000001"),
        max(_dec(details["min_notional"], "0.5"), Decimal("0.5")),
    )


def _spot_min_size(client: Client) -> Decimal:
    details = client.ptm.get_trading_details("bingx", SPOT_SYMBOL)
    return max(_dec(details.get("min_size"), "0.000008"), Decimal("0.000008"))


async def _spot_order_params(client: Client) -> tuple[str, str]:
    tick, step, min_notional = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    quantity = _round_to_step(min_notional * SPOT_NOTIONAL_BUFFER / price, step, ROUND_UP)
    quantity = max(quantity, _spot_min_size(client))
    return _fmt(quantity), _fmt(price)


async def _spot_market_quote_amount(client: Client) -> Decimal:
    _, step, min_notional = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    min_quantity = _round_to_step(
        max(_spot_min_size(client), min_notional / best_ask) * SPOT_NOTIONAL_BUFFER,
        step,
        ROUND_UP,
    )
    return min_quantity * best_ask * SPOT_NOTIONAL_BUFFER


async def _spot_fillable_limit_buy_params(client: Client) -> tuple[str, str]:
    tick, step, _ = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    price = _round_to_step(best_ask + tick, tick, ROUND_UP)
    quantity = _round_to_step((await _spot_market_quote_amount(client)) / price, step, ROUND_UP)
    quantity = max(quantity, _spot_min_size(client))
    return _fmt(quantity), _fmt(price)


async def _spot_fillable_limit_sell_price(client: Client) -> str:
    tick, _, _ = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_bid - tick, tick, ROUND_DOWN))


async def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _ = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _spot_trade_delta(client: Client, before: Decimal, asset: str) -> Decimal:
    return max(await _spot_available(client, asset) - before, Decimal("0"))


async def _spot_sell_quantity(client: Client, quantity: Decimal) -> str:
    _, step, _ = _spot_details(client)
    return _fmt(_round_to_step(quantity, step, ROUND_DOWN))


async def _ensure_spot_usdt(client: Client, quantity: str, price: str) -> None:
    required = Decimal(quantity) * Decimal(price)
    await _ensure_usdt_for_account(
        client=client,
        to_account=SPOT_ACCOUNT,
        required=required,
        current_available=await _spot_available(client, "USDT"),
    )
    if await _spot_available(client, "USDT") < required:
        pytest.skip("BingX spot USDT remains insufficient after internal transfer.")


async def _spot_market_buy_delta(client: Client, quote_amount: Decimal) -> Decimal:
    before_btc = await _spot_available(client, "BTC")
    assert (
        await client.place_spot_market_buy_order(
            product_symbol=SPOT_SYMBOL,
            quoteOrderQty=_fmt(quote_amount),
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    await asyncio.sleep(3)
    return await _spot_trade_delta(client, before_btc, "BTC")


async def _swap_current_price(client: Client) -> Decimal:
    return _dec((await client.get_ticker(product_symbol=SWAP_SYMBOL))["data"]["lastPrice"])


def _swap_details(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("bingx", SWAP_SYMBOL)
    return (
        _dec(details["price_precision"], "0.1"),
        _dec(details["size_precision"], "0.0001"),
        max(_dec(details["min_size"], "0.0001"), Decimal("0.0001")),
        max(_dec(details["min_notional"], "2"), Decimal("2")),
    )


async def _swap_order_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _swap_details(client)
    best_bid, _ = await _swap_orderbook_prices(client)
    price = _round_to_step(best_bid * Decimal("0.95"), tick, ROUND_DOWN)
    quantity = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(quantity, min_size)), _fmt(price)


async def _swap_fillable_limit_buy_price(client: Client) -> float:
    tick, _, _, _ = _swap_details(client)
    _, best_ask = await _swap_orderbook_prices(client)
    price = max(best_ask + tick, best_ask * Decimal("1.002"))
    price = _round_to_step(price, tick, ROUND_UP)
    return float(_fmt(price))


async def _swap_fillable_limit_sell_price(client: Client) -> float:
    tick, _, _, _ = _swap_details(client)
    best_bid, _ = await _swap_orderbook_prices(client)
    price = min(best_bid - tick, best_bid * Decimal("0.998"))
    price = _round_to_step(price, tick, ROUND_DOWN)
    return float(_fmt(price))


async def _swap_post_only_sell_price(client: Client) -> str:
    tick, _, _, _ = _swap_details(client)
    _, best_ask = await _swap_orderbook_prices(client)
    price = max(best_ask + tick, best_ask * Decimal("1.001"))
    return _fmt(_round_to_step(price, tick, ROUND_UP))


async def _ensure_swap_usdt_for_quantity(client: Client, quantity: str) -> None:
    required = (
        Decimal(quantity) * await _swap_current_price(client) / Decimal("10") * Decimal("1.05")
    )
    await _ensure_usdt_for_account(
        client=client,
        to_account=SWAP_ACCOUNT,
        required=required,
        current_available=await _swap_available_usdt(client),
    )
    if await _swap_available_usdt(client) < required:
        pytest.skip("BingX swap USDT remains insufficient after internal transfer.")


def _position_id(positions: list[dict], side: str) -> str | None:
    for position in positions:
        if position.get("positionSide") == side and _dec(
            position.get("positionAmt", position.get("positionAmount", "0"))
        ) != Decimal("0"):
            position_id = position.get("positionId")
            return str(position_id) if position_id is not None else None
    return None


async def _wait_for_position(client: Client, side: str) -> str | None:
    for _ in range(10):
        position_id = _position_id(await _positions(client), side)
        if position_id is not None:
            return position_id
        await asyncio.sleep(1)
    return None


async def _wait_for_position_or_skip(client: Client, side: str, action: str) -> str:
    position_id = await _wait_for_position(client, side)
    if position_id is None:
        pytest.skip(f"BingX {action} did not fill before timeout.")
    return position_id


async def _cleanup(client: Client) -> None:
    with suppress(Exception):
        if await _spot_open_orders(client):
            await client.cancel_spot_open_orders(product_symbol=SPOT_SYMBOL)
            await asyncio.sleep(1)

    with suppress(Exception):
        if await _swap_open_orders(client):
            await client.cancel_swap_all_orders(product_symbol=SWAP_SYMBOL)
            await asyncio.sleep(1)

    with suppress(Exception):
        if await _positions(client):
            await client.close_swap_all_positions(product_symbol=SWAP_SYMBOL)
            await asyncio.sleep(3)

    with suppress(Exception):
        btc = await _spot_available(client, "BTC")
        if btc > Decimal("0"):
            sell_quantity = await _spot_sell_quantity(client, btc)
            if Decimal(sell_quantity) > 0:
                await client.place_spot_market_sell_order(
                    product_symbol=SPOT_SYMBOL,
                    quantity=sell_quantity,
                    clientOrderId=_client_order_id(),
                )
                await asyncio.sleep(3)

    with suppress(Exception):
        spot_usdt = await _spot_available(client, "USDT")
        if spot_usdt > Decimal("0.0001"):
            await _asset_transfer(client, SPOT_ACCOUNT, FUND_ACCOUNT, "USDT", spot_usdt)

    with suppress(Exception):
        spot_btc = await _spot_available(client, "BTC")
        if spot_btc > Decimal("0"):
            await _asset_transfer(client, SPOT_ACCOUNT, FUND_ACCOUNT, "BTC", spot_btc)

    with suppress(Exception):
        swap_usdt = await _swap_available_usdt(client)
        if swap_usdt > Decimal("0.0001"):
            await _asset_transfer(client, SWAP_ACCOUNT, FUND_ACCOUNT, "USDT", swap_usdt)


async def _exercise_spot_stateful_methods(client: Client) -> None:
    quantity, price = await _spot_order_params(client)
    await _ensure_spot_usdt(client, quantity, price)

    order_id = None
    try:
        order = await client.place_spot_order(
            SPOT_SYMBOL,
            side="BUY",
            type_="LIMIT",
            timeInForce="POC",
            quantity=quantity,
            price=price,
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["orderId"]
        assert await client.get_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id) is not None
        assert await _cancel_spot_order(client, order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await _cancel_spot_order(client, order_id)

    order_id = None
    try:
        order = await client.place_spot_limit_order(
            SPOT_SYMBOL,
            side="BUY",
            quantity=quantity,
            price=price,
            timeInForce="POC",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_spot_open_orders(product_symbol=SPOT_SYMBOL) is not None
        order_id = None
        await asyncio.sleep(1)
    finally:
        if order_id is not None:
            await _cancel_spot_order(client, order_id)

    order_id = None
    try:
        order = await client.place_spot_post_only_order(
            SPOT_SYMBOL,
            side="BUY",
            quantity=quantity,
            price=price,
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["orderId"]
        assert await _cancel_spot_order(client, order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await _cancel_spot_order(client, order_id)

    order_id = None
    try:
        order = await client.place_spot_post_only_buy_order(
            SPOT_SYMBOL,
            quantity=quantity,
            price=price,
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["orderId"]
        assert await _cancel_spot_order(client, order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await _cancel_spot_order(client, order_id)

    order_id = None
    try:
        order = await client.place_spot_batch_order(
            [
                {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": quantity,
                    "price": price,
                    "timeInForce": "POC",
                    "newClientOrderId": _client_order_id(),
                }
            ]
        )
        orders = order.get("data", {}).get("orders", [])
        if orders:
            order_id = orders[0]["orderId"]
            assert await _cancel_spot_batch_orders_if_present(client, [order_id]) is not None
            order_id = None
    finally:
        if order_id is not None:
            await _cancel_spot_order(client, order_id)

    quote_amount = await _spot_market_quote_amount(client)
    await _ensure_usdt_for_account(
        client,
        SPOT_ACCOUNT,
        quote_amount,
        await _spot_available(client, "USDT"),
    )
    bought = await _spot_market_buy_delta(client, quote_amount)
    sell_quantity = await _spot_sell_quantity(client, bought)
    assert Decimal(sell_quantity) > 0
    assert (
        await client.place_spot_market_sell_order(
            product_symbol=SPOT_SYMBOL,
            quantity=sell_quantity,
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    await asyncio.sleep(3)

    quantity, price = await _spot_fillable_limit_buy_params(client)
    await _ensure_spot_usdt(client, quantity, price)
    before_btc = await _spot_available(client, "BTC")
    try:
        assert (
            await client.place_spot_limit_buy_order(
                SPOT_SYMBOL,
                quantity=quantity,
                price=price,
                timeInForce="GTC",
                clientOrderId=_client_order_id(),
            )
            is not None
        )
        await asyncio.sleep(3)
        bought = await _spot_trade_delta(client, before_btc, "BTC")
        sell_quantity = await _spot_sell_quantity(client, bought)
        assert Decimal(sell_quantity) > 0
        assert (
            await client.place_spot_limit_sell_order(
                SPOT_SYMBOL,
                quantity=sell_quantity,
                price=await _spot_fillable_limit_sell_price(client),
                timeInForce="GTC",
                clientOrderId=_client_order_id(),
            )
            is not None
        )
    finally:
        if await _spot_open_orders(client):
            await client.cancel_spot_open_orders(product_symbol=SPOT_SYMBOL)
        remaining = await _spot_trade_delta(client, before_btc, "BTC")
        sell_quantity = await _spot_sell_quantity(client, remaining)
        if Decimal(sell_quantity) > 0:
            await client.place_spot_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=sell_quantity,
                clientOrderId=_client_order_id(),
            )

    quote_amount = await _spot_market_quote_amount(client)
    await _ensure_usdt_for_account(
        client,
        SPOT_ACCOUNT,
        quote_amount,
        await _spot_available(client, "USDT"),
    )
    before_btc = await _spot_available(client, "BTC")
    order_id = None
    try:
        bought = await _spot_market_buy_delta(client, quote_amount)
        sell_quantity = await _spot_sell_quantity(client, bought)
        assert Decimal(sell_quantity) > 0
        order = await client.place_spot_post_only_sell_order(
            SPOT_SYMBOL,
            quantity=sell_quantity,
            price=await _spot_post_only_sell_price(client),
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["orderId"]
        assert await client.get_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id) is not None
    finally:
        if order_id is not None:
            await _cancel_spot_order(client, order_id)
        remaining = await _spot_trade_delta(client, before_btc, "BTC")
        sell_quantity = await _spot_sell_quantity(client, remaining)
        if Decimal(sell_quantity) > 0:
            await client.place_spot_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=sell_quantity,
                clientOrderId=_client_order_id(),
            )


async def _exercise_swap_stateful_methods(client: Client) -> None:
    margin = (await client.get_margin_type(product_symbol=SWAP_SYMBOL))["data"]["marginType"]
    leverage = (await client.get_leverage(product_symbol=SWAP_SYMBOL))["data"]
    mode = (await client.get_position_mode())["data"]["dualSidePosition"]
    assert (
        await client.change_margin_type(product_symbol=SWAP_SYMBOL, marginType=margin) is not None
    )
    assert (
        await client.set_leverage(
            product_symbol=SWAP_SYMBOL,
            side="LONG",
            leverage=int(leverage["longLeverage"]),
        )
        is not None
    )
    assert (
        await client.set_leverage(
            product_symbol=SWAP_SYMBOL,
            side="SHORT",
            leverage=int(leverage["shortLeverage"]),
        )
        is not None
    )
    assert await client.set_position_mode(dualSidePosition=mode) is not None

    quantity, price = await _swap_order_params(client)
    await _ensure_swap_usdt_for_quantity(client, quantity)
    assert (
        await client.test_swap_order(
            product_symbol=SWAP_SYMBOL,
            type_="LIMIT",
            side="BUY",
            positionSide="LONG",
            quantity=float(quantity),
            price=float(price),
            timeInForce="PostOnly",
            clientOrderId=_client_order_id(),
        )
        is not None
    )

    order_id = None
    try:
        order = await client.place_swap_order(
            SWAP_SYMBOL,
            type_="LIMIT",
            side="BUY",
            positionSide="LONG",
            quantity=float(quantity),
            price=float(price),
            timeInForce="PostOnly",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["order"]["orderId"]
        assert (
            await client.get_order_detail(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
        )
        assert (
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    order_id = None
    try:
        order = await client.place_swap_limit_order(
            SWAP_SYMBOL,
            side="BUY",
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            timeInForce="PostOnly",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["order"]["orderId"]
        assert await client.cancel_swap_all_orders(product_symbol=SWAP_SYMBOL) is not None
        order_id = None
        await asyncio.sleep(1)
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    order_id = None
    try:
        order = await client.place_swap_post_only_order(
            SWAP_SYMBOL,
            side="BUY",
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["order"]["orderId"]
        assert (
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    order_id = None
    try:
        order = await client.place_swap_post_only_buy_order(
            SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["order"]["orderId"]
        assert (
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    order_id = None
    try:
        high_price = await _swap_post_only_sell_price(client)
        order = await client.place_swap_post_only_sell_order(
            SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(high_price),
            positionSide="SHORT",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["order"]["orderId"]
        assert (
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    order_id = None
    try:
        order = await client.place_swap_batch_order(
            [
                {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "positionSide": "LONG",
                    "quantity": quantity,
                    "price": price,
                    "timeInForce": "PostOnly",
                    "clientOrderId": _client_order_id(),
                }
            ]
        )
        orders = order.get("data", {}).get("orders", [])
        if orders:
            order_id = orders[0]["orderId"]
            assert (
                await client.cancel_swap_batch_order(
                    product_symbol=SWAP_SYMBOL,
                    orderIdList=[order_id],
                )
                is not None
            )
            order_id = None
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    order_id = None
    try:
        order = await client.place_swap_post_only_buy_order(
            product_symbol=SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            clientOrderId=_client_order_id(),
        )
        order_id = order["data"]["order"]["orderId"]
        replacement_price = _fmt(Decimal(price) * Decimal("0.99"))
        assert (
            await client.replace_swap_order(
                product_symbol=SWAP_SYMBOL,
                orderId=str(order_id),
                cancelReplaceMode="STOP_ON_FAILURE",
                type_="LIMIT",
                side="BUY",
                positionSide="LONG",
                quantity=float(quantity),
                price=float(replacement_price),
                timeInForce="PostOnly",
            )
            is not None
        )
        order_id = None
        await client.cancel_swap_all_orders(product_symbol=SWAP_SYMBOL)
        await asyncio.sleep(1)
    finally:
        if order_id is not None:
            await client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)

    await _ensure_swap_usdt_for_quantity(client, quantity)
    assert (
        await client.place_swap_market_order(
            SWAP_SYMBOL,
            side="BUY",
            quantity=float(quantity),
            positionSide="LONG",
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    position_id = await _wait_for_position(client, "LONG")
    assert position_id is not None
    assert await client.close_swap_position(positionId=position_id) is not None
    await asyncio.sleep(3)

    await _ensure_swap_usdt_for_quantity(client, quantity)
    assert (
        await client.place_swap_market_buy_order(
            SWAP_SYMBOL,
            quantity=float(quantity),
            positionSide="LONG",
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    position_id = await _wait_for_position(client, "LONG")
    assert position_id is not None
    assert await client.close_swap_position(positionId=position_id) is not None
    await asyncio.sleep(3)

    await _ensure_swap_usdt_for_quantity(client, quantity)
    assert (
        await client.place_swap_market_sell_order(
            SWAP_SYMBOL,
            quantity=float(quantity),
            positionSide="SHORT",
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    assert await _wait_for_position(client, "SHORT") is not None
    assert await client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None
    await asyncio.sleep(3)

    await _ensure_swap_usdt_for_quantity(client, quantity)
    assert (
        await client.place_swap_limit_buy_order(
            SWAP_SYMBOL,
            quantity=float(quantity),
            price=await _swap_fillable_limit_buy_price(client),
            positionSide="LONG",
            timeInForce="GTC",
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    await _wait_for_position_or_skip(client, "LONG", "fillable limit buy")
    assert await client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None
    await asyncio.sleep(3)

    await _ensure_swap_usdt_for_quantity(client, quantity)
    assert (
        await client.place_swap_limit_sell_order(
            SWAP_SYMBOL,
            quantity=float(quantity),
            price=await _swap_fillable_limit_sell_price(client),
            positionSide="SHORT",
            timeInForce="GTC",
            clientOrderId=_client_order_id(),
        )
        is not None
    )
    await _wait_for_position_or_skip(client, "SHORT", "fillable limit sell")
    assert await client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None
    await asyncio.sleep(3)


async def test_async_stateful_order_transfer_and_position_lifecycle(client):
    await _skip_if_existing_state(client)
    try:
        await _exercise_spot_stateful_methods(client)
        await _exercise_swap_stateful_methods(client)
    finally:
        await _cleanup(client)

    assert not await _spot_open_orders(client)
    assert not await _swap_open_orders(client)
    assert not await _positions(client)


@pytest.mark.private
async def test_async_trade_read_endpoints(client):
    await _skip_if_existing_state(client)

    assert await client.get_order_history(product_symbol=SWAP_SYMBOL, limit=5) is not None
    assert await client.get_spot_order_history(product_symbol=SPOT_SYMBOL, pageSize=5) is not None
    assert await client.get_spot_my_trades(product_symbol=SPOT_SYMBOL, limit=5) is not None
    assert await client.get_spot_commission_rate(product_symbol=SPOT_SYMBOL) is not None
