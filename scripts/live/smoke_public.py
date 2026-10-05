"""
Call every public (unauthenticated) client method once and classify the outcome.

Read-only market data only: no credentials are loaded and nothing is signed. Methods
are discovered from source (a call to a public request helper), so new endpoints are
picked up automatically. Results go to live-results/ (gitignored).
"""

import argparse
import ast
import importlib
import inspect
import json
import re
import textwrap
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PUBLIC_HELPERS = {
    "_native_public",
    "public_request",
    "_earn_native_public",
    "_native_finance_public",
}
# Public but not plain reads (signed submissions, auth handshakes): never called.
SKIP_NAME = re.compile(r"send|submit|login|logout|register|auth|sign|faucet|verify|create|cancel")
EXCHANGES = (
    "arcus",
    "aster",
    "backpack",
    "binance",
    "bingx",
    "bitget",
    "bybit",
    "extended",
    "hyperliquid",
    "kraken",
    "kucoin",
    "lighter",
    "mexc",
    "okx",
    "ondo",
)
SHARED_ERROR = re.compile(r"API Error: \[([^\]]+)\] (.*?)(?: \(HTTP (\d{3})\))?$", re.S)
PAUSE_SECONDS = 0.25
NOW_MS = int(time.time() * 1000)
DAY_MS = 86_400_000
NOW_S = NOW_MS // 1000
DAY_S = 86_400
# A well-known public address (Hyperliquid's HLP vault): public per-user reads only.
HL_PUBLIC_ADDRESS = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"

# Unified symbols tried in order; a local resolver rejection moves to the next one.
SYMBOLS = {
    "arcus": ["BTC-USD"],
    "aster": ["BTC-USDT-SWAP", "BTC-USDT-SPOT"],
    "backpack": ["SOL-USDC-SWAP", "SOL-USDC-SPOT"],
    "binance": ["BTC-USDT-SWAP", "BTC-USDT-SPOT", "BTC-USD-SWAP"],
    "bingx": ["BTC-USDT-SWAP", "BTC-USDT-SPOT", "BTC-USD-SWAP"],
    "bitget": ["BTC-USDT-SWAP", "BTC-USDT-SPOT"],
    "bybit": ["BTC-USDT-SWAP", "BTC-USDT-SPOT"],
    "extended": ["BTC-USD-SWAP"],
    "hyperliquid": ["BTC-USD-SWAP", "PURR-USDC-SPOT"],
    "kraken": ["BTC-USD-SWAP", "BTC-USD-SPOT"],
    "kucoin": ["BTC-USDT-SWAP", "BTC-USDT-SPOT"],
    "lighter": ["ETH"],
    "mexc": ["BTC-USDT-SWAP", "BTC-USDT-SPOT"],
    "okx": ["BTC-USDT-SWAP", "BTC-USDT-SPOT"],
    "ondo": ["BTC-USD-SWAP"],
}
# The library normalises timeframes, so "1h" is the unified interval everywhere.
COMMON: dict[str, Any] = {
    "interval": "1h",
    "timeframe": "1h",
    "resolution": "1h",
    "start_time": NOW_MS - DAY_MS,
    "startTime": NOW_MS - DAY_MS,
    "end_time": NOW_MS,
    "endTime": NOW_MS,
    "limit": 5,
    "page": 1,
    "page_index": 1,
    "page_size": 10,
    "ccy": "BTC",
    "coin": "BTC",
    "currency": "BTC",
    "asset": "BTC",
}
# Per-exchange values (native symbols, enums, time units) override COMMON.
FIXTURES: dict[str, dict[str, Any]] = {
    "arcus": {"market": "BTC-USD", "to": NOW_S},
    "aster": {"symbol": "BTCUSDT", "pair": "BTCUSDT", "asset": "USDT", "leverage": 10},
    "backpack": {"symbol": "SOL_USDC", "startTime": NOW_S - DAY_S, "endTime": NOW_S},
    "binance": {
        "symbol": "BTCUSDT",
        "pair": "BTCUSDT",
        "contract_type": "PERPETUAL",
        "period": "1h",
        "underlying": "BTCUSDT",
        "underlyingAsset": "BTC",
    },
    "bingx": {"symbol": "BTC-USDT", "depth": 5, "type_": "step0"},
    "bitget": {
        "symbol": "BTCUSDT",
        "category": "USDT-FUTURES",
        "product_type": "USDT-FUTURES",
        "granularity": "1H",
        "interval": "1H",
        "coin": "USDT",
        "code": "AAPL",
        "language": "en_US",
    },
    "bybit": {
        "symbol": "BTCUSDT",
        "category": "linear",
        "base_coin": "BTC",
        "index_name": "BTCUSDT",
        "locale": "en-US",
        "lt_coin": "BTC3L",
    },
    "extended": {"market": "BTC-USD"},
    "hyperliquid": {"token": "PURR", "user": HL_PUBLIC_ADDRESS, "vault_address": HL_PUBLIC_ADDRESS},
    "kraken": {
        "symbol": "XBTUSD",
        "interval": 60,
        "tradeable": "PF_XBTUSD",
        "tick_type": "trade",
        "since": NOW_S - DAY_S,
        "analytics_type": "open-interest",
    },
    "kucoin": {
        "symbol": "BTC-USDT",
        "trade_type": "SPOT",
        "base": "USD",
        "from_": NOW_MS - DAY_MS,
        "to": NOW_MS,
        "from_currency": "BTC",
        "to_currency": "USDT",
        "size": 20,
        "start_at": NOW_MS - DAY_MS,
        "end_at": NOW_MS,
    },
    "lighter": {
        "market_id": 0,
        "count_back": 5,
        "start_timestamp": NOW_MS - DAY_MS,
        "end_timestamp": NOW_MS,
        "by": "index",
        "value": "1",
        "account_index": 1,
    },
    "mexc": {"symbol": "BTCUSDT", "interval": "60m"},
    "okx": {
        "inst_id": "BTC-USDT-SWAP",
        "inst_type": "SWAP",
        "instType": "SWAP",
        "instrument_type": "SWAP",
        "inst_family": "BTC-USD",
        "instFamily": "BTC-USD",
        "index": "BTC-USD",
        "days": 7,
        "sprd_id": "BTC-USDT_BTC-USDT-SWAP",
        "sz": "1",
    },
    "ondo": {
        "market": "BTCUSD.P",
        "symbol": "BTCUSD.P",
        "from_time": NOW_S - DAY_S,
        "to_time": NOW_S,
    },
}
# Method-specific values, including optional parameters an endpoint needs in practice.
METHOD_FIXTURES: dict[str, dict[str, Any]] = {
    "backpack.get_borrow_lend_market_history": {"interval": "1d"},
    "backpack.get_vault_history": {"interval": "1d"},
    "bingx.get_content_v1_announcement": {"content_type": "LATEST_ANNOUNCEMENT"},
    "bingx.get_swap_funding_rate": {"product_symbol": "BTC-USDT-SWAP"},
    "bitget.get_uta_position_tiers": {"product_symbol": "BTC-USDT-SWAP"},
    "bitget.get_uta_current_funding_rate": {"product_symbol": "BTC-USDT-SWAP"},
    "bybit.get_public_trade_history": {"category": "linear"},
    "extended.get_candles": {"limit": 5},
    "extended.get_open_interest": {"interval": "P1H"},
    "extended.get_interest_rate_curves_history": {"interval": "DAY"},
    "extended.get_vault_performance": {"interval": "DAY"},
    "hyperliquid.get_borrow_lend_reserve_state": {"token": 0},
    "kraken.get_futures_ticker": {"symbol": "PF_XBTUSD"},
    "kraken.get_futures_kline": {"symbol": "PF_XBTUSD"},
    "kucoin.get_futures_orderbook": {"product_symbol": "BTC-USDT-SWAP"},
    "okx.get_index_candles": {"inst_id": "BTC-USD"},
    "okx.get_history_index_candles": {"inst_id": "BTC-USD"},
    "okx.get_index_tickers": {"inst_id": "BTC-USD"},
    "okx.get_delivery_exercise_history": {"inst_type": "OPTION", "inst_family": "BTC-USD"},
    "okx.get_option_summary": {"inst_family": "BTC-USD"},
    "okx.get_option_trades": {"inst_family": "BTC-USD"},
    "okx.get_position_tiers": {"inst_type": "SWAP", "inst_family": "BTC-USD"},
    "okx.get_insurance_fund": {"inst_type": "SWAP", "inst_family": "BTC-USD"},
}


def public_methods(exchange: str) -> list[tuple[str, Any]]:
    """Client methods whose body calls a public request helper."""
    client_cls = importlib.import_module(f"dcex.{exchange}.client").Client
    found = []
    for name, fn in inspect.getmembers(client_cls, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
        except (OSError, TypeError):
            continue
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        if calls & PUBLIC_HELPERS:
            found.append((name, fn))
    return found


def required_params(fn: Any) -> list[str]:  # noqa: ANN401
    """Parameters without a default (the ones a call must supply)."""
    return [
        p.name
        for p in inspect.signature(fn).parameters.values()
        if p.name != "self"
        and p.default is inspect.Parameter.empty
        and p.kind not in (p.VAR_KEYWORD, p.VAR_POSITIONAL)
    ]


def build_kwargs(exchange: str, method: str, fn: Any) -> tuple[dict[str, Any], list[str]]:  # noqa: ANN401
    """Fill required parameters plus method fixtures; report required ones without a value."""
    accepted = set(inspect.signature(fn).parameters)
    specific = METHOD_FIXTURES.get(f"{exchange}.{method}", {})
    values = {**COMMON, **FIXTURES.get(exchange, {}), **specific}
    kwargs = {k: v for k, v in specific.items() if k in accepted}
    missing = []
    for name in required_params(fn):
        if name == "product_symbol" or name in kwargs:
            continue
        if name in values:
            kwargs[name] = values[name]
        else:
            missing.append(name)
    return kwargs, missing


def classify(error: BaseException) -> dict[str, str]:
    """Sort a failure into exchange, key, local-validation or transport errors."""
    text = str(error).splitlines()[0] if str(error) else type(error).__name__
    shared = SHARED_ERROR.search(text)
    if shared:
        return {
            "outcome": "exchange_error",
            "code": shared.group(1),
            "http": shared.group(3) or "",
            "message": shared.group(2)[:300],
        }
    if "API key is required" in text:
        return {"outcome": "needs_key", "message": text[:300]}
    if isinstance(error, ValueError | TypeError):
        return {"outcome": "local_error", "message": text[:300]}
    return {"outcome": "transport_error", "message": text[:300]}


def call_method(
    client: Any,  # noqa: ANN401
    exchange: str,
    name: str,
    fn: Any,  # noqa: ANN401
    skip: re.Pattern[str] = SKIP_NAME,
) -> dict[str, Any]:
    """Call one method with fixtures and record only the outcome (never the response)."""
    row: dict[str, Any] = {"exchange": exchange, "method": name}
    if skip.search(name):
        return {**row, "outcome": "skipped", "message": "not a plain read"}
    kwargs, missing = build_kwargs(exchange, name, fn)
    if missing:
        return {**row, "outcome": "needs_fixture", "message": ", ".join(missing)}
    if "product_symbol" in kwargs:
        symbols = [kwargs.pop("product_symbol")]
    elif "product_symbol" in required_params(fn):
        symbols = SYMBOLS[exchange]
    else:
        symbols = [None]
    result: dict[str, Any] = {}
    for symbol in symbols:
        call_kwargs = dict(kwargs, **({"product_symbol": symbol} if symbol else {}))
        try:
            getattr(client, name)(**call_kwargs)
        except Exception as error:  # noqa: BLE001 - every outcome is recorded
            result = classify(error)
            if result["outcome"] == "local_error" and symbol != symbols[-1]:
                continue  # e.g. a spot-only method rejecting the swap symbol locally
        else:
            result = {"outcome": "ok"}
        if symbol:
            result["product_symbol"] = symbol
        break
    return {**row, **result}


def run_exchange(exchange: str) -> list[dict[str, Any]]:
    """Call every public method of one exchange, pausing between requests."""
    module = importlib.import_module(f"dcex.{exchange}.client")
    try:
        client = module.Client()
    except Exception as error:  # noqa: BLE001
        return [{"exchange": exchange, "method": "<client>", **classify(error)}]
    rows = []
    try:
        for name, fn in public_methods(exchange):
            rows.append(call_method(client, exchange, name, fn))
            time.sleep(PAUSE_SECONDS)
    finally:
        try:
            client.close()
        except Exception:  # noqa: BLE001, S110 - closing never hides results
            pass
    return rows


OUTCOMES = (
    "ok",
    "exchange_error",
    "local_error",
    "transport_error",
    "needs_fixture",
    "needs_key",
    "skipped",
)


def main() -> int:
    """Run the selected exchanges and write the results file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exchange", choices=EXCHANGES, action="append")
    args = parser.parse_args()
    exchanges = args.exchange or list(EXCHANGES)
    for exchange in exchanges:
        # Import up front: concurrent first imports race on package initialisation.
        importlib.import_module(f"dcex.{exchange}.client")
    with ThreadPoolExecutor(max_workers=len(exchanges)) as pool:
        rows = [row for result in pool.map(run_exchange, exchanges) for row in result]
    out = Path("live-results") / f"smoke-public-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print("exchange | " + " | ".join(OUTCOMES))
    for exchange in exchanges:
        counts = Counter(r["outcome"] for r in rows if r["exchange"] == exchange)
        print(exchange + " | " + " | ".join(str(counts[o]) for o in OUTCOMES))
    total = Counter(r["outcome"] for r in rows)
    print("total | " + " | ".join(str(total[o]) for o in OUTCOMES))
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
