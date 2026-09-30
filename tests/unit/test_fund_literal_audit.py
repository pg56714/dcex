"""Fund statement pins and obfuscated dispatch mutation coverage."""

import json
from collections import Counter

import pytest

from scripts import fund_literal_audit as audit
from tests.unit.input_contract_coverage import MAX_REASON_REPETITIONS, normalized_reason

MUTATIONS = [
    'const W: &str = concat!("create_with", "drawal3"); self.call(W);',
    'const W: &str = "create_with\\\ndrawal3"; self.call(W);',
    'let name = String::from_utf8(vec![99, 114, 101, 97, 116, 101]).unwrap(); self.call(&name);',
    'match name { "get_account_extra" => self.signed_call("POST", "/sapi/v1/capital/withdraw/apply", p) }',
]


@pytest.mark.parametrize("relative", [
    "crates/dcex/src/exchanges/binance/account.rs",
    "crates/dcex/src/exchanges/schema.rs",
    "crates/dcex/src/exchanges/mod.rs",
    "crates/dcex/src/ws/connection.rs",
    "crates/dcex-python/src/lib.rs",
])
@pytest.mark.parametrize("mutation", MUTATIONS)
def test_obfuscated_fund_dispatch_is_found_in_all_production_roots(tmp_path, relative, mutation):
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text(mutation, encoding="utf8")
    observed = audit.inventory(tmp_path)
    assert observed and all(entry["source"] == relative for entry in observed)


def test_pin_covers_the_surrounding_arm_and_ignores_unrelated_statements():
    source = 'match name { "withdraw_all" => self.owner(p), "ping" => pong() }'
    entry, = audit.occurrences(source, "account.rs")
    changed, = audit.occurrences(source.replace('self.owner(p)', 'self.owner(p); self.post(p)'), "account.rs")
    assert entry["sha256"] != changed["sha256"]
    assert list(audit.occurrences(source.replace('pong()', 'other()'), "account.rs")) == [entry]


def test_macro_pins_only_the_complete_wrapper_entry():
    source = 'private [ get_info(), send(transfer_type => "transferType", amount => "amount"), get_other() ];'
    entry, = audit.occurrences(source, "account.rs")
    assert entry["context"] == 'send(transfer_type => "transferType", amount => "amount"),'
    assert list(audit.occurrences(source.replace('get_info()', 'new_info()'), "account.rs")) == [entry]
    assert list(audit.occurrences(source.replace('amount =>', 'quantity =>'), "account.rs")) != [entry]


def test_exception_writer_never_auto_approves_or_replaces_reasons():
    occurrence, = audit.occurrences('const W: &str = "withdraw_all";', "account.rs")
    entry = {"source": "account.rs", **occurrence, "reason": "Delegates to the withdrawal owner."}
    observed = [entry]
    assert audit.approved_update([], {}, observed) == []
    assert audit.approved_update([], {"add": [entry]}, observed) == [entry]
    with pytest.raises(ValueError, match="cannot be overwritten"):
        audit.approved_update([entry], {"add": [entry | {"reason": "Changed reason"}]}, observed)
    with pytest.raises(ValueError, match="current statement hash"):
        audit.approved_update([], {"add": [entry | {"sha256": "wrong"}]}, observed)
    with pytest.raises(ValueError, match="exact existing"):
        audit.approved_update([entry], {"remove": [entry | {"reason": "wrong"}]}, observed)


def test_existing_exception_reasons_are_specific_and_generated_files_are_not_pinned():
    entries = json.loads(audit.ALLOWLIST.read_text(encoding="utf8"))
    identities = [part for entry in entries for part in [entry["source"], entry["name"]]]
    reasons = Counter(normalized_reason(entry["reason"], identities) for entry in entries)
    assert max(reasons.values()) <= MAX_REASON_REPETITIONS, reasons
    assert all("/generated/" not in entry["source"] for entry in entries)
    assert len({audit.identity(entry) for entry in entries}) == len(entries)


def test_check_mode_is_read_only_and_catches_unapproved_mutation(tmp_path, monkeypatch):
    import sys
    allowance = tmp_path / "pins.json"
    allowance.write_text("[]\n", encoding="utf8")
    before = allowance.read_bytes(), allowance.stat().st_mtime_ns
    monkeypatch.setattr(audit, "ALLOWLIST", allowance)
    monkeypatch.setattr(audit, "inventory", lambda: [{"source": "account.rs", **next(audit.occurrences(MUTATIONS[0], "account.rs"))}])
    monkeypatch.setattr(sys, "argv", ["audit", "--check"])
    monkeypatch.setattr(type(allowance), "write_text", lambda *a, **k: pytest.fail("check mode wrote a file"))
    assert audit.main() == 1
    assert (allowance.read_bytes(), allowance.stat().st_mtime_ns) == before


def test_test_only_blocks_do_not_hide_later_production_code():
    source = '#[cfg(test)] mod tests { const W: &str = "withdraw_test"; } const W: &str = "withdraw_real";'
    assert [entry["name"] for entry in audit.occurrences(source, "account.rs")] == ["withdraw_real"]

def test_generated_schema_inputs_cannot_add_an_unowned_fund_operation(tmp_path, monkeypatch):
    from tests.unit import test_fund_dispatch_ownership as ownership
    schema = tmp_path / "binance/schemas/new_funds.json"
    schema.parent.mkdir(parents=True)
    schema.write_text(json.dumps([{"name": "create_withdrawal_unowned", "path": "/withdraw"}]), encoding="utf8")
    monkeypatch.setattr(ownership, "NATIVE", tmp_path)
    with pytest.raises(AssertionError, match="create_withdrawal_unowned"):
        ownership.test_fund_schema_operations_have_actual_owner_routes("binance")
