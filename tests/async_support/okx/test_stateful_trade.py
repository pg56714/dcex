# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import os
import uuid
from contextlib import suppress
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.okx.client import Client

load_dotenv()

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_API_SECRET = os.getenv("OKX_API_SECRET")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")
SPOT_SYMBOL = "BTC-USDT-SPOT"
SWAP_SYMBOL = "BTC-USDT-SWAP"
TRANSFER_AMOUNT = Decimal("0.1")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real OKX order and transfer tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=OKX_API_KEY,
        api_secret=OKX_API_SECRET,
        passphrase=OKX_PASSPHRASE,
    ) as client_instance:
        yield client_instance


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


async def _spot_available(client: Client, currency: str) -> Decimal:
    for account in _data(await client.get_account_balance(ccy=[currency])):
        details = account.get("details")
        if not isinstance(details, list):
            continue
        for item in details:
            if isinstance(item, dict) and item.get("ccy") == currency:
                return _dec(item.get("availBal"))
    return Decimal("0")


async def _funding_available(client: Client, currency: str) -> Decimal:
    for item in _data(await client.get_balances(ccy=[currency])):
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


async def _spot_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    books = _data(await client.get_orderbook(product_symbol=SPOT_SYMBOL, sz="5"))
    assert books
    bids = books[0].get("bids", [])
    asks = books[0].get("asks", [])
    assert bids and asks
    return _dec(bids[0][0]), _dec(asks[0][0])


async def _spot_post_only_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    price = _round_to_step(best_bid * Decimal("0.50"), tick, ROUND_DOWN)
    size = _round_to_step(min_notional * Decimal("1.5") / price, step, ROUND_UP)
    return _fmt(max(size, min_size)), _fmt(price)


async def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask * Decimal("1.50"), tick, ROUND_UP))


def _spot_sell_size(client: Client, size: Decimal) -> str:
    _, step, _, _ = _spot_details(client)
    return _fmt(_round_to_step(size, step, ROUND_DOWN))


def _spot_market_quote(client: Client) -> Decimal:
    _, _, _, min_notional = _spot_details(client)
    return max(min_notional * Decimal("2"), Decimal("2"))


async def _open_orders(client: Client, product_symbol: str) -> list[dict]:
    return _data(await client.get_order_list(product_symbol=product_symbol))


async def _swap_position_size(client: Client) -> Decimal:
    return sum(
        (
            _dec(item.get("pos"))
            for item in _data(await client.get_positions(product_symbol=SWAP_SYMBOL))
        ),
        Decimal("0"),
    )


async def _skip_if_existing_state(client: Client) -> None:
    if await _open_orders(client, SPOT_SYMBOL) or await _open_orders(client, SWAP_SYMBOL):
        pytest.skip("OKX already has open BTC orders; not touching unrelated orders.")
    if await _swap_position_size(client) != 0:
        pytest.skip("OKX BTC-USDT swap already has a position; not changing exposure.")


async def _ensure_trading_usdt(client: Client, required: Decimal) -> Decimal:
    available = await _spot_available(client, "USDT")
    if available >= required:
        return Decimal("0")
    needed = required - available
    if await _funding_available(client, "USDT") < needed:
        pytest.skip("Insufficient OKX USDT for stateful trading tests.")
    _assert_ok(
        await client.funds_transfer(
            ccy="USDT",
            amt=_fmt(needed),
            from_account="FUND",
            to_account="TRADING",
        )
    )
    await asyncio.sleep(2)
    if await _spot_available(client, "USDT") < required:
        pytest.skip("OKX trading USDT remains insufficient after transfer.")
    return needed


async def _return_to_funding(client: Client, transferred: Decimal) -> None:
    amount = min(transferred, await _spot_available(client, "USDT"))
    if amount <= 0:
        return
    _assert_ok(
        await client.funds_transfer(
            ccy="USDT",
            amt=_fmt(amount),
            from_account="TRADING",
            to_account="FUND",
        )
    )


async def _wait_for_spot_delta(client: Client, before: Decimal) -> Decimal:
    for _ in range(8):
        delta = await _spot_available(client, "BTC") - before
        if delta > 0:
            return delta
        await asyncio.sleep(1)
    return Decimal("0")


async def _wait_for_swap_position(client: Client) -> Decimal:
    for _ in range(8):
        size = await _swap_position_size(client)
        if size != 0:
            return size
        await asyncio.sleep(1)
    return Decimal("0")


async def _cancel_order(client: Client, order_id: str) -> None:
    _assert_ok(await client.cancel_order(product_symbol=SPOT_SYMBOL, ordId=order_id))


async def _cleanup(client: Client, initial_btc: Decimal) -> None:
    with suppress(Exception):
        if await _open_orders(client, SPOT_SYMBOL):
            _assert_ok(await client.cancel_all_orders(product_symbol=SPOT_SYMBOL))
    with suppress(Exception):
        if await _open_orders(client, SWAP_SYMBOL):
            _assert_ok(await client.cancel_all_orders(product_symbol=SWAP_SYMBOL))
    with suppress(Exception):
        if await _swap_position_size(client) != 0:
            _assert_ok(await client.close_positions(product_symbol=SWAP_SYMBOL, mgnMode="cross"))
            await asyncio.sleep(2)
    with suppress(Exception):
        delta = await _spot_available(client, "BTC") - initial_btc
        sell_size = _spot_sell_size(client, delta)
        if Decimal(sell_size) > 0:
            _assert_ok(
                await client.place_market_sell_order(
                    product_symbol=SPOT_SYMBOL,
                    tdMode="cash",
                    sz=sell_size,
                )
            )
            await asyncio.sleep(2)


async def test_funds_transfer_round_trip(client):
    funding = await _funding_available(client, "USDT")
    trading = await _spot_available(client, "USDT")
    if funding >= TRANSFER_AMOUNT:
        from_account, to_account = "FUND", "TRADING"
    elif trading >= TRANSFER_AMOUNT:
        from_account, to_account = "TRADING", "FUND"
    else:
        pytest.skip("Insufficient OKX USDT for transfer round-trip.")

    response = _assert_ok(
        await client.funds_transfer(
            ccy="USDT",
            amt=_fmt(TRANSFER_AMOUNT),
            from_account=from_account,
            to_account=to_account,
        )
    )
    transfer_id = str(_data(response)[0]["transId"])
    try:
        assert await client.get_transfer_state(transId=transfer_id) is not None
    finally:
        await asyncio.sleep(1)
        _assert_ok(
            await client.funds_transfer(
                ccy="USDT",
                amt=_fmt(TRANSFER_AMOUNT),
                from_account=to_account,
                to_account=from_account,
            )
        )


async def test_spot_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    transferred = Decimal("0")
    try:
        size, price = await _spot_post_only_buy_params(client)
        transferred += await _ensure_trading_usdt(
            client, Decimal(size) * Decimal(price) * Decimal("3")
        )

        order_id = None
        try:
            order_id = _order_id(
                await client.place_order(
                    product_symbol=SPOT_SYMBOL,
                    tdMode="cash",
                    side="buy",
                    ordType="post_only",
                    sz=size,
                    px=price,
                    clOrdId=_client_id(),
                )
            )
            assert await client.get_order(product_symbol=SPOT_SYMBOL, ordId=order_id) is not None
            amended_price = _fmt(Decimal(price) * Decimal("0.99"))
            _assert_ok(
                await client.amend_order(
                    product_symbol=SPOT_SYMBOL,
                    ordId=order_id,
                    newPx=amended_price,
                )
            )
            await _cancel_order(client, order_id)
            order_id = None
        finally:
            if order_id is not None:
                await _cancel_order(client, order_id)

        exchange_symbol = client.ptm.get_exchange_symbol("okx", SPOT_SYMBOL)
        batch = _assert_ok(
            await client.place_batch_orders(
                [
                    {
                        "instId": exchange_symbol,
                        "tdMode": "cash",
                        "side": "buy",
                        "ordType": "post_only",
                        "sz": size,
                        "px": price,
                        "clOrdId": _client_id(),
                    },
                    {
                        "instId": exchange_symbol,
                        "tdMode": "cash",
                        "side": "buy",
                        "ordType": "post_only",
                        "sz": size,
                        "px": _fmt(Decimal(price) * Decimal("0.98")),
                        "clOrdId": _client_id(),
                    },
                ]
            )
        )
        batch_ids = [str(item["ordId"]) for item in _data(batch)]
        try:
            _assert_ok(
                await client.amend_multiple_orders(
                    [
                        {
                            "instId": exchange_symbol,
                            "ordId": order_id,
                            "newPx": _fmt(Decimal(price) * Decimal("0.97")),
                        }
                        for order_id in batch_ids
                    ]
                )
            )
            _assert_ok(
                await client.cancel_batch_orders(
                    [{"instId": exchange_symbol, "ordId": order_id} for order_id in batch_ids]
                )
            )
            batch_ids = []
        finally:
            for order_id in batch_ids:
                with suppress(Exception):
                    await _cancel_order(client, order_id)

        creators = (
            lambda: client.place_limit_order(SPOT_SYMBOL, "cash", "buy", size, price),
            lambda: client.place_limit_buy_order(SPOT_SYMBOL, "cash", size, price),
            lambda: client.place_post_only_limit_order(SPOT_SYMBOL, "cash", "buy", size, price),
            lambda: client.place_post_only_limit_buy_order(SPOT_SYMBOL, "cash", size, price),
        )
        for create_order in creators:
            order_id = None
            try:
                order_id = _order_id(await create_order())
                await _cancel_order(client, order_id)
                order_id = None
            finally:
                if order_id is not None:
                    await _cancel_order(client, order_id)

        order_id = _order_id(await client.place_limit_buy_order(SPOT_SYMBOL, "cash", size, price))
        try:
            _assert_ok(await client.cancel_all_orders(product_symbol=SPOT_SYMBOL))
            order_id = None
        finally:
            if order_id is not None:
                await _cancel_order(client, order_id)

        quote = _spot_market_quote(client)
        transferred += await _ensure_trading_usdt(client, quote)
        before_btc = await _spot_available(client, "BTC")
        _assert_ok(await client.place_market_buy_order(SPOT_SYMBOL, "cash", _fmt(quote)))
        bought = await _wait_for_spot_delta(client, before_btc)
        assert bought > 0
        sell_size = _spot_sell_size(client, bought)

        sell_price = await _spot_post_only_sell_price(client)
        creators = (
            lambda: client.place_limit_sell_order(SPOT_SYMBOL, "cash", sell_size, sell_price),
            lambda: client.place_post_only_limit_sell_order(
                SPOT_SYMBOL, "cash", sell_size, sell_price
            ),
        )
        for create_order in creators:
            order_id = None
            try:
                order_id = _order_id(await create_order())
                await _cancel_order(client, order_id)
                order_id = None
            finally:
                if order_id is not None:
                    await _cancel_order(client, order_id)

        _assert_ok(await client.place_market_sell_order(SPOT_SYMBOL, "cash", sell_size))
        await asyncio.sleep(2)

        before_btc = await _spot_available(client, "BTC")
        _assert_ok(
            await client.place_market_order(
                product_symbol=SPOT_SYMBOL,
                tdMode="cash",
                side="buy",
                sz=_fmt(quote),
            )
        )
        bought = await _wait_for_spot_delta(client, before_btc)
        assert bought > 0
        _assert_ok(
            await client.place_market_order(
                product_symbol=SPOT_SYMBOL,
                tdMode="cash",
                side="sell",
                sz=_spot_sell_size(client, bought),
            )
        )
        await asyncio.sleep(2)

        assert await client.get_order_list(product_symbol=SPOT_SYMBOL) is not None
        assert (
            await client.get_orders_history(instType="SPOT", product_symbol=SPOT_SYMBOL) is not None
        )
        assert (
            await client.get_orders_history_archive(
                instType="SPOT",
                product_symbol=SPOT_SYMBOL,
            )
            is not None
        )
        assert await client.get_fills(instType="SPOT", product_symbol=SPOT_SYMBOL) is not None
        assert (
            await client.get_fills_history(
                instType="SPOT",
                product_symbol=SPOT_SYMBOL,
            )
            is not None
        )
        assert await client.get_account_rate_limit() is not None
    finally:
        await _cleanup(client, initial_btc)
        await _return_to_funding(client, transferred)


async def test_swap_close_position_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    transferred = Decimal("0")
    try:
        details = client.ptm.get_trading_details("okx", SWAP_SYMBOL)
        size = _fmt(max(_dec(details["min_size"], "0.01"), Decimal("0.01")))
        transferred += await _ensure_trading_usdt(client, Decimal("1"))
        _assert_ok(
            await client.place_market_buy_order(
                product_symbol=SWAP_SYMBOL,
                tdMode="cross",
                sz=size,
            )
        )
        assert await _wait_for_swap_position(client) != 0
        _assert_ok(await client.close_positions(product_symbol=SWAP_SYMBOL, mgnMode="cross"))
        await asyncio.sleep(2)
        assert await _swap_position_size(client) == 0
    finally:
        await _cleanup(client, initial_btc)
        await _return_to_funding(client, transferred)
