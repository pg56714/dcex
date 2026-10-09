"""
End-to-end offline coverage for every OKX REST wrapper.

Each public wrapper on the sync and async OKX clients is driven through the
real native extension against a local HTTP server, and the resulting HTTP
method, path, signing mode and key parameters are checked against the official
OKX v5 routes. This complements the auto-generated wrapper tests (which stub
the native client) and also covers ``_finance_http.py`` and
``_subaccount_http.py``, which are outside ``ENDPOINT_FILE_SUFFIXES``.
"""
# ruff: noqa: D101, D103, ANN401

from __future__ import annotations

import ast
import base64
import hashlib
import hmac
import json
import queue
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
SPRD = "BTC-USDT_BTC-USDT-SWAP"
SWAP = "BTC-USDT-SWAP"


@dataclass(frozen=True)
class Case:
    name: str
    method: str
    path: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    signed: bool = True
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] | list[dict[str, Any]] = field(default_factory=dict)


def pub(
    name: str, path: str, *args: Any, query: dict[str, str] | None = None, **kwargs: Any
) -> Case:
    return Case(name, "GET", path, args, kwargs, signed=False, query=query or {})


def get(
    name: str, path: str, *args: Any, query: dict[str, str] | None = None, **kwargs: Any
) -> Case:
    return Case(name, "GET", path, args, kwargs, query=query or {})


def post(
    name: str, path: str, *args: Any, body: dict[str, Any] | None = None, **kwargs: Any
) -> Case:
    return Case(name, "POST", path, args, kwargs, body=body or {})


CASES: tuple[Case, ...] = (
    Case(
        "trading_bot_grid_order_algo",
        "POST",
        "/api/v5/tradingBot/grid/order-algo",
        kwargs={
            "inst_id": "BTC-USDT",
            "algo_ord_type": "grid",
            "max_px": "60000",
            "min_px": "40000",
            "grid_num": "10",
            "quote_sz": "100",
        },
        signed=True,
        body={
            "instId": "BTC-USDT",
            "algoOrdType": "grid",
            "maxPx": "60000",
            "minPx": "40000",
            "gridNum": "10",
            "quoteSz": "100",
        },
    ),
    Case(
        "trading_bot_grid_amend_algo_basic_param",
        "POST",
        "/api/v5/tradingBot/grid/amend-algo-basic-param",
        kwargs={"algo_id": "1", "min_px": "40000", "max_px": "60000", "grid_num": "10"},
        signed=True,
        body={"algoId": "1", "minPx": "40000", "maxPx": "60000", "gridNum": "10"},
    ),
    Case(
        "trading_bot_grid_amend_order_algo",
        "POST",
        "/api/v5/tradingBot/grid/amend-order-algo",
        kwargs={"algo_id": "1", "inst_id": "BTC-USDT"},
        signed=True,
        body={"algoId": "1", "instId": "BTC-USDT"},
    ),
    Case(
        "trading_bot_grid_stop_order_algo",
        "POST",
        "/api/v5/tradingBot/grid/stop-order-algo",
        kwargs={
            "orders": [
                {"algoId": "1", "instId": "BTC-USDT", "algoOrdType": "grid", "stopType": "1"}
            ]
        },
        signed=True,
        body=[{"algoId": "1", "instId": "BTC-USDT", "algoOrdType": "grid", "stopType": "1"}],
    ),
    Case(
        "trading_bot_grid_close_position",
        "POST",
        "/api/v5/tradingBot/grid/close-position",
        kwargs={"algo_id": "1", "mkt_close": True},
        signed=True,
        body={"algoId": "1", "mktClose": True},
    ),
    Case(
        "trading_bot_grid_cancel_close_order",
        "POST",
        "/api/v5/tradingBot/grid/cancel-close-order",
        kwargs={"algo_id": "1", "ord_id": "1"},
        signed=True,
        body={"algoId": "1", "ordId": "1"},
    ),
    Case(
        "trading_bot_grid_order_instant_trigger",
        "POST",
        "/api/v5/tradingBot/grid/order-instant-trigger",
        kwargs={"algo_id": "1"},
        signed=True,
        body={"algoId": "1"},
    ),
    Case(
        "get_trading_bot_grid_orders_algo_pending",
        "GET",
        "/api/v5/tradingBot/grid/orders-algo-pending",
        kwargs={"algo_ord_type": "grid"},
        signed=True,
        query={"algoOrdType": "grid"},
    ),
    Case(
        "get_trading_bot_grid_orders_algo_history",
        "GET",
        "/api/v5/tradingBot/grid/orders-algo-history",
        kwargs={"algo_ord_type": "grid"},
        signed=True,
        query={"algoOrdType": "grid"},
    ),
    Case(
        "get_trading_bot_grid_orders_algo_details",
        "GET",
        "/api/v5/tradingBot/grid/orders-algo-details",
        kwargs={"algo_ord_type": "grid", "algo_id": "1"},
        signed=True,
        query={"algoOrdType": "grid", "algoId": "1"},
    ),
    Case(
        "get_trading_bot_grid_sub_orders",
        "GET",
        "/api/v5/tradingBot/grid/sub-orders",
        kwargs={"algo_ord_type": "grid", "algo_id": "1", "type_": "1"},
        signed=True,
        query={"algoOrdType": "grid", "algoId": "1", "type": "1"},
    ),
    Case(
        "get_trading_bot_grid_positions",
        "GET",
        "/api/v5/tradingBot/grid/positions",
        kwargs={"algo_ord_type": "grid", "algo_id": "1"},
        signed=True,
        query={"algoOrdType": "grid", "algoId": "1"},
    ),
    Case(
        "trading_bot_grid_withdraw_income",
        "POST",
        "/api/v5/tradingBot/grid/withdraw-income",
        kwargs={"algo_id": "1"},
        signed=True,
        body={"algoId": "1"},
    ),
    Case(
        "trading_bot_grid_compute_margin_balance",
        "POST",
        "/api/v5/tradingBot/grid/compute-margin-balance",
        kwargs={"algo_id": "1", "type_": "1"},
        signed=True,
        body={"algoId": "1", "type": "1"},
    ),
    Case(
        "trading_bot_grid_margin_balance",
        "POST",
        "/api/v5/tradingBot/grid/margin-balance",
        kwargs={"algo_id": "1", "type_": "1"},
        signed=True,
        body={"algoId": "1", "type": "1"},
    ),
    Case(
        "trading_bot_grid_adjust_investment",
        "POST",
        "/api/v5/tradingBot/grid/adjust-investment",
        kwargs={"algo_id": "1", "amt": "100"},
        signed=True,
        body={"algoId": "1", "amt": "100"},
    ),
    Case(
        "get_trading_bot_grid_ai_param",
        "GET",
        "/api/v5/tradingBot/grid/ai-param",
        kwargs={"algo_ord_type": "grid", "inst_id": "BTC-USDT"},
        signed=False,
        query={"algoOrdType": "grid", "instId": "BTC-USDT"},
    ),
    Case(
        "trading_bot_grid_min_investment",
        "POST",
        "/api/v5/tradingBot/grid/min-investment",
        kwargs={
            "inst_id": "BTC-USDT",
            "algo_ord_type": "grid",
            "max_px": "60000",
            "min_px": "40000",
            "grid_num": "10",
            "run_type": "1",
        },
        signed=False,
        body={
            "instId": "BTC-USDT",
            "algoOrdType": "grid",
            "maxPx": "60000",
            "minPx": "40000",
            "gridNum": "10",
            "runType": "1",
        },
    ),
    Case(
        "get_trading_bot_public_rsi_back_testing",
        "GET",
        "/api/v5/tradingBot/public/rsi-back-testing",
        kwargs={"inst_id": "BTC-USDT", "timeframe": "1H", "thold": "50", "time_period": "14"},
        signed=False,
        query={"instId": "BTC-USDT", "timeframe": "1H", "thold": "50", "timePeriod": "14"},
    ),
    Case(
        "get_trading_bot_grid_grid_quantity",
        "GET",
        "/api/v5/tradingBot/grid/grid-quantity",
        kwargs={
            "inst_id": "BTC-USDT",
            "run_type": "1",
            "algo_ord_type": "grid",
            "max_px": "60000",
            "min_px": "40000",
        },
        signed=False,
        query={
            "instId": "BTC-USDT",
            "runType": "1",
            "algoOrdType": "grid",
            "maxPx": "60000",
            "minPx": "40000",
        },
    ),
    Case(
        "trading_bot_grid_copy_order_algo",
        "POST",
        "/api/v5/tradingBot/grid/copy-order-algo",
        kwargs={"inst_id": "BTC-USDT", "algo_ord_type": "grid", "source_algo_id": "1"},
        signed=True,
        body={"instId": "BTC-USDT", "algoOrdType": "grid", "sourceAlgoId": "1"},
    ),
    Case(
        "trading_bot_dca_create",
        "POST",
        "/api/v5/tradingBot/dca/create",
        kwargs={
            "inst_id": "BTC-USDT",
            "algo_ord_type": "grid",
            "init_ord_amt": "1",
            "max_safety_ords": "1",
            "tp_pct": "1",
            "lever": "2",
            "trigger_params": [{"triggerAction": "1", "triggerStrategy": "1"}],
        },
        signed=True,
        body={
            "instId": "BTC-USDT",
            "algoOrdType": "grid",
            "initOrdAmt": "1",
            "maxSafetyOrds": "1",
            "tpPct": "1",
            "lever": "2",
            "triggerParams": [{"triggerAction": "1", "triggerStrategy": "1"}],
        },
    ),
    Case(
        "trading_bot_dca_amend_order_algo",
        "POST",
        "/api/v5/tradingBot/dca/amend-order-algo",
        kwargs={
            "algo_id": "1",
            "px_steps": "1",
            "px_steps_mult": "1",
            "vol_mult": "1",
            "tp_pct": "1",
            "sl_pct": "1",
            "init_ord_amt": "1",
            "safety_ord_amt": "1",
            "max_safety_ords": "1",
            "reserve_funds": True,
            "trigger_params": [{}],
        },
        signed=True,
        body={
            "algoId": "1",
            "pxSteps": "1",
            "pxStepsMult": "1",
            "volMult": "1",
            "tpPct": "1",
            "slPct": "1",
            "initOrdAmt": "1",
            "safetyOrdAmt": "1",
            "maxSafetyOrds": "1",
            "reserveFunds": True,
            "triggerParams": [{}],
        },
    ),
    Case(
        "trading_bot_dca_stop",
        "POST",
        "/api/v5/tradingBot/dca/stop",
        kwargs={"algo_id": "1", "algo_ord_type": "grid", "stop_type": "1"},
        signed=True,
        body={"algoId": "1", "algoOrdType": "grid", "stopType": "1"},
    ),
    Case(
        "get_trading_bot_dca_ongoing_list",
        "GET",
        "/api/v5/tradingBot/dca/ongoing-list",
        kwargs={"algo_ord_type": "grid"},
        signed=True,
        query={"algoOrdType": "grid"},
    ),
    Case(
        "get_trading_bot_dca_history_list",
        "GET",
        "/api/v5/tradingBot/dca/history-list",
        kwargs={"algo_ord_type": "grid"},
        signed=True,
        query={"algoOrdType": "grid"},
    ),
    Case(
        "get_trading_bot_dca_orders",
        "GET",
        "/api/v5/tradingBot/dca/orders",
        kwargs={"algo_id": "1", "algo_ord_type": "grid"},
        signed=True,
        query={"algoId": "1", "algoOrdType": "grid"},
    ),
    Case(
        "trading_bot_dca_orders_manual_buy",
        "POST",
        "/api/v5/tradingBot/dca/orders/manual-buy",
        kwargs={"algo_id": "1", "algo_ord_type": "grid", "price": "1", "amt": "100"},
        signed=True,
        body={"algoId": "1", "algoOrdType": "grid", "price": "1", "amt": "100"},
    ),
    Case(
        "trading_bot_dca_settings_reinvestment",
        "POST",
        "/api/v5/tradingBot/dca/settings/reinvestment",
        kwargs={"algo_id": "1", "algo_ord_type": "grid", "allow_reinvest": True},
        signed=True,
        body={"algoId": "1", "algoOrdType": "grid", "allowReinvest": True},
    ),
    Case(
        "trading_bot_dca_settings_take_profit",
        "POST",
        "/api/v5/tradingBot/dca/settings/take-profit",
        kwargs={"algo_id": "1", "algo_ord_type": "grid", "tp_price": "1"},
        signed=True,
        body={"algoId": "1", "algoOrdType": "grid", "tpPrice": "1"},
    ),
    Case(
        "get_trading_bot_dca_position_details",
        "GET",
        "/api/v5/tradingBot/dca/position-details",
        kwargs={"algo_id": "1", "algo_ord_type": "grid"},
        signed=True,
        query={"algoId": "1", "algoOrdType": "grid"},
    ),
    Case(
        "get_trading_bot_dca_cycle_list",
        "GET",
        "/api/v5/tradingBot/dca/cycle-list",
        kwargs={"algo_id": "1", "algo_ord_type": "grid"},
        signed=True,
        query={"algoId": "1", "algoOrdType": "grid"},
    ),
    Case(
        "trading_bot_dca_margin_add",
        "POST",
        "/api/v5/tradingBot/dca/margin/add",
        kwargs={"algo_id": "1", "amt": "100"},
        signed=True,
        body={"algoId": "1", "amt": "100"},
    ),
    Case(
        "trading_bot_dca_margin_reduce",
        "POST",
        "/api/v5/tradingBot/dca/margin/reduce",
        kwargs={"algo_id": "1", "amt": "100"},
        signed=True,
        body={"algoId": "1", "amt": "100"},
    ),
    Case(
        "trading_bot_signal_create_signal",
        "POST",
        "/api/v5/tradingBot/signal/create-signal",
        kwargs={"signal_chan_name": "1"},
        signed=True,
        body={"signalChanName": "1"},
    ),
    Case(
        "get_trading_bot_signal_signals",
        "GET",
        "/api/v5/tradingBot/signal/signals",
        kwargs={"signal_source_type": "1"},
        signed=True,
        query={"signalSourceType": "1"},
    ),
    Case(
        "trading_bot_signal_order_algo",
        "POST",
        "/api/v5/tradingBot/signal/order-algo",
        kwargs={"signal_chan_id": "1", "lever": "2", "invest_amt": "1", "sub_ord_type": "1"},
        signed=True,
        body={"signalChanId": "1", "lever": "2", "investAmt": "1", "subOrdType": "1"},
    ),
    Case(
        "trading_bot_signal_stop_order_algo",
        "POST",
        "/api/v5/tradingBot/signal/stop-order-algo",
        kwargs={"orders": [{"algoId": "1"}]},
        signed=True,
        body=[{"algoId": "1"}],
    ),
    Case(
        "trading_bot_signal_margin_balance",
        "POST",
        "/api/v5/tradingBot/signal/margin-balance",
        kwargs={"algo_id": "1", "type_": "1", "amt": "100"},
        signed=True,
        body={"algoId": "1", "type": "1", "amt": "100"},
    ),
    Case(
        "trading_bot_signal_amend_tpsl",
        "POST",
        "/api/v5/tradingBot/signal/amendTPSL",
        kwargs={"algo_id": "1", "exit_setting_param": {"tpSlType": "1"}},
        signed=True,
        body={"algoId": "1", "exitSettingParam": {"tpSlType": "1"}},
    ),
    Case(
        "trading_bot_signal_set_instruments",
        "POST",
        "/api/v5/tradingBot/signal/set-instruments",
        kwargs={"algo_id": "1", "inst_ids": ["1"], "include_all": True},
        signed=True,
        body={"algoId": "1", "instIds": ["1"], "includeAll": True},
    ),
    Case(
        "get_trading_bot_signal_orders_algo_details",
        "GET",
        "/api/v5/tradingBot/signal/orders-algo-details",
        kwargs={"algo_ord_type": "grid", "algo_id": "1"},
        signed=True,
        query={"algoOrdType": "grid", "algoId": "1"},
    ),
    Case(
        "get_trading_bot_signal_orders_algo_pending",
        "GET",
        "/api/v5/tradingBot/signal/orders-algo-pending",
        kwargs={"algo_ord_type": "grid", "after": "1"},
        signed=True,
        query={"algoOrdType": "grid", "after": "1"},
    ),
    Case(
        "get_trading_bot_signal_orders_algo_history",
        "GET",
        "/api/v5/tradingBot/signal/orders-algo-history",
        kwargs={"algo_ord_type": "grid", "algo_id": "1", "after": "1"},
        signed=True,
        query={"algoOrdType": "grid", "algoId": "1", "after": "1"},
    ),
    Case(
        "get_trading_bot_signal_positions",
        "GET",
        "/api/v5/tradingBot/signal/positions",
        kwargs={"algo_ord_type": "grid", "algo_id": "1"},
        signed=True,
        query={"algoOrdType": "grid", "algoId": "1"},
    ),
    Case(
        "get_trading_bot_signal_positions_history",
        "GET",
        "/api/v5/tradingBot/signal/positions-history",
        kwargs={"algo_id": "1"},
        signed=True,
        query={"algoId": "1"},
    ),
    Case(
        "trading_bot_signal_close_position",
        "POST",
        "/api/v5/tradingBot/signal/close-position",
        kwargs={"algo_id": "1", "inst_id": "BTC-USDT"},
        signed=True,
        body={"algoId": "1", "instId": "BTC-USDT"},
    ),
    Case(
        "trading_bot_signal_sub_order",
        "POST",
        "/api/v5/tradingBot/signal/sub-order",
        kwargs={
            "inst_id": "BTC-USDT",
            "algo_id": "1",
            "side": "buy",
            "ord_type": "market",
            "sz": "100",
        },
        signed=True,
        body={"instId": "BTC-USDT", "algoId": "1", "side": "buy", "ordType": "market", "sz": "100"},
    ),
    Case(
        "trading_bot_signal_cancel_sub_order",
        "POST",
        "/api/v5/tradingBot/signal/cancel-sub-order",
        kwargs={"algo_id": "1", "inst_id": "BTC-USDT", "signal_ord_id": "1"},
        signed=True,
        body={"algoId": "1", "instId": "BTC-USDT", "signalOrdId": "1"},
    ),
    Case(
        "get_trading_bot_signal_sub_orders",
        "GET",
        "/api/v5/tradingBot/signal/sub-orders",
        kwargs={"algo_id": "1", "algo_ord_type": "grid"},
        signed=True,
        query={"algoId": "1", "algoOrdType": "grid"},
    ),
    Case(
        "get_trading_bot_signal_event_history",
        "GET",
        "/api/v5/tradingBot/signal/event-history",
        kwargs={"algo_id": "1"},
        signed=True,
        query={"algoId": "1"},
    ),
    Case(
        "trading_bot_recurring_order_algo",
        "POST",
        "/api/v5/tradingBot/recurring/order-algo",
        kwargs={
            "stgy_name": "Strategy",
            "recurring_list": [{"ccy": "USDG", "ratio": "1"}],
            "period": "daily",
            "recurring_time": "0",
            "time_zone": "8",
            "amt": "100",
            "investment_ccy": "USDT",
            "td_mode": "cash",
        },
        signed=True,
        body={
            "stgyName": "Strategy",
            "recurringList": [{"ccy": "USDG", "ratio": "1"}],
            "period": "daily",
            "recurringTime": "0",
            "timeZone": "8",
            "amt": "100",
            "investmentCcy": "USDT",
            "tdMode": "cash",
        },
    ),
    Case(
        "trading_bot_recurring_amend_order_algo",
        "POST",
        "/api/v5/tradingBot/recurring/amend-order-algo",
        kwargs={"algo_id": "1", "stgy_name": "Strategy"},
        signed=True,
        body={"algoId": "1", "stgyName": "Strategy"},
    ),
    Case(
        "trading_bot_recurring_stop_order_algo",
        "POST",
        "/api/v5/tradingBot/recurring/stop-order-algo",
        kwargs={"orders": [{"algoId": "1"}]},
        signed=True,
        body=[{"algoId": "1"}],
    ),
    Case(
        "get_trading_bot_recurring_orders_algo_pending",
        "GET",
        "/api/v5/tradingBot/recurring/orders-algo-pending",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_trading_bot_recurring_orders_algo_history",
        "GET",
        "/api/v5/tradingBot/recurring/orders-algo-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_trading_bot_recurring_orders_algo_details",
        "GET",
        "/api/v5/tradingBot/recurring/orders-algo-details",
        kwargs={"algo_id": "1"},
        signed=True,
        query={"algoId": "1"},
    ),
    Case(
        "get_trading_bot_recurring_sub_orders",
        "GET",
        "/api/v5/tradingBot/recurring/sub-orders",
        kwargs={"algo_id": "1"},
        signed=True,
        query={"algoId": "1"},
    ),
    Case(
        "trading_bot_recurring_amend_recurring_time",
        "POST",
        "/api/v5/tradingBot/recurring/amend-recurring-time",
        kwargs={"algo_id": "1", "recurring_time_type": "1", "time_zone": "8", "period": "daily"},
        signed=True,
        body={"algoId": "1", "recurringTimeType": "1", "timeZone": "8", "period": "daily"},
    ),
    Case(
        "trading_bot_recurring_amend_recurring_amount",
        "POST",
        "/api/v5/tradingBot/recurring/amend-recurring-amount",
        kwargs={"algo_id": "1", "amount": "1"},
        signed=True,
        body={"algoId": "1", "amount": "1"},
    ),
    Case(
        "trading_bot_recurring_add_investment",
        "POST",
        "/api/v5/tradingBot/recurring/add-investment",
        kwargs={"algo_id": "1", "amount": "1"},
        signed=True,
        body={"algoId": "1", "amount": "1"},
    ),
    Case(
        "trading_bot_recurring_pause",
        "POST",
        "/api/v5/tradingBot/recurring/pause",
        kwargs={"algo_id": "1"},
        signed=True,
        body={"algoId": "1"},
    ),
    Case(
        "trading_bot_recurring_restart",
        "POST",
        "/api/v5/tradingBot/recurring/restart",
        kwargs={"algo_id": "1"},
        signed=True,
        body={"algoId": "1"},
    ),
    Case(
        "trading_bot_recurring_amend_price_range",
        "POST",
        "/api/v5/tradingBot/recurring/amend-price-range",
        kwargs={
            "algo_id": "1",
            "recurring_list": [{"ccy": "USDG", "minPx": "40000", "maxPx": "60000"}],
        },
        signed=True,
        body={
            "algoId": "1",
            "recurringList": [{"ccy": "USDG", "minPx": "40000", "maxPx": "60000"}],
        },
    ),
    Case(
        "get_copytrading_current_subpositions",
        "GET",
        "/api/v5/copytrading/current-subpositions",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_copytrading_subpositions_history",
        "GET",
        "/api/v5/copytrading/subpositions-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "copytrading_algo_order",
        "POST",
        "/api/v5/copytrading/algo-order",
        kwargs={"sub_pos_id": "1"},
        signed=True,
        body={"subPosId": "1"},
    ),
    Case(
        "copytrading_close_subposition",
        "POST",
        "/api/v5/copytrading/close-subposition",
        kwargs={"sub_pos_id": "1"},
        signed=True,
        body={"subPosId": "1"},
    ),
    Case(
        "get_copytrading_instruments",
        "GET",
        "/api/v5/copytrading/instruments",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "copytrading_set_instruments",
        "POST",
        "/api/v5/copytrading/set-instruments",
        kwargs={"inst_id": "BTC-USDT"},
        signed=True,
        body={"instId": "BTC-USDT"},
    ),
    Case(
        "get_copytrading_profit_sharing_details",
        "GET",
        "/api/v5/copytrading/profit-sharing-details",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_copytrading_total_profit_sharing",
        "GET",
        "/api/v5/copytrading/total-profit-sharing",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_copytrading_unrealized_profit_sharing_details",
        "GET",
        "/api/v5/copytrading/unrealized-profit-sharing-details",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_copytrading_total_unrealized_profit_sharing",
        "GET",
        "/api/v5/copytrading/total-unrealized-profit-sharing",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "copytrading_amend_profit_sharing_ratio",
        "POST",
        "/api/v5/copytrading/amend-profit-sharing-ratio",
        kwargs={"profit_sharing_ratio": "1"},
        signed=True,
        body={"profitSharingRatio": "1"},
    ),
    Case(
        "get_copytrading_config",
        "GET",
        "/api/v5/copytrading/config",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "copytrading_first_copy_settings",
        "POST",
        "/api/v5/copytrading/first-copy-settings",
        kwargs={
            "unique_code": "1",
            "copy_mgn_mode": "1",
            "copy_inst_id_type": "1",
            "copy_total_amt": "1",
            "sub_pos_close_type": "1",
        },
        signed=True,
        body={
            "uniqueCode": "1",
            "copyMgnMode": "1",
            "copyInstIdType": "1",
            "copyTotalAmt": "1",
            "subPosCloseType": "1",
        },
    ),
    Case(
        "copytrading_amend_copy_settings",
        "POST",
        "/api/v5/copytrading/amend-copy-settings",
        kwargs={
            "unique_code": "1",
            "copy_mgn_mode": "1",
            "copy_inst_id_type": "1",
            "copy_total_amt": "1",
            "sub_pos_close_type": "1",
        },
        signed=True,
        body={
            "uniqueCode": "1",
            "copyMgnMode": "1",
            "copyInstIdType": "1",
            "copyTotalAmt": "1",
            "subPosCloseType": "1",
        },
    ),
    Case(
        "copytrading_stop_copy_trading",
        "POST",
        "/api/v5/copytrading/stop-copy-trading",
        kwargs={"unique_code": "1", "sub_pos_close_type": "1"},
        signed=True,
        body={"uniqueCode": "1", "subPosCloseType": "1"},
    ),
    Case(
        "get_copytrading_copy_settings",
        "GET",
        "/api/v5/copytrading/copy-settings",
        kwargs={"unique_code": "1"},
        signed=True,
        query={"uniqueCode": "1"},
    ),
    Case(
        "get_copytrading_current_lead_traders",
        "GET",
        "/api/v5/copytrading/current-lead-traders",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_copytrading_public_config",
        "GET",
        "/api/v5/copytrading/public-config",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_copytrading_public_lead_traders",
        "GET",
        "/api/v5/copytrading/public-lead-traders",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_copytrading_public_weekly_pnl",
        "GET",
        "/api/v5/copytrading/public-weekly-pnl",
        kwargs={"unique_code": "1"},
        signed=False,
        query={"uniqueCode": "1"},
    ),
    Case(
        "get_copytrading_public_pnl",
        "GET",
        "/api/v5/copytrading/public-pnl",
        kwargs={"unique_code": "1", "last_days": "1"},
        signed=False,
        query={"uniqueCode": "1", "lastDays": "1"},
    ),
    Case(
        "get_copytrading_public_stats",
        "GET",
        "/api/v5/copytrading/public-stats",
        kwargs={"unique_code": "1", "last_days": "1"},
        signed=False,
        query={"uniqueCode": "1", "lastDays": "1"},
    ),
    Case(
        "get_copytrading_public_preference_currency",
        "GET",
        "/api/v5/copytrading/public-preference-currency",
        kwargs={"unique_code": "1"},
        signed=False,
        query={"uniqueCode": "1"},
    ),
    Case(
        "get_copytrading_public_current_subpositions",
        "GET",
        "/api/v5/copytrading/public-current-subpositions",
        kwargs={"unique_code": "1"},
        signed=False,
        query={"uniqueCode": "1"},
    ),
    Case(
        "get_copytrading_public_subpositions_history",
        "GET",
        "/api/v5/copytrading/public-subpositions-history",
        kwargs={"unique_code": "1"},
        signed=False,
        query={"uniqueCode": "1"},
    ),
    Case(
        "get_copytrading_public_copy_traders",
        "GET",
        "/api/v5/copytrading/public-copy-traders",
        kwargs={"unique_code": "1"},
        signed=False,
        query={"uniqueCode": "1"},
    ),
    Case(
        "get_public_event_contract_series",
        "GET",
        "/api/v5/public/event-contract/series",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_public_event_contract_events",
        "GET",
        "/api/v5/public/event-contract/events",
        kwargs={"series_id": "1"},
        signed=False,
        query={"seriesId": "1"},
    ),
    Case(
        "get_public_event_contract_markets",
        "GET",
        "/api/v5/public/event-contract/markets",
        kwargs={"series_id": "1"},
        signed=False,
        query={"seriesId": "1"},
    ),
    Case(
        "get_public_interest_rate_loan_quota",
        "GET",
        "/api/v5/public/interest-rate-loan-quota",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_asset_withdrawal_history",
        "GET",
        "/api/v5/asset/withdrawal-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_fiat_deposit_payment_methods",
        "GET",
        "/api/v5/fiat/deposit-payment-methods",
        kwargs={"ccy": "USDG"},
        signed=True,
        query={"ccy": "USDG"},
    ),
    Case(
        "get_fiat_withdrawal_payment_methods",
        "GET",
        "/api/v5/fiat/withdrawal-payment-methods",
        kwargs={"ccy": "USDG"},
        signed=True,
        query={"ccy": "USDG"},
    ),
    Case(
        "get_fiat_withdrawal_order_history",
        "GET",
        "/api/v5/fiat/withdrawal-order-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_fiat_withdrawal",
        "GET",
        "/api/v5/fiat/withdrawal",
        kwargs={"ord_id": "1"},
        signed=True,
        query={"ordId": "1"},
    ),
    Case(
        "get_fiat_deposit_order_history",
        "GET",
        "/api/v5/fiat/deposit-order-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_fiat_deposit",
        "GET",
        "/api/v5/fiat/deposit",
        kwargs={"ord_id": "1"},
        signed=True,
        query={"ordId": "1"},
    ),
    Case(
        "get_fiat_buy_sell_currencies",
        "GET",
        "/api/v5/fiat/buy-sell/currencies",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_fiat_buy_sell_currency_pair",
        "GET",
        "/api/v5/fiat/buy-sell/currency-pair",
        kwargs={"from_ccy": "1", "to_ccy": "1"},
        signed=True,
        query={"fromCcy": "1", "toCcy": "1"},
    ),
    Case(
        "fiat_buy_sell_quote",
        "POST",
        "/api/v5/fiat/buy-sell/quote",
        kwargs={"side": "buy", "from_ccy": "1", "to_ccy": "1", "rfq_amt": "1", "rfq_ccy": "1"},
        signed=True,
        body={"side": "buy", "fromCcy": "1", "toCcy": "1", "rfqAmt": "1", "rfqCcy": "1"},
    ),
    Case(
        "fiat_buy_sell_trade",
        "POST",
        "/api/v5/fiat/buy-sell/trade",
        kwargs={
            "quote_id": "1",
            "side": "buy",
            "from_ccy": "1",
            "to_ccy": "1",
            "rfq_amt": "1",
            "rfq_ccy": "1",
            "payment_method": "1",
            "cl_ord_id": "1",
        },
        signed=True,
        body={
            "quoteId": "1",
            "side": "buy",
            "fromCcy": "1",
            "toCcy": "1",
            "rfqAmt": "1",
            "rfqCcy": "1",
            "paymentMethod": "1",
            "clOrdId": "1",
        },
    ),
    Case(
        "get_fiat_buy_sell_history",
        "GET",
        "/api/v5/fiat/buy-sell/history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_account_subaccount_max_withdrawal",
        "GET",
        "/api/v5/account/subaccount/max-withdrawal",
        kwargs={"sub_acct": "subaccount"},
        signed=True,
        query={"subAcct": "subaccount"},
    ),
    Case(
        "get_asset_subaccount_managed_subaccount_bills",
        "GET",
        "/api/v5/asset/subaccount/managed-subaccount-bills",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_finance_stable_rewards_product_info",
        "GET",
        "/api/v5/finance/stable-rewards/product-info",
        kwargs={"ccy": "USDG"},
        signed=True,
        query={"ccy": "USDG"},
    ),
    Case(
        "get_finance_stable_rewards_balance",
        "GET",
        "/api/v5/finance/stable-rewards/balance",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_finance_stable_rewards_apy_history",
        "GET",
        "/api/v5/finance/stable-rewards/apy-history",
        kwargs={"ccy": "USDG"},
        signed=True,
        query={"ccy": "USDG"},
    ),
    Case("get_bill_types", "GET", "/api/v5/account/subtypes", kwargs={}, signed=True, query={}),
    Case(
        "simulate_positions",
        "POST",
        "/api/v5/account/position-builder",
        kwargs={},
        signed=True,
        body={},
    ),
    Case(
        "get_position_margin_graph",
        "POST",
        "/api/v5/account/position-builder-graph",
        kwargs={"type_": "mmr", "mmr_config": {"acctLv": "4"}},
        signed=True,
        body={"type": "mmr", "mmrConfig": {"acctLv": "4"}},
    ),
    Case(
        "move_positions",
        "POST",
        "/api/v5/account/move-positions",
        kwargs={
            "from_acct": "0",
            "to_acct": "subacct1",
            "legs": [{"from": {"posId": "1", "sz": "1", "side": "buy"}, "to": {}}],
            "client_id": "move1",
        },
        signed=True,
        body={
            "fromAcct": "0",
            "toAcct": "subacct1",
            "legs": [{"from": {"posId": "1", "sz": "1", "side": "buy"}, "to": {}}],
            "clientId": "move1",
        },
    ),
    Case(
        "get_move_positions_history",
        "GET",
        "/api/v5/account/move-positions-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "adjust_demo_balance",
        "POST",
        "/api/v5/account/demo-adjust-balance",
        kwargs={"type_": "increase", "adjustments": [{"ccy": "BTC", "amt": "0.1"}]},
        signed=True,
        body={"type": "increase", "adjustments": [{"ccy": "BTC", "amt": "0.1"}]},
    ),
    Case(
        "get_books_rpi",
        "GET",
        "/api/v5/market/books-rpi",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_platform_24_volume",
        "GET",
        "/api/v5/market/platform-24-volume",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_call_auction_details",
        "GET",
        "/api/v5/market/call-auction-details",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "rfq_create_rfq",
        "POST",
        "/api/v5/rfq/create-rfq",
        kwargs={
            "counterparties": ["maker1"],
            "legs": [{"instId": "BTC-USDT-SWAP", "sz": "1", "side": "buy"}],
        },
        signed=True,
        body={
            "counterparties": ["maker1"],
            "legs": [{"instId": "BTC-USDT-SWAP", "sz": "1", "side": "buy"}],
        },
    ),
    Case(
        "get_rfq_counterparties",
        "GET",
        "/api/v5/rfq/counterparties",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "rfq_cancel_rfq",
        "POST",
        "/api/v5/rfq/cancel-rfq",
        kwargs={"rfq_id": "1"},
        signed=True,
        body={"rfqId": "1"},
    ),
    Case(
        "rfq_cancel_batch_rfqs",
        "POST",
        "/api/v5/rfq/cancel-batch-rfqs",
        kwargs={"rfq_ids": ["1"]},
        signed=True,
        body={"rfqIds": ["1"]},
    ),
    Case(
        "rfq_cancel_all_rfqs",
        "POST",
        "/api/v5/rfq/cancel-all-rfqs",
        kwargs={},
        signed=True,
        body={},
    ),
    Case(
        "rfq_execute_quote",
        "POST",
        "/api/v5/rfq/execute-quote",
        kwargs={"rfq_id": "1", "quote_id": "1"},
        signed=True,
        body={"rfqId": "1", "quoteId": "1"},
    ),
    Case("get_rfq_rfqs", "GET", "/api/v5/rfq/rfqs", kwargs={}, signed=True, query={}),
    Case("get_rfq_quotes", "GET", "/api/v5/rfq/quotes", kwargs={}, signed=True, query={}),
    Case("get_rfq_trades", "GET", "/api/v5/rfq/trades", kwargs={}, signed=True, query={}),
    Case(
        "get_block_tickers",
        "GET",
        "/api/v5/market/block-tickers",
        kwargs={"inst_type": "SWAP"},
        signed=False,
        query={"instType": "SWAP"},
    ),
    Case(
        "get_block_ticker",
        "GET",
        "/api/v5/market/block-ticker",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_rfq_public_trades",
        "GET",
        "/api/v5/rfq/public-trades",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_block_trades",
        "GET",
        "/api/v5/public/block-trades",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_estimated_settlement_info",
        "GET",
        "/api/v5/public/estimated-settlement-info",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_settlement_history",
        "GET",
        "/api/v5/public/settlement-history",
        kwargs={"inst_family": "BTC-USDT"},
        signed=False,
        query={"instFamily": "BTC-USDT"},
    ),
    Case(
        "get_insurance_fund",
        "GET",
        "/api/v5/public/insurance-fund",
        kwargs={"inst_type": "SWAP", "inst_family": "BTC-USDT"},
        signed=False,
        query={"instType": "SWAP", "instFamily": "BTC-USDT"},
    ),
    Case(
        "get_premium_history",
        "GET",
        "/api/v5/public/premium-history",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_index_candles",
        "GET",
        "/api/v5/market/index-candles",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_history_index_candles",
        "GET",
        "/api/v5/market/history-index-candles",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_history_mark_price_candles",
        "GET",
        "/api/v5/market/history-mark-price-candles",
        kwargs={"inst_id": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_exchange_rate",
        "GET",
        "/api/v5/market/exchange-rate",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_index_components",
        "GET",
        "/api/v5/market/index-components",
        kwargs={"index": "BTC-USDT"},
        signed=False,
        query={"index": "BTC-USDT"},
    ),
    Case(
        "get_economic_calendar",
        "GET",
        "/api/v5/public/economic-calendar",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_market_data_history",
        "GET",
        "/api/v5/public/market-data-history",
        kwargs={
            "module": "1",
            "inst_type": "SWAP",
            "date_aggr_type": "daily",
            "begin": "1700000000000",
            "end": "1700000001000",
            "inst_family_list": "BTC-USDT",
        },
        signed=False,
        query={
            "module": "1",
            "instType": "SWAP",
            "dateAggrType": "daily",
            "begin": "1700000000000",
            "end": "1700000001000",
            "instFamilyList": "BTC-USDT",
        },
    ),
    Case(
        "get_delta_hedge_currencies",
        "GET",
        "/api/v5/public/delta-hedge-currencies",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_loan_ratio",
        "GET",
        "/api/v5/rubik/stat/margin/loan-ratio",
        kwargs={"ccy": "BTC"},
        signed=False,
        query={"ccy": "BTC"},
    ),
    Case(
        "get_non_tradable_assets",
        "GET",
        "/api/v5/asset/non-tradable-assets",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "create_sub_account",
        "POST",
        "/api/v5/users/subaccount/create-subaccount",
        kwargs={"sub_acct": "subacct1", "type_": "1"},
        signed=True,
        body={"subAcct": "subacct1", "type": "1"},
    ),
    Case(
        "create_sub_account_api_key",
        "POST",
        "/api/v5/users/subaccount/apikey",
        kwargs={"sub_acct": "subacct1", "label": "trading", "passphrase": "Trader123!"},
        signed=True,
        body={"subAcct": "subacct1", "label": "trading", "passphrase": "Trader123!"},
    ),
    Case(
        "get_sub_account_api_keys",
        "GET",
        "/api/v5/users/subaccount/apikey",
        kwargs={"sub_acct": "subacct1"},
        signed=True,
        query={"subAcct": "subacct1"},
    ),
    Case(
        "modify_sub_account_api_key",
        "POST",
        "/api/v5/users/subaccount/modify-apikey",
        kwargs={"sub_acct": "subacct1", "api_key": "api-key"},
        signed=True,
        body={"subAcct": "subacct1", "apiKey": "api-key"},
    ),
    Case(
        "delete_sub_account_api_key",
        "POST",
        "/api/v5/users/subaccount/delete-apikey",
        kwargs={"sub_acct": "subacct1", "api_key": "api-key"},
        signed=True,
        body={"subAcct": "subacct1", "apiKey": "api-key"},
    ),
    Case(
        "set_sub_account_transfer_out",
        "POST",
        "/api/v5/users/subaccount/set-transfer-out",
        kwargs={"sub_acct": "subacct1"},
        signed=True,
        body={"subAcct": "subacct1"},
    ),
    Case(
        "get_announcements",
        "GET",
        "/api/v5/support/announcements",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "get_announcement_types",
        "GET",
        "/api/v5/support/announcement-types",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "set_fee_type",
        "POST",
        "/api/v5/account/set-fee-type",
        kwargs={"fee_type": "1"},
        signed=True,
        body={"feeType": "1"},
    ),
    Case(
        "set_risk_offset_amount",
        "POST",
        "/api/v5/account/set-riskOffset-amt",
        kwargs={"ccy": "BTC", "cl_spot_in_use_amt": "0"},
        signed=True,
        body={"ccy": "BTC", "clSpotInUseAmt": "0"},
    ),
    Case(
        "activate_options",
        "POST",
        "/api/v5/account/activate-option",
        kwargs={},
        signed=True,
        body={},
    ),
    Case(
        "set_auto_loan",
        "POST",
        "/api/v5/account/set-auto-loan",
        kwargs={"auto_loan": False},
        signed=True,
        body={"autoLoan": False},
    ),
    Case(
        "preset_account_level_switch",
        "POST",
        "/api/v5/account/account-level-switch-preset",
        kwargs={"acct_lv": "2", "lever": "5"},
        signed=True,
        body={"acctLv": "2", "lever": "5"},
    ),
    Case(
        "precheck_account_level_switch",
        "GET",
        "/api/v5/account/set-account-switch-precheck",
        kwargs={"acct_lv": "3"},
        signed=True,
        query={"acctLv": "3"},
    ),
    Case(
        "set_collateral_assets",
        "POST",
        "/api/v5/account/set-collateral-assets",
        kwargs={"type_": "custom", "collateral_enabled": True, "ccy_list": ["BTC", "ETH"]},
        signed=True,
        body={"type": "custom", "collateralEnabled": True, "ccyList": ["BTC", "ETH"]},
    ),
    Case(
        "set_settlement_currency",
        "POST",
        "/api/v5/account/set-settle-currency",
        kwargs={"settle_ccy": "USDC"},
        signed=True,
        body={"settleCcy": "USDC"},
    ),
    Case(
        "set_trading_config",
        "POST",
        "/api/v5/account/set-trading-config",
        kwargs={"type_": "stgyType", "stgy_type": "1"},
        signed=True,
        body={"type": "stgyType", "stgyType": "1"},
    ),
    Case(
        "precheck_delta_neutral",
        "GET",
        "/api/v5/account/precheck-set-delta-neutral",
        kwargs={"stgy_type": "1"},
        signed=True,
        query={"stgyType": "1"},
    ),
    Case(
        "get_repayment_currencies",
        "GET",
        "/api/v5/trade/one-click-repay-currency-list-v2",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "repay_debt",
        "POST",
        "/api/v5/trade/one-click-repay-v2",
        kwargs={"debt_ccy": "USDT", "repay_ccy_list": ["USDC", "BTC"]},
        signed=True,
        body={"debtCcy": "USDT", "repayCcyList": ["USDC", "BTC"]},
    ),
    Case(
        "get_repayment_history",
        "GET",
        "/api/v5/trade/one-click-repay-history-v2",
        kwargs={"limit": "100"},
        signed=True,
        query={"limit": "100"},
    ),
    Case(
        "get_spread_order_history_archive",
        "GET",
        "/api/v5/sprd/orders-history-archive",
        kwargs={"inst_type": "SWAP", "limit": "100"},
        signed=True,
        query={"instType": "SWAP", "limit": "100"},
    ),
    Case("get_server_time", "GET", "/api/v5/public/time", kwargs={}, signed=False, query={}),
    Case(
        "set_isolated_mode",
        "POST",
        "/api/v5/account/set-isolated-mode",
        kwargs={"iso_mode": "automatic", "type_": "MARGIN"},
        signed=True,
        body={"isoMode": "automatic", "type": "MARGIN"},
    ),
    Case(
        "get_account_risk_state",
        "GET",
        "/api/v5/account/risk-state",
        kwargs={},
        signed=True,
        query={},
    ),
    Case("get_greeks", "GET", "/api/v5/account/greeks", kwargs={}, signed=True, query={}),
    Case(
        "get_pm_position_tiers",
        "GET",
        "/api/v5/account/position-tiers",
        kwargs={"inst_type": "SWAP", "inst_family": "BTC-USDT"},
        signed=True,
        query={"instType": "SWAP", "instFamily": "BTC-USDT"},
    ),
    Case(
        "set_account_level",
        "POST",
        "/api/v5/account/set-account-level",
        kwargs={"acct_lv": "3"},
        signed=True,
        body={"acctLv": "3"},
    ),
    Case(
        "get_collateral_assets",
        "GET",
        "/api/v5/account/collateral-assets",
        kwargs={"ccy": "BTC,ETH", "collateral_enabled": False},
        signed=True,
        query={"ccy": "BTC,ETH", "collateralEnabled": "false"},
    ),
    Case(
        "get_ticker",
        "GET",
        "/api/v5/market/ticker",
        kwargs={"product_symbol": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_full_orderbook",
        "GET",
        "/api/v5/market/books-full",
        kwargs={"product_symbol": "BTC-USDT-SWAP", "sz": "5000"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP", "sz": "5000"},
    ),
    Case(
        "get_candles_history",
        "GET",
        "/api/v5/market/history-candles",
        kwargs={"product_symbol": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_trades_history",
        "GET",
        "/api/v5/market/history-trades",
        kwargs={"product_symbol": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "amend_spread_order",
        "POST",
        "/api/v5/sprd/amend-order",
        kwargs={"ord_id": "1", "new_px": "-0.5"},
        signed=True,
        body={"ordId": "1", "newPx": "-0.5"},
    ),
    Case(
        "get_estimated_delivery_price",
        "GET",
        "/api/v5/public/estimated-price",
        kwargs={"product_symbol": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_discount_rates",
        "GET",
        "/api/v5/public/discount-rate-interest-free-quota",
        kwargs={},
        signed=False,
        query={},
    ),
    Case(
        "convert_contract_coin",
        "GET",
        "/api/v5/public/convert-contract-coin",
        kwargs={"product_symbol": "BTC-USDT-SWAP", "sz": "1"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP", "sz": "1"},
    ),
    Case(
        "get_index_tickers",
        "GET",
        "/api/v5/market/index-tickers",
        kwargs={"quote_ccy": "USDT"},
        signed=False,
        query={"quoteCcy": "USDT"},
    ),
    Case(
        "get_mark_price_candles",
        "GET",
        "/api/v5/market/mark-price-candles",
        kwargs={"product_symbol": "BTC-USDT-SWAP"},
        signed=False,
        query={"instId": "BTC-USDT-SWAP"},
    ),
    Case(
        "get_asset_bill_history",
        "GET",
        "/api/v5/asset/bills-history",
        kwargs={},
        signed=True,
        query={},
    ),
    Case(
        "get_convert_currency_pair",
        "GET",
        "/api/v5/asset/convert/currency-pair",
        kwargs={"from_ccy": "USDT", "to_ccy": "BTC"},
        signed=True,
        query={"fromCcy": "USDT", "toCcy": "BTC"},
    ),
    Case(
        "estimate_convert_quote",
        "POST",
        "/api/v5/asset/convert/estimate-quote",
        kwargs={
            "base_ccy": "BTC",
            "quote_ccy": "USDT",
            "side": "buy",
            "rfq_sz": "1",
            "rfq_sz_ccy": "BTC",
        },
        signed=True,
        body={"baseCcy": "BTC", "quoteCcy": "USDT", "side": "buy", "rfqSz": "1", "rfqSzCcy": "BTC"},
    ),
    Case(
        "execute_convert_trade",
        "POST",
        "/api/v5/asset/convert/trade",
        kwargs={
            "quote_id": "quote1",
            "base_ccy": "BTC",
            "quote_ccy": "USDT",
            "side": "buy",
            "sz": "1",
            "sz_ccy": "BTC",
        },
        signed=True,
        body={
            "quoteId": "quote1",
            "baseCcy": "BTC",
            "quoteCcy": "USDT",
            "side": "buy",
            "sz": "1",
            "szCcy": "BTC",
        },
    ),
    Case("get_system_status", "GET", "/api/v5/system/status", kwargs={}, signed=False, query={}),
    pub("get_price_limit", "/api/v5/public/price-limit", SWAP, query={"instId": SWAP}),
    pub("get_mark_price", "/api/v5/public/mark-price", "SWAP", query={"instType": "SWAP"}),
    post(
        "place_algo_order",
        "/api/v5/trade/order-algo",
        SWAP,
        "cross",
        "sell",
        "conditional",
        sz="1",
        sl_trigger_px="50000",
        sl_ord_px="-1",
        reduce_only=True,
        body={
            "instId": SWAP,
            "tdMode": "cross",
            "side": "sell",
            "ordType": "conditional",
            "sz": "1",
            "slTriggerPx": "50000",
            "slOrdPx": "-1",
            "reduceOnly": True,
        },
    ),
    post(
        "amend_algo_order",
        "/api/v5/trade/amend-algos",
        SWAP,
        algo_id="42",
        new_sl_trigger_px="49000",
        cancel_on_fail=True,
        body={"instId": SWAP, "algoId": "42", "newSlTriggerPx": "49000", "cxlOnFail": True},
    ),
    post("cancel_algo_orders", "/api/v5/trade/cancel-algos", [{"instId": SWAP, "algoId": "42"}]),
    get("get_algo_order", "/api/v5/trade/order-algo", algo_id="42", query={"algoId": "42"}),
    get(
        "get_pending_algo_orders",
        "/api/v5/trade/orders-algo-pending",
        "conditional,oco",
        query={"ordType": "conditional,oco"},
    ),
    get(
        "get_algo_order_history",
        "/api/v5/trade/orders-algo-history",
        "trigger",
        state="effective",
        query={"ordType": "trigger", "state": "effective"},
    ),
    post(
        "adjust_position_margin",
        "/api/v5/account/position/margin-balance",
        SWAP,
        "net",
        "add",
        "1",
        body={"instId": SWAP, "posSide": "net", "type": "add", "amt": "1"},
    ),
    # Market data.
    pub(
        "get_candles_ticks",
        "/api/v5/market/candles",
        SWAP,
        bar="1m",
        query={"instId": SWAP, "bar": "1m"},
    ),
    pub("get_orderbook", "/api/v5/market/books", SWAP, sz="5", query={"instId": SWAP, "sz": "5"}),
    pub("get_tickers", "/api/v5/market/tickers", "SWAP", query={"instType": "SWAP"}),
    pub(
        "get_public_trades", "/api/v5/market/trades", "BTC-USDT-SPOT", query={"instId": "BTC-USDT"}
    ),
    pub("get_option_family_trades", "/api/v5/market/option/instrument-family-trades", "BTC-USD"),
    # Public data.
    pub("get_public_instruments", "/api/v5/public/instruments", "SPOT", query={"instType": "SPOT"}),
    pub("get_public_underlying", "/api/v5/public/underlying", "SWAP"),
    pub("get_funding_rate", "/api/v5/public/funding-rate", SWAP, query={"instId": SWAP}),
    pub("get_funding_rate_history", "/api/v5/public/funding-rate-history", SWAP, limit=5),
    pub("get_open_interest", "/api/v5/public/open-interest", "SWAP"),
    pub(
        "get_position_tiers",
        "/api/v5/public/position-tiers",
        "SWAP",
        "cross",
        product_symbol=SWAP,
        query={"instType": "SWAP", "tdMode": "cross", "instFamily": "BTC-USDT"},
    ),
    pub("get_trading_data_support_coin", "/api/v5/rubik/stat/trading-data/support-coin"),
    pub("get_taker_volume", "/api/v5/rubik/stat/taker-volume", "BTC", "SPOT"),
    pub("get_contract_taker_volume", "/api/v5/rubik/stat/taker-volume-contract", SWAP),
    pub("get_long_short_ratio", "/api/v5/rubik/stat/contracts/long-short-account-ratio", "BTC"),
    pub(
        "get_contract_long_short_ratio",
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract",
        SWAP,
    ),
    pub(
        "get_top_trader_long_short_account_ratio",
        "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader",
        SWAP,
    ),
    pub(
        "get_top_trader_long_short_position_ratio",
        "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader",
        SWAP,
    ),
    pub(
        "get_contracts_open_interest_and_volume",
        "/api/v5/rubik/stat/contracts/open-interest-volume",
        "BTC",
    ),
    pub(
        "get_contract_open_interest_history",
        "/api/v5/rubik/stat/contracts/open-interest-history",
        SWAP,
    ),
    pub(
        "get_delivery_exercise_history",
        "/api/v5/public/delivery-exercise-history",
        "OPTION",
        instFamily="BTC-USD",
    ),
    pub("get_option_summary", "/api/v5/public/opt-summary", instFamily="BTC-USD"),
    pub("get_option_tick_bands", "/api/v5/public/instrument-tick-bands", "OPTION"),
    pub("get_option_trades", "/api/v5/public/option-trades", instFamily="BTC-USD"),
    pub(
        "get_options_open_interest_and_volume",
        "/api/v5/rubik/stat/option/open-interest-volume",
        "BTC",
    ),
    pub("get_option_put_call_ratio", "/api/v5/rubik/stat/option/open-interest-volume-ratio", "BTC"),
    pub(
        "get_option_open_interest_and_volume_by_expiry",
        "/api/v5/rubik/stat/option/open-interest-volume-expiry",
        "BTC",
    ),
    pub(
        "get_option_open_interest_and_volume_by_strike",
        "/api/v5/rubik/stat/option/open-interest-volume-strike",
        "BTC",
        "20261225",
    ),
    pub("get_option_taker_block_volume", "/api/v5/rubik/stat/option/taker-block-volume", "BTC"),
    # Spread public data.
    pub("get_spread_spreads", "/api/v5/sprd/spreads", base_ccy="BTC", query={"baseCcy": "BTC"}),
    pub(
        "get_spread_books", "/api/v5/sprd/books", SPRD, depth="5", query={"sprdId": SPRD, "sz": "5"}
    ),
    pub("get_spread_ticker", "/api/v5/market/sprd-ticker", SPRD),
    pub("get_spread_candles", "/api/v5/market/sprd-candles", SPRD, bar="1m"),
    pub("get_spread_history_candles", "/api/v5/market/sprd-history-candles", SPRD, bar="1m"),
    pub("get_spread_public_trades", "/api/v5/sprd/public-trades", SPRD),
    # Trade.
    post(
        "place_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "buy",
        "limit",
        "1",
        px="100",
        clOrdId="c1",
        reduceOnly=True,
        body={"instId": SWAP, "side": "buy", "ordType": "limit", "px": "100", "reduceOnly": True},
    ),
    post(
        "place_batch_orders",
        "/api/v5/trade/batch-orders",
        [
            {
                "instId": SWAP,
                "tdMode": "cross",
                "side": "buy",
                "ordType": "limit",
                "sz": "1",
                "px": "1",
            }
        ],
    ),
    post(
        "place_market_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "sell",
        "1",
        body={"ordType": "market"},
    ),
    post(
        "place_market_buy_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        body={"ordType": "market", "side": "buy"},
    ),
    post(
        "place_market_sell_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        body={"ordType": "market", "side": "sell"},
    ),
    post(
        "place_limit_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "buy",
        "1",
        "10",
        body={"ordType": "limit"},
    ),
    post(
        "place_limit_buy_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "limit", "side": "buy"},
    ),
    post(
        "place_limit_sell_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "limit", "side": "sell"},
    ),
    post(
        "place_post_only_limit_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "buy",
        "1",
        "10",
        body={"ordType": "post_only"},
    ),
    post(
        "place_post_only_limit_buy_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "post_only", "side": "buy"},
    ),
    post(
        "place_post_only_limit_sell_order",
        "/api/v5/trade/order",
        SWAP,
        "cross",
        "1",
        "10",
        body={"ordType": "post_only", "side": "sell"},
    ),
    post(
        "pre_check_order",
        "/api/v5/trade/order-precheck",
        SWAP,
        "cross",
        "buy",
        "limit",
        "1",
        body={"instId": SWAP},
    ),
    post(
        "cancel_order",
        "/api/v5/trade/cancel-order",
        SWAP,
        ordId="1",
        body={"instId": SWAP, "ordId": "1"},
    ),
    post(
        "cancel_batch_orders", "/api/v5/trade/cancel-batch-orders", [{"instId": SWAP, "ordId": "1"}]
    ),
    # With no pending orders the native helper only lists and returns.
    get(
        "cancel_all_orders",
        "/api/v5/trade/orders-pending",
        SWAP,
        query={"instId": SWAP, "limit": "100"},
    ),
    post(
        "amend_order",
        "/api/v5/trade/amend-order",
        SWAP,
        ordId="1",
        newPx="11",
        body={"instId": SWAP, "ordId": "1", "newPx": "11"},
    ),
    post(
        "amend_multiple_orders",
        "/api/v5/trade/amend-batch-orders",
        [{"instId": SWAP, "ordId": "1", "newSz": "2"}],
    ),
    post(
        "close_positions",
        "/api/v5/trade/close-position",
        SWAP,
        "cross",
        autoCxl=True,
        body={"instId": SWAP, "mgnMode": "cross", "autoCxl": True},
    ),
    get("get_order", "/api/v5/trade/order", SWAP, ordId="1", query={"instId": SWAP, "ordId": "1"}),
    get("get_order_list", "/api/v5/trade/orders-pending", "SWAP", query={"instType": "SWAP"}),
    get("get_orders_history", "/api/v5/trade/orders-history", "SWAP", query={"instType": "SWAP"}),
    get("get_orders_history_archive", "/api/v5/trade/orders-history-archive", "SWAP"),
    get("get_fills", "/api/v5/trade/fills", "SWAP"),
    get("get_fills_history", "/api/v5/trade/fills-history", "SWAP"),
    get("get_account_rate_limit", "/api/v5/trade/account-rate-limit"),
    post("set_cancel_all_after", "/api/v5/trade/cancel-all-after", "30", body={"timeOut": "30"}),
    get("get_easy_convert_currencies", "/api/v5/trade/easy-convert-currency-list"),
    get("get_easy_convert_history", "/api/v5/trade/easy-convert-history"),
    post(
        "place_easy_convert",
        "/api/v5/trade/easy-convert",
        ["ADA"],
        "USDT",
        body={"fromCcy": ["ADA"], "toCcy": "USDT"},
    ),
    # Spread trading.
    post(
        "place_spread_order",
        "/api/v5/sprd/order",
        SPRD,
        "buy",
        "limit",
        "1",
        price="2",
        body={"sprdId": SPRD, "px": "2", "sz": "1"},
    ),
    post("cancel_spread_order", "/api/v5/sprd/cancel-order", order_id="1", body={"ordId": "1"}),
    post("cancel_all_spread_orders", "/api/v5/sprd/mass-cancel", SPRD),
    get("get_spread_order", "/api/v5/sprd/order", order_id="1", query={"ordId": "1"}),
    get("get_spread_orders_pending", "/api/v5/sprd/orders-pending"),
    get("get_spread_orders_history", "/api/v5/sprd/orders-history"),
    post(
        "set_spread_cancel_all_after", "/api/v5/sprd/cancel-all-after", "10", body={"timeOut": "10"}
    ),
    get("get_spread_trades", "/api/v5/sprd/trades"),
    # Trading account.
    get("get_account_instruments", "/api/v5/account/instruments", "SWAP"),
    get("get_account_balance", "/api/v5/account/balance", "BTC", query={"ccy": "BTC"}),
    get("get_positions", "/api/v5/account/positions", "SWAP"),
    get("get_positions_history", "/api/v5/account/positions-history", "SWAP"),
    get("get_position_risk", "/api/v5/account/account-position-risk", "SWAP"),
    get("get_account_bills", "/api/v5/account/bills", "SWAP"),
    get("get_account_bills_archive", "/api/v5/account/bills-archive", "SWAP"),
    get("get_account_bills_history_archive", "/api/v5/account/bills-history-archive", "2026", "Q1"),
    post(
        "post_account_bills_history_archive", "/api/v5/account/bills-history-archive", "2026", "Q1"
    ),
    get("get_account_config", "/api/v5/account/config"),
    post(
        "set_position_mode",
        "/api/v5/account/set-position-mode",
        "long_short_mode",
        body={"posMode": "long_short_mode"},
    ),
    post(
        "set_leverage",
        "/api/v5/account/set-leverage",
        "5",
        "cross",
        product_symbol=SWAP,
        body={"lever": "5", "mgnMode": "cross", "instId": SWAP},
    ),
    get(
        "get_max_order_size",
        "/api/v5/account/max-size",
        SWAP,
        "cross",
        query={"instId": SWAP, "tdMode": "cross"},
    ),
    get("get_max_avail_size", "/api/v5/account/max-avail-size", SWAP, "cross"),
    get("get_leverage", "/api/v5/account/leverage-info", "cross", product_symbol=SWAP),
    get("get_adjust_leverage", "/api/v5/account/adjust-leverage-info", "SWAP", "cross", "3"),
    get("get_max_loan", "/api/v5/account/max-loan", "cross", product_symbol="BTC-USDT-SPOT"),
    get("get_spot_fee_rates", "/api/v5/account/trade-fee", query={"instType": "SPOT"}),
    get("get_margin_fee_rates", "/api/v5/account/trade-fee", query={"instType": "MARGIN"}),
    get("get_swap_fee_rates", "/api/v5/account/trade-fee", query={"instType": "SWAP"}),
    get("get_futures_fee_rates", "/api/v5/account/trade-fee", query={"instType": "FUTURES"}),
    get("get_option_fee_rates", "/api/v5/account/trade-fee", query={"instType": "OPTION"}),
    get("get_interest_accrued", "/api/v5/account/interest-accrued"),
    get("get_interest_rate", "/api/v5/account/interest-rate"),
    post("set_greeks", "/api/v5/account/set-greeks", "PA"),
    get("get_max_withdrawal", "/api/v5/account/max-withdrawal"),
    get("get_interest_limits", "/api/v5/account/interest-limits"),
    post(
        "spot_manual_borrow_repay",
        "/api/v5/account/spot-manual-borrow-repay",
        "USDT",
        "borrow",
        "1",
    ),
    post("set_spot_auto_repay", "/api/v5/account/set-auto-repay", True, body={"autoRepay": True}),
    get("get_spot_borrow_repay_history", "/api/v5/account/spot-borrow-repay-history"),
    # Funding account.
    get("get_currencies", "/api/v5/asset/currencies"),
    get("get_balances", "/api/v5/asset/balances"),
    get("get_asset_valuation", "/api/v5/asset/asset-valuation"),
    post(
        "funds_transfer",
        "/api/v5/asset/transfer",
        "USDT",
        "1",
        "6",
        "18",
        body={"ccy": "USDT", "amt": "1", "from": "6", "to": "18"},
    ),
    get("get_transfer_state", "/api/v5/asset/transfer-state", "1"),
    get("get_bills", "/api/v5/asset/bills"),
    get("get_deposit_address", "/api/v5/asset/deposit-address", "USDT", query={"ccy": "USDT"}),
    get("get_deposit_history", "/api/v5/asset/deposit-history"),
    get(
        "get_deposit_withdraw_status",
        "/api/v5/asset/deposit-withdraw-status",
        "1",
        query={"wdId": "1"},
    ),
    get("get_exchange_list", "/api/v5/asset/exchange-list"),
    post("post_monthly_statement", "/api/v5/asset/monthly-statement", "Jan"),
    get("get_monthly_statement", "/api/v5/asset/monthly-statement", "Jan"),
    get("get_convert_currencies", "/api/v5/asset/convert/currencies"),
    get("get_convert_history", "/api/v5/asset/convert/history"),
    # Sub-account.
    get("get_subaccount_list", "/api/v5/users/subaccount/list"),
    get("get_subaccount_trading_balance", "/api/v5/account/subaccount/balances", "alpha"),
    get("get_subaccount_funding_balance", "/api/v5/asset/subaccount/balances", "alpha"),
    get("get_subaccount_bills", "/api/v5/asset/subaccount/bills", "alpha"),
    post(
        "transfer_between_subaccounts",
        "/api/v5/asset/subaccount/transfer",
        "USDT",
        "1",
        "6",
        "18",
        "alpha",
        "beta",
        body={"from": "6", "to": "18", "fromSubAccount": "alpha", "toSubAccount": "beta"},
    ),
    get("get_entrusted_subaccount_list", "/api/v5/users/entrust-subaccount-list"),
    get("get_subaccount_interest_limits", "/api/v5/account/subaccount/interest-limits", "alpha"),
    # Financial products.
    get("get_saving_balance", "/api/v5/finance/savings/balance"),
    post(
        "purchase_redeem_savings",
        "/api/v5/finance/savings/purchase-redempt",
        "USDT",
        "1",
        "purchase",
    ),
    post("set_savings_lending_rate", "/api/v5/finance/savings/set-lending-rate", "USDT", "0.01"),
    get("get_savings_lending_history", "/api/v5/finance/savings/lending-history"),
    pub("get_public_borrow_info", "/api/v5/finance/savings/lending-rate-summary"),
    pub("get_public_borrow_history", "/api/v5/finance/savings/lending-rate-history"),
    post("set_auto_earn", "/api/v5/account/set-auto-earn", "USDT", "turn_on"),
    get("get_staking_offers", "/api/v5/finance/staking-defi/offers"),
    post(
        "purchase_staking",
        "/api/v5/finance/staking-defi/purchase",
        "p1",
        [{"ccy": "ETH", "amt": "1"}],
        body={"productId": "p1", "investData": [{"ccy": "ETH", "amt": "1"}]},
    ),
    post("redeem_staking", "/api/v5/finance/staking-defi/redeem", "o1", "defi"),
    post("cancel_staking", "/api/v5/finance/staking-defi/cancel", "o1", "defi"),
    get("get_active_staking_orders", "/api/v5/finance/staking-defi/orders-active"),
    get("get_staking_order_history", "/api/v5/finance/staking-defi/orders-history"),
    get("get_eth_staking_product_info", "/api/v5/finance/staking-defi/eth/product-info"),
    post("purchase_eth_staking", "/api/v5/finance/staking-defi/eth/purchase", "1"),
    post("redeem_eth_staking", "/api/v5/finance/staking-defi/eth/redeem", "1"),
    post("cancel_eth_staking_redemption", "/api/v5/finance/staking-defi/eth/cancel-redeem", "o1"),
    get("get_eth_staking_balance", "/api/v5/finance/staking-defi/eth/balance"),
    get(
        "get_eth_staking_history",
        "/api/v5/finance/staking-defi/eth/purchase-redeem-history",
        "purchase",
    ),
    pub(
        "get_eth_staking_apy_history",
        "/api/v5/finance/staking-defi/eth/apy-history",
        7,
        query={"days": "7"},
    ),
    get("get_sol_staking_product_info", "/api/v5/finance/staking-defi/sol/product-info"),
    post("purchase_sol_staking", "/api/v5/finance/staking-defi/sol/purchase", "1"),
    post("redeem_sol_staking", "/api/v5/finance/staking-defi/sol/redeem", "1"),
    get("get_sol_staking_balance", "/api/v5/finance/staking-defi/sol/balance"),
    get(
        "get_sol_staking_history",
        "/api/v5/finance/staking-defi/sol/purchase-redeem-history",
        "redeem",
    ),
    pub("get_sol_staking_apy_history", "/api/v5/finance/staking-defi/sol/apy-history", 7),
    get("get_flexible_loan_borrow_currencies", "/api/v5/finance/flexible-loan/borrow-currencies"),
    get("get_flexible_loan_collateral_assets", "/api/v5/finance/flexible-loan/collateral-assets"),
    post(
        "get_flexible_loan_max_loan",
        "/api/v5/finance/flexible-loan/max-loan",
        "USDT",
        [{"ccy": "BTC", "amt": "1"}],
    ),
    get(
        "get_flexible_loan_max_collateral_redeem",
        "/api/v5/finance/flexible-loan/max-collateral-redeem-amount",
        "BTC",
    ),
    post(
        "adjust_flexible_loan_collateral",
        "/api/v5/finance/flexible-loan/adjust-collateral",
        "add",
        "BTC",
        "1",
    ),
    get("get_flexible_loan_info", "/api/v5/finance/flexible-loan/loan-info"),
    get("get_flexible_loan_history", "/api/v5/finance/flexible-loan/loan-history"),
    get("get_flexible_loan_interest_accrued", "/api/v5/finance/flexible-loan/interest-accrued"),
    post(
        "borrow_flexible_loan",
        "/api/v5/finance/flexible-loan/borrow",
        [{"ccy": "USDT", "amt": "10"}],
        "c1",
    ),
    post("repay_flexible_loan", "/api/v5/finance/flexible-loan/repay", "o1", "USDT", "1", "c1"),
    get("get_flexible_loan_emode_info", "/api/v5/finance/flexible-loan/emode-info"),
    get("get_dual_investment_currency_pairs", "/api/v5/finance/sfp/dcd/currency-pair"),
    get("get_dual_investment_products", "/api/v5/finance/sfp/dcd/products", "BTC", "USDT", "C"),
    post("request_dual_investment_quote", "/api/v5/finance/sfp/dcd/quote", "p1", "10", "USDT"),
    post("trade_dual_investment", "/api/v5/finance/sfp/dcd/trade", "q1"),
    post("request_dual_investment_redeem_quote", "/api/v5/finance/sfp/dcd/redeem-quote", "o1"),
    post("redeem_dual_investment", "/api/v5/finance/sfp/dcd/redeem", "o1", "q1"),
    get("get_dual_investment_order_status", "/api/v5/finance/sfp/dcd/order-status", "o1"),
    get("get_dual_investment_order_history", "/api/v5/finance/sfp/dcd/order-history"),
    get("get_okusd_limits", "/api/v5/finance/okusd/limits"),
    get("get_okusd_account", "/api/v5/finance/okusd/account"),
    get("get_okusd_rate_history", "/api/v5/finance/okusd/rate/history"),
    get("get_okusd_subscribe_history", "/api/v5/finance/okusd/subscribe/history"),
    get("get_okusd_redeem_history", "/api/v5/finance/okusd/redeem/history"),
    get("get_okusd_rewards_history", "/api/v5/finance/okusd/rewards/history"),
    post("subscribe_okusd", "/api/v5/finance/okusd/subscribe", "10", "c1"),
    post("redeem_okusd", "/api/v5/finance/okusd/redeem", "10", "1", "c1"),
)

WRAPPER_FILES = (
    "_withdrawals_http.py",
    "_transfers_http.py",
    "_batch_http.py",
    "_account_http.py",
    "_asset_http.py",
    "_finance_http.py",
    "_market_http.py",
    "_public_http.py",
    "_subaccount_http.py",
    "_trade_http.py",
)


COMPLETION = json.loads(
    (ROOT / "tests/fixtures/okx_request_cases.json").read_text(encoding="utf-8")
)
COMPLETION_NAMES = {e["name"] for e in COMPLETION}
CASES += tuple(
    Case(
        e["name"],
        e["method"],
        e["path"],
        kwargs=e["kwargs"],
        signed=not e["public"],
        body=e["wire"] if e["method"] == "POST" else {},
        query=e["wire"] if e["method"] == "GET" else {},
    )
    for e in COMPLETION
)


class _Handler(BaseHTTPRequestHandler):
    received: queue.Queue[dict[str, Any]]

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode() if length else ""
        self.received.put(
            {
                "method": self.command,
                "path": self.path,
                "body": body,
                "signed": self.headers.get("OK-ACCESS-SIGN") is not None,
                "headers": {key.lower(): value for key, value in self.headers.items()},
            }
        )
        payload = b'{"code":"0","msg":"","data":[]}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = _handle  # noqa: N815
    do_POST = _handle  # noqa: N815

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture(scope="module")
def okx_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    handler = type("Handler", (_Handler,), {"received": received})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
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


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": "key",
        "api_secret": "secret",
        "passphrase": "pass",
        "base_api": base_url,
        "timeout": 5,
        "preload_product_table": False,
    }


def _drain(received: queue.Queue[dict[str, Any]]) -> None:
    while not received.empty():
        received.get_nowait()


def _assert_request(case: Case, request: dict[str, Any]) -> None:
    from tests.unit.wire_contracts import assert_wire_contract
    assert_wire_contract("okx", case.name, request)
    split = urlsplit(request["path"])
    assert request["method"] == case.method, case.name
    assert split.path == case.path, case.name
    assert request["signed"] is case.signed, case.name
    if case.name in COMPLETION_NAMES:
        assert dict(parse_qsl(split.query)) == case.query
        if case.method == "POST":
            assert json.loads(request["body"]) == case.body
        if case.signed:
            headers = request["headers"]
            message = (
                headers["ok-access-timestamp"] + case.method + request["path"] + request["body"]
            )
            expected = base64.b64encode(
                hmac.new(b"secret", message.encode(), hashlib.sha256).digest()
            ).decode()
            assert headers["ok-access-sign"] == expected
    query = dict(parse_qsl(split.query))
    for key, value in case.query.items():
        assert query.get(key) == value, (case.name, key, query)
    if case.method == "POST":
        body = json.loads(request["body"])
        if case.name == "cancel_algo_orders":
            assert body == [{"instId": SWAP, "algoId": "42"}]
        if isinstance(case.body, list):
            assert body == case.body
        for key, value in case.body.items() if isinstance(case.body, dict) else []:
            assert body.get(key) == value, (case.name, key, body)
    else:
        assert request["body"] == "", case.name


def _native_supports_spread() -> bool:
    """
    Return whether the installed native extension dispatches spread routes.

    Spread trading was added to the Rust sources after some local builds of
    ``dcex._native``; stale builds reject the method name before any network I/O.
    """
    import dcex._native as native

    client = native.OkxHttpClient(timeout=10, base_url="http://127.0.0.1:9")
    try:
        client.public_request_json("get_spread_books", [])
    except ValueError as error:
        return "unsupported OKX public method" not in str(error)
    except Exception:  # noqa: BLE001 - any transport error means the route exists
        return True
    return True


NATIVE_SUPPORTS_SPREAD = _native_supports_spread()


def _skip_if_stale_native(case: Case) -> None:
    if "spread" in case.name and not NATIVE_SUPPORTS_SPREAD:
        pytest.skip("installed dcex._native predates OKX spread routes; rebuild with maturin")


def _public_wrapper_names(base: Path) -> set[str]:
    names: set[str] = set()
    for file_name in WRAPPER_FILES:
        tree = ast.parse((base / file_name).read_text(encoding="utf-8"))
        for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for node in cls.body:
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)
                ) and not node.name.startswith("_"):
                    names.add(node.name)
    return names


def test_case_table_covers_every_sync_and_async_wrapper() -> None:
    case_names = [case.name for case in CASES]
    assert len(case_names) == len(set(case_names))
    sync_names = _public_wrapper_names(ROOT / "dcex" / "okx")
    async_names = _public_wrapper_names(ROOT / "dcex" / "async_support" / "okx")
    assert sync_names == async_names
    assert sync_names == set(case_names) | {"get_sbe_orderbook"}


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_sync_okx_wrapper_hits_official_route(
    case: Case, okx_server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    from dcex.okx.client import Client

    _skip_if_stale_native(case)
    base_url, received = okx_server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    result = getattr(client, case.name)(*case.args, **case.kwargs)
    assert result["code"] == "0"
    _assert_request(case, received.get(timeout=10))
    assert received.empty(), case.name


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
async def test_async_okx_wrapper_hits_official_route(
    case: Case, okx_server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    from dcex.async_support.okx.client import Client

    _skip_if_stale_native(case)
    base_url, received = okx_server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    await client.async_init()
    try:
        result = await getattr(client, case.name)(*case.args, **case.kwargs)
    finally:
        await client.close()
    assert result["code"] == "0"
    _assert_request(case, received.get(timeout=10))
    assert received.empty(), case.name


def test_sync_cancel_all_orders_batches_only_matching_pending_orders() -> None:
    """cancel_all_orders must list, filter by instrument, then batch-cancel."""
    from dcex.okx.client import Client

    pending = {
        "code": "0",
        "msg": "",
        "data": [
            {"instId": SWAP, "ordId": "1", "clOrdId": "a"},
            {"instId": "ETH-USDT-SWAP", "ordId": "2"},
            {"instId": SWAP, "ordId": "3"},
        ],
    }
    received: queue.Queue[dict[str, Any]] = queue.Queue()

    class Handler(_Handler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode() if length else ""
            received.put({"method": self.command, "path": self.path, "body": body})
            payload = json.dumps(
                pending
                if self.command == "GET"
                else {"code": "0", "msg": "", "data": [{"sCode": "0"}]}
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = _handle  # noqa: N815
        do_POST = _handle  # noqa: N815

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = server.server_address[:2]
        client = Client(**_client_kwargs(f"http://{host}:{port}"))
        result = client.cancel_all_orders(SWAP)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)

    listing = received.get_nowait()
    cancel = received.get_nowait()
    assert received.empty()
    assert listing["method"] == "GET"
    assert urlsplit(listing["path"]).path == "/api/v5/trade/orders-pending"
    assert cancel["method"] == "POST"
    assert cancel["path"] == "/api/v5/trade/cancel-batch-orders"
    assert json.loads(cancel["body"]) == [
        {"instId": SWAP, "ordId": "1", "clOrdId": "a"},
        {"instId": SWAP, "ordId": "3"},
    ]
    assert result["data"] == [{"sCode": "0"}]


@pytest.mark.parametrize(
    ("module_path", "method_name"),
    [
        ("dcex.okx._finance_http:FinanceHTTP", "set_savings_lending_rate"),
        ("dcex.okx._subaccount_http:SubaccountHTTP", "get_subaccount_interest_limits"),
        ("dcex.async_support.okx._finance_http:FinanceHTTP", "set_savings_lending_rate"),
        (
            "dcex.async_support.okx._subaccount_http:SubaccountHTTP",
            "get_subaccount_interest_limits",
        ),
    ],
)
def test_undocumented_okx_wrappers_are_marked_deprecated(
    module_path: str, method_name: str
) -> None:
    import importlib

    module_name, class_name = module_path.split(":")
    method = getattr(getattr(importlib.import_module(module_name), class_name), method_name)
    assert method.__doc__ is not None
    assert "Deprecated" in method.__doc__


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "method,kwargs",
    [
        (
            "place_algo_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "trade_mode": "cross",
                "side": "sell",
                "order_type": "trigger",
                "sz": "1",
                "trigger_px": "100",
            },
        ),
        (
            "place_algo_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "trade_mode": "cross",
                "side": "sell",
                "order_type": "move_order_stop",
                "sz": "1",
                "callback_ratio": "0.01",
                "callback_spread": "1",
            },
        ),
        (
            "place_algo_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "trade_mode": "cross",
                "side": "sell",
                "order_type": "conditional",
                "close_fraction": "1",
                "sl_trigger_px": "100",
                "sl_ord_px": "-1",
            },
        ),
        (
            "place_algo_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "trade_mode": "cross",
                "side": "sell",
                "order_type": "conditional",
                "sz": "1",
                "sl_trigger_px": "100",
                "sl_ord_px": "NaN",
            },
        ),
        ("cancel_algo_orders", {"orders": []}),
        (
            "cancel_algo_orders",
            {
                "orders": [
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "0"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "1"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "2"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "3"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "4"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "5"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "6"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "7"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "8"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "9"},
                    {"product_symbol": "BTC-USDT-SWAP", "algoId": "10"},
                ]
            },
        ),
    ],
)
async def test_new_risk_controls_reject_invalid_input_before_transport(
    method: str, kwargs: dict[str, Any], mode: str
) -> None:
    """Invalid trading parameters fail locally in both public Python interfaces."""
    import importlib

    module = importlib.import_module(
        ("dcex.async_support." if mode == "async" else "dcex.") + "okx.client"
    )
    client = module.Client(**_client_kwargs("http://127.0.0.1:1"))
    try:
        if mode == "async":
            await client.async_init()
        with pytest.raises(
            ValueError,
            match="(?i)(invalid|required|must|requires|outside|unsupported|expected|between|specify|limit)",
        ):
            if mode == "async":
                await getattr(client, method)(**kwargs)
            else:
                getattr(client, method)(**kwargs)
    finally:
        if mode == "async":
            await client.close()
        else:
            client.close()
