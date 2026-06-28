# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
from dotenv import load_dotenv

from dcex.mexc.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
CONTRACT_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("1")
FUTURES_TRANSFER_AMOUNT = Decimal("1")
CONTRACT_TEST_LEVERAGE = 50
SPOT_NOTIONAL_BUFFER = Decimal("1.08")

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real MEXC order and transfer tests.",
    ),
]


@pytest.fixture
def client():
    client_instance = Client(api_key=MEXC_API_KEY, api_secret=MEXC_API_SECRET, timeout=20)
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


def _client_id() -> str:
    return f"dcex{uuid.uuid4().hex[:16]}"


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _order_id(response: object) -> str:
    if isinstance(response, dict):
        for key in ("orderId", "order_id", "id"):
            if response.get(key) is not None:
                return str(response[key])
        data = response.get("data")
        if isinstance(data, (str, int)):
            return str(data)
        if isinstance(data, dict):
            for key in ("orderId", "order_id", "id"):
                if data.get(key) is not None:
                    return str(data[key])
        if isinstance(data, list) and data and isinstance(data[0], dict):
            for key in ("orderId", "order_id", "id"):
                if data[0].get(key) is not None:
                    return str(data[0][key])
    raise AssertionError(f"MEXC order response has no order id: {response}")


def _spot_available(client: Client, asset: str) -> Decimal:
    response = client.get_spot_account()
    for item in response.get("balances", []):
        if item.get("asset") == asset:
            return _dec(item.get("free"))
    return Decimal("0")


def _spot_open_orders(client: Client) -> list[dict]:
    response = client.get_spot_open_orders(SPOT_SYMBOL)
    return (
        [item for item in response if isinstance(item, dict)] if isinstance(response, list) else []
    )


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    market = client.get_spot_exchange_info(SPOT_SYMBOL)["symbols"][0]
    step = _dec(market.get("baseSizePrecision"), "0.000001")
    min_notional = max(_dec(market.get("quoteAmountPrecision"), "1"), Decimal("1"))
    price_step = Decimal("1").scaleb(-int(market.get("quotePrecision", 2)))
    return step, min_notional, price_step


def _spot_prices(client: Client) -> tuple[Decimal, Decimal]:
    book = client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
    return _dec(book["bids"][0][0]), _dec(book["asks"][0][0])


def _contract_data(response: object) -> object:
    assert isinstance(response, dict)
    assert response.get("success") is True
    return response.get("data")


def _contract_records(response: object) -> list[dict]:
    data = _contract_data(response)
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("resultList", "items", "records", "list"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _contract_available(client: Client) -> Decimal:
    data = _contract_data(client.get_contract_asset("USDT"))
    assert isinstance(data, dict)
    return _dec(data.get("availableBalance"))


def _contract_open_orders(client: Client) -> list[dict]:
    return _contract_records(
        client.get_contract_open_orders(CONTRACT_SYMBOL, page_num=1, page_size=20)
    )


def _contract_positions(client: Client) -> list[dict]:
    return [
        item
        for item in _contract_records(client.get_contract_open_positions(CONTRACT_SYMBOL))
        if item.get("symbol") == "BTC_USDT"
    ]


def _contract_position_volume(client: Client) -> Decimal:
    return sum((_dec(item.get("holdVol")) for item in _contract_positions(client)), Decimal("0"))


def _contract_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _contract_data(client.get_contract_ticker(CONTRACT_SYMBOL))
    assert isinstance(data, dict)
    return _dec(data.get("bid1")), _dec(data.get("ask1"))


def _contract_post_only_buy_price(client: Client) -> str:
    bid, _ = _contract_prices(client)
    return _fmt(_round_to_step(bid - Decimal("0.1"), Decimal("0.1"), ROUND_DOWN))


def _contract_post_only_sell_price(client: Client) -> str:
    _, ask = _contract_prices(client)
    return _fmt(_round_to_step(ask + Decimal("0.1"), Decimal("0.1"), ROUND_UP))


def _contract_volume(client: Client) -> int:
    details = client.ptm.get_trading_details("mexc", CONTRACT_SYMBOL)
    step = max(_dec(details.get("size_precision"), "1"), Decimal("1"))
    min_size = max(_dec(details.get("min_size"), "1"), step)
    return int(_round_to_step(min_size, step, ROUND_UP).to_integral_value(rounding=ROUND_UP))


def _spot_market_notional(client: Client) -> Decimal:
    _, min_notional, _ = _spot_details(client)
    return min_notional * SPOT_NOTIONAL_BUFFER


def _post_only_buy_params(client: Client) -> tuple[str, str]:
    step, min_notional, price_step = _spot_details(client)
    bid, _ = _spot_prices(client)
    price = _round_to_step(bid - price_step, price_step, ROUND_DOWN)
    quantity = max(
        _round_to_step((min_notional * SPOT_NOTIONAL_BUFFER) / price, step, ROUND_UP),
        step,
    )
    return _fmt(quantity), _fmt(price)


def _post_only_sell_price(client: Client) -> str:
    _, ask = _spot_prices(client)
    _, _, price_step = _spot_details(client)
    return _fmt(_round_to_step(ask + price_step, price_step, ROUND_UP))


def _sell_size(client: Client, amount: Decimal) -> Decimal:
    step, _, _ = _spot_details(client)
    return _round_to_step(amount, step, ROUND_DOWN)


def _ensure_spot_usdt(client: Client, required: Decimal) -> None:
    if _spot_available(client, "USDT") < required:
        pytest.skip("Insufficient MEXC spot USDT for stateful test.")


def _ensure_contract_usdt(client: Client, required: Decimal) -> Decimal:
    if _contract_available(client) >= required:
        return Decimal("0")
    _ensure_spot_usdt(client, FUTURES_TRANSFER_AMOUNT)
    _transfer(client, "SPOT", "FUTURES", FUTURES_TRANSFER_AMOUNT)
    time.sleep(3)
    if _contract_available(client) < required:
        pytest.skip("Insufficient MEXC futures USDT for stateful test.")
    return FUTURES_TRANSFER_AMOUNT


def _skip_if_existing_state(client: Client) -> None:
    if _spot_open_orders(client):
        pytest.skip("MEXC spot already has BTCUSDT open orders; not touching unrelated orders.")


def _skip_if_existing_contract_state(client: Client) -> None:
    if _contract_open_orders(client):
        pytest.skip("MEXC futures already has BTC_USDT open orders; not touching unrelated orders.")
    if _contract_position_volume(client) > 0:
        pytest.skip(
            "MEXC futures already has a BTC_USDT position; not touching unrelated position."
        )


def _cleanup_spot_btc(client: Client, initial_btc: Decimal) -> None:
    extra = _sell_size(client, _spot_available(client, "BTC") - initial_btc)
    if extra > 0:
        with suppress(Exception):
            client.place_spot_market_sell_order(SPOT_SYMBOL, _fmt(extra), _client_id())
            time.sleep(2)


def _cleanup_contract_btc(client: Client) -> None:
    for position in _contract_positions(client):
        volume = int(_dec(position.get("holdVol")))
        if volume <= 0:
            continue
        position_type = int(_dec(position.get("positionType"), "1"))
        side = 4 if position_type == 1 else 2
        with suppress(Exception):
            client.place_contract_market_order(
                CONTRACT_SYMBOL,
                side=side,
                vol=volume,
                leverage=CONTRACT_TEST_LEVERAGE,
                openType=int(_dec(position.get("openType"), "2")),
            )
            time.sleep(3)


def _return_futures_transfer(client: Client, amount: Decimal) -> None:
    if amount <= 0:
        return
    available = _round_to_step(_contract_available(client), Decimal("0.000001"), ROUND_DOWN)
    amount = min(amount, available)
    if amount > 0:
        with suppress(Exception):
            _transfer(client, "FUTURES", "SPOT", amount)
            time.sleep(3)


def _wait_for_contract_volume(client: Client, expected: Decimal) -> Decimal:
    volume = _contract_position_volume(client)
    for _ in range(20):
        if volume == expected:
            return volume
        time.sleep(1)
        volume = _contract_position_volume(client)
    return volume


def _assert_contract_volume(client: Client, expected: Decimal) -> None:
    if _wait_for_contract_volume(client, expected) == expected:
        return
    _cleanup_contract_btc(client)
    assert _wait_for_contract_volume(client, expected) == expected


def _transfer(client: Client, from_type: str, to_type: str, amount: Decimal) -> str:
    response = client.user_universal_transfer(from_type, to_type, "USDT", _fmt(amount))
    if isinstance(response, dict):
        for key in ("tranId", "transactId", "id"):
            if response.get(key) is not None:
                return str(response[key])
        data = response.get("data")
        if isinstance(data, dict):
            for key in ("tranId", "transactId", "id"):
                if data.get(key) is not None:
                    return str(data[key])
    raise AssertionError(f"MEXC transfer response has no id: {response}")


def _cancel_order(client: Client, order_id: str) -> None:
    try:
        client.cancel_spot_order(SPOT_SYMBOL, orderId=order_id)
    except FailedRequestError as exc:
        if "-2011" in str(exc) or "Order cancelled" in str(exc):
            if _spot_open_orders(client):
                raise
            return
        raise
    time.sleep(1)


def test_transfer_round_trip(client):
    _skip_if_existing_state(client)
    _ensure_spot_usdt(client, TRANSFER_AMOUNT)

    first_id = _transfer(client, "SPOT", "FUTURES", TRANSFER_AMOUNT)
    time.sleep(3)
    assert client.get_user_universal_transfer_by_id(first_id) is not None
    assert (
        client.get_user_universal_transfer_history(
            "SPOT",
            "FUTURES",
            page=1,
            size=10,
        )
        is not None
    )

    second_id = _transfer(client, "FUTURES", "SPOT", TRANSFER_AMOUNT)
    time.sleep(3)
    assert client.get_user_universal_transfer_by_id(second_id) is not None
    assert (
        client.get_user_universal_transfer_history(
            "FUTURES",
            "SPOT",
            page=1,
            size=10,
        )
        is not None
    )


def test_spot_stateful_order_lifecycle(client):
    _skip_if_existing_state(client)
    initial_btc = _spot_available(client, "BTC")
    spot_notional = _spot_market_notional(client)
    _ensure_spot_usdt(client, spot_notional * Decimal("3"))

    try:
        quantity, price = _post_only_buy_params(client)
        assert (
            client.test_spot_order(
                SPOT_SYMBOL,
                "BUY",
                "LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC",
            )
            is not None
        )

        for create_order in (
            lambda: client.place_spot_limit_buy_order(SPOT_SYMBOL, quantity, price, _client_id()),
            lambda: client.place_spot_post_only_limit_order(
                SPOT_SYMBOL,
                "BUY",
                quantity,
                price,
                _client_id(),
            ),
            lambda: client.place_spot_post_only_limit_buy_order(
                SPOT_SYMBOL,
                quantity,
                price,
                _client_id(),
            ),
        ):
            order_id = None
            try:
                order_id = _order_id(create_order())
                assert client.get_spot_order(SPOT_SYMBOL, orderId=order_id) is not None
            finally:
                if order_id is not None:
                    _cancel_order(client, order_id)

        assert client.place_spot_batch_orders(
            [
                {
                    "product_symbol": SPOT_SYMBOL,
                    "side": "BUY",
                    "type": "LIMIT_MAKER",
                    "quantity": quantity,
                    "price": price,
                    "newClientOrderId": _client_id(),
                }
            ]
        )
        time.sleep(1)
        assert client.cancel_spot_open_orders(SPOT_SYMBOL) is not None

        before_btc = _spot_available(client, "BTC")
        buy_order = client.place_spot_market_buy_order(
            SPOT_SYMBOL,
            _fmt(spot_notional),
            _client_id(),
        )
        buy_order_id = _order_id(buy_order)
        time.sleep(3)
        bought = _sell_size(client, _spot_available(client, "BTC") - before_btc)
        assert bought > 0

        sell_order_id = None
        try:
            sell_order_id = _order_id(
                client.place_spot_limit_sell_order(
                    SPOT_SYMBOL,
                    _fmt(bought),
                    _post_only_sell_price(client),
                    _client_id(),
                )
            )
        finally:
            if sell_order_id is not None:
                _cancel_order(client, sell_order_id)

        sell_order_id = None
        try:
            sell_order_id = _order_id(
                client.place_spot_post_only_limit_sell_order(
                    SPOT_SYMBOL,
                    _fmt(bought),
                    _post_only_sell_price(client),
                    _client_id(),
                )
            )
        finally:
            if sell_order_id is not None:
                _cancel_order(client, sell_order_id)

        assert client.place_spot_market_sell_order(SPOT_SYMBOL, _fmt(bought), _client_id())
        time.sleep(3)
        assert client.get_spot_my_trades(SPOT_SYMBOL, orderId=buy_order_id, limit=10) is not None

        before_btc = _spot_available(client, "BTC")
        assert client.place_spot_market_order(
            SPOT_SYMBOL,
            "BUY",
            quoteOrderQty=_fmt(spot_notional),
            newClientOrderId=_client_id(),
        )
        time.sleep(3)
        bought = _sell_size(client, _spot_available(client, "BTC") - before_btc)
        assert bought > 0
        assert client.place_spot_market_order(
            SPOT_SYMBOL,
            "SELL",
            quantity=_fmt(bought),
            newClientOrderId=_client_id(),
        )
        time.sleep(3)

        assert client.get_spot_all_orders(SPOT_SYMBOL, limit=10) is not None
        assert client.get_spot_open_orders(SPOT_SYMBOL) is not None
    finally:
        with suppress(Exception):
            client.cancel_spot_open_orders(SPOT_SYMBOL)
        _cleanup_spot_btc(client, initial_btc)


def test_contract_stateful_order_lifecycle(client):
    _skip_if_existing_contract_state(client)
    transferred = Decimal("0")

    try:
        transferred = _ensure_contract_usdt(client, Decimal("0.5"))
        contract_vol = _contract_volume(client)
        buy_price = _contract_post_only_buy_price(client)
        sell_price = _contract_post_only_sell_price(client)

        direct_id = _order_id(
            client.place_contract_order(
                CONTRACT_SYMBOL,
                side=1,
                type_=2,
                openType=2,
                vol=contract_vol,
                price=buy_price,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=_client_id(),
            )
        )
        assert client.get_contract_order(direct_id) is not None
        assert client.cancel_contract_orders([{"orderId": direct_id}]) is not None
        time.sleep(1)

        external_id = _client_id()
        external_order_id = _order_id(
            client.place_contract_post_only_order(
                CONTRACT_SYMBOL,
                side=1,
                price=buy_price,
                vol=contract_vol,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=external_id,
            )
        )
        assert client.get_contract_order_by_external_id(CONTRACT_SYMBOL, external_id) is not None
        assert (
            client.cancel_contract_order_with_external_id(CONTRACT_SYMBOL, external_id) is not None
        )
        time.sleep(1)
        assert client.get_contract_order(external_order_id) is not None

        for create_order in (
            lambda: client.place_contract_limit_buy_order(
                CONTRACT_SYMBOL,
                buy_price,
                contract_vol,
                externalOid=_client_id(),
            ),
            lambda: client.place_contract_limit_sell_order(
                CONTRACT_SYMBOL,
                sell_price,
                contract_vol,
                externalOid=_client_id(),
            ),
            lambda: client.place_contract_post_only_buy_order(
                CONTRACT_SYMBOL,
                buy_price,
                contract_vol,
                externalOid=_client_id(),
            ),
            lambda: client.place_contract_post_only_sell_order(
                CONTRACT_SYMBOL,
                sell_price,
                contract_vol,
                externalOid=_client_id(),
            ),
        ):
            order_id = None
            try:
                order_id = _order_id(create_order())
                assert client.get_contract_orders([order_id]) is not None
            finally:
                if order_id is not None:
                    client.cancel_contract_order(order_id)
                    time.sleep(1)

        long_open_id = _order_id(
            client.place_contract_market_buy_order(
                CONTRACT_SYMBOL,
                vol=contract_vol,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=_client_id(),
            )
        )
        assert _wait_for_contract_volume(client, Decimal(contract_vol)) > 0
        assert client.get_contract_order(long_open_id) is not None
        assert client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=4,
            vol=contract_vol,
            leverage=CONTRACT_TEST_LEVERAGE,
            openType=2,
            externalOid=_client_id(),
        )
        _assert_contract_volume(client, Decimal("0"))

        isolated_open_id = _order_id(
            client.place_contract_market_buy_order(
                CONTRACT_SYMBOL,
                vol=contract_vol,
                leverage=CONTRACT_TEST_LEVERAGE,
                openType=1,
                externalOid=_client_id(),
            )
        )
        assert _wait_for_contract_volume(client, Decimal(contract_vol)) > 0
        long_position = next(
            position
            for position in _contract_positions(client)
            if int(_dec(position.get("positionType"), "1")) == 1
        )
        assert client.change_contract_margin(
            int(_dec(long_position.get("positionId"))),
            "0.01",
            "ADD",
        )
        assert client.get_contract_order(isolated_open_id) is not None
        assert client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=4,
            vol=contract_vol,
            leverage=CONTRACT_TEST_LEVERAGE,
            openType=1,
            externalOid=_client_id(),
        )
        _assert_contract_volume(client, Decimal("0"))
        time.sleep(3)

        short_open_id = _order_id(
            client.place_contract_market_sell_order(
                CONTRACT_SYMBOL,
                vol=contract_vol,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=_client_id(),
            )
        )
        assert _wait_for_contract_volume(client, Decimal(contract_vol)) > 0
        assert client.get_contract_order(short_open_id) is not None
        assert client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=2,
            vol=contract_vol,
            leverage=CONTRACT_TEST_LEVERAGE,
            openType=2,
            externalOid=_client_id(),
        )
        _assert_contract_volume(client, Decimal("0"))

        assert client.get_contract_history_orders(CONTRACT_SYMBOL, page_num=1, page_size=10)
        assert client.get_contract_order_deals(CONTRACT_SYMBOL, page_num=1, page_size=10)
        assert client.get_contract_order_deal_details(long_open_id)
        assert client.get_contract_open_orders(CONTRACT_SYMBOL, page_num=1, page_size=10)
    finally:
        with suppress(Exception):
            client.cancel_all_contract_orders(CONTRACT_SYMBOL)
        _cleanup_contract_btc(client)
        _return_futures_transfer(client, transferred)
