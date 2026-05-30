"""Unit tests for cross-exchange unified enums (offline)."""

import pytest

from dcex.enums import (
    OrderSide,
    _BOOL_SIDE_EXCHANGES,
    _exchanges_needing_string_side,
)
from dcex.registry import EXCHANGES


def test_from_any_parses_loose_strings() -> None:
    """Case-insensitive buy/sell parsing works; junk raises."""
    assert OrderSide.from_any("buy") is OrderSide.BUY
    assert OrderSide.from_any("  SELL ") is OrderSide.SELL
    with pytest.raises(ValueError, match="Unknown order side"):
        OrderSide.from_any("hodl")


def test_to_exchange_native_values() -> None:
    """Native side strings match what each exchange actually expects."""
    assert OrderSide.BUY.to_exchange("binance") == "BUY"
    assert OrderSide.SELL.to_exchange("binance") == "SELL"
    assert OrderSide.BUY.to_exchange("bybit") == "Buy"
    assert OrderSide.BUY.to_exchange("okx") == "buy"
    assert OrderSide.SELL.to_exchange("bitmex") == "Sell"
    # case-insensitive exchange name
    assert OrderSide.BUY.to_exchange("BINANCE") == "BUY"


def test_boolean_side_exchange_rejected() -> None:
    """Exchanges using a boolean flag must use is_buy(), not to_exchange()."""
    with pytest.raises(ValueError, match="boolean"):
        OrderSide.BUY.to_exchange("hyperliquid")
    assert OrderSide.BUY.is_buy() is True
    assert OrderSide.SELL.is_buy() is False


def test_every_registry_exchange_is_covered() -> None:
    """
    Anti-drift guard: every registered exchange either has a string-side
    mapping or is explicitly marked as a boolean-side exchange.
    """
    from dcex.enums import _ORDER_SIDE_MAP

    string_side = _exchanges_needing_string_side()
    for exchange in EXCHANGES:
        if exchange in _BOOL_SIDE_EXCHANGES:
            continue
        assert exchange in _ORDER_SIDE_MAP["BUY"], f"{exchange} missing BUY mapping"
        assert exchange in _ORDER_SIDE_MAP["SELL"], f"{exchange} missing SELL mapping"
    # and no stray exchanges in the map that aren't registered
    for exchange in _ORDER_SIDE_MAP["BUY"]:
        assert exchange in string_side, f"{exchange} in map but not registered (or is bool-side)"
