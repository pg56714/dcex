"""Audited positive, signed and structured declaration regressions."""

from decimal import Decimal

import pytest

from dcex._input_codec import CATALOG, normalize


@pytest.mark.parametrize("exchange,method,key", [
    ("okx", "trading_bot_grid_amend_order_algo", "top_up_amt"),
    ("okx", "trading_bot_signal_order_algo", "invest_amt"),
    ("okx", "copytrading_first_copy_settings", "copy_amt"),
    ("okx", "fiat_buy_sell_trade", "rfq_amt"),
    ("okx", "place_algo_order", "callback_spread"),
    ("okx", "place_algo_order", "callback_ratio"),
    ("binance", "place_order", "trailingDelta"),
    ("bitget", "stock_plus_orders_place_order", "limit_offset"),
    ("bitget", "stock_plus_orders_place_order", "trailing_percent"),
    ("bybit", "crypto_loan_fixed_borrow", "annual_rate"),
    ("kraken", "place_spot_order", "leverage"),
])
def test_sampled_holes_reject_lossy_values(exchange, method, key):
    schema = CATALOG["exchanges"][exchange][method]
    for value in [1e-7, "1e-7"]:
        with pytest.raises(ValueError, match="decimal"):
            normalize({key: value}, schema=schema)
    assert normalize({key: Decimal("0.1234567890123456789")}, schema=schema)[key] == "0.1234567890123456789"


@pytest.mark.parametrize("method", ["uta_trade_grid_create_neutral_bot", "uta_trade_grid_validate_neutral"])
def test_neutral_grid_investment_is_an_array(method):
    schema = CATALOG["exchanges"]["bitget"][method]
    value = {"investment_amount": [{"coin": "USDT", "amount": "10.25"}]}
    assert normalize(value, schema=schema) == value
    with pytest.raises(ValueError):
        normalize({"investment_amount": [{"amount": 0.1}]}, schema=schema)


def test_documented_signed_values_and_percent_scope():
    for exchange, method, key in [("kraken", "place_futures_order", "limitPriceOffsetValue"), ("okx", "simulate_positions", "idxVol")]:
        schema = CATALOG["exchanges"][exchange][method]
        assert normalize({key: "-0.5"}, schema=schema) == {key: "-0.5"}
        with pytest.raises(ValueError):
            normalize({key: "-5e-1"}, schema=schema)
    with pytest.raises(ValueError):
        normalize({"triggerQuantity": "50%"}, schema=CATALOG["exchanges"]["backpack"]["place_order"])


def test_positive_amounts_and_zero_control_values():
    for exchange, method, key in [("binance", "place_order", "quantity"), ("bybit", "create_internal_transfer", "amount"), ("okx", "place_order", "sz")]:
        with pytest.raises(ValueError, match="positive"):
            normalize({key: "0"}, schema=CATALOG["exchanges"][exchange][method])
    # OKX amendments use zero to remove a TP/SL leg and -1 to execute at market.
    schema = CATALOG["exchanges"]["okx"]["amend_algo_order"]
    normalize({"newTpTriggerPx": "0", "newTpOrdPx": "-1"}, schema=schema)
