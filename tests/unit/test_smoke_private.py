"""The private smoke runner calls only plain reads and never keeps response data."""

# ruff: noqa: D103
from __future__ import annotations

import json

import pytest

from scripts.live import smoke_private


@pytest.mark.parametrize(
    "name",
    [
        "get_asset_balance",
        "get_exchange_info",
        "get_closed_pnl",
        "get_withdraw_history",
        "get_futures_order_modify_history",
        "query_sub_account_assets",
        "list_api_keys",
    ],
)
def test_read_verbs_with_noun_words_are_reads(name: str) -> None:
    assert smoke_private.classify(name) == "read"


@pytest.mark.parametrize(
    "name",
    [
        "place_order",
        "cancel_all_orders",
        "set_leverage",
        "transfer_between_accounts",
        "get_listen_key",
        "get_spot_websocket_token",
        "get_convert_quote",
        "get_bridge_quote",
        "get_futures_download_id_for_futures_trade_history",
        "get_monthly_statement",
        "get_account_bills_history_archive",
    ],
)
def test_actions_and_minting_reads_are_never_called(name: str) -> None:
    assert smoke_private.classify(name) == "never"


@pytest.mark.parametrize("name", ["cfd_trade_get_current_positions", "pre_check_order"])
def test_read_verb_inside_the_name_needs_review(name: str) -> None:
    assert smoke_private.classify(name) == "review"


class FakeClient:
    def get_balance(self) -> dict[str, str]:
        return {"secret": "do-not-store-me"}

    def place_order(self) -> None:
        raise AssertionError("an order method was called")

    def get_listen_key(self) -> None:
        raise AssertionError("a minting read was called")

    def cfd_trade_get_positions(self) -> None:
        raise AssertionError("a review method was called")

    def close(self) -> None:
        pass


def test_run_calls_reads_only_and_records_no_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(smoke_private, "make_client", lambda exchange: FakeClient())
    monkeypatch.setattr(
        smoke_private,
        "private_methods",
        lambda exchange: [
            "get_balance",
            "place_order",
            "get_listen_key",
            "cfd_trade_get_positions",
        ],
    )
    monkeypatch.setattr(smoke_private, "PAUSE_SECONDS", 0)
    monkeypatch.setattr("scripts.live.smoke_private.time.sleep", lambda _: None)
    rows = smoke_private.run_exchange("okx")
    assert [(r["method"], r["outcome"]) for r in rows] == [("get_balance", "ok")]
    assert "do-not-store-me" not in json.dumps(rows)


def test_missing_credentials_skip_the_exchange(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_client(exchange: str) -> None:
        raise LookupError("missing credentials")

    monkeypatch.setattr(smoke_private, "make_client", no_client)
    rows = smoke_private.run_exchange("okx")
    assert rows == [
        {
            "exchange": "okx",
            "method": "<client>",
            "outcome": "skipped",
            "message": "missing credentials",
        }
    ]
