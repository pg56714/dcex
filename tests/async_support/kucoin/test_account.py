import pytest
import pytest_asyncio
from dcex.async_support.kucoin.client import Client
import os
from dotenv import load_dotenv

load_dotenv()


KUCOIN_API_KEY = os.getenv("KUCOIN_API_KEY")
KUCOIN_API_SECRET = os.getenv("KUCOIN_API_SECRET")
KUCOIN_API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=KUCOIN_API_KEY,
        api_secret=KUCOIN_API_SECRET,
        passphrase=KUCOIN_API_PASSPHRASE,
    ) as client_instance:
        yield client_instance


@pytest.mark.asyncio
@pytest.mark.private
async def test_get_account_balance(client):
    res = await client.get_account_balance()
    assert res is not None
