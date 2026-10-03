"""Offline boundary cases for newly added nested account and risk requests."""

from __future__ import annotations

import json
from typing import Any

import pytest

from dcex import _native

CASES = [
    ("Bybit", "set_api_rate_limits", {"list": [{"uids": "1", "bizType": "UTA", "rate": 10}]}),
    ("Bybit", "set_api_rate_limits", {"list": [{"uids": "1", "bizType": "SPOT", "rate": 1.5}]}),
    ("Bybit", "get_all_api_rate_limits", {"limit": 1001}),
    (
        "Bitget",
        "move_uta_positions",
        {
            "fromUid": "1",
            "toUid": "1",
            "category": "USDT-FUTURES",
            "positionList": [{"symbol": "BTCUSDT", "side": "buy", "qty": "1"}],
        },
    ),
    (
        "Bitget",
        "move_uta_positions",
        {
            "fromUid": "1",
            "toUid": "2",
            "category": "USDT-FUTURES",
            "positionList": [{"symbol": "BTCUSDT", "side": "buy", "qty": "NaN"}],
        },
    ),
    (
        "Kraken",
        "simulate_futures_portfolio",
        {"json": {"positions": [{"instrument": "PF_XBTUSD", "size": "1", "entryPrice": 1}]}},
    ),
    (
        "Kraken",
        "request_spot_export_report",
        {"report": "trades", "description": "history", "starttm": 2, "endtm": 1},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("exchange,method,params", CASES)
async def test_native_rejects_invalid_nested_risk_fields(
    exchange: str, method: str, params: dict[str, Any], asynchronous: bool
) -> None:
    options: dict[str, Any] = {"timeout": 1}
    if exchange != "Kraken":
        options["base_url"] = "http://127.0.0.1:1"
    else:
        options.update(spot_base_url="http://127.0.0.1:1", futures_base_url="http://127.0.0.1:1")
    client = getattr(_native, exchange + "HttpClient")(**options)
    pairs = [
        (k, json.dumps(v, separators=(",", ":")) if isinstance(v, (dict, list)) else str(v))
        for k, v in params.items()
    ]
    with pytest.raises(
        ValueError,
        match="(?i)(invalid|must|require|expected|positive|outside|range|at most|exceed|different|distinct|same)",
    ):
        if asynchronous:
            await client.private_request_json_async(method, pairs)
        else:
            client.private_request_json(method, pairs)
