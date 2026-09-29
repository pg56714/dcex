"""Wire completeness cannot be disabled by descriptions or control labels."""

from copy import deepcopy

import pytest

from tests.unit.input_contract_coverage import missing_wire_declarations
from tests.unit.wire_contracts import CATALOG, CONTROLS, assert_wire_contract


def test_descriptions_do_not_exempt_financial_wire_fields():
    assert missing_wire_declarations({"price": "1"}, {"properties": {"price": {"description": "not a decimal"}}}) == [("price",)]


def test_control_inventory_does_not_contain_amounts_or_prices():
    financial = {"price", "px", "qty", "quantity", "amount", "amt", "size", "sz", "volume", "margin", "baseamount", "usdcamount", "triggerprice", "fee", "leverage"}
    for endpoint, controls in CONTROLS.items():
        for path, control in controls.items():
            assert path.split("/")[-1].replace("_", "").lower() not in financial, (endpoint, path)
            assert control["reason"] and control["values"]


@pytest.mark.parametrize("exchange", list(CATALOG["exchanges"]))
def test_new_wire_numeric_field_is_checked_on_every_exchange(exchange):
    with pytest.raises(AssertionError):
        assert_wire_contract(exchange, "new_endpoint", {"body": '{"takeProfit":"1"}'})


def test_wrong_declared_name_fails_through_capture_adapter(monkeypatch):
    contract = deepcopy(CATALOG["exchanges"]["okx"]["amend_order"])
    fields = contract["properties"]["attachAlgoOrds"]["items"]["properties"]
    fields["wrong_sz"] = fields.pop("sz")
    monkeypatch.setitem(CATALOG["exchanges"]["okx"], "amend_order", contract)
    with pytest.raises(AssertionError):
        assert_wire_contract("okx", "amend_order", {"body": '{"attachAlgoOrds":[{"sz":"1"}]}'})
