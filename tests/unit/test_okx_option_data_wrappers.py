"""Regression coverage for OKX option market-data wrappers."""
# ruff: noqa: ANN001, ANN202, D103

import pytest


class _SyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    def public_request_json(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"code": "0", "data": []}


class _AsyncNative:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[tuple[str, str]]]] = []

    async def public_request_json_async(self, method_name, params):
        self.calls.append((method_name, params))
        return 200, {}, {"code": "0", "data": []}


def test_sync_okx_option_data_wrappers_forward_official_fields() -> None:
    from dcex.okx.client import Client

    client = object.__new__(Client)
    native = _SyncNative()
    client._native_client = native

    client.get_delivery_exercise_history("OPTION", instFamily="BTC-USD", limit=20)
    client.get_option_summary(instFamily="BTC-USD", expTime="2000000000000")
    client.get_option_tick_bands(instFamily="BTC-USD")
    client.get_option_trades(instFamily="BTC-USD", optType="C")
    client.get_option_family_trades("BTC-USD")
    client.get_options_open_interest_and_volume("BTC")
    client.get_option_put_call_ratio("BTC")
    client.get_option_open_interest_and_volume_by_expiry("BTC")
    client.get_option_open_interest_and_volume_by_strike("BTC", "2000000000000")
    client.get_option_taker_block_volume("BTC")
    client.get_public_underlying("OPTION")

    assert native.calls[0] == (
        "get_delivery_exercise_history",
        [("instType", "OPTION"), ("instFamily", "BTC-USD"), ("limit", "20")],
    )
    assert native.calls[3][1] == [("instFamily", "BTC-USD"), ("optType", "C")]
    assert native.calls[8][1] == [
        ("ccy", "BTC"),
        ("expTime", "2000000000000"),
        ("period", "8H"),
    ]
    assert native.calls[-1] == ("get_public_underlying", [("instType", "OPTION")])


@pytest.mark.asyncio
async def test_async_okx_option_data_wrappers_forward_official_fields() -> None:
    from dcex.async_support.okx.client import Client

    client = object.__new__(Client)
    native = _AsyncNative()
    client._native_client = native

    await client.get_option_summary(uly="BTC-USD")
    await client.get_option_family_trades("BTC-USD")
    await client.get_option_put_call_ratio("BTC", period="1D")
    await client.get_option_open_interest_and_volume_by_strike(
        "BTC", "2000000000000", period="1D"
    )
    await client.get_public_underlying("OPTION")

    assert native.calls[0] == ("get_option_summary", [("uly", "BTC-USD")])
    assert native.calls[1] == ("get_option_family_trades", [("instFamily", "BTC-USD")])
    assert native.calls[-2][1][-1] == ("period", "1D")
    assert native.calls[-1] == ("get_public_underlying", [("instType", "OPTION")])
