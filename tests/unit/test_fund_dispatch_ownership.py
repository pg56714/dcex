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
    delegates = {name for route in catalog_routes() if route["exchange"] == exchange for name in [route["method"], route["transport"]]}
    owners = {}
    for domain in ["withdrawals", "transfers"]:
        path = folder / f"{domain}.rs"
        owners[domain] = request_owners(path.read_text(encoding="utf-8"), delegates) if path.exists() else set()
    readonly = json.loads((ROOT / "tests/fixtures/fund_readonly_dispatch.json").read_text(encoding="utf-8")).get(exchange, {})
    for path in folder.rglob("*.rs"):
        if "tests" in path.relative_to(folder).parts:
            continue
        nondispatch = [entry for entry in json.loads((ROOT / "tests/fixtures/fund_nondispatch_arms.json").read_text(encoding="utf-8")) if entry["source"] == path.relative_to(NATIVE).as_posix()]
        assert not misplaced_fund_arms(path.read_text(encoding="utf-8"), path.name, owners, readonly, nondispatch), path


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


def catalog_routes():
    return json.loads((ROOT / "tests/fixtures/fund_catalog_dispatch.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("route", catalog_routes(), ids=lambda route: route["exchange"] + "/" + route["method"])
def test_catalog_dispatch_must_route_funds_through_domain_owner(route):
    from tests.unit.rust_dispatch import functions
    folder = NATIVE / route["exchange"]
    source = (folder / route["source"]).read_text(encoding="utf-8")
    router = dict(functions(source))[route["method"]]
    assert "schema::fund_domain(" in router
    assert re.search(r"None\s*=>\s*\{?\s*self\." + route["transport"], router)
    for domain, variant in [("withdrawals", "Withdrawals"), ("transfers", "Transfers")]:
        owner = domain + "_" + route["method"]
        assert f"FundDomain::{variant}) =>" in router and f"self.{owner}(" in router
        body = dict(functions((folder / (domain + ".rs")).read_text(encoding="utf-8")))[owner]
        assert "schema::fund_domain(" in body and f"FundDomain::{variant}" in body
        assert f"self.{route['transport']}(" in body


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_fund_schema_operations_have_actual_owner_routes(exchange):
    folder = NATIVE / exchange
    routed = {row["source"] for row in catalog_routes() if row["exchange"] == exchange}
    supported = set()
    pending = set()
    for path in (folder / "schemas").glob("*.json"):
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        names = {row["name"] for row in rows if fund_domain(row.get("name", ""))}
        pending |= names
        for loader in folder.rglob("*.rs"):
            if "tests" in loader.parts:
                continue
            source = loader.read_text(encoding="utf-8")
            if f"schemas/{path.name}\"" not in source:
                continue
            relative = loader.relative_to(folder).as_posix()
            if loader.name in {"withdrawals.rs", "transfers.rs"} or relative in routed or relative == "generated/schema_tables.rs" and "schema_requests.rs" in routed:
                supported |= names
    assert not pending - supported, (exchange, sorted(pending - supported))
    assert not (ROOT / "tests/fixtures/fund_schema_exceptions.json").exists()


@pytest.mark.parametrize("source", [
    'match name { "create_withdrawal3" => Box::pin(self.signed_call("POST", "/api/v3/withdrawals", p)) }',
    'match name { "create_withdrawal3" => { self.withdrawal_request(m,p); self.transport.execute(req).await } }',
    'match name { "create_withdrawal3" => { self.withdrawal_request(m,p); private_post!(req) } }',
    'match name { "create_withdrawal3" => { self.withdrawal_request(m,p); self.transport.get(req).await } }',
    'match name { "create_withdrawal3" => { self.withdrawal_request(m,p); private_post! { req } } }',
    'if "create_withdrawal3" == name { self.signed_call(p) }',
    'if name == "a" || name == "create_withdrawal3" { self.signed_call(p) }',
    'if name.contains("withdraw") { self.signed_call(p) }',
    'if matches!(name, "create_withdrawal3") { self.signed_call(p) }',
    'match name { "create_withdrawal3" => ("POST", "/api/v3/withdrawals") }',
    'match name { "create_withdrawal3" => Some(Route { method: "POST", path: "/withdraw" }) }',
])
def test_round_seven_fund_dispatch_bypass_mutations(source):
    assert misplaced_fund_arms(source, "account.rs", {"withdrawals": {"withdrawal_request"}}, {})


def test_nondispatch_allowance_is_invalidated_by_added_sender():
    import hashlib
    body = 'validate(params);'
    entry = {"names": ["create_withdrawal3"], "sha256": hashlib.sha256(body.encode()).hexdigest()}
    clean = f'match name {{ "create_withdrawal3" => {body} }}'
    assert not misplaced_fund_arms(clean, "account.rs", {}, {}, [entry])
    mutated = clean.replace(body, '{ validate(params); self.transport.execute(req).await }')
    assert misplaced_fund_arms(mutated, "account.rs", {}, {}, [entry])


def test_await_and_transport_suffix_do_not_create_unlisted_owners():
    assert request_owners("async fn sign_only() { self.next_nonce().await } async fn decoy() { self.unknown_transport().await } fn route_only() { let method = HttpMethod::Post; }") == set()
