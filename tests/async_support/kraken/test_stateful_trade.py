# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import asyncio
import os
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.kraken.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

KRAKEN_SPOT_API_KEY = os.getenv("KRAKEN_SPOT_API_KEY")
KRAKEN_SPOT_API_SECRET = os.getenv("KRAKEN_SPOT_API_SECRET")
KRAKEN_FUTURES_API_KEY = os.getenv("KRAKEN_FUTURES_API_KEY")
KRAKEN_FUTURES_API_SECRET = os.getenv("KRAKEN_FUTURES_API_SECRET")
SPOT_QUOTES = ("USDT", "USDC", "USD")
FUTURES_SYMBOL = "BTC-USD-SWAP"
FUTURES_EXCHANGE_SYMBOL = "PF_XBTUSD"
SPOT_TRANSFER_AMOUNT = Decimal("1")
FUTURES_TRANSFER_AMOUNT = Decimal("0.1")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Kraken order and transfer tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        spot_api_key=KRAKEN_SPOT_API_KEY,
        spot_api_secret=KRAKEN_SPOT_API_SECRET,
        futures_api_key=KRAKEN_FUTURES_API_KEY,
        futures_api_secret=KRAKEN_FUTURES_API_SECRET,
    ) as client_instance:
        yield client_instance


def _dec(value, default="0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _assert_spot_ok(response):
    assert isinstance(response, dict)
    assert response.get("error", []) == []
    assert "result" in response
    return response


def _assert_futures_ok(response):
    assert isinstance(response, dict)
    assert response.get("result") == "success", response
    return response


async def _spot_balances(client: Client) -> dict:
    result = _assert_spot_ok(await client.get_spot_account_balance()).get("result", {})
    return result if isinstance(result, dict) else {}


async def _spot_available(client: Client, asset: str) -> Decimal:
    aliases = {"BTC": ("XXBT", "XBT", "BTC"), "USD": ("ZUSD", "USD")}
    balances = await _spot_balances(client)
    for name in aliases.get(asset, (asset,)):
        if name in balances:
            return _dec(balances[name])
    return Decimal("0")


def _spot_details(client: Client, product_symbol: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("kraken", product_symbol)
    return (
        _dec(details.get("price_precision"), "0.01"),
        _dec(details.get("size_precision"), "0.00000001"),
        _dec(details.get("min_size"), "0.00001"),
        max(_dec(details.get("min_notional"), "1"), Decimal("1")),
    )


async def _spot_prices(client: Client, product_symbol: str) -> tuple[Decimal, Decimal]:
    result = (await client.get_spot_orderbook(product_symbol, count=5)).get("result", {})
    assert isinstance(result, dict) and result
    book = next(iter(result.values()))
    return _dec(book["bids"][0][0]), _dec(book["asks"][0][0])


async def _spot_symbol_with_funds(client: Client) -> tuple[str, str, Decimal, Decimal, Decimal]:
    for quote in SPOT_QUOTES:
        if await _spot_available(client, quote) <= 0:
            continue
        product_symbol = f"BTC-{quote}-SPOT"
        with suppress(Exception):
            client.ptm.get_exchange_symbol("kraken", product_symbol)
            _, ask = await _spot_prices(client, product_symbol)
            _, step, min_size, min_notional = _spot_details(client, product_symbol)
            volume = max(
                _round_to_step(min_notional * Decimal("1.01") / ask, step, ROUND_UP),
                min_size,
            )
            if await _spot_available(client, quote) >= volume * ask * Decimal("1.01"):
                return product_symbol, quote, step, min_size, volume
    pytest.skip("Insufficient Kraken spot quote balance for BTC spot order tests.")


async def _spot_limit_buy_params(client: Client) -> tuple[str, str, str]:
    product_symbol, quote, _, _, _ = await _spot_symbol_with_funds(client)
    tick, step, min_size, min_notional = _spot_details(client, product_symbol)
    bid, _ = await _spot_prices(client, product_symbol)
    price = _round_to_step(min(bid - tick, bid * Decimal("0.999")), tick, ROUND_DOWN)
    volume = max(
        _round_to_step(min_notional * Decimal("1.01") / price, step, ROUND_UP),
        min_size,
    )
    if await _spot_available(client, quote) < price * volume:
        pytest.skip("Insufficient Kraken spot quote balance for post-only order.")
    return product_symbol, _fmt(volume), _fmt(price)


async def _spot_high_sell_price(client: Client, product_symbol: str) -> str:
    tick, _, _, _ = _spot_details(client, product_symbol)
    _, ask = await _spot_prices(client, product_symbol)
    return _fmt(_round_to_step(ask + tick, tick, ROUND_UP))


def _spot_txid(response) -> str:
    txids = _assert_spot_ok(response).get("result", {}).get("txid", [])
    assert txids, response
    return str(txids[0])


async def _cancel_spot(client: Client, txid: str) -> None:
    try:
        _assert_spot_ok(await client.cancel_spot_order(txid=txid))
    except FailedRequestError as exc:
        if "Unknown order" not in str(exc):
            raise
    await asyncio.sleep(0.5)


async def _skip_if_spot_open_orders(client: Client) -> None:
    open_orders = (
        _assert_spot_ok(await client.get_spot_open_orders()).get("result", {}).get("open", {})
    )
    if open_orders:
        pytest.skip("Kraken spot already has open orders; not touching unrelated orders.")


async def _futures_accounts(client: Client) -> dict:
    accounts = _assert_futures_ok(await client.get_futures_accounts()).get("accounts", {})
    return accounts if isinstance(accounts, dict) else {}


async def _futures_flex_available(client: Client) -> Decimal:
    flex = (await _futures_accounts(client)).get("flex", {})
    return _dec(flex.get("availableMargin")) if isinstance(flex, dict) else Decimal("0")


async def _futures_cash_available(client: Client, unit: str) -> Decimal:
    cash = (await _futures_accounts(client)).get("cash", {})
    balances = cash.get("balances", {}) if isinstance(cash, dict) else {}
    item = balances.get(unit.lower(), {}) if isinstance(balances, dict) else {}
    if not isinstance(item, dict):
        return Decimal("0")
    for key in ("available", "balance", "amount"):
        if key in item:
            return _dec(item[key])
    return Decimal("0")


async def _ensure_futures_margin(client: Client, required: Decimal = Decimal("0.5")) -> Decimal:
    if await _futures_flex_available(client) >= required:
        return Decimal("0")
    needed = required - await _futures_flex_available(client)
    amount = needed.quantize(Decimal("0.00000001"), rounding=ROUND_UP)
    if await _futures_cash_available(client, "usdt") < amount:
        pytest.skip("Insufficient Kraken Futures cash USDT to fund flex margin.")
    _assert_futures_ok(
        await client.futures_wallet_transfer(
            amount=_fmt(amount),
            fromAccount="cash",
            toAccount="flex",
            unit="USDT",
        )
    )
    await asyncio.sleep(2)
    if await _futures_flex_available(client) < required:
        pytest.skip("Kraken Futures flex margin remains insufficient after transfer.")
    return amount


async def _return_futures_margin(client: Client, amount: Decimal) -> None:
    if amount <= 0:
        return
    transfer_amount = min(amount, await _futures_flex_available(client)).quantize(
        Decimal("0.00000001"),
        rounding=ROUND_DOWN,
    )
    if transfer_amount <= 0:
        return
    _assert_futures_ok(
        await client.futures_wallet_transfer(
            amount=_fmt(transfer_amount),
            fromAccount="flex",
            toAccount="cash",
            unit="USDT",
        )
    )


async def _futures_position_size(client: Client) -> Decimal:
    response = _assert_futures_ok(await client.get_futures_open_positions())
    positions = response.get("openPositions") or response.get("positions") or []
    total = Decimal("0")
    if not isinstance(positions, list):
        return total
    for item in positions:
        if not isinstance(item, dict):
            continue
        if item.get("symbol") and item.get("symbol") != FUTURES_EXCHANGE_SYMBOL:
            continue
        for key in ("size", "qty", "quantity"):
            if key in item:
                total += _dec(item[key])
                break
    return total


async def _skip_if_futures_state(client: Client) -> None:
    open_orders = _assert_futures_ok(await client.get_futures_open_orders()).get("openOrders", [])
    if open_orders:
        pytest.skip("Kraken Futures already has open orders; not touching unrelated orders.")
    if await _futures_position_size(client) != 0:
        pytest.skip("Kraken Futures already has a BTC position; not changing unrelated exposure.")


def _futures_min_size(client: Client) -> Decimal:
    details = client.ptm.get_trading_details("kraken", FUTURES_SYMBOL)
    step = _dec(details.get("size_precision"), "0.0001")
    min_size = max(_dec(details.get("min_size"), "0.0001"), step)
    return _round_to_step(min_size, step, ROUND_UP)


async def _futures_order_params(client: Client, side: str) -> tuple[str, str]:
    tick = Decimal("0.5")
    book = _assert_futures_ok(await client.get_futures_orderbook(FUTURES_SYMBOL)).get(
        "orderBook",
        {},
    )
    bids = book.get("bids", []) if isinstance(book, dict) else []
    asks = book.get("asks", []) if isinstance(book, dict) else []
    assert bids and asks
    if side == "buy":
        price = _round_to_step(_dec(bids[0][0]) - tick, tick, ROUND_DOWN)
    else:
        price = _round_to_step(_dec(asks[0][0]) + tick, tick, ROUND_UP)
    return _fmt(_futures_min_size(client)), _fmt(price)


def _futures_order_id(response) -> str:
    send_status = _assert_futures_ok(response).get("sendStatus", {})
    order_id = send_status.get("order_id") if isinstance(send_status, dict) else None
    assert order_id, response
    return str(order_id)


async def _cancel_futures(client: Client, order_id: str) -> None:
    _assert_futures_ok(await client.cancel_futures_order(order_id=order_id))
    await asyncio.sleep(0.5)


def _is_kraken_service_unavailable(exc: FailedRequestError) -> bool:
    return str(exc.status_code) == "503" or "ErrCode: 503" in str(exc)


async def _wait_for_spot_floor(client: Client, currency: str, floor: Decimal) -> bool:
    for delay in (0, 1, 2, 3, 4, 5):
        if delay:
            await asyncio.sleep(delay)
        if await _spot_available(client, currency) >= floor:
            return True
    return False


async def _withdraw_futures_to_spot_safely(
    client: Client,
    *,
    amount: str,
    currency: str,
    sourceWallet: str,
    restored_spot_floor: Decimal | None = None,
) -> None:
    try:
        _assert_futures_ok(
            await client.withdraw_futures_to_spot_wallet(
                amount=amount,
                currency=currency,
                sourceWallet=sourceWallet,
            )
        )
    except FailedRequestError as exc:
        if (
            not _is_kraken_service_unavailable(exc)
            or restored_spot_floor is None
            or not await _wait_for_spot_floor(client, currency, restored_spot_floor)
        ):
            raise
        return

    if restored_spot_floor is not None:
        assert await _wait_for_spot_floor(client, currency, restored_spot_floor), (
            f"Kraken spot {currency} balance did not recover after Futures withdrawal."
        )


async def test_wallet_transfer_round_trip(client):
    initial_spot = await _spot_available(client, "USDT")
    if initial_spot < SPOT_TRANSFER_AMOUNT:
        pytest.skip("Insufficient Kraken spot USDT for Spot-to-Futures transfer round-trip.")

    transferred = False
    try:
        _assert_spot_ok(
            await client.wallet_transfer_to_futures(
                asset="USDT",
                amount=_fmt(SPOT_TRANSFER_AMOUNT),
                from_="Spot Wallet",
                to="Futures Wallet",
            )
        )
        transferred = True
        await asyncio.sleep(2)
        transferred = False
        await _withdraw_futures_to_spot_safely(
            client,
            amount=_fmt(SPOT_TRANSFER_AMOUNT),
            currency="USDT",
            sourceWallet="flex",
            restored_spot_floor=initial_spot,
        )
    finally:
        if transferred:
            with suppress(Exception):
                await _withdraw_futures_to_spot_safely(
                    client,
                    amount=_fmt(SPOT_TRANSFER_AMOUNT),
                    currency="USDT",
                    sourceWallet="flex",
                    restored_spot_floor=initial_spot,
                )
        await asyncio.sleep(2)


async def test_futures_internal_transfer_round_trip(client):
    if await _futures_flex_available(client) >= FUTURES_TRANSFER_AMOUNT:
        from_account, to_account = "flex", "cash"
    elif await _futures_cash_available(client, "usdt") >= FUTURES_TRANSFER_AMOUNT:
        from_account, to_account = "cash", "flex"
    else:
        pytest.skip("Insufficient Kraken Futures USDT for internal transfer round-trip.")

    _assert_futures_ok(
        await client.futures_wallet_transfer(
            amount=_fmt(FUTURES_TRANSFER_AMOUNT),
            fromAccount=from_account,
            toAccount=to_account,
            unit="USDT",
        )
    )
    await asyncio.sleep(2)
    _assert_futures_ok(
        await client.futures_wallet_transfer(
            amount=_fmt(FUTURES_TRANSFER_AMOUNT),
            fromAccount=to_account,
            toAccount=from_account,
            unit="USDT",
        )
    )


async def test_spot_post_only_order_lifecycle(client):
    await _skip_if_spot_open_orders(client)
    product_symbol, volume, price = await _spot_limit_buy_params(client)

    creators = (
        lambda: client.place_spot_limit_order(product_symbol, "buy", volume, price),
        lambda: client.place_spot_limit_buy_order(product_symbol, volume, price),
        lambda: client.place_spot_post_only_limit_order(product_symbol, "buy", volume, price),
        lambda: client.place_spot_post_only_limit_buy_order(product_symbol, volume, price),
    )
    for create_order in creators:
        txid = None
        try:
            txid = _spot_txid(await create_order())
            _assert_spot_ok(await client.get_spot_orders(txid=txid))
            assert (
                _assert_spot_ok(await client.get_spot_open_orders()).get("result", {}).get("open")
            )
        finally:
            if txid is not None:
                await _cancel_spot(client, txid)


async def test_spot_cancel_all_orders(client):
    await _skip_if_spot_open_orders(client)
    product_symbol, volume, price = await _spot_limit_buy_params(client)
    txid = None
    try:
        txid = _spot_txid(
            await client.place_spot_post_only_limit_buy_order(product_symbol, volume, price)
        )
        _assert_spot_ok(await client.cancel_spot_all_orders())
        txid = None
        await asyncio.sleep(1)
        open_orders = (await client.get_spot_open_orders()).get("result", {}).get("open", {})
        assert not open_orders
    finally:
        if txid is not None:
            await _cancel_spot(client, txid)


async def test_spot_market_round_trip_and_sell_wrappers(client):
    await _skip_if_spot_open_orders(client)
    product_symbol, _, step, min_size, volume = await _spot_symbol_with_funds(client)
    before = await _spot_available(client, "BTC")
    acquired = Decimal("0")
    try:
        _assert_spot_ok(await client.place_spot_market_order(product_symbol, "buy", _fmt(volume)))
        await asyncio.sleep(3)
        acquired = _round_to_step(await _spot_available(client, "BTC") - before, step, ROUND_DOWN)
        assert acquired >= min_size

        sell_price = await _spot_high_sell_price(client, product_symbol)
        for create_order in (
            lambda: client.place_spot_limit_sell_order(product_symbol, _fmt(acquired), sell_price),
            lambda: client.place_spot_post_only_limit_sell_order(
                product_symbol,
                _fmt(acquired),
                sell_price,
            ),
        ):
            txid = None
            try:
                txid = _spot_txid(await create_order())
            finally:
                if txid is not None:
                    await _cancel_spot(client, txid)

        _assert_spot_ok(await client.place_spot_market_sell_order(product_symbol, _fmt(acquired)))
        acquired = Decimal("0")
        await asyncio.sleep(3)

        before = await _spot_available(client, "BTC")
        _assert_spot_ok(await client.place_spot_market_buy_order(product_symbol, _fmt(volume)))
        await asyncio.sleep(3)
        acquired = _round_to_step(await _spot_available(client, "BTC") - before, step, ROUND_DOWN)
        assert acquired >= min_size
        _assert_spot_ok(
            await client.place_spot_market_order(product_symbol, "sell", _fmt(acquired))
        )
        acquired = Decimal("0")
    finally:
        leftover = _round_to_step(await _spot_available(client, "BTC") - before, step, ROUND_DOWN)
        cleanup_size = max(leftover, acquired)
        if cleanup_size >= min_size:
            with suppress(Exception):
                await client.place_spot_market_sell_order(product_symbol, _fmt(cleanup_size))

    _assert_spot_ok(await client.get_spot_closed_orders())
    _assert_spot_ok(await client.get_spot_trade_history())


async def test_futures_post_only_order_lifecycle(client):
    await _skip_if_futures_state(client)
    transferred = await _ensure_futures_margin(client)
    try:
        buy_size, buy_price = await _futures_order_params(client, "buy")
        for create_order in (
            lambda: client.place_futures_limit_order(FUTURES_SYMBOL, "buy", buy_size, buy_price),
            lambda: client.place_futures_limit_buy_order(FUTURES_SYMBOL, buy_size, buy_price),
            lambda: client.place_futures_post_only_limit_order(
                FUTURES_SYMBOL,
                "buy",
                buy_size,
                buy_price,
            ),
            lambda: client.place_futures_post_only_limit_buy_order(
                FUTURES_SYMBOL,
                buy_size,
                buy_price,
            ),
        ):
            order_id = None
            try:
                order_id = _futures_order_id(await create_order())
                _assert_futures_ok(await client.get_futures_order_status(orderIds=[order_id]))
                _assert_futures_ok(await client.get_futures_open_orders())
            finally:
                if order_id is not None:
                    await _cancel_futures(client, order_id)

        sell_size, sell_price = await _futures_order_params(client, "sell")
        for create_order in (
            lambda: client.place_futures_limit_sell_order(FUTURES_SYMBOL, sell_size, sell_price),
            lambda: client.place_futures_post_only_limit_sell_order(
                FUTURES_SYMBOL,
                sell_size,
                sell_price,
            ),
        ):
            order_id = None
            try:
                order_id = _futures_order_id(await create_order())
            finally:
                if order_id is not None:
                    await _cancel_futures(client, order_id)
    finally:
        await _return_futures_margin(client, transferred)


async def test_futures_cancel_all_orders(client):
    await _skip_if_futures_state(client)
    transferred = await _ensure_futures_margin(client)
    order_id = None
    try:
        size, price = await _futures_order_params(client, "buy")
        order_id = _futures_order_id(
            await client.place_futures_post_only_limit_buy_order(FUTURES_SYMBOL, size, price)
        )
        _assert_futures_ok(await client.cancel_futures_all_orders(product_symbol=FUTURES_SYMBOL))
        order_id = None
        await asyncio.sleep(1)
        assert not _assert_futures_ok(await client.get_futures_open_orders()).get("openOrders", [])
    finally:
        if order_id is not None:
            await _cancel_futures(client, order_id)
        await _return_futures_margin(client, transferred)


async def test_futures_market_round_trip(client):
    await _skip_if_futures_state(client)
    transferred = await _ensure_futures_margin(client)
    size = _fmt(_futures_min_size(client))
    try:
        _assert_futures_ok(await client.place_futures_market_order(FUTURES_SYMBOL, "buy", size))
        await asyncio.sleep(2)
        _assert_futures_ok(
            await client.place_futures_market_sell_order(
                FUTURES_SYMBOL,
                size,
                reduceOnly=True,
            )
        )
        await asyncio.sleep(2)
        assert await _futures_position_size(client) == 0

        _assert_futures_ok(await client.place_futures_market_buy_order(FUTURES_SYMBOL, size))
        await asyncio.sleep(2)
        _assert_futures_ok(
            await client.place_futures_market_order(
                FUTURES_SYMBOL,
                "sell",
                size,
                reduceOnly=True,
            )
        )
        await asyncio.sleep(2)
        assert await _futures_position_size(client) == 0
    finally:
        if await _futures_position_size(client) > 0:
            with suppress(Exception):
                await client.place_futures_market_sell_order(
                    FUTURES_SYMBOL,
                    size,
                    reduceOnly=True,
                )
        await _return_futures_margin(client, transferred)
