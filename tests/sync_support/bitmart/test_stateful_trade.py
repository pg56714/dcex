# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.bitmart.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BITMART_API_KEY = os.getenv("BITMART_API_KEY")
BITMART_API_SECRET = os.getenv("BITMART_API_SECRET")
BITMART_MEMO = os.getenv("BITMART_MEMO")
SPOT_SYMBOL = "DOGE-USDT-SPOT"
SPOT_EXCHANGE_SYMBOL = "DOGE_USDT"
SPOT_BASE_CURRENCY = "DOGE"
CONTRACT_SYMBOL = "DOGE-USDT-SWAP"
CONTRACT_SIZE = 1
CONTRACT_LEVERAGE = "50"
CONTRACT_TRANSFER_USDT = Decimal("2")
SPOT_TEST_NOTIONAL = Decimal("5.4")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real BitMart order tests.",
    ),
]


@pytest.fixture
def client():
    return Client(
        api_key=BITMART_API_KEY,
        api_secret=BITMART_API_SECRET,
        memo=BITMART_MEMO,
        timeout=20,
    )


def _dec(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _client_id() -> str:
    return f"dcex{uuid.uuid4().hex[:20]}"


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _items(res: object) -> list[dict]:
    if isinstance(res, list):
        return [item for item in res if isinstance(item, dict)]
    if isinstance(res, dict):
        data = res.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            for key in ("orders", "trades", "records", "wallet", "symbols"):
                if isinstance(data.get(key), list):
                    return [item for item in data[key] if isinstance(item, dict)]
    return []


def _data(res: dict) -> dict:
    data = res.get("data", {})
    return data if isinstance(data, dict) else {}


def _order_id(res: dict) -> str:
    data = _data(res)
    for key in ("order_id", "orderId", "orderID", "id"):
        if data.get(key) is not None:
            return str(data[key])
    raise AssertionError(f"BitMart order response has no order id: {res}")


def _skip_if_account_restriction(exc: FailedRequestError) -> None:
    message = str(exc)
    if (
        "33136" in message
        or "personal verification" in message.lower()
        or "60052" in message
    ):
        pytest.skip(f"BitMart account restriction prevented live trading endpoint: {exc}")
    raise exc


def _spot_available(client: Client, currency: str) -> Decimal:
    for item in _items(client.get_spot_wallet()):
        if item.get("id") == currency or item.get("currency") == currency:
            return _dec(item.get("available"))
    return Decimal("0")


def _contract_available_usdt(client: Client) -> Decimal:
    for item in _items(client.get_contract_assets()):
        if item.get("currency") == "USDT":
            return _dec(item.get("available_balance"))
    return Decimal("0")


def _spot_open_orders(client: Client) -> list[dict]:
    return _items(client.get_spot_open_orders(product_symbol=SPOT_SYMBOL, limit=20))


def _contract_open_orders(client: Client) -> list[dict]:
    return _items(client.get_contract_open_order(product_symbol=CONTRACT_SYMBOL, limit=20))


def _contract_positions(client: Client) -> list[dict]:
    return _items(client.get_contract_position(product_symbol=CONTRACT_SYMBOL))


def _contract_position_size(client: Client) -> Decimal:
    size = Decimal("0")
    for position in _contract_positions(client):
        amount = _dec(position.get("current_amount", position.get("position_amount")))
        if _dec(position.get("position_type")) == Decimal("2"):
            size -= amount
        else:
            size += amount
    return size


def _skip_if_existing_state(client: Client) -> None:
    if _spot_open_orders(client):
        pytest.skip("BitMart spot already has open orders; not touching unrelated orders.")
    if _contract_open_orders(client):
        pytest.skip("BitMart contract already has open orders; not touching unrelated orders.")
    if _contract_position_size(client) != 0:
        pytest.skip("BitMart contract already has a position; not changing exposure.")


def _spot_pair_details(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    for item in _items(client.get_trading_pairs_details()):
        if item.get("symbol") == SPOT_EXCHANGE_SYMBOL:
            base_step = _dec(item.get("base_min_size"), "0.00001")
            min_notional = max(
                _dec(item.get("min_buy_amount"), "5"),
                _dec(item.get("min_sell_amount"), "5"),
                Decimal("5"),
            )
            precision = item.get("price_max_precision")
            if precision is None:
                price_step = Decimal("0.01")
            else:
                price_step = Decimal("1").scaleb(-int(precision))
            return base_step, min_notional, price_step
    return Decimal("0.00001"), Decimal("5"), Decimal("0.01")


def _spot_best_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _data(client.get_ticker_of_a_pair(product_symbol=SPOT_SYMBOL))
    bid = _dec(data.get("bid_px", data.get("last")))
    ask = _dec(data.get("ask_px", data.get("last")))
    if bid <= 0 or ask <= 0:
        pytest.skip("BitMart spot ticker did not return bid/ask prices.")
    return bid, ask


def _spot_post_only_buy_params(client: Client) -> tuple[str, str]:
    base_step, min_notional, price_step = _spot_pair_details(client)
    best_bid, _ = _spot_best_prices(client)
    price = _round_to_step(best_bid * Decimal("0.98"), price_step, ROUND_DOWN)
    size = _round_to_step((min_notional * Decimal("1.05")) / price, base_step, ROUND_UP)
    return _fmt(size), _fmt(price)


def _spot_market_notional(client: Client) -> str:
    _, min_notional, _ = _spot_pair_details(client)
    return _fmt(max(min_notional * Decimal("1.2"), SPOT_TEST_NOTIONAL))


def _spot_sell_size(client: Client, size: Decimal) -> str:
    base_step, _, _ = _spot_pair_details(client)
    return _fmt(_round_to_step(size, base_step, ROUND_DOWN))


def _spot_post_only_sell_price(client: Client) -> str:
    _, _, price_step = _spot_pair_details(client)
    _, best_ask = _spot_best_prices(client)
    return _fmt(_round_to_step(best_ask * Decimal("1.50"), price_step, ROUND_UP))


def _spot_fillable_buy_params(client: Client) -> tuple[str, str]:
    base_step, min_notional, price_step = _spot_pair_details(client)
    _, best_ask = _spot_best_prices(client)
    price = _round_to_step(best_ask + price_step, price_step, ROUND_UP)
    size = _round_to_step((min_notional * Decimal("1.2")) / price, base_step, ROUND_UP)
    return _fmt(size), _fmt(price)


def _spot_fillable_sell_price(client: Client) -> str:
    _, _, price_step = _spot_pair_details(client)
    best_bid, _ = _spot_best_prices(client)
    return _fmt(_round_to_step(best_bid - price_step, price_step, ROUND_DOWN))


def _contract_best_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _data(client.get_depth(product_symbol=CONTRACT_SYMBOL))
    bids = data.get("bids", [])
    asks = data.get("asks", [])
    if not bids or not asks:
        pytest.skip("BitMart contract depth did not return bid/ask prices.")
    return _dec(bids[0][0]), _dec(asks[0][0])


def _contract_price_step(client: Client) -> Decimal:
    symbols = _items(client.get_contracts_details(product_symbol=CONTRACT_SYMBOL))
    if symbols:
        return _dec(symbols[0].get("price_precision"), "0.1")
    return Decimal("0.1")


def _contract_post_only_buy_price(client: Client) -> str:
    best_bid, _ = _contract_best_prices(client)
    return _fmt(
        _round_to_step(best_bid * Decimal("0.98"), _contract_price_step(client), ROUND_DOWN)
    )


def _contract_post_only_sell_price(client: Client) -> str:
    _, best_ask = _contract_best_prices(client)
    return _fmt(_round_to_step(best_ask * Decimal("1.02"), _contract_price_step(client), ROUND_UP))


def _contract_fillable_buy_price(client: Client) -> str:
    _, best_ask = _contract_best_prices(client)
    step = _contract_price_step(client)
    return _fmt(_round_to_step(best_ask * Decimal("1.02"), step, ROUND_UP))


def _contract_fillable_sell_price(client: Client) -> str:
    best_bid, _ = _contract_best_prices(client)
    step = _contract_price_step(client)
    return _fmt(_round_to_step(best_bid * Decimal("0.98"), step, ROUND_DOWN))


def _ensure_spot_usdt(client: Client, required: Decimal) -> None:
    if _spot_available(client, "USDT") < required:
        pytest.skip("Insufficient BitMart spot USDT for stateful order test.")


def _ensure_contract_margin(client: Client) -> None:
    if _contract_available_usdt(client) >= Decimal("1"):
        return
    _ensure_spot_usdt(client, CONTRACT_TRANSFER_USDT)
    assert (
        client.transfer_contract(amount=_fmt(CONTRACT_TRANSFER_USDT), type="spot_to_contract")
        is not None
    )
    time.sleep(2)
    if _contract_available_usdt(client) < Decimal("1"):
        pytest.skip("Insufficient BitMart contract USDT after transfer.")


def _cleanup_spot_base(client: Client, initial_spot_base: Decimal) -> None:
    base_delta = _spot_available(client, SPOT_BASE_CURRENCY) - initial_spot_base
    sell_size = _spot_sell_size(client, base_delta)
    best_bid, _ = _spot_best_prices(client)
    _, min_notional, _ = _spot_pair_details(client)
    if Decimal(sell_size) > 0 and Decimal(sell_size) * best_bid >= min_notional:
        client.place_spot_market_sell_order(SPOT_SYMBOL, size=sell_size)
        time.sleep(2)

    remaining = _spot_available(client, SPOT_BASE_CURRENCY) - initial_spot_base
    if remaining <= 0:
        return

    top_up_notional = max(min_notional * Decimal("1.05"), SPOT_TEST_NOTIONAL)
    if _spot_available(client, "USDT") < top_up_notional:
        return

    client.place_spot_market_buy_order(SPOT_SYMBOL, notional=_fmt(top_up_notional))
    time.sleep(2)
    sell_size = _spot_sell_size(
        client,
        _spot_available(client, SPOT_BASE_CURRENCY) - initial_spot_base,
    )
    best_bid, _ = _spot_best_prices(client)
    if Decimal(sell_size) > 0 and Decimal(sell_size) * best_bid >= min_notional:
        client.place_spot_market_sell_order(SPOT_SYMBOL, size=sell_size)
        time.sleep(2)


def _cleanup_contract_excess(client: Client, initial_contract_usdt: Decimal) -> None:
    for _ in range(4):
        time.sleep(2)
        excess_contract = _contract_available_usdt(client) - initial_contract_usdt
        transfer_amount = _round_to_step(excess_contract, Decimal("0.1"), ROUND_DOWN)
        if transfer_amount <= 0:
            return
        client.transfer_contract(amount=_fmt(transfer_amount), type="contract_to_spot")
        time.sleep(2)


def _cleanup(client: Client, initial_spot_base: Decimal, initial_contract_usdt: Decimal) -> None:
    with suppress(Exception):
        if _spot_open_orders(client):
            client.cancel_spot_all_order(product_symbol=SPOT_SYMBOL)
            time.sleep(1)
    with suppress(Exception):
        if _contract_open_orders(client):
            client.cancel_all_contract_order(product_symbol=CONTRACT_SYMBOL)
            time.sleep(1)
    with suppress(Exception):
        size = _contract_position_size(client)
        if size > 0:
            client.place_contract_market_order(CONTRACT_SYMBOL, side=3, size=int(abs(size)))
        elif size < 0:
            client.place_contract_market_order(CONTRACT_SYMBOL, side=2, size=int(abs(size)))
        time.sleep(2)
    with suppress(Exception):
        _cleanup_spot_base(client, initial_spot_base)
    with suppress(Exception):
        _cleanup_contract_excess(client, initial_contract_usdt)


def _wait_for_contract_position(client: Client, sign: int) -> Decimal:
    for _ in range(8):
        size = _contract_position_size(client)
        if sign > 0 and size > 0:
            return size
        if sign < 0 and size < 0:
            return size
        time.sleep(1)
    return Decimal("0")


def _close_contract_position(client: Client) -> None:
    size = _contract_position_size(client)
    if size > 0:
        client.place_contract_market_order(CONTRACT_SYMBOL, side=3, size=int(abs(size)))
    elif size < 0:
        client.place_contract_market_order(CONTRACT_SYMBOL, side=2, size=int(abs(size)))
    time.sleep(2)
    assert _contract_position_size(client) == 0


def _wait_for_contract_flat(client: Client) -> None:
    for _ in range(8):
        if _contract_position_size(client) == 0:
            return
        time.sleep(1)
    raise AssertionError(f"BitMart contract position remains open: {_contract_positions(client)}")


def test_spot_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    initial_base = _spot_available(client, SPOT_BASE_CURRENCY)
    initial_contract_usdt = _contract_available_usdt(client)
    try:
        size, price = _spot_post_only_buy_params(client)
        _ensure_spot_usdt(client, Decimal(size) * Decimal(price))

        order_id = None
        client_id = _client_id()
        try:
            order = client.place_spot_order(
                SPOT_SYMBOL,
                side="buy",
                type="limit_maker",
                size=size,
                price=price,
                client_order_id=client_id,
            )
            order_id = _order_id(order)
            assert client.get_spot_order_by_order_id(order_id, queryState="open") is not None
            assert (
                client.get_spot_order_by_order_client_id(client_id, queryState="open") is not None
            )
            assert client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id)

        order_id = None
        try:
            order = client.place_spot_limit_buy_order(SPOT_SYMBOL, size, price, _client_id())
            order_id = _order_id(order)
            assert client.cancel_spot_all_order(product_symbol=SPOT_SYMBOL) is not None
            order_id = None
            time.sleep(1)
        finally:
            if order_id is not None:
                client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id)

        order_id = None
        try:
            order = client.place_spot_post_only_limit_buy_order(
                SPOT_SYMBOL,
                size,
                price,
                _client_id(),
            )
            order_id = _order_id(order)
            assert client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id)

        notional = _spot_market_notional(client)
        _ensure_spot_usdt(client, Decimal(notional))
        before_base = _spot_available(client, SPOT_BASE_CURRENCY)
        market_buy = client.place_spot_market_buy_order(SPOT_SYMBOL, notional, _client_id())
        time.sleep(2)
        bought = _spot_available(client, SPOT_BASE_CURRENCY) - before_base
        sell_size = _spot_sell_size(client, bought)
        assert Decimal(sell_size) > 0
        assert client.get_spot_order_trade_list(_order_id(market_buy)) is not None
        assert client.place_spot_market_sell_order(SPOT_SYMBOL, sell_size, _client_id()) is not None
        time.sleep(2)

        fill_size, fill_price = _spot_fillable_buy_params(client)
        _ensure_spot_usdt(client, Decimal(fill_size) * Decimal(fill_price))
        before_base = _spot_available(client, SPOT_BASE_CURRENCY)
        assert client.place_spot_limit_buy_order(SPOT_SYMBOL, fill_size, fill_price) is not None
        time.sleep(2)
        bought = _spot_available(client, SPOT_BASE_CURRENCY) - before_base
        sell_size = _spot_sell_size(client, bought)
        assert Decimal(sell_size) > 0
        assert client.place_spot_limit_sell_order(
            SPOT_SYMBOL,
            sell_size,
            _spot_fillable_sell_price(client),
        ) is not None
        time.sleep(2)

        notional = _spot_market_notional(client)
        _ensure_spot_usdt(client, Decimal(notional))
        before_base = _spot_available(client, SPOT_BASE_CURRENCY)
        assert client.place_spot_market_order(
            SPOT_SYMBOL,
            side="buy",
            notional=notional,
        ) is not None
        time.sleep(2)
        bought = _spot_available(client, SPOT_BASE_CURRENCY) - before_base
        sell_size = _spot_sell_size(client, bought)
        assert Decimal(sell_size) > 0
        order_id = None
        try:
            order = client.place_spot_post_only_limit_sell_order(
                SPOT_SYMBOL,
                sell_size,
                _spot_post_only_sell_price(client),
                _client_id(),
            )
            order_id = _order_id(order)
            assert client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id) is not None
            order_id = None
            alias_order = client.place_post_only_limit_sell_order(
                SPOT_SYMBOL,
                sell_size,
                _spot_post_only_sell_price(client),
                _client_id(),
            )
            order_id = _order_id(alias_order)
            assert client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                client.cancel_spot_order(SPOT_SYMBOL, order_id=order_id)
            remaining = _spot_available(client, SPOT_BASE_CURRENCY) - before_base
            sell_size = _spot_sell_size(client, remaining)
            if Decimal(sell_size) > 0:
                client.place_spot_market_sell_order(SPOT_SYMBOL, sell_size)

        assert client.get_spot_open_orders(product_symbol=SPOT_SYMBOL, limit=10) is not None
        assert client.get_spot_account_orders(product_symbol=SPOT_SYMBOL, limit=10) is not None
        assert client.get_spot_account_trade_list(product_symbol=SPOT_SYMBOL, limit=10) is not None
    except FailedRequestError as exc:
        _skip_if_account_restriction(exc)
    finally:
        _cleanup(client, initial_base, initial_contract_usdt)


def test_contract_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    initial_base = _spot_available(client, SPOT_BASE_CURRENCY)
    initial_contract_usdt = _contract_available_usdt(client)
    try:
        _ensure_contract_margin(client)
        assert client.submit_leverage(
            CONTRACT_SYMBOL,
            leverage=CONTRACT_LEVERAGE,
            open_type="cross",
        ) is not None

        price = _contract_post_only_buy_price(client)
        order_id = None
        client_id = _client_id()
        try:
            order = client.place_contract_order(
                CONTRACT_SYMBOL,
                side=1,
                size=CONTRACT_SIZE,
                price=price,
                client_order_id=client_id,
                type="limit",
                leverage=CONTRACT_LEVERAGE,
                open_type="cross",
                mode=4,
            )
            order_id = _order_id(order)
            assert client.get_contract_order_detail(CONTRACT_SYMBOL, order_id) is not None
            assert client.modify_limit_order(
                CONTRACT_SYMBOL,
                order_id=order_id,
                price=_contract_post_only_buy_price(client),
                size=CONTRACT_SIZE,
            ) is not None
            assert client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id)

        order_id = None
        try:
            order = client.place_contract_limit_order(
                CONTRACT_SYMBOL,
                side=1,
                price=price,
                size=CONTRACT_SIZE,
                client_order_id=_client_id(),
                mode=4,
            )
            order_id = _order_id(order)
            assert client.cancel_all_contract_order(CONTRACT_SYMBOL) is not None
            order_id = None
            time.sleep(1)
        finally:
            if order_id is not None:
                client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id)

        for side, price_func in (
            (1, _contract_post_only_buy_price),
            (4, _contract_post_only_sell_price),
        ):
            order_id = None
            try:
                order = client.place_contract_post_only_order(
                    CONTRACT_SYMBOL,
                    side=side,
                    price=price_func(client),
                    size=CONTRACT_SIZE,
                    client_order_id=_client_id(),
                )
                order_id = _order_id(order)
                assert client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id) is not None
                order_id = None
            finally:
                if order_id is not None:
                    client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id)

        order_id = None
        try:
            order = client.place_contract_post_only_buy_order(
                CONTRACT_SYMBOL,
                price=_contract_post_only_buy_price(client),
                size=CONTRACT_SIZE,
                client_order_id=_client_id(),
            )
            order_id = _order_id(order)
            assert client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id) is not None
            order_id = None

            order = client.place_contract_post_only_sell_order(
                CONTRACT_SYMBOL,
                price=_contract_post_only_sell_price(client),
                size=CONTRACT_SIZE,
                client_order_id=_client_id(),
            )
            order_id = _order_id(order)
            assert client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                client.cancel_contract_order(CONTRACT_SYMBOL, order_id=order_id)

        assert client.place_contract_market_buy_order(
            CONTRACT_SYMBOL,
            CONTRACT_SIZE,
            _client_id(),
        ) is not None
        assert _wait_for_contract_position(client, sign=1) > 0
        assert client.place_contract_market_sell_order(
            CONTRACT_SYMBOL,
            CONTRACT_SIZE,
            _client_id(),
        ) is not None
        time.sleep(2)
        assert _contract_position_size(client) == 0

        assert client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=1,
            size=CONTRACT_SIZE,
            client_order_id=_client_id(),
        ) is not None
        assert _wait_for_contract_position(client, sign=1) > 0
        _close_contract_position(client)

        assert client.place_contract_limit_order(
            CONTRACT_SYMBOL,
            side=1,
            price=_contract_fillable_buy_price(client),
            size=CONTRACT_SIZE,
            client_order_id=_client_id(),
            mode=3,
        ) is not None
        assert _wait_for_contract_position(client, sign=1) > 0
        assert client.place_contract_limit_order(
            CONTRACT_SYMBOL,
            side=3,
            price=_contract_fillable_sell_price(client),
            size=CONTRACT_SIZE,
            client_order_id=_client_id(),
            mode=3,
        ) is not None
        _wait_for_contract_flat(client)

        assert client.get_contract_open_order(product_symbol=CONTRACT_SYMBOL, limit=10) is not None
        assert client.get_contract_order_history(product_symbol=CONTRACT_SYMBOL) is not None
        assert client.get_contract_trade(product_symbol=CONTRACT_SYMBOL) is not None
        assert client.get_contract_transaction_history(product_symbol=CONTRACT_SYMBOL) is not None
        assert client.get_contract_transfer_list(page=1, limit=10, currency="USDT") is not None
    except FailedRequestError as exc:
        _skip_if_account_restriction(exc)
    finally:
        _cleanup(client, initial_base, initial_contract_usdt)

    assert not _spot_open_orders(client)
    assert not _contract_open_orders(client)
    assert _contract_position_size(client) == 0
