"""Dispatch names, including newly introduced names, determine fund ownership."""

import importlib
import hashlib
import inspect
import json
import re
from pathlib import Path

import pytest

from tests.unit.rust_dispatch import (
    fund_domain,
    misplaced_fund_arms,
    request_owners,
    unauthorized_transport_references,
    unpinned_fund_literals,
)
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


def test_every_fund_literal_outside_owners_is_statement_pinned():
    from scripts.fund_literal_audit import identity, inventory
    allowances = json.loads((ROOT / "tests/fixtures/fund_literal_allowlist.json").read_text(encoding="utf-8"))
    assert {identity(entry) for entry in inventory()} == {identity(entry) for entry in allowances}


@pytest.mark.parametrize("source", [
    'const W: &str = "create_withdrawal3"; match name { W => self.signed_call(p) }',
    'match (name, 1) { ("create_withdrawal3", _) => self.signed_call(p) }',
    'match name { "create_withdrawal3" /* comment */ => self.signed_call(p) }',
    'match name { "create_withdrawal" if !public => self.signed_call("POST", "/w", p).await }',
    'static T: &[(&str, &str)] = &[("create_withdrawal3", "/api/v3/withdrawals")]; T.iter().find(|r| r.0 == name)',
    r'const W: &str = "create_with\u{64}rawal3"; call(W);',
])
def test_fund_literal_mutations_cannot_depend_on_dispatch_syntax(source):
    from scripts.fund_literal_audit import occurrences
    assert unpinned_fund_literals(source, "account.rs")
    allowances = list(occurrences(source, "account.rs"))
    assert not unpinned_fund_literals(source, "account.rs", allowances)
    assert unpinned_fund_literals(source.replace("create_with", "create_another_with"), "account.rs", allowances)
    # An unrelated statement does not require re-approving existing exceptions.
    assert not unpinned_fund_literals(source + '; log_status();', "account.rs", allowances)


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
        assert "debug_assert!" not in body and "return Err(" in body
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
        exceptions = json.loads((ROOT / "tests/fixtures/fund_schema_path_exceptions.json").read_text(encoding="utf8"))
        assert not schema_path_violations(rows, path.relative_to(NATIVE).as_posix(), exceptions)
        names = {row["name"] for row in rows if fund_domain(row.get("name", ""))}
        pending |= names
        for loader in folder.rglob("*.rs"):
            if "tests" in loader.parts:
                continue
            source = loader.read_text(encoding="utf-8")
            if f"schemas/{path.name}\"" not in source:
                continue
            relative = loader.relative_to(folder).as_posix()
            if relative in {"withdrawals.rs", "transfers.rs"} or relative in routed or relative == "generated/schema_tables.rs" and "schema_requests.rs" in routed:
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
def test_fund_dispatch_inline_sender_mutations(source):
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


@pytest.mark.parametrize("route", catalog_routes())
def test_schema_transports_have_only_audited_callers(route):
    for path in (NATIVE / route["exchange"]).rglob("*.rs"):
        if "tests" in path.parts:
            continue
        relative = path.relative_to(NATIVE / route["exchange"]).as_posix()
        permitted = [route["method"]] if relative == route["source"] else []
        if path.name in {"withdrawals.rs", "transfers.rs"}:
            permitted.append(path.stem + "_" + route["method"])
        assert not unauthorized_transport_references(path.read_text(encoding="utf-8"), route["transport"], permitted, impl_owner=route["exchange"].capitalize() + "Client", allow_definition=relative == route["source"]), (path, route)


@pytest.mark.parametrize("transport", ["table_request_transport", "catalog_request_transport", "field_schema_request_transport"])
def test_direct_schema_transport_call_mutation_is_rejected(transport):
    source = f'async fn account(&self) {{ self.{transport}("fiat_withdraw", p, false).await }}'
    assert unauthorized_transport_references(source, transport, ["table_request", "withdrawals_table_request"])


def test_nondispatch_allowance_reasons_are_specific():
    from collections import Counter

    from tests.unit.input_contract_coverage import MAX_REASON_REPETITIONS, normalized_reason
    entries = json.loads((ROOT / "tests/fixtures/fund_nondispatch_arms.json").read_text(encoding="utf-8"))
    identities = [name for entry in entries for name in entry["names"]]
    reasons = Counter(normalized_reason(entry["reason"], identities) for entry in entries)
    assert all(count <= MAX_REASON_REPETITIONS for count in reasons.values()), reasons


@pytest.mark.parametrize("transport", ["table_request_transport", "catalog_request_transport", "field_schema_request_transport"])
def test_same_named_transport_in_foreign_impl_cannot_bypass_guard(transport):
    source = f"struct H; impl H {{ async fn {transport}(&self, c: &BinanceClient) {{ c.{transport}(n, p, false).await }} }}"
    assert unauthorized_transport_references(source, transport, [], impl_owner="BinanceClient")
    assert unauthorized_transport_references(source, transport, [], impl_owner="BinanceClient", allow_definition=True)
    legitimate = source.replace("impl H", "impl BinanceClient")
    assert unauthorized_transport_references(legitimate, transport, [], impl_owner="BinanceClient")
    assert not unauthorized_transport_references(legitimate, transport, [], impl_owner="BinanceClient", allow_definition=True)


def schema_row_hash(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def schema_path_violations(rows, source, exceptions):
    return [row["name"] for row in rows if fund_domain(row.get("path", "")) and not fund_domain(row.get("name", "")) and not any(e["source"] == source and e["name"] == row["name"] and e["sha256"] == schema_row_hash(row) and e["reason"].strip() for e in exceptions)]


def test_schema_path_exceptions_pin_exact_rows_and_reject_mutations():
    from tests.unit.input_contract_coverage import normalized_reason, MAX_REASON_REPETITIONS
    from collections import Counter
    exceptions = json.loads((ROOT / "tests/fixtures/fund_schema_path_exceptions.json").read_text(encoding="utf8"))
    assert len({(e['source'],e['name']) for e in exceptions}) == len(exceptions)
    assert max(Counter(normalized_reason(e['reason'], [e['name']]) for e in exceptions).values()) <= MAX_REASON_REPETITIONS
    for entry in exceptions:
        rows = json.loads((NATIVE / entry['source']).read_text(encoding="utf8"))
        row, = [row for row in rows if row['name'] == entry['name']]
        assert schema_row_hash(row) == entry['sha256']
        assert not schema_path_violations([row], entry['source'], exceptions)
        changed = row | {'path': '/sapi/v1/capital/withdraw/apply'}
        assert schema_path_violations([changed], entry['source'], exceptions) == [row['name']]
        assert schema_path_violations([row], 'other/schemas/fake.json', exceptions) == [row['name']]
