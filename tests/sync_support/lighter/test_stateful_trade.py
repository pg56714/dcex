# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
from contextlib import suppress
from decimal import ROUND_CEILING, ROUND_DOWN, Decimal

import pytest
from dotenv import load_dotenv

from dcex.lighter.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

ACCOUNT_INDEX = os.getenv("LIGHTER_ACCOUNT_INDEX")
API_KEY_INDEX = os.getenv("LIGHTER_API_KEY_INDEX")
API_PRIVATE_KEY = os.getenv("LIGHTER_API_PRIVATE_KEY")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Lighter trade tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        account_index=int(ACCOUNT_INDEX or 0),
        api_key_index=int(API_KEY_INDEX or 0),
        api_private_key=API_PRIVATE_KEY,
        preload_product_table=False,
    )
    try:
        yield client_instance
    finally:
        client_instance.close()


def _assert_response(res) -> None:
    assert isinstance(res, dict)
    assert res.get("code", 200) == 200


def _market(client: Client, preferred_symbols: set[str] | None = None) -> dict:
    details = client.get_order_book_details()
    markets = details.get("order_book_details", [])
    preferred_symbols = preferred_symbols or {"ETH", "BTC"}
    preferred = [market for market in markets if market.get("symbol") in preferred_symbols]
    candidates = preferred or markets
    return next(market for market in candidates if market.get("status") == "active")


def _post_only_buy_order(market: dict) -> tuple[int, int, int]:
    price_decimals = int(market["price_decimals"])
    size_decimals = int(market["size_decimals"])
    last_price = Decimal(str(market["last_trade_price"]))
    price = (last_price * Decimal("0.8")).quantize(
        Decimal(1).scaleb(-price_decimals),
        rounding=ROUND_DOWN,
    )
    min_base = Decimal(str(market["min_base_amount"]))
    min_quote = Decimal(str(market["min_quote_amount"]))
    min_size = Decimal(1).scaleb(-size_decimals)
    base = max(min_base, min_quote / price).quantize(min_size, rounding=ROUND_CEILING)

    market_index = int(market["market_id"])
    base_amount = int(base * (Decimal(10) ** size_decimals))
    price_amount = int(price * (Decimal(10) ** price_decimals))
    return market_index, base_amount, price_amount


def _ioc_market_order(client: Client, market: dict) -> tuple[int, int, int, int]:
    market_index = int(market["market_id"])
    price_decimals = int(market["price_decimals"])
    size_decimals = int(market["size_decimals"])
    order_book = client.get_order_book_orders(market_id=market_index, limit=5)
    best_ask = Decimal(str(order_book["asks"][0]["price"]))
    best_bid = Decimal(str(order_book["bids"][0]["price"]))
    min_base = Decimal(str(market["min_base_amount"]))
    min_quote = Decimal(str(market["min_quote_amount"]))
    min_size = Decimal(1).scaleb(-size_decimals)
    base = max(min_base, min_quote / best_ask).quantize(min_size, rounding=ROUND_CEILING)
    price_step = Decimal(1).scaleb(-price_decimals)
    buy_price = (best_ask * Decimal("1.02")).quantize(price_step, rounding=ROUND_CEILING)
    sell_price = (best_bid * Decimal("0.98")).quantize(price_step, rounding=ROUND_DOWN)
    return (
        market_index,
        int(base * (Decimal(10) ** size_decimals)),
        int(buy_price * (Decimal(10) ** price_decimals)),
        int(sell_price * (Decimal(10) ** price_decimals)),
    )


def _assert_signed(result) -> None:
    tx_type, tx_info, tx_hash, error = result
    assert error is None
    assert tx_type is not None
    assert tx_info
    assert tx_hash


def _active_order_index(client: Client, market_index: int, client_order_index: int) -> int:
    for _ in range(10):
        active_orders = client.get_account_active_orders(market_id=market_index)
        for order in active_orders.get("orders", []):
            if int(order.get("client_order_index", -1)) == client_order_index:
                return int(order["order_index"])
        time.sleep(0.5)
    pytest.fail(f"Lighter active order not found for client_order_index={client_order_index}")


def _wait_for_trade_client_ids(
    client: Client, market_index: int, client_order_ids: set[int]
) -> None:
    account_index = int(ACCOUNT_INDEX or 0)
    pending = {str(client_order_id) for client_order_id in client_order_ids}
    for _ in range(12):
        res = client.get_trades(
            account_index=account_index,
            market_id=market_index,
            sort_by="timestamp",
            limit=20,
        )
        for trade in res.get("trades", []):
            pending.discard(str(trade.get("ask_client_id")))
            pending.discard(str(trade.get("bid_client_id")))
        if not pending:
            return
        time.sleep(0.5)
    pytest.fail(f"Lighter trades not found for client_order_ids={sorted(pending)}")


def test_signing_helpers(client):
    market = _market(client)
    market_index, base_amount, price = _post_only_buy_order(market)
    client_order_index = int(time.time() * 1000)

    next_nonce = int(client.get_next_nonce()["nonce"])
    _assert_signed(
        client.sign_create_order(
            market_index=market_index,
            client_order_index=client_order_index,
            base_amount=base_amount,
            price=price,
            is_ask=False,
            order_type=0,
            time_in_force=2,
            order_expiry=int(time.time() * 1000) + 600_000,
            nonce=next_nonce,
        )
    )
    _assert_signed(client.sign_cancel_order(market_index, order_index=1, nonce=next_nonce))
    _assert_signed(
        client.sign_modify_order(
            market_index,
            order_index=1,
            base_amount=base_amount,
            price=price,
            nonce=next_nonce,
        )
    )
    _assert_signed(
        client.sign_cancel_all_orders(
            time_in_force=0,
            timestamp_ms=0,
            nonce=next_nonce,
        )
    )
    _assert_signed(
        client.sign_update_leverage(
            market_index=market_index,
            fraction=1000,
            margin_mode=0,
            nonce=next_nonce,
        )
    )
    _assert_signed(
        client.sign_update_margin(
            market_index=market_index,
            usdc_amount=1,
            direction=1,
            nonce=next_nonce,
        )
    )


def test_post_only_order_lifecycle(client):
    market = _market(client)
    market_index, base_amount, price = _post_only_buy_order(market)
    client_order_index = int(time.time() * 1000)

    try:
        _assert_response(
            client.create_order(
                market_index=market_index,
                client_order_index=client_order_index,
                base_amount=base_amount,
                price=price,
                is_ask=False,
                order_type=0,
                time_in_force=2,
                order_expiry=int(time.time() * 1000) + 600_000,
            )
        )
    except FailedRequestError as exc:
        message = str(exc).lower()
        if any(term in message for term in ("insufficient", "balance", "collateral", "margin")):
            pytest.skip(f"Lighter account has insufficient collateral for order test: {exc}")
        raise
    finally:
        time.sleep(1)

    order_index = _active_order_index(client, market_index, client_order_index)
    _assert_response(client.cancel_order(market_index=market_index, order_index=order_index))


def test_ioc_market_fill_lifecycle(client):
    market = _market(client, preferred_symbols={"SOL", "ETH", "BTC"})
    market_index, base_amount, buy_price, sell_price = _ioc_market_order(client, market)
    client_order_index = int(time.time() * 1000)
    close_client_order_index = client_order_index + 1
    buy_sent = False
    sell_sent = False

    try:
        _assert_response(
            client.create_order(
                market_index=market_index,
                client_order_index=client_order_index,
                base_amount=base_amount,
                price=buy_price,
                is_ask=False,
                order_type=1,
                time_in_force=0,
                order_expiry=0,
            )
        )
        buy_sent = True
        time.sleep(2)
        _assert_response(
            client.create_order(
                market_index=market_index,
                client_order_index=close_client_order_index,
                base_amount=base_amount,
                price=sell_price,
                is_ask=True,
                order_type=1,
                time_in_force=0,
                reduce_only=True,
                order_expiry=0,
            )
        )
        sell_sent = True
    except FailedRequestError as exc:
        message = str(exc).lower()
        if any(term in message for term in ("insufficient", "balance", "collateral", "margin")):
            pytest.skip(f"Lighter account has insufficient collateral for fill test: {exc}")
        raise
    finally:
        if buy_sent and not sell_sent:
            with suppress(Exception):
                client.create_order(
                    market_index=market_index,
                    client_order_index=close_client_order_index,
                    base_amount=base_amount,
                    price=sell_price,
                    is_ask=True,
                    order_type=1,
                    time_in_force=0,
                    reduce_only=True,
                    order_expiry=0,
                )
        time.sleep(2)

    _wait_for_trade_client_ids(client, market_index, {client_order_index, close_client_order_index})
