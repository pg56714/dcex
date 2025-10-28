"""Utility functions for decimal precision handling."""

import math


def get_decimal_places(value: float) -> int:
    """Returns the number of decimal places for a given value."""
    if value > 0:
        return int(-math.log10(value))
    return 0  # Avoid errors when value is 0


def reverse_decimal_places(decimal_places: int) -> float:
    """Converts a decimal place count back to its corresponding value."""
    return 10**-decimal_places
