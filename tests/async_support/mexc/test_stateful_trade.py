# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.mexc.client import Client

load_dotenv()

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_API_SECRET = os.getenv("MEXC_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
CONTRACT_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("1")
FUTURES_TRANSFER_AMOUNT = Decimal("1")
CONTRACT_TEST_LEVERAGE = 50
CONTRACT_TEST_VOL = 1

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real MEXC order and transfer tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=MEXC_API_KEY, api_secret=MEXC_API_SECRET, timeout=20
    ) as client_instance:
        yield client_instance


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


async def _spot_available(client: Client, asset: str) -> Decimal:
    response = await client.get_spot_account()
    for item in response.get("balances", []):
        if item.get("asset") == asset:
            return _dec(item.get("free"))
    return Decimal("0")


async def _spot_open_orders(client: Client) -> list[dict]:
    response = await client.get_spot_open_orders(SPOT_SYMBOL)
    return (
        [item for item in response if isinstance(item, dict)] if isinstance(response, list) else []
    )


async def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal]:
    market = (await client.get_spot_exchange_info(SPOT_SYMBOL))["symbols"][0]
    step = _dec(market.get("baseSizePrecision"), "0.000001")
    min_notional = max(_dec(market.get("quoteAmountPrecision"), "1"), Decimal("1"))
    price_step = Decimal("1").scaleb(-int(market.get("quotePrecision", 2)))
    return step, min_notional, price_step


async def _spot_prices(client: Client) -> tuple[Decimal, Decimal]:
    book = await client.get_spot_orderbook(SPOT_SYMBOL, limit=5)
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


async def _contract_available(client: Client) -> Decimal:
    data = _contract_data(await client.get_contract_asset("USDT"))
    assert isinstance(data, dict)
    return _dec(data.get("availableBalance"))


async def _contract_open_orders(client: Client) -> list[dict]:
    return _contract_records(
        await client.get_contract_open_orders(CONTRACT_SYMBOL, page_num=1, page_size=20)
    )


async def _contract_positions(client: Client) -> list[dict]:
    return [
        item
        for item in _contract_records(await client.get_contract_open_positions(CONTRACT_SYMBOL))
        if item.get("symbol") == "BTC_USDT"
    ]


async def _contract_position_volume(client: Client) -> Decimal:
    return sum(
        (_dec(item.get("holdVol")) for item in await _contract_positions(client)),
        Decimal("0"),
    )


async def _contract_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _contract_data(await client.get_contract_ticker(CONTRACT_SYMBOL))
    assert isinstance(data, dict)
    return _dec(data.get("bid1")), _dec(data.get("ask1"))


async def _contract_post_only_buy_price(client: Client) -> str:
    bid, _ = await _contract_prices(client)
    return _fmt(_round_to_step(bid - Decimal("0.1"), Decimal("0.1"), ROUND_DOWN))


async def _contract_post_only_sell_price(client: Client) -> str:
    _, ask = await _contract_prices(client)
    return _fmt(_round_to_step(ask + Decimal("0.1"), Decimal("0.1"), ROUND_UP))


async def _spot_market_notional(client: Client) -> Decimal:
    _, min_notional, _ = await _spot_details(client)
    return min_notional * Decimal("1.01")


async def _post_only_buy_params(client: Client) -> tuple[str, str]:
    step, min_notional, price_step = await _spot_details(client)
    bid, _ = await _spot_prices(client)
    price = _round_to_step(bid - price_step, price_step, ROUND_DOWN)
    quantity = max(
        _round_to_step((min_notional * Decimal("1.01")) / price, step, ROUND_UP),
        step,
    )
    return _fmt(quantity), _fmt(price)


async def _post_only_sell_price(client: Client) -> str:
    _, ask = await _spot_prices(client)
    _, _, price_step = await _spot_details(client)
    return _fmt(_round_to_step(ask + price_step, price_step, ROUND_UP))


async def _sell_size(client: Client, amount: Decimal) -> Decimal:
    step, _, _ = await _spot_details(client)
    return _round_to_step(amount, step, ROUND_DOWN)


async def _ensure_spot_usdt(client: Client, required: Decimal) -> None:
    if await _spot_available(client, "USDT") < required:
        pytest.skip("Insufficient MEXC spot USDT for stateful test.")


async def _ensure_contract_usdt(client: Client, required: Decimal) -> Decimal:
    if await _contract_available(client) >= required:
        return Decimal("0")
    await _ensure_spot_usdt(client, FUTURES_TRANSFER_AMOUNT)
    await _transfer(client, "SPOT", "FUTURES", FUTURES_TRANSFER_AMOUNT)
    await asyncio.sleep(3)
    if await _contract_available(client) < required:
        pytest.skip("Insufficient MEXC futures USDT for stateful test.")
    return FUTURES_TRANSFER_AMOUNT


async def _skip_if_existing_state(client: Client) -> None:
    if await _spot_open_orders(client):
        pytest.skip("MEXC spot already has BTCUSDT open orders; not touching unrelated orders.")


async def _skip_if_existing_contract_state(client: Client) -> None:
    if await _contract_open_orders(client):
        pytest.skip("MEXC futures already has BTC_USDT open orders; not touching unrelated orders.")
    if await _contract_position_volume(client) > 0:
        pytest.skip(
            "MEXC futures already has a BTC_USDT position; not touching unrelated position."
        )


async def _cleanup_spot_btc(client: Client, initial_btc: Decimal) -> None:
    extra = await _sell_size(client, await _spot_available(client, "BTC") - initial_btc)
    if extra > 0:
        with suppress(Exception):
            await client.place_spot_market_sell_order(SPOT_SYMBOL, _fmt(extra), _client_id())
            await asyncio.sleep(2)


async def _cleanup_contract_btc(client: Client) -> None:
    for position in await _contract_positions(client):
        volume = int(_dec(position.get("holdVol")))
        if volume <= 0:
            continue
        position_type = int(_dec(position.get("positionType"), "1"))
        side = 4 if position_type == 1 else 2
        with suppress(Exception):
            await client.place_contract_market_order(
                CONTRACT_SYMBOL,
                side=side,
                vol=volume,
                leverage=CONTRACT_TEST_LEVERAGE,
                openType=int(_dec(position.get("openType"), "2")),
            )
            await asyncio.sleep(3)


async def _return_futures_transfer(client: Client, amount: Decimal) -> None:
    if amount <= 0:
        return
    available = _round_to_step(await _contract_available(client), Decimal("0.000001"), ROUND_DOWN)
    amount = min(amount, available)
    if amount > 0:
        with suppress(Exception):
            await _transfer(client, "FUTURES", "SPOT", amount)
            await asyncio.sleep(3)


async def _wait_for_contract_volume(client: Client, expected: Decimal) -> Decimal:
    volume = await _contract_position_volume(client)
    for _ in range(10):
        if volume == expected:
            return volume
        await asyncio.sleep(1)
        volume = await _contract_position_volume(client)
    return volume


async def _transfer(client: Client, from_type: str, to_type: str, amount: Decimal) -> str:
    response = await client.user_universal_transfer(from_type, to_type, "USDT", _fmt(amount))
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


async def _cancel_order(client: Client, order_id: str) -> None:
    await client.cancel_spot_order(SPOT_SYMBOL, orderId=order_id)
    await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_transfer_round_trip(client):
    await _skip_if_existing_state(client)
    await _ensure_spot_usdt(client, TRANSFER_AMOUNT)

    first_id = await _transfer(client, "SPOT", "FUTURES", TRANSFER_AMOUNT)
    await asyncio.sleep(3)
    assert await client.get_user_universal_transfer_by_id(first_id) is not None
    assert (
        await client.get_user_universal_transfer_history(
            "SPOT",
            "FUTURES",
            page=1,
            size=10,
        )
        is not None
    )

    second_id = await _transfer(client, "FUTURES", "SPOT", TRANSFER_AMOUNT)
    await asyncio.sleep(3)
    assert await client.get_user_universal_transfer_by_id(second_id) is not None
    assert (
        await client.get_user_universal_transfer_history(
            "FUTURES",
            "SPOT",
            page=1,
            size=10,
        )
        is not None
    )


@pytest.mark.asyncio
async def test_spot_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    spot_notional = await _spot_market_notional(client)
    await _ensure_spot_usdt(client, spot_notional * Decimal("3"))

    try:
        quantity, price = await _post_only_buy_params(client)
        assert (
            await client.test_spot_order(
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
                order_id = _order_id(await create_order())
                assert await client.get_spot_order(SPOT_SYMBOL, orderId=order_id) is not None
            finally:
                if order_id is not None:
                    await _cancel_order(client, order_id)

        assert await client.place_spot_batch_orders(
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
        await asyncio.sleep(1)
        assert await client.cancel_spot_open_orders(SPOT_SYMBOL) is not None

        before_btc = await _spot_available(client, "BTC")
        buy_order = await client.place_spot_market_buy_order(
            SPOT_SYMBOL,
            _fmt(spot_notional),
            _client_id(),
        )
        buy_order_id = _order_id(buy_order)
        await asyncio.sleep(3)
        bought = await _sell_size(client, await _spot_available(client, "BTC") - before_btc)
        assert bought > 0

        sell_order_id = None
        try:
            sell_order_id = _order_id(
                await client.place_spot_limit_sell_order(
                    SPOT_SYMBOL,
                    _fmt(bought),
                    await _post_only_sell_price(client),
                    _client_id(),
                )
            )
        finally:
            if sell_order_id is not None:
                await _cancel_order(client, sell_order_id)

        sell_order_id = None
        try:
            sell_order_id = _order_id(
                await client.place_spot_post_only_limit_sell_order(
                    SPOT_SYMBOL,
                    _fmt(bought),
                    await _post_only_sell_price(client),
                    _client_id(),
                )
            )
        finally:
            if sell_order_id is not None:
                await _cancel_order(client, sell_order_id)

        assert await client.place_spot_market_sell_order(SPOT_SYMBOL, _fmt(bought), _client_id())
        await asyncio.sleep(3)
        assert (
            await client.get_spot_my_trades(SPOT_SYMBOL, orderId=buy_order_id, limit=10) is not None
        )

        before_btc = await _spot_available(client, "BTC")
        assert await client.place_spot_market_order(
            SPOT_SYMBOL,
            "BUY",
            quoteOrderQty=_fmt(spot_notional),
            newClientOrderId=_client_id(),
        )
        await asyncio.sleep(3)
        bought = await _sell_size(client, await _spot_available(client, "BTC") - before_btc)
        assert bought > 0
        assert await client.place_spot_market_order(
            SPOT_SYMBOL,
            "SELL",
            quantity=_fmt(bought),
            newClientOrderId=_client_id(),
        )
        await asyncio.sleep(3)

        assert await client.get_spot_all_orders(SPOT_SYMBOL, limit=10) is not None
        assert await client.get_spot_open_orders(SPOT_SYMBOL) is not None
    finally:
        with suppress(Exception):
            await client.cancel_spot_open_orders(SPOT_SYMBOL)
        await _cleanup_spot_btc(client, initial_btc)


@pytest.mark.asyncio
async def test_contract_stateful_order_lifecycle(client):
    await _skip_if_existing_contract_state(client)
    transferred = Decimal("0")

    try:
        transferred = await _ensure_contract_usdt(client, Decimal("0.5"))
        buy_price = await _contract_post_only_buy_price(client)
        sell_price = await _contract_post_only_sell_price(client)

        direct_id = _order_id(
            await client.place_contract_order(
                CONTRACT_SYMBOL,
                side=1,
                type_=2,
                openType=2,
                vol=CONTRACT_TEST_VOL,
                price=buy_price,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=_client_id(),
            )
        )
        assert await client.get_contract_order(direct_id) is not None
        assert await client.cancel_contract_orders([{"orderId": direct_id}]) is not None
        await asyncio.sleep(1)

        external_id = _client_id()
        external_order_id = _order_id(
            await client.place_contract_post_only_order(
                CONTRACT_SYMBOL,
                side=1,
                price=buy_price,
                vol=CONTRACT_TEST_VOL,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=external_id,
            )
        )
        assert await client.get_contract_order_by_external_id(CONTRACT_SYMBOL, external_id)
        assert await client.cancel_contract_order_with_external_id(CONTRACT_SYMBOL, external_id)
        await asyncio.sleep(1)
        assert await client.get_contract_order(external_order_id) is not None

        for create_order in (
            lambda: client.place_contract_limit_buy_order(
                CONTRACT_SYMBOL,
                buy_price,
                CONTRACT_TEST_VOL,
                externalOid=_client_id(),
            ),
            lambda: client.place_contract_limit_sell_order(
                CONTRACT_SYMBOL,
                sell_price,
                CONTRACT_TEST_VOL,
                externalOid=_client_id(),
            ),
            lambda: client.place_contract_post_only_buy_order(
                CONTRACT_SYMBOL,
                buy_price,
                CONTRACT_TEST_VOL,
                externalOid=_client_id(),
            ),
            lambda: client.place_contract_post_only_sell_order(
                CONTRACT_SYMBOL,
                sell_price,
                CONTRACT_TEST_VOL,
                externalOid=_client_id(),
            ),
        ):
            order_id = None
            try:
                order_id = _order_id(await create_order())
                assert await client.get_contract_orders([order_id]) is not None
            finally:
                if order_id is not None:
                    await client.cancel_contract_order(order_id)
                    await asyncio.sleep(1)

        long_open_id = _order_id(
            await client.place_contract_market_buy_order(
                CONTRACT_SYMBOL,
                vol=CONTRACT_TEST_VOL,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=_client_id(),
            )
        )
        assert await _wait_for_contract_volume(client, Decimal(CONTRACT_TEST_VOL)) > 0
        assert await client.get_contract_order(long_open_id) is not None
        assert await client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=4,
            vol=CONTRACT_TEST_VOL,
            leverage=CONTRACT_TEST_LEVERAGE,
            openType=2,
            externalOid=_client_id(),
        )
        assert await _wait_for_contract_volume(client, Decimal("0")) == 0

        isolated_open_id = _order_id(
            await client.place_contract_market_buy_order(
                CONTRACT_SYMBOL,
                vol=CONTRACT_TEST_VOL,
                leverage=CONTRACT_TEST_LEVERAGE,
                openType=1,
                externalOid=_client_id(),
            )
        )
        assert await _wait_for_contract_volume(client, Decimal(CONTRACT_TEST_VOL)) > 0
        long_position = next(
            position
            for position in await _contract_positions(client)
            if int(_dec(position.get("positionType"), "1")) == 1
        )
        assert await client.change_contract_margin(
            int(_dec(long_position.get("positionId"))),
            "0.01",
            "ADD",
        )
        assert await client.get_contract_order(isolated_open_id) is not None
        assert await client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=4,
            vol=CONTRACT_TEST_VOL,
            leverage=CONTRACT_TEST_LEVERAGE,
            openType=1,
            externalOid=_client_id(),
        )
        assert await _wait_for_contract_volume(client, Decimal("0")) == 0
        await asyncio.sleep(3)

        short_open_id = _order_id(
            await client.place_contract_market_sell_order(
                CONTRACT_SYMBOL,
                vol=CONTRACT_TEST_VOL,
                leverage=CONTRACT_TEST_LEVERAGE,
                externalOid=_client_id(),
            )
        )
        assert await _wait_for_contract_volume(client, Decimal(CONTRACT_TEST_VOL)) > 0
        assert await client.get_contract_order(short_open_id) is not None
        assert await client.place_contract_market_order(
            CONTRACT_SYMBOL,
            side=2,
            vol=CONTRACT_TEST_VOL,
            leverage=CONTRACT_TEST_LEVERAGE,
            openType=2,
            externalOid=_client_id(),
        )
        assert await _wait_for_contract_volume(client, Decimal("0")) == 0

        assert await client.get_contract_history_orders(CONTRACT_SYMBOL, page_num=1, page_size=10)
        assert await client.get_contract_order_deals(CONTRACT_SYMBOL, page_num=1, page_size=10)
        assert await client.get_contract_order_deal_details(long_open_id)
        assert await client.get_contract_open_orders(CONTRACT_SYMBOL, page_num=1, page_size=10)
    finally:
        with suppress(Exception):
            await client.cancel_all_contract_orders(CONTRACT_SYMBOL)
        await _cleanup_contract_btc(client)
        await _return_futures_transfer(client, transferred)
