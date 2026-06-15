"""Utility functions for decimal precision handling."""

from .. import _native


def get_decimal_places(value: float) -> int:
    """Returns the number of decimal places for a given value."""
    return _native.get_decimal_places(value)


def reverse_decimal_places(decimal_places: int) -> float:
    """Converts a decimal place count back to its corresponding value."""
    return _native.reverse_decimal_places(decimal_places)
