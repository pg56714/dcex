# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.bybit.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
SWAP_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("0.1")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Bybit order and transfer tests.",
    ),
]


@pytest.fixture
def client():
    return Client(
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )


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


def _assert_ok(response: object) -> dict:
    assert isinstance(response, dict)
    assert str(response.get("retCode", "0")) == "0", response
    extension = response.get("retExtInfo")
    if isinstance(extension, dict):
        for item in extension.get("list", []):
            if isinstance(item, dict):
                assert str(item.get("code", "0")) == "0", response
    return response


def _result(response: object) -> dict:
    result = _assert_ok(response).get("result")
    return result if isinstance(result, dict) else {}


def _order_id(response: object) -> str:
    order_id = _result(response).get("orderId")
    assert order_id, response
    return str(order_id)


def _batch_order_ids(response: object) -> list[str]:
    items = _result(response).get("list", [])
    return [
        str(item["orderId"]) for item in items if isinstance(item, dict) and item.get("orderId")
    ]


def _wallet_available(client: Client, coin: str) -> Decimal:
    accounts = _result(client.get_wallet_balance()).get("list", [])
    for account in accounts:
        if not isinstance(account, dict):
            continue
        coins = account.get("coin", [])
        for item in coins:
            if isinstance(item, dict) and item.get("coin") == coin:
                for key in ("walletBalance", "availableToWithdraw", "equity"):
                    if item.get(key) not in (None, ""):
                        return _dec(item[key])
    return Decimal("0")


def _transferable_balance(client: Client, account_type: str, coin: str) -> Decimal:
    balance = _result(
        client.get_coin_balance(
            accountType=account_type,
            coin=coin,
        )
    ).get("balance", {})
    if not isinstance(balance, dict):
        return Decimal("0")
    for key in ("transferBalance", "walletBalance"):
        if balance.get(key) not in (None, ""):
            return _dec(balance[key])
    return Decimal("0")


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("bybit", SPOT_SYMBOL)
    return (
        _dec(details["price_precision"], "0.1"),
        _dec(details["size_precision"], "0.00000001"),
        _dec(details["min_size"], "0.00001"),
        max(_dec(details["min_notional"], "5"), Decimal("5")),
    )


def _spot_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    result = _result(client.get_orderbook(product_symbol=SPOT_SYMBOL, limit=5))
    bids = result.get("b", [])
    asks = result.get("a", [])
    assert bids and asks
    return _dec(bids[0][0]), _dec(asks[0][0])


def _spot_post_only_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    best_bid, _ = _spot_orderbook_prices(client)
    price = _round_to_step(best_bid * Decimal("0.50"), tick, ROUND_DOWN)
    quantity = _round_to_step(min_notional * Decimal("1.25") / price, step, ROUND_UP)
    return _fmt(max(quantity, min_size)), _fmt(price)


def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, best_ask = _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask * Decimal("1.50"), tick, ROUND_UP))


def _spot_sell_size(client: Client, size: Decimal) -> str:
    _, step, _, _ = _spot_details(client)
    return _fmt(_round_to_step(size, step, ROUND_DOWN))


def _spot_market_quote(client: Client) -> Decimal:
    _, _, _, min_notional = _spot_details(client)
    return max(min_notional * Decimal("1.25"), Decimal("5"))


def _open_orders(client: Client, product_symbol: str) -> list[dict]:
    items = _result(client.get_open_orders(product_symbol=product_symbol)).get("list", [])
    return [item for item in items if isinstance(item, dict)]


def _positions(client: Client) -> list[dict]:
    items = _result(client.get_positions(product_symbol=SWAP_SYMBOL)).get("list", [])
    return [item for item in items if isinstance(item, dict)]


def _skip_if_existing_state(client: Client) -> None:
    if _open_orders(client, SPOT_SYMBOL) or _open_orders(client, SWAP_SYMBOL):
        pytest.skip("Bybit already has open BTC orders; not touching unrelated orders.")
    if any(_dec(item.get("size")) != 0 for item in _positions(client)):
        pytest.skip("Bybit BTC-USDT swap already has a position; not changing exposure.")


def _wait_for_spot_delta(client: Client, before: Decimal) -> Decimal:
    for _ in range(8):
        delta = _wallet_available(client, "BTC") - before
        if delta > 0:
            return delta
        time.sleep(1)
    return Decimal("0")


def _cancel(client: Client, order_id: str) -> None:
    _assert_ok(client.cancel_order(product_symbol=SPOT_SYMBOL, orderId=order_id))


def _cleanup(client: Client, initial_btc: Decimal) -> None:
    with suppress(Exception):
        if _open_orders(client, SPOT_SYMBOL):
            _assert_ok(client.cancel_all_orders(product_symbol=SPOT_SYMBOL))
    with suppress(Exception):
        if _open_orders(client, SWAP_SYMBOL):
            _assert_ok(client.cancel_all_orders(product_symbol=SWAP_SYMBOL))
    with suppress(Exception):
        delta = _wallet_available(client, "BTC") - initial_btc
        sell_size = _spot_sell_size(client, delta)
        if Decimal(sell_size) > 0:
            _assert_ok(client.place_market_sell_order(SPOT_SYMBOL, sell_size))
            time.sleep(2)


def _accept_unchanged(call, codes: tuple[str, ...]) -> None:
    try:
        _assert_ok(call())
    except FailedRequestError as exc:
        if not any(code in exc.message for code in codes):
            raise


def test_account_settings_and_internal_transfer(client):
    account_info = _result(client.get_account_info())
    unified_status = str(account_info.get("unifiedMarginStatus", ""))
    if unified_status in {"1", "2"}:
        _assert_ok(client.upgrade_to_unified_trading_account())
        pytest.skip("Bybit unified account upgrade submitted; rerun after it completes.")
    else:
        assert unified_status

    margin_mode = str(account_info.get("marginMode") or "REGULAR_MARGIN")
    _accept_unchanged(
        lambda: client.set_margin_mode(margin_mode=margin_mode),
        ("110026",),
    )

    position_items = _positions(client)
    leverage = next(
        (
            str(item["leverage"])
            for item in position_items
            if item.get("leverage") not in (None, "")
        ),
        "2",
    )
    _accept_unchanged(
        lambda: client.set_leverage(product_symbol=SWAP_SYMBOL, leverage=leverage),
        ("110043",),
    )
    mode = 3 if any(str(item.get("positionIdx")) in {"1", "2"} for item in position_items) else 0
    _accept_unchanged(
        lambda: client.switch_position_mode(mode=mode, product_symbol=SWAP_SYMBOL),
        ("110025",),
    )

    deposit_account = os.getenv("BYBIT_DEPOSIT_ACCOUNT_TYPE", "FUND")
    _assert_ok(client.set_deposit_account(accountType=deposit_account))

    fund_balance = _transferable_balance(client, "FUND", "USDT")
    unified_balance = _transferable_balance(client, "UNIFIED", "USDT")
    if fund_balance >= TRANSFER_AMOUNT:
        from_account, to_account = "FUND", "UNIFIED"
    elif unified_balance >= TRANSFER_AMOUNT:
        from_account, to_account = "UNIFIED", "FUND"
    else:
        pytest.skip("Insufficient Bybit USDT for internal transfer round-trip.")

    _assert_ok(
        client.create_internal_transfer(
            coin="USDT",
            amount=_fmt(TRANSFER_AMOUNT),
            fromAccountType=from_account,
            toAccountType=to_account,
        )
    )
    try:
        time.sleep(1)
        assert client.get_internal_transfer_records(coin="USDT") is not None
    finally:
        _assert_ok(
            client.create_internal_transfer(
                coin="USDT",
                amount=_fmt(TRANSFER_AMOUNT),
                fromAccountType=to_account,
                toAccountType=from_account,
            )
        )


def test_spot_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    initial_btc = _wallet_available(client, "BTC")
    try:
        size, price = _spot_post_only_buy_params(client)
        required = Decimal(size) * Decimal(price) * Decimal("3")
        if _wallet_available(client, "USDT") < required:
            pytest.skip("Insufficient Bybit unified USDT for spot stateful orders.")

        order_id = None
        try:
            order_id = _order_id(
                client.place_order(
                    product_symbol=SPOT_SYMBOL,
                    side="Buy",
                    orderType="Limit",
                    qty=size,
                    price=price,
                    timeInForce="PostOnly",
                )
            )
            amended_price = _fmt(Decimal(price) * Decimal("0.99"))
            _assert_ok(
                client.amend_order(
                    product_symbol=SPOT_SYMBOL,
                    orderId=order_id,
                    price=amended_price,
                )
            )
            _cancel(client, order_id)
            order_id = None
        finally:
            if order_id is not None:
                _cancel(client, order_id)

        exchange_symbol = client.ptm.get_exchange_symbol("bybit", SPOT_SYMBOL)
        batch = _assert_ok(
            client.place_batch_order(
                category="spot",
                request=[
                    {
                        "symbol": exchange_symbol,
                        "side": "Buy",
                        "orderType": "Limit",
                        "qty": size,
                        "price": price,
                        "timeInForce": "PostOnly",
                    },
                    {
                        "symbol": exchange_symbol,
                        "side": "Buy",
                        "orderType": "Limit",
                        "qty": size,
                        "price": _fmt(Decimal(price) * Decimal("0.98")),
                        "timeInForce": "PostOnly",
                    },
                ],
            )
        )
        batch_ids = _batch_order_ids(batch)
        assert len(batch_ids) == 2
        try:
            _assert_ok(
                client.amend_batch_order(
                    category="spot",
                    request=[
                        {
                            "symbol": exchange_symbol,
                            "orderId": order_id,
                            "price": _fmt(Decimal(price) * Decimal("0.97")),
                        }
                        for order_id in batch_ids
                    ],
                )
            )
            _assert_ok(
                client.cancel_batch_orders(
                    category="spot",
                    request=[
                        {"symbol": exchange_symbol, "orderId": order_id} for order_id in batch_ids
                    ],
                )
            )
            batch_ids = []
        finally:
            for order_id in batch_ids:
                with suppress(Exception):
                    _cancel(client, order_id)

        creators = (
            lambda: client.place_limit_order(SPOT_SYMBOL, "Buy", size, price),
            lambda: client.place_limit_buy_order(SPOT_SYMBOL, size, price),
            lambda: client.place_post_only_limit_order(SPOT_SYMBOL, "Buy", size, price),
            lambda: client.place_post_only_limit_buy_order(SPOT_SYMBOL, size, price),
        )
        for create_order in creators:
            order_id = None
            try:
                order_id = _order_id(create_order())
                _cancel(client, order_id)
                order_id = None
            finally:
                if order_id is not None:
                    _cancel(client, order_id)

        order_id = _order_id(client.place_limit_buy_order(SPOT_SYMBOL, size, price))
        try:
            _assert_ok(client.cancel_all_orders(product_symbol=SPOT_SYMBOL))
            order_id = None
        finally:
            if order_id is not None:
                _cancel(client, order_id)

        quote = _spot_market_quote(client)
        if _wallet_available(client, "USDT") < quote:
            pytest.skip("Insufficient Bybit unified USDT for spot market round-trip.")
        before_btc = _wallet_available(client, "BTC")
        _assert_ok(client.place_market_buy_order(SPOT_SYMBOL, _fmt(quote)))
        bought = _wait_for_spot_delta(client, before_btc)
        assert bought > 0
        sell_size = _spot_sell_size(client, bought)
        sell_price = _spot_post_only_sell_price(client)

        for create_order in (
            lambda: client.place_limit_sell_order(SPOT_SYMBOL, sell_size, sell_price),
            lambda: client.place_post_only_limit_sell_order(SPOT_SYMBOL, sell_size, sell_price),
        ):
            order_id = None
            try:
                order_id = _order_id(create_order())
                _cancel(client, order_id)
                order_id = None
            finally:
                if order_id is not None:
                    _cancel(client, order_id)

        _assert_ok(client.place_market_sell_order(SPOT_SYMBOL, sell_size))
        time.sleep(2)

        before_btc = _wallet_available(client, "BTC")
        _assert_ok(client.place_market_order(SPOT_SYMBOL, "Buy", _fmt(quote)))
        bought = _wait_for_spot_delta(client, before_btc)
        assert bought > 0
        _assert_ok(
            client.place_market_order(
                SPOT_SYMBOL,
                "Sell",
                _spot_sell_size(client, bought),
            )
        )
        time.sleep(2)

        assert client.get_open_orders(product_symbol=SPOT_SYMBOL) is not None
        assert client.get_order_history(product_symbol=SPOT_SYMBOL) is not None
        assert client.get_execution_list(product_symbol=SPOT_SYMBOL) is not None
        assert client.get_borrow_quota(product_symbol=SPOT_SYMBOL, side="Buy") is not None
        assert client.get_vip_margin_data(currency="USDT") is not None
        assert client.get_collateral(currency="USDT") is not None
        assert client.get_historical_interest_rate(currency="USDT") is not None
        assert client.get_status_and_leverage() is not None
    finally:
        _cleanup(client, initial_btc)
