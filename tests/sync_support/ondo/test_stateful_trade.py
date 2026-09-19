"""Opt-in Ondo limit-order and cancellation test; fills are not intended."""

import os
import time
from decimal import Decimal, ROUND_CEILING
from uuid import uuid4

import pytest

from dcex.ondo.client import Client

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to send a real Ondo order.",
    ),
]


@pytest.fixture
def client():
    instance = Client(preload_product_table=False)
    try:
        yield instance
    finally:
        instance.close()


def _result(response: object) -> object:
    assert isinstance(response, dict) and response.get("success") is True, response
    return response.get("result")


def _rows(response: object) -> list[dict]:
    result = _result(response)
    assert isinstance(result, list), response
    assert all(isinstance(row, dict) for row in result), response
    return result


def _order_id(value: object) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in ("orderID", "orderId", "id"):
        identifier = value.get(key)
        if isinstance(identifier, str | int) and str(identifier):
            return str(identifier)
    for nested in ("order", "result"):
        found = _order_id(value.get(nested))
        if found:
            return found
    return None


def _test_orders(client: Client, market: str, client_order_id: str) -> list[dict]:
    return [
        order
        for order in _rows(client.get_open_orders(market=market))
        if order.get("clientOrderId") == client_order_id
        and order.get("status") not in {"canceled", "cancelled", "filled", "expired", "rejected"}
    ]


def _cancel_test_orders(client: Client, market: str, client_order_id: str) -> None:
    for _ in range(4):
        orders = _test_orders(client, market, client_order_id)
        if not orders:
            return
        for order in orders:
            order_id = _order_id(order)
            assert order_id, f"Ondo test order has no cancellable ID: {order}"
            _result(client.cancel_order(order_id))
        time.sleep(0.5)
    assert not _test_orders(client, market, client_order_id), "Ondo test order remains open"


def test_post_only_limit_order_and_cancel(client: Client) -> None:
    """Use a capped BTC limit bid and never cancel or close pre-existing state."""
    if _rows(client.get_positions()) or _rows(client.get_open_orders()):
        pytest.skip("Ondo account must start without positions or open orders.")

    markets = _result(client.get_markets())
    assert isinstance(markets, dict)
    pairs = markets["perps"]["tradingPairs"]
    pair = next(p for p in pairs if p.get("market") == "BTC-USD.P" and not p.get("disabled"))
    market = pair["market"]
    depth = _result(client.get_depth(market, 5))
    assert isinstance(depth, dict) and depth["bids"]
    bid = Decimal(depth["bids"][0][0])
    tick = Decimal(pair["quoteIncrement"])
    size_increment = Decimal(pair["baseIncrement"])
    price = (bid * Decimal("0.95") // tick) * tick
    size_steps = (Decimal("10") / (price * size_increment)).to_integral_value(
        rounding=ROUND_CEILING
    )
    size = size_steps * size_increment
    assert Decimal("10") <= price * size <= Decimal("20")
    assert Decimal(_result(client.get_max_order_size(market))["percent25"]["maxBidBaseSize"]) >= size

    client_order_id = f"dcex-{uuid4().hex[:20]}"
    order_id = None
    try:
        placed = _result(
            client.place_order(
                market=market,
                side="buy",
                type="limit",
                price=str(price),
                size=str(size),
                timeInForce="GTC",
                postOnly=True,
                clientOrderId=client_order_id,
            )
        )
        order_id = _order_id(placed)
        if not order_id:
            for _ in range(4):
                orders = _test_orders(client, market, client_order_id)
                if orders:
                    order_id = _order_id(orders[0])
                    break
                time.sleep(0.5)
        assert order_id, f"Could not identify Ondo test order: {placed}"
        _result(client.cancel_order(order_id))
    finally:
        _cancel_test_orders(client, market, client_order_id)

    final_order = _result(client.get_order(order_id))
    assert isinstance(final_order, dict)
    filled_size = Decimal(str(final_order["filledSize"]))
    if filled_size > 0:
        _result(
            client.place_order(
                market=market,
                side="sell",
                type="market",
                size=str(filled_size),
                reduceOnly=True,
            )
        )
        assert not _rows(client.get_positions()), "Ondo unexpected fill did not close"
        pytest.fail("Ondo post-only order filled unexpectedly and was closed reduce-only.")
    assert final_order["status"] == "canceled", final_order
    assert not _rows(client.get_positions()), "Ondo test left a position"
