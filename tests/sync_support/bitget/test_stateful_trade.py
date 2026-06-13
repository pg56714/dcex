# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os
import time
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.bitget.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")
SPOT_SYMBOL = "BTC-USDT-SPOT"
SWAP_SYMBOL = "BTC-USDT-SWAP"
EXCHANGE_SYMBOL = "BTCUSDT"
SPOT_TEST_NOTIONAL = Decimal("5.8")
FUTURES_TRANSFER_AMOUNT = Decimal("2")
FUTURES_SIZE = Decimal("0.0001")
IS_UTA: bool | None = None

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Bitget order and transfer tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(
        api_key=BITGET_API_KEY,
        api_secret=BITGET_API_SECRET,
        passphrase=BITGET_PASSPHRASE,
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


def _client_oid() -> str:
    return f"dcex{uuid.uuid4().hex[:20]}"


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _assert_ok(response):
    assert isinstance(response, dict)
    assert response["code"] == "00000", response
    assert "data" in response
    return response


def _skip_if_unified_account_error(exc: FailedRequestError) -> None:
    if "40085" in str(exc) or "Unified Account mode" in str(exc):
        pytest.skip(
            "Bitget account is in Unified Account mode; Classic Account API is unsupported."
        )


def _is_uta(client: Client) -> bool:
    global IS_UTA
    if IS_UTA is None:
        try:
            data = _assert_ok(client.get_uta_account_info()).get("data", {})
        except FailedRequestError:
            IS_UTA = False
        else:
            permissions = data.get("permissions", []) if isinstance(data, dict) else []
            IS_UTA = "uta_trade" in permissions or "uta_mgt" in permissions
    return IS_UTA


def _items(response: object) -> list[dict]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    if isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            for key in ("orderList", "orders", "fills", "list", "assets"):
                if isinstance(data.get(key), list):
                    return [item for item in data[key] if isinstance(item, dict)]
    return []


def _spot_available(client: Client, coin: str) -> Decimal:
    if _is_uta(client):
        for item in _items(_assert_ok(client.get_uta_account_assets())):
            if item.get("coin") == coin:
                return _dec(item.get("available"))
        return Decimal("0")
    for item in _items(_assert_ok(client.get_spot_account_assets(coin=coin))):
        if item.get("coin") == coin:
            return _dec(item.get("available"))
    return Decimal("0")


def _futures_available(client: Client) -> Decimal:
    if _is_uta(client):
        return _spot_available(client, "USDT")
    for item in _items(_assert_ok(client.get_futures_accounts())):
        if item.get("marginCoin") == "USDT":
            return _dec(item.get("available"))
    return Decimal("0")


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("bitget", SPOT_SYMBOL)
    return (
        _dec(details.get("price_precision"), "0.01"),
        _dec(details.get("size_precision"), "0.000001"),
        _dec(details.get("min_size"), "0.000001"),
        max(_dec(details.get("min_notional"), "5"), Decimal("5")),
    )


def _spot_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _assert_ok(client.get_spot_orderbook(SPOT_SYMBOL, limit=5))["data"]
    return _dec(data["bids"][0][0]), _dec(data["asks"][0][0])


def _spot_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    bid, _ = _spot_prices(client)
    price = _round_to_step(bid * Decimal("0.98"), tick, ROUND_DOWN)
    size = max(
        _round_to_step((min_notional * Decimal("1.12")) / price, step, ROUND_UP),
        min_size,
    )
    return _fmt(size), _fmt(price)


def _spot_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, ask = _spot_prices(client)
    return _fmt(_round_to_step(ask * Decimal("1.02"), tick, ROUND_UP))


def _spot_sell_size(client: Client, amount: Decimal) -> Decimal:
    _, step, _, _ = _spot_details(client)
    return _round_to_step(amount, step, ROUND_DOWN)


def _futures_details(client: Client) -> tuple[Decimal, Decimal]:
    details = client.ptm.get_trading_details("bitget", SWAP_SYMBOL)
    return _dec(details.get("price_precision"), "0.1"), _dec(details.get("min_size"), "0.0001")


def _futures_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _assert_ok(client.get_futures_orderbook(SWAP_SYMBOL, limit=5))["data"]
    return _dec(data["bids"][0][0]), _dec(data["asks"][0][0])


def _futures_buy_params(client: Client) -> tuple[str, str]:
    tick, min_size = _futures_details(client)
    bid, _ = _futures_prices(client)
    price = _round_to_step(bid * Decimal("0.98"), tick, ROUND_DOWN)
    return _fmt(max(FUTURES_SIZE, min_size)), _fmt(price)


def _futures_sell_price(client: Client) -> str:
    tick, _ = _futures_details(client)
    _, ask = _futures_prices(client)
    return _fmt(_round_to_step(ask * Decimal("1.02"), tick, ROUND_UP))


def _order_id(response) -> str:
    data = _assert_ok(response)["data"]
    if isinstance(data, dict):
        for key in ("orderId", "order_id", "id"):
            if data.get(key):
                return str(data[key])
    raise AssertionError(f"Bitget order response has no order id: {response}")


def _batch_order_id(response) -> str:
    data = _assert_ok(response)["data"]
    if isinstance(data, list):
        success = data
    else:
        success = data.get("successList", []) if isinstance(data, dict) else []
    assert success, response
    return str(success[0]["orderId"])


def _spot_open_orders(client: Client) -> list[dict]:
    if _is_uta(client):
        return _items(_assert_ok(client.get_uta_open_orders("SPOT", SPOT_SYMBOL, limit=20)))
    try:
        return _items(_assert_ok(client.get_spot_open_orders(SPOT_SYMBOL, limit=20)))
    except FailedRequestError as exc:
        _skip_if_unified_account_error(exc)
        raise


def _futures_open_orders(client: Client) -> list[dict]:
    if _is_uta(client):
        return _items(_assert_ok(client.get_uta_open_orders("USDT-FUTURES", SWAP_SYMBOL, limit=20)))
    return _items(_assert_ok(client.get_futures_open_orders(SWAP_SYMBOL, limit=20)))


def _futures_positions(client: Client) -> list[dict]:
    if _is_uta(client):
        return [
            item
            for item in _items(_assert_ok(client.get_uta_positions("USDT-FUTURES", SWAP_SYMBOL)))
            if item.get("symbol") == EXCHANGE_SYMBOL
        ]
    return [
        item
        for item in _items(_assert_ok(client.get_futures_positions(marginCoin="USDT")))
        if item.get("symbol") == EXCHANGE_SYMBOL
    ]


def _futures_position_size(client: Client) -> Decimal:
    size = Decimal("0")
    for position in _futures_positions(client):
        total = _dec(position.get("total"))
        if total == 0:
            continue
        hold_side = str(position.get("holdSide") or position.get("posSide") or "").lower()
        size += -total if hold_side == "short" else total
    return size


def _skip_if_existing_state(client: Client) -> None:
    if _spot_open_orders(client):
        pytest.skip("Bitget spot already has BTCUSDT open orders; not touching unrelated orders.")
    if _futures_open_orders(client):
        pytest.skip(
            "Bitget futures already has BTCUSDT open orders; not touching unrelated orders."
        )
    if _futures_position_size(client) != 0:
        pytest.skip("Bitget futures already has a BTCUSDT position; not changing exposure.")


def _ensure_spot_usdt(client: Client, amount: Decimal) -> None:
    if _spot_available(client, "USDT") < amount:
        pytest.skip("Insufficient Bitget spot USDT for stateful test.")


def _transfer(client: Client, amount: Decimal, from_type: str, to_type: str) -> None:
    _assert_ok(
        client.transfer(
            coin="USDT",
            amount=_fmt(amount),
            fromType=from_type,
            toType=to_type,
            clientOid=_client_oid(),
        )
    )
    time.sleep(2)


def _ensure_futures_margin(client: Client, amount: Decimal = FUTURES_TRANSFER_AMOUNT) -> Decimal:
    if _is_uta(client):
        if _futures_available(client) < Decimal("1"):
            pytest.skip("Insufficient Bitget UTA USDT for futures stateful test.")
        return Decimal("0")
    if _futures_available(client) >= Decimal("1"):
        return Decimal("0")
    _ensure_spot_usdt(client, amount)
    _transfer(client, amount, "spot", "usdt_futures")
    if _futures_available(client) <= 0:
        pytest.skip("Bitget futures USDT remains unavailable after transfer.")
    return amount


def _return_futures_margin(client: Client, amount: Decimal) -> None:
    if _is_uta(client):
        return
    if amount <= 0:
        return
    transfer_amount = min(amount, _futures_available(client)).quantize(
        Decimal("0.000001"),
        rounding=ROUND_DOWN,
    )
    if transfer_amount > 0:
        _transfer(client, transfer_amount, "usdt_futures", "spot")


def _cancel_spot(client: Client, order_id: str) -> None:
    if _is_uta(client):
        _assert_ok(client.cancel_uta_order(orderId=order_id, category="SPOT"))
        time.sleep(1)
        return
    _assert_ok(client.cancel_spot_order(SPOT_SYMBOL, orderId=order_id))
    time.sleep(1)


def _cancel_futures(client: Client, order_id: str) -> None:
    if _is_uta(client):
        _assert_ok(client.cancel_uta_order(orderId=order_id, category="USDT-FUTURES"))
        time.sleep(1)
        return
    _assert_ok(client.cancel_futures_order(SWAP_SYMBOL, orderId=order_id))
    time.sleep(1)


def _place_spot_limit(
    client: Client,
    side: str,
    size: str,
    price: str,
    force: str = "gtc",
) -> dict:
    if _is_uta(client):
        return client.place_uta_order(
            "SPOT",
            SPOT_SYMBOL,
            side,
            "limit",
            size,
            price=price,
            timeInForce=force,
            clientOid=_client_oid(),
        )
    return client.place_spot_limit_order(SPOT_SYMBOL, side, size, price, force)


def _place_spot_market(client: Client, side: str, size: str) -> dict:
    if _is_uta(client):
        return client.place_uta_order(
            "SPOT",
            SPOT_SYMBOL,
            side,
            "market",
            size,
            clientOid=_client_oid(),
        )
    return client.place_spot_market_order(SPOT_SYMBOL, side, size)


def _place_spot_batch(client: Client, side: str, size: str, price: str) -> dict:
    if _is_uta(client):
        return client.place_uta_batch_orders(
            [
                {
                    "category": "SPOT",
                    "symbol": EXCHANGE_SYMBOL,
                    "side": side,
                    "orderType": "limit",
                    "timeInForce": "post_only",
                    "price": price,
                    "qty": size,
                    "clientOid": _client_oid(),
                }
            ]
        )
    return client.place_spot_batch_orders(
        [
            {
                "side": side,
                "orderType": "limit",
                "force": "post_only",
                "price": price,
                "size": size,
                "clientOid": _client_oid(),
            }
        ],
        product_symbol=SPOT_SYMBOL,
    )


def _cancel_spot_batch(client: Client, order_id: str) -> dict:
    if _is_uta(client):
        return client.cancel_uta_batch_orders(
            [{"orderId": order_id, "category": "SPOT", "symbol": EXCHANGE_SYMBOL}]
        )
    return client.cancel_spot_batch_orders([{"orderId": order_id}], SPOT_SYMBOL)


def _get_spot_order(client: Client, order_id: str) -> dict:
    if _is_uta(client):
        return client.get_uta_order(orderId=order_id)
    return client.get_spot_order(orderId=order_id)


def _get_spot_history_orders(client: Client) -> dict:
    if _is_uta(client):
        return client.get_uta_history_orders("SPOT", SPOT_SYMBOL, limit=20)
    return client.get_spot_history_orders(SPOT_SYMBOL, limit=20)


def _get_spot_fills(client: Client) -> dict:
    if _is_uta(client):
        return client.get_uta_fills("SPOT", limit=20)
    return client.get_spot_fills(SPOT_SYMBOL, limit=20)


def _place_futures_limit(
    client: Client,
    side: str,
    size: str,
    price: str,
    force: str = "gtc",
) -> dict:
    if _is_uta(client):
        return client.place_uta_order(
            "USDT-FUTURES",
            SWAP_SYMBOL,
            side,
            "limit",
            size,
            price=price,
            timeInForce=force,
            clientOid=_client_oid(),
            marginMode="crossed",
        )
    return client.place_futures_limit_order(SWAP_SYMBOL, side, size, price, force)


def _place_futures_market(
    client: Client,
    side: str,
    size: str,
    reduce_only: str | None = None,
) -> dict:
    if _is_uta(client):
        reduce_only_value = reduce_only.lower() if reduce_only is not None else None
        return client.place_uta_order(
            "USDT-FUTURES",
            SWAP_SYMBOL,
            side,
            "market",
            size,
            clientOid=_client_oid(),
            reduceOnly=reduce_only_value,
            marginMode="crossed",
        )
    classic_reduce_only = reduce_only.upper() if reduce_only is not None else None
    return client.place_futures_market_order(
        SWAP_SYMBOL,
        side,
        size,
        reduceOnly=classic_reduce_only,
    )


def _place_futures_batch(client: Client, side: str, size: str, price: str) -> dict:
    if _is_uta(client):
        return client.place_uta_batch_orders(
            [
                {
                    "category": "USDT-FUTURES",
                    "symbol": EXCHANGE_SYMBOL,
                    "qty": size,
                    "price": price,
                    "side": side,
                    "orderType": "limit",
                    "timeInForce": "post_only",
                    "clientOid": _client_oid(),
                }
            ]
        )
    return client.place_futures_batch_orders(
        [
            {
                "symbol": EXCHANGE_SYMBOL,
                "marginMode": "crossed",
                "marginCoin": "USDT",
                "size": size,
                "price": price,
                "side": side,
                "orderType": "limit",
                "force": "post_only",
                "clientOid": _client_oid(),
            }
        ],
        product_symbol=SWAP_SYMBOL,
    )


def _cancel_futures_batch(client: Client, order_id: str) -> dict:
    if _is_uta(client):
        return client.cancel_uta_batch_orders(
            [{"orderId": order_id, "category": "USDT-FUTURES", "symbol": EXCHANGE_SYMBOL}]
        )
    return client.cancel_futures_batch_orders(SWAP_SYMBOL, [{"orderId": order_id}])


def _get_futures_order(client: Client, order_id: str) -> dict:
    if _is_uta(client):
        return client.get_uta_order(orderId=order_id)
    return client.get_futures_order(SWAP_SYMBOL, orderId=order_id)


def _get_futures_history_orders(client: Client) -> dict:
    if _is_uta(client):
        return client.get_uta_history_orders("USDT-FUTURES", SWAP_SYMBOL, limit=20)
    return client.get_futures_history_orders(SWAP_SYMBOL, limit=20)


def _get_futures_fills(client: Client) -> dict:
    if _is_uta(client):
        return client.get_uta_fills("USDT-FUTURES", limit=20)
    return client.get_futures_fills(SWAP_SYMBOL, limit=20)


def _cleanup_spot_btc(client: Client, initial_btc: Decimal) -> None:
    extra = _spot_sell_size(client, _spot_available(client, "BTC") - initial_btc)
    _, _, _, min_notional = _spot_details(client)
    bid, _ = _spot_prices(client)
    if extra > 0 and extra * bid >= min_notional:
        _assert_ok(_place_spot_market(client, "sell", _fmt(extra)))
        time.sleep(2)


def _cleanup_futures(client: Client) -> None:
    size = _futures_position_size(client)
    if size > 0:
        _assert_ok(_place_futures_market(client, "sell", _fmt(abs(size)), "yes"))
    elif size < 0:
        _assert_ok(_place_futures_market(client, "buy", _fmt(abs(size)), "yes"))
    time.sleep(2)


def _safe_setting_call(call) -> None:
    try:
        _assert_ok(call())
    except FailedRequestError as exc:
        message = str(exc).lower()
        if any(token in message for token in ("no need", "already", "same")):
            return
        raise


def test_transfer_round_trip(client):
    if _is_uta(client):
        pytest.skip("Bitget UTA uses shared margin; spot-to-futures transfer is not applicable.")
    _skip_if_existing_state(client)
    _ensure_spot_usdt(client, Decimal("1"))
    _transfer(client, Decimal("1"), "spot", "usdt_futures")
    _transfer(client, Decimal("1"), "usdt_futures", "spot")
    _assert_ok(client.get_transfer_records(coin="USDT", limit=20))


def test_spot_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    initial_btc = _spot_available(client, "BTC")
    _ensure_spot_usdt(client, SPOT_TEST_NOTIONAL)

    try:
        size, price = _spot_buy_params(client)
        if _is_uta(client):
            creators = (
                lambda: _place_spot_limit(client, "buy", size, price),
                lambda: _place_spot_limit(client, "buy", size, price, "post_only"),
            )
        else:
            creators = (
                lambda: client.place_spot_limit_order(SPOT_SYMBOL, "buy", size, price),
                lambda: client.place_spot_limit_buy_order(SPOT_SYMBOL, size, price),
                lambda: client.place_spot_post_only_limit_order(SPOT_SYMBOL, "buy", size, price),
                lambda: client.place_spot_post_only_limit_buy_order(SPOT_SYMBOL, size, price),
            )
        for create_order in creators:
            order_id = None
            try:
                order_id = _order_id(create_order())
                _assert_ok(_get_spot_order(client, order_id))
            finally:
                if order_id is not None:
                    _cancel_spot(client, order_id)

        order_id = _batch_order_id(_place_spot_batch(client, "buy", size, price))
        _assert_ok(_cancel_spot_batch(client, order_id))
        time.sleep(1)

        before_btc = _spot_available(client, "BTC")
        _assert_ok(_place_spot_market(client, "buy", _fmt(SPOT_TEST_NOTIONAL)))
        time.sleep(2)
        acquired = _spot_sell_size(client, _spot_available(client, "BTC") - before_btc)
        assert acquired > 0

        sell_price = _spot_sell_price(client)
        if _is_uta(client):
            sell_creators = (
                lambda: _place_spot_limit(client, "sell", _fmt(acquired), sell_price),
                lambda: _place_spot_limit(client, "sell", _fmt(acquired), sell_price, "post_only"),
            )
        else:
            sell_creators = (
                lambda: client.place_spot_limit_sell_order(SPOT_SYMBOL, _fmt(acquired), sell_price),
                lambda: client.place_spot_post_only_limit_sell_order(
                    SPOT_SYMBOL,
                    _fmt(acquired),
                    sell_price,
                ),
            )
        for create_sell in sell_creators:
            order_id = None
            try:
                order_id = _order_id(create_sell())
                _assert_ok(_get_spot_order(client, order_id))
            finally:
                if order_id is not None:
                    _cancel_spot(client, order_id)

        _assert_ok(_place_spot_market(client, "sell", _fmt(acquired)))
        time.sleep(2)

        before_btc = _spot_available(client, "BTC")
        _assert_ok(_place_spot_market(client, "buy", _fmt(SPOT_TEST_NOTIONAL)))
        time.sleep(2)
        acquired = _spot_sell_size(client, _spot_available(client, "BTC") - before_btc)
        assert acquired > 0
        _assert_ok(_place_spot_market(client, "sell", _fmt(acquired)))
        time.sleep(2)

        _assert_ok(_get_spot_history_orders(client))
        _assert_ok(_get_spot_fills(client))
    finally:
        with suppress(Exception):
            _cleanup_spot_btc(client, initial_btc)


def test_futures_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    transferred = _ensure_futures_margin(client)
    try:
        if _is_uta(client):
            _safe_setting_call(lambda: client.set_uta_hold_mode("one_way_mode"))
            _assert_ok(client.set_uta_leverage("USDT-FUTURES", "50", SWAP_SYMBOL))
        else:
            _safe_setting_call(lambda: client.set_futures_position_mode("one_way_mode"))
            _safe_setting_call(lambda: client.set_futures_margin_mode(SWAP_SYMBOL, "crossed"))
            _assert_ok(client.set_futures_leverage(SWAP_SYMBOL, "50"))

        size, price = _futures_buy_params(client)
        if _is_uta(client):
            creators = (
                lambda: _place_futures_limit(client, "buy", size, price),
                lambda: _place_futures_limit(client, "buy", size, price, "post_only"),
            )
        else:
            creators = (
                lambda: client.place_futures_limit_order(SWAP_SYMBOL, "buy", size, price),
                lambda: client.place_futures_limit_buy_order(SWAP_SYMBOL, size, price),
                lambda: client.place_futures_post_only_limit_order(SWAP_SYMBOL, "buy", size, price),
                lambda: client.place_futures_post_only_limit_buy_order(SWAP_SYMBOL, size, price),
            )
        for create_order in creators:
            order_id = None
            try:
                order_id = _order_id(create_order())
                _assert_ok(_get_futures_order(client, order_id))
            finally:
                if order_id is not None:
                    _cancel_futures(client, order_id)

        sell_price = _futures_sell_price(client)
        if _is_uta(client):
            sell_creators = (
                lambda: _place_futures_limit(client, "sell", size, sell_price),
                lambda: _place_futures_limit(client, "sell", size, sell_price, "post_only"),
            )
        else:
            sell_creators = (
                lambda: client.place_futures_limit_sell_order(SWAP_SYMBOL, size, sell_price),
                lambda: client.place_futures_post_only_limit_sell_order(
                    SWAP_SYMBOL, size, sell_price
                ),
            )
        for create_sell in sell_creators:
            order_id = None
            try:
                order_id = _order_id(create_sell())
            finally:
                if order_id is not None:
                    _cancel_futures(client, order_id)

        order_id = _batch_order_id(_place_futures_batch(client, "buy", size, price))
        _assert_ok(_cancel_futures_batch(client, order_id))
        time.sleep(1)

        _assert_ok(_place_futures_market(client, "buy", _fmt(FUTURES_SIZE)))
        time.sleep(2)
        assert _futures_position_size(client) > 0
        _assert_ok(_place_futures_market(client, "sell", _fmt(FUTURES_SIZE), "yes"))
        time.sleep(2)

        _assert_ok(_place_futures_market(client, "buy", _fmt(FUTURES_SIZE)))
        time.sleep(2)
        assert _futures_position_size(client) > 0
        _assert_ok(_place_futures_market(client, "sell", _fmt(FUTURES_SIZE), "yes"))
        time.sleep(2)

        assert _futures_position_size(client) == 0
        _assert_ok(_get_futures_history_orders(client))
        _assert_ok(_get_futures_fills(client))
    finally:
        with suppress(Exception):
            _cleanup_futures(client)
        _return_futures_margin(client, transferred)
