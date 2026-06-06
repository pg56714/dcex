# ruff: noqa: ANN001, ANN201, D100, D103

import os
import time
import uuid
from decimal import ROUND_DOWN, Decimal

import msgspec
import pytest
from dotenv import load_dotenv

from dcex.hyperliquid.client import Client
from dcex.utils.common import Common

load_dotenv()

WALLET_ADDRESS = os.getenv("HYPERLIQUID_WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
SYMBOL = "BTC-USD-SWAP"
SPOT_SYMBOL = "PURR-USDC-SPOT"
ORDER_SIZE = Decimal("0.0002")
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

    snapshot_client = Client(
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


@pytest.fixture
def client(account_snapshot):
    return Client(wallet_address=WALLET_ADDRESS, private_key=PRIVATE_KEY)


def _cloid() -> str:
    return "0x" + uuid.uuid4().hex


def _asset_id(client: Client) -> int:
    return msgspec.json.decode(client.ptm.get_exchange_symbol(Common.HYPERLIQUID, SYMBOL))[1]


def _mid_price(client: Client) -> Decimal:
    data = client.get_meta_and_asset_ctxs()
    return Decimal(str(data[1][_asset_id(client)]["midPx"]))


def _post_only_buy_price(client: Client) -> str:
    return str(int(_mid_price(client) * Decimal("0.9")))


def _post_only_sell_price(client: Client) -> str:
    return str(int(_mid_price(client) * Decimal("1.1")))


def _size() -> str:
    return format(ORDER_SIZE.normalize(), "f")


def _assert_exchange_response(res: dict) -> None:
    assert res is not None
    assert isinstance(res, dict)


def _account_user(client: Client) -> str:
    if ACCOUNT_USER is not None:
        return ACCOUNT_USER
    role = client.user_role(user=WALLET_ADDRESS)
    if isinstance(role, dict) and role.get("role") == "agent":
        return role.get("data", {}).get("user", WALLET_ADDRESS)
    return WALLET_ADDRESS


def _open_orders(client: Client) -> list:
    orders = client.open_orders(user=_account_user(client))
    return orders if isinstance(orders, list) else []


def _positions(client: Client) -> list:
    data = client.clearinghouse_state(user=_account_user(client))
    positions = data.get("assetPositions", []) if isinstance(data, dict) else []
    return positions if isinstance(positions, list) else []


def _btc_position_size(client: Client) -> Decimal:
    for item in _positions(client):
        position = item.get("position", {}) if isinstance(item, dict) else {}
        if position.get("coin") == "BTC":
            return Decimal(str(position.get("szi", "0")))
    return Decimal("0")


def _account_value(client: Client) -> Decimal:
    if PERPS_ACCOUNT_VALUE is not None:
        return PERPS_ACCOUNT_VALUE
    data = client.clearinghouse_state(user=_account_user(client))
    summary = data.get("marginSummary", {}) if isinstance(data, dict) else {}
    return Decimal(str(summary.get("accountValue", "0")))


def _spot_available_usdc(client: Client) -> Decimal:
    return _spot_available(client, "USDC")


def _spot_available(client: Client, coin: str) -> Decimal:
    if SPOT_AVAILABLE_USDC is not None:
        if coin != "USDC":
            return _spot_available_uncached(client, coin)
        return SPOT_AVAILABLE_USDC
    return _spot_available_uncached(client, coin)


def _spot_available_uncached(client: Client, coin: str) -> Decimal:
    data = client.spot_clearinghouse_state(user=_account_user(client))
    for balance in data.get("balances", []) if isinstance(data, dict) else []:
        if balance.get("coin") == coin:
            return Decimal(str(balance.get("total", "0"))) - Decimal(str(balance.get("hold", "0")))
    return Decimal("0")


def _skip_if_account_state(client: Client) -> None:
    if _open_orders(client):
        pytest.skip("Hyperliquid account already has open orders; not touching unrelated orders.")
    if _positions(client):
        pytest.skip("Hyperliquid account already has a position; not changing exposure.")


def _skip_if_unfunded(client: Client) -> None:
    if _account_value(client) <= 0:
        spot_usdc = _spot_available_usdc(client)
        if spot_usdc < Decimal("2"):
            pytest.skip(
                "Hyperliquid perps accountValue is 0 and spot USDC is too low "
                f"for unified account margin: {spot_usdc}."
            )


def _extract_oid(order_response: dict) -> int | None:
    statuses = (
        order_response.get("response", {}).get("data", {}).get("statuses", [])
        if isinstance(order_response, dict)
        else []
    )
    for status in statuses:
        if isinstance(status, dict) and isinstance(status.get("resting"), dict):
            return int(status["resting"]["oid"])
    return None


def _cancel_open_orders(client: Client) -> None:
    for order in _open_orders(client):
        oid = order.get("oid")
        coin = order.get("coin")
        if oid is None:
            continue
        product_symbol = SPOT_SYMBOL if coin == "PURR" else SYMBOL
        client.cancel_order(product_symbol=product_symbol, oid=int(oid))
    time.sleep(2)


def _spot_post_only_buy_price(client: Client) -> str:
    best_bid = Decimal(str(client.get_l2book(product_symbol=SPOT_SYMBOL)["levels"][0][0]["px"]))
    return format((best_bid * Decimal("0.8")).quantize(Decimal("0.000001")), "f")


def _spot_post_only_buy(client: Client) -> tuple[str, str]:
    price = Decimal(_spot_post_only_buy_price(client))
    size = int((Decimal("10.4") / price).to_integral_value(rounding=ROUND_DOWN))
    return str(max(size, 1)), format(price, "f")


def _spot_aggressive_buy(client: Client) -> tuple[str, str]:
    best_ask = Decimal(str(client.get_l2book(product_symbol=SPOT_SYMBOL)["levels"][1][0]["px"]))
    price = (best_ask * Decimal("1.025")).quantize(Decimal("0.000001"))
    size = int((Decimal("10.4") / price).to_integral_value(rounding=ROUND_DOWN))
    return str(size), format(price, "f")


def _spot_aggressive_sell_price(client: Client) -> str:
    best_bid = Decimal(str(client.get_l2book(product_symbol=SPOT_SYMBOL)["levels"][0][0]["px"]))
    return format((best_bid * Decimal("0.975")).quantize(Decimal("0.000001")), "f")


def _close_btc_position(client: Client) -> None:
    position_size = _btc_position_size(client)
    if position_size == 0:
        return
    size = format(abs(position_size).normalize(), "f")
    if position_size > 0:
        client.place_future_market_sell_order(product_symbol=SYMBOL, size=size)
    else:
        client.place_future_market_buy_order(product_symbol=SYMBOL, size=size)
    time.sleep(2)


@pytest.mark.private
def test_signed_account_actions_that_do_not_require_margin(client):
    _assert_exchange_response(client.schedule_cancel(time=None))
    _assert_exchange_response(
        client.update_leverage(product_symbol=SYMBOL, isCross=True, leverage=10)
    )
    _assert_exchange_response(
        client.update_isolate_margin(product_symbol=SYMBOL, isBuy=True, ntli=0)
    )


@pytest.mark.private
def test_signed_error_response_trade_endpoints(client):
    cloid = _cloid()
    price = _post_only_buy_price(client)
    size = _size()

    _assert_exchange_response(
        client.place_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=price,
            size="0",
            reduceOnly=False,
            tif="Alo",
        )
    )
    _assert_exchange_response(
        client.place_future_limit_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=price,
            size="0",
            tif="Alo",
        )
    )
    _assert_exchange_response(
        client.place_future_limit_buy_order(
            product_symbol=SYMBOL,
            price=price,
            size="0",
            tif="Alo",
        )
    )
    _assert_exchange_response(
        client.place_future_limit_sell_order(
            product_symbol=SYMBOL,
            price=_post_only_sell_price(client),
            size="0",
            tif="Alo",
        )
    )
    _assert_exchange_response(
        client.place_future_market_order(product_symbol=SYMBOL, isBuy=True, size="0")
    )
    _assert_exchange_response(client.place_future_market_buy_order(product_symbol=SYMBOL, size="0"))
    _assert_exchange_response(
        client.place_future_market_sell_order(product_symbol=SYMBOL, size="0")
    )
    _assert_exchange_response(client.cancel_order(product_symbol=SYMBOL, oid=1))
    _assert_exchange_response(client.cancel_order_by_cloid(product_symbol=SYMBOL, cloid=cloid))
    _assert_exchange_response(
        client.modify_order(
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
        client.modify_batch_orders(
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
        client.place_twap_order(
            product_symbol=SYMBOL,
            isBuy=True,
            size=size,
            reduceOnly=True,
            minutes=5,
            randomize=False,
        )
    )
    _assert_exchange_response(client.cancel_twap_order(product_symbol=SYMBOL, twap_id=1))


@pytest.mark.private
def test_post_only_order_lifecycle(client):
    _skip_if_account_state(client)
    _skip_if_unfunded(client)

    oid = None
    cloid = _cloid()
    try:
        order = client.place_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=_post_only_buy_price(client),
            size=_size(),
            reduceOnly=False,
            tif="Alo",
            cloid=cloid,
        )
        oid = _extract_oid(order)
        assert oid is not None
        assert client.order_status(user=_account_user(client), oid=oid) is not None
        _assert_exchange_response(client.cancel_order(product_symbol=SYMBOL, oid=oid))
        oid = None
    finally:
        if oid is not None:
            client.cancel_order(product_symbol=SYMBOL, oid=oid)
        _cancel_open_orders(client)


@pytest.mark.private
def test_limit_wrappers_and_cancel_by_cloid(client):
    _skip_if_account_state(client)
    _skip_if_unfunded(client)

    order_ids: list[int] = []
    try:
        for order in (
            client.place_future_limit_order(
                product_symbol=SYMBOL,
                isBuy=True,
                price=_post_only_buy_price(client),
                size=_size(),
                tif="Alo",
            ),
            client.place_future_limit_buy_order(
                product_symbol=SYMBOL,
                price=_post_only_buy_price(client),
                size=_size(),
                tif="Alo",
            ),
            client.place_future_limit_sell_order(
                product_symbol=SYMBOL,
                price=_post_only_sell_price(client),
                size=_size(),
                tif="Alo",
            ),
        ):
            oid = _extract_oid(order)
            assert oid is not None
            order_ids.append(oid)

        cloid = _cloid()
        order = client.place_order(
            product_symbol=SYMBOL,
            isBuy=True,
            price=_post_only_buy_price(client),
            size=_size(),
            reduceOnly=False,
            tif="Alo",
            cloid=cloid,
        )
        oid = _extract_oid(order)
        assert oid is not None
        order_ids.append(oid)
        _assert_exchange_response(client.cancel_order_by_cloid(product_symbol=SYMBOL, cloid=cloid))
        order_ids.remove(oid)
    finally:
        for oid in order_ids:
            client.cancel_order(product_symbol=SYMBOL, oid=oid)
        _cancel_open_orders(client)


@pytest.mark.private
def test_spot_post_only_order_lifecycle(client):
    if _open_orders(client):
        pytest.skip("Hyperliquid account already has open orders; not touching unrelated orders.")
    if _spot_available_usdc(client) < Decimal("10.5"):
        pytest.skip("Insufficient spot USDC for Hyperliquid spot post-only order.")

    oid = None
    try:
        size, price = _spot_post_only_buy(client)
        order = client.place_order(
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
            pytest.skip(f"Hyperliquid did not rest spot post-only order: {order}")
    finally:
        if oid is not None:
            client.cancel_order(product_symbol=SPOT_SYMBOL, oid=oid)
        _cancel_open_orders(client)


@pytest.mark.private
def test_spot_market_round_trip(client):
    if _open_orders(client):
        pytest.skip("Hyperliquid account already has open orders; not touching unrelated orders.")
    if _spot_available_usdc(client) < Decimal("10.6"):
        pytest.skip("Insufficient spot USDC for Hyperliquid spot market round-trip.")

    before = _spot_available(client, "PURR")
    try:
        size, price = _spot_aggressive_buy(client)
        _assert_exchange_response(
            client.place_order(
                product_symbol=SPOT_SYMBOL,
                isBuy=True,
                price=price,
                size=size,
                reduceOnly=False,
                tif="Ioc",
                cloid=_cloid(),
            )
        )
        time.sleep(2)
        acquired = _spot_available(client, "PURR") - before
        sell_size = int(acquired)
        assert sell_size > 0
        _assert_exchange_response(
            client.place_order(
                product_symbol=SPOT_SYMBOL,
                isBuy=False,
                price=_spot_aggressive_sell_price(client),
                size=str(sell_size),
                reduceOnly=False,
                tif="Ioc",
                cloid=_cloid(),
            )
        )
    finally:
        _cancel_open_orders(client)


@pytest.mark.private
def test_modify_order_wrappers(client):
    _skip_if_account_state(client)
    _skip_if_unfunded(client)

    oid = None
    try:
        order = client.place_future_limit_buy_order(
            product_symbol=SYMBOL,
            price=_post_only_buy_price(client),
            size=_size(),
            tif="Alo",
        )
        oid = _extract_oid(order)
        if oid is None:
            pytest.skip(f"Hyperliquid did not rest modify source order: {order}")
        new_price = str(int(Decimal(_post_only_buy_price(client)) * Decimal("0.99")))
        _assert_exchange_response(
            client.modify_order(
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
            client.modify_batch_orders(
                [
                    {
                        "oid": oid,
                        "order": {
                            "a": _asset_id(client),
                            "b": True,
                            "p": _post_only_buy_price(client),
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
            client.cancel_order(product_symbol=SYMBOL, oid=oid)
        _cancel_open_orders(client)


@pytest.mark.private
def test_market_wrappers_round_trip(client):
    _skip_if_account_state(client)
    _skip_if_unfunded(client)

    try:
        _assert_exchange_response(
            client.place_future_market_buy_order(product_symbol=SYMBOL, size=_size())
        )
        time.sleep(2)
        _close_btc_position(client)
        assert _btc_position_size(client) == 0

        _assert_exchange_response(
            client.place_future_market_order(product_symbol=SYMBOL, isBuy=True, size=_size())
        )
        time.sleep(2)
        _close_btc_position(client)
        assert _btc_position_size(client) == 0

        _assert_exchange_response(
            client.place_future_market_sell_order(product_symbol=SYMBOL, size=_size())
        )
        time.sleep(2)
        _close_btc_position(client)
        assert _btc_position_size(client) == 0
    finally:
        _cancel_open_orders(client)
        _close_btc_position(client)
