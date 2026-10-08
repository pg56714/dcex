"""Typed Rust wrappers and Python methods reach the same dispatch the same way.

Both packages call one Rust dispatch by method name, so live results from the Python
smoke and order tests carry over to Rust only if, for every typed wrapper, Python uses
the same method name, the same visibility and the same required wire keys. The Rust
side (crates/dcex/src/exchanges/wrapper_dispatch.rs) proves each wrapper reaches its
dispatch; this test proves Python matches it.
"""

# ruff: noqa: D103
from __future__ import annotations

import importlib
import inspect
import json
import re
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLIENTS = {
    "arcus": "ArcusClient",
    "aster": "AsterClient",
    "backpack": "BackpackClient",
    "binance": "BinanceClient",
    "bingx": "BingxClient",
    "bitget": "BitgetClient",
    "bybit": "BybitClient",
    "extended": "ExtendedClient",
    "hyperliquid": "HyperliquidClient",
    "kraken": "KrakenClient",
    "kucoin": "KucoinClient",
    "lighter": "LighterClient",
    "mexc": "MexcClient",
    "okx": "OkxClient",
    "ondo": "OndoClient",
}
# Accepted required-key differences: (rust-only keys, python-required-only keys) -> reason.
OKX_ALIAS = ({"product_symbol"}, {"instId"})  # dispatch resolves product_symbol to instId
KNOWN: dict[tuple[str, str], tuple[set[str], set[str]]] = {
    **{
        ("okx", name): OKX_ALIAS
        for name in (
            "get_candles_ticks",
            "get_contract_long_short_ratio",
            "get_contract_open_interest_history",
            "get_contract_taker_volume",
            "get_funding_rate",
            "get_funding_rate_history",
            "get_orderbook",
            "get_public_trades",
            "get_top_trader_long_short_account_ratio",
            "get_top_trader_long_short_position_ratio",
        )
    },
    # One of two identifiers; the typed wrapper takes the exchange ID, Python either.
    ("kraken", "edit_futures_order"): ({"orderId"}, set()),
    ("kraken", "amend_spot_order"): ({"txid"}, set()),
    ("okx", "cancel_spread_order"): ({"ordId"}, set()),
    ("okx", "get_spread_order"): ({"ordId"}, set()),
    # Python keeps its positional order (type_ precedes size); dispatch requires both.
    ("kucoin", "place_futures_order"): ({"side", "size"}, set()),
    ("kucoin", "place_futures_market_order"): ({"side", "size"}, set()),
    ("kucoin", "test_futures_order"): ({"side", "size"}, set()),
    # Python takes the documented order body as keyword arguments.
    ("ondo", "place_order"): ({"market", "side"}, set()),
    # Python keeps all four optional (the category is derived from a unified symbol);
    # dispatch still requires the symbol, side and strategy type.
    ("bybit", "create_strategy"): ({"category", "product_symbol", "side", "strategyType"}, set()),
    # The typed wrapper names the symbol; the exchange also accepts category-wide queries.
    ("bybit", "get_public_trade_history"): ({"product_symbol"}, set()),
}


def rust_wrappers(exchange: str) -> list[tuple[str, str, bool, list[str]]]:
    """(client type, method, public, wire keys) for every typed wrapper of an exchange."""
    found = []
    for path in sorted((ROOT / "crates/dcex/src/exchanges" / exchange).rglob("*.rs")):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"impl_exchange_method_wrappers!\s*\{", text):
            body = _balanced(text, match.end() - 1, "{", "}")
            body = re.sub(r"//[^\n]*", "", body)
            body = re.sub(r"#\[[^\]]*\]", "", body)
            client = re.match(r"\{\s*(?:@extend;\s*)?(\w+)", body).group(1)  # type: ignore[union-attr]
            for label, public in (("public", True), ("private", False)):
                section = re.search(rf"\b{label}\s*\[", body)
                if section is None:
                    continue
                entries = _balanced(body, section.end() - 1, "[", "]")
                for entry in re.finditer(r"(\w+)\s*\(([^)]*)\)", entries[1:-1]):
                    keys = re.findall(r'=>\s*"([^"]+)"', entry.group(2))
                    found.append((client, entry.group(1), public, keys))
    return found


def _balanced(text: str, start: int, open_: str, close: str) -> str:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == open_:
            depth += 1
        elif text[index] == close:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError("unbalanced wrapper macro")


class Recorder:
    """Stands in for the native client and records the dispatch call."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    def __getattr__(self, attr: str) -> Any:  # noqa: ANN401
        def record(*args: Any, **_: Any) -> tuple[int, dict[str, str], bytes]:  # noqa: ANN401
            self.calls.append((attr, args))
            return 200, {}, b'{"code":0,"data":{}}'

        return record


def _dummy(parameter: inspect.Parameter) -> Any:  # noqa: ANN401
    annotation = str(parameter.annotation)
    if "list" in annotation or "Sequence" in annotation:
        return [{"symbol": "BTCUSDT", "side": "BUY", "quantity": "1", "price": "1"}]
    if "dict" in annotation:
        return {"a": "1"}
    if "bool" in annotation:
        return True
    if "int" in annotation and "str" not in annotation:
        return 7000 + sum(map(ord, parameter.name))
    return "v_" + parameter.name


def python_call(exchange: str, name: str) -> tuple[str, str, set[str], set[str]] | None:
    """(native attribute, method name, sent keys, required keys) for one Python call."""
    client_cls = importlib.import_module(f"dcex.{exchange}.client").Client
    function = getattr(client_cls, name)
    try:
        client = client_cls(preload_product_table=False)
    except TypeError:
        client = client_cls()
    recorder = Recorder()
    client._native_client = recorder
    required = [
        p
        for p in inspect.signature(function).parameters.values()
        if p.name != "self"
        and p.default is inspect.Parameter.empty
        and p.kind not in (p.VAR_KEYWORD, p.VAR_POSITIONAL)
    ]
    values = {p.name: _dummy(p) for p in required}
    try:
        getattr(client, name)(**values)
    except Exception:  # noqa: BLE001, S110 - local validation may still have dispatched
        pass
    if not recorder.calls:
        return None
    attr, args = recorder.calls[0]
    if len(args) < 2 or not isinstance(args[1], list):
        return None
    sent = dict(args[1])
    scalars = {str(v) for v in values.values() if not isinstance(v, list | dict | bool)}
    encoded = {
        json.dumps(v, separators=(",", ":")) for v in values.values() if isinstance(v, list | dict)
    } | {json.dumps(v) for v in values.values() if isinstance(v, list | dict)}
    required_keys = {k for k, v in sent.items() if str(v) in scalars | encoded}
    return attr, args[0], set(sent), required_keys


@pytest.mark.parametrize("exchange", sorted(CLIENTS))
def test_typed_wrappers_match_python(exchange: str) -> None:
    client_cls = importlib.import_module(f"dcex.{exchange}.client").Client
    problems = []
    compared = 0
    for client, name, public, keys in rust_wrappers(exchange):
        if client != CLIENTS[exchange]:
            continue
        if not hasattr(client_cls, name):
            problems.append(f"{name}: typed Rust wrapper without a Python method")
            continue
        call = python_call(exchange, name)
        if call is None:
            continue  # rejected before dispatch (e.g. a confirm flag); checked elsewhere
        attr, dispatched, sent, required = call
        compared += 1
        if dispatched != name:
            problems.append(f"{name}: Python dispatches {dispatched!r}")
        if attr.startswith("public") != public:
            problems.append(f"{name}: Rust {'public' if public else 'private'}, Python {attr}")
        diff = (set(keys) - sent, required - set(keys))
        if any(diff) and KNOWN.get((exchange, name)) != diff:
            problems.append(f"{name}: rust-only {sorted(diff[0])}, python-only {sorted(diff[1])}")
    assert compared > 0
    assert not problems, "\n".join(problems)


def test_known_differences_are_still_needed() -> None:
    stale = []
    for exchange, name in KNOWN:
        wrapper = next(
            (w for w in rust_wrappers(exchange) if w[1] == name and w[0] == CLIENTS[exchange]),
            None,
        )
        call = python_call(exchange, name)
        if wrapper is None or call is None:
            stale.append(f"{exchange}.{name}")
            continue
        _, _, sent, required = call
        if (set(wrapper[3]) - sent, required - set(wrapper[3])) != KNOWN[(exchange, name)]:
            stale.append(f"{exchange}.{name}")
    assert not stale, "remove resolved KNOWN entries: " + ", ".join(stale)
