"""Regression tests for the examples layout."""
# ruff: noqa: D103

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples"
MIGRATED_EXCHANGES = (
    "aster",
    "backpack",
    "binance",
    "bingx",
    "bitget",
    "bitmart",
    "bitmex",
    "bybit",
    "hyperliquid",
    "kraken",
    "kucoin",
    "lighter",
    "mexc",
    "okx",
)
MUTATING_EXAMPLE_PREFIXES = (
    "amend",
    "cancel",
    "change_margin",
    "close_position",
    "close_swap",
    "create",
    "funds_transfer",
    "future_dual_mode_switch",
    "modify",
    "place",
    "post_withdraw",
    "repay",
    "set",
    "submit_leverage",
    "switch",
    "transfer",
    "update",
    "withdraw",
)


def _client_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if ast.unparse(node.func.value) == "client":
                calls.append(node.func.attr)
    return calls


def test_examples_do_not_include_notebooks() -> None:
    assert list(EXAMPLES.rglob("*.ipynb")) == []


def test_python_examples_use_main_entrypoints() -> None:
    for path in EXAMPLES.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        function_names = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert "main" in function_names, path
        assert not any(name.startswith("test_") for name in function_names), path


def test_migrated_exchanges_have_sync_and_async_examples() -> None:
    missing: list[str] = []
    for exchange in MIGRATED_EXCHANGES:
        for mode in ("sync", "async"):
            for suffix in ("public", "private_readonly"):
                path = EXAMPLES / mode / f"{exchange}_{suffix}.py"
                if not path.exists():
                    missing.append(str(path.relative_to(ROOT)))

    assert missing == []


def test_examples_do_not_call_mutating_client_methods() -> None:
    offenders: list[str] = []
    for path in EXAMPLES.rglob("*.py"):
        offenders.extend(
            f"{path.relative_to(ROOT)}::{method_name}"
            for method_name in _client_calls(path)
            if method_name.startswith(MUTATING_EXAMPLE_PREFIXES)
        )

    assert offenders == []
