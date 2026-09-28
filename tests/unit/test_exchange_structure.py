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
    # Existing product handlers are explicit, reviewed delegates of private.rs.
    # New names (including suffix/prefix variants) must never silently escape.
    domains = json.loads((ROOT / "tests/fixtures/private_domain_handlers.json").read_text(encoding="utf-8"))
    dispatch_files = set()
    for path in native.rglob("*.rs"):
        relative = path.relative_to(native).as_posix()
        if "tests" in path.relative_to(native).parts:
            continue
        names = re.findall(r"\bfn\s+(\w*private_request\w*)", _rust_code(path.read_text(encoding="utf-8")))
        for name in names:
            if name not in domains.get(exchange, {}).get(relative, []):
                dispatch_files.add(relative)
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
    assert_test_modules_declared(native)
    assert not (native / "tests/route_coverage.rs").exists()


def assert_test_modules_declared(native):
    for path in (native / "tests").rglob("*.rs"):
        relative = path.relative_to(native / "tests")
        if relative.name == "mod.rs":
            module = relative.parent.name
            parent = path.parent.parent
        else:
            module = relative.stem
            parent = path.parent
        declaration = parent.with_suffix(".rs")
        if not declaration.is_file():
            declaration = parent / "mod.rs"
        assert declaration.is_file(), path
        assert re.search(r"\bmod\s+" + re.escape(module) + r"\s*;", _rust_code(declaration.read_text(encoding="utf-8"))), path


def test_nested_test_file_requires_parent_declaration(tmp_path):
    (tmp_path / "tests/sub").mkdir(parents=True)
    (tmp_path / "tests.rs").write_text("mod sub;", encoding="utf-8")
    (tmp_path / "tests/sub.rs").write_text("", encoding="utf-8")
    (tmp_path / "tests/sub/x.rs").write_text("fn sample() {}", encoding="utf-8")
    with pytest.raises(AssertionError):
        assert_test_modules_declared(tmp_path)
    (tmp_path / "tests/sub.rs").write_text("mod x;", encoding="utf-8")
    assert_test_modules_declared(tmp_path)


@pytest.mark.parametrize("name", ["private_request_inner", "signed_private_request"])
def test_private_dispatch_name_variants_are_detected(name):
    assert re.search(r"\bfn\s+\w*private_request\w*", f"async fn {name}() {{}}")


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
