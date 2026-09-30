"""
Offline end-to-end route coverage for every KuCoin Python wrapper.

Every public wrapper on the sync and async KuCoin clients (including the
``_earn_http.py`` and ``_margin_http.py`` mixins, which the shared
``ENDPOINT_FILE_SUFFIXES`` list does not pick up) is called against local HTTP
servers through the real native transport. Each case asserts the HTTP method,
the REST path from the official KuCoin API docs, and that the request reached
the right host (spot ``api.kucoin.com`` vs futures ``api-futures.kucoin.com``).
"""

# ruff: noqa: D103

from __future__ import annotations

import inspect
import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
SPOT = "BTC-USDT-SPOT"
SWAP = "BTC-USDT-SWAP"


@dataclass(frozen=True)
class Case:
    """One wrapper call and the HTTP request it must produce."""

    method_name: str
    kwargs: dict[str, Any]
    route: str
    host: str = "spot"
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | list[dict[str, Any]] = field(default_factory=dict)
    signed: bool = True

    @property
    def id(self) -> str:
        """Return the pytest id, disambiguating repeated method names."""
        suffix = "-".join(sorted(self.kwargs)) if self.method_name in _DUPLICATE_NAMES else ""
        return f"{self.method_name}{'-' + suffix if suffix else ''}"


_DUPLICATE_NAMES = {"get_futures_orderbook", "get_spot_orderbook"}

LIMIT = {"size": "1", "price": "100"}
FUT_LIMIT = {"size": "1", "price": "100", "leverage": 3}

CASES: tuple[Case, ...] = (
    Case(
        "create_withdrawal",
        {
            "currency": "USDT",
            "amount": "1.000000000000000001",
            "to_address": "offline-address",
            "withdraw_type": "ADDRESS",
            "chain": "trx",
            "memo": "",
            "is_inner": False,
            "fee_deduct_type": "EXTERNAL",
        },
        "POST /api/v3/withdrawals",
        body={
            "currency": "USDT",
            "amount": "1.000000000000000001",
            "toAddress": "offline-address",
            "withdrawType": "ADDRESS",
            "chain": "trx",
            "memo": "",
            "isInner": False,
            "feeDeductType": "EXTERNAL",
        },
    ),
    Case(
        "create_uta_withdrawal",
        {
            "currency": "USDT",
            "amount": "3",
            "to_address": "123456",
            "withdraw_type": "UID",
            "is_inner": True,
            "remark": "offline",
        },
        "POST /api/ua/v2/asset/withdrawal",
        body={
            "currency": "USDT",
            "amount": "3",
            "toAddress": "123456",
            "withdrawType": "UID",
            "isInner": True,
            "remark": "offline",
        },
    ),
    Case(
        "cancel_withdrawal",
        {"withdrawal_id": "test-withdrawal"},
        "DELETE /api/v1/withdrawals/test-withdrawal",
    ),
    Case(
        "cancel_uta_withdrawal",
        {"withdraw_id": "test-withdrawal"},
        "POST /api/ua/v2/asset/withdraw/cancel",
        body={"withdrawId": "test-withdrawal"},
    ),
    Case(
        "cancel_margin_stop_order_by_id_raw",
        {"orderId": "test-order", "callerFlag": "keep"},
        "DELETE /api/v3/hf/margin/stop-order/cancel-by-id",
        query={"orderId": "test-order", "callerFlag": "keep"},
    ),
    Case("get_currencies_v3", {}, "GET /api/v3/currencies", body={}, signed=False),
    Case(
        "set_uta_account_mode",
        {"account_type": "UNIFIED", "confirm": True},
        "POST /api/ua/v2/account/mode",
        body={"accountType": "UNIFIED"},
        signed=True,
    ),
    Case(
        "get_withdrawal_history_by_id",
        {"withdrawal_id": "example"},
        "GET /api/v1/withdrawals/example",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_withdrawal_history",
        {"currency": "USDT"},
        "GET /api/v1/withdrawals",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_withdrawal_quotas",
        {"currency": "USDT"},
        "GET /api/v1/withdrawals/quotas",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_loan_info",
        {},
        "GET /api/v1/otc-loan/loan",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_otc_loan_accounts",
        {},
        "GET /api/v1/otc-loan/accounts",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_discount_rate_configs",
        {},
        "GET /api/v1/otc-loan/discount-rate-configs",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_oes_custody_quota",
        {},
        "GET /api/ua/v2/oes/custody-quota",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_oes_currency",
        {},
        "GET /api/ua/v2/oes/currency",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_accounts",
        {},
        "GET /api/ua/v2/otc-loan/account",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_discount_rate_configs",
        {},
        "GET /api/ua/v2/otc-loan/discount-rate",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_loan_info",
        {},
        "GET /api/ua/v2/otc-loan/loan",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_withdrawal_history",
        {},
        "GET /api/ua/v2/asset/withdrawal/history",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_withdrawal_quotas",
        {"currency": "USDT", "withdraw_type": "ADDRESS"},
        "GET /api/ua/v2/withdrawals/quotas",
        host="spot",
        query={"currency": "USDT", "withdrawType": "ADDRESS"},
        body={},
        signed=True,
    ),
    Case(
        "get_account_info", {}, "GET /api/v2/user-info", host="spot", query={}, body={}, signed=True
    ),
    Case(
        "get_spot_account_type",
        {},
        "GET /api/v1/hf/accounts/opened",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "add_sub_account",
        {"password": "trade1234", "sub_name": "trader123", "access": "Spot"},
        "POST /api/v2/sub/user/created",
        host="spot",
        query={},
        body={"password": "trade1234", "subName": "trader123", "access": "Spot"},
        signed=True,
    ),
    Case(
        "get_spot_24h_statistics",
        {"symbol": "BTC-USDT"},
        "GET /api/v1/market/stats",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_client_ip_address",
        {},
        "GET /api/v1/my-ip",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_kyc_regions",
        {},
        "GET /api/kyc/regions/v4",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_spot_index_price",
        {"symbol": "BTC-USDT"},
        "GET /api/v1/index/query",
        host="futures",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_24h_statistics",
        {},
        "GET /api/v1/trade-statistics",
        host="futures",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_apikey_info",
        {},
        "GET /api/v1/user/api-key",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "create_deposit_address_v3",
        {"currency": "USDT", "chain": "trx"},
        "POST /api/v3/deposit-address/create",
        host="spot",
        query={},
        body={"currency": "USDT", "chain": "trx"},
        signed=True,
    ),
    Case(
        "get_deposit_addresses_v3",
        {"currency": "USDT"},
        "GET /api/v3/deposit-addresses",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "add_sub_account_api",
        {"passphrase": "testpass123", "remark": "trading", "sub_name": "trader123"},
        "POST /api/v1/sub/api-key",
        host="spot",
        query={},
        body={"passphrase": "testpass123", "remark": "trading", "subName": "trader123"},
        signed=True,
    ),
    Case(
        "delete_sub_account_api",
        {"api_key": "query-key", "sub_name": "trader123", "passphrase": "testpass123"},
        "DELETE /api/v1/sub/api-key",
        host="spot",
        query={"apiKey": "query-key", "subName": "trader123", "passphrase": "testpass123"},
        body={},
        signed=True,
    ),
    Case(
        "get_sub_account_api_list",
        {"sub_name": "trader123"},
        "GET /api/v1/sub/api-key",
        host="spot",
        query={"subName": "trader123"},
        body={},
        signed=True,
    ),
    Case(
        "modify_sub_account_api",
        {"passphrase": "testpass123", "sub_name": "trader123", "api_key": "query-key"},
        "POST /api/v1/sub/api-key/update",
        host="spot",
        query={},
        body={"passphrase": "testpass123", "subName": "trader123", "apiKey": "query-key"},
        signed=True,
    ),
    Case(
        "add_sub_account_futures_permission",
        {"uid": "123"},
        "POST /api/v3/sub/user/futures/enable",
        host="spot",
        query={},
        body={"uid": "123"},
        signed=True,
    ),
    Case(
        "add_sub_account_margin_permission",
        {"uid": "123"},
        "POST /api/v3/sub/user/margin/enable",
        host="spot",
        query={},
        body={"uid": "123"},
        signed=True,
    ),
    Case("get_basic_fee", {}, "GET /api/v1/base-fee", host="spot", query={}, body={}, signed=True),
    Case(
        "add_convert_limit_order",
        {
            "client_order_id": "client-order-1",
            "from_currency": "BTC",
            "to_currency": "USDT",
            "from_currency_size": "0.123456789123456789",
            "to_currency_size": "1000.123456789123456789",
        },
        "POST /api/v1/convert/limit/order",
        host="spot",
        query={},
        body={
            "clientOrderId": "client-order-1",
            "fromCurrency": "BTC",
            "toCurrency": "USDT",
            "fromCurrencySize": 0.12345678912345678,
            "toCurrencySize": 1000.1234567891235,
        },
        signed=True,
    ),
    Case(
        "add_convert_order",
        {"client_order_id": "client-order-1", "quote_id": "quote-1"},
        "POST /api/v1/convert/order",
        host="spot",
        query={},
        body={"clientOrderId": "client-order-1", "quoteId": "quote-1"},
        signed=True,
    ),
    Case(
        "cancel_convert_limit_order",
        {"order_id": "order-1"},
        "DELETE /api/v1/convert/limit/order/cancel",
        host="spot",
        query={"orderId": "order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_convert_currencies",
        {},
        "GET /api/v1/convert/currencies",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_convert_limit_order_detail",
        {"order_id": "order-1"},
        "GET /api/v1/convert/limit/order/detail",
        host="spot",
        query={"orderId": "order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_convert_limit_order_detail_list",
        {},
        "GET /api/v1/convert/limit/orders",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_convert_limit_quote",
        {
            "from_currency": "BTC",
            "to_currency": "USDT",
            "from_currency_size": "0.123456789123456789",
        },
        "GET /api/v1/convert/limit/quote",
        host="spot",
        query={
            "fromCurrency": "BTC",
            "toCurrency": "USDT",
            "fromCurrencySize": "0.123456789123456789",
        },
        body={},
        signed=True,
    ),
    Case(
        "get_convert_order_detail",
        {"order_id": "order-1"},
        "GET /api/v1/convert/order/detail",
        host="spot",
        query={"orderId": "order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_convert_order_history",
        {},
        "GET /api/v1/convert/order/history",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_convert_quote",
        {
            "from_currency": "BTC",
            "to_currency": "USDT",
            "from_currency_size": "0.123456789123456789",
        },
        "GET /api/v1/convert/quote",
        host="spot",
        query={
            "fromCurrency": "BTC",
            "toCurrency": "USDT",
            "fromCurrencySize": "0.123456789123456789",
        },
        body={},
        signed=True,
    ),
    Case(
        "get_convert_symbol",
        {"from_currency": "BTC", "to_currency": "USDT"},
        "GET /api/v1/convert/symbol",
        host="spot",
        query={"fromCurrency": "BTC", "toCurrency": "USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_interest_rate_index",
        {"symbol": ".XBTINT8H"},
        "GET /api/v1/interest/query",
        host="futures",
        query={"symbol": ".XBTINT8H"},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_premium_index",
        {"symbol": ".XBTUSDTMPI8H"},
        "GET /api/v1/premium/query",
        host="futures",
        query={"symbol": ".XBTUSDTMPI8H"},
        body={},
        signed=False,
    ),
    Case(
        "get_margin_config",
        {},
        "GET /api/v1/margin/config",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_announcements",
        {},
        "GET /api/v3/announcements",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_call_auction_info",
        {"symbol": "BTC-USDT"},
        "GET /api/v1/market/callauctionData",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_call_auction_part_order_book",
        {"size": 20, "symbol": "BTC-USDT"},
        "GET /api/v1/market/orderbook/callauction/level2_20",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_spot_currency_v3",
        {"currency": "USDT"},
        "GET /api/v3/currencies/USDT",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case("get_fiat_price", {}, "GET /api/v1/prices", host="spot", query={}, body={}, signed=False),
    Case(
        "get_market_list", {}, "GET /api/v1/markets", host="spot", query={}, body={}, signed=False
    ),
    Case(
        "get_spot_symbol_v2",
        {"symbol": "BTC-USDT"},
        "GET /api/v2/symbols/BTC-USDT",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "add_uta_sub_account",
        {"password": "trade1234", "sub_name": "trader123", "access": "Spot"},
        "POST /api/ua/v2/user/sub/create-sub-account",
        host="spot",
        query={},
        body={"password": "trade1234", "subName": "trader123", "access": "Spot"},
        signed=True,
    ),
    Case(
        "add_uta_sub_account_api",
        {"sub_name": "trader123", "passphrase": "testpass123", "remark": "trading"},
        "POST /api/ua/v2/user/create-sub-api-key",
        host="spot",
        query={},
        body={"subName": "trader123", "passphrase": "testpass123", "remark": "trading"},
        signed=True,
    ),
    Case(
        "get_uta_apikey_info",
        {},
        "GET /api/ua/v2/user/api-key",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_currencies",
        {},
        "GET /api/ua/v2/asset/currencies",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_currency",
        {"currency": "USDT"},
        "GET /api/ua/v2/market/currency",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=False,
    ),
    Case(
        "delete_uta_sub_account_api",
        {"api_key": "query-key", "sub_name": "trader123", "passphrase": "testpass123"},
        "DELETE /api/ua/v2/user/sub-api-key",
        host="spot",
        query={"apiKey": "query-key", "subName": "trader123", "passphrase": "testpass123"},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_deposit_address",
        {"currency": "USDT"},
        "GET /api/ua/v2/asset/deposit/address",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_deposit_history",
        {},
        "GET /api/ua/v2/asset/deposit/history",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_fiat_price",
        {"base": "USD"},
        "GET /api/ua/v2/market/fiat-price",
        host="spot",
        query={"base": "USD"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_announcements",
        {},
        "GET /api/ua/v2/market/announcement",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_call_auction_info",
        {"symbol": "BTC-USDT"},
        "GET /api/ua/v2/market/call-auction-info",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_client_ip_address",
        {},
        "GET /api/ua/v2/user/my-ip",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_kyc_regions",
        {},
        "GET /api/ua/v2/user/kyc-region",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "set_uta_kcs_fee_deduction",
        {"enabled": True},
        "GET /api/ua/v2/account/fee/kcs-deduct",
        host="spot",
        query={"enabled": "true"},
        body={},
        signed=True,
    ),
    Case(
        "modify_uta_sub_account_api",
        {"sub_name": "trader123", "api_key": "query-key", "passphrase": "testpass123"},
        "POST /api/ua/v2/user/modify-sub-api-key",
        host="spot",
        query={},
        body={"subName": "trader123", "apiKey": "query-key", "passphrase": "testpass123"},
        signed=True,
    ),
    Case(
        "set_uta_rate_limit",
        {"list": [{"uid": "123", "rate": 50}]},
        "POST /api/ua/v2/rate-limit/set",
        host="spot",
        query={},
        body={"list": [{"uid": "123", "rate": 50}]},
        signed=True,
    ),
    Case(
        "get_uta_sub_account_api_list",
        {"api_key": "query-key", "sub_name": "trader123"},
        "GET /api/ua/v2/user/sub-api-key",
        host="spot",
        query={"apiKey": "query-key", "subName": "trader123"},
        body={},
        signed=True,
    ),
    Case(
        "set_uta_sub_account_transfer_permission",
        {"sub_uids": "123", "sub_to_sub": True},
        "POST /api/ua/v2/sub-account/canTransferOut",
        host="spot",
        query={},
        body={"subUids": "123", "subToSub": True},
        signed=True,
    ),
    Case(
        "place_spot_order_sync",
        {
            "product_symbol": SPOT,
            "side": "buy",
            "type_": "limit",
            "size": "1",
            "price": "100",
            "clientOid": "sync-1",
        },
        "POST /api/v1/hf/orders/sync",
        body={
            "symbol": "BTC-USDT",
            "side": "buy",
            "type": "limit",
            "size": "1",
            "price": "100",
            "clientOid": "sync-1",
        },
    ),
    Case(
        "place_spot_batch_orders_sync",
        {
            "orders": [
                {
                    "product_symbol": SPOT,
                    "side": "buy",
                    "type": "market",
                    "funds": "10",
                    "clientOid": "sync-1",
                }
            ]
        },
        "POST /api/v1/hf/orders/multi/sync",
        body={
            "orderList": [
                {
                    "symbol": "BTC-USDT",
                    "side": "buy",
                    "type": "market",
                    "funds": "10",
                    "clientOid": "sync-1",
                }
            ]
        },
    ),
    Case(
        "cancel_spot_order_sync",
        {"product_symbol": SPOT, "order_id": "order-1"},
        "DELETE /api/v1/hf/orders/sync/order-1",
        query={"symbol": "BTC-USDT"},
    ),
    Case(
        "cancel_spot_order_by_client_oid_sync",
        {"product_symbol": SPOT, "client_oid": "sync-1"},
        "DELETE /api/v1/hf/orders/sync/client-order/sync-1",
        query={"symbol": "BTC-USDT"},
    ),
    Case(
        "get_futures_account_ledgers",
        {},
        "GET /api/v1/transaction-history",
        host="futures",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_hf_account_ledgers",
        {},
        "GET /api/v3/hf/margin/account/ledgers",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_account_ledgers",
        {},
        "GET /api/v1/accounts/ledgers",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_hf_account_ledgers",
        {},
        "GET /api/v1/hf/accounts/ledgers",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_deposit_history",
        {"currency": "USDT"},
        "GET /api/v1/deposits",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_all_tickers",
        {},
        "GET /api/v1/allTickers",
        host="futures",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_mark_price",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/mark-price/XBTUSDTM/current",
        host="futures",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_server_time",
        {},
        "GET /api/v1/timestamp",
        host="futures",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_service_status",
        {},
        "GET /api/v1/status",
        host="futures",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_margin_mark_price",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v1/mark-price/BTC-USDT/current",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_margin_mark_prices",
        {},
        "GET /api/v3/mark-price/all-symbols",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_margin_currency_risk_limits",
        {"currency": "USDT"},
        "GET /api/v3/margin/currencies",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_full_orderbook",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v3/market/orderbook/level2",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_server_time",
        {},
        "GET /api/v1/timestamp",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_spot_service_status",
        {},
        "GET /api/v1/status",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_account_ledgers",
        {"account_type": "UNIFIED"},
        "GET /api/ua/v2/account/ledger",
        host="spot",
        query={"accountType": "UNIFIED"},
        body={},
        signed=True,
    ),
    Case(
        "get_classic_account_balances_v2",
        {"account_type": "SPOT"},
        "GET /api/ua/v2/account/balance",
        host="spot",
        query={"accountType": "SPOT"},
        body={},
        signed=True,
    ),
    Case(
        "transfer_uta_accounts",
        {
            "client_oid": "transfer-123",
            "transfer_type": "INTERNAL",
            "currency": "USDT",
            "amount": "1",
            "from_account_type": "FUNDING",
            "from_account_tag": "DEFAULT",
            "to_account_type": "SPOT",
            "to_account_tag": "DEFAULT",
        },
        "POST /api/ua/v2/account/transfer",
        host="spot",
        query={},
        body={
            "clientOid": "transfer-123",
            "transferType": "INTERNAL",
            "currency": "USDT",
            "amount": "1",
            "fromAccountType": "FUNDING",
            "fromAccountTag": "DEFAULT",
            "toAccountType": "SPOT",
            "toAccountTag": "DEFAULT",
        },
        signed=True,
    ),
    Case(
        "get_uta_account_mode",
        {},
        "GET /api/ua/v2/account/mode",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_all_rate_limits",
        {},
        "GET /api/ua/v2/rate-limit/query-all",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_rate_limits",
        {"uids": "123,456"},
        "GET /api/ua/v2/rate-limit/query",
        host="spot",
        query={"uids": "123,456"},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_rate_limit_cap",
        {},
        "GET /api/ua/v2/rate-limit/query-cap",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_borrowable_currencies",
        {},
        "GET /api/ua/v2/market/borrowable-currency",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_borrowing_rates_limits",
        {"currency": "USDT"},
        "GET /api/ua/v2/account/interest-limits",
        host="spot",
        query={"currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_collateral_ratios",
        {},
        "GET /api/ua/v2/market/collateral-discount-ratio",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_current_funding_rates",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/ua/v2/market/funding-rate",
        host="spot",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_funding_rate_history",
        {"product_symbol": "BTC-USDT-SWAP", "start_at": "1700000000000", "end_at": "1700000060000"},
        "GET /api/ua/v2/market/funding-rate-history",
        host="spot",
        query={"symbol": "XBTUSDTM", "startAt": "1700000000000", "endAt": "1700000060000"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_index_prices",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/ua/v2/market/index-price",
        host="spot",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_interest_history",
        {"account_type": "UNIFIED"},
        "GET /api/ua/v2/account/interest-history",
        host="spot",
        query={"accountType": "UNIFIED"},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_interest_rate_index",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/ua/v2/market/interest-rate-index",
        host="spot",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_klines",
        {"product_symbol": "BTC-USDT-SPOT", "trade_type": "SPOT", "interval": "1min"},
        "GET /api/ua/v2/market/kline",
        host="spot",
        query={"symbol": "BTC-USDT", "tradeType": "SPOT", "interval": "1min"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_orderbook",
        {"trade_type": "SPOT", "product_symbol": "BTC-USDT-SPOT", "limit": "FULL"},
        "GET /api/ua/v2/market/orderbook",
        host="spot",
        query={"tradeType": "SPOT", "symbol": "BTC-USDT", "limit": "FULL"},
        body={},
        signed=True,
    ),
    Case(
        "get_uta_service_status",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/server/status",
        host="spot",
        query={"tradeType": "SPOT"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_tickers",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/market/ticker",
        host="spot",
        query={"tradeType": "SPOT"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_trade_statistics",
        {},
        "GET /api/ua/v2/trade-statistics",
        host="spot",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_public_trades",
        {"trade_type": "SPOT", "product_symbol": "BTC-USDT-SPOT"},
        "GET /api/ua/v2/market/trade",
        host="spot",
        query={"tradeType": "SPOT", "symbol": "BTC-USDT"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_instruments",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/market/instrument",
        host="spot",
        query={"tradeType": "SPOT"},
        body={},
        signed=False,
    ),
    Case(
        "get_uta_transfer_quota",
        {"account_type": "UNIFIED", "currency": "USDT"},
        "GET /api/ua/v2/account/transfer-quota",
        host="spot",
        query={"accountType": "UNIFIED", "currency": "USDT"},
        body={},
        signed=True,
    ),
    Case(
        "place_futures_batch_orders",
        {
            "orders": [
                {
                    "clientOid": "batch-1",
                    "product_symbol": "BTC-USDT-SWAP",
                    "side": "buy",
                    "type": "limit",
                    "size": 1,
                    "price": "100",
                    "leverage": 3,
                }
            ]
        },
        "POST /api/v1/orders/multi",
        host="futures",
        body=[
            {
                "clientOid": "batch-1",
                "symbol": "XBTUSDTM",
                "side": "buy",
                "type": "limit",
                "size": 1,
                "price": "100",
                "leverage": 3,
            }
        ],
    ),
    Case(
        "cancel_futures_batch_orders",
        {"client_orders": [{"symbol": "BTC-USDT-SWAP", "clientOid": "c-1"}]},
        "DELETE /api/v1/orders/multi-cancel",
        host="futures",
        body={"clientOidsList": [{"symbol": "XBTUSDTM", "clientOid": "c-1"}]},
    ),
    Case(
        "set_futures_batch_margin_mode",
        {"margin_mode": "CROSS", "symbols": ["BTC-USDT-SWAP"]},
        "POST /api/v2/position/batchChangeMarginMode",
        host="futures",
        body={"marginMode": "CROSS", "symbols": ["XBTUSDTM"]},
    ),
    Case(
        "get_spot_stop_order_by_client_oid",
        {"client_oid": "c-1", "product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v1/stop-order/queryOrderByClientOid",
        query={"clientOid": "c-1", "symbol": "BTC-USDT"},
    ),
    Case(
        "cancel_spot_order_by_client_oid",
        {"product_symbol": "BTC-USDT-SPOT", "client_oid": "test-order-1"},
        "DELETE /api/v1/hf/orders/client-order/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_spot_partial_order",
        {"product_symbol": "BTC-USDT-SPOT", "cancel_size": "1", "order_id": "test-order-1"},
        "DELETE /api/v1/hf/orders/cancel/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT", "cancelSize": "1"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_order",
        {"product_symbol": "BTC-USDT-SPOT", "order_id": "test-order-1"},
        "GET /api/v1/hf/orders/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_order_by_client_oid",
        {"product_symbol": "BTC-USDT-SPOT", "client_oid": "test-order-1"},
        "GET /api/v1/hf/orders/client-order/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_active_order_symbols",
        {},
        "GET /api/v1/hf/orders/active/symbols",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_active_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v1/hf/orders/active",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_closed_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v1/hf/orders/done",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "place_spot_stop_order",
        {
            "side": "buy",
            "product_symbol": "BTC-USDT-SPOT",
            "type_": "limit",
            "stop_price": "100",
            "price": "100",
            "size": "1",
        },
        "POST /api/v1/stop-order",
        host="spot",
        query={},
        body={
            "side": "buy",
            "symbol": "BTC-USDT",
            "type": "limit",
            "price": "100",
            "size": "1",
            "stopPrice": "100",
        },
        signed=True,
    ),
    Case(
        "cancel_spot_stop_order_by_client_oid",
        {"client_oid": "test-order-1", "product_symbol": "BTC-USDT-SPOT"},
        "DELETE /api/v1/stop-order/cancelOrderByClientOid",
        host="spot",
        query={"symbol": "BTC-USDT", "clientOid": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_spot_stop_order",
        {"order_id": "test-order-1"},
        "DELETE /api/v1/stop-order/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "cancel_spot_stop_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "DELETE /api/v1/stop-order/cancel",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_stop_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v1/stop-order",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_stop_order",
        {"order_id": "test-order-1"},
        "GET /api/v1/stop-order/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "place_spot_oco_order",
        {
            "client_oid": "test-order-1",
            "side": "buy",
            "product_symbol": "BTC-USDT-SPOT",
            "price": "100",
            "size": "1",
            "stop_price": "100",
            "limit_price": "100",
        },
        "POST /api/v3/oco/order",
        host="spot",
        query={},
        body={
            "clientOid": "test-order-1",
            "side": "buy",
            "symbol": "BTC-USDT",
            "price": "100",
            "size": "1",
            "stopPrice": "100",
            "limitPrice": "100",
        },
        signed=True,
    ),
    Case(
        "cancel_spot_oco_order",
        {"order_id": "test-order-1"},
        "DELETE /api/v3/oco/order/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "cancel_spot_oco_order_by_client_oid",
        {"client_oid": "test-order-1"},
        "DELETE /api/v3/oco/client-order/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "cancel_spot_oco_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "DELETE /api/v3/oco/orders",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_oco_order",
        {"order_id": "test-order-1"},
        "GET /api/v3/oco/order/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_oco_order_by_client_oid",
        {"client_oid": "test-order-1"},
        "GET /api/v3/oco/client-order/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_oco_order_details",
        {"order_id": "test-order-1"},
        "GET /api/v3/oco/order/details/test-order-1",
        host="spot",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "get_spot_oco_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v3/oco/orders",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "place_margin_order",
        {
            "client_oid": "test-order-1",
            "side": "buy",
            "product_symbol": "BTC-USDT-SPOT",
            "type_": "limit",
            "price": "100",
            "size": "1",
        },
        "POST /api/v3/hf/margin/order",
        host="spot",
        query={},
        body={
            "clientOid": "test-order-1",
            "side": "buy",
            "symbol": "BTC-USDT",
            "type": "limit",
            "price": "100",
            "size": "1",
        },
        signed=True,
    ),
    Case(
        "test_margin_order",
        {
            "client_oid": "test-order-1",
            "side": "buy",
            "product_symbol": "BTC-USDT-SPOT",
            "type_": "limit",
            "price": "100",
            "size": "1",
        },
        "POST /api/v3/hf/margin/order/test",
        host="spot",
        query={},
        body={
            "clientOid": "test-order-1",
            "side": "buy",
            "symbol": "BTC-USDT",
            "type": "limit",
            "price": "100",
            "size": "1",
        },
        signed=True,
    ),
    Case(
        "cancel_margin_order",
        {"product_symbol": "BTC-USDT-SPOT", "order_id": "test-order-1"},
        "DELETE /api/v3/hf/margin/orders/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_margin_order_by_client_oid",
        {"product_symbol": "BTC-USDT-SPOT", "client_oid": "test-order-1"},
        "DELETE /api/v3/hf/margin/orders/client-order/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_margin_orders_by_symbol",
        {"product_symbol": "BTC-USDT-SPOT", "trade_type": "MARGIN_TRADE"},
        "DELETE /api/v3/hf/margin/orders",
        host="spot",
        query={"symbol": "BTC-USDT", "tradeType": "MARGIN_TRADE"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_active_order_symbols",
        {"trade_type": "MARGIN_TRADE"},
        "GET /api/v3/hf/margin/order/active/symbols",
        host="spot",
        query={"tradeType": "MARGIN_TRADE"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_open_orders",
        {"product_symbol": "BTC-USDT-SPOT", "trade_type": "MARGIN_TRADE"},
        "GET /api/v3/hf/margin/orders/active",
        host="spot",
        query={"symbol": "BTC-USDT", "tradeType": "MARGIN_TRADE"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_closed_orders",
        {"product_symbol": "BTC-USDT-SPOT", "trade_type": "MARGIN_TRADE"},
        "GET /api/v3/hf/margin/orders/done",
        host="spot",
        query={"symbol": "BTC-USDT", "tradeType": "MARGIN_TRADE"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_trade_history",
        {"product_symbol": "BTC-USDT-SPOT", "trade_type": "MARGIN_TRADE"},
        "GET /api/v3/hf/margin/fills",
        host="spot",
        query={"symbol": "BTC-USDT", "tradeType": "MARGIN_TRADE"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_order",
        {"product_symbol": "BTC-USDT-SPOT", "order_id": "test-order-1"},
        "GET /api/v3/hf/margin/orders/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_order_by_client_oid",
        {"product_symbol": "BTC-USDT-SPOT", "client_oid": "test-order-1"},
        "GET /api/v3/hf/margin/orders/client-order/test-order-1",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "place_margin_stop_order",
        {
            "client_oid": "test-order-1",
            "side": "buy",
            "product_symbol": "BTC-USDT-SPOT",
            "is_isolated": False,
            "auto_borrow": False,
            "auto_repay": False,
            "stop_price": "100",
            "type_": "limit",
            "price": "100",
            "size": "1",
        },
        "POST /api/v3/hf/margin/stop-order",
        host="spot",
        query={},
        body={
            "clientOid": "test-order-1",
            "side": "buy",
            "symbol": "BTC-USDT",
            "type": "limit",
            "price": "100",
            "size": "1",
            "isIsolated": False,
            "autoBorrow": False,
            "autoRepay": False,
            "stopPrice": "100",
        },
        signed=True,
    ),
    Case(
        "cancel_margin_stop_order_by_client_oid",
        {"client_oid": "test-order-1"},
        "DELETE /api/v3/hf/margin/stop-order/cancel-by-clientOid",
        host="spot",
        query={"clientOid": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_margin_stop_orders",
        {"trade_type": "MARGIN_TRADE", "product_symbol": "BTC-USDT-SPOT"},
        "DELETE /api/v3/hf/margin/stop-order/cancel",
        host="spot",
        query={"symbol": "BTC-USDT", "tradeType": "MARGIN_TRADE"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_stop_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v3/hf/margin/stop-orders",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_stop_order",
        {"order_id": "test-order-1"},
        "GET /api/v3/hf/margin/stop-order/orderId",
        host="spot",
        query={"orderId": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_stop_order_by_client_oid",
        {"client_oid": "test-order-1"},
        "GET /api/v3/hf/margin/stop-order/clientOid",
        host="spot",
        query={"clientOid": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "place_margin_oco_order",
        {
            "client_oid": "test-order-1",
            "side": "buy",
            "product_symbol": "BTC-USDT-SPOT",
            "price": "100",
            "size": "1",
            "stop_price": "100",
            "limit_price": "100",
            "is_isolated": False,
        },
        "POST /api/v3/hf/margin/oco-order",
        host="spot",
        query={},
        body={
            "clientOid": "test-order-1",
            "side": "buy",
            "symbol": "BTC-USDT",
            "price": "100",
            "size": "1",
            "stopPrice": "100",
            "limitPrice": "100",
            "isIsolated": False,
        },
        signed=True,
    ),
    Case(
        "cancel_margin_oco_order",
        {"order_id": "test-order-1"},
        "DELETE /api/v3/hf/margin/oco-order/cancel-by-id",
        host="spot",
        query={"orderId": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_margin_oco_order_by_client_oid",
        {"client_oid": "test-order-1"},
        "DELETE /api/v3/hf/margin/oco-order/cancel-by-clientOid",
        host="spot",
        query={"clientOid": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "cancel_margin_oco_orders",
        {"product_symbol": "BTC-USDT-SPOT"},
        "DELETE /api/v3/hf/margin/oco-order/cancel",
        host="spot",
        query={"symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_oco_order",
        {"order_id": "test-order-1"},
        "GET /api/v3/hf/margin/oco-order/orderId",
        host="spot",
        query={"orderId": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_oco_order_by_client_oid",
        {"client_oid": "test-order-1"},
        "GET /api/v3/hf/margin/oco-order/clientOid",
        host="spot",
        query={"clientOid": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_oco_order_details",
        {"order_id": "test-order-1"},
        "GET /api/v3/hf/margin/oco-order/detail/orderId",
        host="spot",
        query={"orderId": "test-order-1"},
        body={},
        signed=True,
    ),
    Case(
        "get_margin_oco_orders",
        {"page_size": 20, "current_page": "1", "product_symbol": "BTC-USDT-SPOT"},
        "GET /api/v3/hf/margin/oco-orders",
        host="spot",
        query={"pageSize": "20", "currentPage": "1", "symbol": "BTC-USDT"},
        body={},
        signed=True,
    ),
    Case(
        "place_futures_tpsl_order",
        {
            "client_oid": "test-order-1",
            "side": "buy",
            "product_symbol": "BTC-USDT-SWAP",
            "type_": "limit",
            "price": "100",
            "size": 1,
            "stop_price_type": "MP",
            "trigger_stop_down_price": "100",
        },
        "POST /api/v1/st-orders",
        host="futures",
        query={},
        body={
            "clientOid": "test-order-1",
            "side": "buy",
            "symbol": "XBTUSDTM",
            "type": "limit",
            "stopPriceType": "MP",
            "price": "100",
            "size": 1,
            "triggerStopDownPrice": "100",
        },
        signed=True,
    ),
    Case(
        "cancel_futures_stop_orders",
        {"product_symbol": "BTC-USDT-SWAP"},
        "DELETE /api/v1/stopOrders",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_recent_closed_orders",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/recentDoneOrders",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_stop_orders",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/stopOrders",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_margin_mode",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v2/position/getMarginMode",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "set_futures_margin_mode",
        {"product_symbol": "BTC-USDT-SWAP", "margin_mode": "ISOLATED"},
        "POST /api/v2/position/changeMarginMode",
        host="futures",
        query={},
        body={"symbol": "XBTUSDTM", "marginMode": "ISOLATED"},
        signed=True,
    ),
    Case(
        "set_futures_position_mode",
        {"position_mode": "0"},
        "POST /api/v2/position/switchPositionMode",
        host="futures",
        query={},
        body={"positionMode": "0"},
        signed=True,
    ),
    Case(
        "get_futures_max_open_size",
        {"product_symbol": "BTC-USDT-SWAP", "price": "100", "leverage": 1},
        "GET /api/v2/getMaxOpenSize",
        host="futures",
        query={"symbol": "XBTUSDTM", "price": "100", "leverage": "1"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_position_history",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/history-positions",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_max_withdraw_margin",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/margin/maxWithdrawMargin",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "add_futures_isolated_margin",
        {"product_symbol": "BTC-USDT-SWAP", "margin": "1.25", "biz_no": "test-order-1"},
        "POST /api/v1/position/margin/deposit-margin",
        host="futures",
        query={},
        body={"symbol": "XBTUSDTM", "margin": 1.25, "bizNo": "test-order-1"},
        signed=True,
    ),
    Case(
        "remove_futures_isolated_margin",
        {"product_symbol": "BTC-USDT-SWAP", "withdraw_amount": "1"},
        "POST /api/v1/margin/withdrawMargin",
        host="futures",
        query={},
        body={"symbol": "XBTUSDTM", "withdrawAmount": "1"},
        signed=True,
    ),
    Case(
        "get_futures_cross_margin_risk_limit",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v2/batchGetCrossOrderLimit",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "get_futures_cross_margin_requirement",
        {"product_symbol": "BTC-USDT-SWAP", "position_value": "1"},
        "POST /api/v2/getCrossModeMarginRequirement",
        host="futures",
        query={},
        body={"symbol": "XBTUSDTM", "positionValue": "1"},
        signed=True,
    ),
    Case(
        "get_futures_isolated_margin_risk_limit",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/contracts/risk-limit/XBTUSDTM",
        host="futures",
        query={},
        body={},
        signed=True,
    ),
    Case(
        "set_futures_isolated_margin_risk_limit",
        {"product_symbol": "BTC-USDT-SWAP", "level": 1},
        "POST /api/v1/position/risk-limit-level/change",
        host="futures",
        query={},
        body={"symbol": "XBTUSDTM", "level": 1},
        signed=True,
    ),
    Case(
        "get_futures_current_funding_rate",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/funding-rate/XBTUSDTM/current",
        host="futures",
        query={},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_public_funding_history",
        {"product_symbol": "BTC-USDT-SWAP", "from_": 1700000000000, "to": 1700000060000},
        "GET /api/v1/contract/funding-rates",
        host="futures",
        query={"symbol": "XBTUSDTM", "from": "1700000000000", "to": "1700000060000"},
        body={},
        signed=False,
    ),
    Case(
        "get_futures_funding_history",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/v1/funding-history",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        body={},
        signed=True,
    ),
    Case(
        "batch_cancel_uta_orders",
        {
            "trade_type": "FUTURES",
            "cancel_order_list": [
                {"symbol": "BTC-USDT-SWAP", "orderId": "1", "clientOid": "c"},
                {"symbol": "ETHUSDTM", "clientOid": "d"},
            ],
        },
        "POST /api/ua/v2/unified/order/cancel-batch",
        query={},
        body={
            "tradeType": "FUTURES",
            "cancelOrderList": [
                {"symbol": "XBTUSDTM", "orderId": "1", "clientOid": "c"},
                {"symbol": "ETHUSDTM", "clientOid": "d"},
            ],
        },
    ),
    Case(
        "cancel_uta_orders_by_symbol",
        {
            "trade_type": "FUTURES",
            "product_symbol": "BTC-USDT-SWAP",
            "order_filter": "ADVANCED",
            "margin_mode": "ISOLATED",
        },
        "POST /api/ua/v2/unified/order/cancel-all",
        query={},
        body={
            "tradeType": "FUTURES",
            "symbol": "XBTUSDTM",
            "orderFilter": "ADVANCED",
            "marginMode": "ISOLATED",
        },
    ),
    Case(
        "get_uta_margin_mode",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET /api/ua/v2/unified/position/margin-mode",
        query={"symbol": "XBTUSDTM"},
        body={},
    ),
    Case(
        "set_uta_margin_mode",
        {"product_symbol": "BTC-USDT-SWAP", "margin_mode": "CROSS"},
        "POST /api/ua/v2/unified/position/margin-mode",
        query={},
        body={"symbol": "XBTUSDTM", "marginMode": "CROSS"},
    ),
    Case(
        "modify_uta_position_margin",
        {"product_symbol": "BTC-USDT-SWAP", "type_": "WITHDRAW", "amount": "1.25"},
        "POST /api/ua/v2/unified/position/modify-margin",
        query={},
        body={"symbol": "XBTUSDTM", "type": "WITHDRAW", "amount": 1.25, "tradeType": "FUTURES"},
    ),
    Case(
        "get_uta_max_order_quantity",
        {"trade_type": "SPOT", "product_symbol": "BTC-USDT-SPOT", "price": "123.45"},
        "GET /api/ua/v2/order/max-order-quantity",
        query={"symbol": "BTC-USDT", "tradeType": "SPOT", "price": "123.45"},
        body={},
    ),
    Case(
        "get_uta_leverage",
        {"trade_type": "MARGIN", "currency": "USDT", "margin_mode": "CROSS"},
        "GET /api/ua/v2/unified/account/leverage",
        query={"tradeType": "MARGIN", "currency": "USDT", "marginMode": "CROSS"},
        body={},
    ),
    Case(
        "modify_uta_futures_leverage",
        {"product_symbol": "BTC-USDT-SWAP", "leverage": "3"},
        "POST /api/ua/v2/unified/account/modify-leverage",
        query={},
        body={"symbol": "XBTUSDTM", "leverage": "3"},
    ),
    Case(
        "modify_uta_cross_margin_leverage",
        {"leverage": "2", "currency": "USDT"},
        "POST /api/ua/v2/unified/account/modify-leverage-margin-cross",
        query={},
        body={"currency": "USDT", "leverage": "2"},
    ),
    Case(
        "get_uta_position_history",
        {"product_symbol": "BTC-USDT-SWAP", "last_id": 1234, "page_size": 20},
        "GET /api/ua/v2/position/history",
        query={"symbol": "XBTUSDTM", "lastId": "1234", "pageSize": "20"},
        body={},
    ),
    Case(
        "get_uta_funding_history",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "start_at": 1700000000000,
            "end_at": 1700000060000,
            "last_id": 42,
            "page_size": 200,
        },
        "GET /api/ua/v2/position/funding-history",
        query={
            "symbol": "XBTUSDTM",
            "startAt": "1700000000000",
            "endAt": "1700000060000",
            "lastId": "42",
            "pageSize": "200",
        },
        body={},
    ),
    # Market data (public).
    Case("get_spot_instrument_info", {}, "GET /api/v2/symbols", signed=False),
    Case(
        "get_spot_ticker",
        {"product_symbol": SPOT},
        "GET /api/v1/market/orderbook/level1",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case("get_spot_all_tickers", {}, "GET /api/v1/market/allTickers", signed=False),
    Case(
        "get_spot_orderbook",
        {"product_symbol": SPOT},
        "GET /api/v1/market/orderbook/level2_20",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case(
        "get_spot_orderbook",
        {"product_symbol": SPOT, "depth": 100},
        "GET /api/v1/market/orderbook/level2_100",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case(
        "get_spot_public_trades",
        {"product_symbol": SPOT},
        "GET /api/v1/market/histories",
        query={"symbol": "BTC-USDT"},
        signed=False,
    ),
    Case(
        "get_spot_kline",
        {"product_symbol": SPOT, "timeframe": "1m"},
        "GET /api/v1/market/candles",
        query={"symbol": "BTC-USDT", "type": "1min"},
        signed=False,
    ),
    Case(
        "get_futures_contracts",
        {},
        "GET /api/v1/contracts/active",
        host="futures",
        signed=False,
    ),
    Case(
        "get_futures_contract",
        {"product_symbol": SWAP},
        "GET /api/v1/contracts/XBTUSDTM",
        host="futures",
        signed=False,
    ),
    Case(
        "get_futures_ticker",
        {"product_symbol": SWAP},
        "GET /api/v1/ticker",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_orderbook",
        {"product_symbol": SWAP},
        "GET /api/v1/level2/snapshot",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_orderbook",
        {"product_symbol": SWAP, "depth": "100"},
        "GET /api/v1/level2/depth100",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_public_trades",
        {"product_symbol": SWAP},
        "GET /api/v1/trade/history",
        host="futures",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_futures_kline",
        {"product_symbol": SWAP, "timeframe": "1m"},
        "GET /api/v1/kline/query",
        host="futures",
        query={"symbol": "XBTUSDTM", "granularity": "1"},
        signed=False,
    ),
    Case(
        "get_futures_open_interest",
        {"product_symbol": SWAP},
        "GET /api/ua/v2/market/open-interest",
        query={"symbol": "XBTUSDTM"},
        signed=False,
    ),
    Case(
        "get_uta_position_tiers",
        {
            "product_symbol": SWAP,
            "tradeType": "FUTURES",
            "marginMode": "CROSS",
            "data": "RISK_LIMIT",
            "accountType": "UNIFIED",
        },
        "GET /api/ua/v2/market/position-tiers",
        query={"symbol": "XBTUSDTM", "tradeType": "FUTURES"},
        signed=False,
    ),
    # Margin market data (public).
    Case("get_cross_margin_symbols", {}, "GET /api/v3/margin/symbols", signed=False),
    Case("get_isolated_margin_symbols", {}, "GET /api/v1/isolated/symbols", signed=False),
    Case(
        "get_margin_collateral_ratio",
        {},
        "GET /api/v3/margin/collateralRatio",
        signed=False,
    ),
    Case(
        "get_margin_available_inventory",
        {"currency": "USDT"},
        "GET /api/v3/margin/available-inventory",
        query={"currency": "USDT"},
        signed=False,
    ),
    Case(
        "get_margin_loan_market_interest_rate",
        {"currency": "USDT"},
        "GET /api/v3/project/marketInterestRate",
        query={"currency": "USDT"},
        signed=False,
    ),
    # Account, fees, transfers, sub-accounts.
    Case(
        "get_spot_fee_rates",
        {"product_symbol": SPOT},
        "GET /api/v1/trade-fees",
        query={"symbols": "BTC-USDT"},
    ),
    Case(
        "get_futures_fee_rates",
        {"product_symbol": SWAP},
        "GET /api/v1/trade-fees",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_uta_fee_rates",
        {"tradeType": "SPOT", "symbol": "BTC-USDT"},
        "GET /api/ua/v2/user/fee-rate",
        query={"tradeType": "SPOT", "symbol": "BTC-USDT"},
    ),
    Case(
        "get_account_balance",
        {"currency": "USDT", "type": "trade"},
        "GET /api/v1/accounts",
        query={"currency": "USDT", "type": "trade"},
    ),
    Case(
        "get_transfer_quotas",
        {"currency": "USDT", "account_type": "MAIN"},
        "GET /api/v1/accounts/transferable",
        query={"currency": "USDT", "type": "MAIN"},
    ),
    Case(
        "flex_transfer",
        {
            "currency": "USDT",
            "amount": "1",
            "fromAccountType": "MAIN",
            "toAccountType": "TRADE",
        },
        "POST /api/v3/accounts/universal-transfer",
        body={"currency": "USDT", "amount": "1", "type": "INTERNAL"},
    ),
    Case("get_subaccounts", {}, "GET /api/v2/sub/user"),
    Case(
        "get_subaccount_balance",
        {"subUserId": "123"},
        "GET /api/v1/sub-accounts/123",
    ),
    Case("get_spot_subaccount_balances", {}, "GET /api/v2/sub-accounts"),
    Case(
        "get_futures_subaccount_balances",
        {"currency": "USDT"},
        "GET /api/v1/account-overview-all",
        host="futures",
        query={"currency": "USDT"},
    ),
    Case("get_uta_subaccounts", {}, "GET /api/ua/v2/user/sub-account-list"),
    Case(
        "get_uta_subaccount_currency_assets",
        {},
        "GET /api/ua/v2/sub-account/balance",
    ),
    Case(
        "get_futures_account",
        {"currency": "USDT"},
        "GET /api/v1/account-overview",
        host="futures",
        query={"currency": "USDT"},
    ),
    Case("get_futures_positions", {}, "GET /api/v1/positions", host="futures"),
    Case(
        "get_futures_position",
        {"product_symbol": SWAP},
        "GET /api/v2/position",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_position_mode",
        {},
        "GET /api/v2/position/getPositionMode",
        host="futures",
    ),
    Case(
        "get_futures_cross_margin_leverage",
        {"product_symbol": SWAP},
        "GET /api/v2/getCrossUserLeverage",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "modify_futures_cross_margin_leverage",
        {"product_symbol": SWAP, "leverage": "5"},
        "POST /api/v2/changeCrossUserLeverage",
        host="futures",
        body={"symbol": "XBTUSDTM", "leverage": "5"},
    ),
    Case("get_uta_positions", {}, "GET /api/ua/v2/unified/position/open-list"),
    Case("get_uta_account_balance", {}, "GET /api/ua/v2/unified/account/balance"),
    Case("get_uta_account_overview", {}, "GET /api/ua/v2/unified/account/overview"),
    # Earn.
    Case(
        "purchase_earn",
        {"productId": "1", "amount": "10", "accountType": "MAIN"},
        "POST /api/v1/earn/orders",
        body={"productId": "1", "amount": "10", "accountType": "MAIN"},
    ),
    Case(
        "get_earn_redeem_preview",
        {"orderId": "1", "fromAccountType": "MAIN"},
        "GET /api/v1/earn/redeem-preview",
        query={"orderId": "1", "fromAccountType": "MAIN"},
    ),
    Case(
        "redeem_earn",
        {"orderId": "1", "amount": "10"},
        "DELETE /api/v1/earn/orders",
        query={"orderId": "1", "amount": "10"},
    ),
    Case(
        "get_earn_savings_products",
        {"currency": "USDT"},
        "GET /api/v1/earn/saving/products",
        query={"currency": "USDT"},
    ),
    Case("get_earn_promotion_products", {}, "GET /api/v1/earn/promotion/products"),
    Case("get_earn_staking_products", {}, "GET /api/v1/earn/staking/products"),
    Case("get_earn_kcs_staking_products", {}, "GET /api/v1/earn/kcs-staking/products"),
    Case("get_earn_eth_staking_products", {}, "GET /api/v1/earn/eth-staking/products"),
    Case("get_earn_account_holdings", {}, "GET /api/v1/earn/hold-assets"),
    Case(
        "get_dual_investment_products",
        {
            "category": "DUAL_CLASSIC",
            "strikeCurrency": "BTC",
            "investCurrency": "USDT",
            "side": "CALL",
        },
        "GET /api/v1/struct-earn/dual/products",
        query={"category": "DUAL_CLASSIC"},
    ),
    Case(
        "purchase_structured_earn",
        {
            "productId": "1",
            "investCurrency": "USDT",
            "investAmount": "10",
            "accountType": "MAIN",
        },
        "POST /api/v1/struct-earn/orders",
        body={"productId": "1", "investCurrency": "USDT"},
    ),
    Case(
        "get_structured_earn_orders",
        {"categories": "DUAL_CLASSIC"},
        "GET /api/v1/struct-earn/orders",
        query={"categories": "DUAL_CLASSIC"},
    ),
    # Margin (private).
    Case("get_cross_margin_account", {}, "GET /api/v3/margin/accounts"),
    Case("get_isolated_margin_account", {}, "GET /api/v3/isolated/accounts"),
    Case(
        "get_margin_borrow_interest_rate",
        {"currency": "USDT"},
        "GET /api/v3/margin/borrowRate",
        query={"currency": "USDT"},
    ),
    Case(
        "borrow_margin",
        {"currency": "USDT", "size": "10", "timeInForce": "IOC"},
        "POST /api/v3/margin/borrow",
        body={"currency": "USDT", "size": "10", "timeInForce": "IOC"},
    ),
    Case(
        "get_margin_borrow_history",
        {"currency": "USDT"},
        "GET /api/v3/margin/borrow",
        query={"currency": "USDT"},
    ),
    Case(
        "repay_margin",
        {"currency": "USDT", "size": "10"},
        "POST /api/v3/margin/repay",
        body={"currency": "USDT", "size": "10"},
    ),
    Case(
        "get_margin_repay_history",
        {"currency": "USDT"},
        "GET /api/v3/margin/repay",
        query={"currency": "USDT"},
    ),
    Case(
        "get_margin_interest_history",
        {"currency": "USDT", "product_symbol": SPOT},
        "GET /api/v3/margin/interest",
        query={"currency": "USDT", "symbol": "BTC-USDT"},
    ),
    Case(
        "modify_margin_leverage",
        {"leverage": "3"},
        "POST /api/v3/position/update-user-leverage",
        body={"leverage": "3"},
    ),
    Case(
        "get_margin_loan_market",
        {"currency": "USDT"},
        "GET /api/v3/project/list",
        query={"currency": "USDT"},
    ),
    Case(
        "purchase_margin_lending",
        {"currency": "USDT", "size": "10", "interestRate": "0.01"},
        "POST /api/v3/purchase",
        body={"currency": "USDT", "size": "10", "interestRate": "0.01"},
    ),
    Case(
        "modify_margin_lending_purchase",
        {"currency": "USDT", "purchaseOrderNo": "1", "interestRate": "0.01"},
        "POST /api/v3/lend/purchase/update",
        body={"currency": "USDT", "purchaseOrderNo": "1"},
    ),
    Case(
        "get_margin_lending_purchase_orders",
        {"status": "DONE", "currency": "USDT"},
        "GET /api/v3/purchase/orders",
        query={"status": "DONE", "currency": "USDT"},
    ),
    Case(
        "redeem_margin_lending",
        {"currency": "USDT", "size": "10", "purchaseOrderNo": "1"},
        "POST /api/v3/redeem",
        body={"currency": "USDT", "size": "10", "purchaseOrderNo": "1"},
    ),
    Case(
        "get_margin_lending_redeem_orders",
        {"status": "DONE", "currency": "USDT"},
        "GET /api/v3/redeem/orders",
        query={"status": "DONE", "currency": "USDT"},
    ),
    # Dead-man switch.
    Case(
        "set_dcp",
        {"timeout": 10, "symbols": ["BTC-USDT"]},
        "POST /api/v1/hf/orders/dead-cancel-all",
        body={"timeout": 10, "symbols": "BTC-USDT"},
    ),
    Case("get_dcp", {}, "GET /api/v1/hf/orders/dead-cancel-all/query"),
    # Spot HF orders.
    Case(
        "place_spot_order",
        {"product_symbol": SPOT, "side": "buy", "type_": "limit", **LIMIT},
        "POST /api/v1/hf/orders",
        body={"symbol": "BTC-USDT", "side": "buy", "type": "limit", "price": "100"},
    ),
    Case(
        "test_spot_order",
        {"product_symbol": SPOT, "side": "buy", "type_": "limit", **LIMIT},
        "POST /api/v1/hf/orders/test",
        body={"symbol": "BTC-USDT", "side": "buy", "type": "limit"},
    ),
    Case(
        "place_spot_market_order",
        {"product_symbol": SPOT, "side": "buy", "size": "1"},
        "POST /api/v1/hf/orders",
        body={"symbol": "BTC-USDT", "side": "buy", "type": "market"},
    ),
    Case(
        "place_spot_market_buy_order",
        {"product_symbol": SPOT, "funds": "10"},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "market", "funds": "10"},
    ),
    Case(
        "place_spot_market_sell_order",
        {"product_symbol": SPOT, "size": "1"},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "market"},
    ),
    Case(
        "place_spot_limit_order",
        {"product_symbol": SPOT, "side": "sell", **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "limit"},
    ),
    Case(
        "place_spot_limit_buy_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "limit"},
    ),
    Case(
        "place_spot_limit_sell_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "limit"},
    ),
    Case(
        "place_spot_post_only_limit_order",
        {"product_symbol": SPOT, "side": "buy", **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_spot_post_only_limit_buy_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "buy", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_spot_post_only_limit_sell_order",
        {"product_symbol": SPOT, **LIMIT},
        "POST /api/v1/hf/orders",
        body={"side": "sell", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_spot_batch_orders",
        {
            "orders": [
                {
                    "product_symbol": SPOT,
                    "side": "buy",
                    "type": "limit",
                    "size": "1",
                    "price": "100",
                }
            ]
        },
        "POST /api/v1/hf/orders/multi",
    ),
    Case(
        "place_spot_batch_limit_orders",
        {"orders": [{"product_symbol": SPOT, "side": "buy", "size": "1", "price": "100"}]},
        "POST /api/v1/hf/orders/multi",
    ),
    Case(
        "place_spot_batch_market_orders",
        {"orders": [{"product_symbol": SPOT, "side": "buy", "size": "1"}]},
        "POST /api/v1/hf/orders/multi",
    ),
    Case(
        "alter_spot_order",
        {"product_symbol": SPOT, "orderId": "1", "newPrice": "101"},
        "POST /api/v1/hf/orders/alter",
        body={"symbol": "BTC-USDT", "orderId": "1", "newPrice": "101"},
    ),
    Case(
        "cancel_spot_order",
        {"orderId": "abc", "product_symbol": SPOT},
        "DELETE /api/v1/hf/orders/abc",
        query={"symbol": "BTC-USDT"},
    ),
    Case(
        "cancel_spot_all_orders_by_symbol",
        {"product_symbol": SPOT},
        "DELETE /api/v1/hf/orders",
        query={"symbol": "BTC-USDT"},
    ),
    Case("cancel_spot_all_orders", {}, "DELETE /api/v1/hf/orders/cancelAll"),
    Case(
        "get_spot_open_orders",
        {"product_symbol": SPOT},
        "GET /api/v1/hf/orders/active/page",
        query={"symbol": "BTC-USDT"},
    ),
    Case(
        "get_spot_trade_history",
        {"product_symbol": SPOT},
        "GET /api/v1/hf/fills",
        query={"symbol": "BTC-USDT"},
    ),
    # Futures orders.
    Case(
        "place_futures_order",
        {"product_symbol": SWAP, "side": "buy", "type_": "limit", **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"symbol": "XBTUSDTM", "side": "buy", "type": "limit", "size": 1},
    ),
    Case(
        "test_futures_order",
        {"product_symbol": SWAP, "side": "buy", "type_": "limit", **FUT_LIMIT},
        "POST /api/v1/orders/test",
        host="futures",
        body={"symbol": "XBTUSDTM", "side": "buy"},
    ),
    Case(
        "place_futures_market_order",
        {"product_symbol": SWAP, "side": "buy", "size": "1", "leverage": 3},
        "POST /api/v1/orders",
        host="futures",
        body={"symbol": "XBTUSDTM", "side": "buy", "type": "market"},
    ),
    Case(
        "place_futures_market_buy_order",
        {"product_symbol": SWAP, "size": "1", "leverage": 3},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "type": "market"},
    ),
    Case(
        "place_futures_market_sell_order",
        {"product_symbol": SWAP, "size": "1", "leverage": 3},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "type": "market"},
    ),
    Case(
        "place_futures_limit_order",
        {"product_symbol": SWAP, "side": "sell", **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "type": "limit", "price": "100"},
    ),
    Case(
        "place_futures_limit_buy_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "type": "limit"},
    ),
    Case(
        "place_futures_limit_sell_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "type": "limit"},
    ),
    Case(
        "place_futures_post_only_limit_order",
        {"product_symbol": SWAP, "side": "buy", **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "type": "limit", "postOnly": True},
    ),
    Case(
        "place_futures_post_only_limit_buy_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "buy", "postOnly": True},
    ),
    Case(
        "place_futures_post_only_limit_sell_order",
        {"product_symbol": SWAP, **FUT_LIMIT},
        "POST /api/v1/orders",
        host="futures",
        body={"side": "sell", "postOnly": True},
    ),
    Case(
        "get_futures_order_list",
        {"status": "active"},
        "GET /api/v1/orders",
        host="futures",
        query={"status": "active"},
    ),
    Case(
        "get_futures_order",
        {"orderId": "abc"},
        "GET /api/v1/orders/abc",
        host="futures",
    ),
    Case(
        "get_futures_order_by_client_oid",
        {"clientOid": "cid"},
        "GET /api/v1/orders/byClientOid",
        host="futures",
        query={"clientOid": "cid"},
    ),
    Case(
        "cancel_futures_order",
        {"orderId": "abc"},
        "DELETE /api/v1/orders/abc",
        host="futures",
    ),
    Case(
        "cancel_futures_order_by_client_oid",
        {"clientOid": "cid", "product_symbol": SWAP},
        "DELETE /api/v1/orders/client-order/cid",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "cancel_futures_all_orders",
        {"product_symbol": SWAP},
        "DELETE /api/v3/orders",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_open_order_value",
        {"product_symbol": SWAP},
        "GET /api/v1/openOrderStatistics",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_trade_history",
        {"product_symbol": SWAP},
        "GET /api/v1/fills",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    Case(
        "get_futures_recent_trade_history",
        {"product_symbol": SWAP},
        "GET /api/v1/recentFills",
        host="futures",
        query={"symbol": "XBTUSDTM"},
    ),
    # UTA orders.
    Case(
        "place_uta_order",
        {
            "trade_type": "SPOT",
            "product_symbol": SPOT,
            "side": "BUY",
            "order_type": "LIMIT",
            "size": "1",
            "size_unit": "BASECCY",
            "price": "100",
            "time_in_force": "GTT",
            "cancel_after": 60,
            "stp": "CN",
        },
        "POST /api/ua/v2/unified/order/place",
        body={
            "tradeType": "SPOT",
            "symbol": "BTC-USDT",
            "side": "BUY",
            "orderType": "LIMIT",
            "sizeUnit": "BASECCY",
            "cancelAfter": 60,
            "stp": "CN",
        },
    ),
    Case(
        "cancel_uta_order",
        {"trade_type": "SPOT", "product_symbol": SPOT, "order_id": "1"},
        "POST /api/ua/v2/unified/order/cancel",
        body={"tradeType": "SPOT", "symbol": "BTC-USDT", "orderId": "1"},
    ),
    Case(
        "amend_uta_order",
        {
            "product_symbol": SWAP,
            "order_id": "1",
            "new_price": "101",
            "size_unit": "UNIT",
            "cxl_on_fail": True,
            "tp_trigger_price": "120",
            "sl_trigger_price": "80",
            "sl_trigger_price_type": "MP",
        },
        "POST /api/ua/v2/unified/order/amend",
        body={
            "symbol": "XBTUSDTM",
            "orderId": "1",
            "newPrice": "101",
            "sizeUnit": "UNIT",
            "cxlOnFail": True,
            "tpTriggerPrice": "120",
            "slTriggerPrice": "80",
            "slTriggerPriceType": "MP",
        },
    ),
    Case(
        "get_uta_order_detail",
        {"trade_type": "SPOT", "product_symbol": SPOT, "order_id": "1"},
        "GET /api/ua/v2/unified/order/detail",
        query={"tradeType": "SPOT", "symbol": "BTC-USDT", "orderId": "1"},
    ),
    Case(
        "get_uta_open_orders",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/unified/order/open-list",
        query={"tradeType": "SPOT"},
    ),
    Case(
        "get_uta_order_history",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/unified/order/history",
        query={"tradeType": "SPOT"},
    ),
    Case(
        "get_uta_trade_history",
        {"trade_type": "SPOT"},
        "GET /api/ua/v2/unified/order/execution",
        query={"tradeType": "SPOT"},
    ),
)


def _params(cases: tuple[Case, ...]) -> list[Any]:
    return [pytest.param(case, id=case.id) for case in cases]


@contextmanager
def _capture_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    payload = json.dumps({"code": "200000", "data": {}}).encode()

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            received.put(
                {
                    "method": self.command,
                    "path": self.path,
                    "headers": {key.lower(): value for key, value in self.headers.items()},
                    "body": self.rfile.read(length).decode() if length else "",
                }
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = _handle  # noqa: N815

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


def _client_kwargs(spot_url: str, futures_url: str) -> dict[str, Any]:
    return {
        "api_key": "api-key",
        "api_secret": "api-secret",
        "passphrase": "passphrase",
        "base_url": spot_url,
        "futures_base_url": futures_url,
        "preload_product_table": False,
        "timeout": 5,
    }


def _assert_request(
    case: Case,
    spot: queue.Queue[dict[str, Any]],
    futures: queue.Queue[dict[str, Any]],
) -> None:
    target, other = (spot, futures) if case.host == "spot" else (futures, spot)
    assert other.empty(), f"{case.method_name} was sent to the wrong KuCoin host"
    request = target.get_nowait()
    from tests.unit.wire_contracts import assert_wire_contract
    assert_wire_contract("kucoin", case.method_name, request)
    assert target.empty(), f"{case.method_name} sent more than one request"

    method, path = case.route.split(" ", 1)
    parts = urlsplit(request["path"])
    assert (request["method"], parts.path) == (method, path)
    query = dict(parse_qsl(parts.query))
    for key, value in case.query.items():
        assert query.get(key) == value, f"{case.method_name} query {query!r}"

    if case.body:
        body = json.loads(request["body"])
        if isinstance(case.body, list):
            assert body == case.body, f"{case.method_name} body {body!r}"
        else:
            for key, value in case.body.items():
                assert body.get(key) == value, f"{case.method_name} body {body!r}"
    elif method == "POST":
        assert isinstance(json.loads(request["body"]), dict | list)

    headers = request["headers"]
    if case.method_name == "cancel_futures_batch_orders":
        import base64
        import hashlib
        import hmac

        assert parts.query == ""
        prehash = headers["kc-api-timestamp"] + "DELETE" + parts.path + request["body"]
        expected = base64.b64encode(
            hmac.new(b"api-secret", prehash.encode(), hashlib.sha256).digest()
        ).decode()
        assert headers["kc-api-sign"] == expected
    if case.signed:
        assert headers.get("kc-api-key") == "api-key"
        assert headers.get("kc-api-sign")
        assert headers.get("kc-api-key-version") == "2"
    else:
        assert "kc-api-sign" not in headers


def _fail_if_native_is_stale(exc: ValueError, case: Case) -> None:
    """Fail when the installed ``dcex._native`` build predates this dispatch name."""
    message = str(exc)
    if "unsupported KuCoin" in message and "method" in message:
        pytest.fail(
            f"installed dcex._native does not know {case.method_name!r}; "
            "rebuild the extension (maturin develop) to exercise it"
        )
    raise exc


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex" / ("async_support" if mode == "async" else "") / "kucoin"
    module = "dcex.async_support.kucoin.client" if mode == "async" else "dcex.kucoin.client"
    client_cls = __import__(module, fromlist=["Client"]).Client
    names: set[str] = set()
    for path in base.glob("_*_http.py"):
        if path.name == "_http_manager.py":
            continue
        for name, member in inspect.getmembers(client_cls, inspect.isfunction):
            if name.startswith("_") or name in {"close", "async_init"}:
                continue
            if inspect.getsourcefile(member) == str(path):
                names.add(name)
    return names


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_every_kucoin_wrapper_has_a_route_case(mode: str) -> None:
    from tests.unit.test_kucoin_schema_requests import NAMES

    covered = {case.method_name for case in CASES} | NAMES
    missing = _wrapper_names(mode) - covered
    assert not missing, f"add route cases for: {sorted(missing)}"


@pytest.mark.parametrize("case", _params(CASES))
def test_sync_kucoin_wrapper_hits_documented_route(case: Case) -> None:
    from dcex.kucoin.client import Client

    with _capture_server() as (spot_url, spot), _capture_server() as (futures_url, futures):
        client = Client(**_client_kwargs(spot_url, futures_url))
        try:
            result = getattr(client, case.method_name)(**case.kwargs)
        except ValueError as exc:
            _fail_if_native_is_stale(exc, case)
        finally:
            client.close()
        assert result == {"code": "200000", "data": {}}
        _assert_request(case, spot, futures)


@pytest.mark.asyncio
@pytest.mark.parametrize("case", _params(CASES))
async def test_async_kucoin_wrapper_hits_documented_route(case: Case) -> None:
    from dcex.async_support.kucoin.client import Client

    with _capture_server() as (spot_url, spot), _capture_server() as (futures_url, futures):
        client = Client(**_client_kwargs(spot_url, futures_url))
        await client.async_init()
        try:
            result = await getattr(client, case.method_name)(**case.kwargs)
        except ValueError as exc:
            _fail_if_native_is_stale(exc, case)
        finally:
            await client.close()
        assert result == {"code": "200000", "data": {}}
        _assert_request(case, spot, futures)


def test_set_dcp_sends_documented_symbols_field() -> None:
    from dcex.kucoin.client import Client

    with _capture_server() as (spot_url, spot), _capture_server() as (futures_url, _futures):
        client = Client(**_client_kwargs(spot_url, futures_url))
        try:
            client.set_dcp(timeout=10, symbols=["BTC-USDT", "ETH-USDT"])
            client.set_dcp(timeout=-1)
        finally:
            client.close()
        armed = json.loads(spot.get_nowait()["body"])
        unset = json.loads(spot.get_nowait()["body"])
    assert armed == {"timeout": 10, "symbols": "BTC-USDT,ETH-USDT"}
    assert unset == {"timeout": -1}


def test_uta_amend_rejects_spot_symbol_and_place_requires_size_unit() -> None:
    from dcex.kucoin.client import Client

    client = Client(**_client_kwargs("http://127.0.0.1:9", "http://127.0.0.1:9"))
    try:
        with pytest.raises(ValueError, match="futures only"):
            client.amend_uta_order(SPOT, order_id="1", new_price="101")
        with pytest.raises(TypeError, match="size_unit"):
            client.place_uta_order("SPOT", SPOT, "BUY", "MARKET", "1")  # type: ignore[call-arg]
    finally:
        client.close()


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("get_uta_account_ledgers", {"account_type": "FUTURES", "page_size": 101}),
        ("get_uta_account_ledgers", {"account_type": "UNIFIED", "page_size": 201}),
        (
            "get_uta_orderbook",
            {
                "trade_type": "SPOT",
                "product_symbol": "BTC-USDT-SPOT",
                "limit": "20",
                "rpi_filter": 1,
            },
        ),
        (
            "get_uta_klines",
            {
                "trade_type": "SPOT",
                "product_symbol": "BTC-USDT-SPOT",
                "interval": "1min",
                "kline_type": "MARK",
            },
        ),
        (
            "get_uta_klines",
            {"trade_type": "FUTURES", "product_symbol": "BTC-USDT-SWAP", "interval": "6hour"},
        ),
        (
            "get_uta_klines",
            {
                "trade_type": "FUTURES",
                "product_symbol": "BTC-USDT-SWAP",
                "interval": "1min",
                "start_at": 2000,
                "end_at": 1000,
            },
        ),
        ("get_uta_transfer_quota", {"account_type": "ISOLATED", "currency": "USDT"}),
        ("get_classic_account_balances_v2", {"account_type": "ISOLATED"}),
        ("get_margin_currency_risk_limits", {"is_isolated": True}),
        ("get_margin_currency_risk_limits", {}),
        (
            "transfer_uta_accounts",
            {
                "client_oid": "t1",
                "transfer_type": "PARENT_TO_SUB",
                "currency": "USDT",
                "amount": "1",
                "from_account_type": "UNIFIED",
                "from_account_tag": "DEFAULT",
                "to_account_type": "UNIFIED",
                "to_account_tag": "DEFAULT",
            },
        ),
        (
            "transfer_uta_accounts",
            {
                "client_oid": "t1",
                "transfer_type": "INTERNAL",
                "currency": "USDT",
                "amount": "NaN",
                "from_account_type": "UNIFIED",
                "from_account_tag": "DEFAULT",
                "to_account_type": "SPOT",
                "to_account_tag": "DEFAULT",
            },
        ),
    ],
)
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_kucoin_risk_conditions_before_transport(
    method: str, kwargs: dict[str, Any], mode: str
) -> None:
    from dcex.async_support.kucoin.client import Client as AsyncClient
    from dcex.kucoin.client import Client

    options = _client_kwargs("http://127.0.0.1:1", "http://127.0.0.1:1")
    if mode == "sync":
        client = Client(**options)
        try:
            with pytest.raises(ValueError):
                getattr(client, method)(**kwargs)
        finally:
            client.close()
    else:
        async_client = await AsyncClient(**options).async_init()
        try:
            with pytest.raises(ValueError):
                await getattr(async_client, method)(**kwargs)
        finally:
            await async_client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_convert_decimal_precision_and_repeated_query_arrays(mode: str) -> None:
    """Decimal input survives JSON encoding; array filters remain repeated query keys."""
    from urllib.parse import parse_qsl, urlsplit

    from dcex.async_support.kucoin.client import Client as AsyncClient
    from dcex.kucoin.client import Client
    from tests.unit.native_http_helpers import _http_server

    amount = "0.123456789012345678901234567890"
    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = (AsyncClient if mode == "async" else Client)(**_client_kwargs(base, base))
        try:
            if mode == "async":
                await client.async_init()
                await client.add_convert_limit_order(
                    client_order_id="precision",
                    from_currency="BTC",
                    to_currency="USDT",
                    from_currency_size=amount,
                    to_currency_size="1.00000000000000000001",
                )
                await client.get_uta_fiat_price(base="USD", currencies=["BTC", "ETH"])
            else:
                client.add_convert_limit_order(
                    client_order_id="precision",
                    from_currency="BTC",
                    to_currency="USDT",
                    from_currency_size=amount,
                    to_currency_size="1.00000000000000000001",
                )
                client.get_uta_fiat_price(base="USD", currencies=["BTC", "ETH"])
        finally:
            if mode == "async":
                await client.close()
            else:
                client.close()
        order = received.get_nowait()
        assert '"fromCurrencySize":' + amount in order["body"]
        assert '"toCurrencySize":1.00000000000000000001' in order["body"]
        query = parse_qsl(urlsplit(received.get_nowait()["path"]).query)
        assert query == [("base", "USD"), ("currencies", "BTC"), ("currencies", "ETH")]
