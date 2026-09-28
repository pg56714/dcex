"""Enforce the shared layout documented in docs/schema-conventions.md."""

import re
import ast
import importlib
import inspect
import json
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
        if "tests" not in path.relative_to(native).parts
        and re.search(r"\bfn\s+(?:legacy_)?private_request(?:_boxed)?\s*(?:<[^\n]+?>)?\s*\(", _rust_code(path.read_text(encoding="utf-8")))
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
    assert {path.stem for path in (native / "tests").glob("*.rs")} == set(modules)
    assert not (native / "tests/route_coverage.rs").exists()


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_schema_data_uses_the_shared_folder(exchange):
    native = NATIVE / exchange
    assert (native / "schemas").is_dir()
    assert not list((native / "endpoint_schemas").rglob("*.*"))


def _rust_code(source):
    return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|r(?P<hash>\#*)"[\s\S]*?"(?P=hash)|"(?:\\[\s\S]|[^"\\])*"', " ", source)


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_retired_module_names_cannot_return(exchange):
    assert not {"wallet.rs", "asset.rs", "batch_controls.rs"} & {
        path.name for path in (NATIVE / exchange).rglob("*.rs")
    }
    for prefix in ("dcex", "dcex/async_support"):
        assert not list((ROOT / prefix / exchange).rglob("_wallet_http.py"))


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.parametrize("prefix", ["dcex", "dcex.async_support"])
def test_core_mixins_are_nonempty_and_inherited(exchange, prefix):
    package = f"{prefix}.{exchange}"
    clients = [importlib.import_module(package + ".client").Client]
    if exchange == "arcus":
        clients.append(importlib.import_module(package + ".spot").SpotClient)
    for file in PYTHON_CORE[1:]:
        module = importlib.import_module(package + "." + file.removesuffix(".py"))
        mixins = [cls for cls in vars(module).values() if isinstance(cls, type) and cls.__module__ == module.__name__]
        assert mixins, (package, file)
        for mixin in mixins:
            assert any(mixin in client.__mro__ for client in clients), (package, mixin)
            tree = ast.parse(inspect.getsource(mixin))
            assert any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in tree.body[0].body), (package, mixin)


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_fund_handlers_stay_in_their_declared_module(exchange):
    manifest = json.loads((ROOT / "tests/fixtures/fund_module_locations.json").read_text(encoding="utf-8"))
    for domain, names in manifest[exchange].items():
        for name in names:
            locations = {
                path.relative_to(NATIVE / exchange).as_posix()
                for path in (NATIVE / exchange).rglob("*.rs")
                if re.search(r"\bfn\s+" + re.escape(name) + r"\s*[<(]", _rust_code(path.read_text(encoding="utf-8")))
            }
            assert locations == {domain + ".rs"}, (exchange, name, locations)
