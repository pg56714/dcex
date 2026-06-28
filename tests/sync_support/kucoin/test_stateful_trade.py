# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.kucoin.client import Client

load_dotenv()

KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
FUTURES_LEVERAGE = Decimal("20")
TRANSFER_BUFFER_USDT = Decimal("0.1")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real KuCoin order tests.",
    ),
]


@pytest.fixture
def client():
    return Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
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


def _fmt_usdt_transfer(value: Decimal) -> str:
    rounded = value.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
    return format(rounded.normalize(), "f")


def _items(res: dict) -> list[dict]:
    data = res.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]
    return []


def _available(client: Client, currency: str, type_: str) -> Decimal:
    res = client.get_account_balance(currency=currency, type=type_)
    return sum((_dec(item.get("available")) for item in _items(res)), Decimal("0"))


def _futures_available_usdt(client: Client) -> Decimal:
    data = client.get_futures_account(currency="USDT").get("data")
    if not isinstance(data, dict):
        return Decimal("0")
    return _dec(data.get("availableBalance"))


def _transfer_from_main(client: Client, amount: Decimal, to_account_type: str, reason: str) -> None:
    main_available = _available(client, "USDT", "main")
    if main_available < amount:
        pytest.skip(reason)

    client.flex_transfer(
        currency="USDT",
        amount=_fmt_usdt_transfer(amount),
        fromAccountType="MAIN",
        toAccountType=to_account_type,
        clientOid=f"dcex-{uuid.uuid4().hex}",
    )
    time.sleep(2)


def _transfer_amount(required: Decimal, available: Decimal, main_available: Decimal) -> Decimal:
    needed = required - available
    buffered = needed + TRANSFER_BUFFER_USDT
    if main_available >= buffered:
        return buffered
    return needed


def _spot_order_params(client: Client) -> tuple[str, str]:
    details = client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)
    tick = _dec(details["price_precision"], "0.01")
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "1"), Decimal("1"))
    best_bid = _dec(client.get_spot_orderbook(product_symbol=SPOT_SYMBOL)["data"]["bids"][0][0])
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    size = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(size, min_size)), _fmt(price)


def _spot_step_and_min(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "1"), Decimal("1"))
    return step, min_size, min_notional


def _futures_position_size(client: Client) -> Decimal:
    data = client.get_futures_position(product_symbol=FUTURES_SYMBOL).get("data")
    if not isinstance(data, dict):
        return Decimal("0")
    for key in ("currentQty", "size", "posQty", "quantity"):
        if key in data:
            return _dec(data.get(key))
    return Decimal("0")


def _futures_order_params(client: Client) -> tuple[int, str, Decimal, Decimal]:
    contract = client.get_futures_contract(product_symbol=FUTURES_SYMBOL)["data"]
    tick = _dec(contract["tickSize"], "0.1")
    lot = _dec(contract["lotSize"], "1")
    multiplier = _dec(contract["multiplier"], "0.001")
    current_price = _dec(client.get_futures_ticker(product_symbol=FUTURES_SYMBOL)["data"]["price"])
    best_bid = _dec(
        client.get_futures_orderbook(product_symbol=FUTURES_SYMBOL, depth=5)["data"]["bids"][0][0]
    )
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    return int(max(lot, Decimal("1"))), _fmt(price), current_price, multiplier


def _ensure_futures_cross_leverage(client: Client) -> None:
    target_leverage = str(int(FUTURES_LEVERAGE))
    data = client.get_futures_cross_margin_leverage(product_symbol=FUTURES_SYMBOL).get("data")
    if isinstance(data, dict) and str(data.get("leverage")) == target_leverage:
        return
    client.modify_futures_cross_margin_leverage(
        product_symbol=FUTURES_SYMBOL,
        leverage=target_leverage,
    )
    time.sleep(1)


def _skip_if_futures_margin_insufficient(
    client: Client,
    size: int,
    price: str,
    multiplier: Decimal,
    leverage: Decimal = FUTURES_LEVERAGE,
) -> None:
    _ensure_futures_cross_leverage(client)
    required_margin = Decimal(price) * multiplier * Decimal(size) / leverage * Decimal("1.05")
    available = _futures_available_usdt(client)
    if available >= required_margin:
        return

    main_available = _available(client, "USDT", "main")
    transfer_amount = _transfer_amount(required_margin, available, main_available)
    _transfer_from_main(
        client,
        transfer_amount,
        "CONTRACT",
        "Insufficient main USDT to fund KuCoin futures stateful order test.",
    )
    available = _futures_available_usdt(client)
    if available < required_margin:
        pytest.skip("Insufficient futures USDT for KuCoin futures post-only order.")


def _skip_if_spot_open_orders(client: Client) -> None:
    if _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL)):
        pytest.skip("BTC-USDT spot already has open orders; not touching unrelated orders.")


def _wait_until_no_spot_open_orders(client: Client) -> None:
    for _ in range(5):
        if not _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL)):
            return
        time.sleep(1)
    assert not _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL))


def _skip_if_spot_usdt_insufficient(client: Client, size: str, price: str) -> None:
    required = Decimal(size) * Decimal(price)
    available = _available(client, "USDT", "trade")
    if available >= required:
        return

    main_available = _available(client, "USDT", "main")
    transfer_amount = _transfer_amount(required, available, main_available)
    _transfer_from_main(
        client,
        transfer_amount,
        "TRADE",
        "Insufficient main USDT to fund KuCoin spot stateful order test.",
    )
    if _available(client, "USDT", "trade") < required:
        pytest.skip("Insufficient spot trade USDT for KuCoin spot post-only order.")


def _skip_if_spot_funds_insufficient(client: Client, funds: Decimal) -> None:
    available = _available(client, "USDT", "trade")
    if available >= funds:
        return

    main_available = _available(client, "USDT", "main")
    transfer_amount = _transfer_amount(funds, available, main_available)
    _transfer_from_main(
        client,
        transfer_amount,
        "TRADE",
        "Insufficient main USDT to fund KuCoin spot market round-trip.",
    )
    if _available(client, "USDT", "trade") < funds:
        pytest.skip("Insufficient spot trade USDT for KuCoin spot market round-trip.")


def _skip_if_futures_state(client: Client) -> None:
    if _items(client.get_futures_order_list(product_symbol=FUTURES_SYMBOL, status="active")):
        pytest.skip("BTC-USDT futures already has open orders; not touching unrelated orders.")
    if _futures_position_size(client) != 0:
        pytest.skip("BTC-USDT futures already has a position; not changing exposure.")


@pytest.mark.private
def test_spot_post_only_order_lifecycle(client):
    _skip_if_spot_open_orders(client)
    size, price = _spot_order_params(client)
    _skip_if_spot_usdt_insufficient(client, size, price)
    order_id = None
    try:
        order = client.place_spot_post_only_limit_buy_order(
            product_symbol=SPOT_SYMBOL,
            size=size,
            price=price,
            clientOid=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["orderId"]
        assert _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL))
    finally:
        if order_id is not None:
            client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)


@pytest.mark.private
def test_spot_batch_order_and_cancel_by_symbol(client):
    _skip_if_spot_open_orders(client)
    size, price = _spot_order_params(client)
    _skip_if_spot_usdt_insufficient(client, size, price)
    try:
        order = client.place_spot_batch_limit_orders(
            [
                {
                    "symbol": SPOT_SYMBOL,
                    "side": "buy",
                    "size": size,
                    "price": price,
                    "clientOid": f"dcex-{uuid.uuid4().hex}",
                    "postOnly": True,
                }
            ]
        )
        assert order.get("data") is not None
    finally:
        client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL)


@pytest.mark.private
def test_spot_cancel_all_orders(client):
    _skip_if_spot_open_orders(client)
    size, price = _spot_order_params(client)
    _skip_if_spot_usdt_insufficient(client, size, price)
    order_id = None
    try:
        order = client.place_spot_post_only_limit_buy_order(
            product_symbol=SPOT_SYMBOL,
            size=size,
            price=price,
            clientOid=f"dcex-{uuid.uuid4().hex}",
        )
        order_id = order["data"]["orderId"]
        assert _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL))
        assert client.cancel_spot_all_orders().get("data") is not None
        order_id = None
        _wait_until_no_spot_open_orders(client)
    finally:
        if order_id is not None:
            client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)


@pytest.mark.private
def test_spot_market_round_trip(client):
    step, min_size, min_notional = _spot_step_and_min(client)
    funds = min_notional * Decimal("1.01")
    _skip_if_spot_funds_insufficient(client, funds)

    btc_before = _available(client, "BTC", "trade")
    client.place_spot_market_buy_order(
        product_symbol=SPOT_SYMBOL,
        funds=_fmt(funds),
        clientOid=f"dcex-{uuid.uuid4().hex}",
    )
    time.sleep(2)
    acquired = _round_to_step(_available(client, "BTC", "trade") - btc_before, step, ROUND_DOWN)
    assert acquired >= min_size
    client.place_spot_market_sell_order(
        product_symbol=SPOT_SYMBOL,
        size=_fmt(acquired),
        clientOid=f"dcex-{uuid.uuid4().hex}",
    )


@pytest.mark.private
def test_futures_post_only_order_lifecycle(client):
    _skip_if_futures_state(client)
    size, price, _, multiplier = _futures_order_params(client)
    _skip_if_futures_margin_insufficient(client, size, price, multiplier)
    order_id = None
    client_oid = f"dcex-{uuid.uuid4().hex}"
    try:
        order = client.place_futures_post_only_limit_buy_order(
            product_symbol=FUTURES_SYMBOL,
            size=size,
            price=price,
            clientOid=client_oid,
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert client.get_futures_order(orderId=order_id).get("data") is not None
        assert (
            client.get_futures_order_by_client_oid(
                clientOid=client_oid,
                product_symbol=FUTURES_SYMBOL,
            ).get("data")
            is not None
        )
        assert _items(client.get_futures_order_list(product_symbol=FUTURES_SYMBOL, status="active"))
        assert client.get_futures_open_order_value(product_symbol=FUTURES_SYMBOL).get("data")
    finally:
        if order_id is not None:
            client.cancel_futures_order(orderId=order_id)


@pytest.mark.private
def test_futures_cancel_by_client_oid(client):
    _skip_if_futures_state(client)
    size, price, _, multiplier = _futures_order_params(client)
    _skip_if_futures_margin_insufficient(client, size, price, multiplier)
    order_id = None
    client_oid = f"dcex-{uuid.uuid4().hex}"
    try:
        order = client.place_futures_post_only_limit_buy_order(
            product_symbol=FUTURES_SYMBOL,
            size=size,
            price=price,
            clientOid=client_oid,
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert (
            client.cancel_futures_order_by_client_oid(
                clientOid=client_oid,
                product_symbol=FUTURES_SYMBOL,
            ).get("data")
            is not None
        )
        order_id = None
    finally:
        if order_id is not None:
            client.cancel_futures_order(orderId=order_id)


@pytest.mark.private
def test_futures_cancel_all_orders(client):
    _skip_if_futures_state(client)
    size, price, _, multiplier = _futures_order_params(client)
    _skip_if_futures_margin_insufficient(client, size, price, multiplier)
    order_id = None
    try:
        order = client.place_futures_post_only_limit_buy_order(
            product_symbol=FUTURES_SYMBOL,
            size=size,
            price=price,
            clientOid=f"dcex-{uuid.uuid4().hex}",
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        order_id = order["data"]["orderId"]
        assert client.cancel_futures_all_orders(product_symbol=FUTURES_SYMBOL).get("data")
        order_id = None
    finally:
        if order_id is not None:
            client.cancel_futures_order(orderId=order_id)


@pytest.mark.private
def test_futures_market_round_trip(client):
    _skip_if_futures_state(client)
    size, _, current_price, multiplier = _futures_order_params(client)
    _skip_if_futures_margin_insufficient(
        client,
        size,
        _fmt(current_price),
        multiplier,
    )

    client.place_futures_market_buy_order(
        product_symbol=FUTURES_SYMBOL,
        size=size,
        clientOid=f"dcex-{uuid.uuid4().hex}",
        leverage=int(FUTURES_LEVERAGE),
        marginMode="CROSS",
        positionSide="BOTH",
    )
    time.sleep(2)
    try:
        client.place_futures_market_sell_order(
            product_symbol=FUTURES_SYMBOL,
            size=size,
            clientOid=f"dcex-{uuid.uuid4().hex}",
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
            reduceOnly=True,
        )
        time.sleep(2)
        assert _futures_position_size(client) == 0
    except Exception:
        if _futures_position_size(client) > 0:
            client.place_futures_market_sell_order(
                product_symbol=FUTURES_SYMBOL,
                size=size,
                clientOid=f"dcex-{uuid.uuid4().hex}",
                leverage=int(FUTURES_LEVERAGE),
                marginMode="CROSS",
                positionSide="BOTH",
                reduceOnly=True,
            )
        raise


@pytest.mark.private
def test_trade_history_endpoints(client):
    assert client.get_spot_trade_history(product_symbol=SPOT_SYMBOL, limit=10) is not None
    assert (
        client.get_futures_order_list(
            product_symbol=FUTURES_SYMBOL,
            status="active",
            pageSize=10,
        )
        is not None
    )
    assert client.get_futures_trade_history(product_symbol=FUTURES_SYMBOL, pageSize=10) is not None
    assert client.get_futures_recent_trade_history(product_symbol=FUTURES_SYMBOL) is not None
