import pytest
import pytest_asyncio

from dcex.async_support.okx.client import Client


@pytest_asyncio.fixture
async def client():
    import asyncio

    client_instance = Client()
    await client_instance.async_init()
    yield client_instance
    await client_instance.close()
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_get_public_instruments(client):
    res = await client.get_public_instruments(instType="SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_funding_rate(client):
    res = await client.get_funding_rate(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_funding_rate_history(client):
    res = await client.get_funding_rate_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_open_interest(client):
    res = await client.get_open_interest(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_position_tiers(client):
    res = await client.get_position_tiers(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_trading_data_support_coin(client):
    res = await client.get_trading_data_support_coin()
    assert res is not None


@pytest.mark.asyncio
async def test_get_taker_volume(client):
    res = await client.get_taker_volume(ccy="BTC", instType="SPOT")
    assert res is not None


@pytest.mark.asyncio
async def test_get_contract_taker_volume(client):
    res = await client.get_contract_taker_volume(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_long_short_ratio(client):
    res = await client.get_long_short_ratio(ccy="BTC")
    assert res is not None


@pytest.mark.asyncio
async def test_get_contract_long_short_ratio(client):
    res = await client.get_contract_long_short_ratio(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_top_trader_long_short_account_ratio(client):
    res = await client.get_top_trader_long_short_account_ratio(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_top_trader_long_short_position_ratio(client):
    res = await client.get_top_trader_long_short_position_ratio(product_symbol="BTC-USDT-SWAP")
    assert res is not None


@pytest.mark.asyncio
async def test_get_contracts_open_interest_and_volume(client):
    res = await client.get_contracts_open_interest_and_volume(ccy="BTC")
    assert res is not None


@pytest.mark.asyncio
async def test_get_contract_open_interest_history(client):
    res = await client.get_contract_open_interest_history(product_symbol="BTC-USDT-SWAP")
    assert res is not None
