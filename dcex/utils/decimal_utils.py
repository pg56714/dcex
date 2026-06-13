"""Utility functions for decimal precision handling."""

from decimal import Decimal


def get_decimal_places(value: float) -> int:
    """Returns the number of decimal places for a given value."""
    decimal_value = Decimal(str(value))
    if not decimal_value.is_finite():
        raise ValueError("value must be finite")
    exponent = decimal_value.normalize().as_tuple().exponent
    return max(0, -int(exponent))


def reverse_decimal_places(decimal_places: int) -> float:
    """Converts a decimal place count back to its corresponding value."""
    return 10**-decimal_places
