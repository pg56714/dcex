# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.gateio.client import Client

load_dotenv()

GATEIO_API_KEY = os.getenv("GATEIO_API_KEY")
GATEIO_API_SECRET = os.getenv("GATEIO_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
FUTURES_LEVERAGE = "2"

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Gate order tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=GATEIO_API_KEY,
        api_secret=GATEIO_API_SECRET,
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


def _text() -> str:
    return f"t-dcex-{uuid.uuid4().hex[:20]}"


def _items(res: object) -> list[dict]:
    if isinstance(res, list):
        return [item for item in res if isinstance(item, dict)]
    if isinstance(res, dict):
        data = res.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return [item for item in data["items"] if isinstance(item, dict)]
    return []


def _first_price(level: object) -> Decimal:
    if isinstance(level, dict):
        return _dec(level.get("p", level.get("price")))
    if isinstance(level, list | tuple) and level:
        return _dec(level[0])
    return Decimal("0")


async def _spot_available(client: Client, currency: str) -> Decimal:
    account = await client.get_spot_account(ccy=currency)
    return sum((_dec(item.get("available")) for item in _items(account)), Decimal("0"))


async def _futures_available_usdt(client: Client) -> Decimal:
    account = await client.get_futures_account()
    data = account.get("data", account) if isinstance(account, dict) else account
    if not isinstance(data, dict):
        return Decimal("0")
    for key in ("available", "available_margin", "availableBalance", "available_balance"):
        if key in data:
            return _dec(data.get(key))
    return Decimal("0")


async def _position_size(client: Client) -> Decimal:
    data = await client.get_contract_single_positions(product_symbol=FUTURES_SYMBOL)
    data = data.get("data", data) if isinstance(data, dict) else data
    if not isinstance(data, dict):
        return Decimal("0")
    return _dec(data.get("size", data.get("value", "0")))


async def _position_leverage(client: Client) -> str:
    data = await client.get_contract_single_positions(product_symbol=FUTURES_SYMBOL)
    data = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(data, dict) and data.get("leverage"):
        return str(data["leverage"])
    return FUTURES_LEVERAGE


async def _spot_open_orders(client: Client) -> list[dict]:
    return _items(await client.get_spot_open_orders())


async def _futures_open_orders(client: Client) -> list[dict]:
    return _items(
        await client.get_contract_order_list(
            status="open",
            product_symbol=FUTURES_SYMBOL,
        )
    )


async def _delivery_product_symbol(client: Client) -> str | None:
    for contract in _items(await client.get_all_delivery_contracts()):
        if not contract.get("in_delisting") and contract.get("name"):
            return "-".join(str(contract["name"]).split("_")) + "-SWAP"
    return None


async def _skip_if_existing_state(client: Client) -> None:
    if await _spot_open_orders(client):
        pytest.skip("Gate spot already has open orders; not touching unrelated orders.")
    if await _futures_open_orders(client):
        pytest.skip("Gate futures already has open orders; not touching unrelated orders.")
    if await _position_size(client) != 0:
        pytest.skip("Gate futures already has a position; not changing exposure.")


async def _cleanup(client: Client, initial_spot_btc: Decimal) -> None:
    with suppress(Exception):
        if await _spot_open_orders(client):
            await client.cancel_spot_order(product_symbol=SPOT_SYMBOL)
            await asyncio.sleep(1)

    with suppress(Exception):
        if await _futures_open_orders(client):
            await client.cancel_contract_all_order_matched(product_symbol=FUTURES_SYMBOL)
            await asyncio.sleep(1)

    with suppress(Exception):
        position_size = await _position_size(client)
        if position_size > 0:
            await client.place_contract_order(
                product_symbol=FUTURES_SYMBOL,
                size=-int(abs(position_size)),
                price="0",
                tif="ioc",
                reduce_only=True,
            )
            await asyncio.sleep(2)
        elif position_size < 0:
            await client.place_contract_order(
                product_symbol=FUTURES_SYMBOL,
                size=int(abs(position_size)),
                price="0",
                tif="ioc",
                reduce_only=True,
            )
            await asyncio.sleep(2)

    with suppress(Exception):
        btc_delta = await _spot_available(client, "BTC") - initial_spot_btc
        if btc_delta > 0:
            sell_amount = _spot_sell_amount(client, btc_delta)
            if Decimal(sell_amount) > 0:
                await client.place_spot_market_sell_order(SPOT_SYMBOL, amount=sell_amount)
                await asyncio.sleep(2)


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("gateio", SPOT_SYMBOL)
    tick = _dec(details["price_precision"], "0.01")
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "3"), Decimal("3"))
    return tick, step, min_size, min_notional


async def _spot_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = await client.get_spot_order_book(product_symbol=SPOT_SYMBOL, limit=5)
    data = data.get("data", data) if isinstance(data, dict) else data
    bids = data.get("bids", []) if isinstance(data, dict) else []
    asks = data.get("asks", []) if isinstance(data, dict) else []
    return _first_price(bids[0]), _first_price(asks[0])


async def _spot_post_only_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    amount = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(amount, min_size)), _fmt(price)


async def _spot_fillable_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    price = _round_to_step(best_ask + tick, tick, ROUND_UP)
    amount = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(amount, min_size)), _fmt(price)


async def _spot_fillable_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_bid - tick, tick, ROUND_DOWN))


async def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _spot_market_buy_amount(client: Client) -> Decimal:
    _, step, min_size, min_notional = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    min_sell_amount = _round_to_step(
        max(min_size, min_notional / best_ask) * Decimal("1.005"),
        step,
        ROUND_UP,
    )
    return (min_sell_amount + step) * best_ask * Decimal("1.01")


def _spot_sell_amount(client: Client, amount: Decimal) -> str:
    _, step, _, _ = _spot_details(client)
    return _fmt(_round_to_step(amount, step, ROUND_DOWN))


async def _ensure_spot_usdt(client: Client, required: Decimal) -> None:
    if await _spot_available(client, "USDT") < required:
        pytest.skip("Insufficient Gate spot USDT for stateful order test.")


async def _contract_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = await client.get_contract_order_book(product_symbol=FUTURES_SYMBOL, limit=5)
    data = data.get("data", data) if isinstance(data, dict) else data
    bids = data.get("bids", []) if isinstance(data, dict) else []
    asks = data.get("asks", []) if isinstance(data, dict) else []
    return _first_price(bids[0]), _first_price(asks[0])


async def _futures_order_params(client: Client) -> tuple[int, str, Decimal]:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    min_size = max(_dec(details["min_size"], "1"), Decimal("1"))
    ticker = await client.get_contract_list_tickers(product_symbol=FUTURES_SYMBOL)
    ticker_data = _items(ticker)
    last_price = _dec(ticker_data[0].get("last")) if ticker_data else Decimal("0")
    if last_price <= 0:
        _, asks_price = await _contract_orderbook_prices(client)
        last_price = asks_price
    best_bid, _ = await _contract_orderbook_prices(client)
    price = _round_to_step(min(best_bid - tick, best_bid * Decimal("0.999")), tick, ROUND_DOWN)
    return int(min_size), _fmt(price), last_price


async def _contract_fillable_buy_price(client: Client) -> str:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    _, best_ask = await _contract_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _contract_fillable_sell_price(client: Client) -> str:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    best_bid, _ = await _contract_orderbook_prices(client)
    return _fmt(_round_to_step(best_bid - tick, tick, ROUND_DOWN))


async def _contract_post_only_sell_price(client: Client) -> str:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    _, best_ask = await _contract_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _ensure_futures_usdt(client: Client) -> None:
    if await _futures_available_usdt(client) <= 0:
        pytest.skip("Insufficient Gate futures USDT for stateful order test.")


async def _wait_for_position(client: Client, sign: int) -> Decimal:
    for _ in range(8):
        size = await _position_size(client)
        if sign > 0 and size > 0:
            return size
        if sign < 0 and size < 0:
            return size
        await asyncio.sleep(1)
    return Decimal("0")


async def _close_position(client: Client) -> None:
    size = await _position_size(client)
    if size > 0:
        await client.place_contract_order(
            product_symbol=FUTURES_SYMBOL,
            size=-int(abs(size)),
            price="0",
            tif="ioc",
            reduce_only=True,
        )
    elif size < 0:
        await client.place_contract_order(
            product_symbol=FUTURES_SYMBOL,
            size=int(abs(size)),
            price="0",
            tif="ioc",
            reduce_only=True,
        )
    await asyncio.sleep(2)
    assert await _position_size(client) == 0


async def test_spot_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    try:
        amount, price = await _spot_post_only_buy_params(client)
        await _ensure_spot_usdt(client, Decimal(amount) * Decimal(price))

        order_id = None
        try:
            order = await client.place_spot_order(
                SPOT_SYMBOL,
                side="buy",
                order_type="limit",
                amount=amount,
                price=price,
                time_in_force="poc",
                text=_text(),
            )
            order_id = str(order["id"])
            assert await client.get_spot_single_order(order_id, SPOT_SYMBOL) is not None
            amended_price = _fmt(Decimal(price) * Decimal("0.99"))
            assert (
                await client.amend_spot_single_order(
                    order_id,
                    product_symbol=SPOT_SYMBOL,
                    price=amended_price,
                )
                is not None
            )
            assert await client.cancel_spot_single_order(order_id, SPOT_SYMBOL) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        order_id = None
        try:
            order = await client.place_spot_limit_order(SPOT_SYMBOL, "buy", amount, price)
            order_id = str(order["id"])
            assert await client.cancel_spot_order(product_symbol=SPOT_SYMBOL) is not None
            order_id = None
            await asyncio.sleep(1)
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        order_id = None
        try:
            order = await client.place_spot_post_only_limit_order(SPOT_SYMBOL, "buy", amount, price)
            order_id = str(order["id"])
            assert await client.cancel_spot_single_order(order_id, SPOT_SYMBOL) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        order_id = None
        try:
            order = await client.place_spot_post_only_limit_buy_order(SPOT_SYMBOL, amount, price)
            order_id = str(order["id"])
            assert await client.cancel_spot_single_order(order_id, SPOT_SYMBOL) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        quote_amount = await _spot_market_buy_amount(client)
        await _ensure_spot_usdt(client, quote_amount)
        before_btc = await _spot_available(client, "BTC")
        assert await client.place_spot_market_buy_order(SPOT_SYMBOL, _fmt(quote_amount)) is not None
        await asyncio.sleep(2)
        acquired = await _spot_available(client, "BTC") - before_btc
        sell_amount = _spot_sell_amount(client, acquired)
        assert Decimal(sell_amount) > 0
        assert await client.place_spot_market_sell_order(SPOT_SYMBOL, sell_amount) is not None
        await asyncio.sleep(2)

        quote_amount = await _spot_market_buy_amount(client)
        await _ensure_spot_usdt(client, quote_amount)
        before_btc = await _spot_available(client, "BTC")
        assert (
            await client.place_spot_market_order(SPOT_SYMBOL, "buy", _fmt(quote_amount)) is not None
        )
        await asyncio.sleep(2)
        acquired = await _spot_available(client, "BTC") - before_btc
        sell_amount = _spot_sell_amount(client, acquired)
        assert Decimal(sell_amount) > 0
        assert await client.place_spot_market_order(SPOT_SYMBOL, "sell", sell_amount) is not None
        await asyncio.sleep(2)

        fill_amount, fill_price = await _spot_fillable_buy_params(client)
        await _ensure_spot_usdt(client, Decimal(fill_amount) * Decimal(fill_price))
        before_btc = await _spot_available(client, "BTC")
        try:
            assert (
                await client.place_spot_limit_buy_order(SPOT_SYMBOL, fill_amount, fill_price)
                is not None
            )
            await asyncio.sleep(2)
            acquired = await _spot_available(client, "BTC") - before_btc
            sell_amount = _spot_sell_amount(client, acquired)
            assert Decimal(sell_amount) > 0
            assert (
                await client.place_spot_limit_sell_order(
                    SPOT_SYMBOL,
                    sell_amount,
                    await _spot_fillable_sell_price(client),
                )
                is not None
            )
            await asyncio.sleep(2)
        finally:
            if await _spot_open_orders(client):
                await client.cancel_spot_order(product_symbol=SPOT_SYMBOL)
            remaining = await _spot_available(client, "BTC") - before_btc
            sell_amount = _spot_sell_amount(client, remaining)
            if Decimal(sell_amount) > 0:
                await client.place_spot_market_sell_order(SPOT_SYMBOL, sell_amount)

        quote_amount = await _spot_market_buy_amount(client)
        await _ensure_spot_usdt(client, quote_amount)
        before_btc = await _spot_available(client, "BTC")
        order_id = None
        try:
            assert (
                await client.place_spot_market_buy_order(SPOT_SYMBOL, _fmt(quote_amount))
                is not None
            )
            await asyncio.sleep(2)
            acquired = await _spot_available(client, "BTC") - before_btc
            sell_amount = _spot_sell_amount(client, acquired)
            assert Decimal(sell_amount) > 0
            order = await client.place_spot_post_only_limit_sell_order(
                SPOT_SYMBOL,
                sell_amount,
                await _spot_post_only_sell_price(client),
            )
            order_id = str(order["id"])
            assert await client.get_spot_order_list(SPOT_SYMBOL, status="open") is not None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)
            remaining = await _spot_available(client, "BTC") - before_btc
            sell_amount = _spot_sell_amount(client, remaining)
            if Decimal(sell_amount) > 0:
                await client.place_spot_market_sell_order(SPOT_SYMBOL, sell_amount)

        assert (
            await client.get_spot_trading_history(product_symbol=SPOT_SYMBOL, limit=10) is not None
        )
    finally:
        await _cleanup(client, initial_btc)


async def test_futures_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    try:
        size, price, _ = await _futures_order_params(client)
        await _ensure_futures_usdt(client)

        assert await client.get_futures_all_positions(holding=False) is not None
        assert await client.get_contract_single_positions(product_symbol=FUTURES_SYMBOL) is not None
        assert (
            await client.update_futures_positions_leverage(
                product_symbol=FUTURES_SYMBOL,
                leverage=await _position_leverage(client),
            )
            is not None
        )

        order_id = None
        try:
            order = await client.place_contract_order(
                product_symbol=FUTURES_SYMBOL,
                size=size,
                price=price,
                tif="poc",
                text=_text(),
            )
            order_id = str(order["id"])
            assert await client.get_contract_single_order(order_id) is not None
            amended_price = _fmt(Decimal(price) * Decimal("0.99"))
            assert (
                await client.amend_futures_single_order(order_id, price=amended_price) is not None
            )
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await client.place_contract_limit_order(FUTURES_SYMBOL, size, price)
            order_id = str(order["id"])
            assert (
                await client.cancel_contract_all_order_matched(product_symbol=FUTURES_SYMBOL)
                is not None
            )
            order_id = None
            await asyncio.sleep(1)
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await client.place_contract_post_only_limit_order(FUTURES_SYMBOL, size, price)
            order_id = str(order["id"])
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await client.place_contract_post_only_limit_buy_order(
                FUTURES_SYMBOL,
                size,
                price,
            )
            order_id = str(order["id"])
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await client.place_contract_post_only_limit_sell_order(
                FUTURES_SYMBOL,
                size,
                await _contract_post_only_sell_price(client),
            )
            order_id = str(order["id"])
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        batch = await client.place_futures_batch_order(
            [
                {
                    "product_symbol": FUTURES_SYMBOL,
                    "size": size,
                    "price": price,
                    "tif": "poc",
                    "text": _text(),
                }
            ]
        )
        assert batch is not None
        assert (
            await client.cancel_contract_all_order_matched(product_symbol=FUTURES_SYMBOL)
            is not None
        )

        assert await client.place_contract_market_order(FUTURES_SYMBOL, size) is not None
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert await client.place_contract_market_buy_order(FUTURES_SYMBOL, size) is not None
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert await client.place_contract_market_sell_order(FUTURES_SYMBOL, size) is not None
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert (
            await client.place_contract_limit_buy_order(
                FUTURES_SYMBOL,
                size,
                await _contract_fillable_buy_price(client),
            )
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await client.place_contract_limit_sell_order(
                FUTURES_SYMBOL,
                size,
                await _contract_fillable_sell_price(client),
            )
            is not None
        )
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert (
            await client.get_contract_order_list(
                status="finished",
                product_symbol=FUTURES_SYMBOL,
            )
            is not None
        )
        assert await client.get_trading_history(product_symbol=FUTURES_SYMBOL, limit=10) is not None
        assert (
            await client.get_futures_position_close_history(
                product_symbol=FUTURES_SYMBOL,
                limit=10,
            )
            is not None
        )
        assert (
            await client.get_futures_auto_deleveraging_history(
                product_symbol=FUTURES_SYMBOL,
                limit=10,
            )
            is not None
        )
        assert await client.get_delivery_all_positions() is not None
        delivery_symbol = await _delivery_product_symbol(client)
        if delivery_symbol is not None:
            assert (
                await client.get_delivery_position_close_history(
                    product_symbol=delivery_symbol,
                    limit=10,
                )
                is not None
            )
    finally:
        await _cleanup(client, initial_btc)

    assert not (await _spot_open_orders(client))
    assert not (await _futures_open_orders(client))
    assert await _position_size(client) == 0
