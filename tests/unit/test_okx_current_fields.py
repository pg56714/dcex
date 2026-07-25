"""Regression coverage for current OKX REST parameter surfaces."""
# ruff: noqa: D103

from __future__ import annotations

import inspect
import json

import pytest

from tests.unit.endpoint_wrapper_helpers import (
    _client_class,
    _client_kwargs,
    _wire_async,
    _wire_sync,
)

CURRENT_FIELDS = {
    "get_account_instruments": {"seriesId", "instFamily", "product_symbol"},
    "get_positions": {"posId"},
    "get_positions_history": {"posId", "after", "before"},
    "get_account_bills": {"after", "before", "begin", "end"},
    "get_max_order_size": {"tradeQuoteCcy", "outcome"},
    "get_max_avail_size": {"tradeQuoteCcy"},
    "get_max_loan": {"tradeQuoteCcy"},
    "get_spot_fee_rates": {"product_symbol", "instFamily", "groupId"},
    "get_interest_accrued": {"type"},
    "get_interest_limits": {"type"},
    "funds_transfer": {"loanTrans", "omitPosRisk", "clientId"},
    "get_bills": {"ccy", "thirdPartyType"},
    "get_candles_ticks": {"adjust"},
    "get_public_instruments": {"seriesId"},
    "get_contract_taker_volume": {"unit", "limit"},
    "get_order_list": {"after", "before"},
    "get_orders_history": {"after", "before"},
    "get_fills": {"after", "before"},
    "amend_order": {"speedBump", "pxAmendType", "attachAlgoOrds"},
    "close_positions": {"clOrdId"},
}


@pytest.mark.parametrize(("method_name", "expected"), CURRENT_FIELDS.items())
def test_okx_sync_and_async_expose_current_official_fields(
    method_name: str, expected: set[str]
) -> None:
    sync_client = _client_class("sync", "okx")
    async_client = _client_class("async", "okx")
    sync_fields = set(inspect.signature(getattr(sync_client, method_name)).parameters)
    async_fields = set(inspect.signature(getattr(async_client, method_name)).parameters)

    assert expected <= sync_fields
    assert sync_fields == async_fields


@pytest.mark.parametrize(
    ("method_name", "obsolete"),
    [
        ("get_account_instruments", {"uly"}),
        ("get_public_instruments", {"uly"}),
        ("get_open_interest", {"uly"}),
        ("get_position_tiers", {"uly"}),
        ("get_spot_fee_rates", {"uly", "ruleType"}),
        ("place_order", {"quickMgnType", "stpId"}),
        ("get_order_list", {"uly"}),
        ("get_orders_history", {"uly"}),
        ("get_fills", {"uly"}),
    ],
)
def test_okx_obsolete_fields_are_not_exposed(method_name: str, obsolete: set[str]) -> None:
    client = _client_class("sync", "okx")
    fields = set(inspect.signature(getattr(client, method_name)).parameters)
    assert fields.isdisjoint(obsolete)


def test_sync_okx_place_order_serializes_json_values_for_native_rust() -> None:
    client = _client_class("sync", "okx")(**_client_kwargs("okx"))
    calls = _wire_sync(client)
    attachments = [{"tpTriggerPx": "110", "tpOrdPx": "109"}]

    client.place_order(
        "BTC-USDT-SWAP",
        "cross",
        "buy",
        "limit",
        "1",
        reduceOnly=True,
        banAmend=False,
        isElpTakerAccess=True,
        attachAlgoOrds=attachments,
    )

    params = dict(calls[0]["query"])
    assert params["reduceOnly"] == "true"
    assert params["banAmend"] == "false"
    assert params["isElpTakerAccess"] == "true"
    assert json.loads(params["attachAlgoOrds"]) == attachments


@pytest.mark.parametrize(
    ("product_symbol", "ord_type", "side", "tgt_ccy", "slippage_pct", "message"),
    [
        ("BTC-USDT-SPOT", "market", "buy", "base_ccy", "0.0501", "between 0 and 0.05"),
        ("BTC-USDT-SPOT", "market", "buy", "base_ccy", "0.01234", "four fractional"),
        ("BTC-USDT-SWAP", "market", "buy", "base_ccy", "0.01", "only supported"),
        ("BTC-USDT-SPOT", "limit", "buy", "base_ccy", "0.01", "only supported"),
        ("BTC-USDT-SPOT", "market", "sell", "base_ccy", "0.01", "tgtCcy=quote_ccy"),
    ],
)
def test_okx_rejects_invalid_slippage_pct_before_transport(
    product_symbol: str,
    ord_type: str,
    side: str,
    tgt_ccy: str,
    slippage_pct: str,
    message: str,
) -> None:
    native = pytest.importorskip("dcex._native")
    client = native.OkxHttpClient(
        api_key="key",
        api_secret="secret",
        passphrase="passphrase",
        timeout=2,
        base_url="http://127.0.0.1:1",
    )
    with pytest.raises(ValueError, match=message):
        client.private_request_json(
            "place_order",
            [
                ("product_symbol", product_symbol),
                ("tdMode", "cash"),
                ("side", side),
                ("ordType", ord_type),
                ("sz", "1"),
                ("tgtCcy", tgt_ccy),
                ("slippagePct", slippage_pct),
            ],
        )


@pytest.mark.asyncio
async def test_async_okx_asset_current_fields_are_forwarded() -> None:
    client = _client_class("async", "okx")(**_client_kwargs("okx"))
    calls = _wire_async(client)

    await client.funds_transfer(
        "USDT",
        "1",
        "FUND",
        "TRADING",
        loanTrans=True,
        omitPosRisk=False,
        clientId="transfer-client-id",
    )

    params = dict(calls[0]["query"])
    assert params["loanTrans"] == "true"
    assert params["omitPosRisk"] == "false"
    assert params["clientId"] == "transfer-client-id"
