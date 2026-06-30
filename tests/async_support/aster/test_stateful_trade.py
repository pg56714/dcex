# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os
import time
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.aster.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

ASTER_USER_ADDRESS = os.getenv("ASTER_USER_ADDRESS")
ASTER_SIGNER_ADDRESS = os.getenv("ASTER_SIGNER_ADDRESS")
ASTER_PRIVATE_KEY = os.getenv("ASTER_PRIVATE_KEY")
SPOT_SYMBOL = "USDCUSDT"
FUTURES_SYMBOL = "ASTERUSDT"
SPOT_USDT_BUFFER = Decimal("0.02")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Aster order tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        user_address=ASTER_USER_ADDRESS,
        signer_address=ASTER_SIGNER_ADDRESS,
        private_key=ASTER_PRIVATE_KEY,
        preload_product_table=False,
        timeout=20,
    ) as client_instance:
        await _cleanup_account(client_instance)
        try:
            yield client_instance
        finally:
            await _cleanup_account(client_instance)


def _dec(value: object) -> Decimal:
    return Decimal(str(value or "0"))


def _margin_type(value: object) -> str:
    return "CROSSED" if str(value).lower() in {"cross", "crossed"} else "ISOLATED"


async def _spot_balances(client: Client) -> dict[str, Decimal]:
    response = await client.get_spot_account()
    assert isinstance(response, dict)
    return {
        str(item["asset"]): _dec(item.get("free"))
        for item in response.get("balances", [])
        if isinstance(item, dict)
    }


async def _futures_balance(client: Client, asset: str) -> Decimal:
    response = await client.get_futures_balance()
    assert isinstance(response, list)
    item = next(
        (
            balance
            for balance in response
            if isinstance(balance, dict) and balance.get("asset") == asset
        ),
        {},
    )
    return _dec(item.get("balance"))


async def _market_info(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    response = await client.get_spot_exchange_info(SPOT_SYMBOL)
    assert isinstance(response, dict)
    market = next(
        item
        for item in response.get("symbols", [])
        if isinstance(item, dict) and item.get("symbol") == SPOT_SYMBOL
    )
    filters = {
        item["filterType"]: item
        for item in market.get("filters", [])
        if isinstance(item, dict) and item.get("filterType")
    }
    return (
        _dec(filters["PRICE_FILTER"]["tickSize"]),
        _dec(filters["LOT_SIZE"]["stepSize"]),
        _dec(filters["LOT_SIZE"]["minQty"]),
        _dec(filters["MIN_NOTIONAL"]["minNotional"]),
    )


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    return (value / step).to_integral_value(rounding=rounding) * step


async def _spot_order_params(client: Client) -> tuple[str, Decimal, Decimal]:
    _, step, min_qty, min_notional = await _market_info(client)
    book = await client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    assert isinstance(book, dict)
    bid = _dec(book["bids"][0][0])
    quantity = max(
        _round_to_step(min_notional * Decimal("1.01") / bid, step, ROUND_UP),
        min_qty,
    )
    transfer_amount = quantity
    buy_quote = min_notional * Decimal("1.01")
    return format(quantity, "f"), transfer_amount, buy_quote


async def _safe_sell_price(client: Client) -> str:
    tick, _, _, _ = await _market_info(client)
    book = await client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    value = _round_to_step(ask + tick, tick, ROUND_UP)
    return format(value, "f")


def _order_id(response: object) -> int:
    assert isinstance(response, dict)
    return int(response["orderId"])


async def _futures_market_info(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    response = await client.get_futures_exchange_info()
    assert isinstance(response, dict)
    market = next(
        item
        for item in response.get("symbols", [])
        if isinstance(item, dict) and item.get("symbol") == FUTURES_SYMBOL
    )
    filters = {
        item["filterType"]: item
        for item in market.get("filters", [])
        if isinstance(item, dict) and item.get("filterType")
    }
    return (
        _dec(filters["PRICE_FILTER"]["tickSize"]),
        _dec(filters["LOT_SIZE"]["stepSize"]),
        _dec(filters["MIN_NOTIONAL"]["notional"]),
    )


async def _futures_order_params(client: Client) -> tuple[str, str, str, str]:
    tick, step, min_notional = await _futures_market_info(client)
    book = await client.get_futures_orderbook(FUTURES_SYMBOL, limit=5)
    assert isinstance(book, dict)
    bid = _dec(book["bids"][0][0])

    def price_value(ticks_below: int) -> Decimal:
        value = _round_to_step(bid - tick * ticks_below, tick, ROUND_DOWN)
        if value <= 0:
            pytest.fail(f"{FUTURES_SYMBOL} futures bid is too small for a post-only test order.")
        return value

    first_price = price_value(1)
    modified_price = price_value(2)
    batch_price = price_value(3)
    quantity = _round_to_step(
        min_notional * Decimal("1.01") / batch_price,
        step,
        ROUND_UP,
    )
    return (
        format(quantity, "f"),
        format(first_price, "f"),
        format(modified_price, "f"),
        format(batch_price, "f"),
    )


async def _futures_safe_sell_price(client: Client) -> str:
    tick, _, _ = await _futures_market_info(client)
    book = await client.get_futures_orderbook(FUTURES_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    value = _round_to_step(ask + tick, tick, ROUND_UP)
    return format(value, "f")


async def _futures_position_amount(client: Client) -> Decimal:
    response = await client.get_futures_position_risk(FUTURES_SYMBOL)
    assert isinstance(response, list)
    position = next(
        (
            item
            for item in response
            if isinstance(item, dict) and item.get("symbol") == FUTURES_SYMBOL
        ),
        {},
    )
    return _dec(position.get("positionAmt"))


async def _wait_for_position(client: Client, *, open_: bool) -> Decimal:
    for _ in range(15):
        amount = await _futures_position_amount(client)
        if (amount != 0) is open_:
            return amount
        await _sleep(1)
    raise AssertionError(f"Aster {FUTURES_SYMBOL} position did not reach expected state.")


async def _cleanup_futures(client: Client) -> None:
    with suppress(Exception):
        await client.set_futures_countdown_cancel_all(FUTURES_SYMBOL, 0)
    with suppress(Exception):
        await client.cancel_all_futures_open_orders(FUTURES_SYMBOL)
    with suppress(Exception):
        amount = await _futures_position_amount(client)
        if amount > 0:
            await client.place_futures_order(
                FUTURES_SYMBOL,
                side="SELL",
                type_="MARKET",
                quantity=format(amount, "f"),
                reduceOnly=True,
                newOrderRespType="RESULT",
            )
        elif amount < 0:
            await client.place_futures_order(
                FUTURES_SYMBOL,
                side="BUY",
                type_="MARKET",
                quantity=format(abs(amount), "f"),
                reduceOnly=True,
                newOrderRespType="RESULT",
            )
    await _wait_for_position(client, open_=False)


async def _restore_futures_settings(
    client: Client,
    *,
    dual: bool,
    multi_assets: bool,
    margin_type: str,
) -> None:
    last_error: Exception | None = None
    for _ in range(15):
        try:
            current_multi = bool(
                (await client.get_futures_multi_assets_mode())["multiAssetsMargin"]
            )
            current_margin = _margin_type(
                (await client.get_futures_position_risk(FUTURES_SYMBOL))[0]["marginType"]
            )
            current_dual = bool((await client.get_futures_position_mode())["dualSidePosition"])

            if current_multi and not multi_assets:
                await client.set_futures_multi_assets_mode(False)
                current_multi = False
            if current_margin != margin_type:
                await client.set_futures_margin_type(FUTURES_SYMBOL, margin_type)
            if not current_multi and multi_assets:
                await client.set_futures_multi_assets_mode(True)
            if current_dual != dual:
                await client.set_futures_position_mode(dual)

            assert (
                bool((await client.get_futures_multi_assets_mode())["multiAssetsMargin"])
                is multi_assets
            )
            assert (
                _margin_type(
                    (await client.get_futures_position_risk(FUTURES_SYMBOL))[0]["marginType"]
                )
                == margin_type
            )
            assert bool((await client.get_futures_position_mode())["dualSidePosition"]) is dual
        except (AssertionError, FailedRequestError) as exc:
            last_error = exc
            await _sleep(1)
        else:
            return
    raise AssertionError("Failed to restore Aster futures account settings.") from last_error


async def _transfer(
    client: Client,
    *,
    amount: Decimal,
    asset: str,
    kind_type: str,
    market: str,
) -> None:
    if amount <= 0:
        return
    response = await client.transfer_spot_futures(
        amount=format(amount, "f"),
        asset=asset,
        clientTranId=f"dcex-{asset.lower()}-{time.time_ns()}",
        kindType=kind_type,
        market=market,
    )
    assert isinstance(response, dict)
    assert response["status"] == "SUCCESS"


async def _return_test_funds(
    client: Client,
    initial_balances: dict[str, Decimal],
) -> None:
    with suppress(Exception):
        await client.cancel_all_spot_open_orders(SPOT_SYMBOL)
    current = await _spot_balances(client)
    for asset in ("USDC", "USDT"):
        delta = current.get(asset, Decimal("0")) - initial_balances.get(asset, Decimal("0"))
        if delta > 0:
            await _transfer(
                client,
                amount=delta,
                asset=asset,
                kind_type="SPOT_FUTURE",
                market="spot",
            )


async def _cleanup_account(client: Client) -> None:
    if await client.get_spot_open_orders(SPOT_SYMBOL):
        await client.cancel_all_spot_open_orders(SPOT_SYMBOL)
    await _cleanup_futures(client)
    assert await client.get_spot_open_orders(SPOT_SYMBOL) == []
    assert await client.get_futures_open_orders(FUTURES_SYMBOL) == []
    assert await _futures_position_amount(client) == 0


@pytest.mark.asyncio
async def test_spot_order_and_transfer_lifecycle(client):
    await _cleanup_account(client)
    spot_quantity, spot_transfer_amount, spot_buy_quote = await _spot_order_params(client)
    if await _futures_balance(client, "USDC") < spot_transfer_amount:
        pytest.fail("Aster futures wallet lacks the minimum USDC for this spot test.")
    if await _futures_balance(client, "USDT") < SPOT_USDT_BUFFER:
        pytest.fail("Aster futures wallet requires at least 0.02 USDT.")

    initial_balances = await _spot_balances(client)
    try:
        await _transfer(
            client,
            amount=spot_transfer_amount,
            asset="USDC",
            kind_type="FUTURE_SPOT",
            market="futures",
        )
        await _transfer(
            client,
            amount=SPOT_USDT_BUFFER,
            asset="USDT",
            kind_type="FUTURE_SPOT",
            market="futures",
        )
        await _sleep(2)

        price = await _safe_sell_price(client)
        first_id = _order_id(
            await client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="LIMIT",
                quantity=spot_quantity,
                price=price,
                timeInForce="GTC",
            )
        )
        assert isinstance(
            await client.get_spot_order(SPOT_SYMBOL, orderId=first_id),
            dict,
        )
        assert isinstance(
            await client.get_spot_open_order(SPOT_SYMBOL, orderId=first_id),
            dict,
        )
        assert isinstance(
            await client.cancel_spot_order(SPOT_SYMBOL, orderId=first_id),
            dict,
        )

        second_id = _order_id(
            await client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="LIMIT",
                quantity=spot_quantity,
                price=price,
                timeInForce="GTC",
            )
        )
        assert isinstance(
            await client.cancel_all_spot_open_orders(
                SPOT_SYMBOL,
                orderIdList=[second_id],
            ),
            dict,
        )

        assert isinstance(
            await client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="MARKET",
                quantity=spot_quantity,
            ),
            dict,
        )
        await _sleep(2)
        gained_usdt = (await _spot_balances(client)).get(
            "USDT", Decimal("0")
        ) - initial_balances.get("USDT", Decimal("0"))
        assert gained_usdt >= spot_buy_quote

        assert isinstance(
            await client.place_spot_order(
                SPOT_SYMBOL,
                side="BUY",
                type_="MARKET",
                quoteOrderQty=format(spot_buy_quote, "f"),
            ),
            dict,
        )
        await _sleep(2)

        assert await client.get_spot_all_orders(SPOT_SYMBOL, limit=20)
        assert await client.get_spot_user_trades(SPOT_SYMBOL, limit=20)
    finally:
        await _return_test_funds(client, initial_balances)


@pytest.mark.asyncio
async def test_futures_order_lifecycle(client):
    await _cleanup_account(client)

    position_mode = await client.get_futures_position_mode()
    multi_assets_mode = await client.get_futures_multi_assets_mode()
    position_risk = await client.get_futures_position_risk(FUTURES_SYMBOL)
    assert isinstance(position_mode, dict)
    assert isinstance(multi_assets_mode, dict)
    assert isinstance(position_risk, list)
    original_dual = bool(position_mode["dualSidePosition"])
    original_multi_assets = bool(multi_assets_mode["multiAssetsMargin"])
    original_margin_type = _margin_type(position_risk[0].get("marginType", "crossed"))

    quantity, price, modified_price, batch_price = await _futures_order_params(client)
    try:
        if original_dual:
            await client.set_futures_position_mode(False)
        if original_multi_assets:
            await client.set_futures_multi_assets_mode(False)
        if original_margin_type != "ISOLATED":
            await client.set_futures_margin_type(FUTURES_SYMBOL, "ISOLATED")
        leverage = await client.set_futures_leverage(FUTURES_SYMBOL, 20)
        assert isinstance(leverage, dict)
        assert int(leverage["leverage"]) == 20

        limit_id = _order_id(
            await client.place_futures_order(
                FUTURES_SYMBOL,
                side="BUY",
                type_="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC",
            )
        )
        assert isinstance(
            await client.get_futures_order(FUTURES_SYMBOL, orderId=limit_id),
            dict,
        )
        assert isinstance(
            await client.get_futures_open_order(FUTURES_SYMBOL, orderId=limit_id),
            dict,
        )
        modified = await client.modify_futures_order(
            FUTURES_SYMBOL,
            orderId=limit_id,
            quantity=quantity,
            price=modified_price,
        )
        assert isinstance(modified, dict)
        assert str(modified["price"]) == modified_price
        assert isinstance(
            await client.cancel_futures_order(FUTURES_SYMBOL, orderId=limit_id),
            dict,
        )

        batch = await client.place_futures_batch_orders(
            [
                {
                    "product_symbol": FUTURES_SYMBOL,
                    "side": "BUY",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                    "quantity": quantity,
                    "price": modified_price,
                },
                {
                    "product_symbol": FUTURES_SYMBOL,
                    "side": "BUY",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                    "quantity": quantity,
                    "price": batch_price,
                },
            ]
        )
        assert isinstance(batch, list)
        batch_ids = [int(item["orderId"]) for item in batch]
        canceled_batch = await client.cancel_futures_batch_orders(
            FUTURES_SYMBOL,
            orderIdList=batch_ids,
        )
        assert isinstance(canceled_batch, list)

        await client.place_futures_order(
            FUTURES_SYMBOL,
            side="BUY",
            type_="LIMIT",
            quantity=quantity,
            price=batch_price,
            timeInForce="GTC",
        )
        assert isinstance(
            await client.cancel_all_futures_open_orders(FUTURES_SYMBOL),
            dict,
        )

        await client.place_futures_order(
            FUTURES_SYMBOL,
            side="BUY",
            type_="LIMIT",
            quantity=quantity,
            price=batch_price,
            timeInForce="GTC",
        )
        assert isinstance(
            await client.set_futures_countdown_cancel_all(FUTURES_SYMBOL, 1000),
            dict,
        )
        await _sleep(2)
        assert await client.get_futures_open_orders(FUTURES_SYMBOL) == []
        await client.set_futures_countdown_cancel_all(FUTURES_SYMBOL, 0)

        chase = await client.place_futures_chase_order(
            FUTURES_SYMBOL,
            side="BUY",
            quantityUnit="BASE",
            quantity=quantity,
            chaseOffset="0.01",
            chaseOffsetType="ABSOLUTE",
            maxChaseOffset="0.10",
            maxChaseOffsetType="ABSOLUTE",
            priceLimit=price,
            timeInForce="GTX",
            clientStrategyId=f"dcex-chase-{time.time_ns()}"[-28:],
        )
        assert isinstance(chase, dict)
        await _sleep(2)
        chase_orders = await client.get_futures_open_orders(FUTURES_SYMBOL)
        assert isinstance(chase_orders, list)
        for order in chase_orders:
            await client.cancel_futures_order(
                FUTURES_SYMBOL,
                orderId=int(order["orderId"]),
            )

        opened = await client.place_futures_order(
            FUTURES_SYMBOL,
            side="BUY",
            type_="MARKET",
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert isinstance(opened, dict)
        amount = await _wait_for_position(client, open_=True)
        assert amount > 0

        assert isinstance(
            await client.modify_futures_position_margin(
                FUTURES_SYMBOL,
                amount="0.1",
                type_=1,
            ),
            dict,
        )
        assert isinstance(
            await client.modify_futures_position_margin(
                FUTURES_SYMBOL,
                amount="0.1",
                type_=2,
            ),
            dict,
        )

        closed = await client.place_futures_order(
            FUTURES_SYMBOL,
            side="SELL",
            type_="MARKET",
            quantity=format(amount, "f"),
            reduceOnly=True,
            newOrderRespType="RESULT",
        )
        assert isinstance(closed, dict)
        assert await _wait_for_position(client, open_=False) == 0
        assert await client.get_futures_all_orders(FUTURES_SYMBOL, limit=20)
        assert await client.get_futures_user_trades(FUTURES_SYMBOL, limit=20)
    finally:
        await _cleanup_futures(client)
        await _restore_futures_settings(
            client,
            dual=original_dual,
            multi_assets=original_multi_assets,
            margin_type=original_margin_type,
        )


@pytest.mark.asyncio
async def test_futures_strategy_documented_payloads(client):
    await _cleanup_account(client)

    quantity, price, _, _ = await _futures_order_params(client)
    sell_price = await _futures_safe_sell_price(client)
    client_strategy_id = f"dcex-{str(time.time_ns())[-18:]}"

    first_order = {
        "strategySubId": "1",
        "securityType": "USDT_FUTURES",
        "symbol": FUTURES_SYMBOL,
        "side": "BUY",
        "positionSide": "BOTH",
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": "GTC",
    }
    second_order = {
        "strategySubId": "2",
        "securityType": "USDT_FUTURES",
        "symbol": FUTURES_SYMBOL,
        "side": "SELL",
        "positionSide": "BOTH",
        "type": "LIMIT",
        "quantity": quantity,
        "price": sell_price,
        "timeInForce": "GTC",
        "reduceOnly": "true",
        "firstDrivenId": 1,
        "firstDrivenOn": "FILLED",
        "firstTrigger": "PLACE_ORDER",
    }

    # The documented payload is currently rejected because Aster treats the
    # documented optional firstDrivenId as mandatory for every sub-order.
    with pytest.raises(FailedRequestError, match="firstDrivenId") as place_error:
        await client.place_futures_strategy_order(
            clientStrategyId=client_strategy_id,
            strategyType="OTO",
            subOrderList=[first_order, second_order],
        )
    assert place_error.value.status_code == 400
    assert place_error.value.request == "<redacted>"

    update_order = dict(first_order)
    update_order.update(firstDrivenId=0, secondDrivenId=0)
    updated = await client.update_futures_strategy_order(
        strategyId="0",
        strategyType="OTO",
        subOrderList=[update_order],
    )
    assert isinstance(updated, list)
    assert updated[0]["updateStatus"] == "FAIL"
    assert int(updated[0]["failureCode"]) == -4124


async def _sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)
