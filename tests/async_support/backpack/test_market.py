# ruff: noqa: ANN001, ANN201, D100, D103

import time

import pytest
import pytest_asyncio

from dcex.async_support.backpack.client import Client


@pytest_asyncio.fixture
async def client():
    async with Client(preload_product_table=False) as client_instance:
        yield client_instance


async def _markets(client: Client) -> list[dict]:
    res = await client.get_markets()
    assert isinstance(res, list)
    assert res
    return res


async def _market_symbol(client: Client, market_type: str) -> str:
    market = next(
        market
        for market in await _markets(client)
        if market.get("visible") is not False
        and market.get("orderBookState") == "Open"
        and market.get("marketType") == market_type
    )
    return str(market["symbol"])


@pytest.mark.asyncio
async def test_get_assets_and_collateral(client):
    assert isinstance(await client.get_assets(), list)
    assert isinstance(await client.get_collateral(), list)


@pytest.mark.asyncio
async def test_get_borrow_lend_public_data(client):
    assert isinstance(await client.get_borrow_lend_markets(), list)
    assert isinstance(await client.get_borrow_lend_market_history(interval="1d"), list)
    assert isinstance(await client.get_borrow_lend_apy(), dict)


@pytest.mark.asyncio
async def test_get_market_metadata(client):
    spot_symbol = await _market_symbol(client, "SPOT")
    assert isinstance(await client.get_market(spot_symbol), dict)
    assert isinstance(await client.get_order_book_depth(spot_symbol, limit=5), dict)
    assert isinstance(await client.get_ticker(spot_symbol), dict)
    assert isinstance(await client.get_tickers(), list)


@pytest.mark.asyncio
async def test_get_public_trades_and_klines(client):
    spot_symbol = await _market_symbol(client, "SPOT")
    now = int(time.time())
    assert isinstance(
        await client.get_klines(
            spot_symbol,
            interval="1m",
            startTime=now - 3600,
            endTime=now,
        ),
        list,
    )
    assert isinstance(await client.get_recent_trades(spot_symbol, limit=5), list)
    assert isinstance(await client.get_historical_trades(spot_symbol, limit=5), list)


@pytest.mark.asyncio
async def test_get_futures_market_data(client):
    perp_symbol = await _market_symbol(client, "PERP")
    assert isinstance(await client.get_mark_prices(perp_symbol), list)
    assert isinstance(await client.get_open_interest(perp_symbol), list)
    assert isinstance(await client.get_funding_rates(perp_symbol, limit=5), list)


@pytest.mark.asyncio
async def test_get_system_public_data(client):
    assert isinstance(await client.get_status(), dict)
    assert await client.ping()
    assert await client.get_time()
    assert isinstance(await client.get_wallets(), list)


@pytest.mark.asyncio
async def test_get_securities_public_data(client):
    assert isinstance(await client.get_market_sessions(), list)
    assert isinstance(await client.get_securities(), list)
