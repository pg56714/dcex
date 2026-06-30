# ruff: noqa: ANN001, ANN201, D100, D103

import json
import os
import time
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.bitmex.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BITMEX_API_KEY = os.getenv("BITMEX_API_KEY")
BITMEX_API_SECRET = os.getenv("BITMEX_API_SECRET")
SYMBOL = "XBT-USDT-SWAP"
EXCHANGE_SYMBOL = "XBTUSDT"
ORDER_QTY = 100
MARGIN_UNIT = Decimal("1000000")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real BitMEX order tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        api_key=BITMEX_API_KEY,
        api_secret=BITMEX_API_SECRET,
        timeout=20,
    )
    _cleanup(client_instance)
    try:
        yield client_instance
    finally:
        _cleanup(client_instance)


def _dec(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _client_id() -> str:
    return f"dcx{uuid.uuid4().hex[:16]}"


def _filter(**kwargs: object) -> str:
    return json.dumps(kwargs, separators=(",", ":"))


def _position(client: Client) -> dict:
    for item in client.get_positions():
        if isinstance(item, dict) and item.get("symbol") == EXCHANGE_SYMBOL:
            return item
    return {}


def _position_qty(client: Client) -> int:
    return int(_dec(_position(client).get("currentQty")))


def _open_orders(client: Client) -> list[dict]:
    try:
        orders = client.get_order(
            product_symbol=SYMBOL,
            filter=_filter(open=True),
            count=100,
            reverse=True,
        )
    except FailedRequestError as exc:
        if "failed to decode response" in str(exc):
            pytest.fail(f"BitMEX open-order endpoint returned an empty response: {exc}")
        raise
    return [item for item in orders if isinstance(item, dict)]


def _best_prices(client: Client) -> tuple[Decimal, Decimal]:
    bids: list[Decimal] = []
    asks: list[Decimal] = []
    for level in client.get_orderbook(product_symbol=SYMBOL, depth=10):
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


def _tick_size(client: Client) -> Decimal:
    data = client.get_instrument_info(product_symbol=SYMBOL)
    if not data:
        return Decimal("0.1")
    return _dec(data[0].get("tickSize"), "0.1")


def _order_qty(client: Client) -> int:
    data = client.get_instrument_info(product_symbol=SYMBOL)
    if not data:
        return ORDER_QTY
    lot_size = _dec(data[0].get("lotSize"), str(ORDER_QTY))
    return int(max(lot_size, Decimal("1")))


def _round_to_tick(value: Decimal, tick: Decimal, rounding: str) -> Decimal:
    return (value / tick).to_integral_value(rounding=rounding) * tick


def _post_only_buy_price(client: Client) -> float:
    best_bid, _ = _best_prices(client)
    tick = _tick_size(client)
    return float(_round_to_tick(best_bid - tick, tick, ROUND_DOWN))


def _post_only_sell_price(client: Client) -> float:
    _, best_ask = _best_prices(client)
    tick = _tick_size(client)
    return float(_round_to_tick(best_ask + tick, tick, ROUND_UP))


def _fillable_buy_price(client: Client) -> float:
    _, best_ask = _best_prices(client)
    tick = _tick_size(client)
    price = max(best_ask + tick, best_ask * Decimal("1.002"))
    return float(_round_to_tick(price, tick, ROUND_UP))


def _fillable_sell_price(client: Client) -> float:
    best_bid, _ = _best_prices(client)
    tick = _tick_size(client)
    price = min(best_bid - tick, best_bid * Decimal("0.998"))
    return float(_round_to_tick(price, tick, ROUND_DOWN))


def _available_margin(client: Client) -> Decimal:
    for item in client.get_margin():
        if isinstance(item, dict) and item.get("currency") == "USDt":
            return _dec(item.get("availableMargin"))
    return Decimal("0")


def _ensure_margin(client: Client) -> None:
    leverage = max(_dec(_position(client).get("leverage"), "1"), Decimal("1"))
    required_margin = Decimal(_order_qty(client)) / leverage * MARGIN_UNIT * Decimal("1.05")
    if _available_margin(client) < required_margin:
        pytest.fail("Insufficient BitMEX available margin for stateful order test.")


def _wait_for_position(client: Client, sign: int) -> int:
    for _ in range(10):
        qty = _position_qty(client)
        if sign > 0 and qty > 0:
            return qty
        if sign < 0 and qty < 0:
            return qty
        time.sleep(1)
    return 0


def _wait_for_position_or_skip(client: Client, sign: int, action: str) -> int:
    qty = _wait_for_position(client, sign)
    if qty == 0:
        pytest.fail(f"BitMEX {action} did not fill before timeout.")
    return qty


def _wait_until_flat(client: Client) -> None:
    for _ in range(10):
        if _position_qty(client) == 0:
            return
        time.sleep(1)
    assert _position_qty(client) == 0


def _close_position(client: Client) -> None:
    qty = _position_qty(client)
    if qty > 0:
        client.place_order(
            SYMBOL,
            side="Sell",
            orderQty=abs(qty),
            ordType="Market",
            execInst="ReduceOnly",
            clOrdID=_client_id(),
        )
    elif qty < 0:
        client.place_order(
            SYMBOL,
            side="Buy",
            orderQty=abs(qty),
            ordType="Market",
            execInst="ReduceOnly",
            clOrdID=_client_id(),
        )
    time.sleep(2)
    _wait_until_flat(client)


def _cleanup(client: Client) -> None:
    if _open_orders(client):
        client.cancel_all_orders(product_symbol=SYMBOL, text="dcex cleanup")
        time.sleep(1)
    _close_position(client)
    assert not _open_orders(client)
    assert _position_qty(client) == 0


def _assert_order_visible(client: Client, order_id: str) -> None:
    for _ in range(5):
        if any(order.get("orderID") == order_id for order in _open_orders(client)):
            return
        orders = client.get_order(
            product_symbol=SYMBOL,
            filter=_filter(orderID=order_id),
            count=1,
            reverse=True,
        )
        if any(isinstance(order, dict) and order.get("orderID") == order_id for order in orders):
            return
        time.sleep(1)
    pytest.fail(f"BitMEX order {order_id} was not visible before live assertion.")


def _is_invalid_order_id(exc: FailedRequestError) -> bool:
    return "invalid orderid" in str(exc).lower()


def _amend_order_or_skip(client: Client, order_id: str, price: float) -> dict:
    try:
        return client.amend_order(orderID=order_id, price=price)
    except FailedRequestError as exc:
        if _is_invalid_order_id(exc):
            pytest.fail(f"BitMEX order {order_id} was no longer amendable: {exc}")
        raise


def _cancel_order_if_present(client: Client, order_id: str, text: str | None = None) -> object:
    try:
        if text is None:
            return client.cancel_order(orderID=order_id)
        return client.cancel_order(orderID=order_id, text=text)
    except FailedRequestError as exc:
        if _is_invalid_order_id(exc):
            return {}
        raise


def test_stateful_order_lifecycle(client):
    _cleanup(client)
    _ensure_margin(client)
    qty = _order_qty(client)

    try:
        order_id = None
        try:
            price = _post_only_buy_price(client)
            order = client.place_order(
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
            _assert_order_visible(client, order_id)
            assert _amend_order_or_skip(client, order_id, price - 1.0) is not None
            assert (
                _cancel_order_if_present(
                    client,
                    order_id,
                    text="dcex stateful cancel",
                )
                is not None
            )
            order_id = None
        finally:
            if order_id is not None:
                _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = client.place_limit_order(
                SYMBOL,
                side="Buy",
                orderQty=qty,
                price=_post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert (
                client.cancel_all_orders(product_symbol=SYMBOL, text="dcex cancel all") is not None
            )
            order_id = None
            time.sleep(1)
        finally:
            if order_id is not None:
                _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = client.place_post_only_order(
                SYMBOL,
                side="Buy",
                orderQty=qty,
                price=_post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert _cancel_order_if_present(client, order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = client.place_post_only_buy_order(
                SYMBOL,
                orderQty=qty,
                price=_post_only_buy_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert _cancel_order_if_present(client, order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                _cancel_order_if_present(client, order_id)

        order_id = None
        try:
            order = client.place_post_only_sell_order(
                SYMBOL,
                orderQty=qty,
                price=_post_only_sell_price(client),
                clOrdID=_client_id(),
            )
            order_id = order["orderID"]
            assert _cancel_order_if_present(client, order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                _cancel_order_if_present(client, order_id)

        assert client.place_market_buy_order(SYMBOL, qty, clOrdID=_client_id()) is not None
        assert _wait_for_position(client, sign=1) > 0
        _close_position(client)

        assert client.place_market_sell_order(SYMBOL, qty, clOrdID=_client_id()) is not None
        assert _wait_for_position(client, sign=-1) < 0
        _close_position(client)

        assert client.place_market_order(SYMBOL, "Buy", qty, clOrdID=_client_id()) is not None
        assert _wait_for_position(client, sign=1) > 0
        _close_position(client)

        assert (
            client.place_limit_buy_order(
                SYMBOL,
                qty,
                _fillable_buy_price(client),
                clOrdID=_client_id(),
            )
            is not None
        )
        assert _wait_for_position_or_skip(client, sign=1, action="limit buy") > 0
        _close_position(client)

        assert (
            client.place_limit_sell_order(
                SYMBOL,
                qty,
                _fillable_sell_price(client),
                clOrdID=_client_id(),
            )
            is not None
        )
        assert _wait_for_position_or_skip(client, sign=-1, action="limit sell") < 0
        _close_position(client)

        assert client.get_order(product_symbol=SYMBOL, count=10, reverse=True) is not None
    finally:
        _cleanup(client)

    assert not _open_orders(client)
    assert _position_qty(client) == 0


@pytest.mark.private
def test_trading_read_endpoints(client):
    assert client.get_executions(product_symbol=SYMBOL, count=5) is not None
    assert client.get_trade_history(product_symbol=SYMBOL, count=5) is not None
    assert client.get_trading_volume() is not None
