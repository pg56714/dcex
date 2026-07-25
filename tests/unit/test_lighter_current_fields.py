# ruff: noqa: D100, D103

import json
from enum import Enum
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def _native_client(*, base_url: str = "http://127.0.0.1:1") -> object:
    native = pytest.importorskip("dcex._native")
    return native.LighterHttpClient(timeout=2, base_url=base_url)


def _signing_client() -> object:
    native = pytest.importorskip("dcex._native")
    return native.LighterHttpClient(
        timeout=2,
        account_index=12,
        api_key_index=3,
        api_private_key="01" + "00" * 39,
    )


def test_lighter_native_params_expand_multi_values_and_enums() -> None:
    from dcex.lighter._http_manager import HTTPManager

    class TransferType(Enum):
        ALL = "all"
        L2_TRANSFER = "L2Transfer"

    assert HTTPManager._native_params(
        type_=[TransferType.ALL, TransferType.L2_TRANSFER],
        enabled=True,
    ) == [("type_", "all"), ("type_", "L2Transfer"), ("enabled", "true")]


def test_lighter_current_public_query_fields_and_no_trades_auth_query() -> None:
    with _http_server({"code": 0}) as (base_url, received):
        client = _native_client(base_url=base_url)
        client.public_request_json(
            "get_trades",
            [("market_id", "0"), ("sort_by", "timestamp"), ("limit", "10")],
        )
        client.public_request_json(
            "get_candles",
            [
                ("market_id", "2048"),
                ("resolution", "1w"),
                ("start_timestamp", "1700000000000"),
                ("end_timestamp", "1700600000000"),
                ("count_back", "10"),
                ("set_timestamp_to_end", "true"),
            ],
        )

    trades = urlsplit(received.get_nowait()["path"])
    candles = urlsplit(received.get_nowait()["path"])
    assert trades.path == "/api/v1/trades"
    assert parse_qsl(trades.query) == [
        ("market_id", "0"),
        ("sort_by", "timestamp"),
        ("limit", "10"),
    ]
    assert candles.path == "/api/v1/candles"
    assert dict(parse_qsl(candles.query)) == {
        "market_id": "2048",
        "resolution": "1w",
        "start_timestamp": "1700000000000",
        "end_timestamp": "1700600000000",
        "count_back": "10",
        "set_timestamp_to_end": "true",
    }


def test_lighter_transfer_history_uses_repeated_type_and_position_funding_is_public() -> None:
    with _http_server({"code": 0}) as (base_url, received):
        client = _native_client(base_url=base_url)
        client.private_request_json(
            "get_transfer_history",
            [
                ("account_index", "12"),
                ("type_", "all"),
                ("type_", "L2Transfer"),
            ],
        )
        client.private_request_json(
            "get_position_funding",
            [("account_index", "12"), ("limit", "100"), ("side", "all")],
        )

    transfer = urlsplit(received.get_nowait()["path"])
    funding = urlsplit(received.get_nowait()["path"])
    assert transfer.path == "/api/v1/transfer/history"
    assert parse_qsl(transfer.query) == [
        ("account_index", "12"),
        ("type", "all"),
        ("type", "L2Transfer"),
    ]
    assert funding.path == "/api/v1/positionFunding"
    assert dict(parse_qsl(funding.query)) == {
        "account_index": "12",
        "limit": "100",
        "side": "all",
    }


def test_lighter_rejects_invalid_current_fields_before_transport() -> None:
    client = _native_client()
    with pytest.raises(ValueError, match="unsupported Lighter parameter"):
        client.public_request_json("get_status", [("unexpected", "1")])
    with pytest.raises(ValueError, match="resolution"):
        client.public_request_json(
            "get_candles",
            [
                ("market_id", "0"),
                ("resolution", "2m"),
                ("start_timestamp", "1"),
                ("end_timestamp", "2"),
                ("count_back", "1"),
            ],
        )
    with pytest.raises(ValueError, match="limit"):
        client.private_request_json(
            "get_position_funding",
            [("account_index", "12"), ("limit", "101")],
        )


def test_lighter_signer_emits_current_self_trade_and_cancel_market_attributes() -> None:
    client = _signing_client()
    tx_type, tx_info, _tx_hash, error = client.sign_request(
        "sign_create_order",
        [
            ("market_index", "0"),
            ("client_order_index", "1"),
            ("base_amount", "10"),
            ("price", "100"),
            ("is_ask", "false"),
            ("order_type", "0"),
            ("time_in_force", "1"),
            ("reduce_only", "false"),
            ("trigger_price", "0"),
            ("order_expiry", "1800000000000"),
            ("self_trade_behavior_mode", "2"),
            ("self_trade_equality_mode", "1"),
            ("nonce", "7"),
        ],
    )
    payload = json.loads(tx_info)
    assert (tx_type, error) == (14, None)
    assert payload["L2TxAttributes"] == {"6": 2, "7": 1}

    tx_type, tx_info, _tx_hash, error = client.sign_request(
        "sign_cancel_all_orders",
        [
            ("time_in_force", "0"),
            ("timestamp_ms", "0"),
            ("cancel_all_market_index", "42"),
            ("nonce", "8"),
        ],
    )
    payload = json.loads(tx_info)
    assert (tx_type, error) == (16, None)
    assert payload["L2TxAttributes"] == {"5": 42}


def test_lighter_signer_rejects_invalid_self_trade_combinations() -> None:
    client = _signing_client()
    common = [
        ("market_index", "0"),
        ("client_order_index", "1"),
        ("base_amount", "10"),
        ("price", "100"),
        ("is_ask", "false"),
        ("order_type", "0"),
        ("time_in_force", "1"),
        ("order_expiry", "1800000000000"),
        ("nonce", "7"),
    ]
    with pytest.raises(ValueError, match="self-trade settings"):
        client.sign_request(
            "sign_create_order",
            common
            + [
                ("integrator_account_index", "12"),
                ("integrator_taker_fee", "1"),
                ("self_trade_behavior_mode", "2"),
            ],
        )
    with pytest.raises(ValueError, match="reduce mode"):
        client.sign_request(
            "sign_create_order",
            common
            + [
                ("self_trade_behavior_mode", "3"),
                ("self_trade_equality_mode", "1"),
            ],
        )
