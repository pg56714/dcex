"""Dispatch names, including newly introduced names, determine fund ownership."""

import importlib
import inspect
import json
import re
from pathlib import Path

import pytest

from tests.unit.rust_dispatch import mask, misplaced_fund_arms
from tests.unit.test_exchange_structure import EXCHANGES, NATIVE, ROOT


@pytest.mark.parametrize("exchange", EXCHANGES)
def test_all_fund_dispatch_arms_have_domain_owners(exchange):
    folder = NATIVE / exchange
    owners = {}
    for domain in ["withdrawals", "transfers"]:
        path = folder / f"{domain}.rs"
        owners[domain] = set(re.findall(r"\bfn\s+(\w+)", mask(path.read_text(encoding="utf-8")))) if path.exists() else set()
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
    recipient_transfers = {"transfer_master_internal", "transfer_sub_account_internal", "transfer_l2_account", "sign_transfer_l2_account", "transfer_same_master_account", "sign_transfer_same_master_account"}
    for name, function in inspect.getmembers(cls, callable):
        if name.startswith("_") or not re.search("withdraw|transfer", name):
            continue
        domain = "withdrawals" if "withdraw" in name or name in recipient_transfers else "transfers"
        path = Path(inspect.getsourcefile(inspect.unwrap(function)))
        assert path.name.lstrip("_") == f"{domain}_http.py", (exchange, name, path)


def test_arcus_withdrawal_dispatch_is_explicit():
    source = (NATIVE / "arcus/private.rs").read_text(encoding="utf-8")
    for name in ["create_withdrawal", "create_withdrawal_signed"]:
        assert f'"{name}"' in source
    assert "withdrawal_schema_request" in source
    assert "fn withdrawal_schema_request" in (NATIVE / "arcus/withdrawals.rs").read_text(encoding="utf-8")
