# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import json
import os
import uuid
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.hyperliquid.client import Client
from dcex.hyperliquid.client import Client as SyncClient
from dcex.utils.common import Common

load_dotenv()

WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
SYMBOL = "BTC-USD-SWAP"
SPOT_SYMBOL = "PURR-USDC-SPOT"
ORDER_SIZE = Decimal("0.0002")
SPOT_ORDER_NOTIONAL = Decimal("12")
SPOT_REQUIRED_USDC = Decimal("12.5")
ACCOUNT_USER: str | None = None
PERPS_ACCOUNT_VALUE: Decimal | None = None
SPOT_AVAILABLE_USDC: Decimal | None = None

pytestmark = [
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Hyperliquid trade tests.",
    ),
]


@pytest.fixture(scope="module")
def account_snapshot():
    global ACCOUNT_USER, PERPS_ACCOUNT_VALUE, SPOT_AVAILABLE_USDC

    snapshot_client = SyncClient(
        wallet_address=WALLET_ADDRESS,
        private_key=PRIVATE_KEY,
        preload_product_table=False,
    )
    role = snapshot_client.user_role(user=WALLET_ADDRESS)
    if isinstance(role, dict) and role.get("role") == "agent":
        ACCOUNT_USER = role.get("data", {}).get("user", WALLET_ADDRESS)
    else:
        ACCOUNT_USER = WALLET_ADDRESS

    perp = snapshot_client.clearinghouse_state(user=ACCOUNT_USER)
    summary = perp.get("marginSummary", {}) if isinstance(perp, dict) else {}
    PERPS_ACCOUNT_VALUE = Decimal(str(summary.get("accountValue", "0")))

    spot = snapshot_client.spot_clearinghouse_state(user=ACCOUNT_USER)
    SPOT_AVAILABLE_USDC = Decimal("0")
    for balance in spot.get("balances", []) if isinstance(spot, dict) else []:
        if balance.get("coin") == "USDC":
            SPOT_AVAILABLE_USDC = Decimal(str(balance.get("total", "0"))) - Decimal(
                str(balance.get("hold", "0"))
            )
            break

    snapshot_client.close()


@pytest_asyncio.fixture
async def client(account_snapshot):
    async with Client(wallet_address=WALLET_ADDRESS, private_key=PRIVATE_KEY) as client_instance:
        yield client_instance


def _cloid() -> str:
    return "0x" + uuid.uuid4().hex


def _asset_id(client: Client) -> int:
    return json.loads(client.ptm.get_exchange_symbol(Common.HYPERLIQUID, SYMBOL))[1]


async def _mid_price(client: Client) -> Decimal:
    data = await client.get_meta_and_asset_ctxs()
    return Decimal(str(data[1][_asset_id(client)]["midPx"]))


async def _post_only_buy_price(client: Client) -> str:
    return str(int(await _mid_price(client) * Decimal("0.9")))


async def _post_only_sell_price(client: Client) -> str:
    return str(int(await _mid_price(client) * Decimal("1.1")))


def _format_hyperliquid_price(value: Decimal, rounding: str) -> str:
    if value <= 0:
        return "0"
    precision_step = Decimal(1).scaleb(value.adjusted() - 4)
    return format(value.quantize(precision_step, rounding=rounding).normalize(), "f")


def _size() -> str:
    return format(ORDER_SIZE.normalize(), "f")


def _assert_exchange_response(res: dict) -> None:
    assert res is not None
    assert isinstance(res, dict)


async def _account_user(client: Client) -> str:
    if ACCOUNT_USER is not None:
        return ACCOUNT_USER
    role = await client.user_role(user=WALLET_ADDRESS)
    if isinstance(role, dict) and role.get("role") == "agent":
        return role.get("data", {}).get("user", WALLET_ADDRESS)
    return WALLET_ADDRESS


async def _open_orders(client: Client) -> list:
    orders = await client.open_orders(user=await _account_user(client))
    return orders if isinstance(orders, list) else []


async def _positions(client: Client) -> list:
    data = await client.clearinghouse_state(user=await _account_user(client))
    positions = data.get("assetPositions", []) if isinstance(data, dict) else []
    return positions if isinstance(positions, list) else []


async def _btc_position_size(client: Client) -> Decimal:
    for item in await _positions(client):
        position = item.get("position", {}) if isinstance(item, dict) else {}
        if position.get("coin") == "BTC":
            return Decimal(str(position.get("szi", "0")))
    return Decimal("0")


async def _account_value(client: Client) -> Decimal:
    if PERPS_ACCOUNT_VALUE is not None:
        return PERPS_ACCOUNT_VALUE
    data = await client.clearinghouse_state(user=await _account_user(client))
    summary = data.get("marginSummary", {}) if isinstance(data, dict) else {}
    return Decimal(str(summary.get("accountValue", "0")))


async def _spot_available_usdc(client: Client) -> Decimal:
    return await _spot_available(client, "USDC")


async def _spot_available(client: Client, coin: str) -> Decimal:
    if SPOT_AVAILABLE_USDC is not None:
        if coin != "USDC":
            return await _spot_available_uncached(client, coin)
        return SPOT_AVAILABLE_USDC
    return await _spot_available_uncached(client, coin)


async def _spot_available_uncached(client: Client, coin: str) -> Decimal:
    data = await client.spot_clearinghouse_state(user=await _account_user(client))
    for balance in data.get("balances", []) if isinstance(data, dict) else []:
        if balance.get("coin") == coin:
            return Decimal(str(balance.get("total", "0"))) - Decimal(str(balance.get("hold", "0")))
    return Decimal("0")


async def _skip_if_account_state(client: Client) -> None:
    if await _open_orders(client):
        pytest.skip("Hyperliquid account already has open orders; not touching unrelated orders.")
    if await _positions(client):
        pytest.skip("Hyperliquid account already has a position; not changing exposure.")


async def _skip_if_unfunded(client: Client) -> None:
    if await _account_value(client) <= 0:
        spot_usdc = await _spot_available_usdc(client)
        if spot_usdc < Decimal("2"):
            pytest.skip(
                "Hyperliquid perps accountValue is 0 and spot USDC is too low "
                f"for unified account margin: {spot_usdc}."
            )


def _order_statuses(order_response: dict) -> list[dict]:
    if not isinstance(order_response, dict):
        return []
    response = order_response.get("response", {})
    if not isinstance(response, dict):
        return []
    data = response.get("data", {})
    statuses = data.get("statuses", []) if isinstance(data, dict) else []
    return [status for status in statuses if isinstance(status, dict)]


def _extract_oid(order_response: dict) -> int | None:
    for status in _order_statuses(order_response):
        if isinstance(status, dict) and isinstance(status.get("resting"), dict):
            return int(status["resting"]["oid"])
    return None


def _order_error_message(order_response: dict) -> str | None:
    if not isinstance(order_response, dict):
        return None
    response = order_response.get("response")
    if isinstance(response, str):
        return response
    if not isinstance(response, dict):
        return None
    errors = [status.get("error") for status in _order_statuses(order_response)]
    messages = [error for error in errors if isinstance(error, str)]
    return "; ".join(messages) if messages else None


def _filled_size(order_response: dict) -> Decimal:
    sizes = []
    for status in _order_statuses(order_response):
        filled = status.get("filled")
        if isinstance(filled, dict) and filled.get("totalSz") is not None:
            sizes.append(Decimal(str(filled["totalSz"])))
    if sizes:
        return sum(sizes, Decimal("0"))

    message = _order_error_message(order_response)
    pytest.fail(
        f"Hyperliquid order was not filled: {message or order_response}",
        pytrace=False,
    )


def _fail_if_api_wallet_missing(order_response: dict) -> None:
    message = _order_error_message(order_response)
    if message and "User or API Wallet" in message and "does not exist" in message:
        pytest.fail("Hyperliquid API wallet does not exist for this account.", pytrace=False)


async def _cancel_open_orders(client: Client) -> None:
    for order in await _open_orders(client):
        oid = order.get("oid")
        coin = order.get("coin")
        if oid is None:
            continue
        product_symbol = SPOT_SYMBOL if coin == "PURR" else SYMBOL
        await client.cancel_order(product_symbol=product_symbol, oid=int(oid))
    await asyncio.sleep(2)


async def _spot_post_only_buy_price(client: Client) -> str:
    best_bid = Decimal(
        str((await client.get_l2book(product_symbol=SPOT_SYMBOL))["levels"][0][0]["px"])
    )
    return _format_hyperliquid_price(best_bid * Decimal("0.8"), ROUND_DOWN)


async def _spot_post_only_buy(client: Client) -> tuple[str, str]:
    price = Decimal(await _spot_post_only_buy_price(client))
    size = int((SPOT_ORDER_NOTIONAL / price).to_integral_value(rounding=ROUND_DOWN))
    return str(max(size, 1)), format(price, "f")


async def _spot_aggressive_buy(client: Client) -> tuple[str, str]:
    best_ask = Decimal(
        str((await client.get_l2book(product_symbol=SPOT_SYMBOL))["levels"][1][0]["px"])
    )
    price = Decimal(_format_hyperliquid_price(best_ask * Decimal("1.025"), ROUND_UP))
    size = int((SPOT_ORDER_NOTIONAL / price).to_integral_value(rounding=ROUND_DOWN))
    return str(size), format(price, "f")


async def _spot_aggressive_sell_price(client: Client, size: Decimal | None = None) -> str:
    bids = (await client.get_l2book(product_symbol=SPOT_SYMBOL))["levels"][0]
    target = size or Decimal("1")
    cumulative = Decimal("0")
    price = Decimal(str(bids[0]["px"]))
    for level in bids:
        price = Decimal(str(level["px"]))
        cumulative += Decimal(str(level["sz"]))
        if cumulative >= target:
            break
    return _format_hyperliquid_price(price * Decimal("0.975"), ROUND_DOWN)


async def _close_spot_test_delta(
    client: Client,
    before: Decimal,
    remaining: Decimal,
) -> None:
    for _ in range(3):
        available_delta = max(await _spot_available(client, "PURR") - before, Decimal("0"))
        sell_size = int(available_delta)
        if sell_size <= 0:
            if remaining > 0:
                await asyncio.sleep(1)
                remaining = Decimal("0")
                continue
            return

        sell = await client.place_order(
            product_symbol=SPOT_SYMBOL,
            isBuy=False,
            price=await _spot_aggressive_sell_price(client, Decimal(sell_size)),
            size=str(sell_size),
            reduceOnly=False,
            tif="Ioc",
            cloid=_cloid(),
        )
        _assert_exchange_response(sell)
        assert _filled_size(sell) > 0
        await asyncio.sleep(2)
        remaining = Decimal("0")

    assert await _spot_available(client, "PURR") - before < Decimal("1")


async def _close_btc_position(client: Client) -> None:
    position_size = await _btc_position_size(client)
    if position_size == 0:
        return
    size = format(abs(position_size).normalize(), "f")
    if position_size > 0:
        _assert_exchange_response(
            await client.place_future_market_sell_order(product_symbol=SYMBOL, size=size)
        )
    else:
        _assert_exchange_response(
            await client.place_future_market_buy_order(product_symbol=SYMBOL, size=size)
        )

    for _ in range(10):
        await asyncio.sleep(1)
        if await _btc_position_size(client) == 0:
            return
    pytest.fail("Hyperliquid BTC position did not close after market reduce.", pytrace=False)


@pytest.mark.asyncio
@pytest.mark.private
async def test_signed_account_actions_that_do_not_require_margin(client):
    _assert_exchange_response(await client.schedule_cancel(time=None))
    _assert_exchange_response(
        await client.update_leverage(product_symbol=SYMBOL, isCross=True, leverage=10)
    )
    _assert_exchange_response(
        await client.update_isolate_margin(product_symbol=SYMBOL, isBuy=True, ntli=0)
    )


@pytest.mark.asyncio
@pytest.mark.private
async def test_signed_error_response_trade_endpoints(client):
    cloid = _cloid()
    price = await _post_only_buy_price(client)
    size = _size()

    _assert_exchange_response(
        await client.place_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=price,
            size="0",
            reduceOnly=False,
            tif="Alo",
        )
    )
    _assert_exchange_response(
        await client.place_future_limit_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=price,
            size="0",
            tif="Alo",
        )
    )
    _assert_exchange_response(
        await client.place_future_limit_buy_order(
            product_symbol=SYMBOL,
            price=price,
            size="0",
            tif="Alo",
        )
    )
    _assert_exchange_response(
        await client.place_future_limit_sell_order(
            product_symbol=SYMBOL,
            price=await _post_only_sell_price(client),
            size="0",
            tif="Alo",
        )
    )
    _assert_exchange_response(
        await client.place_future_market_order(product_symbol=SYMBOL, isBuy=True, size="0")
    )
    _assert_exchange_response(
        await client.place_future_market_buy_order(product_symbol=SYMBOL, size="0")
    )
    _assert_exchange_response(
        await client.place_future_market_sell_order(product_symbol=SYMBOL, size="0")
    )
    _assert_exchange_response(await client.cancel_order(product_symbol=SYMBOL, oid=1))
    _assert_exchange_response(
        await client.cancel_order_by_cloid(product_symbol=SYMBOL, cloid=cloid)
    )
    _assert_exchange_response(
        await client.modify_order(
            oid=1,
            product_symbol=SYMBOL,
            isBuy=True,
            price=price,
            size=size,
            reduceOnly=False,
            tif="Alo",
        )
    )
    _assert_exchange_response(
        await client.modify_batch_orders(
            [
                {
                    "oid": 1,
                    "order": {
                        "a": _asset_id(client),
                        "b": True,
                        "p": price,
                        "s": size,
                        "r": False,
                        "t": {"limit": {"tif": "Alo"}},
                    },
                }
            ]
        )
    )
    _assert_exchange_response(
        await client.place_twap_order(
            product_symbol=SYMBOL,
            isBuy=True,
            size=size,
            reduceOnly=True,
            minutes=5,
            randomize=False,
        )
    )
    _assert_exchange_response(await client.cancel_twap_order(product_symbol=SYMBOL, twap_id=1))


@pytest.mark.asyncio
@pytest.mark.private
async def test_post_only_order_lifecycle(client):
    await _skip_if_account_state(client)
    await _skip_if_unfunded(client)

    oid = None
    cloid = _cloid()
    try:
        order = await client.place_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=await _post_only_buy_price(client),
            size=_size(),
            reduceOnly=False,
            tif="Alo",
            cloid=cloid,
        )
        oid = _extract_oid(order)
        assert oid is not None
        assert await client.order_status(user=await _account_user(client), oid=oid) is not None
        _assert_exchange_response(await client.cancel_order(product_symbol=SYMBOL, oid=oid))
        oid = None
    finally:
        if oid is not None:
            await client.cancel_order(product_symbol=SYMBOL, oid=oid)
        await _cancel_open_orders(client)


@pytest.mark.asyncio
@pytest.mark.private
async def test_limit_wrappers_and_cancel_by_cloid(client):
    await _skip_if_account_state(client)
    await _skip_if_unfunded(client)

    order_ids: list[int] = []
    try:
        for order in (
            await client.place_future_limit_order(
                product_symbol=SYMBOL,
                isBuy=True,
                price=await _post_only_buy_price(client),
                size=_size(),
                tif="Alo",
            ),
            await client.place_future_limit_buy_order(
                product_symbol=SYMBOL,
                price=await _post_only_buy_price(client),
                size=_size(),
                tif="Alo",
            ),
            await client.place_future_limit_sell_order(
                product_symbol=SYMBOL,
                price=await _post_only_sell_price(client),
                size=_size(),
                tif="Alo",
            ),
        ):
            oid = _extract_oid(order)
            assert oid is not None
            order_ids.append(oid)

        cloid = _cloid()
        order = await client.place_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=await _post_only_buy_price(client),
            size=_size(),
            reduceOnly=False,
            tif="Alo",
            cloid=cloid,
        )
        oid = _extract_oid(order)
        assert oid is not None
        order_ids.append(oid)
        _assert_exchange_response(
            await client.cancel_order_by_cloid(product_symbol=SYMBOL, cloid=cloid)
        )
        order_ids.remove(oid)
    finally:
        for oid in order_ids:
            await client.cancel_order(product_symbol=SYMBOL, oid=oid)
        await _cancel_open_orders(client)


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_post_only_order_lifecycle(client):
    if await _open_orders(client):
        pytest.skip("Hyperliquid account already has open orders; not touching unrelated orders.")
    if await _spot_available_usdc(client) < SPOT_REQUIRED_USDC:
        pytest.skip("Insufficient spot USDC for Hyperliquid spot post-only order.")

    oid = None
    try:
        size, price = await _spot_post_only_buy(client)
        order = await client.place_order(
            product_symbol=SPOT_SYMBOL,
            isBuy=True,
            price=price,
            size=size,
            reduceOnly=False,
            tif="Alo",
            cloid=_cloid(),
        )
        oid = _extract_oid(order)
        if oid is None:
            _fail_if_api_wallet_missing(order)
            pytest.fail(f"Hyperliquid did not rest spot post-only order: {order}", pytrace=False)
    finally:
        if oid is not None:
            await client.cancel_order(product_symbol=SPOT_SYMBOL, oid=oid)
        await _cancel_open_orders(client)


@pytest.mark.asyncio
@pytest.mark.private
async def test_spot_market_round_trip(client):
    if await _open_orders(client):
        pytest.skip("Hyperliquid account already has open orders; not touching unrelated orders.")
    if await _spot_available_usdc(client) < SPOT_REQUIRED_USDC:
        pytest.skip("Insufficient spot USDC for Hyperliquid spot market round-trip.")

    before = await _spot_available(client, "PURR")
    bought_size = Decimal("0")
    sold_size = Decimal("0")
    sell_submitted = False
    sell_outcome_known = False
    try:
        size, price = await _spot_aggressive_buy(client)
        buy = await client.place_order(
            product_symbol=SPOT_SYMBOL,
            isBuy=True,
            price=price,
            size=size,
            reduceOnly=False,
            tif="Ioc",
            cloid=_cloid(),
        )
        _assert_exchange_response(buy)
        bought_size = _filled_size(buy)
        await asyncio.sleep(2)
        sell_size = int(bought_size)
        assert sell_size > 0
        sell_submitted = True
        sell = await client.place_order(
            product_symbol=SPOT_SYMBOL,
            isBuy=False,
            price=await _spot_aggressive_sell_price(client, Decimal(sell_size)),
            size=str(sell_size),
            reduceOnly=False,
            tif="Ioc",
            cloid=_cloid(),
        )
        _assert_exchange_response(sell)
        if _order_error_message(sell) is not None:
            sell_outcome_known = True
        sold_size = _filled_size(sell)
        sell_outcome_known = True
        assert sold_size > 0
        await asyncio.sleep(2)
        remaining = max(await _spot_available(client, "PURR") - before, Decimal("0"))
        if remaining >= Decimal("1"):
            await _close_spot_test_delta(client, before, remaining)
        assert await _spot_available(client, "PURR") - before < Decimal("1")
    finally:
        try:
            remaining = max(await _spot_available(client, "PURR") - before, Decimal("0"))
            if remaining > 0 and (not sell_submitted or sell_outcome_known):
                await _close_spot_test_delta(client, before, remaining)
        finally:
            await _cancel_open_orders(client)


@pytest.mark.asyncio
@pytest.mark.private
async def test_modify_order_wrappers(client):
    await _skip_if_account_state(client)
    await _skip_if_unfunded(client)

    oid = None
    try:
        order = await client.place_future_limit_buy_order(
            product_symbol=SYMBOL,
            price=await _post_only_buy_price(client),
            size=_size(),
            tif="Alo",
        )
        oid = _extract_oid(order)
        if oid is None:
            pytest.skip(f"Hyperliquid did not rest modify source order: {order}")
        new_price = str(int(Decimal(await _post_only_buy_price(client)) * Decimal("0.99")))
        _assert_exchange_response(
            await client.modify_order(
                oid=oid,
                product_symbol=SYMBOL,
                isBuy=True,
                price=new_price,
                size=_size(),
                reduceOnly=False,
                tif="Alo",
            )
        )
        _assert_exchange_response(
            await client.modify_batch_orders(
                [
                    {
                        "oid": oid,
                        "order": {
                            "a": _asset_id(client),
                            "b": True,
                            "p": await _post_only_buy_price(client),
                            "s": _size(),
                            "r": False,
                            "t": {"limit": {"tif": "Alo"}},
                        },
                    }
                ]
            )
        )
    finally:
        if oid is not None:
            await client.cancel_order(product_symbol=SYMBOL, oid=oid)
        await _cancel_open_orders(client)


@pytest.mark.asyncio
@pytest.mark.private
async def test_market_wrapper_buy_and_sell_are_reachable_when_funded(client):
    await _skip_if_account_state(client)
    await _skip_if_unfunded(client)

    try:
        _assert_exchange_response(
            await client.place_future_market_buy_order(product_symbol=SYMBOL, size=_size())
        )
        await _close_btc_position(client)
        assert await _btc_position_size(client) == 0

        _assert_exchange_response(
            await client.place_future_market_sell_order(product_symbol=SYMBOL, size=_size())
        )
        await _close_btc_position(client)
        assert await _btc_position_size(client) == 0
    finally:
        await _cancel_open_orders(client)
        await _close_btc_position(client)
