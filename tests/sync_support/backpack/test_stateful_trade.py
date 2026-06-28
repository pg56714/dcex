# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os
import time
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.backpack.client import Client

load_dotenv()

BACKPACK_API_KEY = os.getenv("BACKPACK_API_KEY")
BACKPACK_API_SECRET = os.getenv("BACKPACK_API_SECRET")
SPOT_SYMBOL = "SOL_USDC"
PERP_SYMBOL = "SOL_USDC_PERP"

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Backpack order tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        api_key=BACKPACK_API_KEY,
        api_secret=BACKPACK_API_SECRET,
        preload_product_table=False,
        timeout=20,
    )
    try:
        yield client_instance
    finally:
        client_instance.close()


def _dec(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _balances(client: Client) -> dict:
    response = client.get_balances()
    assert isinstance(response, dict)
    return response


def _available(client: Client, asset: str) -> Decimal:
    balance = _balances(client).get(asset, {})
    if isinstance(balance, dict):
        return _dec(balance.get("available"))
    return Decimal("0")


def _lent(client: Client, asset: str) -> Decimal:
    positions = _items(client.get_borrow_lend_positions())
    for position in positions:
        if position.get("symbol") == asset:
            return max(_dec(position.get("netQuantity")), Decimal("0"))
    return Decimal("0")


def _total_asset(client: Client, asset: str) -> Decimal:
    return _available(client, asset) + _lent(client, asset)


def _market_details(client: Client, symbol: str) -> tuple[Decimal, Decimal, Decimal]:
    market = client.get_market(symbol)
    assert isinstance(market, dict)
    filters = market.get("filters", {})
    assert isinstance(filters, dict)
    price_filter = filters.get("price", {})
    quantity_filter = filters.get("quantity", {})
    assert isinstance(price_filter, dict)
    assert isinstance(quantity_filter, dict)
    tick = _dec(price_filter.get("tickSize"), "0.01")
    step = _dec(quantity_filter.get("stepSize"), "0.01")
    min_size = _dec(quantity_filter.get("minQuantity"), "0.01")
    return tick, step, min_size


def _book_prices(client: Client, symbol: str) -> tuple[Decimal, Decimal]:
    book = client.get_order_book_depth(symbol, limit=5)
    assert isinstance(book, dict)
    bids = book.get("bids", [])
    asks = book.get("asks", [])
    assert bids and asks
    return _dec(bids[0][0]), _dec(asks[0][0])


def _safe_limit_price(client: Client, symbol: str, side: str) -> str:
    tick, _, _ = _market_details(client, symbol)
    bid, ask = _book_prices(client, symbol)
    if side == "Bid":
        return _fmt(_round_to_step(bid - tick, tick, ROUND_DOWN))
    return _fmt(_round_to_step(ask + tick, tick, ROUND_UP))


def _min_quantity(client: Client, symbol: str) -> Decimal:
    _, step, min_size = _market_details(client, symbol)
    return _round_to_step(min_size, step, ROUND_UP)


def _order_id(response) -> str:
    if isinstance(response, dict):
        for key in ("id", "orderId"):
            if response.get(key):
                return str(response[key])
    raise AssertionError(f"Backpack order response has no order id: {response}")


def _items(response: object) -> list[dict]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    return []


def _open_orders(client: Client, symbol: str) -> list[dict]:
    return _items(client.get_open_orders(product_symbol=symbol))


def _position_size(client: Client, symbol: str) -> Decimal:
    positions = _items(client.get_open_positions())
    size = Decimal("0")
    for position in positions:
        if position.get("symbol") != symbol:
            continue
        quantity = _dec(position.get("netQuantity") or position.get("quantity"))
        size += quantity
    return size


def _skip_if_existing_state(client: Client) -> None:
    if _open_orders(client, SPOT_SYMBOL):
        pytest.skip("Backpack spot already has SOL_USDC open orders.")
    if _open_orders(client, PERP_SYMBOL):
        pytest.skip("Backpack perp already has SOL_USDC_PERP open orders.")
    if _position_size(client, PERP_SYMBOL) != 0:
        pytest.skip("Backpack already has a SOL_USDC_PERP position.")


def _ensure_usdc(client: Client, required: Decimal) -> None:
    if _available(client, "USDC") + _lent(client, "USDC") < required:
        pytest.skip("Insufficient Backpack USDC for stateful test.")


def _cancel_order(client: Client, symbol: str, order_id: str) -> None:
    client.cancel_order(symbol, orderId=order_id)
    time.sleep(1)


def _cancel_all_symbol_orders(client: Client, symbol: str) -> None:
    with suppress(Exception):
        client.cancel_open_orders(product_symbol=symbol)
    time.sleep(1)


def test_spot_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    min_qty = _min_quantity(client, SPOT_SYMBOL)
    qty = min_qty * 2
    _, ask = _book_prices(client, SPOT_SYMBOL)
    _ensure_usdc(client, qty * ask * Decimal("1.01"))
    initial_sol = _total_asset(client, "SOL")
    if initial_sol >= min_qty:
        pytest.skip("Backpack already has a tradable SOL balance.")

    try:
        client.place_market_order(
            SPOT_SYMBOL,
            side="Bid",
            quantity=_fmt(qty),
            autoLend=False,
            autoLendRedeem=True,
        )
        time.sleep(2)
        acquired = _total_asset(client, "SOL") - initial_sol
        _, step, _ = _market_details(client, SPOT_SYMBOL)
        sell_qty = _round_to_step(acquired, step, ROUND_DOWN)
        assert sell_qty >= min_qty

        order_id = _order_id(
            client.place_limit_order(
                SPOT_SYMBOL,
                side="Ask",
                quantity=_fmt(sell_qty),
                price=_safe_limit_price(client, SPOT_SYMBOL, "Ask"),
                postOnly=True,
                autoLendRedeem=True,
            )
        )
        assert isinstance(client.get_open_order(SPOT_SYMBOL, orderId=order_id), dict)
        _cancel_order(client, SPOT_SYMBOL, order_id)

        client.place_batch_orders(
            [
                {
                    "symbol": SPOT_SYMBOL,
                    "side": "Ask",
                    "orderType": "Limit",
                    "quantity": _fmt(sell_qty),
                    "price": _safe_limit_price(client, SPOT_SYMBOL, "Ask"),
                    "postOnly": True,
                    "autoLendRedeem": True,
                }
            ]
        )
        _cancel_all_symbol_orders(client, SPOT_SYMBOL)

        client.place_market_order(
            SPOT_SYMBOL,
            side="Ask",
            quantity=_fmt(sell_qty),
            autoLend=True,
            autoLendRedeem=True,
        )
        time.sleep(2)
        if initial_sol == 0 and 0 < _total_asset(client, "SOL") < min_qty:
            client.convert_dust("SOL")
            time.sleep(1)

        assert isinstance(client.get_order_history(product_symbol=SPOT_SYMBOL, limit=20), list)
        assert isinstance(client.get_fill_history(product_symbol=SPOT_SYMBOL, limit=20), list)
    finally:
        _cancel_all_symbol_orders(client, SPOT_SYMBOL)
        with suppress(Exception):
            _, step, min_qty = _market_details(client, SPOT_SYMBOL)
            acquired = max(_total_asset(client, "SOL") - initial_sol, Decimal("0"))
            remaining = _round_to_step(acquired, step, ROUND_DOWN)
            if remaining >= min_qty:
                client.place_market_order(
                    SPOT_SYMBOL,
                    side="Ask",
                    quantity=_fmt(remaining),
                    autoLend=True,
                    autoLendRedeem=True,
                )
                time.sleep(1)
            if initial_sol == 0 and 0 < _total_asset(client, "SOL") < min_qty:
                client.convert_dust("SOL")


def test_perp_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    qty = _min_quantity(client, PERP_SYMBOL)
    _, ask = _book_prices(client, PERP_SYMBOL)
    _ensure_usdc(client, qty * ask * Decimal("0.2"))

    try:
        client.place_market_order(
            PERP_SYMBOL,
            side="Bid",
            quantity=_fmt(qty),
            autoLend=False,
            autoLendRedeem=True,
        )
        time.sleep(2)
        assert _position_size(client, PERP_SYMBOL) > 0

        order_id = _order_id(
            client.place_limit_order(
                PERP_SYMBOL,
                side="Ask",
                quantity=_fmt(qty),
                price=_safe_limit_price(client, PERP_SYMBOL, "Ask"),
                postOnly=True,
                reduceOnly=True,
            )
        )
        assert isinstance(client.get_open_order(PERP_SYMBOL, orderId=order_id), dict)
        _cancel_order(client, PERP_SYMBOL, order_id)

        client.place_batch_orders(
            [
                {
                    "symbol": PERP_SYMBOL,
                    "side": "Ask",
                    "orderType": "Limit",
                    "quantity": _fmt(qty),
                    "price": _safe_limit_price(client, PERP_SYMBOL, "Ask"),
                    "postOnly": True,
                    "reduceOnly": True,
                }
            ]
        )
        _cancel_all_symbol_orders(client, PERP_SYMBOL)

        client.place_market_order(
            PERP_SYMBOL,
            side="Ask",
            quantity=_fmt(qty),
            reduceOnly=True,
            autoLend=True,
        )
        time.sleep(2)

        assert _position_size(client, PERP_SYMBOL) == 0
        assert isinstance(client.get_order_history(product_symbol=PERP_SYMBOL, limit=20), list)
        assert isinstance(client.get_fill_history(product_symbol=PERP_SYMBOL, limit=20), list)
    finally:
        _cancel_all_symbol_orders(client, PERP_SYMBOL)
        with suppress(Exception):
            size = _position_size(client, PERP_SYMBOL)
            if size > 0:
                client.place_market_order(
                    PERP_SYMBOL,
                    side="Ask",
                    quantity=_fmt(size),
                    reduceOnly=True,
                    autoLend=True,
                )
