# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import asyncio
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bitget.client import Client
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

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Bitget async order and transfer tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BITGET_API_KEY,
        api_secret=BITGET_API_SECRET,
        passphrase=BITGET_PASSPHRASE,
        timeout=20,
    ) as client_instance:
        yield client_instance


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


def _items(response: object) -> list[dict]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    if isinstance(response, dict):
        data = response.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            for key in ("orderList", "orders", "fills", "list"):
                if isinstance(data.get(key), list):
                    return [item for item in data[key] if isinstance(item, dict)]
    return []


async def _spot_available(client: Client, coin: str) -> Decimal:
    for item in _items(_assert_ok(await client.get_spot_account_assets(coin=coin))):
        if item.get("coin") == coin:
            return _dec(item.get("available"))
    return Decimal("0")


async def _futures_available(client: Client) -> Decimal:
    for item in _items(_assert_ok(await client.get_futures_accounts())):
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


async def _spot_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _assert_ok(await client.get_spot_orderbook(SPOT_SYMBOL, limit=5))["data"]
    return _dec(data["bids"][0][0]), _dec(data["asks"][0][0])


async def _spot_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    bid, _ = await _spot_prices(client)
    price = _round_to_step(bid * Decimal("0.98"), tick, ROUND_DOWN)
    size = max(
        _round_to_step((min_notional * Decimal("1.12")) / price, step, ROUND_UP),
        min_size,
    )
    return _fmt(size), _fmt(price)


async def _spot_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, ask = await _spot_prices(client)
    return _fmt(_round_to_step(ask * Decimal("1.02"), tick, ROUND_UP))


def _spot_sell_size(client: Client, amount: Decimal) -> Decimal:
    _, step, _, _ = _spot_details(client)
    return _round_to_step(amount, step, ROUND_DOWN)


def _futures_details(client: Client) -> tuple[Decimal, Decimal]:
    details = client.ptm.get_trading_details("bitget", SWAP_SYMBOL)
    return _dec(details.get("price_precision"), "0.1"), _dec(details.get("min_size"), "0.0001")


async def _futures_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = _assert_ok(await client.get_futures_orderbook(SWAP_SYMBOL, limit=5))["data"]
    return _dec(data["bids"][0][0]), _dec(data["asks"][0][0])


async def _futures_buy_params(client: Client) -> tuple[str, str]:
    tick, min_size = _futures_details(client)
    bid, _ = await _futures_prices(client)
    price = _round_to_step(bid * Decimal("0.98"), tick, ROUND_DOWN)
    return _fmt(max(FUTURES_SIZE, min_size)), _fmt(price)


async def _futures_sell_price(client: Client) -> str:
    tick, _ = _futures_details(client)
    _, ask = await _futures_prices(client)
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
    success = data.get("successList", []) if isinstance(data, dict) else []
    assert success, response
    return str(success[0]["orderId"])


async def _spot_open_orders(client: Client) -> list[dict]:
    try:
        return _items(_assert_ok(await client.get_spot_open_orders(SPOT_SYMBOL, limit=20)))
    except FailedRequestError as exc:
        _skip_if_unified_account_error(exc)
        raise


async def _futures_open_orders(client: Client) -> list[dict]:
    return _items(_assert_ok(await client.get_futures_open_orders(SWAP_SYMBOL, limit=20)))


async def _futures_positions(client: Client) -> list[dict]:
    return [
        item
        for item in _items(_assert_ok(await client.get_futures_positions(marginCoin="USDT")))
        if item.get("symbol") == EXCHANGE_SYMBOL
    ]


async def _futures_position_size(client: Client) -> Decimal:
    size = Decimal("0")
    for position in await _futures_positions(client):
        total = _dec(position.get("total"))
        if total == 0:
            continue
        hold_side = str(position.get("holdSide", "")).lower()
        size += -total if hold_side == "short" else total
    return size


async def _skip_if_existing_state(client: Client) -> None:
    if await _spot_open_orders(client):
        pytest.skip("Bitget spot already has BTCUSDT open orders; not touching unrelated orders.")
    if await _futures_open_orders(client):
        pytest.skip(
            "Bitget futures already has BTCUSDT open orders; not touching unrelated orders."
        )
    if await _futures_position_size(client) != 0:
        pytest.skip("Bitget futures already has a BTCUSDT position; not changing exposure.")


async def _ensure_spot_usdt(client: Client, amount: Decimal) -> None:
    if await _spot_available(client, "USDT") < amount:
        pytest.skip("Insufficient Bitget spot USDT for async stateful test.")


async def _transfer(client: Client, amount: Decimal, from_type: str, to_type: str) -> None:
    _assert_ok(
        await client.transfer(
            coin="USDT",
            amount=_fmt(amount),
            fromType=from_type,
            toType=to_type,
            clientOid=_client_oid(),
        )
    )
    await asyncio.sleep(2)


async def _ensure_futures_margin(
    client: Client,
    amount: Decimal = FUTURES_TRANSFER_AMOUNT,
) -> Decimal:
    if await _futures_available(client) >= Decimal("1"):
        return Decimal("0")
    await _ensure_spot_usdt(client, amount)
    await _transfer(client, amount, "spot", "usdt_futures")
    if await _futures_available(client) <= 0:
        pytest.skip("Bitget futures USDT remains unavailable after transfer.")
    return amount


async def _return_futures_margin(client: Client, amount: Decimal) -> None:
    if amount <= 0:
        return
    transfer_amount = min(amount, await _futures_available(client)).quantize(
        Decimal("0.000001"),
        rounding=ROUND_DOWN,
    )
    if transfer_amount > 0:
        await _transfer(client, transfer_amount, "usdt_futures", "spot")


async def _cancel_spot(client: Client, order_id: str) -> None:
    _assert_ok(await client.cancel_spot_order(SPOT_SYMBOL, orderId=order_id))
    await asyncio.sleep(1)


async def _cancel_futures(client: Client, order_id: str) -> None:
    _assert_ok(await client.cancel_futures_order(SWAP_SYMBOL, orderId=order_id))
    await asyncio.sleep(1)


async def _cleanup_spot_btc(client: Client, initial_btc: Decimal) -> None:
    extra = _spot_sell_size(client, await _spot_available(client, "BTC") - initial_btc)
    _, _, _, min_notional = _spot_details(client)
    bid, _ = await _spot_prices(client)
    if extra > 0 and extra * bid >= min_notional:
        _assert_ok(await client.place_spot_market_sell_order(SPOT_SYMBOL, _fmt(extra)))
        await asyncio.sleep(2)


async def _cleanup_futures(client: Client) -> None:
    size = await _futures_position_size(client)
    if size > 0:
        _assert_ok(
            await client.place_futures_market_sell_order(SWAP_SYMBOL, _fmt(abs(size)), "YES")
        )
    elif size < 0:
        _assert_ok(
            await client.place_futures_market_order(
                SWAP_SYMBOL,
                "buy",
                _fmt(abs(size)),
                reduceOnly="YES",
            )
        )
    await asyncio.sleep(2)


async def _safe_setting_call(call) -> None:
    try:
        _assert_ok(await call())
    except FailedRequestError as exc:
        message = str(exc).lower()
        if any(token in message for token in ("no need", "already", "same")):
            return
        raise


@pytest.mark.asyncio
async def test_transfer_round_trip(client):
    await _skip_if_existing_state(client)
    await _ensure_spot_usdt(client, Decimal("1"))
    await _transfer(client, Decimal("1"), "spot", "usdt_futures")
    await _transfer(client, Decimal("1"), "usdt_futures", "spot")
    _assert_ok(await client.get_transfer_records(coin="USDT", limit=20))


@pytest.mark.asyncio
async def test_spot_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    await _ensure_spot_usdt(client, SPOT_TEST_NOTIONAL)

    try:
        size, price = await _spot_buy_params(client)
        order_id = None
        try:
            order_id = _order_id(
                await client.place_spot_limit_order(SPOT_SYMBOL, "buy", size, price)
            )
            _assert_ok(await client.get_spot_order(orderId=order_id))
        finally:
            if order_id is not None:
                await _cancel_spot(client, order_id)

        order_id = _batch_order_id(
            await client.place_spot_batch_orders(
                [
                    {
                        "side": "buy",
                        "orderType": "limit",
                        "force": "post_only",
                        "price": price,
                        "size": size,
                        "clientOid": _client_oid(),
                    }
                ],
                product_symbol=SPOT_SYMBOL,
            )
        )
        _assert_ok(await client.cancel_spot_batch_orders([{"orderId": order_id}], SPOT_SYMBOL))
        await asyncio.sleep(1)

        before_btc = await _spot_available(client, "BTC")
        _assert_ok(await client.place_spot_market_buy_order(SPOT_SYMBOL, _fmt(SPOT_TEST_NOTIONAL)))
        await asyncio.sleep(2)
        acquired = _spot_sell_size(client, await _spot_available(client, "BTC") - before_btc)
        assert acquired > 0

        sell_price = await _spot_sell_price(client)
        for create_sell in (
            lambda: client.place_spot_limit_sell_order(SPOT_SYMBOL, _fmt(acquired), sell_price),
            lambda: client.place_spot_post_only_limit_sell_order(
                SPOT_SYMBOL,
                _fmt(acquired),
                sell_price,
            ),
        ):
            order_id = None
            try:
                order_id = _order_id(await create_sell())
                _assert_ok(await client.get_spot_order(orderId=order_id))
            finally:
                if order_id is not None:
                    await _cancel_spot(client, order_id)

        _assert_ok(await client.place_spot_market_sell_order(SPOT_SYMBOL, _fmt(acquired)))
        await asyncio.sleep(2)
        _assert_ok(await client.get_spot_history_orders(SPOT_SYMBOL, limit=20))
        _assert_ok(await client.get_spot_fills(SPOT_SYMBOL, limit=20))
    finally:
        with suppress(Exception):
            await _cleanup_spot_btc(client, initial_btc)


@pytest.mark.asyncio
async def test_futures_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    transferred = await _ensure_futures_margin(client)
    try:
        await _safe_setting_call(lambda: client.set_futures_position_mode("one_way_mode"))
        await _safe_setting_call(lambda: client.set_futures_margin_mode(SWAP_SYMBOL, "crossed"))
        _assert_ok(await client.set_futures_leverage(SWAP_SYMBOL, "50"))

        size, price = await _futures_buy_params(client)
        order_id = None
        try:
            order_id = _order_id(
                await client.place_futures_limit_order(SWAP_SYMBOL, "buy", size, price)
            )
            _assert_ok(await client.get_futures_order(SWAP_SYMBOL, orderId=order_id))
        finally:
            if order_id is not None:
                await _cancel_futures(client, order_id)

        sell_price = await _futures_sell_price(client)
        order_id = None
        try:
            order_id = _order_id(
                await client.place_futures_post_only_limit_sell_order(SWAP_SYMBOL, size, sell_price)
            )
        finally:
            if order_id is not None:
                await _cancel_futures(client, order_id)

        order_id = _batch_order_id(
            await client.place_futures_batch_orders(
                [
                    {
                        "symbol": EXCHANGE_SYMBOL,
                        "size": size,
                        "price": price,
                        "side": "buy",
                        "orderType": "limit",
                        "force": "post_only",
                        "clientOid": _client_oid(),
                    }
                ],
                product_symbol=SWAP_SYMBOL,
            )
        )
        _assert_ok(await client.cancel_futures_batch_orders(SWAP_SYMBOL, [{"orderId": order_id}]))
        await asyncio.sleep(1)

        _assert_ok(await client.place_futures_market_order(SWAP_SYMBOL, "buy", _fmt(FUTURES_SIZE)))
        await asyncio.sleep(2)
        assert await _futures_position_size(client) > 0
        _assert_ok(
            await client.place_futures_market_sell_order(SWAP_SYMBOL, _fmt(FUTURES_SIZE), "YES")
        )
        await asyncio.sleep(2)

        _assert_ok(await client.place_futures_market_buy_order(SWAP_SYMBOL, _fmt(FUTURES_SIZE)))
        await asyncio.sleep(2)
        assert await _futures_position_size(client) > 0
        _assert_ok(
            await client.place_futures_market_order(
                SWAP_SYMBOL,
                "sell",
                _fmt(FUTURES_SIZE),
                reduceOnly="YES",
            )
        )
        await asyncio.sleep(2)

        assert await _futures_position_size(client) == 0
        _assert_ok(await client.get_futures_history_orders(SWAP_SYMBOL, limit=20))
        _assert_ok(await client.get_futures_fills(SWAP_SYMBOL, limit=20))
    finally:
        with suppress(Exception):
            await _cleanup_futures(client)
        await _return_futures_margin(client, transferred)
