# ruff: noqa: D103
"""
Offline wire coverage for every Aster V3 sync and async endpoint wrapper.

The generic endpoint suite replaces ``_request`` with a fake and never reaches
the native dispatcher.  These tests drive each public wrapper through the real
Rust client against a local HTTP server and assert that the documented Aster
V3 path (https://github.com/asterdex/api-docs) and key parameters arrive on
the wire, and that private calls are EIP-712 signed while public calls are not.
"""

from __future__ import annotations

import json
import queue
from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

import pytest

from tests.unit.wire_expectations import EXPECTED_VERBS as _ALL_VERBS

EXPECTED_VERBS = _ALL_VERBS["aster"]

from dcex.aster.client import Client
from dcex.async_support.aster.client import Client as AsyncClient
from dcex.utils.errors import FailedRequestError
from tests.unit.native_http_helpers import _http_server

USER = "0x0000000000000000000000000000000000000001"
SIGNER = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
PRIVATE_KEY = "0x" + "11" * 32
SPOT = "BTC-USDT-SPOT"
SWAP = "BTC-USDT-SWAP"
RUST_DIR = Path(__file__).resolve().parents[2] / "crates" / "dcex" / "src" / "exchanges" / "aster"
RUST_SOURCE = "\n".join(
    path.read_text(encoding="utf-8")
    for path in [*RUST_DIR.glob("*.rs"), *(RUST_DIR / "schemas").glob("*.json")]
)


@dataclass(frozen=True)
class WireCase:
    """One wrapper call and the request it must produce."""

    method: str
    kwargs: dict[str, Any]
    path: str
    params: dict[str, str]
    signed: bool
    verb: str | None = None

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return f"{self.method}-{self.path}"


def pub(method: str, path: str, params: dict[str, str] | None = None, **kwargs: Any) -> WireCase:  # noqa: ANN401
    """Build a public (unsigned) wire case."""
    return WireCase(method, kwargs, path, params or {}, signed=False)


def priv(method: str, path: str, params: dict[str, str] | None = None, **kwargs: Any) -> WireCase:  # noqa: ANN401
    """Build a private (signed) wire case."""
    return WireCase(method, kwargs, path, params or {}, signed=True)


OCO_LEGS = [
    {
        "strategySubId": 1,
        "securityType": "USDT_FUTURES",
        "product_symbol": SWAP,
        "side": "SELL",
        "type": "TAKE_PROFIT_MARKET",
        "quantity": "1",
        "stopPrice": "120",
    },
    {
        "strategySubId": 2,
        "securityType": "USDT_FUTURES",
        "product_symbol": SWAP,
        "side": "SELL",
        "type": "STOP_MARKET",
        "quantity": "1",
        "stopPrice": "80",
    },
]

CASES = [
    priv(
        "get_asset_migration_history",
        "/fapi/v3/asset/migrateUser/history",
        {"batchId": "batch1"},
        batch_id="batch1",
    ),
    pub("get_prediction_ping", "/api/v3/ping", {}, **{}),
    pub("get_prediction_time", "/api/v3/time", {}, **{}),
    pub("get_prediction_exchange_info", "/api/v3/prediction/exchangeInfo", {}, **{}),
    pub(
        "get_prediction_depth",
        "/api/v3/depth",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
    ),
    pub(
        "get_prediction_trades",
        "/api/v3/trades",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
    ),
    pub(
        "get_prediction_historical_trades",
        "/api/v3/historicalTrades",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
    ),
    pub(
        "get_prediction_agg_trades",
        "/api/v3/aggTrades",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
    ),
    pub(
        "get_prediction_klines",
        "/api/v3/klines",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "interval": "1m"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "interval": "1m"},
    ),
    pub("get_prediction_ticker_24hr", "/api/v3/ticker/24hr", {}, **{}),
    pub("get_prediction_ticker_price", "/api/v3/ticker/price", {}, **{}),
    pub("get_prediction_ticker_book_ticker", "/api/v3/ticker/bookTicker", {}, **{}),
    priv(
        "get_prediction_commission_rate",
        "/api/v3/commissionRate",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
    ),
    priv(
        "create_prediction_order",
        "/api/v3/order",
        {
            "symbol": "EVENT4_ALGERIA_WIN_YUSDT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": "1",
            "price": "0.5",
            "timeInForce": "GTC",
        },
        **{
            "symbol": "EVENT4_ALGERIA_WIN_YUSDT",
            "side": "BUY",
            "type_": "LIMIT",
            "quantity": "1",
            "price": "0.5",
            "time_in_force": "GTC",
        },
    ),
    priv(
        "cancel_prediction_order",
        "/api/v3/order",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "orderId": "1"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "order_id": 1},
    ),
    priv(
        "get_prediction_order",
        "/api/v3/order",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "orderId": "1"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "order_id": 1},
    ),
    priv(
        "get_prediction_open_order",
        "/api/v3/openOrder",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "orderId": "1"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "order_id": 1},
    ),
    priv("get_prediction_open_orders", "/api/v3/openOrders", {}, **{}),
    priv(
        "get_prediction_all_orders",
        "/api/v3/allOrders",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT"},
    ),
    priv(
        "create_prediction_asset_wallet_transfer",
        "/api/v3/asset/wallet/transfer",
        {"amount": "1", "asset": "USDT", "clientTranId": "example", "kindType": "FUTURE_SPOT"},
        **{"amount": "1", "asset": "USDT", "client_tran_id": "example", "kind_type": "FUTURE_SPOT"},
    ),
    priv(
        "create_prediction_mint",
        "/api/v3/prediction/mint",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "quantity": "1"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "quantity": "1"},
    ),
    priv(
        "create_prediction_burn",
        "/api/v3/prediction/burn",
        {"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "quantity": "1"},
        **{"symbol": "EVENT4_ALGERIA_WIN_YUSDT", "quantity": "1"},
    ),
    priv(
        "create_prediction_split",
        "/api/v3/prediction/split",
        {"event": "EVENT4", "symbol": "EVENT4_ALGERIA_WIN_YUSDT", "quantity": "1"},
        **{"event": "EVENT4", "symbol": "EVENT4_ALGERIA_WIN_YUSDT", "quantity": "1"},
    ),
    priv(
        "create_prediction_merge",
        "/api/v3/prediction/merge",
        {"event": "EVENT4", "quantity": "1"},
        **{"event": "EVENT4", "quantity": "1"},
    ),
    priv("get_prediction_positions", "/api/v3/prediction/positions", {}, **{}),
    priv("get_prediction_position_histories", "/api/v3/prediction/positionHistories", {}, **{}),
    priv("get_prediction_settlement_histories", "/api/v3/prediction/settlementHistories", {}, **{}),
    priv("get_prediction_account", "/api/v3/account", {}, **{}),
    priv("get_prediction_user_trades", "/api/v3/userTrades", {}, **{}),
    priv("create_prediction_listen_key", "/api/v3/listenKey", {}, **{}),
    priv(
        "update_prediction_listen_key",
        "/api/v3/listenKey",
        {"listenKey": "example"},
        **{"listen_key": "example"},
    ),
    priv(
        "cancel_prediction_listen_key",
        "/api/v3/listenKey",
        {"listenKey": "example"},
        **{"listen_key": "example"},
    ),
    pub("get_asset_logos", "/fapi/v3/common/asset/all-asset-logo", {}, **{}),
    priv("trigger_futures_asset_exchange", "/fapi/v3/assetExchange", {}, confirm=True),
    priv("get_sub_accounts", "/fapi/v3/getSubAccountList", {}, **{}),
    priv("get_direct_announcements", "/fapi/v3/announcement/direct", {}, **{}),
    priv("get_direct_announcement", "/fapi/v3/announcement/directById", {"id": "1"}, **{"id": 1}),
    priv(
        "create_sub_account_signed",
        "/fapi/v3/createSubAccount",
        {
            "subAccountName": "desk",
            "subSourceAddr": "0x0000000000000000000000000000000000000002",
            "nonce": "1700000000000123",
            "user": "0x0000000000000000000000000000000000000001",
            "signer": "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a",
            "childSignature": (
                "0x22222222222222222222222222222222222222222222222222222"
                "2222222222222222222222222222222222222222222222222222222"
                "2222222222222222222222"
            ),
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
        },
        **{
            "sub_account_name": "desk",
            "sub_source_addr": "0x0000000000000000000000000000000000000002",
            "nonce": 1700000000000123,
            "user": "0x0000000000000000000000000000000000000001",
            "signer": "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a",
            "child_signature": (
                "0x22222222222222222222222222222222222222222222222222222"
                "2222222222222222222222222222222222222222222222222222222"
                "2222222222222222222222"
            ),
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
        },
    ),
    priv(
        "update_sub_account_signed",
        "/fapi/v3/updateSubAccount",
        {
            "subSourceAddr": "0x0000000000000000000000000000000000000002",
            "nonce": "1700000000000123",
            "user": "0x0000000000000000000000000000000000000001",
            "signer": "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a",
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
            "status": "FROZEN",
        },
        **{
            "sub_source_addr": "0x0000000000000000000000000000000000000002",
            "nonce": 1700000000000123,
            "user": "0x0000000000000000000000000000000000000001",
            "signer": "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a",
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
            "status": "FROZEN",
        },
    ),
    priv(
        "bind_sub_account_signed",
        "/fapi/v3/sub-accounts/bind",
        {
            "childAddress": "0x0000000000000000000000000000000000000002",
            "name": "desk",
            "nonce": "1700000000000123",
            "user": "0x0000000000000000000000000000000000000001",
            "childSignature": (
                "0x22222222222222222222222222222222222222222222222222222"
                "2222222222222222222222222222222222222222222222222222222"
                "2222222222222222222222"
            ),
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
        },
        **{
            "child_address": "0x0000000000000000000000000000000000000002",
            "name": "desk",
            "nonce": 1700000000000123,
            "user": "0x0000000000000000000000000000000000000001",
            "child_signature": (
                "0x22222222222222222222222222222222222222222222222222222"
                "2222222222222222222222222222222222222222222222222222222"
                "2222222222222222222222"
            ),
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
        },
    ),
    priv(
        "register_agent_signed",
        "/fapi/v3/registerAndApproveAgent",
        {
            "user": "0x0000000000000000000000000000000000000001",
            "nonce": "1700000000000123",
            "agentName": "trader",
            "agentAddress": "0x0000000000000000000000000000000000000003",
            "expired": "1800000000000",
            "signatureChainId": "56",
            "canSpotTrade": "true",
            "canPerpTrade": "true",
            "canWithdraw": "false",
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
        },
        **{
            "user": "0x0000000000000000000000000000000000000001",
            "nonce": 1700000000000123,
            "agent_name": "trader",
            "agent_address": "0x0000000000000000000000000000000000000003",
            "expired": 1800000000000,
            "signature_chain_id": 56,
            "can_spot_trade": True,
            "can_perp_trade": True,
            "can_withdraw": False,
            "signature": (
                "0x11111111111111111111111111111111111111111111111111111"
                "1111111111111111111111111111111111111111111111111111111"
                "1111111111111111111111"
            ),
        },
    ),
    priv("noop_spot", "/api/v3/noop", {"nonce": "1700000000000123"}, nonce=1700000000000123),
    priv("noop_futures", "/fapi/v3/noop", {"nonce": "1700000000000123"}, nonce=1700000000000123),
    priv(
        "guarded_cancel_futures_order",
        "/fapi/v3/guardedCancelOrder",
        {"symbol": "BTCUSDT", "nonce": "1700000000000123", "orderId": "123"},
        product_symbol=SWAP,
        nonce=1700000000000123,
        orderId=123,
    ),
    priv(
        "guarded_cancel_futures_batch_orders",
        "/fapi/v3/guardedBatchOrders",
        {"symbol": "BTCUSDT", "nonce": "1700000000000123", "orderIdList": "[123,456]"},
        product_symbol=SWAP,
        nonce=1700000000000123,
        orderIdList=[123, 456],
    ),
    priv(
        "transfer_sub_account",
        "/fapi/v3/subAccountTransfer",
        {"toAccountAddress": USER, "asset": "USDT", "amount": "10", "kindType": "FUTURE_FUTURE"},
        to_account_address=USER,
        asset="USDT",
        amount="10",
        kind_type="FUTURE_FUTURE",
    ),
    # Spot market data
    pub("ping_spot", "/api/v3/ping"),
    pub("get_spot_server_time", "/api/v3/time"),
    pub("get_spot_exchange_info", "/api/v3/exchangeInfo"),
    pub(
        "get_spot_orderbook",
        "/api/v3/depth",
        {"symbol": "BTCUSDT", "limit": "5"},
        product_symbol=SPOT,
        limit=5,
    ),
    pub(
        "get_spot_recent_trades",
        "/api/v3/trades",
        {"symbol": "BTCUSDT", "limit": "10"},
        product_symbol=SPOT,
        limit=10,
    ),
    pub(
        "get_spot_historical_trades",
        "/api/v3/historicalTrades",
        {"symbol": "BTCUSDT", "fromId": "7"},
        product_symbol=SPOT,
        fromId=7,
    ),
    pub(
        "get_spot_agg_trades",
        "/api/v3/aggTrades",
        {"symbol": "BTCUSDT", "startTime": "1", "endTime": "2"},
        product_symbol=SPOT,
        startTime=1,
        endTime=2,
    ),
    pub(
        "get_spot_klines",
        "/api/v3/klines",
        {"symbol": "BTCUSDT", "interval": "1m", "limit": "3"},
        product_symbol=SPOT,
        interval="1m",
        limit=3,
    ),
    pub("get_spot_ticker_24hr", "/api/v3/ticker/24hr", {"symbol": "BTCUSDT"}, product_symbol=SPOT),
    pub("get_spot_ticker_price", "/api/v3/ticker/price"),
    pub(
        "get_spot_book_ticker",
        "/api/v3/ticker/bookTicker",
        {"symbol": "BTCUSDT"},
        product_symbol=SPOT,
    ),
    pub(
        "get_spot_withdraw_fee",
        "/api/v3/aster/withdraw/estimateFee",
        {"chainId": "56", "asset": "USDT"},
        chainId="56",
        asset="USDT",
    ),
    # Futures market data
    pub("ping_futures", "/fapi/v3/ping"),
    pub("get_futures_server_time", "/fapi/v3/time"),
    pub("get_futures_exchange_info", "/fapi/v3/exchangeInfo"),
    pub(
        "get_futures_orderbook",
        "/fapi/v3/depth",
        {"symbol": "BTCUSDT", "limit": "10"},
        product_symbol=SWAP,
        limit=10,
    ),
    pub(
        "get_futures_recent_trades",
        "/fapi/v3/trades",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    pub(
        "get_futures_historical_trades",
        "/fapi/v3/historicalTrades",
        {"symbol": "BTCUSDT", "limit": "5"},
        product_symbol=SWAP,
        limit=5,
    ),
    pub(
        "get_futures_agg_trades",
        "/fapi/v3/aggTrades",
        {"symbol": "BTCUSDT", "fromId": "3"},
        product_symbol=SWAP,
        fromId=3,
    ),
    pub(
        "get_futures_klines",
        "/fapi/v3/klines",
        {"symbol": "BTCUSDT", "interval": "1h"},
        product_symbol=SWAP,
        interval="1h",
    ),
    pub(
        "get_futures_index_price_klines",
        "/fapi/v3/indexPriceKlines",
        {"pair": "BTCUSDT", "interval": "1m"},
        pair="BTCUSDT",
        interval="1m",
    ),
    pub(
        "get_futures_mark_price_klines",
        "/fapi/v3/markPriceKlines",
        {"symbol": "BTCUSDT", "interval": "5m"},
        product_symbol=SWAP,
        interval="5m",
    ),
    pub(
        "get_futures_ticker_24hr",
        "/fapi/v3/ticker/24hr",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    pub(
        "get_futures_ticker_price",
        "/fapi/v3/ticker/price",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    pub("get_futures_book_ticker", "/fapi/v3/ticker/bookTicker"),
    pub(
        "get_futures_premium_index",
        "/fapi/v3/premiumIndex",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    pub(
        "get_futures_funding_rate",
        "/fapi/v3/fundingRate",
        {"symbol": "BTCUSDT", "limit": "100"},
        product_symbol=SWAP,
        limit=100,
    ),
    pub("get_futures_funding_info", "/fapi/v3/fundingInfo"),
    pub(
        "get_futures_index_references",
        "/fapi/v3/indexreferences",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    pub(
        "get_futures_remaining_openable_notional",
        "/fapi/v3/remainingOpenableNotionalValue",
        {"symbol": "BTCUSDT", "leverage": "3"},
        product_symbol=SWAP,
        leverage=3,
    ),
    # Spot account / trading
    priv("get_spot_account", "/api/v3/account"),
    priv(
        "get_spot_transaction_history",
        "/api/v3/transactionHistory",
        {"asset": "USDT", "type": "TRADE_TARGET"},
        asset="USDT",
        type_="TRADE_TARGET",
    ),
    priv(
        "transfer_spot_futures",
        "/api/v3/asset/wallet/transfer",
        {"amount": "1", "asset": "USDT", "clientTranId": "tx-1", "kindType": "SPOT_FUTURE"},
        amount="1",
        asset="USDT",
        clientTranId="tx-1",
        kindType="SPOT_FUTURE",
    ),
    priv(
        "get_spot_commission_rate",
        "/api/v3/commissionRate",
        {"symbol": "BTCUSDT"},
        product_symbol=SPOT,
    ),
    priv(
        "place_spot_order",
        "/api/v3/order",
        {"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "price": "100"},
        product_symbol=SPOT,
        side="BUY",
        type_="LIMIT",
        quantity="1",
        price="100",
        timeInForce="GTC",
    ),
    priv(
        "cancel_spot_order",
        "/api/v3/order",
        {"symbol": "BTCUSDT", "orderId": "11"},
        product_symbol=SPOT,
        orderId=11,
    ),
    priv(
        "get_spot_order",
        "/api/v3/order",
        {"symbol": "BTCUSDT", "origClientOrderId": "mine"},
        product_symbol=SPOT,
        origClientOrderId="mine",
    ),
    priv(
        "get_spot_open_order",
        "/api/v3/openOrder",
        {"symbol": "BTCUSDT", "orderId": "12"},
        product_symbol=SPOT,
        orderId=12,
    ),
    priv("get_spot_open_orders", "/api/v3/openOrders", {"symbol": "BTCUSDT"}, product_symbol=SPOT),
    priv(
        "cancel_all_spot_open_orders",
        "/api/v3/allOpenOrders",
        {"symbol": "BTCUSDT", "orderIdList": "[1,2]"},
        product_symbol=SPOT,
        orderIdList=[1, 2],
    ),
    priv(
        "get_spot_all_orders",
        "/api/v3/allOrders",
        {"symbol": "BTCUSDT", "limit": "50"},
        product_symbol=SPOT,
        limit=50,
    ),
    priv(
        "get_spot_user_trades",
        "/api/v3/userTrades",
        {"symbol": "BTCUSDT", "fromId": "4"},
        product_symbol=SPOT,
        fromId=4,
    ),
    priv("create_spot_listen_key", "/api/v3/listenKey"),
    priv(
        "keep_alive_spot_listen_key",
        "/api/v3/listenKey",
        {"listenKey": "abc"},
        listenKey="abc",
    ),
    priv("close_spot_listen_key", "/api/v3/listenKey", {"listenKey": "abc"}, listenKey="abc"),
    # Futures account
    priv(
        "transfer_spot_futures",
        "/fapi/v3/asset/wallet/transfer",
        {"kindType": "FUTURE_SPOT", "user": USER},
        amount="2",
        asset="USDT",
        clientTranId="tx-2",
        kindType="FUTURE_SPOT",
        market="futures",
    ),
    priv("get_futures_position_mode", "/fapi/v3/positionSide/dual", {"user": USER}),
    priv(
        "set_futures_position_mode",
        "/fapi/v3/positionSide/dual",
        {"dualSidePosition": "true"},
        dualSidePosition=True,
    ),
    priv("get_futures_stp_mode", "/fapi/v3/stpMode"),
    priv(
        "set_futures_stp_mode",
        "/fapi/v3/stpMode",
        {"stpMode": "EXPIRE_MAKER"},
        stpMode="EXPIRE_MAKER",
    ),
    priv("get_futures_multi_assets_mode", "/fapi/v3/multiAssetsMargin"),
    priv(
        "set_futures_multi_assets_mode",
        "/fapi/v3/multiAssetsMargin",
        {"multiAssetsMargin": "false"},
        multiAssetsMargin=False,
    ),
    priv("get_futures_balance", "/fapi/v3/balance"),
    priv("get_futures_account", "/fapi/v3/accountWithJoinMargin"),
    priv(
        "modify_futures_position_margin",
        "/fapi/v3/positionMargin",
        {"symbol": "BTCUSDT", "amount": "5", "type": "1"},
        product_symbol=SWAP,
        amount="5",
        type_=1,
    ),
    priv(
        "get_futures_position_margin_history",
        "/fapi/v3/positionMargin/history",
        {"symbol": "BTCUSDT", "type": "2"},
        product_symbol=SWAP,
        type_=2,
    ),
    priv(
        "get_futures_position_risk",
        "/fapi/v3/positionRisk",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    priv(
        "get_futures_user_trades",
        "/fapi/v3/userTrades",
        {"symbol": "BTCUSDT", "limit": "20"},
        product_symbol=SWAP,
        limit=20,
    ),
    priv(
        "get_futures_income",
        "/fapi/v3/income",
        {"incomeType": "FUNDING_FEE"},
        incomeType="FUNDING_FEE",
    ),
    priv(
        "get_futures_leverage_bracket",
        "/fapi/v3/leverageBrackets",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    priv("get_futures_adl_quantile", "/fapi/v3/adlQuantile"),
    priv(
        "get_futures_force_orders",
        "/fapi/v3/forceOrders",
        {"autoCloseType": "LIQUIDATION"},
        autoCloseType="LIQUIDATION",
    ),
    priv(
        "get_futures_commission_rate",
        "/fapi/v3/commissionRate",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    priv(
        "update_futures_mmp",
        "/fapi/v3/mmp",
        {"symbol": "BTCUSDT", "windowTimeInMilliseconds": "1000", "qtyLimit": "10"},
        product_symbol=SWAP,
        windowTimeInMilliseconds=1000,
        frozenTimeInMilliseconds=5000,
        qtyLimit=10,
    ),
    priv("get_futures_mmp", "/fapi/v3/mmp"),
    priv("delete_futures_mmp", "/fapi/v3/mmp", {"symbol": "BTCUSDT"}, product_symbol=SWAP),
    priv("reset_futures_mmp", "/fapi/v3/mmpReset", {"symbol": "BTCUSDT"}, product_symbol=SWAP),
    priv("create_futures_listen_key", "/fapi/v3/listenKey"),
    priv("keep_alive_futures_listen_key", "/fapi/v3/listenKey"),
    priv("close_futures_listen_key", "/fapi/v3/listenKey"),
    # Futures trading
    priv(
        "place_futures_order",
        "/fapi/v3/order",
        {"symbol": "BTCUSDT", "side": "SELL", "type": "STOP_MARKET", "closePosition": "true"},
        product_symbol=SWAP,
        side="SELL",
        type_="STOP_MARKET",
        stopPrice="90",
        closePosition=True,
        workingType="MARK_PRICE",
    ),
    priv(
        "modify_futures_order",
        "/fapi/v3/order",
        {"symbol": "BTCUSDT", "orderId": "5", "quantity": "2", "price": "99"},
        product_symbol=SWAP,
        quantity="2",
        price="99",
        orderId=5,
    ),
    priv(
        "place_futures_chase_order",
        "/fapi/v3/chase",
        {"symbol": "BTCUSDT", "side": "BUY", "quantityUnit": "BASE"},
        product_symbol=SWAP,
        side="BUY",
        quantityUnit="BASE",
        quantity="0.001",
    ),
    priv(
        "place_futures_batch_orders",
        "/fapi/v3/batchOrders",
        {},
        batchOrders=[
            {
                "product_symbol": SWAP,
                "side": "buy",
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": "1",
                "price": "100",
            }
        ],
    ),
    priv(
        "modify_futures_batch_orders",
        "/fapi/v3/batchOrders",
        {},
        batchOrders=[{"product_symbol": SWAP, "orderId": 1, "quantity": "1", "price": "101"}],
    ),
    priv(
        "get_futures_order",
        "/fapi/v3/order",
        {"symbol": "BTCUSDT", "orderId": "6"},
        product_symbol=SWAP,
        orderId=6,
    ),
    priv(
        "cancel_futures_order",
        "/fapi/v3/order",
        {"symbol": "BTCUSDT", "origClientOrderId": "cid"},
        product_symbol=SWAP,
        origClientOrderId="cid",
    ),
    priv(
        "cancel_all_futures_open_orders",
        "/fapi/v3/allOpenOrders",
        {"symbol": "BTCUSDT"},
        product_symbol=SWAP,
    ),
    priv(
        "cancel_futures_batch_orders",
        "/fapi/v3/batchOrders",
        {"symbol": "BTCUSDT", "orderIdList": "[1,2]"},
        product_symbol=SWAP,
        orderIdList=[1, 2],
    ),
    priv(
        "set_futures_countdown_cancel_all",
        "/fapi/v3/countdownCancelAll",
        {"symbol": "BTCUSDT", "countdownTime": "60000"},
        product_symbol=SWAP,
        countdownTime=60000,
    ),
    priv(
        "get_futures_open_order",
        "/fapi/v3/openOrder",
        {"symbol": "BTCUSDT", "orderId": "7"},
        product_symbol=SWAP,
        orderId=7,
    ),
    priv("get_futures_open_orders", "/fapi/v3/openOrders"),
    priv(
        "get_futures_all_orders",
        "/fapi/v3/allOrders",
        {"symbol": "BTCUSDT", "limit": "10"},
        product_symbol=SWAP,
        limit=10,
    ),
    priv(
        "set_futures_leverage",
        "/fapi/v3/leverage",
        {"symbol": "BTCUSDT", "leverage": "10"},
        product_symbol=SWAP,
        leverage=10,
    ),
    priv(
        "set_futures_margin_type",
        "/fapi/v3/marginType",
        {"symbol": "BTCUSDT", "marginType": "ISOLATED"},
        product_symbol=SWAP,
        marginType="ISOLATED",
    ),
    priv(
        "place_futures_strategy_order",
        "/fapi/v3/placeStrategyOrder",
        {"strategyType": "OCO", "clientStrategyId": "tpsl-1"},
        strategyType="OCO",
        subOrderList=OCO_LEGS,
        clientStrategyId="tpsl-1",
    ),
    priv(
        "update_futures_strategy_order",
        "/fapi/v3/updateStrategyOrder",
        {"strategyId": "9", "strategyType": "OCO"},
        strategyId=9,
        strategyType="OCO",
        subOrderList=[
            {
                "strategySubId": 2,
                "securityType": "USDT_FUTURES",
                "symbol": "BTCUSDT",
                "side": "SELL",
                "type": "STOP_MARKET",
                "stopPrice": "85",
            }
        ],
    ),
    priv(
        "get_futures_strategy_open_order",
        "/fapi/v3/strategyOpenOrder",
        {"strategyId": "9", "strategyType": "OCO"},
        strategyType="OCO",
        strategyId=9,
    ),
    priv(
        "get_futures_strategy_history_order",
        "/fapi/v3/strategyHistoryOrder",
        {"clientStrategyId": "tpsl-1", "strategyType": "OTO"},
        strategyType="OTO",
        clientStrategyId="tpsl-1",
    ),
]

BATCH_PATH_METHODS = {
    "place_futures_batch_orders",
    "modify_futures_batch_orders",
    "place_futures_strategy_order",
    "update_futures_strategy_order",
}


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "user_address": USER,
        "signer_address": SIGNER,
        "private_key": PRIVATE_KEY,
        "spot_base_url": base_url,
        "futures_base_url": base_url,
        "prediction_base_url": base_url,
        "preload_product_table": False,
    }


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    """Share one recording server across the module to keep the suite fast."""
    with _http_server() as (base_url, received):
        yield base_url, received


def _drain(received: queue.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    while not received.empty():
        requests.append(received.get_nowait())
    return requests


def _fail_if_native_is_stale(case: WireCase, error: ValueError) -> None:
    """Fail when the prebuilt extension predates a dispatch name present in source."""
    if "unsupported Aster" not in str(error):
        raise error
    if f'"{case.method}"' not in RUST_SOURCE:
        raise error
    pytest.fail(f"installed dcex._native predates Rust dispatch {case.method!r}; rebuild needed")


def _fresh_nonce_case(case: WireCase) -> WireCase:
    from time import time_ns

    if "nonce" in case.kwargs and not case.method.endswith("_signed"):
        nonce = time_ns() // 1000
        if case.method.startswith("guarded_cancel_"):
            nonce -= 300_000_000
        return replace(
            case,
            kwargs={**case.kwargs, "nonce": nonce},
            params={**case.params, "nonce": str(nonce)},
        )
    return case


def _assert_request(case: WireCase, requests: list[dict[str, Any]]) -> None:
    assert len(requests) == 1, requests
    request = requests[0]
    from tests.unit.wire_contracts import assert_wire_contract

    assert_wire_contract("aster", case.method, request)
    assert request["method"] == (case.verb or EXPECTED_VERBS[case.method])
    path, _, query = request["path"].partition("?")
    assert path == case.path
    pairs = dict(parse_qsl(query or request["body"], keep_blank_values=True))
    for key, value in case.params.items():
        assert pairs.get(key) == value, (key, pairs)
    if case.method.endswith("_signed") and not case.method.startswith("withdraw_"):
        assert pairs == case.params
    elif case.signed:
        assert pairs["signer"] == SIGNER
        assert pairs["signature"].startswith("0x")
        assert "nonce" in pairs
        assert ("user" in pairs) is (
            path.startswith("/fapi/") and case.method != "transfer_sub_account"
        )
    else:
        assert "signature" not in pairs
    if case.method in BATCH_PATH_METHODS:
        key = "batchOrders" if "batch" in case.method else "subOrderList"
        orders = json.loads(pairs[key])
        assert all(order["symbol"] == "BTCUSDT" for order in orders)
        assert all("product_symbol" not in order for order in orders)
        assert all(order.get("side", "SELL") in {"BUY", "SELL"} for order in orders)


CASES += [
    WireCase(c["name"], c["kwargs"], c["path"], c["wire"], True, c["verb"])
    for c in json.loads(
        (Path(__file__).parents[1] / "fixtures/aster_request_cases.json").read_text(
            encoding="utf-8"
        )
    )
]
CASES += [
    WireCase(
        "get_futures_market_klines",
        {"symbol": "BTCUSDT", "interval": "1m", "callerFlag": "keep"},
        "/fapi/v3/marketKlines",
        {"symbol": "BTCUSDT", "interval": "1m", "callerFlag": "keep"},
        False,
        "GET",
    ),
    WireCase(
        "get_spot_optimized_ticker_24hr",
        {"symbol": "BTCUSDT"},
        "/api/v3/ticker/opt/24hr",
        {"symbol": "BTCUSDT"},
        False,
        "GET",
    ),
    WireCase(
        "place_spot_batch_orders_raw",
        {"batchOrders": '[{"symbol":"BTCUSDT"}]', "callerFlag": "keep"},
        "/api/v3/batchOrders",
        {"batchOrders": '[{"symbol":"BTCUSDT"}]', "callerFlag": "keep"},
        True,
        "POST",
    ),
    WireCase(
        "cancel_spot_batch_orders_raw",
        {"orderIdList": "[1]"},
        "/api/v3/batchOrders",
        {"orderIdList": "[1]"},
        True,
        "DELETE",
    ),
    WireCase("noop_prediction", {"nonce": 1}, "/api/v3/noop", {}, True, "POST"),
]


def test_every_endpoint_wrapper_has_a_wire_case() -> None:
    wrappers = {
        name for name, value in vars(Client).items() if not name.startswith("_") and callable(value)
    }
    for base in Client.__mro__:
        module = getattr(base, "__module__", "")
        if module.startswith("dcex.aster._") and module.endswith("_http"):
            wrappers.update(
                name
                for name, value in vars(base).items()
                if not name.startswith("_") and callable(value)
            )
    from tests.unit.test_aster_chain_and_announcements import CASES as AUXILIARY_CASES

    assert (
        wrappers - ({case.method for case in CASES} | {case[0] for case in AUXILIARY_CASES})
        == set()
    )
    for case in CASES:
        assert f'"{case.method}"' in RUST_SOURCE, case.method


@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_sync_wrapper_reaches_documented_route(
    case: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    case = _fresh_nonce_case(case)
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        result = getattr(client, case.method)(**case.kwargs)
    except ValueError as error:
        _fail_if_native_is_stale(case, error)
    finally:
        client.close()
    assert result in ({"ok": True}, {"serverTime": 1})
    _assert_request(case, _drain(received))


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
async def test_async_wrapper_reaches_documented_route(
    case: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    case = _fresh_nonce_case(case)
    base_url, received = server
    _drain(received)
    client = AsyncClient(**_client_kwargs(base_url))
    await client.async_init()
    try:
        result = await getattr(client, case.method)(**case.kwargs)
    except ValueError as error:
        _fail_if_native_is_stale(case, error)
    finally:
        await client.close()
    assert result in ({"ok": True}, {"serverTime": 1})
    _assert_request(case, _drain(received))


def test_unsafe_orders_are_rejected_before_the_wire(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    with pytest.raises((ValueError, FailedRequestError), match="closePosition"):
        client.place_futures_order(
            product_symbol=SWAP,
            side="SELL",
            type_="STOP_MARKET",
            stopPrice="90",
            closePosition=True,
            quantity="1",
        )
    with pytest.raises((ValueError, FailedRequestError)):
        client.cancel_futures_batch_orders(
            product_symbol=SWAP,
            orderIdList=[1],
            origClientOrderIdList=["a"],
        )
    with pytest.raises((ValueError, FailedRequestError)):
        client.set_futures_leverage(product_symbol=SWAP, leverage=0)
    with pytest.raises((ValueError, FailedRequestError)):
        client.place_futures_strategy_order(strategyType="OCO", subOrderList=OCO_LEGS[:1])
    client.close()
    assert _drain(received) == []


@pytest.mark.parametrize(
    ("method", "kwargs", "path"),
    [
        ("place_spot_order", {"product_symbol": SPOT, "type_": "MARKET"}, "/api/v3/order"),
        ("place_futures_order", {"product_symbol": SWAP, "type_": "MARKET"}, "/fapi/v3/order"),
        (
            "place_futures_chase_order",
            {"product_symbol": SWAP, "quantityUnit": "BASE"},
            "/fapi/v3/chase",
        ),
    ],
)
def test_single_orders_accept_lowercase_side(
    method: str,
    kwargs: dict[str, Any],
    path: str,
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        getattr(client, method)(side="buy", quantity="1", **kwargs)
    finally:
        client.close()
    requests = _drain(received)
    assert len(requests) == 1, requests
    request_path, _, query = requests[0]["path"].partition("?")
    assert request_path == path
    pairs = dict(parse_qsl(query or requests[0]["body"], keep_blank_values=True))
    assert pairs["side"] == "BUY"


def test_cancel_without_order_identifier_raises_locally(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    with pytest.raises(ValueError, match="orderId or origClientOrderId"):
        client.cancel_spot_order(product_symbol=SPOT)
    with pytest.raises(ValueError, match="orderId or origClientOrderId"):
        client.cancel_futures_order(product_symbol=SWAP)
    client.close()
    assert _drain(received) == []


@pytest.mark.parametrize(
    "method", ["place_spot_order", "place_futures_order", "place_futures_batch_orders"]
)
def test_explicit_placement_nonce_is_preserved(
    method: str, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    from time import time_ns

    nonce = time_ns() // 1000
    client = Client(**_client_kwargs(base_url))
    kwargs: dict[str, Any] = {
        "product_symbol": SWAP,
        "side": "BUY",
        "type_": "MARKET",
        "quantity": "1",
    }
    if method == "place_futures_batch_orders":
        kwargs = {
            "batchOrders": [{"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET", "quantity": "1"}]
        }
    try:
        getattr(client, method)(nonce=nonce, **kwargs)
    finally:
        client.close()
    (request,) = _drain(received)
    pairs = parse_qsl(request["body"])
    assert [value for key, value in pairs if key == "nonce"] == [str(nonce)]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_asset_exchange_accepts_empty_success_response(asynchronous: bool) -> None:
    """The documented empty asset-exchange response is successful, not invalid JSON."""
    from dcex.aster.client import Client
    from dcex.async_support.aster.client import Client as AsyncClient

    with _http_server(response_bytes=b"") as (base, received):
        client = (AsyncClient if asynchronous else Client)(**_client_kwargs(base))
        try:
            if asynchronous:
                await client.async_init()
                assert await client.trigger_futures_asset_exchange(confirm=True) == {}
            else:
                assert client.trigger_futures_asset_exchange(confirm=True) == {}
        finally:
            if asynchronous:
                await client.close()
            else:
                client.close()
        request = received.get_nowait()
        assert request["path"].split("?", 1)[0] == "/fapi/v3/assetExchange"
        assert request["method"] == "POST"
