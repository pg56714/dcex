# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.binance.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("0.1")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Binance order and transfer tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
    )
    _cleanup_futures_test_state(client_instance)
    _return_spot_btc_delta(client_instance, Decimal("0"))
    try:
        yield client_instance
    finally:
        try:
            _return_spot_btc_delta(client_instance, Decimal("0"))
        finally:
            _cleanup_futures_test_state(client_instance)


def _filters(exchange_info: dict) -> dict[str, dict]:
    return {item["filterType"]: item for item in exchange_info["symbols"][0]["filters"]}


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    return (value / step).to_integral_value(rounding=rounding) * step


def _format_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _get_futures_algo_order_with_retry(client: Client, client_algo_id: str) -> dict:
    for attempt in range(8):
        try:
            return client.get_futures_algo_order(clientAlgoId=client_algo_id)
        except FailedRequestError as exc:
            if "-2013" not in str(exc) or attempt == 7:
                raise
            time.sleep(1)
    raise AssertionError("unreachable")


def _minimum_notional(filters: dict[str, dict], default: Decimal) -> Decimal:
    if "NOTIONAL" in filters:
        return Decimal(str(filters["NOTIONAL"].get("minNotional", default)))
    if "MIN_NOTIONAL" in filters:
        return Decimal(str(filters["MIN_NOTIONAL"].get("minNotional", default)))
    return default


def _symbol_exchange_info(client: Client, product_symbol: str, *, futures: bool) -> dict:
    exchange_info = (
        client.get_futures_exchange_info()
        if futures
        else client.get_spot_exchange_info(product_symbol=product_symbol)
    )
    if futures:
        symbol = client.ptm.get_exchange_symbol("binance", product_symbol)
        exchange_info["symbols"] = [
            item for item in exchange_info["symbols"] if item["symbol"] == symbol
        ]
    return exchange_info


def _step_size(client: Client, product_symbol: str, *, futures: bool) -> Decimal:
    return Decimal(
        _filters(_symbol_exchange_info(client, product_symbol, futures=futures))["LOT_SIZE"][
            "stepSize"
        ]
    )


def _tick_size(client: Client, product_symbol: str, *, futures: bool) -> Decimal:
    return Decimal(
        _filters(_symbol_exchange_info(client, product_symbol, futures=futures))["PRICE_FILTER"][
            "tickSize"
        ]
    )


def _spot_best_bid(client: Client, product_symbol: str) -> Decimal:
    book = client.get_spot_orderbook(product_symbol=product_symbol, limit=5)
    bids = book.get("bids", []) if isinstance(book, dict) else []
    if not bids:
        pytest.fail(f"{product_symbol} spot orderbook did not return bids.", pytrace=False)
    return Decimal(str(bids[0][0]))


def _spot_best_ask(client: Client, product_symbol: str) -> Decimal:
    book = client.get_spot_orderbook(product_symbol=product_symbol, limit=5)
    asks = book.get("asks", []) if isinstance(book, dict) else []
    if not asks:
        pytest.fail(f"{product_symbol} spot orderbook did not return asks.", pytrace=False)
    return Decimal(str(asks[0][0]))


def _safe_spot_market_quote(client: Client, product_symbol: str) -> Decimal:
    filters = _filters(_symbol_exchange_info(client, product_symbol, futures=False))
    lot_filter = filters["LOT_SIZE"]
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("10"))
    best_ask = _spot_best_ask(client, product_symbol)
    min_sell_qty = _round_to_step(
        max(min_qty, min_notional / best_ask) * Decimal("1.005"),
        step_size,
        ROUND_UP,
    )
    return (min_sell_qty + step_size) * best_ask * Decimal("1.01")


def _safe_buy_order_params(
    client: Client, product_symbol: str, *, futures: bool
) -> tuple[str, str]:
    filters = _filters(_symbol_exchange_info(client, product_symbol, futures=futures))
    price_filter = filters["PRICE_FILTER"]
    lot_filter = filters["LOT_SIZE"]
    tick_size = Decimal(price_filter["tickSize"])
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("10"))

    current_price = (
        Decimal(client.get_futures_ticker(product_symbol=product_symbol)["bidPrice"])
        if futures
        else _spot_best_bid(client, product_symbol)
    )
    price = _round_to_step(current_price * Decimal("0.95"), tick_size, ROUND_DOWN)
    required_notional = min_notional * Decimal("1.01")
    quantity = _round_to_step(required_notional / price, step_size, ROUND_UP)
    quantity = max(quantity, min_qty)

    return _format_decimal(quantity), _format_decimal(price)


def _cancel_order_if_present(client: Client, product_symbol: str, order_id: int) -> None:
    try:
        client.cancel_order(product_symbol=product_symbol, orderId=order_id)
    except FailedRequestError as exc:
        message = str(exc)
        if "-2011" in message or "Unknown order" in message:
            if client.get_open_orders(product_symbol=product_symbol):
                raise
            return
        raise


def _safe_market_quantity(client: Client, product_symbol: str) -> str:
    filters = _filters(_symbol_exchange_info(client, product_symbol, futures=True))
    lot_filter = filters["LOT_SIZE"]
    step_size = Decimal(lot_filter["stepSize"])
    min_qty = Decimal(lot_filter["minQty"])
    min_notional = _minimum_notional(filters, Decimal("100"))
    price = Decimal(client.get_futures_ticker(product_symbol=product_symbol)["askPrice"])
    required_notional = min_notional * Decimal("1.01")
    quantity = _round_to_step(required_notional / price, step_size, ROUND_UP)
    return _format_decimal(max(quantity, min_qty))


def _spot_free(client: Client, asset: str) -> Decimal:
    account = client.get_account_balance(market_type="spot")
    for balance in account["balances"]:
        if balance["asset"] == asset:
            return Decimal(balance["free"])
    return Decimal("0")


def _funding_free(client: Client, asset: str) -> Decimal:
    for balance in client.get_funding_wallet(asset=asset):
        if balance.get("asset") == asset:
            return Decimal(str(balance.get("free", "0")))
    return Decimal("0")


def _futures_available(client: Client, asset: str) -> Decimal:
    for balance in client.get_account_balance(market_type="swap"):
        if balance.get("asset") == asset:
            return Decimal(str(balance.get("availableBalance", "0")))
    return Decimal("0")


def _rows(payload: object, *keys: str) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return value
        value = payload.get("data")
        if isinstance(value, list):
            return value
    return []


def _ensure_balance(
    client: Client,
    required: Decimal,
    destination: str,
) -> tuple[Decimal, str | None]:
    if destination == "spot":
        destination_balance = _spot_free(client, "USDT")
        sources = (
            (_funding_free(client, "USDT"), "FUNDING_MAIN", "MAIN_FUNDING"),
            (_futures_available(client, "USDT"), "UMFUTURE_MAIN", "MAIN_UMFUTURE"),
        )
    else:
        destination_balance = _futures_available(client, "USDT")
        sources = (
            (_funding_free(client, "USDT"), "FUNDING_UMFUTURE", "UMFUTURE_FUNDING"),
            (_spot_free(client, "USDT"), "MAIN_UMFUTURE", "UMFUTURE_MAIN"),
        )

    if destination_balance >= required:
        return Decimal("0"), None

    needed = (required - destination_balance).quantize(Decimal("0.000001"), rounding=ROUND_UP)
    for source_balance, transfer_type, reverse_type in sources:
        if source_balance >= needed:
            client.create_universal_transfer(
                type_=transfer_type,
                asset="USDT",
                amount=_format_decimal(needed),
            )
            time.sleep(1)
            return needed, reverse_type
    pytest.fail(f"Insufficient Binance USDT for {destination} stateful tests.", pytrace=False)


def _return_transfer(client: Client, amount: Decimal, transfer_type: str | None) -> None:
    if amount <= 0 or transfer_type is None:
        return
    time.sleep(1)
    if transfer_type.startswith("MAIN_"):
        available = _spot_free(client, "USDT")
    elif transfer_type.startswith("UMFUTURE_"):
        available = _futures_available(client, "USDT")
    else:
        available = _funding_free(client, "USDT")
    return_amount = min(amount, available).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
    if return_amount <= 0:
        return
    client.create_universal_transfer(
        type_=transfer_type,
        asset="USDT",
        amount=_format_decimal(return_amount),
    )


def _futures_position_amt(client: Client, product_symbol: str) -> Decimal:
    positions = client.get_future_position(product_symbol=product_symbol)
    if not positions:
        return Decimal("0")
    return Decimal(positions[0]["positionAmt"])


def _close_futures_position(client: Client, product_symbol: str) -> None:
    for _ in range(3):
        amount = _futures_position_amt(client, product_symbol)
        if amount == 0:
            return
        client.place_market_order(
            product_symbol=product_symbol,
            side="SELL" if amount > 0 else "BUY",
            quantity=_format_decimal(abs(amount)),
            reduceOnly="true",
            newOrderRespType="RESULT",
        )
        for _ in range(10):
            time.sleep(1)
            if _futures_position_amt(client, product_symbol) == 0:
                return
    raise AssertionError(f"{product_symbol} futures position did not close.")


def _cleanup_futures_test_state(client: Client) -> None:
    if client.get_open_orders(product_symbol=FUTURES_SYMBOL):
        client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
    if _rows(client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL), "orders"):
        client.cancel_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL)
    _close_futures_position(client, FUTURES_SYMBOL)
    if client.get_open_orders(product_symbol=FUTURES_SYMBOL):
        pytest.fail("Binance futures still has open orders after cleanup.", pytrace=False)
    if _rows(client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL), "orders"):
        pytest.fail("Binance futures still has open algo orders after cleanup.", pytrace=False)
    if _futures_position_amt(client, FUTURES_SYMBOL) != 0:
        pytest.fail("Binance futures position still exists after cleanup.", pytrace=False)


def _return_spot_btc_delta(client: Client, btc_before: Decimal) -> None:
    filters = _filters(_symbol_exchange_info(client, SPOT_SYMBOL, futures=False))
    step_size = _step_size(client, SPOT_SYMBOL, futures=False)
    min_qty = Decimal(filters["LOT_SIZE"]["minQty"])
    min_notional = _minimum_notional(filters, Decimal("10"))
    for _ in range(3):
        remaining = _round_to_step(_spot_free(client, "BTC") - btc_before, step_size, ROUND_DOWN)
        if remaining <= 0:
            return
        best_bid = _spot_best_bid(client, SPOT_SYMBOL)
        transferred = Decimal("0")
        reverse_type = None
        try:
            if remaining < min_qty or remaining * best_bid < min_notional:
                quote_amount = _safe_spot_market_quote(client, SPOT_SYMBOL)
                transferred, reverse_type = _ensure_balance(client, quote_amount, "spot")
                client.place_order(
                    product_symbol=SPOT_SYMBOL,
                    side="BUY",
                    type_="MARKET",
                    quoteOrderQty=_format_decimal(quote_amount),
                    newOrderRespType="FULL",
                )
                time.sleep(1)
                remaining = _round_to_step(
                    _spot_free(client, "BTC") - btc_before,
                    step_size,
                    ROUND_DOWN,
                )

            if remaining <= 0:
                return
            client.place_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=_format_decimal(remaining),
                newOrderRespType="FULL",
            )
            time.sleep(1)
        finally:
            _return_transfer(client, transferred, reverse_type)
    remaining = _round_to_step(_spot_free(client, "BTC") - btc_before, step_size, ROUND_DOWN)
    assert remaining <= 0


def test_universal_transfer_round_trip(client):
    funding = _funding_free(client, "USDT")
    spot = _spot_free(client, "USDT")
    futures = _futures_available(client, "USDT")
    if funding >= TRANSFER_AMOUNT:
        forward, reverse = "FUNDING_MAIN", "MAIN_FUNDING"
    elif spot >= TRANSFER_AMOUNT:
        forward, reverse = "MAIN_FUNDING", "FUNDING_MAIN"
    elif futures >= TRANSFER_AMOUNT:
        forward, reverse = "UMFUTURE_MAIN", "MAIN_UMFUTURE"
    else:
        pytest.fail("Insufficient Binance USDT for universal transfer round-trip.", pytrace=False)

    response = client.create_universal_transfer(
        type_=forward,
        asset="USDT",
        amount=_format_decimal(TRANSFER_AMOUNT),
    )
    assert response.get("tranId")
    try:
        time.sleep(1)
        assert client.get_universal_transfer_history(type_=forward, size=1) is not None
    finally:
        client.create_universal_transfer(
            type_=reverse,
            asset="USDT",
            amount=_format_decimal(TRANSFER_AMOUNT),
        )


@pytest.mark.private
def test_spot_post_only_order_lifecycle(client):
    quantity, price = _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    btc_before = _spot_free(client, "BTC")
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) * Decimal("1.05"),
        "spot",
    )
    test_res = client.test_order(
        product_symbol=SPOT_SYMBOL,
        side="BUY",
        type_="LIMIT_MAKER",
        quantity=quantity,
        price=price,
    )
    assert test_res is not None

    try:
        creators = (
            lambda: client.place_limit_order(SPOT_SYMBOL, "BUY", quantity, price),
            lambda: client.place_limit_buy_order(SPOT_SYMBOL, quantity, price),
            lambda: client.place_post_only_limit_order(SPOT_SYMBOL, "BUY", quantity, price),
            lambda: client.place_post_only_limit_buy_order(SPOT_SYMBOL, quantity, price),
        )
        for create_order in creators:
            order = None
            try:
                order = create_order()
                order_id = int(order["orderId"])
                queried = client.get_order(product_symbol=SPOT_SYMBOL, orderId=order_id)
                assert queried["orderId"] == order_id
                assert isinstance(client.get_open_orders(product_symbol=SPOT_SYMBOL), list)
            finally:
                if order is not None:
                    _cancel_order_if_present(client, SPOT_SYMBOL, int(order["orderId"]))
    finally:
        _return_spot_btc_delta(client, btc_before)
        _return_transfer(client, transferred, reverse_type)

    assert isinstance(client.get_all_orders(product_symbol=SPOT_SYMBOL, limit=1), list)
    assert isinstance(client.get_account_trades(product_symbol=SPOT_SYMBOL, limit=1), list)


@pytest.mark.private
def test_spot_cancel_all_open_orders(client):
    if client.get_open_orders(product_symbol=SPOT_SYMBOL):
        client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)

    quantity, price = _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    btc_before = _spot_free(client, "BTC")
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) * Decimal("1.05"),
        "spot",
    )
    try:
        client.place_post_only_limit_buy_order(
            product_symbol=SPOT_SYMBOL,
            quantity=quantity,
            price=price,
        )
        client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)
        assert client.get_open_orders(product_symbol=SPOT_SYMBOL) == []
    finally:
        if client.get_open_orders(product_symbol=SPOT_SYMBOL):
            client.cancel_all_open_orders(product_symbol=SPOT_SYMBOL)
        _return_spot_btc_delta(client, btc_before)
        _return_transfer(client, transferred, reverse_type)


@pytest.mark.private
def test_spot_market_order_round_trip(client):
    quote_amount = _safe_spot_market_quote(client, SPOT_SYMBOL)
    transferred, reverse_type = _ensure_balance(
        client,
        quote_amount,
        "spot",
    )
    step_size = _step_size(client, SPOT_SYMBOL, futures=False)
    tick_size = _tick_size(client, SPOT_SYMBOL, futures=False)
    btc_before = _spot_free(client, "BTC")
    try:
        order = client.place_order(
            product_symbol=SPOT_SYMBOL,
            side="BUY",
            type_="MARKET",
            quoteOrderQty=_format_decimal(quote_amount),
            newOrderRespType="FULL",
        )
        assert order["status"] == "FILLED"

        acquired = _round_to_step(
            _spot_free(client, "BTC") - btc_before,
            step_size,
            ROUND_DOWN,
        )
        assert acquired > 0
        sell_price = _format_decimal(
            _round_to_step(
                Decimal(client.get_spot_price(product_symbol=SPOT_SYMBOL)["price"]) + tick_size,
                tick_size,
                ROUND_UP,
            )
        )
        for create_order in (
            lambda quantity: client.place_limit_sell_order(SPOT_SYMBOL, quantity, sell_price),
            lambda quantity: client.place_post_only_limit_sell_order(
                SPOT_SYMBOL, quantity, sell_price
            ),
        ):
            remaining = _round_to_step(
                _spot_free(client, "BTC") - btc_before,
                step_size,
                ROUND_DOWN,
            )
            if remaining <= 0:
                break
            sell_order = None
            try:
                sell_order = create_order(_format_decimal(remaining))
            finally:
                if sell_order is not None:
                    _cancel_order_if_present(client, SPOT_SYMBOL, int(sell_order["orderId"]))

        remaining = _round_to_step(
            _spot_free(client, "BTC") - btc_before,
            step_size,
            ROUND_DOWN,
        )
        if remaining > 0:
            sell = client.place_market_sell_order(
                product_symbol=SPOT_SYMBOL,
                quantity=_format_decimal(remaining),
                newOrderRespType="FULL",
            )
            assert sell["status"] == "FILLED"
    finally:
        _return_spot_btc_delta(client, btc_before)
        _return_transfer(client, transferred, reverse_type)


@pytest.mark.private
def test_futures_post_only_order_lifecycle(client):
    _cleanup_futures_test_state(client)
    quantity, price = _safe_buy_order_params(client, FUTURES_SYMBOL, futures=True)
    assert client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)["leverage"] == 20
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    test_res = client.test_order(
        product_symbol=FUTURES_SYMBOL,
        side="BUY",
        type_="LIMIT",
        quantity=quantity,
        price=price,
        timeInForce="GTX",
    )
    assert test_res is not None

    order = None
    try:
        try:
            order = client.place_post_only_limit_buy_order(
                product_symbol=FUTURES_SYMBOL,
                quantity=quantity,
                price=price,
            )
        except FailedRequestError as exc:
            if "insufficient" in str(exc).lower() or "-2019" in str(exc):
                pytest.fail(
                    f"Insufficient Binance futures margin for post-only order: {exc}",
                    pytrace=False,
                )
            raise
        order_id = int(order["orderId"])
        assert (
            client.get_order(product_symbol=FUTURES_SYMBOL, orderId=order_id)["orderId"] == order_id
        )
        assert isinstance(client.get_open_orders(product_symbol=FUTURES_SYMBOL), list)
        assert isinstance(client.get_all_open_orders(product_symbol=FUTURES_SYMBOL), list)
    finally:
        if order is not None:
            _cancel_order_if_present(client, FUTURES_SYMBOL, int(order["orderId"]))
        _cleanup_futures_test_state(client)
        _return_transfer(client, transferred, reverse_type)

    assert isinstance(client.get_all_orders(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(client.get_future_all_order(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(client.get_account_trades(product_symbol=FUTURES_SYMBOL, limit=1), list)
    assert isinstance(client.get_future_position(product_symbol=FUTURES_SYMBOL), list)


@pytest.mark.private
def test_futures_cancel_all_open_orders(client):
    _cleanup_futures_test_state(client)

    quantity, price = _safe_buy_order_params(client, FUTURES_SYMBOL, futures=True)
    assert client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)["leverage"] == 20
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(quantity) * Decimal(price) / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    try:
        client.place_post_only_limit_buy_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            price=price,
        )
        client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
        assert client.get_open_orders(product_symbol=FUTURES_SYMBOL) == []
    finally:
        if client.get_open_orders(product_symbol=FUTURES_SYMBOL):
            client.cancel_all_open_orders(product_symbol=FUTURES_SYMBOL)
        _cleanup_futures_test_state(client)
        _return_transfer(client, transferred, reverse_type)


@pytest.mark.private
def test_futures_market_long_round_trip(client):
    _cleanup_futures_test_state(client)

    quantity = _safe_market_quantity(client, FUTURES_SYMBOL)
    assert client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)["leverage"] == 20
    price = Decimal(client.get_futures_ticker(product_symbol=FUTURES_SYMBOL)["askPrice"])
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(quantity) * price / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    try:
        open_order = client.place_market_buy_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert open_order["status"] == "FILLED"
    finally:
        _close_futures_position(client, FUTURES_SYMBOL)
        _return_transfer(client, transferred, reverse_type)

    assert _futures_position_amt(client, FUTURES_SYMBOL) == 0


@pytest.mark.private
def test_futures_market_short_round_trip(client):
    _cleanup_futures_test_state(client)

    quantity = _safe_market_quantity(client, FUTURES_SYMBOL)
    assert client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)["leverage"] == 20
    price = Decimal(client.get_futures_ticker(product_symbol=FUTURES_SYMBOL)["bidPrice"])
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(quantity) * price / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    try:
        open_order = client.place_market_sell_order(
            product_symbol=FUTURES_SYMBOL,
            quantity=quantity,
            newOrderRespType="RESULT",
        )
        assert open_order["status"] == "FILLED"
    finally:
        _close_futures_position(client, FUTURES_SYMBOL)
        _return_transfer(client, transferred, reverse_type)

    assert _futures_position_amt(client, FUTURES_SYMBOL) == 0


@pytest.mark.private
def test_advanced_order_validation(client):
    spot_quantity, spot_price = _safe_buy_order_params(client, SPOT_SYMBOL, futures=False)
    spot_tick = _tick_size(client, SPOT_SYMBOL, futures=False)
    spot_stop = _format_decimal(
        _round_to_step(Decimal(spot_price) * Decimal("1.05"), spot_tick, ROUND_UP)
    )
    spot_transferred, spot_reverse = _ensure_balance(
        client,
        Decimal(spot_quantity) * Decimal(spot_stop) * Decimal("1.05"),
        "spot",
    )
    try:
        assert (
            client.test_order(
                product_symbol=SPOT_SYMBOL,
                side="BUY",
                type_="STOP_LOSS_LIMIT",
                quantity=spot_quantity,
                price=spot_stop,
                stopPrice=spot_stop,
                timeInForce="GTC",
            )
            is not None
        )
    finally:
        _return_transfer(client, spot_transferred, spot_reverse)

    futures_quantity = _safe_market_quantity(client, FUTURES_SYMBOL)
    futures_price = Decimal(client.get_futures_ticker(product_symbol=FUTURES_SYMBOL)["askPrice"])
    futures_tick = _tick_size(client, FUTURES_SYMBOL, futures=True)
    trigger_price = _format_decimal(
        _round_to_step(futures_price * Decimal("1.05"), futures_tick, ROUND_UP)
    )

    _cleanup_futures_test_state(client)
    assert client.set_leverage(product_symbol=FUTURES_SYMBOL, leverage=20)["leverage"] == 20
    transferred, reverse_type = _ensure_balance(
        client,
        Decimal(futures_quantity) * futures_price / Decimal("20") * Decimal("1.05"),
        "futures",
    )
    algo_order = None
    client_algo_id = f"dcx{int(time.time() * 1000)}"
    try:
        algo_order = client.place_futures_algo_order(
            product_symbol=FUTURES_SYMBOL,
            side="BUY",
            type_="STOP_MARKET",
            quantity=futures_quantity,
            triggerPrice=trigger_price,
            clientAlgoId=client_algo_id,
            newOrderRespType="ACK",
        )
        time.sleep(0.5)
        queried = _get_futures_algo_order_with_retry(client, client_algo_id)
        assert queried["clientAlgoId"] == client_algo_id
        assert isinstance(
            client.get_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL), list
        )
        client.cancel_futures_algo_order(clientAlgoId=client_algo_id)
        algo_order = None

        client_algo_id = f"dcx{int(time.time() * 1000)}all"
        algo_order = client.place_futures_algo_order(
            product_symbol=FUTURES_SYMBOL,
            side="BUY",
            type_="STOP_MARKET",
            quantity=futures_quantity,
            triggerPrice=trigger_price,
            clientAlgoId=client_algo_id,
            newOrderRespType="ACK",
        )
        time.sleep(0.5)
    finally:
        if algo_order is not None:
            client.cancel_all_open_futures_algo_orders(product_symbol=FUTURES_SYMBOL)
        _cleanup_futures_test_state(client)
        _return_transfer(client, transferred, reverse_type)

    assert isinstance(
        client.get_all_futures_algo_orders(product_symbol=FUTURES_SYMBOL, limit=1), list
    )
