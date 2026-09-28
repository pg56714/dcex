"""Enforce the shared layout documented in docs/schema-conventions.md."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "crates/dcex/src/exchanges"
EXCHANGES = re.findall(r"^pub mod (\w+);$", (NATIVE / "mod.rs").read_text(encoding="utf-8"), re.M)
RUST_CORE = (
    "mod.rs",
    "client.rs",
    "market.rs",
    "trade.rs",
    "params.rs",
    "signing.rs",
    "private.rs",
    "tests.rs",
    "tests/endpoint_coverage.rs",
)
PYTHON_CORE = (
    "client.py",
    "_http_manager.py",
    "_market_http.py",
    "_trade_http.py",
    "_account_http.py",
)


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_exchange_core_files(exchange):
    native = NATIVE / exchange
    assert all((native / name).is_file() for name in RUST_CORE)
    for package in (ROOT / "dcex", ROOT / "dcex/async_support"):
        assert all((package / exchange / name).is_file() for name in PYTHON_CORE)


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_private_dispatch_has_one_home(exchange):
    native = NATIVE / exchange
    assert re.search(r"^mod private;$", (native / "mod.rs").read_text(encoding="utf-8"), re.M)
    dispatch_files = {
        path.relative_to(native).as_posix()
        for path in native.rglob("*.rs")
        if re.search(r"pub\s+async\s+fn\s+private_request\s*\(", path.read_text(encoding="utf-8"))
    }
    assert dispatch_files == {"private.rs"}


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_native_test_entry_only_declares_existing_modules(exchange):
    native = NATIVE / exchange
    source = (native / "tests.rs").read_text(encoding="utf-8")
    assert re.fullmatch(r"(?:\s*mod \w+;\s*)+", source)
    modules = re.findall(r"mod (\w+);", source)
    assert len(modules) == len(set(modules))
    assert "endpoint_coverage" in modules
    assert all((native / "tests" / f"{name}.rs").is_file() for name in modules)
    assert not (native / "tests/route_coverage.rs").exists()


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_schema_data_uses_the_shared_folder(exchange):
    native = NATIVE / exchange
    assert (native / "schemas").is_dir()
    assert not list((native / "endpoint_schemas").rglob("*.*"))
