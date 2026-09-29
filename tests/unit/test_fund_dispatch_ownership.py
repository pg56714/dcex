"""Dispatch names, including newly introduced names, determine fund ownership."""

import importlib
import inspect
import json
import re
from pathlib import Path

import pytest

from tests.unit.rust_dispatch import fund_domain, misplaced_fund_arms, request_owners
from tests.unit.test_exchange_structure import EXCHANGES, NATIVE, ROOT


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_all_fund_dispatch_arms_have_domain_owners(exchange):
    folder = NATIVE / exchange
    owners = {}
    for domain in ["withdrawals", "transfers"]:
        path = folder / f"{domain}.rs"
        owners[domain] = request_owners(path.read_text(encoding="utf-8")) if path.exists() else set()
    readonly = json.loads((ROOT / "tests/fixtures/fund_readonly_dispatch.json").read_text(encoding="utf-8")).get(exchange, {})
    for path in folder.rglob("*.rs"):
        if "tests" in path.relative_to(folder).parts:
            continue
        assert not misplaced_fund_arms(path.read_text(encoding="utf-8"), path.name, owners, readonly), path


def test_new_withdrawal_arm_cannot_hide_in_account():
    source = 'match name { "create_withdrawal2" => post("/api/v1/user/withdrawal"), _ => None }'
    assert misplaced_fund_arms(source, "account.rs", {}, {}) == ["create_withdrawal2"]
    assert not misplaced_fund_arms(source, "withdrawals.rs", {}, {})
    delegated = 'match name { "create_withdrawal2" => self.withdrawal_request(params).await, _ => None }'
    assert not misplaced_fund_arms(delegated, "account.rs", {"withdrawals": {"withdrawal_request"}}, {})


@pytest.mark.parametrize("prefix", ["dcex", "dcex.async_support"])
@pytest.mark.parametrize("exchange", EXCHANGES)
def test_all_python_fund_methods_have_domain_owners(prefix, exchange):
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    readonly = json.loads((ROOT / "tests/fixtures/fund_readonly_dispatch.json").read_text(encoding="utf-8")).get(exchange, {})
    for name, function in inspect.getmembers(cls, callable):
        domain = fund_domain(name)
        if name.startswith("_") or domain is None or name in readonly:
            continue
        path = Path(inspect.getsourcefile(inspect.unwrap(function)))
        assert path.name.lstrip("_") == f"{domain}_http.py", (exchange, name, path)


def test_arcus_withdrawal_dispatch_is_explicit():
    source = (NATIVE / "arcus/private.rs").read_text(encoding="utf-8")
    for name in ["create_withdrawal", "create_withdrawal_signed"]:
        assert f'"{name}"' in source
    assert "withdrawal_schema_request" in source
    assert "fn withdrawal_schema_request" in (NATIVE / "arcus/withdrawals.rs").read_text(encoding="utf-8")


@pytest.mark.parametrize("body", [
    'return Err(invalid("x")); private_post("/withdraw").await',
    'validate_withdrawal(params); private_post("/withdraw").await',
    'withdrawal_request(params).await; private_post("/withdraw").await',
])
def test_validation_or_delegation_cannot_hide_inline_sending(body):
    owners = request_owners('fn invalid() { Err(error) } fn validate_withdrawal() { Ok(()) } async fn withdrawal_request() { post("/withdraw").await }')
    assert owners == {"withdrawal_request"}
    assert misplaced_fund_arms(f'match name {{ "withdraw_all" => {{ {body} }} }}', "account.rs", {"withdrawals": owners}, {}) == ["withdraw_all"]


@pytest.mark.parametrize("source,name", [
    ('if name == "create_withdrawal2" { private_post("/withdraw").await }', "create_withdrawal2"),
    ('match name { "withdraw_all" => Some(("POST", "/withdraw")) }', "withdraw_all"),
    ('match name { "send_asset_signed" => post("/exchange") }', "send_asset_signed"),
    ('match name { "commit_bridge_quote" => post("/bridge") }', "commit_bridge_quote"),
])
def test_other_dispatch_forms_and_fund_names_are_governed(source, name):
    assert misplaced_fund_arms(source, "account.rs", {}, {}) == [name]


def misplaced_schema_operations(filename, rows, exceptions):
    return [row["name"] for row in rows if fund_domain(row.get("name", "")) and not filename.startswith("table_" + fund_domain(row["name"])) and f'{filename}/{row["name"]}' not in exceptions]


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_fund_schema_operations_have_named_ownership(exchange):
    exceptions = json.loads((ROOT / "tests/fixtures/fund_schema_exceptions.json").read_text(encoding="utf-8")).get(exchange, {})
    seen = set()
    for path in (NATIVE / exchange / "schemas").glob("*.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        assert not misplaced_schema_operations(path.name, rows, exceptions), path
        seen.update(f'{path.name}/{row["name"]}' for row in rows if "name" in row)
    assert set(exceptions) <= seen
    assert all(len(set(reason.split())) >= 8 for reason in exceptions.values())


def test_new_schema_fund_operation_requires_domain_or_named_exception():
    rows = [{"name": "create_new_withdrawal"}]
    assert misplaced_schema_operations("broker.json", rows, {}) == ["create_new_withdrawal"]
    assert not misplaced_schema_operations("table_withdrawals.json", rows, {})
