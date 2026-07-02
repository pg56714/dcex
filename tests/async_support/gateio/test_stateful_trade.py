# ruff: noqa: ANN001, ANN201, D100, D103

import asyncio
import os
import uuid
from dataclasses import dataclass
from decimal import ROUND_DOWN, ROUND_UP, Decimal

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.gateio.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

GATEIO_API_KEY = os.getenv("GATEIO_API_KEY")
GATEIO_API_SECRET = os.getenv("GATEIO_API_SECRET")
SPOT_SYMBOL = "BTC-USDT-SPOT"
FUTURES_SYMBOL = "BTC-USDT-SWAP"
FUTURES_LEVERAGE = "2"
SPOT_NOTIONAL_BUFFER = Decimal("1.05")
MIN_FUTURES_AVAILABLE_USDT = Decimal("1")
SPOT_ACCOUNT = "spot"
FUTURES_ACCOUNT = "futures"
TRANSFER_STEP = Decimal("0.00000001")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.private,
    pytest.mark.stateful,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_TRADING_TESTS") != "1",
        reason="Set RUN_LIVE_TRADING_TESTS=1 to run real Gate order tests.",
    ),
]


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=GATEIO_API_KEY,
        api_secret=GATEIO_API_SECRET,
        timeout=20,
    ) as client_instance:
        await _cleanup(client_instance, Decimal("0"))
        try:
            yield client_instance
        finally:
            await _cleanup(client_instance, Decimal("0"))


def _dec(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        value = default
    return Decimal(str(value))


def _round_to_step(value: Decimal, step: Decimal, rounding: str) -> Decimal:
    if step <= 0:
        return value
    return (value / step).to_integral_value(rounding=rounding) * step


def _fmt(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _text() -> str:
    return f"t-dcex-{uuid.uuid4().hex[:20]}"


@dataclass(frozen=True)
class _TransferBack:
    from_account: str
    to_account: str
    amount: Decimal


def _items(res: object) -> list[dict]:
    if isinstance(res, list):
        return [item for item in res if isinstance(item, dict)]
    if isinstance(res, dict):
        data = res.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict) and isinstance(data.get("items"), list):
            return [item for item in data["items"] if isinstance(item, dict)]
    return []


def _first_price(level: object) -> Decimal:
    if isinstance(level, dict):
        return _dec(level.get("p", level.get("price")))
    if isinstance(level, list | tuple) and level:
        return _dec(level[0])
    return Decimal("0")


async def _spot_available(client: Client, currency: str) -> Decimal:
    account = await client.get_spot_account(ccy=currency)
    return sum((_dec(item.get("available")) for item in _items(account)), Decimal("0"))


async def _wait_for_spot_delta(client: Client, before: Decimal) -> Decimal:
    for _ in range(10):
        delta = await _spot_available(client, "BTC") - before
        if delta > 0:
            return delta
        await asyncio.sleep(1)
    return Decimal("0")


async def _futures_available_usdt(client: Client) -> Decimal:
    account = await client.get_futures_account()
    data = account.get("data", account) if isinstance(account, dict) else account
    if not isinstance(data, dict):
        return Decimal("0")
    for key in ("available_margin", "available_balance", "availableBalance", "available"):
        if key in data:
            return _dec(data.get(key))
    return Decimal("0")


async def _account_usdt(client: Client, account: str) -> Decimal:
    if account == SPOT_ACCOUNT:
        return await _spot_available(client, "USDT")
    if account == FUTURES_ACCOUNT:
        return await _futures_available_usdt(client)
    return Decimal("0")


async def _wallet_transfer(
    client: Client,
    from_account: str,
    to_account: str,
    amount: Decimal,
) -> None:
    amount = _round_to_step(amount, TRANSFER_STEP, ROUND_DOWN)
    if amount <= 0:
        return
    response = await client.wallet_transfer(
        currency="USDT",
        from_account=from_account,
        to_account=to_account,
        amount=_fmt(amount),
        settle="usdt",
    )
    assert response is not None


async def _return_transfer(client: Client, transfer: _TransferBack) -> None:
    if transfer.amount <= 0:
        return
    amount = min(transfer.amount, await _account_usdt(client, transfer.from_account))
    if amount <= 0:
        return
    await _wallet_transfer(client, transfer.from_account, transfer.to_account, amount)


async def _return_transfers(client: Client, transfers: list[_TransferBack]) -> None:
    for transfer in reversed(transfers):
        await _return_transfer(client, transfer)


async def _ensure_usdt(
    client: Client,
    target_account: str,
    source_account: str,
    required: Decimal,
) -> _TransferBack:
    target = await _account_usdt(client, target_account)
    if target >= required:
        return _TransferBack(target_account, source_account, Decimal("0"))

    needed = _round_to_step(required - target, TRANSFER_STEP, ROUND_UP)
    source = await _account_usdt(client, source_account)
    if source < needed:
        pytest.fail(
            "Insufficient transferable Gate USDT for stateful order test: "
            f"required={required}, {target_account}={target}, {source_account}={source}.",
            pytrace=False,
        )

    try:
        await _wallet_transfer(client, source_account, target_account, needed)
    except FailedRequestError as exc:
        pytest.fail(
            f"Gate wallet transfer {source_account}->{target_account} failed: {exc}",
            pytrace=False,
        )
    await asyncio.sleep(2)

    transfer = _TransferBack(target_account, source_account, needed)
    if await _account_usdt(client, target_account) < required:
        await _return_transfer(client, transfer)
        pytest.fail(
            f"Gate {target_account} USDT remains insufficient after transfer: required={required}.",
            pytrace=False,
        )
    return transfer


async def _position_size(client: Client) -> Decimal:
    data = await client.get_contract_single_positions(product_symbol=FUTURES_SYMBOL)
    data = data.get("data", data) if isinstance(data, dict) else data
    if not isinstance(data, dict):
        return Decimal("0")
    return _dec(data.get("size", data.get("value", "0")))


async def _position_leverage(client: Client) -> str:
    data = await client.get_contract_single_positions(product_symbol=FUTURES_SYMBOL)
    data = data.get("data", data) if isinstance(data, dict) else data
    if isinstance(data, dict) and data.get("leverage"):
        return str(data["leverage"])
    return FUTURES_LEVERAGE


async def _spot_open_orders(client: Client) -> list[dict]:
    return _items(await client.get_spot_open_orders())


async def _futures_open_orders(client: Client) -> list[dict]:
    return _items(
        await client.get_contract_order_list(
            status="open",
            product_symbol=FUTURES_SYMBOL,
        )
    )


async def _delivery_product_symbol(client: Client) -> str | None:
    for contract in _items(await client.get_all_delivery_contracts()):
        if not contract.get("in_delisting") and contract.get("name"):
            return "-".join(str(contract["name"]).split("_")) + "-SWAP"
    return None


async def _skip_if_existing_state(client: Client) -> None:
    await _cleanup(client, Decimal("0"))


async def _cleanup(client: Client, initial_spot_btc: Decimal) -> None:
    if await _spot_open_orders(client):
        await client.cancel_spot_order(product_symbol=SPOT_SYMBOL)
        await asyncio.sleep(1)

    if await _futures_open_orders(client):
        await client.cancel_contract_all_order_matched(product_symbol=FUTURES_SYMBOL)
        await asyncio.sleep(1)

    await _close_position(client)
    await _cleanup_spot_btc(client, initial_spot_btc)

    if await _spot_open_orders(client):
        pytest.fail("Gate spot still has open orders after cleanup.", pytrace=False)
    if await _futures_open_orders(client):
        pytest.fail("Gate futures still has open orders after cleanup.", pytrace=False)
    if await _position_size(client) != 0:
        pytest.fail("Gate futures position still exists after cleanup.", pytrace=False)
    _, step, _, _ = _spot_details(client)
    if await _spot_available(client, "BTC") - initial_spot_btc > step:
        pytest.fail("Gate BTC spot balance still exists after cleanup.", pytrace=False)


def _spot_details(client: Client) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    details = client.ptm.get_trading_details("gateio", SPOT_SYMBOL)
    tick = _dec(details["price_precision"], "0.01")
    step = _dec(details["size_precision"], "0.00000001")
    min_size = _dec(details["min_size"], "0.00001")
    min_notional = max(_dec(details["min_notional"], "3"), Decimal("3"))
    return tick, step, min_size, min_notional


async def _spot_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = await client.get_spot_order_book(product_symbol=SPOT_SYMBOL, limit=5)
    data = data.get("data", data) if isinstance(data, dict) else data
    bids = data.get("bids", []) if isinstance(data, dict) else []
    asks = data.get("asks", []) if isinstance(data, dict) else []
    return _first_price(bids[0]), _first_price(asks[0])


async def _spot_post_only_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    price = _round_to_step(min(best_bid - tick, best_bid * Decimal("0.999")), tick, ROUND_DOWN)
    amount = _round_to_step(min_notional * SPOT_NOTIONAL_BUFFER / price, step, ROUND_UP)
    return _fmt(max(amount, min_size)), _fmt(price)


async def _spot_fillable_buy_params(client: Client) -> tuple[str, str]:
    tick, step, min_size, min_notional = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    price = _round_to_step(max(best_ask + tick, best_ask * Decimal("1.01")), tick, ROUND_UP)
    amount = _round_to_step(min_notional * SPOT_NOTIONAL_BUFFER / price, step, ROUND_UP)
    return _fmt(max(amount, min_size)), _fmt(price)


async def _spot_fillable_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    best_bid, _ = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(best_bid - tick, tick, ROUND_DOWN))


async def _spot_post_only_sell_price(client: Client) -> str:
    tick, _, _, _ = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    return _fmt(_round_to_step(max(best_ask + tick, best_ask * Decimal("1.001")), tick, ROUND_UP))


async def _spot_market_buy_amount(client: Client) -> Decimal:
    _, step, min_size, min_notional = _spot_details(client)
    _, best_ask = await _spot_orderbook_prices(client)
    min_sell_amount = _round_to_step(
        max(min_size, min_notional / best_ask) * SPOT_NOTIONAL_BUFFER,
        step,
        ROUND_UP,
    )
    return (min_sell_amount + step) * best_ask * SPOT_NOTIONAL_BUFFER


def _spot_sell_amount(client: Client, amount: Decimal) -> str:
    _, step, _, _ = _spot_details(client)
    return _fmt(_round_to_step(amount, step, ROUND_DOWN))


async def _cleanup_spot_btc(client: Client, initial_spot_btc: Decimal) -> None:
    _, step, min_size, min_notional = _spot_details(client)
    delta = await _spot_available(client, "BTC") - initial_spot_btc
    if delta <= step:
        return

    sell_amount = Decimal(_spot_sell_amount(client, delta))
    best_bid, _ = await _spot_orderbook_prices(client)
    transfer = _TransferBack(SPOT_ACCOUNT, FUTURES_ACCOUNT, Decimal("0"))
    try:
        if sell_amount < min_size or sell_amount * best_bid < min_notional:
            quote_amount = await _spot_market_buy_amount(client)
            transfer = await _ensure_spot_usdt(client, quote_amount)
            assert (
                await client.place_spot_market_buy_order(SPOT_SYMBOL, _fmt(quote_amount))
                is not None
            )
            await asyncio.sleep(2)
            sell_amount = Decimal(
                _spot_sell_amount(client, await _spot_available(client, "BTC") - initial_spot_btc)
            )

        if sell_amount > 0:
            assert (
                await client.place_spot_market_sell_order(
                    SPOT_SYMBOL,
                    amount=_fmt(sell_amount),
                )
                is not None
            )
            await asyncio.sleep(2)
    finally:
        await _return_transfer(client, transfer)


async def _ensure_spot_usdt(client: Client, required: Decimal) -> _TransferBack:
    return await _ensure_usdt(client, SPOT_ACCOUNT, FUTURES_ACCOUNT, required)


async def _contract_orderbook_prices(client: Client) -> tuple[Decimal, Decimal]:
    data = await client.get_contract_order_book(product_symbol=FUTURES_SYMBOL, limit=5)
    data = data.get("data", data) if isinstance(data, dict) else data
    bids = data.get("bids", []) if isinstance(data, dict) else []
    asks = data.get("asks", []) if isinstance(data, dict) else []
    return _first_price(bids[0]), _first_price(asks[0])


async def _futures_order_params(client: Client) -> tuple[int, str, Decimal]:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    min_size = max(_dec(details["min_size"], "1"), Decimal("1"))
    ticker = await client.get_contract_list_tickers(product_symbol=FUTURES_SYMBOL)
    ticker_data = _items(ticker)
    last_price = _dec(ticker_data[0].get("last")) if ticker_data else Decimal("0")
    if last_price <= 0:
        _, asks_price = await _contract_orderbook_prices(client)
        last_price = asks_price
    best_bid, _ = await _contract_orderbook_prices(client)
    price = _round_to_step(min(best_bid - tick, best_bid * Decimal("0.999")), tick, ROUND_DOWN)
    return int(min_size), _fmt(price), last_price


async def _contract_fillable_buy_price(client: Client) -> str:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    _, best_ask = await _contract_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _contract_fillable_sell_price(client: Client) -> str:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    best_bid, _ = await _contract_orderbook_prices(client)
    return _fmt(_round_to_step(best_bid - tick, tick, ROUND_DOWN))


async def _contract_post_only_sell_price(client: Client) -> str:
    details = client.ptm.get_trading_details("gateio", FUTURES_SYMBOL)
    tick = _dec(details["price_precision"], "0.1")
    _, best_ask = await _contract_orderbook_prices(client)
    return _fmt(_round_to_step(best_ask + tick, tick, ROUND_UP))


async def _ensure_futures_usdt(client: Client) -> _TransferBack:
    return await _ensure_usdt(
        client,
        FUTURES_ACCOUNT,
        SPOT_ACCOUNT,
        MIN_FUTURES_AVAILABLE_USDT,
    )


def _skip_if_futures_margin_insufficient(exc: FailedRequestError) -> None:
    message = str(exc).lower()
    if "insufficient_available" in message or "insufficient" in message:
        pytest.fail(
            f"Insufficient Gate futures USDT for stateful order test: {exc}",
            pytrace=False,
        )
    raise exc


async def _futures_order_or_skip(awaitable) -> object:
    try:
        return await awaitable
    except FailedRequestError as exc:
        _skip_if_futures_margin_insufficient(exc)


async def _wait_for_position(client: Client, sign: int) -> Decimal:
    for _ in range(8):
        size = await _position_size(client)
        if sign > 0 and size > 0:
            return size
        if sign < 0 and size < 0:
            return size
        await asyncio.sleep(1)
    return Decimal("0")


async def _close_position(client: Client) -> None:
    size = await _position_size(client)
    if size > 0:
        await client.place_contract_order(
            product_symbol=FUTURES_SYMBOL,
            size=-int(abs(size)),
            price="0",
            tif="ioc",
            reduce_only=True,
        )
    elif size < 0:
        await client.place_contract_order(
            product_symbol=FUTURES_SYMBOL,
            size=int(abs(size)),
            price="0",
            tif="ioc",
            reduce_only=True,
        )
    await asyncio.sleep(2)
    assert await _position_size(client) == 0


async def test_spot_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    transfers: list[_TransferBack] = []
    try:
        amount, price = await _spot_post_only_buy_params(client)
        transfers.append(await _ensure_spot_usdt(client, Decimal(amount) * Decimal(price)))

        order_id = None
        try:
            order = await client.place_spot_order(
                SPOT_SYMBOL,
                side="buy",
                order_type="limit",
                amount=amount,
                price=price,
                time_in_force="poc",
                text=_text(),
            )
            order_id = str(order["id"])
            assert await client.get_spot_single_order(order_id, SPOT_SYMBOL) is not None
            amended_price = _fmt(Decimal(price) * Decimal("0.99"))
            assert (
                await client.amend_spot_single_order(
                    order_id,
                    product_symbol=SPOT_SYMBOL,
                    price=amended_price,
                )
                is not None
            )
            assert await client.cancel_spot_single_order(order_id, SPOT_SYMBOL) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        order_id = None
        try:
            order = await client.place_spot_limit_order(SPOT_SYMBOL, "buy", amount, price)
            order_id = str(order["id"])
            assert await client.cancel_spot_order(product_symbol=SPOT_SYMBOL) is not None
            order_id = None
            await asyncio.sleep(1)
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        order_id = None
        try:
            order = await client.place_spot_post_only_limit_order(SPOT_SYMBOL, "buy", amount, price)
            order_id = str(order["id"])
            assert await client.cancel_spot_single_order(order_id, SPOT_SYMBOL) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        order_id = None
        try:
            order = await client.place_spot_post_only_limit_buy_order(SPOT_SYMBOL, amount, price)
            order_id = str(order["id"])
            assert await client.cancel_spot_single_order(order_id, SPOT_SYMBOL) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)

        quote_amount = await _spot_market_buy_amount(client)
        transfers.append(await _ensure_spot_usdt(client, quote_amount))
        before_btc = await _spot_available(client, "BTC")
        assert await client.place_spot_market_buy_order(SPOT_SYMBOL, _fmt(quote_amount)) is not None
        acquired = await _wait_for_spot_delta(client, before_btc)
        sell_amount = _spot_sell_amount(client, acquired)
        assert Decimal(sell_amount) > 0
        assert await client.place_spot_market_sell_order(SPOT_SYMBOL, sell_amount) is not None
        await asyncio.sleep(2)

        quote_amount = await _spot_market_buy_amount(client)
        transfers.append(await _ensure_spot_usdt(client, quote_amount))
        before_btc = await _spot_available(client, "BTC")
        assert (
            await client.place_spot_market_order(SPOT_SYMBOL, "buy", _fmt(quote_amount)) is not None
        )
        acquired = await _wait_for_spot_delta(client, before_btc)
        sell_amount = _spot_sell_amount(client, acquired)
        assert Decimal(sell_amount) > 0
        assert await client.place_spot_market_order(SPOT_SYMBOL, "sell", sell_amount) is not None
        await asyncio.sleep(2)

        fill_amount, fill_price = await _spot_fillable_buy_params(client)
        transfers.append(
            await _ensure_spot_usdt(client, Decimal(fill_amount) * Decimal(fill_price))
        )
        before_btc = await _spot_available(client, "BTC")
        try:
            assert (
                await client.place_spot_limit_buy_order(SPOT_SYMBOL, fill_amount, fill_price)
                is not None
            )
            acquired = await _wait_for_spot_delta(client, before_btc)
            sell_amount = _spot_sell_amount(client, acquired)
            if Decimal(sell_amount) <= 0:
                pytest.fail("Gate spot fillable limit buy did not fill before timeout.")
            assert (
                await client.place_spot_limit_sell_order(
                    SPOT_SYMBOL,
                    sell_amount,
                    await _spot_fillable_sell_price(client),
                )
                is not None
            )
            await asyncio.sleep(2)
        finally:
            if await _spot_open_orders(client):
                await client.cancel_spot_order(product_symbol=SPOT_SYMBOL)
            remaining = await _spot_available(client, "BTC") - before_btc
            sell_amount = _spot_sell_amount(client, remaining)
            if Decimal(sell_amount) > 0:
                await client.place_spot_market_sell_order(SPOT_SYMBOL, sell_amount)

        quote_amount = await _spot_market_buy_amount(client)
        transfers.append(await _ensure_spot_usdt(client, quote_amount))
        before_btc = await _spot_available(client, "BTC")
        order_id = None
        try:
            assert (
                await client.place_spot_market_buy_order(SPOT_SYMBOL, _fmt(quote_amount))
                is not None
            )
            acquired = await _wait_for_spot_delta(client, before_btc)
            sell_amount = _spot_sell_amount(client, acquired)
            assert Decimal(sell_amount) > 0
            order = await client.place_spot_post_only_limit_sell_order(
                SPOT_SYMBOL,
                sell_amount,
                await _spot_post_only_sell_price(client),
            )
            order_id = str(order["id"])
            assert await client.get_spot_order_list(SPOT_SYMBOL, status="open") is not None
        finally:
            if order_id is not None:
                await client.cancel_spot_single_order(order_id, SPOT_SYMBOL)
            remaining = await _spot_available(client, "BTC") - before_btc
            sell_amount = _spot_sell_amount(client, remaining)
            if Decimal(sell_amount) > 0:
                await client.place_spot_market_sell_order(SPOT_SYMBOL, sell_amount)

        assert (
            await client.get_spot_trading_history(product_symbol=SPOT_SYMBOL, limit=10) is not None
        )
    finally:
        await _cleanup(client, initial_btc)
        await _return_transfers(client, transfers)


async def test_futures_stateful_order_lifecycle(client):
    await _skip_if_existing_state(client)
    initial_btc = await _spot_available(client, "BTC")
    transfers: list[_TransferBack] = []
    try:
        size, price, _ = await _futures_order_params(client)
        transfers.append(await _ensure_futures_usdt(client))

        assert await client.get_futures_all_positions(holding=False) is not None
        assert await client.get_contract_single_positions(product_symbol=FUTURES_SYMBOL) is not None
        assert (
            await client.update_futures_positions_leverage(
                product_symbol=FUTURES_SYMBOL,
                leverage=await _position_leverage(client),
            )
            is not None
        )

        order_id = None
        try:
            order = await _futures_order_or_skip(
                client.place_contract_order(
                    product_symbol=FUTURES_SYMBOL,
                    size=size,
                    price=price,
                    tif="poc",
                    text=_text(),
                )
            )
            order_id = str(order["id"])
            assert await client.get_contract_single_order(order_id) is not None
            amended_price = _fmt(Decimal(price) * Decimal("0.99"))
            assert (
                await client.amend_futures_single_order(order_id, price=amended_price) is not None
            )
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await _futures_order_or_skip(
                client.place_contract_limit_order(FUTURES_SYMBOL, size, price)
            )
            order_id = str(order["id"])
            assert (
                await client.cancel_contract_all_order_matched(product_symbol=FUTURES_SYMBOL)
                is not None
            )
            order_id = None
            await asyncio.sleep(1)
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await _futures_order_or_skip(
                client.place_contract_post_only_limit_order(FUTURES_SYMBOL, size, price)
            )
            order_id = str(order["id"])
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await _futures_order_or_skip(
                client.place_contract_post_only_limit_buy_order(
                    FUTURES_SYMBOL,
                    size,
                    price,
                )
            )
            order_id = str(order["id"])
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        order_id = None
        try:
            order = await _futures_order_or_skip(
                client.place_contract_post_only_limit_sell_order(
                    FUTURES_SYMBOL,
                    size,
                    await _contract_post_only_sell_price(client),
                )
            )
            order_id = str(order["id"])
            assert await client.cancel_contract_single_order(order_id) is not None
            order_id = None
        finally:
            if order_id is not None:
                await client.cancel_contract_single_order(order_id)

        batch = await _futures_order_or_skip(
            client.place_futures_batch_order(
                [
                    {
                        "product_symbol": FUTURES_SYMBOL,
                        "size": size,
                        "price": price,
                        "tif": "poc",
                        "text": _text(),
                    }
                ]
            )
        )
        assert batch is not None
        assert (
            await client.cancel_contract_all_order_matched(product_symbol=FUTURES_SYMBOL)
            is not None
        )

        assert (
            await _futures_order_or_skip(client.place_contract_market_order(FUTURES_SYMBOL, size))
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await _futures_order_or_skip(
                client.place_contract_market_buy_order(FUTURES_SYMBOL, size)
            )
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await _futures_order_or_skip(
                client.place_contract_market_sell_order(FUTURES_SYMBOL, size)
            )
            is not None
        )
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert (
            await _futures_order_or_skip(
                client.place_contract_limit_buy_order(
                    FUTURES_SYMBOL,
                    size,
                    await _contract_fillable_buy_price(client),
                )
            )
            is not None
        )
        assert await _wait_for_position(client, sign=1) > 0
        await _close_position(client)

        assert (
            await _futures_order_or_skip(
                client.place_contract_limit_sell_order(
                    FUTURES_SYMBOL,
                    size,
                    await _contract_fillable_sell_price(client),
                )
            )
            is not None
        )
        assert await _wait_for_position(client, sign=-1) < 0
        await _close_position(client)

        assert (
            await client.get_contract_order_list(
                status="finished",
                product_symbol=FUTURES_SYMBOL,
            )
            is not None
        )
        assert await client.get_trading_history(product_symbol=FUTURES_SYMBOL, limit=10) is not None
        assert (
            await client.get_futures_position_close_history(
                product_symbol=FUTURES_SYMBOL,
                limit=10,
            )
            is not None
        )
        assert (
            await client.get_futures_auto_deleveraging_history(
                product_symbol=FUTURES_SYMBOL,
                limit=10,
            )
            is not None
        )
        assert await client.get_delivery_all_positions() is not None
        delivery_symbol = await _delivery_product_symbol(client)
        if delivery_symbol is not None:
            assert (
                await client.get_delivery_position_close_history(
                    product_symbol=delivery_symbol,
                    limit=10,
                )
                is not None
            )
    finally:
        await _cleanup(client, initial_btc)
        await _return_transfers(client, transfers)

    assert not (await _spot_open_orders(client))
    assert not (await _futures_open_orders(client))
    assert await _position_size(client) == 0
