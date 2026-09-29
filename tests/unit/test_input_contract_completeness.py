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
            missing.extend((exchange, *item) for item in missing_declarations(path.read_text(encoding="utf-8"), methods, exemptions.get(exchange, {}), exchange))
    assert not missing, missing


@pytest.mark.parametrize("parameter", ["new_amount: str", "trailing_ratio: str", "lever: str", "slippagePct: str", "orders: list[dict]", "take_profit: str", "takeProfit: str", "stopLoss: str", "lossReserve: str", "stop_loss: str", "tp: str", "sl: str", "trigger: str", "trail: str", "cost: str", "budget: str", "premium: str", "value: str"])
def test_adding_an_undeclared_numeric_or_batch_parameter_fails(parameter):
    source = f"class Trade:\n def place_order(self, {parameter}, **params): pass\n"
    assert missing_declarations(source, {"place_order": {"type": "object", "properties": {}}}, {}) == [("place_order", parameter.split(":")[0])]


def test_new_variadic_operation_requires_a_declaration():
    assert missing_declarations("class Trade:\n def withdraw_new(self, **params): pass\n", {}, {}) == [("withdraw_new", "<method>")]


def test_numeric_exemption_cannot_disable_decimal_review():
    source = "class Trade:\n def add_margin(self, margin: str): pass\n"
    with pytest.raises(AssertionError):
        missing_declarations(source, {}, {"add_margin/margin": "add_margin/margin: this string is deliberately described as a nonfinancial selector"})


def test_boilerplate_exemption_reason_is_rejected():
    with pytest.raises(AssertionError):
        missing_declarations("class Trade:\n def get_orders(self, page_size: int): pass\n", {}, {"get_orders/page_size": "Integer pagination control; not a financial decimal"})


@pytest.mark.parametrize("field", ["price", "base_amount", "usdc_amount", "trigger_price", "integrator_taker_fee", "integrator_maker_fee", "amount", "share_amount", "operator_fee"])
def test_lighter_scaled_financial_integers_cannot_be_exempted(field):
    source = f"class Client:\n def create_order(self, {field}: int): pass\n"
    identity = f"create_order/{field}"
    with pytest.raises(AssertionError):
        missing_declarations(source, {"create_order": {"properties": {}}}, {identity: f"{identity}: a seemingly plausible description with at least eight distinct words"}, "lighter")


def test_repeated_reasons_are_rejected_after_removing_identity():
    from tests.unit.input_contract_coverage import validate_exemptions
    with pytest.raises(AssertionError):
        validate_exemptions({f"m{i}/page_size": f"m{i}/page_size: limits the number of result records returned by this endpoint" for i in range(5)})


def test_method_prefixes_and_field_tokens_cannot_hide_repeated_reasons():
    from tests.unit.input_contract_coverage import validate_exemptions
    with pytest.raises(AssertionError):
        validate_exemptions({f"m{i}/field{i}": f"m{i}/field{i}: For m{i}, field{i} identifies existing requests without order quantities" for i in range(5)})


@pytest.mark.parametrize("method,field", [("mint_shares", "share_amount"), ("create_public_pool", "operator_fee")])
def test_lighter_pool_financial_fields_cannot_be_exempted(method, field):
    identity = f"{method}/{field}"
    source = f"class Client:\n def {method}(self, {field}: int): pass\n"
    with pytest.raises(AssertionError):
        missing_declarations(source, {method: {"properties": {}}}, {identity: f"{identity}: integer control described with several distinct words to conceal missing financial coverage"}, "lighter")
