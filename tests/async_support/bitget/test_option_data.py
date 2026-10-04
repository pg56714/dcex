# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv

from dcex.async_support.bitget.client import Client
from dcex.utils.errors import FailedRequestError

load_dotenv()

BITGET_API_KEY = os.getenv("BITGET_API_KEY")
BITGET_API_SECRET = os.getenv("BITGET_API_SECRET")
BITGET_PASSPHRASE = os.getenv("BITGET_PASSPHRASE")
UNDERLYING = "AAPL.US"

pytestmark = pytest.mark.private


@pytest_asyncio.fixture
async def client():
    async with Client(
        api_key=BITGET_API_KEY,
        api_secret=BITGET_API_SECRET,
        passphrase=BITGET_PASSPHRASE,
    ) as client_instance:
        yield client_instance


def _assert_ok(response) -> dict:
    assert isinstance(response, dict)
    assert response["code"] == "00000", response
    assert "data" in response
    return response["data"]


@pytest.mark.asyncio
async def test_stock_plus_option_quote_endpoints(client):
    try:
        raw = await client.stock_plus_options_quotes_get_option_expiry_date(symbol=UNDERLYING)
    except FailedRequestError as error:
        # Account eligibility, not a code fault: U.S. stock trading must be enabled first.
        if "U.S. stock trading is not enabled" in str(error):
            pytest.skip("Bitget account has U.S. stock trading disabled")
        raise
    expiries = _assert_ok(raw)
    expiry_dates = expiries["expiryDate"] if isinstance(expiries, dict) else expiries
    assert expiry_dates
    expiry_date = min(str(value) for value in expiry_dates)

    chain = _assert_ok(
        await client.stock_plus_options_quotes_get_option_chain_info(
            symbol=UNDERLYING, expiry_date=expiry_date
        )
    )
    strikes = chain["strikePriceInfo"] if isinstance(chain, dict) else chain
    assert strikes
    option_symbol = strikes[len(strikes) // 2]["callSymbol"]

    quotes = _assert_ok(
        await client.stock_plus_options_quotes_get_option_quote(symbol=option_symbol)
    )
    assert quotes
    quote = quotes[0] if isinstance(quotes, list) else quotes
    assert {"impliedVolatility", "strikePrice", "expiryDate"} <= quote.keys()

    volume = _assert_ok(await client.stock_plus_options_quotes_get_option_volume(symbol=UNDERLYING))
    assert {"c", "p"} <= volume.keys()
