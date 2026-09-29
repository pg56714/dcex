"""New public numeric parameters must never bypass the declaration review."""

import json
from pathlib import Path

import pytest

from dcex._input_codec import CATALOG
from tests.unit.input_contract_coverage import missing_declarations

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST = ROOT / "tests/fixtures/input_contract_exemptions.json"


@pytest.mark.parametrize("prefix", ["dcex", "dcex/async_support"])
def test_all_public_numeric_and_structured_inputs_are_declared(prefix):
    exemptions = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    missing = []
    for exchange, methods in CATALOG["exchanges"].items():
        for path in (ROOT / prefix / exchange).rglob("*.py"):
            missing.extend((exchange, *item) for item in missing_declarations(path.read_text(encoding="utf-8"), methods, exemptions.get(exchange, {})))
    assert not missing, missing


@pytest.mark.parametrize("parameter", ["new_amount: str", "trailing_ratio: str", "lever: str", "slippagePct: str", "orders: list[dict]"])
def test_adding_an_undeclared_numeric_or_batch_parameter_fails(parameter):
    source = f"class Trade:\n def place_order(self, {parameter}, **params): pass\n"
    assert missing_declarations(source, {"place_order": {"type": "object", "properties": {}}}, {}) == [("place_order", parameter.split(":")[0])]


def test_new_variadic_operation_requires_a_declaration():
    assert missing_declarations("class Trade:\n def withdraw_new(self, **params): pass\n", {}, {}) == [("withdraw_new", "<method>")]
