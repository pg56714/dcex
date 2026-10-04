# ruff: noqa: ANN001, ANN201, ANN202, D100, D103

from datetime import UTC, datetime, timedelta

import pytest

from dcex.async_support.okx.client import Client


def _assert_ok(response):
    assert response["code"] in ("0", 0), response
    assert "data" in response
    return response


@pytest.mark.asyncio
async def test_option_public_data_endpoints():
    async with Client(preload_product_table=False) as client:
        instruments = _assert_ok(
            await client.get_public_instruments("OPTION", instFamily="BTC-USD")
        )
        assert instruments["data"]
        _assert_ok(
            await client.get_delivery_exercise_history("OPTION", instFamily="BTC-USD", limit=20)
        )
        _assert_ok(await client.get_option_summary(instFamily="BTC-USD"))
        _assert_ok(await client.get_option_tick_bands(instFamily="BTC-USD"))
        _assert_ok(await client.get_option_trades(instFamily="BTC-USD"))
        _assert_ok(await client.get_option_family_trades("BTC-USD"))
        _assert_ok(await client.get_options_open_interest_and_volume("BTC"))
        _assert_ok(await client.get_option_put_call_ratio("BTC"))
        expiry_distribution = _assert_ok(
            await client.get_option_open_interest_and_volume_by_expiry("BTC")
        )
        cutoff = (datetime.now(UTC) + timedelta(days=1)).strftime("%Y%m%d")
        expiry_time = next(row[1] for row in expiry_distribution["data"] if row[1] > cutoff)
        _assert_ok(await client.get_option_open_interest_and_volume_by_strike("BTC", expiry_time))
        _assert_ok(await client.get_option_taker_block_volume("BTC"))


@pytest.mark.asyncio
async def test_option_market_endpoints():
    async with Client(preload_product_table=False) as client:
        instruments = _assert_ok(
            await client.get_public_instruments("OPTION", instFamily="BTC-USD")
        )
        live = [row for row in instruments["data"] if row["state"] == "live"]
        assert live
        symbol = min(live, key=lambda row: int(row["expTime"]))["instId"]

        estimated = _assert_ok(await client.get_estimated_delivery_price(symbol))
        assert estimated["data"][0]["instId"] == symbol
        assert "settlePx" in estimated["data"][0]

        tickers = _assert_ok(await client.get_tickers("OPTION", instFamily="BTC-USD"))
        assert tickers["data"]
        assert {"instId", "bidPx", "askPx"} <= tickers["data"][0].keys()

        marks = _assert_ok(await client.get_mark_price("OPTION", instrument_family="BTC-USD"))
        assert marks["data"]
        assert {"instId", "markPx"} <= marks["data"][0].keys()

        open_interest = _assert_ok(await client.get_open_interest("OPTION", instFamily="BTC-USD"))
        assert open_interest["data"]
        assert {"instId", "oi"} <= open_interest["data"][0].keys()
