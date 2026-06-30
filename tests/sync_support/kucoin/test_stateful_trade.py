# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.kucoin.client import Client
from dcex.utils.errors import FailedRequestError

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
    client_instance = Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
    )
    _cleanup(client_instance, _snapshot_balances(client_instance))
    clean_initial = _snapshot_balances(client_instance)
    try:
        yield client_instance
    finally:
        _cleanup(client_instance, clean_initial)


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
        pytest.fail(reason, pytrace=False)

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
    best_bid, _ = _spot_prices(client)
    price = _round_to_step(min(best_bid - tick, best_bid * Decimal("0.999")), tick, ROUND_DOWN)
    size = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(size, min_size)), _fmt(price)


def _spot_step_and_min(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("kucoin", SPOT_SYMBOL)
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "1"), Decimal("1"))
    return step, min_size, min_notional


def _spot_prices(client: Client) -> tuple[Decimal, Decimal]:
    book = client.get_spot_orderbook(product_symbol=SPOT_SYMBOL)["data"]
    return _dec(book["bids"][0][0]), _dec(book["asks"][0][0])


def _spot_market_funds(client: Client) -> Decimal:
    _, _, min_notional = _spot_step_and_min(client)
    return min_notional * Decimal("1.01")


def _spot_sell_quantity(client: Client, quantity: Decimal) -> str:
    step, _, _ = _spot_step_and_min(client)
    return _fmt(_round_to_step(quantity, step, ROUND_DOWN))


def _spot_sellable_quantity(client: Client, quantity: Decimal) -> str:
    step, min_size, min_notional = _spot_step_and_min(client)
    bid, _ = _spot_prices(client)
    size = _round_to_step(quantity, step, ROUND_DOWN)
    if size < min_size or size * bid < min_notional:
        return "0"
    return _fmt(size)


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
    ticker = client.get_futures_ticker(product_symbol=FUTURES_SYMBOL)["data"]
    current_price = _dec(ticker["price"])
    best_bid = _dec(ticker.get("bestBidPrice"), str(current_price))
    price = _round_to_step(min(best_bid - tick, best_bid * Decimal("0.999")), tick, ROUND_DOWN)
    return int(max(lot, Decimal("1"))), _fmt(price), current_price, multiplier


def _snapshot_balances(client: Client) -> dict[str, Decimal]:
    return {
        "trade_usdt": _available(client, "USDT", "trade"),
        "trade_btc": _available(client, "BTC", "trade"),
        "contract_usdt": _futures_available_usdt(client),
    }


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
        pytest.fail("Insufficient futures USDT for KuCoin futures post-only order.", pytrace=False)


def _skip_if_spot_open_orders(client: Client) -> None:
    _cancel_spot_open_orders(client)


def _wait_until_no_spot_open_orders(client: Client) -> None:
    for _ in range(5):
        if not _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL)):
            return
        time.sleep(1)
    assert not _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL))


def _wait_until_no_futures_open_orders(client: Client) -> None:
    for _ in range(5):
        if not _items(
            client.get_futures_order_list(product_symbol=FUTURES_SYMBOL, status="active")
        ):
            return
        time.sleep(1)
    assert not _items(client.get_futures_order_list(product_symbol=FUTURES_SYMBOL, status="active"))


def _wait_for_spot_open_orders(client: Client) -> list[dict]:
    for _ in range(5):
        orders = _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL))
        if orders:
            return orders
        time.sleep(1)
    return []


def _cancel_spot_order(client: Client, order_id: str) -> dict:
    try:
        return client.cancel_spot_order(orderId=order_id, product_symbol=SPOT_SYMBOL)
    except FailedRequestError as exc:
        if "400100" not in str(exc) and "Order not exist" not in str(exc):
            raise
        return {"code": "200000", "data": {}}


def _cancel_spot_open_orders(client: Client) -> None:
    if _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL)):
        client.cancel_spot_all_orders_by_symbol(product_symbol=SPOT_SYMBOL)
        _wait_until_no_spot_open_orders(client)


def _is_futures_order_not_cancelable(exc: FailedRequestError) -> bool:
    message = str(exc).lower()
    return "100004" in message and "cannot be canceled" in message


def _cancel_futures_order(client: Client, order_id: str) -> dict:
    try:
        return client.cancel_futures_order(orderId=order_id)
    except FailedRequestError as exc:
        if _is_futures_order_not_cancelable(exc):
            return {"code": "200000", "data": {}}
        raise


def _cancel_futures_open_orders(client: Client) -> None:
    if _items(client.get_futures_order_list(product_symbol=FUTURES_SYMBOL, status="active")):
        client.cancel_futures_all_orders(product_symbol=FUTURES_SYMBOL)
        _wait_until_no_futures_open_orders(client)


def _wait_until_flat(client: Client) -> None:
    for _ in range(10):
        if _futures_position_size(client) == 0:
            return
        time.sleep(1)
    assert _futures_position_size(client) == 0


def _close_futures_position(client: Client) -> None:
    for _ in range(3):
        position_size = _futures_position_size(client)
        if position_size == 0:
            return
        close_size = int(abs(position_size))
        if close_size <= 0:
            raise AssertionError(f"Invalid KuCoin futures position size: {position_size}")
        if position_size > 0:
            client.place_futures_market_sell_order(
                product_symbol=FUTURES_SYMBOL,
                size=close_size,
                clientOid=f"dcex-{uuid.uuid4().hex}",
                leverage=int(FUTURES_LEVERAGE),
                marginMode="CROSS",
                positionSide="BOTH",
                reduceOnly=True,
            )
        else:
            client.place_futures_market_buy_order(
                product_symbol=FUTURES_SYMBOL,
                size=close_size,
                clientOid=f"dcex-{uuid.uuid4().hex}",
                leverage=int(FUTURES_LEVERAGE),
                marginMode="CROSS",
                positionSide="BOTH",
                reduceOnly=True,
            )
        time.sleep(2)
        if _futures_position_size(client) == 0:
            return
    _wait_until_flat(client)


def _top_up_spot_btc_for_sell(client: Client, btc_delta: Decimal) -> None:
    if btc_delta <= 0:
        return
    step, min_size, min_notional = _spot_step_and_min(client)
    bid, ask = _spot_prices(client)
    sellable = _round_to_step(btc_delta, step, ROUND_DOWN)
    target = max(min_size, _round_to_step(min_notional / bid, step, ROUND_UP))
    top_up_size = target - sellable
    if top_up_size <= 0:
        return
    funds = top_up_size * ask * Decimal("1.02")
    _skip_if_spot_funds_insufficient(client, funds)
    client.place_spot_market_buy_order(
        product_symbol=SPOT_SYMBOL,
        funds=_fmt(funds),
        clientOid=f"dcex-{uuid.uuid4().hex}",
    )
    time.sleep(2)


def _return_spot_btc_delta(client: Client, initial_btc: Decimal) -> None:
    for _ in range(4):
        btc_delta = _available(client, "BTC", "trade") - initial_btc
        if btc_delta <= 0:
            return
        sell_size = _spot_sellable_quantity(client, btc_delta)
        if Decimal(sell_size) <= 0:
            _top_up_spot_btc_for_sell(client, btc_delta)
            continue
        client.place_spot_market_sell_order(
            product_symbol=SPOT_SYMBOL,
            size=sell_size,
            clientOid=f"dcex-{uuid.uuid4().hex}",
        )
        time.sleep(2)

    step, _, _ = _spot_step_and_min(client)
    remaining = _available(client, "BTC", "trade") - initial_btc
    assert remaining <= step


def _return_excess_balances(client: Client, initial: dict[str, Decimal]) -> None:
    trade_usdt = _available(client, "USDT", "trade")
    excess_usdt = trade_usdt - initial["trade_usdt"]
    if excess_usdt > Decimal("0.00000001"):
        client.flex_transfer(
            currency="USDT",
            amount=_fmt_usdt_transfer(excess_usdt),
            fromAccountType="TRADE",
            toAccountType="MAIN",
            clientOid=f"dcex-{uuid.uuid4().hex}",
        )
        time.sleep(2)

    contract_usdt = _futures_available_usdt(client)
    excess_contract_usdt = contract_usdt - initial["contract_usdt"]
    if excess_contract_usdt > Decimal("0.00000001"):
        client.flex_transfer(
            currency="USDT",
            amount=_fmt_usdt_transfer(excess_contract_usdt),
            fromAccountType="CONTRACT",
            toAccountType="MAIN",
            clientOid=f"dcex-{uuid.uuid4().hex}",
        )
        time.sleep(2)


def _cleanup(client: Client, initial: dict[str, Decimal]) -> None:
    _cancel_spot_open_orders(client)
    _cancel_futures_open_orders(client)
    _close_futures_position(client)
    _return_spot_btc_delta(client, initial["trade_btc"])
    _return_excess_balances(client, initial)
    assert not _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL))
    assert not _items(client.get_futures_order_list(product_symbol=FUTURES_SYMBOL, status="active"))
    assert _futures_position_size(client) == 0


def _skip_if_spot_usdt_insufficient(client: Client, size: str, price: str) -> None:
    required = Decimal(size) * Decimal(price) * Decimal("1.02")
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
        pytest.fail("Insufficient spot trade USDT for KuCoin spot post-only order.", pytrace=False)


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
        pytest.fail(
            "Insufficient spot trade USDT for KuCoin spot market round-trip.", pytrace=False
        )


def _skip_if_futures_state(client: Client) -> None:
    _cancel_futures_open_orders(client)
    _close_futures_position(client)


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
        assert _wait_for_spot_open_orders(client)
    finally:
        if order_id is not None:
            _cancel_spot_order(client, order_id)


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
        assert _wait_for_spot_open_orders(client)
        assert client.cancel_spot_all_orders().get("data") is not None
        order_id = None
        _wait_until_no_spot_open_orders(client)
    finally:
        if order_id is not None:
            _cancel_spot_order(client, order_id)


@pytest.mark.private
def test_spot_market_round_trip(client):
    step, min_size, _ = _spot_step_and_min(client)
    funds = _spot_market_funds(client)
    _skip_if_spot_funds_insufficient(client, funds)

    btc_before = _available(client, "BTC", "trade")
    try:
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
    finally:
        _return_spot_btc_delta(client, btc_before)


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
            _cancel_futures_order(client, order_id)


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
            _cancel_futures_order(client, order_id)


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
            _cancel_futures_order(client, order_id)


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

    try:
        client.place_futures_market_buy_order(
            product_symbol=FUTURES_SYMBOL,
            size=size,
            clientOid=f"dcex-{uuid.uuid4().hex}",
            leverage=int(FUTURES_LEVERAGE),
            marginMode="CROSS",
            positionSide="BOTH",
        )
        time.sleep(2)
        assert _futures_position_size(client) > 0
    finally:
        _close_futures_position(client)


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
