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
FUTURES_SYMBOL = "ASTERUSDT"
SPOT_TRANSFER_AMOUNT = Decimal("5.1")
SPOT_USDT_BUFFER = Decimal("0.02")
SPOT_ORDER_QUANTITY = "5"
SPOT_BUY_QUOTE = "5.01"

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
        yield client_instance
    finally:
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


def _market_info(client: Client) -> tuple[Decimal, Decimal]:
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
    return _dec(filters["PRICE_FILTER"]["tickSize"]), _dec(filters["MIN_NOTIONAL"]["minNotional"])


def _safe_sell_price(client: Client) -> str:
    tick, _ = _market_info(client)
    book = client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    value = (ask * Decimal("1.05") / tick).to_integral_value(rounding=ROUND_UP) * tick
    return format(value, "f")


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
    quantity = ((min_notional * Decimal("1.10") / bid) / step).to_integral_value(
        rounding=ROUND_UP
    ) * step

    def price(multiplier: str) -> str:
        value = (bid * Decimal(multiplier) / tick).to_integral_value(rounding=ROUND_DOWN) * tick
        return format(value, "f")

    return format(quantity, "f"), price("0.95"), price("0.94"), price("0.93")


def _futures_safe_sell_price(client: Client) -> str:
    tick, _, _ = _futures_market_info(client)
    book = client.get_futures_orderbook(FUTURES_SYMBOL, limit=5)
    assert isinstance(book, dict)
    ask = _dec(book["asks"][0][0])
    value = (ask * Decimal("1.05") / tick).to_integral_value(rounding=ROUND_UP) * tick
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


def _return_test_funds(
    client: Client,
    initial_balances: dict[str, Decimal],
) -> None:
    with suppress(Exception):
        client.cancel_all_spot_open_orders(SPOT_SYMBOL)
    current = _spot_balances(client)
    for asset in ("USDC", "USDT"):
        delta = current.get(asset, Decimal("0")) - initial_balances.get(asset, Decimal("0"))
        if delta > 0:
            _transfer(
                client,
                amount=delta,
                asset=asset,
                kind_type="SPOT_FUTURE",
                market="spot",
            )


def test_spot_order_and_transfer_lifecycle(client):
    if client.get_spot_open_orders(SPOT_SYMBOL):
        pytest.skip(f"Aster already has {SPOT_SYMBOL} open orders.")
    if _futures_balance(client, "USDC") < SPOT_TRANSFER_AMOUNT:
        pytest.skip("Aster futures wallet requires at least 5.1 USDC.")
    if _futures_balance(client, "USDT") < SPOT_USDT_BUFFER:
        pytest.skip("Aster futures wallet requires at least 0.02 USDT.")

    initial_balances = _spot_balances(client)
    try:
        _transfer(
            client,
            amount=SPOT_TRANSFER_AMOUNT,
            asset="USDC",
            kind_type="FUTURE_SPOT",
            market="futures",
        )
        _transfer(
            client,
            amount=SPOT_USDT_BUFFER,
            asset="USDT",
            kind_type="FUTURE_SPOT",
            market="futures",
        )
        time.sleep(2)

        price = _safe_sell_price(client)
        first_id = _order_id(
            client.place_spot_order(
                SPOT_SYMBOL,
                side="SELL",
                type_="LIMIT",
                quantity=SPOT_ORDER_QUANTITY,
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
                quantity=SPOT_ORDER_QUANTITY,
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
                quantity=SPOT_ORDER_QUANTITY,
            ),
            dict,
        )
        time.sleep(2)
        gained_usdt = _spot_balances(client).get("USDT", Decimal("0")) - initial_balances.get(
            "USDT", Decimal("0")
        )
        assert gained_usdt >= Decimal(SPOT_BUY_QUOTE)

        assert isinstance(
            client.place_spot_order(
                SPOT_SYMBOL,
                side="BUY",
                type_="MARKET",
                quoteOrderQty=SPOT_BUY_QUOTE,
            ),
            dict,
        )
        time.sleep(2)

        assert client.get_spot_all_orders(SPOT_SYMBOL, limit=20)
        assert client.get_spot_user_trades(SPOT_SYMBOL, limit=20)
    finally:
        _return_test_funds(client, initial_balances)


def test_futures_order_lifecycle(client):
    if client.get_futures_open_orders(FUTURES_SYMBOL):
        pytest.skip(f"Aster already has {FUTURES_SYMBOL} open orders.")
    if _futures_position_amount(client) != 0:
        pytest.skip(f"Aster already has a {FUTURES_SYMBOL} position.")

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
    if client.get_futures_open_orders(FUTURES_SYMBOL):
        pytest.skip(f"Aster already has {FUTURES_SYMBOL} open orders.")
    if _futures_position_amount(client) != 0:
        pytest.skip(f"Aster already has a {FUTURES_SYMBOL} position.")

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
    assert "/fapi/v3/placeStrategyOrder" in place_error.value.request

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
