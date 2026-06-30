# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import os
import time
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.binance.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("0.1")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Binance order and transfer tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    ) as client_instance:
        await _cleanup_futures_test_state(client_instance)
        await _return_spot_btc_delta(client_instance, Decimal("0"))
        try:
            yield client_instance
        finally:
            try:
                await _return_spot_btc_delta(client_instance, Decimal("0"))
            finally:
                await _cleanup_futures_test_state(client_instance)


def _filters(exchange_info: dict) -> dict[str, dict]:
    return {item["filterType"]: item for item in exchange_info["symbols"][0]["filters"]}


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    return (value / step).to_integral_value(rounding=rounding) * step


def _format_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


async def _get_futures_algo_order_with_retry(client: Client, client_algo_id: str) -> dict:
    for attempt in range(8):
        try:
            return await client.get_futures_algo_order(clientAlgoId=client_algo_id)
        except FailedRequestError as exc:
            if "-2013" not in str(exc) or attempt == 7:
                raise
            await asyncio.sleep(1)
    raise AssertionError("unreachable")


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


async def _spot_best_bid(client: Client, product_symbol: str) -> Decimal:
    book = await client.get_spot_orderbook(product_symbol=product_symbol, limit=5)
    bids = book.get("bids", []) if isinstance(book, dict) else []
    if not bids:
        pytest.fail(f"{product_symbol} spot orderbook did not return bids.", pytrace=False)
    return Decimal(str(bids[0][0]))


async def _spot_best_ask(client: Client, product_symbol: str) -> Decimal:
    book = await client.get_spot_orderbook(product_symbol=product_symbol, limit=5)
    asks = book.get("asks", []) if isinstance(book, dict) else []
    if not asks:
        pytest.fail(f"{product_symbol} spot orderbook did not return asks.", pytrace=False)
    return Decimal(str(asks[0][0]))


async def _safe_spot_market_quote(client: Client, product_symbol: str) -> Decimal:
    filters = _filters(await _symbol_exchange_info(client, product_symbol, futures=False))
    lot_filter = filters["LOT_SIZE"]
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("10"))
    best_ask = await _spot_best_ask(client, product_symbol)
    min_sell_qty = _round_to_step(
        max(min_qty, min_notional / best_ask) * Decimal("1.005"),
        step_size,
        ROUND_UP,
    )
    return (min_sell_qty + step_size) * best_ask * Decimal("1.01")


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
        else await _spot_best_bid(client, product_symbol)
    )
    price = _round_to_step(current_price * Decimal("0.95"), tick_size, ROUND_DOWN)
    required_notional = min_notional * Decimal("1.01")
    quantity = _round_to_step(required_notional / price, step_size, ROUND_UP)
    quantity = max(quantity, min_qty)

    return _format_decimal(quantity), _format_decimal(price)


async def _cancel_order_if_present(client: Client, product_symbol: str, order_id: int) -> None:
    try:
        await client.cancel_order(product_symbol=product_symbol, orderId=order_id)
    except FailedRequestError as exc:
        message = str(exc)
        if "-2011" in message or "Unknown order" in message:
            if await client.get_open_orders(product_symbol=product_symbol):
                raise
            return
        raise


async def _safe_market_quantity(client: Client, product_symbol: str) -> str:
    filters = _filters(await _symbol_exchange_info(client, product_symbol, futures=True))
    lot_filter = filters["LOT_SIZE"]
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("100"))
    price = Decimal((await client.get_futures_ticker(product_symbol=product_symbol))["askPrice"])
    required_notional = min_notional * Decimal("1.01")
    quantity = _round_to_step(required_notional / price, step_size, ROUND_UP)
    return _format_decimal(max(quantity, min_qty))


async def _spot_free(client: Client, asset: str) -> Decimal:
    account = await client.get_account_balance(market_type="spot")
    for balance in account["balances"]:
        if balance["asset"] == asset:
            return Decimal(balance["free"])
    return Decimal("0")


async def _funding_free(client: Client, asset: str) -> Decimal:
    for balance in await client.get_funding_wallet(asset=asset):
        if balance.get("asset") == asset:
            return Decimal(str(balance.get("free", "0")))
    return Decimal("0")


async def _futures_available(client: Client, asset: str) -> Decimal:
    for balance in await client.get_account_balance(market_type="swap"):
        if balance.get("asset") == asset:
            return Decimal(str(balance.get("availableBalance", "0")))
    return Decimal("0")


def _rows(payload: object, *keys: str) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return value
        value = payload.get("data")
        if isinstance(value, list):
            return value
    return []


async def _ensure_balance(
    client: Client,
    required: Decimal,
    destination: str,
) -> tuple[Decimal, str | None]:
    if destination == "spot":
        destination_balance = await _spot_free(client, "USDT")
        sources = (
            (await _funding_free(client, "USDT"), "FUNDING_MAIN", "MAIN_FUNDING"),
            (await _futures_available(client, "USDT"), "UMFUTURE_MAIN", "MAIN_UMFUTURE"),
        )
    else:
        destination_balance = await _futures_available(client, "USDT")
        sources = (
            (
                await _funding_free(client, "USDT"),
                "FUNDING_UMFUTURE",
                "UMFUTURE_FUNDING",
            ),
            (await _spot_free(client, "USDT"), "MAIN_UMFUTURE", "UMFUTURE_MAIN"),
        )

    if destination_balance >= required:
        return Decimal("0"), None

    needed = (required - destination_balance).quantize(Decimal("0.000001"), rounding=ROUND_UP)
    for source_balance, transfer_type, reverse_type in sources:
        if source_balance >= needed:
            await client.create_universal_transfer(
                type_=transfer_type,
                asset="USDT",
                amount=_format_decimal(needed),
            )
            await asyncio.sleep(1)
            return needed, reverse_type
    pytest.fail(f"Insufficient Binance USDT for {destination} stateful tests.", pytrace=False)


async def _return_transfer(
    client: Client,
    amount: Decimal,
    transfer_type: str | None,
) -> None:
    if amount <= 0 or transfer_type is None:
        return
    await asyncio.sleep(1)
    if transfer_type.startswith("MAIN_"):
        available = await _spot_free(client, "USDT")
    elif transfer_type.startswith("UMFUTURE_"):
        available = await _futures_available(client, "USDT")
    else:
        available = await _funding_free(client, "USDT")
    return_amount = min(amount, available).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    if return_amount <= 0:
        return
    await client.create_universal_transfer(
        type_=transfer_type,
        asset="USDT",
        amount=_format_decimal(return_amount),
    )


async def _futures_position_amt(client: Client, product_symbol: str) -> Decimal:
    positions = await client.get_future_position(product_symbol=product_symbol)
    if not positions:
        return Decimal("0")
    return Decimal(positions[0]["positionAmt"])


async def _close_futures_position(client: Client, product_symbol: str) -> None:
    for _ in range(3):
        amount = await _futures_position_amt(client, product_symbol)
        if amount == 0:
            return
        await client.place_market_order(
            product_symbol=product_symbol,
            side="SELL" if amount > 0 else "BUY",
            quantity=_format_decimal(abs(amount)),
            reduceOnly="true",
            newOrderRespType="RESULT",
        )
        for _ in range(10):
            await asyncio.sleep(1)
            if await _futures_position_amt(client, product_symbol) == 0:
                return
    raise AssertionError(f"{product_symbol} futures position did not close.")


async def _cleanup_futures_test_state(client: Client) -> None:
    if await client.get_open_orders(product_symbol=FUTURES_SYMBOL):
        await client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
    open_algo = await client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL)
    if _rows(open_algo, "orders"):
        await client.cancel_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL)
    await _close_futures_position(client, FUTURES_SYMBOL)
    if await client.get_open_orders(product_symbol=FUTURES_SYMBOL):
        pytest.fail("Binance futures still has open orders after cleanup.", pytrace=False)
    open_algo = await client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL)
    if _rows(open_algo, "orders"):
        pytest.fail("Binance futures still has open algo orders after cleanup.", pytrace=False)
    if await _futures_position_amt(client, FUTURES_SYMBOL) != 0:
        pytest.fail("Binance futures position still exists after cleanup.", pytrace=False)


async def _return_spot_btc_delta(client: Client, btc_before: Decimal) -> None:
    filters = _filters(await _symbol_exchange_info(client, SPOT_SYMBOL, futures=False))
    step_size = await _step_size(client, SPOT_SYMBOL, futures=False)
    min_qty = Decimal(filters["LOT_SIZE"]["minQty"])
    min_notional = _minimum_notional(filters, Decimal("10"))
    for _ in range(3):
        remaining = _round_to_step(
            await _spot_free(client, "BTC") - btc_before, step_size, ROUND_DOWN
        )
        if remaining <= 0:
            return
        best_bid = await _spot_best_bid(client, SPOT_SYMBOL)
        transferred = Decimal("0")
        reverse_type = None
        try:
            if remaining < min_qty or remaining * best_bid < min_notional:
                quote_amount = await _safe_spot_market_quote(client, SPOT_SYMBOL)
                transferred, reverse_type = await _ensure_balance(client, quote_amount, "spot")
                await client.place_order(
                    product_symbol=SPOT_SYMBOL,
                    side="BUY",
                    type_="MARKET",
                    quoteOrderQty=_format_decimal(quote_amount),
                    newOrderRespType="FULL",
                )
                await asyncio.sleep(1)
                remaining = _round_to_step(
                    await _spot_free(client, "BTC") - btc_before,
                    step_size,
                    ROUND_DOWN,
                )

            if remaining <= 0:
                return
            await client.place_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=_format_decimal(remaining),
                newOrderRespType="FULL",
            )
            await asyncio.sleep(1)
        finally:
            await _return_transfer(client, transferred, reverse_type)
    remaining = _round_to_step(await _spot_free(client, "BTC") - btc_before, step_size, ROUND_DOWN)
    assert remaining <= 0


@pytest.mark.asyncio
async def test_universal_transfer_round_trip(client):
    funding = await _funding_free(client, "USDT")
    spot = await _spot_free(client, "USDT")
    futures = await _futures_available(client, "USDT")
    if funding >= TRANSFER_AMOUNT:
        forward, reverse = "FUNDING_MAIN", "MAIN_FUNDING"
    elif spot >= TRANSFER_AMOUNT:
        forward, reverse = "MAIN_FUNDING", "FUNDING_MAIN"
    elif futures >= TRANSFER_AMOUNT:
        forward, reverse = "UMFUTURE_MAIN", "MAIN_UMFUTURE"
    else:
        pytest.fail("Insufficient Binance USDT for universal transfer round-trip.", pytrace=False)

    response = await client.create_universal_transfer(
        type_=forward,
        asset="USDT",
        amount=_format_decimal(TRANSFER_AMOUNT),
    )
    assert response.get("tranId")
    try:
        await asyncio.sleep(1)
        assert await client.get_universal_transfer_history(type_=forward, size=1) is not None
    finally:
        await client.create_universal_transfer(
            type_=reverse,
            asset="USDT",
            amount=_format_decimal(TRANSFER_AMOUNT),
        )


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_post_only_order_lifecycle(client):
    quantity, price = await _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    btc_before = await _spot_free(client, "BTC")
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) * Decimal("1.05"),
        "spot",
    )
    test_res = await client.test_order(
        product_symbol=SPOT_SYMBOL,
        side="BUY",
        type_="LIMIT_MAKER",
        quantity=quantity,
        price=price,
    )
    assert test_res is not None

    try:
        creators = (
            lambda: client.place_limit_order(SPOT_SYMBOL, "BUY", quantity, price),
            lambda: client.place_limit_buy_order(SPOT_SYMBOL, quantity, price),
            lambda: client.place_post_only_limit_order(SPOT_SYMBOL, "BUY", quantity, price),
            lambda: client.place_post_only_limit_buy_order(SPOT_SYMBOL, quantity, price),
        )
        for create_order in creators:
            order = None
            try:
                order = await create_order()
                order_id = int(order["orderId"])
                queried = await client.get_order(
                    product_symbol=SPOT_SYMBOL,
                    orderId=order_id,
                )
                assert queried["orderId"] == order_id
                assert isinstance(await client.get_open_orders(product_symbol=SPOT_SYMBOL), list)
            finally:
                if order is not None:
                    await _cancel_order_if_present(client, SPOT_SYMBOL, int(order["orderId"]))
    finally:
        await _return_spot_btc_delta(client, btc_before)
        await _return_transfer(client, transferred, reverse_type)

    assert isinstance(await client.get_all_orders(product_symbol=SPOT_SYMBOL, limit=1), list)
    assert isinstance(await client.get_account_trades(product_symbol=SPOT_SYMBOL, limit=1), list)


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_cancel_all_open_orders(client):
    if await client.get_open_orders(product_symbol=SPOT_SYMBOL):
        await client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)

    quantity, price = await _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    btc_before = await _spot_free(client, "BTC")
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) * Decimal("1.05"),
        "spot",
    )
    try:
        await client.place_post_only_limit_buy_order(
            product_symbol=SPOT_SYMBOL,
            quantity=quantity,
            price=price,
        )
        await client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)
        assert await client.get_open_orders(product_symbol=SPOT_SYMBOL) == []
    finally:
        if await client.get_open_orders(product_symbol=SPOT_SYMBOL):
            await client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)
        await _return_spot_btc_delta(client, btc_before)
        await _return_transfer(client, transferred, reverse_type)


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_market_order_round_trip(client):
    quote_amount = await _safe_spot_market_quote(client, SPOT_SYMBOL)
    transferred, reverse_type = await _ensure_balance(
        client,
        quote_amount,
        "spot",
    )
    step_size = await _step_size(client, SPOT_SYMBOL, futures=False)
    tick_size = await _tick_size(client, SPOT_SYMBOL, futures=False)
    btc_before = await _spot_free(client, "BTC")
    try:
        order = await client.place_order(
            product_symbol=SPOT_SYMBOL,
            side="BUY",
            type_="MARKET",
            quoteOrderQty=_format_decimal(quote_amount),
            newOrderRespType="FULL",
        )
        assert order["status"] == "FILLED"

        acquired = _round_to_step(
            await _spot_free(client, "BTC") - btc_before,
            step_size,
            ROUND_DOWN,
        )
        assert acquired > 0
        sell_price = _format_decimal(
            _round_to_step(
                Decimal((await client.get_spot_price(product_symbol=SPOT_SYMBOL))["price"])
                + tick_size,
                tick_size,
                ROUND_UP,
            )
        )
        for create_order in (
            lambda quantity: client.place_limit_sell_order(SPOT_SYMBOL, quantity, sell_price),
            lambda quantity: client.place_post_only_limit_sell_order(
                SPOT_SYMBOL, quantity, sell_price
            ),
        ):
            remaining = _round_to_step(
                await _spot_free(client, "BTC") - btc_before,
                step_size,
                ROUND_DOWN,
            )
            if remaining <= 0:
                break
            sell_order = None
            try:
                sell_order = await create_order(_format_decimal(remaining))
            finally:
                if sell_order is not None:
                    await _cancel_order_if_present(
                        client,
                        SPOT_SYMBOL,
                        int(sell_order["orderId"]),
                    )

        remaining = _round_to_step(
            await _spot_free(client, "BTC") - btc_before,
            step_size,
            ROUND_DOWN,
        )
        if remaining > 0:
            sell = await client.place_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=_format_decimal(remaining),
                newOrderRespType="FULL",
            )
            assert sell["status"] == "FILLED"
    finally:
        await _return_spot_btc_delta(client, btc_before)
        await _return_transfer(client, transferred, reverse_type)


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_post_only_order_lifecycle(client):
    await _cleanup_futures_test_state(client)
    quantity, price = await _safe_buy_order_params(client, FUTURES_SYMBOL, futures=True)
    leverage = await client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)
    assert leverage["leverage"] == 20
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) / Decimal("20") * Decimal("1.05"),
        "futures",
    )
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
        try:
            order = await client.place_post_only_limit_buy_order(
                product_symbol=FUTURES_SYMBOL,
                quantity=quantity,
                price=price,
            )
        except FailedRequestError as exc:
            if "insufficient" in str(exc).lower() or "-2019" in str(exc):
                pytest.fail(
                    f"Insufficient Binance futures margin for post-only order: {exc}",
                    pytrace=False,
                )
            raise
        order_id = int(order["orderId"])
        queried = await client.get_order(product_symbol=FUTURES_SYMBOL, orderId=order_id)
        assert queried["orderId"] == order_id
        assert isinstance(await client.get_open_orders(product_symbol=FUTURES_SYMBOL), list)
        assert isinstance(await client.get_all_open_orders(product_symbol=FUTURES_SYMBOL), list)
    finally:
        if order is not None:
            await _cancel_order_if_present(client, FUTURES_SYMBOL, int(order["orderId"]))
        await _cleanup_futures_test_state(client)
        await _return_transfer(client, transferred, reverse_type)

    assert isinstance(await client.get_all_orders(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(
        await client.get_future_all_order(product_symbol=FUTURES_SYMBOL, limit=1),
        list,
    )
    assert isinstance(await client.get_account_trades(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(await client.get_future_position(product_symbol=FUTURES_SYMBOL), list)


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_cancel_all_open_orders(client):
    await _cleanup_futures_test_state(client)

    quantity, price = await _safe_buy_order_params(client, FUTURES_SYMBOL, futures=True)
    leverage = await client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)
    assert leverage["leverage"] == 20
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    try:
        await client.place_post_only_limit_buy_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            price=price,
        )
        await client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
        assert await client.get_open_orders(product_symbol=FUTURES_SYMBOL) == []
    finally:
        if await client.get_open_orders(product_symbol=FUTURES_SYMBOL):
            await client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
        await _cleanup_futures_test_state(client)
        await _return_transfer(client, transferred, reverse_type)


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_market_long_round_trip(client):
    await _cleanup_futures_test_state(client)

    quantity = await _safe_market_quantity(client, FUTURES_SYMBOL)
    leverage = await client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)
    assert leverage["leverage"] == 20
    price = Decimal((await client.get_futures_ticker(product_symbol=FUTURES_SYMBOL))["askPrice"])
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(quantity) * price / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    try:
        open_order = await client.place_market_buy_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert open_order["status"] == "FILLED"
    finally:
        await _close_futures_position(client, FUTURES_SYMBOL)
        await _return_transfer(client, transferred, reverse_type)

    assert await _futures_position_amt(client, FUTURES_SYMBOL) == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_futures_market_short_round_trip(client):
    await _cleanup_futures_test_state(client)

    quantity = await _safe_market_quantity(client, FUTURES_SYMBOL)
    leverage = await client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)
    assert leverage["leverage"] == 20
    price = Decimal((await client.get_futures_ticker(product_symbol=FUTURES_SYMBOL))["bidPrice"])
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(quantity) * price / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    try:
        open_order = await client.place_market_sell_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert open_order["status"] == "FILLED"
    finally:
        await _close_futures_position(client, FUTURES_SYMBOL)
        await _return_transfer(client, transferred, reverse_type)

    assert await _futures_position_amt(client, FUTURES_SYMBOL) == 0


@pytest.mark.asyncio
@pytest.mark.private
async def test_advanced_order_validation(client):
    spot_quantity, spot_price = await _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    spot_tick = await _tick_size(client, SPOT_SYMBOL, futures=False)
    spot_stop = _format_decimal(
        _round_to_step(Decimal(spot_price) * Decimal("1.05"), spot_tick, ROUND_UP)
    )
    spot_transferred, spot_reverse = await _ensure_balance(
        client,
        Decimal(spot_quantity) * Decimal(spot_stop) * Decimal("1.05"),
        "spot",
    )
    try:
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
    finally:
        await _return_transfer(client, spot_transferred, spot_reverse)

    futures_quantity = await _safe_market_quantity(client, FUTURES_SYMBOL)
    futures_price = Decimal(
        (await client.get_futures_ticker(product_symbol=FUTURES_SYMBOL))["askPrice"]
    )
    futures_tick = await _tick_size(client, FUTURES_SYMBOL, futures=True)
    trigger_price = _format_decimal(
        _round_to_step(futures_price * Decimal("1.05"), futures_tick, ROUND_UP)
    )

    await _cleanup_futures_test_state(client)
    leverage = await client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)
    assert leverage["leverage"] == 20
    transferred, reverse_type = await _ensure_balance(
        client,
        Decimal(futures_quantity) * futures_price / Decimal("20") * Decimal("1.05"),
        "futures",
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
        queried = await _get_futures_algo_order_with_retry(client, client_algo_id)
        assert queried["clientAlgoId"] == client_algo_id
        assert isinstance(
            await client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL), list
        )
        await client.cancel_futures_algo_order(clientAlgoId=client_algo_id)
        algo_order = None

        client_algo_id = f"dcx{int(time.time() * 1000)}all"
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
    finally:
        if algo_order is not None:
            await client.cancel_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL)
        await _cleanup_futures_test_state(client)
        await _return_transfer(client, transferred, reverse_type)

    assert isinstance(
        await client.get_all_futures_algo_orders(product_symbol=FUTURES_SYMBOL, limit=1), list
    )
