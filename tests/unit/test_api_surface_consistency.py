"""Offline checks for Python and Rust exchange API surface parity."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCHANGES = (
    "aster",
    "backpack",
    "binance",
    "bingx",
    "bitget",
    "bitmart",
    "bitmex",
    "bybit",
    "extended",
    "hyperliquid",
    "kraken",
    "kucoin",
    "lighter",
    "mexc",
    "okx",
)
PYTHON_LIFECYCLE_METHODS = {"async_init", "close"}


def _python_client_methods(base: Path, exchange: str) -> set[str]:
    methods: set[str] = set()
    for path in (base / exchange).glob("*.py"):
        if path.name.startswith("__") or path.name.endswith("enums.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for child in node.body:
                if not isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                    continue
                if child.name.startswith("_") or child.name in PYTHON_LIFECYCLE_METHODS:
                    continue
                methods.add(child.name)
    return methods


def _rust_exchange_source(exchange: str) -> str:
    source_dir = ROOT / "crates" / "dcex" / "src" / "exchanges" / exchange
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in source_dir.glob("*.rs")
        if path.name != "tests.rs"
    )


def test_python_sync_and_async_clients_expose_same_methods() -> None:
    """Python sync and async clients should expose matching method names."""
    for exchange in EXCHANGES:
        sync_methods = _python_client_methods(ROOT / "dcex", exchange)
        async_methods = _python_client_methods(ROOT / "dcex" / "async_support", exchange)
        assert sync_methods == async_methods, exchange


def test_rust_clients_cover_python_client_method_names() -> None:
    """Rust direct clients should expose every Python client method name."""
    for exchange in EXCHANGES:
        rust_source = _rust_exchange_source(exchange)
        missing = sorted(
            method
            for method in _python_client_methods(ROOT / "dcex", exchange)
            if f"{method}(" not in rust_source
        )
        assert not missing, f"{exchange}: {missing}"
