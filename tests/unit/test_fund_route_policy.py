"""Nonliteral transport routes fail closed, independent of string construction."""

import json

import pytest

from scripts import fund_literal_audit as audit

ASSEMBLIES = [
    'const A: &str = "create_with"; const B: &str = "drawal3"; let s = format!("{A}{B}");',
    'const A: &str = "create_with"; const B: &str = "drawal3"; let s = [A,B].concat();',
    'let s: String = [99u8,114].into_iter().map(char::from).collect();',
    'let mut s = String::new(); write!(s, "{}{}", "create_with", "drawal3");',
    'let mut s = String::new(); s.extend([99u8,114].map(char::from));',
    'let mut s = String::new(); s.insert_str(0, "create_with"); s.insert_str(11,"drawal3");',
    'let s = "create_withdrXX".replace("XX", "awal3");',
    'let s = format!("/sapi/v1/capital/withdra{}", "w/apply");',
    'let s = ["create_w", "ithd", "rawal3"].concat();',
    'fn piece() -> String { external_piece() } let s = piece();',
]


@pytest.mark.parametrize('assembly', ASSEMBLIES)
@pytest.mark.parametrize('call', ['self.signed_call("POST", &s, p)', 'self.private_request(&s, p)', 'self.submit_action(s, p)'])
def test_dynamic_route_construction_mutations_fail(tmp_path, assembly, call):
    source = f'fn dispatch() {{ {assembly} {call}; }}'
    path = tmp_path / 'crates/dcex/src/exchanges/example/account.rs'
    path.parent.mkdir(parents=True)
    assert not audit.route_policy_violations(tmp_path)
    path.write_text(source, encoding='utf8')
    assert audit.route_policy_violations(tmp_path)


@pytest.mark.parametrize('relative', ['crates/dcex/src/ws/withdrawals.rs', 'crates/dcex-python/src/transfers.rs', 'crates/dcex/src/exchanges/example/nested/withdrawals.rs'])
def test_dynamic_routes_cannot_hide_in_decoy_owner_files(tmp_path, relative):
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text('fn f() { self.private_request(helper(), p); }')
    assert audit.route_policy_violations(tmp_path)


def test_literal_routes_and_exact_owner_files_are_allowed(tmp_path):
    folder = tmp_path / 'crates/dcex/src/exchanges/example'
    folder.mkdir(parents=True)
    (folder / 'account.rs').write_text('fn f() { self.signed_call("POST", r#"/orders"#, p); }')
    for owner in ['withdrawals', 'transfers']:
        (folder / f'{owner}.rs').write_text('fn f() { self.private_request(helper(), p); }')
    assert not audit.route_policy_violations(tmp_path)


def test_repository_transport_routes_are_literal_or_exactly_pinned():
    assert not audit.route_policy_violations()


@pytest.mark.parametrize('action', ['usdSend', 'spotSend', 'sendAsset', 'sendToEvm'])
def test_neutral_schema_name_cannot_hide_fund_action(action):
    from tests.unit.test_fund_dispatch_ownership import schema_path_violations
    row = {'name': 'get_account_extra', 'type': action, 'signed': True, 'public': False}
    assert schema_path_violations([row], 'hyperliquid/schemas/account.json', []) == ['get_account_extra']


def test_route_policy_is_checked_by_audit_cli(tmp_path, monkeypatch):
    import sys
    pins = tmp_path / 'literals.json'
    pins.write_text('[]')
    monkeypatch.setattr(audit, 'ALLOWLIST', pins)
    monkeypatch.setattr(audit, 'inventory', lambda: [])
    monkeypatch.setattr(audit, 'route_policy_violations', lambda: ['nonliteral route'])
    monkeypatch.setattr(sys, 'argv', ['audit', '--check'])
    before = pins.read_bytes(), pins.stat().st_mtime_ns
    assert audit.main() == 1
    assert before == (pins.read_bytes(), pins.stat().st_mtime_ns)


@pytest.mark.parametrize('call', [
    'let f = Client::signed_call; f(client, "POST", helper(), p);',
    'self.private_request::<String>(helper(), p);',
    'private_post! { helper(), p }',
    'Client::private_request(client, helper(), p);',
])
def test_indirect_transport_mutations_fail(tmp_path, call):
    path = tmp_path / 'crates/dcex/src/exchanges/example/account.rs'
    path.parent.mkdir(parents=True)
    path.write_text('fn f() { ' + call + ' }')
    assert audit.route_policy_violations(tmp_path)


@pytest.mark.parametrize('change', ['call', 'constant', 'helper', 'pin'])
def test_existing_router_approval_is_invalidated_by_mutation(tmp_path, change):
    from scripts import fund_routes
    folder = tmp_path / 'crates/dcex/src/exchanges/example'
    folder.mkdir(parents=True)
    caller = folder / 'account.rs'
    caller.write_text('fn route() { self.private_request(NAME, p); }')
    helper = folder / 'constants.rs'
    helper.write_text('const NAME: &str = "orders"; fn helper() { original(); }')
    entries = fund_routes.inventory(tmp_path)
    for entry in entries:
        entry['reason'] = 'Fixture with an explicitly fixed operation and helper.'
    pins = tmp_path / 'tests/fixtures/fund_dynamic_routes.json'
    pins.parent.mkdir(parents=True)
    pins.write_text(json.dumps(entries))
    assert not audit.route_policy_violations(tmp_path)
    if change == 'call':
        caller.write_text(caller.read_text() + '\nfn added() { self.private_request(helper(), p); }')
    elif change == 'constant':
        helper.write_text(helper.read_text().replace('"orders"', 'concat!("usd", "Send")'))
    elif change == 'helper':
        helper.write_text(helper.read_text().replace('original()', 'different()'))
    else:
        entries[0]['reason'] = ''
        pins.write_text(json.dumps(entries))
    assert audit.route_policy_violations(tmp_path)
