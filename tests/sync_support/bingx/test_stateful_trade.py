# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.bingx.client import Client

load_dotenv()

BINGX_API_KEY = os.getenv("BINGX_API_KEY")
BINGX_API_SECRET = os.getenv("BINGX_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
SWAP_SYMBOL = "BTC-USDT-SWAP"
FUND_ACCOUNT = "fund"
SPOT_ACCOUNT = "spot"
SWAP_ACCOUNT = "USDTMPerp"


@pytest.fixture
def client():
    return Client(
        api_key=BINGX_API_KEY,
        api_secret=BINGX_API_SECRET,
    )


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


def _swap_available_usdt(client: Client) -> Decimal:
    data = client.get_swap_account_balance().get("data", [])
    if isinstance(data, list):
        for item in data:
            if item.get("asset") == "USDT":
                return _dec(item.get("availableMargin"))
        return Decimal("0")
    balance = data.get("balance", {}) if isinstance(data, dict) else {}
    return _dec(balance.get("availableMargin"))


def _spot_available(client: Client, asset: str) -> Decimal:
    balances = client.get_spot_account_balance().get("data", {}).get("balances", [])
    for item in balances:
        if item.get("asset") == asset:
            return _dec(item.get("free"))
    return Decimal("0")


def _fund_available(client: Client, asset: str) -> Decimal:
    balances = client.get_fund_account_balance(asset=asset).get("data", {}).get("balances", [])
    for item in balances:
        if item.get("asset") == asset:
            return _dec(item.get("free"))
    return Decimal("0")


def _transferable(client: Client, from_account: str, to_account: str, asset: str) -> Decimal:
    data = client.get_transferable_coins(
        fromAccount=from_account,
        toAccount=to_account,
    ).get("data", {})
    for item in data.get("coins", []):
        if item.get("asset") == asset:
            return _dec(item.get("availableTransferAmount", item.get("amount")))
    return Decimal("0")


def _swap_open_orders(client: Client) -> list[dict]:
    data = client.get_open_orders(product_symbol=SWAP_SYMBOL).get("data", {})
    orders = data.get("orders", []) if isinstance(data, dict) else []
    return orders if isinstance(orders, list) else []


def _spot_open_orders(client: Client) -> list[dict]:
    data = client.get_spot_open_orders(product_symbol=SPOT_SYMBOL).get("data", {})
    orders = data.get("orders", []) if isinstance(data, dict) else []
    return orders if isinstance(orders, list) else []


def _positions(client: Client) -> list[dict]:
    data = client.get_open_positions(product_symbol=SWAP_SYMBOL).get("data", [])
    return data if isinstance(data, list) else []


def _skip_if_swap_state(client: Client) -> None:
    if _swap_open_orders(client):
        pytest.skip("BTC-USDT swap already has open orders; not touching unrelated orders.")
    if _positions(client):
        pytest.skip("BTC-USDT swap already has a position; not changing exposure.")


def _skip_if_spot_state(client: Client) -> None:
    if _spot_open_orders(client):
        pytest.skip("BTC-USDT spot already has open orders; not touching unrelated orders.")


def _swap_order_params(client: Client) -> tuple[str, str]:
    details = client.ptm.get_trading_details("bingx", SWAP_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    step = _dec(details["size_precision"], "0.0001")
    min_size = _dec(details["min_size"], "0.0001")
    min_notional = max(_dec(details["min_notional"], "2"), Decimal("2"))
    current_price = _dec(client.get_ticker(product_symbol=SWAP_SYMBOL)["data"]["lastPrice"])
    price = _round_to_step(current_price * Decimal("0.50"), tick, ROUND_DOWN)
    quantity = _round_to_step(min_notional * Decimal("1.25") / price, step, ROUND_UP)
    return _fmt(max(quantity, min_size)), _fmt(price)


def _spot_order_params(client: Client) -> tuple[str, str]:
    details = client.ptm.get_trading_details("bingx", SPOT_SYMBOL)
    tick = _dec(details["price_precision"], "0.01")
    step = _dec(details["size_precision"], "0.000001")
    min_size = _dec(details["min_size"], "0.000001")
    min_notional = max(_dec(details["min_notional"], "0.5"), Decimal("0.5"))
    best_bid = _dec(
        client.get_spot_orderbook(product_symbol=SPOT_SYMBOL, limit=5)["data"]["bids"][0][0]
    )
    price = _round_to_step(best_bid * Decimal("0.50"), tick, ROUND_DOWN)
    quantity = _round_to_step(min_notional * Decimal("1.25") / price, step, ROUND_UP)
    return _fmt(max(quantity, min_size)), _fmt(price)


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("bingx", SPOT_SYMBOL)
    return (
        _dec(details["price_precision"], "0.01"),
        _dec(details["size_precision"], "0.000001"),
        max(_dec(details["min_notional"], "0.5"), Decimal("0.5")),
    )


def _spot_market_quote_amount(client: Client) -> Decimal:
    _, _, min_notional = _spot_details(client)
    return max(min_notional * Decimal("2"), Decimal("2"))


def _spot_fillable_limit_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_notional = _spot_details(client)
    best_ask = _dec(
        client.get_spot_orderbook(product_symbol=SPOT_SYMBOL, limit=5)["data"]["asks"][0][0]
    )
    price = _round_to_step(best_ask * Decimal("1.02"), tick, ROUND_UP)
    quantity = _round_to_step(_spot_market_quote_amount(client) / price, step, ROUND_UP)
    return _fmt(quantity), _fmt(price)


def _spot_fillable_limit_sell_price(client: Client) -> str:
    tick, _, _ = _spot_details(client)
    best_bid = _dec(
        client.get_spot_orderbook(product_symbol=SPOT_SYMBOL, limit=5)["data"]["bids"][0][0]
    )
    return _fmt(_round_to_step(best_bid * Decimal("0.98"), tick, ROUND_DOWN))


def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _ = _spot_details(client)
    best_ask = _dec(
        client.get_spot_orderbook(product_symbol=SPOT_SYMBOL, limit=5)["data"]["asks"][0][0]
    )
    return _fmt(_round_to_step(best_ask * Decimal("1.50"), tick, ROUND_UP))


def _spot_trade_delta(client: Client, before: Decimal, asset: str) -> Decimal:
    return max(_spot_available(client, asset) - before, Decimal("0"))


def _spot_market_buy_delta(client: Client, quote_amount: Decimal) -> Decimal:
    before_btc = _spot_available(client, "BTC")
    assert (
        client.place_spot_market_buy_order(
            product_symbol=SPOT_SYMBOL,
            quoteOrderQty=_fmt(quote_amount),
            clientOrderId=f"dcex{uuid.uuid4().hex[:16]}",
        )
        is not None
    )
    time.sleep(2)
    return _spot_trade_delta(client, before_btc, "BTC")


def _spot_sell_quantity(client: Client, quantity: Decimal) -> str:
    _, step, _ = _spot_details(client)
    return _fmt(_round_to_step(quantity, step, ROUND_DOWN))


def _swap_current_price(client: Client) -> Decimal:
    return _dec(client.get_ticker(product_symbol=SWAP_SYMBOL)["data"]["lastPrice"])


def _ensure_swap_usdt_for_quantity(client: Client, quantity: str) -> None:
    current_price = _swap_current_price(client)
    required = Decimal(quantity) * current_price / Decimal("10") * Decimal("1.50")
    _ensure_usdt_for_account(
        client=client,
        to_account=SWAP_ACCOUNT,
        required=required,
        current_available=_swap_available_usdt(client),
    )
    if _swap_available_usdt(client) < required:
        pytest.skip("BingX swap USDT remains insufficient after fund transfer.")


def _swap_fillable_limit_buy_price(client: Client) -> float:
    tick = _dec(client.ptm.get_trading_details("bingx", SWAP_SYMBOL)["price_precision"], "0.1")
    price = _round_to_step(_swap_current_price(client) * Decimal("1.02"), tick, ROUND_UP)
    return float(_fmt(price))


def _swap_fillable_limit_sell_price(client: Client) -> float:
    tick = _dec(client.ptm.get_trading_details("bingx", SWAP_SYMBOL)["price_precision"], "0.1")
    price = _round_to_step(_swap_current_price(client) * Decimal("0.98"), tick, ROUND_DOWN)
    return float(_fmt(price))


def _position_id(client: Client, side: str) -> str | None:
    for position in _positions(client):
        if position.get("positionSide") == side and _dec(
            position.get("positionAmt", position.get("positionAmount", "0"))
        ) != Decimal("0"):
            position_id = position.get("positionId")
            return str(position_id) if position_id is not None else None
    return None


def _wait_for_position(client: Client, side: str) -> str | None:
    for _ in range(5):
        position_id = _position_id(client, side)
        if position_id is not None:
            return position_id
        time.sleep(1)
    return None


def _ensure_usdt_for_account(
    client: Client,
    to_account: str,
    required: Decimal,
    current_available: Decimal,
) -> None:
    if current_available >= required:
        return

    transferable = _transferable(client, FUND_ACCOUNT, to_account, "USDT")
    fund_available = _fund_available(client, "USDT")
    source_available = min(transferable, fund_available) if fund_available > 0 else transferable
    amount = max(required - current_available + Decimal("0.5"), Decimal("1"))
    if source_available < amount:
        pytest.skip(f"Insufficient BingX fund USDT to transfer into {to_account}.")

    client.asset_transfer(
        fromAccount=FUND_ACCOUNT,
        toAccount=to_account,
        asset="USDT",
        amount=_fmt(amount),
    )
    time.sleep(2)


def _ensure_swap_usdt(client: Client, quantity: str, price: str) -> None:
    required = Decimal(quantity) * Decimal(price) / Decimal("10") * Decimal("1.25")
    _ensure_usdt_for_account(
        client=client,
        to_account=SWAP_ACCOUNT,
        required=required,
        current_available=_swap_available_usdt(client),
    )
    if _swap_available_usdt(client) < required:
        pytest.skip("BingX swap USDT remains insufficient after fund transfer.")


def _ensure_spot_usdt(client: Client, quantity: str, price: str) -> None:
    required = Decimal(quantity) * Decimal(price)
    _ensure_usdt_for_account(
        client=client,
        to_account=SPOT_ACCOUNT,
        required=required,
        current_available=_spot_available(client, "USDT"),
    )
    if _spot_available(client, "USDT") < required:
        pytest.skip("BingX spot USDT remains insufficient after fund transfer.")


@pytest.mark.private
def test_swap_margin_leverage_and_position_mode_idempotent(client):
    _skip_if_swap_state(client)
    margin = client.get_margin_type(product_symbol=SWAP_SYMBOL)["data"]["marginType"]
    assert client.change_margin_type(product_symbol=SWAP_SYMBOL, marginType=margin) is not None

    leverage = client.get_leverage(product_symbol=SWAP_SYMBOL)["data"]
    assert (
        client.set_leverage(
            product_symbol=SWAP_SYMBOL,
            side="LONG",
            leverage=int(leverage["longLeverage"]),
        )
        is not None
    )
    assert (
        client.set_leverage(
            product_symbol=SWAP_SYMBOL,
            side="SHORT",
            leverage=int(leverage["shortLeverage"]),
        )
        is not None
    )

    mode = client.get_position_mode()["data"]["dualSidePosition"]
    assert client.set_position_mode(dualSidePosition=mode) is not None


@pytest.mark.private
def test_swap_close_all_positions_when_flat(client):
    _skip_if_swap_state(client)
    assert client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None


@pytest.mark.private
def test_swap_post_only_order_lifecycle(client):
    _skip_if_swap_state(client)
    quantity, price = _swap_order_params(client)
    _ensure_swap_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_swap_post_only_buy_order(
            product_symbol=SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            clientOrderId=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["order"]["orderId"]
        assert client.get_order_detail(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
    finally:
        if order_id is not None:
            client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_swap_batch_order_and_cancel_batch(client):
    _skip_if_swap_state(client)
    quantity, price = _swap_order_params(client)
    _ensure_swap_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_swap_batch_order(
            [
                {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "positionSide": "LONG",
                    "quantity": quantity,
                    "price": price,
                    "timeInForce": "PostOnly",
                    "clientOrderId": f"dcex-{uuid.uuid4().hex}",
                }
            ]
        )
        orders = order.get("data", {}).get("orders", [])
        if orders:
            order_id = orders[0]["orderId"]
            assert (
                client.cancel_swap_batch_order(
                    product_symbol=SWAP_SYMBOL,
                    orderIdList=[order_id],
                )
                is not None
            )
            order_id = None
    finally:
        if order_id is not None:
            client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_swap_cancel_all_orders(client):
    _skip_if_swap_state(client)
    quantity, price = _swap_order_params(client)
    _ensure_swap_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_swap_post_only_buy_order(
            product_symbol=SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            clientOrderId=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["order"]["orderId"]
        assert client.cancel_swap_all_orders(product_symbol=SWAP_SYMBOL) is not None
        order_id = None
        time.sleep(1)
        assert not _swap_open_orders(client)
    finally:
        if order_id is not None:
            client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_swap_replace_order(client):
    _skip_if_swap_state(client)
    quantity, price = _swap_order_params(client)
    _ensure_swap_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_swap_post_only_buy_order(
            product_symbol=SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(price),
            positionSide="LONG",
            clientOrderId=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["order"]["orderId"]
        new_price = _fmt(Decimal(price) * Decimal("0.99"))
        assert (
            client.replace_swap_order(
                product_symbol=SWAP_SYMBOL,
                orderId=str(order_id),
                cancelReplaceMode="STOP_ON_FAILURE",
                type_="LIMIT",
                side="BUY",
                positionSide="LONG",
                quantity=float(quantity),
                price=float(new_price),
                timeInForce="PostOnly",
            )
            is not None
        )
        order_id = None
        client.cancel_swap_all_orders(product_symbol=SWAP_SYMBOL)
    finally:
        if order_id is not None:
            client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_swap_market_buy_and_close_position(client):
    _skip_if_swap_state(client)
    quantity, _ = _swap_order_params(client)
    _ensure_swap_usdt_for_quantity(client, quantity)

    try:
        assert (
            client.place_swap_market_buy_order(
                product_symbol=SWAP_SYMBOL,
                quantity=float(quantity),
                positionSide="LONG",
                clientOrderId=f"dcex-{uuid.uuid4().hex}",
            )
            is not None
        )
        position_id = _wait_for_position(client, "LONG")
        assert position_id is not None
        assert client.close_swap_position(positionId=position_id) is not None
        time.sleep(2)
        assert not _positions(client)
    finally:
        if _positions(client):
            client.close_swap_all_positions(product_symbol=SWAP_SYMBOL)


@pytest.mark.private
def test_swap_market_sell_and_close_all_positions(client):
    _skip_if_swap_state(client)
    quantity, _ = _swap_order_params(client)
    _ensure_swap_usdt_for_quantity(client, quantity)

    try:
        assert (
            client.place_swap_market_sell_order(
                product_symbol=SWAP_SYMBOL,
                quantity=float(quantity),
                positionSide="SHORT",
                clientOrderId=f"dcex-{uuid.uuid4().hex}",
            )
            is not None
        )
        assert _wait_for_position(client, "SHORT") is not None
        assert client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None
        time.sleep(2)
        assert not _positions(client)
    finally:
        if _positions(client):
            client.close_swap_all_positions(product_symbol=SWAP_SYMBOL)


@pytest.mark.private
def test_swap_fillable_limit_buy_and_sell(client):
    _skip_if_swap_state(client)
    quantity, _ = _swap_order_params(client)
    _ensure_swap_usdt_for_quantity(client, quantity)

    try:
        assert (
            client.place_swap_limit_buy_order(
                product_symbol=SWAP_SYMBOL,
                quantity=float(quantity),
                price=_swap_fillable_limit_buy_price(client),
                positionSide="LONG",
                timeInForce="GTC",
                clientOrderId=f"dcex-{uuid.uuid4().hex}",
            )
            is not None
        )
        assert _wait_for_position(client, "LONG") is not None
        assert client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None
        time.sleep(2)
        assert not _positions(client)

        assert (
            client.place_swap_limit_sell_order(
                product_symbol=SWAP_SYMBOL,
                quantity=float(quantity),
                price=_swap_fillable_limit_sell_price(client),
                positionSide="SHORT",
                timeInForce="GTC",
                clientOrderId=f"dcex-{uuid.uuid4().hex}",
            )
            is not None
        )
        assert _wait_for_position(client, "SHORT") is not None
        assert client.close_swap_all_positions(product_symbol=SWAP_SYMBOL) is not None
        time.sleep(2)
        assert not _positions(client)
    finally:
        if _swap_open_orders(client):
            client.cancel_swap_all_orders(product_symbol=SWAP_SYMBOL)
        if _positions(client):
            client.close_swap_all_positions(product_symbol=SWAP_SYMBOL)


@pytest.mark.private
def test_swap_post_only_sell_order_lifecycle(client):
    _skip_if_swap_state(client)
    quantity, _ = _swap_order_params(client)
    _ensure_swap_usdt_for_quantity(client, quantity)
    tick = _dec(client.ptm.get_trading_details("bingx", SWAP_SYMBOL)["price_precision"], "0.1")
    price = _fmt(_round_to_step(_swap_current_price(client) * Decimal("1.50"), tick, ROUND_UP))
    order_id = None
    try:
        order = client.place_swap_post_only_sell_order(
            product_symbol=SWAP_SYMBOL,
            quantity=float(quantity),
            price=float(price),
            positionSide="SHORT",
            clientOrderId=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["order"]["orderId"]
        assert client.get_order_detail(product_symbol=SWAP_SYMBOL, orderId=order_id) is not None
    finally:
        if order_id is not None:
            client.cancel_swap_order(product_symbol=SWAP_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_spot_post_only_order_lifecycle(client):
    _skip_if_spot_state(client)
    quantity, price = _spot_order_params(client)
    _ensure_spot_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_spot_post_only_buy_order(
            product_symbol=SPOT_SYMBOL,
            quantity=quantity,
            price=price,
            clientOrderId=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["orderId"]
        assert client.get_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id) is not None
    finally:
        if order_id is not None:
            client.cancel_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_spot_market_buy_and_sell(client):
    _skip_if_spot_state(client)
    quote_amount = _spot_market_quote_amount(client)
    _ensure_spot_usdt(client, "1", _fmt(quote_amount))
    before_btc = _spot_available(client, "BTC")

    try:
        bought = _spot_market_buy_delta(client, quote_amount)
        sell_quantity = _spot_sell_quantity(client, bought)
        assert Decimal(sell_quantity) > 0
        assert (
            client.place_spot_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=sell_quantity,
                clientOrderId=f"dcex{uuid.uuid4().hex[:16]}",
            )
            is not None
        )
        time.sleep(2)
    finally:
        remaining = _spot_sell_quantity(client, _spot_trade_delta(client, before_btc, "BTC"))
        if Decimal(remaining) > 0:
            client.place_spot_market_sell_order(product_symbol=SPOT_SYMBOL, quantity=remaining)


@pytest.mark.private
def test_spot_fillable_limit_buy_and_sell(client):
    _skip_if_spot_state(client)
    quantity, price = _spot_fillable_limit_buy_params(client)
    _ensure_spot_usdt(client, quantity, price)
    before_btc = _spot_available(client, "BTC")

    try:
        assert (
            client.place_spot_limit_buy_order(
                product_symbol=SPOT_SYMBOL,
                quantity=quantity,
                price=price,
                timeInForce="GTC",
                clientOrderId=f"dcex{uuid.uuid4().hex[:16]}",
            )
            is not None
        )
        time.sleep(2)
        bought = _spot_trade_delta(client, before_btc, "BTC")
        sell_quantity = _spot_sell_quantity(client, bought)
        assert Decimal(sell_quantity) > 0
        assert (
            client.place_spot_limit_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=sell_quantity,
                price=_spot_fillable_limit_sell_price(client),
                timeInForce="GTC",
                clientOrderId=f"dcex{uuid.uuid4().hex[:16]}",
            )
            is not None
        )
    finally:
        if _spot_open_orders(client):
            client.cancel_spot_open_orders(product_symbol=SPOT_SYMBOL)
        remaining = _spot_trade_delta(client, before_btc, "BTC")
        sell_quantity = _spot_sell_quantity(client, remaining)
        if Decimal(sell_quantity) > 0:
            client.place_spot_market_sell_order(product_symbol=SPOT_SYMBOL, quantity=sell_quantity)


@pytest.mark.private
def test_spot_post_only_sell_order_lifecycle(client):
    _skip_if_spot_state(client)
    quote_amount = _spot_market_quote_amount(client)
    _ensure_spot_usdt(client, "1", _fmt(quote_amount))
    before_btc = _spot_available(client, "BTC")
    order_id = None

    try:
        bought = _spot_market_buy_delta(client, quote_amount)
        sell_quantity = _spot_sell_quantity(client, bought)
        assert Decimal(sell_quantity) > 0
        order = client.place_spot_post_only_sell_order(
            product_symbol=SPOT_SYMBOL,
            quantity=sell_quantity,
            price=_spot_post_only_sell_price(client),
            clientOrderId=f"dcex{uuid.uuid4().hex[:16]}",
        )
        order_id = order["data"]["orderId"]
        assert client.get_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id) is not None
    finally:
        if order_id is not None:
            client.cancel_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id)
        remaining = _spot_trade_delta(client, before_btc, "BTC")
        sell_quantity = _spot_sell_quantity(client, remaining)
        if Decimal(sell_quantity) > 0:
            client.place_spot_market_sell_order(product_symbol=SPOT_SYMBOL, quantity=sell_quantity)


@pytest.mark.private
def test_spot_batch_order_and_cancel_batch(client):
    _skip_if_spot_state(client)
    quantity, price = _spot_order_params(client)
    _ensure_spot_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_spot_batch_order(
            [
                {
                    "symbol": "BTC-USDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": quantity,
                    "price": price,
                    "timeInForce": "POC",
                    "newClientOrderId": f"dcex{uuid.uuid4().hex[:16]}",
                }
            ]
        )
        orders = order.get("data", {}).get("orders", [])
        if orders:
            order_id = orders[0]["orderId"]
            assert (
                client.cancel_spot_batch_orders(
                    product_symbol=SPOT_SYMBOL,
                    orderIds=[order_id],
                )
                is not None
            )
            order_id = None
    finally:
        if order_id is not None:
            client.cancel_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id)


@pytest.mark.private
def test_spot_cancel_all_orders(client):
    _skip_if_spot_state(client)
    quantity, price = _spot_order_params(client)
    _ensure_spot_usdt(client, quantity, price)
    order_id = None
    try:
        order = client.place_spot_post_only_buy_order(
            product_symbol=SPOT_SYMBOL,
            quantity=quantity,
            price=price,
            clientOrderId=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["orderId"]
        assert client.cancel_spot_open_orders(product_symbol=SPOT_SYMBOL) is not None
        order_id = None
        time.sleep(1)
        assert not _spot_open_orders(client)
    finally:
        if order_id is not None:
            client.cancel_spot_order(product_symbol=SPOT_SYMBOL, orderId=order_id)
