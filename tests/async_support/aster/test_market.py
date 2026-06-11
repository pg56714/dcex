# ruff: noqa: ANN001, ANN201, D100, D103

import pytest
import pytest_asyncio

from dcex.async_support.aster.client import Client
from dcex.async_support.product_table.fetch import aster as fetch_aster_products


@pytest_asyncio.fixture
async def client():
    async with Client(preload_product_table=False, timeout=20) as client_instance:
        yield client_instance


def _market(exchange_info: object, preferred: str) -> dict:
    assert isinstance(exchange_info, dict)
    symbols = [
        market
        for market in exchange_info.get("symbols", [])
        if isinstance(market, dict) and market.get("status") == "TRADING"
    ]
    assert symbols
    return next(
        (market for market in symbols if market.get("symbol") == preferred),
        symbols[0],
    )


@pytest.mark.asyncio
async def test_connectivity_and_exchange_info(client):
    assert isinstance(await client.ping_spot(), dict)
    assert isinstance(await client.ping_futures(), dict)
    assert isinstance(await client.get_spot_server_time(), dict)
    assert isinstance(await client.get_futures_server_time(), dict)
    assert _market(await client.get_spot_exchange_info(), "BTCUSDT")
    assert _market(await client.get_futures_exchange_info(), "BTCUSDT")


@pytest.mark.asyncio
async def test_spot_public_market_data(client):
    market = _market(await client.get_spot_exchange_info(), "BTCUSDT")
    symbol = str(market["symbol"])

    assert isinstance(await client.get_spot_exchange_info(symbol), dict)
    assert isinstance(await client.get_spot_orderbook(symbol, limit=5), dict)
    assert isinstance(await client.get_spot_recent_trades(symbol, limit=5), list)
    assert isinstance(await client.get_spot_historical_trades(symbol, limit=5), list)
    assert isinstance(await client.get_spot_agg_trades(symbol, limit=5), list)
    assert isinstance(await client.get_spot_klines(symbol, interval="1m", limit=5), list)
    assert isinstance(await client.get_spot_ticker_24hr(symbol), dict)
    assert isinstance(await client.get_spot_ticker_price(symbol), dict)
    assert isinstance(await client.get_spot_book_ticker(symbol), dict)
    assert isinstance(
        await client.get_spot_withdraw_fee(chainId="56", asset="USDT"),
        dict,
    )


@pytest.mark.asyncio
async def test_futures_public_market_data(client):
    market = _market(await client.get_futures_exchange_info(), "BTCUSDT")
    symbol = str(market["symbol"])
    pair = str(market.get("pair") or symbol)

    assert isinstance(await client.get_futures_orderbook(symbol, limit=5), dict)
    assert isinstance(await client.get_futures_recent_trades(symbol, limit=5), list)
    assert isinstance(await client.get_futures_historical_trades(symbol, limit=5), list)
    assert isinstance(await client.get_futures_agg_trades(symbol, limit=5), list)
    assert isinstance(await client.get_futures_klines(symbol, interval="1m", limit=5), list)
    assert isinstance(
        await client.get_futures_index_price_klines(pair, interval="1m", limit=5),
        list,
    )
    assert isinstance(
        await client.get_futures_mark_price_klines(symbol, interval="1m", limit=5),
        list,
    )
    assert isinstance(await client.get_futures_premium_index(symbol), dict)
    assert isinstance(await client.get_futures_funding_rate(symbol, limit=5), list)
    assert isinstance(await client.get_futures_funding_info(symbol), list | dict)
    assert isinstance(await client.get_futures_ticker_24hr(symbol), dict)
    assert isinstance(await client.get_futures_ticker_price(symbol), dict)
    assert isinstance(await client.get_futures_book_ticker(symbol), dict)
    assert isinstance(await client.get_futures_index_references(symbol), list | dict)


@pytest.mark.asyncio
async def test_product_table_fetch():
    table = await fetch_aster_products()
    assert table.height > 0
    assert {"spot", "swap"}.issubset(set(table["product_type"].to_list()))
