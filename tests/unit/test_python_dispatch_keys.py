"""
The keys every Python wrapper sends to the native dispatcher, kept in a committed table.

Rust's ``wrapper_dispatch`` test replays the table against each exchange dispatcher and
fails when a key is rejected, so an allow-list can never silently drop a Python argument.
Regenerate the table after changing a wrapper with ``DCEX_WRITE_DISPATCH_KEYS=1``.
"""

from __future__ import annotations

import asyncio
import contextlib
import importlib
import inspect
import json
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

TABLE = Path(__file__).resolve().parents[2] / "crates/dcex/src/exchanges/python_dispatch_keys.json"
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
REQUESTS = {
    "public_request_json": "public",
    "public_request_json_async": "public",
    "private_request_json": "private",
    "private_request_json_async": "private",
}


CALL_ERROR = re.compile(
    r"multiple values for|unexpected keyword argument|missing \d+ required|positional argument"
)


class _Recorder:
    """Stands in for the native client and records each dispatched request."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, list[str]]] = []

    def __getattr__(self, attr: str) -> Any:  # noqa: ANN401
        def record(*args: Any) -> Any:  # noqa: ANN401
            side = REQUESTS.get(attr)
            if side and len(args) >= 2 and isinstance(args[1], list):
                self.calls.append((side, args[0], [key for key, _ in args[1]]))
            result = (200, {}, "{}")
            if attr.endswith("_async"):

                async def done() -> Any:  # noqa: ANN401
                    return result

                return done()
            return result

        return record


def _placeholder(parameter: inspect.Parameter) -> Any:  # noqa: ANN401
    annotation = str(parameter.annotation)
    if "bool" in annotation:
        return True
    if "int" in annotation:
        return 1
    if "Decimal" in annotation or "float" in annotation:
        return Decimal(1)
    if "list" in annotation or "Sequence" in annotation:
        return [{"a": "1"}]
    if "dict" in annotation or "Mapping" in annotation:
        return {"a": "1"}
    return "1"


def _record(module_name: str) -> dict[str, set[str]]:
    cls = importlib.import_module(module_name).Client
    client = cls.__new__(cls)
    recorded: dict[str, set[str]] = {}
    for name, member in inspect.getmembers(cls, inspect.isfunction):
        if name.startswith("_") or name in {"close", "async_init"}:
            continue
        recorder = _Recorder()
        client.__dict__["_native_client"] = recorder
        kwargs = {
            parameter.name: _placeholder(parameter)
            for parameter in list(inspect.signature(member).parameters.values())[1:]
            if parameter.kind not in {parameter.VAR_KEYWORD, parameter.VAR_POSITIONAL}
        }
        # Placeholder values may fail validation; only the dispatched keys matter here.
        # A call-signature TypeError is a broken wrapper (e.g. a keyword passed twice).
        try:
            result = getattr(client, name)(**kwargs)
            if inspect.isawaitable(result):
                asyncio.run(result)
        except TypeError as error:
            if CALL_ERROR.search(str(error)):
                raise AssertionError(f"{module_name}.{name}: {error}") from error
        except Exception:  # noqa: BLE001, S110
            pass
        for side, method, keys in recorder.calls:
            if re.fullmatch(r"[a-z][a-z0-9_]*", method):
                recorded.setdefault(f"{side} {method}", set()).update(keys)
    return recorded


def _current() -> dict[str, dict[str, list[str]]]:
    table: dict[str, dict[str, list[str]]] = {}
    for exchange in EXCHANGES:
        merged: dict[str, set[str]] = {}
        for module in (f"dcex.{exchange}.client", f"dcex.async_support.{exchange}.client"):
            for entry, keys in _record(module).items():
                merged.setdefault(entry, set()).update(keys)
        table[exchange] = {entry: sorted(keys) for entry, keys in sorted(merged.items())}
    return table


def _render(table: dict[str, dict[str, list[str]]]) -> str:
    """One line per dispatched method keeps the table reviewable in diffs."""
    exchanges = []
    for exchange, entries in table.items():
        lines = ",\n".join(
            f"  {json.dumps(entry)}: {json.dumps(keys)}" for entry, keys in entries.items()
        )
        exchanges.append(f" {json.dumps(exchange)}: {{\n{lines}\n }}")
    return "{\n" + ",\n".join(exchanges) + "\n}\n"


def test_dispatch_key_table_matches_the_python_wrappers() -> None:
    """The committed table lists exactly what the Python wrappers dispatch."""
    current = _current()
    if os.environ.get("DCEX_WRITE_DISPATCH_KEYS") == "1":
        TABLE.write_text(_render(current), encoding="utf-8", newline="\n")
    committed = json.loads(TABLE.read_text(encoding="utf-8"))
    assert committed == current, (
        "python_dispatch_keys.json is stale; rerun with DCEX_WRITE_DISPATCH_KEYS=1"
    )
