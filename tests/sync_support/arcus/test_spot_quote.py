"""Read-only Arcus spot RFQ quote check: requests a price and a firm quote, never submits."""

import os

import pytest
from dotenv import load_dotenv

from dcex.arcus.spot import SpotClient

load_dotenv()

pytestmark = [pytest.mark.live, pytest.mark.private]

# Above Arcus' minimum trade notional (1 and 3 USDG were rejected as TRADE_NOTIONAL_BELOW_MINIMUM).
SELL_USDG = "10000000"  # 10 USDG in 6-decimal atomic units


def _token(tokens, symbol):
    rows = tokens if isinstance(tokens, list) else tokens.get("tokens", tokens.get("data", []))
    match = next(row for row in rows if isinstance(row, dict) and row.get("symbol") == symbol)
    return match.get("address") or match["token"]


def test_spot_price_and_quote_without_submitting():
    wallet = os.environ["ARCUS_ADDRESS"]
    client = SpotClient(api_key=os.environ["ARCUS_API_KEY"], wallet_address=wallet)
    try:
        tokens = client.get_tokens()
        usdg, nvda = _token(tokens, "USDG"), _token(tokens, "NVDA")
        price = client.get_price(usdg, nvda, SELL_USDG)
        assert price["recommended"] and price["all"]
        quote = client.get_quote(usdg, nvda, SELL_USDG, wallet, slippage_bps=100)
        assert quote["recommended"] and int(quote["all"][0]["buyAmount"]) > 0
        # submit_signed_quote is deliberately never called: it would execute a real trade.
    finally:
        client.close()
