# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.okx.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
SPOT_SYMBOL = "BTC-USDT-SPOT"
SWAP_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("0.1")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real OKX order and transfer tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    )
    _cleanup(client_instance, Decimal("0"))
    try:
        yield client_instance
    finally:
        _cleanup(client_instance, Decimal("0"))


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


def _data(response: object) -> list[dict]:
    if not isinstance(response, dict):
        return []
    data = response.get("data")
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _assert_ok(response: object) -> dict:
    assert isinstance(response, dict)
    assert str(response.get("code", "0")) == "0", response
    for item in _data(response):
        assert str(item.get("sCode", "0")) == "0", response
    return response


def _order_id(response: object) -> str:
    items = _data(_assert_ok(response))
    assert items and items[0].get("ordId"), response
    return str(items[0]["ordId"])


def _client_id() -> str:
    return f"dcex{uuid.uuid4().hex[:20]}"


def _spot_available(client: Client, currency: str) -> Decimal:
    for account in _data(client.get_account_balance(ccy=[currency])):
        details = account.get("details")
        if not isinstance(details, list):
            continue
        for item in details:
            if isinstance(item, dict) and item.get("ccy") == currency:
                return _dec(item.get("availBal"))
    return Decimal("0")


def _funding_available(client: Client, currency: str) -> Decimal:
    for item in _data(client.get_balances(ccy=[currency])):
        if item.get("ccy") == currency:
            return _dec(item.get("availBal"))
    return Decimal("0")


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("okx", SPOT_SYMBOL)
    return (
        _dec(details["price_precision"], "0.1"),
        _dec(details["size_precision"], "0.00000001"),
        _dec(details["min_size"], "0.00001"),
        max(_dec(details["min_notional"], "1"), Decimal("1")),
    )


def _spot_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    books = _data(client.get_orderbook(product_symbol=SPOT_SYMBOL, sz="5"))
    assert books
    bids = books[0].get("bids", [])
    asks = books[0].get("asks", [])
    assert bids and asks
    return _dec(bids[0][0]), _dec(asks[0][0])


def _spot_post_only_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    best_bid, _ = _spot_orderbook_prices(client)
    price = _round_to_step(best_bid - tick, tick, ROUND_DOWN)
    size = _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP)
    return _fmt(max(size, min_size)), _fmt(price)


def _spot_price_below(client: Client, price: str, multiplier: Decimal) -> str:
    tick, _, _, _ = _spot_details(client)
    return _fmt(_round_to_step(Decimal(price) * multiplier, tick, ROUND_DOWN))


def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, best_ask = _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


def _spot_sell_size(client: Client, size: Decimal) -> str:
    _, step, _, _ = _spot_details(client)
    return _fmt(_round_to_step(size, step, ROUND_DOWN))


def _spot_market_quote(client: Client) -> Decimal:
    _, _, _, min_notional = _spot_details(client)
    return min_notional * Decimal("1.01")


def _open_orders(client: Client, product_symbol: str) -> list[dict]:
    return _data(client.get_order_list(product_symbol=product_symbol))


def _swap_position_size(client: Client) -> Decimal:
    return sum(
        (_dec(item.get("pos")) for item in _data(client.get_positions(product_symbol=SWAP_SYMBOL))),
        Decimal("0"),
    )


def _skip_if_existing_state(client: Client) -> None:
    _cleanup(client, Decimal("0"))


def _ensure_trading_usdt(client: Client, required: Decimal) -> Decimal:
    available = _spot_available(client, "USDT")
    if available >= required:
        return Decimal("0")
    needed = required - available
    if _funding_available(client, "USDT") < needed:
        pytest.fail("Insufficient OKX USDT for stateful trading tests.", pytrace=False)
    _assert_ok(
        client.funds_transfer(
            ccy="USDT",
            amt=_fmt(needed),
            from_account="FUND",
            to_account="TRADING",
        )
    )
    time.sleep(2)
    if _spot_available(client, "USDT") < required:
        pytest.fail("OKX trading USDT remains insufficient after transfer.", pytrace=False)
    return needed


def _return_to_funding(client: Client, transferred: Decimal) -> None:
    amount = min(transferred, _spot_available(client, "USDT"))
    if amount <= 0:
        return
    _assert_ok(
        client.funds_transfer(
            ccy="USDT",
            amt=_fmt(amount),
            from_account="TRADING",
            to_account="FUND",
        )
    )


def _wait_for_spot_delta(client: Client, before: Decimal) -> Decimal:
    for _ in range(8):
        delta = _spot_available(client, "BTC") - before
        if delta > 0:
            return delta
        time.sleep(1)
    return Decimal("0")


def _wait_for_swap_position(client: Client) -> Decimal:
    for _ in range(8):
        size = _swap_position_size(client)
        if size != 0:
            return size
        time.sleep(1)
    return Decimal("0")


def _is_order_no_longer_open(exc: FailedRequestError) -> bool:
    message = str(exc).lower()
    return (
        "51400" in message
        or "51503" in message
        or "does not exist" in message
        or "filled or canceled" in message
    )


def _is_rate_limited(exc: FailedRequestError) -> bool:
    message = str(exc).lower()
    return "50011" in message or "rate limit" in message


def _rate_limited_request(factory) -> object:
    last_error = None
    for attempt in range(4):
        try:
            return factory()
        except FailedRequestError as exc:
            if not _is_rate_limited(exc):
                raise
            last_error = exc
            time.sleep(5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def _is_empty_cancel_all_error(exc: FailedRequestError) -> bool:
    message = str(exc).lower()
    return "50000" in message and "body for post request cannot be empty" in message


def _skip_if_order_no_longer_open(exc: FailedRequestError) -> None:
    if _is_order_no_longer_open(exc):
        pytest.fail(f"OKX order was filled or canceled before amend/cancel: {exc}", pytrace=False)
    if _is_rate_limited(exc):
        pytest.fail(f"OKX rate limit reached during live order lifecycle: {exc}", pytrace=False)
    raise exc


def _cleanup_if_order_no_longer_open(
    client: Client,
    initial_btc: Decimal,
    exc: FailedRequestError,
) -> bool:
    if not _is_order_no_longer_open(exc):
        _skip_if_order_no_longer_open(exc)
    _cleanup(client, initial_btc)
    return True


def _order_id_or_skip(create_order) -> str:
    try:
        return _order_id(_rate_limited_request(create_order))
    except FailedRequestError as exc:
        _skip_if_order_no_longer_open(exc)


def _cancel_order(client: Client, order_id: str) -> None:
    try:
        _assert_ok(
            _rate_limited_request(
                lambda: client.cancel_order(product_symbol=SPOT_SYMBOL, ordId=order_id)
            )
        )
    except FailedRequestError as exc:
        if _is_order_no_longer_open(exc):
            return
        raise
    time.sleep(0.5)


def _cancel_all_orders(client: Client, product_symbol: str) -> None:
    try:
        _assert_ok(
            _rate_limited_request(lambda: client.cancel_all_orders(product_symbol=product_symbol))
        )
    except FailedRequestError as exc:
        if _is_empty_cancel_all_error(exc):
            return
        raise
    time.sleep(0.5)


def _cleanup(client: Client, initial_btc: Decimal) -> None:
    if _open_orders(client, SPOT_SYMBOL):
        _cancel_all_orders(client, SPOT_SYMBOL)
    if _open_orders(client, SWAP_SYMBOL):
        _cancel_all_orders(client, SWAP_SYMBOL)
    if _swap_position_size(client) != 0:
        _assert_ok(client.close_positions(product_symbol=SWAP_SYMBOL, mgnMode="cross"))
        time.sleep(2)
    _cleanup_spot_btc(client, initial_btc)

    if _open_orders(client, SPOT_SYMBOL) or _open_orders(client, SWAP_SYMBOL):
        pytest.fail("OKX still has open BTC orders after cleanup.", pytrace=False)
    if _swap_position_size(client) != 0:
        pytest.fail("OKX BTC-USDT swap position still exists after cleanup.", pytrace=False)
    _, step, _, _ = _spot_details(client)
    if _spot_available(client, "BTC") - initial_btc > step:
        pytest.fail("OKX BTC spot balance still exists after cleanup.", pytrace=False)


def _cleanup_spot_btc(client: Client, initial_btc: Decimal) -> None:
    _, step, min_size, min_notional = _spot_details(client)
    delta = _spot_available(client, "BTC") - initial_btc
    if delta <= step:
        return

    sell_size = Decimal(_spot_sell_size(client, delta))
    best_bid, _ = _spot_orderbook_prices(client)
    transferred = Decimal("0")
    try:
        if sell_size < min_size or sell_size * best_bid < min_notional:
            quote = _spot_market_quote(client)
            transferred += _ensure_trading_usdt(client, quote)
            _assert_ok(
                _rate_limited_request(
                    lambda: client.place_market_buy_order(SPOT_SYMBOL, "cash", _fmt(quote))
                )
            )
            time.sleep(2)
            sell_size = Decimal(
                _spot_sell_size(client, _spot_available(client, "BTC") - initial_btc)
            )

        if sell_size > 0:
            _assert_ok(
                _rate_limited_request(
                    lambda: client.place_market_sell_order(SPOT_SYMBOL, "cash", _fmt(sell_size))
                )
            )
            time.sleep(2)
    finally:
        _return_to_funding(client, transferred)


def test_funds_transfer_round_trip(client):
    funding = _funding_available(client, "USDT")
    trading = _spot_available(client, "USDT")
    if funding >= TRANSFER_AMOUNT:
        from_account, to_account = "FUND", "TRADING"
    elif trading >= TRANSFER_AMOUNT:
        from_account, to_account = "TRADING", "FUND"
    else:
        pytest.fail("Insufficient OKX USDT for transfer round-trip.", pytrace=False)

    response = _assert_ok(
        client.funds_transfer(
            ccy="USDT",
            amt=_fmt(TRANSFER_AMOUNT),
            from_account=from_account,
            to_account=to_account,
        )
    )
    transfer_id = str(_data(response)[0]["transId"])
    try:
        assert client.get_transfer_state(transId=transfer_id) is not None
    finally:
        time.sleep(1)
        _assert_ok(
            client.funds_transfer(
                ccy="USDT",
                amt=_fmt(TRANSFER_AMOUNT),
                from_account=to_account,
                to_account=from_account,
            )
        )


def test_spot_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    initial_btc = _spot_available(client, "BTC")
    transferred = Decimal("0")
    try:
        size, price = _spot_post_only_buy_params(client)
        transferred += _ensure_trading_usdt(client, Decimal(size) * Decimal(price) * Decimal("3"))

        order_id = None
        try:
            order_id = _order_id(
                client.place_order(
                    product_symbol=SPOT_SYMBOL,
                    tdMode="cash",
                    side="buy",
                    ordType="post_only",
                    sz=size,
                    px=price,
                    clOrdId=_client_id(),
                )
            )
            assert client.get_order(product_symbol=SPOT_SYMBOL, ordId=order_id) is not None
            amended_price = _spot_price_below(client, price, Decimal("0.97"))
            try:
                _assert_ok(
                    client.amend_order(
                        product_symbol=SPOT_SYMBOL,
                        ordId=order_id,
                        newPx=amended_price,
                    )
                )
            except FailedRequestError as exc:
                if _cleanup_if_order_no_longer_open(client, initial_btc, exc):
                    order_id = None
            else:
                _cancel_order(client, order_id)
                order_id = None
        finally:
            if order_id is not None:
                _cancel_order(client, order_id)

        exchange_symbol = client.ptm.get_exchange_symbol("okx", SPOT_SYMBOL)
        batch = _assert_ok(
            client.place_batch_orders(
                [
                    {
                        "instId": exchange_symbol,
                        "tdMode": "cash",
                        "side": "buy",
                        "ordType": "post_only",
                        "sz": size,
                        "px": _spot_price_below(client, price, Decimal("0.95")),
                        "clOrdId": _client_id(),
                    },
                    {
                        "instId": exchange_symbol,
                        "tdMode": "cash",
                        "side": "buy",
                        "ordType": "post_only",
                        "sz": size,
                        "px": _spot_price_below(client, price, Decimal("0.94")),
                        "clOrdId": _client_id(),
                    },
                ]
            )
        )
        batch_ids = [str(item["ordId"]) for item in _data(batch)]
        try:
            _assert_ok(
                client.amend_multiple_orders(
                    [
                        {
                            "instId": exchange_symbol,
                            "ordId": order_id,
                            "newPx": _spot_price_below(client, price, Decimal("0.93")),
                        }
                        for order_id in batch_ids
                    ]
                )
            )
        except FailedRequestError as exc:
            if _cleanup_if_order_no_longer_open(client, initial_btc, exc):
                batch_ids = []
        else:
            _assert_ok(
                client.cancel_batch_orders(
                    [{"instId": exchange_symbol, "ordId": order_id} for order_id in batch_ids]
                )
            )
            time.sleep(0.5)
            batch_ids = []
        finally:
            for order_id in batch_ids:
                with suppress(Exception):
                    _cancel_order(client, order_id)

        creators = (
            lambda: client.place_limit_order(SPOT_SYMBOL, "cash", "buy", size, price),
            lambda: client.place_limit_buy_order(SPOT_SYMBOL, "cash", size, price),
            lambda: client.place_post_only_limit_order(SPOT_SYMBOL, "cash", "buy", size, price),
            lambda: client.place_post_only_limit_buy_order(SPOT_SYMBOL, "cash", size, price),
        )
        for create_order in creators:
            order_id = None
            try:
                order_id = _order_id_or_skip(create_order)
                _cancel_order(client, order_id)
                order_id = None
            finally:
                if order_id is not None:
                    _cancel_order(client, order_id)

        order_id = _order_id_or_skip(
            lambda: client.place_limit_buy_order(SPOT_SYMBOL, "cash", size, price)
        )
        try:
            _cancel_all_orders(client, SPOT_SYMBOL)
            order_id = None
        finally:
            if order_id is not None:
                _cancel_order(client, order_id)

        quote = _spot_market_quote(client)
        transferred += _ensure_trading_usdt(client, quote)
        before_btc = _spot_available(client, "BTC")
        _assert_ok(client.place_market_buy_order(SPOT_SYMBOL, "cash", _fmt(quote)))
        bought = _wait_for_spot_delta(client, before_btc)
        assert bought > 0
        sell_size = _spot_sell_size(client, bought)

        sell_price = _spot_post_only_sell_price(client)
        for create_order in (
            lambda: client.place_limit_sell_order(SPOT_SYMBOL, "cash", sell_size, sell_price),
            lambda: client.place_post_only_limit_sell_order(
                SPOT_SYMBOL, "cash", sell_size, sell_price
            ),
        ):
            order_id = None
            try:
                order_id = _order_id_or_skip(create_order)
                _cancel_order(client, order_id)
                order_id = None
            finally:
                if order_id is not None:
                    _cancel_order(client, order_id)

        _assert_ok(client.place_market_sell_order(SPOT_SYMBOL, "cash", sell_size))
        time.sleep(2)

        before_btc = _spot_available(client, "BTC")
        _assert_ok(
            client.place_market_order(
                product_symbol=SPOT_SYMBOL,
                tdMode="cash",
                side="buy",
                sz=_fmt(quote),
            )
        )
        bought = _wait_for_spot_delta(client, before_btc)
        assert bought > 0
        _assert_ok(
            client.place_market_order(
                product_symbol=SPOT_SYMBOL,
                tdMode="cash",
                side="sell",
                sz=_spot_sell_size(client, bought),
            )
        )
        time.sleep(2)

        assert client.get_order_list(product_symbol=SPOT_SYMBOL) is not None
        assert client.get_orders_history(instType="SPOT", product_symbol=SPOT_SYMBOL) is not None
        assert (
            client.get_orders_history_archive(
                instType="SPOT",
                product_symbol=SPOT_SYMBOL,
            )
            is not None
        )
        assert client.get_fills(instType="SPOT", product_symbol=SPOT_SYMBOL) is not None
        assert client.get_fills_history(instType="SPOT", product_symbol=SPOT_SYMBOL) is not None
        assert client.get_account_rate_limit() is not None
    finally:
        _cleanup(client, initial_btc)
        _return_to_funding(client, transferred)


def test_swap_close_position_lifecycle(client):
    _skip_if_existing_state(client)
    initial_btc = _spot_available(client, "BTC")
    transferred = Decimal("0")
    try:
        details = client.ptm.get_trading_details("okx", SWAP_SYMBOL)
        size = _fmt(max(_dec(details["min_size"], "0.01"), Decimal("0.01")))
        transferred += _ensure_trading_usdt(client, Decimal("1"))
        _assert_ok(
            client.place_market_buy_order(
                product_symbol=SWAP_SYMBOL,
                tdMode="cross",
                sz=size,
            )
        )
        assert _wait_for_swap_position(client) != 0
        _assert_ok(client.close_positions(product_symbol=SWAP_SYMBOL, mgnMode="cross"))
        time.sleep(2)
        assert _swap_position_size(client) == 0
    finally:
        _cleanup(client, initial_btc)
        _return_to_funding(client, transferred)
