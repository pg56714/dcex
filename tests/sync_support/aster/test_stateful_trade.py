# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os
import time
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.aster.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

ASTER_USER_ADDRESS = os.getenv("ASTER_USER_ADDRESS")
ASTER_SIGNER_ADDRESS = os.getenv("ASTER_SIGNER_ADDRESS")
ASTER_PRIVATE_KEY = os.getenv("ASTER_PRIVATE_KEY")
SPOT_SYMBOL = "USDCUSDT"
SPOT_BASE_ASSET = "USDC"
SPOT_QUOTE_ASSET = "USDT"
FUTURES_SYMBOL = "ASTERUSDT"
SPOT_NOTIONAL_BUFFER = Decimal("1.01")
SPOT_DUST_TOLERANCE = Decimal("0.00000001")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Aster order tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        user_address=ASTER_USER_ADDRESS,
        signer_address=ASTER_SIGNER_ADDRESS,
        private_key=ASTER_PRIVATE_KEY,
        preload_product_table=False,
        timeout=20,
    )
    try:
        _cleanup_account(client_instance)
        yield client_instance
    finally:
        _cleanup_account(client_instance)
        client_instance.close()


def _dec(value: object) -> Decimal:
    return Decimal(str(value or "0"))


def _margin_type(value: object) -> str:
    return "CROSSED" if str(value).lower() in {"cross", "crossed"} else "ISOLATED"


def _spot_balances(client: Client) -> dict[str, Decimal]:
    response = client.get_spot_account()
    assert isinstance(response, dict)
    return {
        str(item["asset"]): _dec(item.get("free"))
        for item in response.get("balances", [])
        if isinstance(item, dict)
    }


def _futures_balance(client: Client, asset: str) -> Decimal:
    response = client.get_futures_balance()
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


def _market_info(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    response = client.get_spot_exchange_info(SPOT_SYMBOL)
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


def _spot_order_params(client: Client) -> tuple[str, Decimal]:
    _, step, min_qty, min_notional = _market_info(client)
    book = client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    quantity = max(
        _round_to_step(min_notional * SPOT_NOTIONAL_BUFFER / ask, step, ROUND_UP),
        min_qty,
    )
    buy_quote = (quantity * ask * SPOT_NOTIONAL_BUFFER).quantize(
        Decimal("0.00000001"),
        rounding=ROUND_UP,
    )
    return format(quantity, "f"), buy_quote


def _safe_sell_price(client: Client) -> str:
    tick, _, _, _ = _market_info(client)
    book = client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    value = _round_to_step(ask + tick, tick, ROUND_UP)
    return format(value, "f")


def _wait_for_spot_delta(client: Client, asset: str, before: Decimal) -> Decimal:
    for _ in range(10):
        delta = _spot_balances(client).get(asset, Decimal("0")) - before
        if delta > 0:
            return delta
        time.sleep(1)
    return Decimal("0")


def _spot_sell_quantity(client: Client, amount: Decimal) -> Decimal:
    _, step, _, _ = _market_info(client)
    return _round_to_step(amount, step, ROUND_DOWN)


def _sell_spot_base_to_quote(client: Client, amount: Decimal) -> None:
    quantity = _spot_sell_quantity(client, amount)
    if quantity <= 0:
        return
    assert isinstance(
        client.place_spot_order(
            SPOT_SYMBOL,
            side="SELL",
            type_="MARKET",
            quantity=format(quantity, "f"),
        ),
        dict,
    )
    time.sleep(2)


def _cleanup_spot_base(client: Client, initial_balances: dict[str, Decimal]) -> None:
    _, step, min_qty, min_notional = _market_info(client)
    current = _spot_balances(client)
    delta = current.get(SPOT_BASE_ASSET, Decimal("0")) - initial_balances.get(
        SPOT_BASE_ASSET,
        Decimal("0"),
    )
    if delta <= SPOT_DUST_TOLERANCE:
        return
    book = client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    assert isinstance(book, dict)
    bid = _dec(book["bids"][0][0])
    ask = _dec(book["asks"][0][0])
    sell_quantity = _spot_sell_quantity(client, delta)
    if sell_quantity < min_qty or sell_quantity * bid < min_notional:
        target = _round_to_step(max(min_qty, min_notional / bid, delta), step, ROUND_UP)
        top_up = target - delta + SPOT_DUST_TOLERANCE
        if top_up > 0:
            if _futures_balance(client, SPOT_BASE_ASSET) >= top_up:
                _transfer(
                    client,
                    amount=top_up,
                    asset=SPOT_BASE_ASSET,
                    kind_type="FUTURE_SPOT",
                    market="futures",
                )
            else:
                quote_needed = max((top_up + step) * ask, min_notional) * SPOT_NOTIONAL_BUFFER
                quote_needed = quote_needed.quantize(
                    SPOT_DUST_TOLERANCE,
                    rounding=ROUND_UP,
                )
                _ensure_spot_quote(client, quote_needed)
                assert isinstance(
                    client.place_spot_order(
                        SPOT_SYMBOL,
                        side="BUY",
                        type_="MARKET",
                        quoteOrderQty=format(quote_needed, "f"),
                    ),
                    dict,
                )
            time.sleep(2)
            delta = _spot_balances(client).get(
                SPOT_BASE_ASSET, Decimal("0")
            ) - initial_balances.get(
                SPOT_BASE_ASSET,
                Decimal("0"),
            )
            sell_quantity = _spot_sell_quantity(client, delta)
    if sell_quantity < min_qty or sell_quantity * bid < min_notional:
        pytest.fail(f"Aster spot {SPOT_BASE_ASSET} is below minimum sell size.")
    _sell_spot_base_to_quote(client, delta)
    remaining = _spot_balances(client).get(SPOT_BASE_ASSET, Decimal("0")) - initial_balances.get(
        SPOT_BASE_ASSET,
        Decimal("0"),
    )
    if remaining > SPOT_DUST_TOLERANCE:
        _transfer(
            client,
            amount=remaining,
            asset=SPOT_BASE_ASSET,
            kind_type="SPOT_FUTURE",
            market="spot",
        )
        time.sleep(2)
        remaining = _spot_balances(client).get(
            SPOT_BASE_ASSET, Decimal("0")
        ) - initial_balances.get(
            SPOT_BASE_ASSET,
            Decimal("0"),
        )
    if remaining > SPOT_DUST_TOLERANCE:
        pytest.fail(f"Aster spot {SPOT_BASE_ASSET} balance still exists after cleanup.")


def _order_id(response: object) -> int:
    assert isinstance(response, dict)
    return int(response["orderId"])


def _futures_market_info(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    response = client.get_futures_exchange_info()
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


def _futures_order_params(client: Client) -> tuple[str, str, str, str]:
    tick, step, min_notional = _futures_market_info(client)
    book = client.get_futures_orderbook(FUTURES_SYMBOL, limit=5)
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


def _futures_safe_sell_price(client: Client) -> str:
    tick, _, _ = _futures_market_info(client)
    book = client.get_futures_orderbook(FUTURES_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    value = _round_to_step(ask + tick, tick, ROUND_UP)
    return format(value, "f")


def _futures_position_amount(client: Client) -> Decimal:
    response = client.get_futures_position_risk(FUTURES_SYMBOL)
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


def _wait_for_position(client: Client, *, open_: bool) -> Decimal:
    for _ in range(15):
        amount = _futures_position_amount(client)
        if (amount != 0) is open_:
            return amount
        time.sleep(1)
    raise AssertionError(f"Aster {FUTURES_SYMBOL} position did not reach expected state.")


def _cleanup_futures(client: Client) -> None:
    with suppress(Exception):
        client.set_futures_countdown_cancel_all(FUTURES_SYMBOL, 0)
    with suppress(Exception):
        client.cancel_all_futures_open_orders(FUTURES_SYMBOL)
    with suppress(Exception):
        amount = _futures_position_amount(client)
        if amount > 0:
            client.place_futures_order(
                FUTURES_SYMBOL,
                side="SELL",
                type_="MARKET",
                quantity=format(amount, "f"),
                reduceOnly=True,
                newOrderRespType="RESULT",
            )
        elif amount < 0:
            client.place_futures_order(
                FUTURES_SYMBOL,
                side="BUY",
                type_="MARKET",
                quantity=format(abs(amount), "f"),
                reduceOnly=True,
                newOrderRespType="RESULT",
            )
    _wait_for_position(client, open_=False)


def _restore_futures_settings(
    client: Client,
    *,
    dual: bool,
    multi_assets: bool,
    margin_type: str,
) -> None:
    last_error: Exception | None = None
    for _ in range(15):
        try:
            current_multi = bool(client.get_futures_multi_assets_mode()["multiAssetsMargin"])
            current_margin = _margin_type(
                client.get_futures_position_risk(FUTURES_SYMBOL)[0]["marginType"]
            )
            current_dual = bool(client.get_futures_position_mode()["dualSidePosition"])

            if current_multi and not multi_assets:
                client.set_futures_multi_assets_mode(False)
                current_multi = False
            if current_margin != margin_type:
                client.set_futures_margin_type(FUTURES_SYMBOL, margin_type)
            if not current_multi and multi_assets:
                client.set_futures_multi_assets_mode(True)
            if current_dual != dual:
                client.set_futures_position_mode(dual)

            assert bool(client.get_futures_multi_assets_mode()["multiAssetsMargin"]) is multi_assets
            assert (
                _margin_type(client.get_futures_position_risk(FUTURES_SYMBOL)[0]["marginType"])
                == margin_type
            )
            assert bool(client.get_futures_position_mode()["dualSidePosition"]) is dual
        except (AssertionError, FailedRequestError) as exc:
            last_error = exc
            time.sleep(1)
        else:
            return
    raise AssertionError("Failed to restore Aster futures account settings.") from last_error


def _transfer(
    client: Client,
    *,
    amount: Decimal,
    asset: str,
    kind_type: str,
    market: str,
) -> None:
    if amount <= 0:
        return
    response = client.transfer_spot_futures(
        amount=format(amount, "f"),
        asset=asset,
        clientTranId=f"dcex-{asset.lower()}-{time.time_ns()}",
        kindType=kind_type,
        market=market,
    )
    assert isinstance(response, dict)
    assert response["status"] == "SUCCESS"


def _ensure_spot_quote(client: Client, required: Decimal) -> None:
    spot_quote = _spot_balances(client).get(SPOT_QUOTE_ASSET, Decimal("0"))
    if spot_quote >= required:
        return
    needed = required - spot_quote
    if _futures_balance(client, SPOT_QUOTE_ASSET) < needed:
        pytest.fail("Aster account lacks transferable USDT for this spot test.")
    _transfer(
        client,
        amount=needed,
        asset=SPOT_QUOTE_ASSET,
        kind_type="FUTURE_SPOT",
        market="futures",
    )
    time.sleep(2)
    if _spot_balances(client).get(SPOT_QUOTE_ASSET, Decimal("0")) < required:
        pytest.fail("Aster spot USDT remains insufficient after transfer.")


def _return_test_funds(
    client: Client,
    initial_balances: dict[str, Decimal],
) -> None:
    with suppress(Exception):
        client.cancel_all_spot_open_orders(SPOT_SYMBOL)
    _cleanup_spot_base(client, initial_balances)
    current = _spot_balances(client)
    delta = current.get(SPOT_QUOTE_ASSET, Decimal("0")) - initial_balances.get(
        SPOT_QUOTE_ASSET,
        Decimal("0"),
    )
    if delta > 0:
        _transfer(
            client,
            amount=delta,
            asset=SPOT_QUOTE_ASSET,
            kind_type="SPOT_FUTURE",
            market="spot",
        )


def _cleanup_account(client: Client) -> None:
    if client.get_spot_open_orders(SPOT_SYMBOL):
        client.cancel_all_spot_open_orders(SPOT_SYMBOL)
    _cleanup_spot_base(client, {})
    spot_quote = _spot_balances(client).get(SPOT_QUOTE_ASSET, Decimal("0"))
    if spot_quote > 0:
        _transfer(
            client,
            amount=spot_quote,
            asset=SPOT_QUOTE_ASSET,
            kind_type="SPOT_FUTURE",
            market="spot",
        )
    _cleanup_futures(client)
    assert client.get_spot_open_orders(SPOT_SYMBOL) == []
    assert client.get_futures_open_orders(FUTURES_SYMBOL) == []
    assert _futures_position_amount(client) == 0


def test_spot_order_and_transfer_lifecycle(client):
    _cleanup_account(client)
    _spot_quantity, spot_buy_quote = _spot_order_params(client)

    initial_balances = _spot_balances(client)
    try:
        _ensure_spot_quote(client, spot_buy_quote)

        before_base = _spot_balances(client).get(SPOT_BASE_ASSET, Decimal("0"))
        assert isinstance(
            client.place_spot_order(
                SPOT_SYMBOL,
                side="BUY",
                type_="MARKET",
                quoteOrderQty=format(spot_buy_quote, "f"),
            ),
            dict,
        )
        acquired = _wait_for_spot_delta(client, SPOT_BASE_ASSET, before_base)
        sell_quantity = _spot_sell_quantity(client, acquired)
        if sell_quantity <= 0:
            pytest.fail(f"Aster spot market buy did not produce sellable {SPOT_BASE_ASSET}.")

        price = _safe_sell_price(client)
        first_id = _order_id(
            client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="LIMIT",
                quantity=format(sell_quantity, "f"),
                price=price,
                timeInForce="GTC",
            )
        )
        assert isinstance(client.get_spot_order(SPOT_SYMBOL, orderId=first_id), dict)
        assert isinstance(client.get_spot_open_order(SPOT_SYMBOL, orderId=first_id), dict)
        assert isinstance(client.cancel_spot_order(SPOT_SYMBOL, orderId=first_id), dict)

        second_id = _order_id(
            client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="LIMIT",
                quantity=format(sell_quantity, "f"),
                price=price,
                timeInForce="GTC",
            )
        )
        assert isinstance(
            client.cancel_all_spot_open_orders(
                SPOT_SYMBOL,
                orderIdList=[second_id],
            ),
            dict,
        )

        assert isinstance(
            client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="MARKET",
                quantity=format(sell_quantity, "f"),
            ),
            dict,
        )
        time.sleep(2)

        assert client.get_spot_all_orders(SPOT_SYMBOL, limit=20)
        assert client.get_spot_user_trades(SPOT_SYMBOL, limit=20)
    finally:
        _return_test_funds(client, initial_balances)


def test_futures_order_lifecycle(client):
    _cleanup_account(client)

    position_mode = client.get_futures_position_mode()
    multi_assets_mode = client.get_futures_multi_assets_mode()
    position_risk = client.get_futures_position_risk(FUTURES_SYMBOL)
    assert isinstance(position_mode, dict)
    assert isinstance(multi_assets_mode, dict)
    assert isinstance(position_risk, list)
    original_dual = bool(position_mode["dualSidePosition"])
    original_multi_assets = bool(multi_assets_mode["multiAssetsMargin"])
    original_margin_type = _margin_type(position_risk[0].get("marginType", "crossed"))

    quantity, price, modified_price, batch_price = _futures_order_params(client)
    try:
        if original_dual:
            client.set_futures_position_mode(False)
        if original_multi_assets:
            client.set_futures_multi_assets_mode(False)
        if original_margin_type != "ISOLATED":
            client.set_futures_margin_type(FUTURES_SYMBOL, "ISOLATED")
        leverage = client.set_futures_leverage(FUTURES_SYMBOL, 20)
        assert isinstance(leverage, dict)
        assert int(leverage["leverage"]) == 20

        limit_id = _order_id(
            client.place_futures_order(
                FUTURES_SYMBOL,
                side="BUY",
                type_="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC",
            )
        )
        assert isinstance(
            client.get_futures_order(FUTURES_SYMBOL, orderId=limit_id),
            dict,
        )
        assert isinstance(
            client.get_futures_open_order(FUTURES_SYMBOL, orderId=limit_id),
            dict,
        )
        modified = client.modify_futures_order(
            FUTURES_SYMBOL,
            orderId=limit_id,
            quantity=quantity,
            price=modified_price,
        )
        assert isinstance(modified, dict)
        assert str(modified["price"]) == modified_price
        assert isinstance(
            client.cancel_futures_order(FUTURES_SYMBOL, orderId=limit_id),
            dict,
        )

        batch = client.place_futures_batch_orders(
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
        canceled_batch = client.cancel_futures_batch_orders(
            FUTURES_SYMBOL,
            orderIdList=batch_ids,
        )
        assert isinstance(canceled_batch, list)

        client.place_futures_order(
            FUTURES_SYMBOL,
            side="BUY",
            type_="LIMIT",
            quantity=quantity,
            price=batch_price,
            timeInForce="GTC",
        )
        assert isinstance(
            client.cancel_all_futures_open_orders(FUTURES_SYMBOL),
            dict,
        )

        client.place_futures_order(
            FUTURES_SYMBOL,
            side="BUY",
            type_="LIMIT",
            quantity=quantity,
            price=batch_price,
            timeInForce="GTC",
        )
        assert isinstance(
            client.set_futures_countdown_cancel_all(FUTURES_SYMBOL, 1000),
            dict,
        )
        time.sleep(2)
        assert client.get_futures_open_orders(FUTURES_SYMBOL) == []
        client.set_futures_countdown_cancel_all(FUTURES_SYMBOL, 0)

        chase = client.place_futures_chase_order(
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
        time.sleep(2)
        chase_orders = client.get_futures_open_orders(FUTURES_SYMBOL)
        assert isinstance(chase_orders, list)
        for order in chase_orders:
            client.cancel_futures_order(
                FUTURES_SYMBOL,
                orderId=int(order["orderId"]),
            )

        opened = client.place_futures_order(
            FUTURES_SYMBOL,
            side="BUY",
            type_="MARKET",
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert isinstance(opened, dict)
        amount = _wait_for_position(client, open_=True)
        assert amount > 0

        assert isinstance(
            client.modify_futures_position_margin(
                FUTURES_SYMBOL,
                amount="0.1",
                type_=1,
            ),
            dict,
        )
        assert isinstance(
            client.modify_futures_position_margin(
                FUTURES_SYMBOL,
                amount="0.1",
                type_=2,
            ),
            dict,
        )

        closed = client.place_futures_order(
            FUTURES_SYMBOL,
            side="SELL",
            type_="MARKET",
            quantity=format(amount, "f"),
            reduceOnly=True,
            newOrderRespType="RESULT",
        )
        assert isinstance(closed, dict)
        assert _wait_for_position(client, open_=False) == 0
        assert client.get_futures_all_orders(FUTURES_SYMBOL, limit=20)
        assert client.get_futures_user_trades(FUTURES_SYMBOL, limit=20)
    finally:
        _cleanup_futures(client)
        _restore_futures_settings(
            client,
            dual=original_dual,
            multi_assets=original_multi_assets,
            margin_type=original_margin_type,
        )


def test_futures_strategy_documented_payloads(client):
    _cleanup_account(client)

    quantity, price, _, _ = _futures_order_params(client)
    sell_price = _futures_safe_sell_price(client)
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
        client.place_futures_strategy_order(
            clientStrategyId=client_strategy_id,
            strategyType="OTO",
            subOrderList=[first_order, second_order],
        )
    assert place_error.value.status_code == 400
    assert place_error.value.request == "<redacted>"

    update_order = dict(first_order)
    update_order.update(firstDrivenId=0, secondDrivenId=0)
    updated = client.update_futures_strategy_order(
        strategyId="0",
        strategyType="OTO",
        subOrderList=[update_order],
    )
    assert isinstance(updated, list)
    assert updated[0]["updateStatus"] == "FAIL"
    assert int(updated[0]["failureCode"]) == -4124
