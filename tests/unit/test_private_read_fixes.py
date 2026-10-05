"""Private read fixes found by the live read-only smoke run (scripts/live/smoke_private.py)."""

# ruff: noqa: D103
from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_order_flag_validation_wire import _binance, _bingx, _kraken, _mexc, _okx

pytest.importorskip("dcex._native")


def _sent(received: Any) -> list[dict[str, Any]]:  # noqa: ANN401
    requests = []
    while not received.empty():
        item = received.get_nowait()
        path = urlsplit(item["path"]).path
        if not path.endswith("/time") and "/server/time" not in path:
            requests.append(item)
    return requests


def _fields(request: dict[str, Any]) -> dict[str, Any]:
    body = request["body"]
    if body.startswith("{"):
        return json.loads(body)
    return dict(parse_qsl(urlsplit(request["path"]).query or body))


REJECTED = [
    # Live -1102: type is mandatory for flexible rewards history.
    ("binance-flex-rewards", _binance, "get_flexible_earn_rewards_history", []),
    ("binance-flex-rewards-type", _binance, "get_flexible_earn_rewards_history", [("type", "x")]),
    ("binance-special-key", _binance, "query_margin_special_key", []),
    (
        "binance-modify-history",
        _binance,
        "get_futures_order_modify_history",
        [("symbol", "BTCUSDT")],
    ),
    ("binance-prevented-none", _binance, "get_prevented_matches", [("product_symbol", "BTCUSDT")]),
    (
        "binance-prevented-both",
        _binance,
        "get_prevented_matches",
        [("product_symbol", "BTCUSDT"), ("orderId", "1"), ("preventedMatchId", "2")],
    ),
    ("okx-mmp", _okx, "get_mmp_config", []),
    ("okx-transfer-state", _okx, "get_transfer_state", []),
    ("kraken-amends", _kraken, "get_spot_order_amends", []),
    ("bingx-partner", _bingx, "get_agent_v1_asset_partner_data", [("startTime", "1")]),
]


@pytest.mark.parametrize(
    ("name", "factory", "method", "params"), REJECTED, ids=[c[0] for c in REJECTED]
)
def test_required_read_parameters_fail_before_sending(
    name: str,
    factory: Any,
    method: str,
    params: list[tuple[str, str]],  # noqa: ANN401
) -> None:
    del name
    with _http_server() as (base, received):
        with pytest.raises(ValueError):
            factory(base).private_request_json(method, params)
        assert _sent(received) == []


SENT = [
    (
        _binance,
        "get_flexible_earn_rewards_history",
        [("type", "REWARDS")],
        {"type": "REWARDS"},
    ),
    (_binance, "query_margin_special_key", [("apiKey", "k1")], {"apiKey": "k1"}),
    (
        _binance,
        "get_futures_order_modify_history",
        [("symbol", "BTCUSDT"), ("orderId", "7")],
        {"orderId": "7"},
    ),
    (
        _binance,
        "get_prevented_matches",
        [("product_symbol", "BTCUSDT"), ("orderId", "7")],
        {"orderId": "7"},
    ),
    (_okx, "get_mmp_config", [("instFamily", "BTC-USD")], {"instFamily": "BTC-USD"}),
    (_okx, "get_transfer_state", [("clientId", "c1")], {"clientId": "c1"}),
    (_kraken, "get_spot_order_amends", [("order_id", "O1")], {"order_id": "O1"}),
    (
        _bingx,
        "get_agent_v1_asset_partner_data",
        [("startTime", "1"), ("endTime", "2"), ("pageIndex", "1"), ("pageSize", "10")],
        {"startTime": "1", "endTime": "2", "pageIndex": "1", "pageSize": "10"},
    ),
]


@pytest.mark.parametrize(("factory", "method", "params", "expected"), SENT)
def test_complete_reads_reach_the_wire(
    factory: Any,  # noqa: ANN401
    method: str,
    params: list[tuple[str, str]],
    expected: dict[str, str],
) -> None:
    with _http_server({"code": 0, "data": {}, "result": {}, "error": []}) as (base, received):
        try:
            factory(base).private_request_json(method, params)
        except Exception:  # noqa: BLE001, S110 - the response shape is irrelevant here
            pass
        requests = _sent(received)
    assert len(requests) == 1
    fields = _fields(requests[0])
    for key, value in expected.items():
        assert str(fields.get(key)) == value, (key, fields)


def test_mexc_open_order_count_uses_get() -> None:
    # The docs say POST, but the live route answers only GET (POST is 404).
    with _http_server({"success": True, "code": 0, "data": {"sumCount": 0}}) as (base, received):
        _mexc(base).private_request_json("get_contract_open_order_count", [])
        requests = _sent(received)
    assert [(r["method"], urlsplit(r["path"]).path) for r in requests] == [
        ("GET", "/api/v1/private/order/open_order_total_count")
    ]


@pytest.mark.parametrize("mode", ["dcex", "dcex.async_support"])
def test_bingx_unavailable_copy_trading_route_is_removed(mode: str) -> None:
    client = pytest.importorskip(f"{mode}.bingx.client").Client
    assert not hasattr(client, "get_copy_trading_v1_swap_trace_current_track")
