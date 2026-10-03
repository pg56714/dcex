"""Positive quantities and documented sentinels remain endpoint-specific."""

import pytest

from dcex._input_codec import CATALOG, normalize


@pytest.mark.parametrize(
    "exchange,method,field",
    [
        ("bitget", "transfer_uta_account", "amount"),
        ("okx", "funds_transfer", "amt"),
        ("okx", "amend_order", "newSz"),
        ("okx", "set_leverage", "lever"),
        ("bybit", "set_leverage", "leverage"),
        ("kraken", "place_futures_order", "size"),
        ("mexc", "place_contract_order", "vol"),
        ("mexc", "place_spot_order", "quoteOrderQty"),
    ],
)
def test_audited_positive_fields_reject_zero(exchange, method, field):
    schema = CATALOG["exchanges"][exchange][method]
    for value in ["0", "0.000", 0]:
        with pytest.raises(ValueError):
            normalize({field: value}, schema=schema)
    assert normalize({field: "1.125"}, schema=schema) == {field: "1.125"}


def test_aster_offset_aliases_have_identical_signed_rules():
    properties = CATALOG["exchanges"]["aster"]["place_futures_order"]["properties"]
    assert properties["peg_offset"] == properties["pegOffset"]


def test_bybit_margin_is_explicitly_signed():
    schema = CATALOG["exchanges"]["bybit"]["add_position_margin"]
    assert normalize({"margin": "-0.125"}, schema=schema) == {"margin": "-0.125"}
    with pytest.raises(ValueError):
        normalize({"margin": 0.1}, schema=schema)
