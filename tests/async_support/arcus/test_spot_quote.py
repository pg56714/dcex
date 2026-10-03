"""Read-only asynchronous Arcus spot RFQ quote check: never submits a quote."""

import os

import pytest
from dotenv import load_dotenv

from dcex.async_support.arcus.spot import SpotClient

load_dotenv()

pytestmark = [pytest.mark.live, pytest.mark.private, pytest.mark.asyncio]

SELL_USDG = "10000000"  # 10 USDG in 6-decimal atomic units


def _token(tokens, symbol):
    rows = tokens if isinstance(tokens, list) else tokens.get("tokens", tokens.get("data", []))
    match = next(row for row in rows if isinstance(row, dict) and row.get("symbol") == symbol)
    return match.get("address") or match["token"]


async def test_spot_price_and_quote_without_submitting():
    wallet = os.environ["ARCUS_ADDRESS"]
    client = SpotClient(api_key=os.environ["ARCUS_API_KEY"], wallet_address=wallet)
    try:
        tokens = await client.get_tokens()
        usdg, nvda = _token(tokens, "USDG"), _token(tokens, "NVDA")
        price = await client.get_price(usdg, nvda, SELL_USDG)
        assert price["recommended"] and price["all"]
        quote = await client.get_quote(usdg, nvda, SELL_USDG, wallet, slippage_bps=100)
        assert quote["recommended"] and int(quote["all"][0]["buyAmount"]) > 0
    finally:
        await client.close()
