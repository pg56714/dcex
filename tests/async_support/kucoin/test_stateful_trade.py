# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.kucoin.client import Client

load_dotenv()

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
FUTURES_LEVERAGE = Decimal("20")
TRANSFER_BUFFER_USDT = Decimal("0.1")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real KuCoin order tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
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


def _fmt_transfer(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN).normalize(), "f")


def _client_oid() -> str:
    return f"dcex-{uuid.uuid4().hex}"


def _items(res: dict) -> list[dict]:
    data = res.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    return []


async def _available(client: Client, currency: str, type_: str) -> Decimal:
    res = await client.get_account_balance(currency=currency, type=type_)
    return sum((_dec(item.get("available")) for item in _items(res)), Decimal("0"))


async def _futures_available_usdt(client: Client) -> Decimal:
    data = (await client.get_futures_account(currency="USDT")).get("data")
    if not isinstance(data, dict):
        return Decimal("0")
    return _dec(data.get("availableBalance"))


async def _futures_position_size(client: Client) -> Decimal:
    data = (await client.get_futures_position(product_symbol=FUTURES_SYMBOL)).get("data")
    if not isinstance(data, dict):
        return Decimal("0")
    for key in ("currentQty", "size", "posQty", "quantity"):
        if key in data:
            return _dec(data.get(key))
    return Decimal("0")


async def _flex_transfer(
    client: Client,
    currency: str,
    amount: Decimal,
    from_account_type: str,
    to_account_type: str,
) -> None:
    if amount <= 0:
        return
    assert (
        await client.flex_transfer(
            currency=currency,
            amount=_fmt_transfer(amount),
            fromAccountType=from_account_type,
            toAccountType=to_account_type,
            clientOid=_client_oid(),
        )
        is not None
    )
    await asyncio.sleep(2)


def _transfer_amount(required: Decimal, available: Decimal, main_available: Decimal) -> Decimal:
    needed = required - available
    buffered = needed + TRANSFER_BUFFER_USDT
    if main_available >= buffered:
        return buffered
    return needed


async def _transfer_from_main(
    client: Client,
    amount: Decimal,
    to_account_type: str,
    reason: str,
) -> None:
    main_available = await _available(client, "USDT", "main")
    if main_available < amount:
        pytest.skip(reason)
    await _flex_transfer(client, "USDT", amount, "MAIN", to_account_type)


async def _spot_open_orders(client: Client, product_symbol: str | None = SPOT_SYMBOL) -> list[dict]:
    if product_symbol is None:
        product_symbol = SPOT_SYMBOL
    return _items(await client.get_spot_open_orders(product_symbol=product_symbol))


async def _futures_open_orders(client: Client) -> list[dict]:
    return _items(
        await client.get_futures_order_list(
            product_symbol=FUTURES_SYMBOL,
            status="active",
        )
    )


async def _skip_if_existing_state(client: Client) -> None:
    if await _spot_open_orders(client, product_symbol=None):
        pytest.skip("KuCoin spot already has open orders; not touching unrelated orders.")
    if await _futures_open_orders(client):
        pytest.skip("BTC-USDT futures already has open orders; not touching unrelated orders.")
    if await _futures_position_size(client) != 0:
        pytest.skip("BTC-USDT futures already has a position; not changing exposure.")


async def _snapshot_balances(client: Client) -> dict[str, Decimal]:
    return {
        "trade_usdt": await _available(client, "USDT", "trade"),
        "trade_btc": await _available(client, "BTC", "trade"),
        "contract_usdt": await _futures_available_usdt(client),
    }


async def _cleanup(client: Client, initial: dict[str, Decimal]) -> None:
    with suppress(Exception):
        if await _spot_open_orders(client):
            await client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL)
            await asyncio.sleep(1)

    with suppress(Exception):
        if await _futures_open_orders(client):
            await client.cancel_futures_all_orders(product_symbol=FUTURES_SYMBOL)
            await asyncio.sleep(1)

    with suppress(Exception):
        position_size = await _futures_position_size(client)
        if position_size > 0:
            await client.place_futures_market_sell_order(
                product_symbol=FUTURES_SYMBOL,
                size=int(position_size),
                clientOid=_client_oid(),
                leverage=int(FUTURES_LEVERAGE),
                marginMode="CROSS",
                positionSide="BOTH",
                reduceOnly=True,
            )
            await asyncio.sleep(2)
        elif position_size < 0:
            await client.place_futures_market_buy_order(
                product_symbol=FUTURES_SYMBOL,
                size=int(abs(position_size)),
                clientOid=_client_oid(),
                leverage=int(FUTURES_LEVERAGE),
                marginMode="CROSS",
                positionSide="BOTH",
                reduceOnly=True,
            )
            await asyncio.sleep(2)

    with suppress(Exception):
        trade_btc = await _available(client, "BTC", "trade")
        excess_btc = trade_btc - initial["trade_btc"]
        if excess_btc > 0:
            size = await _spot_sell_quantity(client, excess_btc)
            if Decimal(size) > 0:
                await client.place_spot_market_sell_order(
                    product_symbol=SPOT_SYMBOL,
                    size=size,
                    clientOid=_client_oid(),
                )
                await asyncio.sleep(2)

    with suppress(Exception):
        trade_usdt = await _available(client, "USDT", "trade")
        excess_usdt = trade_usdt - initial["trade_usdt"]
        if excess_usdt > Decimal("0.00000001"):
            await _flex_transfer(client, "USDT", excess_usdt, "TRADE", "MAIN")

    with suppress(Exception):
        trade_btc = await _available(client, "BTC", "trade")
        excess_btc = trade_btc - initial["trade_btc"]
        if excess_btc > Decimal("0.00000001"):
            await _flex_transfer(client, "BTC", excess_btc, "TRADE", "MAIN")

    with suppress(Exception):
        contract_usdt = await _futures_available_usdt(client)
        excess_contract_usdt = contract_usdt - initial["contract_usdt"]
        if excess_contract_usdt > Decimal("0.00000001"):
            await _flex_transfer(client, "USDT", excess_contract_usdt, "CONTRACT", "MAIN")


def _spot_step_and_min(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "1"), Decimal("1"))
    return step, min_size, min_notional


async def _spot_order_params(client: Client) -> tuple[str, str]:
    details = client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)
    tick = _dec(details["price_precision"], "0.01")
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "1"), Decimal("1"))
    best_bid = _dec(
        (await client.get_spot_orderbook(product_symbol=SPOT_SYMBOL))["data"]["bids"][0][0]
    )
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    size = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(size, min_size)), _fmt(price)


async def _spot_fillable_limit_buy_params(client: Client) -> tuple[str, str]:
    details = client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)
    tick = _dec(details["price_precision"], "0.01")
    step, min_size, min_notional = _spot_step_and_min(client)
    best_ask = _dec(
        (await client.get_spot_orderbook(product_symbol=SPOT_SYMBOL))["data"]["asks"][0][0]
    )
    price = _round_to_step(best_ask + tick, tick, ROUND_UP)
    size = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(size, min_size)), _fmt(price)


async def _spot_fillable_limit_sell_price(client: Client) -> str:
    tick = _dec(client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)["price_precision"], "0.01")
    best_bid = _dec(
        (await client.get_spot_orderbook(product_symbol=SPOT_SYMBOL))["data"]["bids"][0][0]
    )
    return _fmt(_round_to_step(best_bid - tick, tick, ROUND_DOWN))


async def _spot_post_only_sell_price(client: Client) -> str:
    tick = _dec(client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)["price_precision"], "0.01")
    best_ask = _dec(
        (await client.get_spot_orderbook(product_symbol=SPOT_SYMBOL))["data"]["asks"][0][0]
    )
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _spot_sell_quantity(client: Client, quantity: Decimal) -> str:
    step, _, _ = _spot_step_and_min(client)
    return _fmt(_round_to_step(quantity, step, ROUND_DOWN))


async def _spot_market_funds(client: Client) -> Decimal:
    _, _, min_notional = _spot_step_and_min(client)
    return min_notional * Decimal("1.01")


async def _ensure_spot_funds(client: Client, funds: Decimal) -> None:
    available = await _available(client, "USDT", "trade")
    if available >= funds:
        return

    main_available = await _available(client, "USDT", "main")
    transfer_amount = _transfer_amount(funds, available, main_available)
    await _transfer_from_main(
        client,
        transfer_amount,
        "TRADE",
        "Insufficient main USDT to fund KuCoin spot stateful order test.",
    )
    if await _available(client, "USDT", "trade") < funds:
        pytest.skip("Insufficient spot trade USDT for KuCoin spot stateful order test.")


async def _ensure_spot_order_funds(client: Client, size: str, price: str) -> None:
    await _ensure_spot_funds(client, Decimal(size) * Decimal(price))


async def _spot_trade_delta(client: Client, before: Decimal) -> Decimal:
    return max(await _available(client, "BTC", "trade") - before, Decimal("0"))


async def _spot_market_buy_delta(client: Client, funds: Decimal) -> Decimal:
    before_btc = await _available(client, "BTC", "trade")
    assert (
        await client.place_spot_market_buy_order(
            product_symbol=SPOT_SYMBOL,
            funds=_fmt(funds),
            clientOid=_client_oid(),
        )
        is not None
    )
    await asyncio.sleep(2)
    return await _spot_trade_delta(client, before_btc)


async def _futures_order_params(client: Client) -> tuple[int, str, Decimal, Decimal]:
    contract = (await client.get_futures_contract(product_symbol=FUTURES_SYMBOL))["data"]
    tick = _dec(contract["tickSize"], "0.1")
    lot = _dec(contract["lotSize"], "1")
    multiplier = _dec(contract["multiplier"], "0.001")
    current_price = _dec(
        (await client.get_futures_ticker(product_symbol=FUTURES_SYMBOL))["data"]["price"]
    )
    best_bid = _dec(
        (await client.get_futures_orderbook(product_symbol=FUTURES_SYMBOL, depth=5))["data"][
            "bids"
        ][0][0]
    )
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    return int(max(lot, Decimal("1"))), _fmt(price), current_price, multiplier


async def _futures_fillable_buy_price(client: Client) -> str:
    contract = (await client.get_futures_contract(product_symbol=FUTURES_SYMBOL))["data"]
    tick = _dec(contract["tickSize"], "0.1")
    best_ask = _dec(
        (await client.get_futures_orderbook(product_symbol=FUTURES_SYMBOL, depth=5))["data"][
            "asks"
        ][0][0]
    )
    price = _round_to_step(best_ask + tick, tick, ROUND_UP)
    return _fmt(price)


async def _futures_fillable_sell_price(client: Client) -> str:
    contract = (await client.get_futures_contract(product_symbol=FUTURES_SYMBOL))["data"]
    tick = _dec(contract["tickSize"], "0.1")
    best_bid = _dec(
        (await client.get_futures_orderbook(product_symbol=FUTURES_SYMBOL, depth=5))["data"][
            "bids"
        ][0][0]
    )
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    return _fmt(price)


async def _ensure_futures_cross_leverage(client: Client) -> None:
    target_leverage = str(int(FUTURES_LEVERAGE))
    data = (await client.get_futures_cross_margin_leverage(product_symbol=FUTURES_SYMBOL)).get(
        "data"
    )
    if isinstance(data, dict) and str(data.get("leverage")) == target_leverage:
        return
    assert (
        await client.modify_futures_cross_margin_leverage(
            product_symbol=FUTURES_SYMBOL,
            leverage=target_leverage,
        )
        is not None
    )
    await asyncio.sleep(1)


async def _ensure_futures_margin(
    client: Client,
    size: int,
    price: str,
    multiplier: Decimal,
    leverage: Decimal = FUTURES_LEVERAGE,
) -> None:
    await _ensure_futures_cross_leverage(client)
    required_margin = Decimal(price) * multiplier * Decimal(size) / leverage * Decimal("1.05")
    available = await _futures_available_usdt(client)
    if available >= required_margin:
        return

    main_available = await _available(client, "USDT", "main")
    transfer_amount = _transfer_amount(required_margin, available, main_available)
    await _transfer_from_main(
        client,
        transfer_amount,
        "CONTRACT",
        "Insufficient main USDT to fund KuCoin futures stateful order test.",
    )
    if await _futures_available_usdt(client) < required_margin:
        pytest.skip("Insufficient futures USDT for KuCoin futures stateful order test.")


async def _wait_for_futures_position(client: Client, sign: int) -> Decimal:
    for _ in range(8):
        size = await _futures_position_size(client)
        if sign > 0 and size > 0:
            return size
        if sign < 0 and size < 0:
            return size
        await asyncio.sleep(1)
    return Decimal("0")


async def _wait_until_flat(client: Client) -> None:
    for _ in range(8):
        if await _futures_position_size(client) == 0:
            return
        await asyncio.sleep(1)
    assert await _futures_position_size(client) == 0


async def _close_futures_position(client: Client) -> None:
    position_size = await _futures_position_size(client)
    if position_size > 0:
        await client.place_futures_market_sell_order(
            product_symbol=FUTURES_SYMBOL,
            size=int(position_size),
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
            reduceOnly=True,
        )
    elif position_size < 0:
        await client.place_futures_market_buy_order(
            product_symbol=FUTURES_SYMBOL,
            size=int(abs(position_size)),
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
            reduceOnly=True,
        )
    await asyncio.sleep(2)
    await _wait_until_flat(client)


async def _exercise_spot_stateful_methods(client: Client) -> None:
    size, price = await _spot_order_params(client)
    await _ensure_spot_order_funds(client, size, price)

    order_id = None
    try:
        order = await client.place_spot_order(
            SPOT_SYMBOL,
            side="buy",
            type_="limit",
            size=size,
            price=price,
            clientOid=_client_oid(),
            postOnly=True,
        )
        order_id = order["data"]["orderId"]
        assert await _spot_open_orders(client)
        assert (
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)

    order_id = None
    try:
        order = await client.place_spot_limit_order(
            SPOT_SYMBOL,
            side="buy",
            size=size,
            price=price,
            clientOid=_client_oid(),
            postOnly=True,
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL) is not None
        order_id = None
        await asyncio.sleep(1)
    finally:
        if order_id is not None:
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)

    order_id = None
    try:
        order = await client.place_spot_post_only_limit_order(
            SPOT_SYMBOL,
            side="buy",
            size=size,
            price=price,
            clientOid=_client_oid(),
        )
        order_id = order["data"]["orderId"]
        assert (
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)

    order_id = None
    try:
        order = await client.place_spot_post_only_limit_buy_order(
            SPOT_SYMBOL,
            size=size,
            price=price,
            clientOid=_client_oid(),
        )
        order_id = order["data"]["orderId"]
        assert (
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL) is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)

    assert (
        await client.place_spot_batch_orders(
            [
                {
                    "symbol": SPOT_SYMBOL,
                    "side": "buy",
                    "type": "limit",
                    "size": size,
                    "price": price,
                    "clientOid": _client_oid(),
                    "postOnly": True,
                }
            ]
        )
    ).get("data") is not None
    assert await client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL) is not None

    assert (
        await client.place_spot_batch_limit_orders(
            [
                {
                    "symbol": SPOT_SYMBOL,
                    "side": "buy",
                    "size": size,
                    "price": price,
                    "clientOid": _client_oid(),
                    "postOnly": True,
                }
            ]
        )
    ).get("data") is not None
    assert await client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL) is not None

    order_id = None
    try:
        order = await client.place_spot_post_only_limit_buy_order(
            SPOT_SYMBOL,
            size=size,
            price=price,
            clientOid=_client_oid(),
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_spot_all_orders() is not None
        order_id = None
        await asyncio.sleep(1)
    finally:
        if order_id is not None:
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)

    funds = await _spot_market_funds(client)
    await _ensure_spot_funds(client, funds)
    acquired = await _spot_market_buy_delta(client, funds)
    sell_size = await _spot_sell_quantity(client, acquired)
    assert Decimal(sell_size) > 0
    assert (
        await client.place_spot_market_sell_order(
            SPOT_SYMBOL,
            size=sell_size,
            clientOid=_client_oid(),
        )
        is not None
    )
    await asyncio.sleep(2)

    funds = await _spot_market_funds(client)
    await _ensure_spot_funds(client, funds)
    before_btc = await _available(client, "BTC", "trade")
    assert (
        await client.place_spot_market_order(
            SPOT_SYMBOL,
            side="buy",
            funds=_fmt(funds),
            clientOid=_client_oid(),
        )
        is not None
    )
    await asyncio.sleep(2)
    acquired = await _spot_trade_delta(client, before_btc)
    sell_size = await _spot_sell_quantity(client, acquired)
    assert Decimal(sell_size) > 0
    assert (
        await client.place_spot_market_order(
            SPOT_SYMBOL,
            side="sell",
            size=sell_size,
            clientOid=_client_oid(),
        )
        is not None
    )
    await asyncio.sleep(2)

    funds = await _spot_market_funds(client)
    await _ensure_spot_funds(client, funds)
    before_btc = await _available(client, "BTC", "trade")
    assert (
        await client.place_spot_batch_market_orders(
            [
                {
                    "symbol": SPOT_SYMBOL,
                    "side": "buy",
                    "funds": _fmt(funds),
                    "clientOid": _client_oid(),
                }
            ]
        )
    ).get("data") is not None
    await asyncio.sleep(2)
    acquired = await _spot_trade_delta(client, before_btc)
    sell_size = await _spot_sell_quantity(client, acquired)
    if Decimal(sell_size) > 0:
        await client.place_spot_market_sell_order(
            SPOT_SYMBOL,
            size=sell_size,
            clientOid=_client_oid(),
        )
        await asyncio.sleep(2)

    fill_size, fill_price = await _spot_fillable_limit_buy_params(client)
    await _ensure_spot_order_funds(client, fill_size, fill_price)
    before_btc = await _available(client, "BTC", "trade")
    try:
        assert (
            await client.place_spot_limit_buy_order(
                SPOT_SYMBOL,
                size=fill_size,
                price=fill_price,
                clientOid=_client_oid(),
            )
            is not None
        )
        await asyncio.sleep(2)
        acquired = await _spot_trade_delta(client, before_btc)
        sell_size = await _spot_sell_quantity(client, acquired)
        assert Decimal(sell_size) > 0
        assert (
            await client.place_spot_limit_sell_order(
                SPOT_SYMBOL,
                size=sell_size,
                price=await _spot_fillable_limit_sell_price(client),
                clientOid=_client_oid(),
            )
            is not None
        )
        await asyncio.sleep(2)
    finally:
        if await _spot_open_orders(client):
            await client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL)
        remaining = await _spot_trade_delta(client, before_btc)
        sell_size = await _spot_sell_quantity(client, remaining)
        if Decimal(sell_size) > 0:
            await client.place_spot_market_sell_order(
                SPOT_SYMBOL,
                size=sell_size,
                clientOid=_client_oid(),
            )

    funds = await _spot_market_funds(client)
    await _ensure_spot_funds(client, funds)
    before_btc = await _available(client, "BTC", "trade")
    order_id = None
    try:
        acquired = await _spot_market_buy_delta(client, funds)
        sell_size = await _spot_sell_quantity(client, acquired)
        assert Decimal(sell_size) > 0
        order = await client.place_spot_post_only_limit_sell_order(
            SPOT_SYMBOL,
            size=sell_size,
            price=await _spot_post_only_sell_price(client),
            clientOid=_client_oid(),
        )
        order_id = order["data"]["orderId"]
        assert await _spot_open_orders(client)
    finally:
        if order_id is not None:
            await client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)
        remaining = await _spot_trade_delta(client, before_btc)
        sell_size = await _spot_sell_quantity(client, remaining)
        if Decimal(sell_size) > 0:
            await client.place_spot_market_sell_order(
                SPOT_SYMBOL,
                size=sell_size,
                clientOid=_client_oid(),
            )


async def _exercise_futures_stateful_methods(client: Client) -> None:
    size, price, current_price, multiplier = await _futures_order_params(client)
    await _ensure_futures_margin(client, size, price, multiplier)

    assert await client.get_futures_position_mode() is not None
    assert await client.get_futures_open_order_value(product_symbol=FUTURES_SYMBOL) is not None

    order_id = None
    client_oid = _client_oid()
    try:
        order = await client.place_futures_order(
            FUTURES_SYMBOL,
            side="buy",
            type_="limit",
            size=size,
            price=price,
            clientOid=client_oid,
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
            postOnly=True,
        )
        order_id = order["data"]["orderId"]
        assert await client.get_futures_order(orderId=order_id) is not None
        assert (
            await client.get_futures_order_by_client_oid(
                clientOid=client_oid,
                product_symbol=FUTURES_SYMBOL,
            )
            is not None
        )
        assert await client.cancel_futures_order(orderId=order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_futures_order(orderId=order_id)

    order_id = None
    try:
        order = await client.place_futures_limit_order(
            FUTURES_SYMBOL,
            side="buy",
            size=size,
            price=price,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
            postOnly=True,
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_futures_all_orders(product_symbol=FUTURES_SYMBOL) is not None
        order_id = None
        await asyncio.sleep(1)
    finally:
        if order_id is not None:
            await client.cancel_futures_order(orderId=order_id)

    order_id = None
    try:
        order = await client.place_futures_post_only_limit_order(
            FUTURES_SYMBOL,
            side="buy",
            size=size,
            price=price,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_futures_order(orderId=order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_futures_order(orderId=order_id)

    order_id = None
    try:
        order = await client.place_futures_post_only_limit_buy_order(
            FUTURES_SYMBOL,
            size=size,
            price=price,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_futures_order(orderId=order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_futures_order(orderId=order_id)

    order_id = None
    try:
        tick = _dec(
            (await client.get_futures_contract(product_symbol=FUTURES_SYMBOL))["data"]["tickSize"],
            "0.1",
        )
        best_ask = _dec(
            (await client.get_futures_orderbook(product_symbol=FUTURES_SYMBOL, depth=5))["data"][
                "asks"
            ][0][0]
        )
        high_price = _fmt(
            _round_to_step(
                best_ask + tick,
                tick,
                ROUND_UP,
            )
        )
        await _ensure_futures_margin(client, size, high_price, multiplier)
        order = await client.place_futures_post_only_limit_sell_order(
            FUTURES_SYMBOL,
            size=size,
            price=high_price,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert await client.cancel_futures_order(orderId=order_id) is not None
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_futures_order(orderId=order_id)

    order_id = None
    client_oid = _client_oid()
    try:
        order = await client.place_futures_post_only_limit_buy_order(
            FUTURES_SYMBOL,
            size=size,
            price=price,
            clientOid=client_oid,
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert (
            await client.cancel_futures_order_by_client_oid(
                clientOid=client_oid,
                product_symbol=FUTURES_SYMBOL,
            )
            is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            await client.cancel_futures_order(orderId=order_id)

    await _ensure_futures_margin(client, size, _fmt(current_price), multiplier)
    assert (
        await client.place_futures_market_order(
            FUTURES_SYMBOL,
            side="buy",
            size=size,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        is not None
    )
    assert await _wait_for_futures_position(client, sign=1) > 0
    await _close_futures_position(client)

    await _ensure_futures_margin(client, size, _fmt(current_price), multiplier)
    assert (
        await client.place_futures_market_buy_order(
            FUTURES_SYMBOL,
            size=size,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        is not None
    )
    assert await _wait_for_futures_position(client, sign=1) > 0
    await _close_futures_position(client)

    await _ensure_futures_margin(client, size, _fmt(current_price), multiplier)
    assert (
        await client.place_futures_market_sell_order(
            FUTURES_SYMBOL,
            size=size,
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        is not None
    )
    assert await _wait_for_futures_position(client, sign=-1) < 0
    await _close_futures_position(client)

    await _ensure_futures_margin(client, size, _fmt(current_price), multiplier)
    assert (
        await client.place_futures_limit_buy_order(
            FUTURES_SYMBOL,
            size=size,
            price=await _futures_fillable_buy_price(client),
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        is not None
    )
    assert await _wait_for_futures_position(client, sign=1) > 0
    await _close_futures_position(client)

    await _ensure_futures_margin(client, size, _fmt(current_price), multiplier)
    assert (
        await client.place_futures_limit_sell_order(
            FUTURES_SYMBOL,
            size=size,
            price=await _futures_fillable_sell_price(client),
            clientOid=_client_oid(),
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        is not None
    )
    assert await _wait_for_futures_position(client, sign=-1) < 0
    await _close_futures_position(client)

    assert (
        await client.get_futures_order_list(
            product_symbol=FUTURES_SYMBOL,
            status="done",
            pageSize=10,
        )
        is not None
    )
    assert (
        await client.get_futures_trade_history(product_symbol=FUTURES_SYMBOL, pageSize=10)
        is not None
    )
    assert await client.get_futures_recent_trade_history(product_symbol=FUTURES_SYMBOL) is not None


async def test_async_stateful_order_transfer_and_position_lifecycle(client):
    await _skip_if_existing_state(client)
    initial = await _snapshot_balances(client)
    try:
        await _exercise_spot_stateful_methods(client)
        await _exercise_futures_stateful_methods(client)
    finally:
        await _cleanup(client, initial)

    assert not await _spot_open_orders(client)
    assert not await _futures_open_orders(client)
    assert await _futures_position_size(client) == 0


@pytest.mark.private
async def test_async_spot_trade_history_endpoint(client):
    assert await client.get_spot_trade_history(product_symbol=SPOT_SYMBOL, limit=10) is not None
