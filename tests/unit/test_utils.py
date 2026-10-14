"""Unit tests for small utility modules."""
# ruff: noqa: D103

import pytest

from dcex.utils.decimal_utils import get_decimal_places, reverse_decimal_places
from dcex.utils.timeframe_utils import bybit_convert_timeframe


@pytest.mark.parametrize(
    ("timeframe", "expected"),
    [
        ("1m", "1"),
        ("3m", "3"),
        ("1h", "60"),
        ("1d", "D"),
        ("1w", "W"),
        ("1M", "M"),
    ],
)
def test_bybit_convert_timeframe(timeframe: str, expected: str) -> None:
    assert bybit_convert_timeframe(timeframe) == expected


def test_timeframe_converter_rejects_unknown_values() -> None:
    with pytest.raises(ValueError, match="timeframe not supported"):
        bybit_convert_timeframe("2d")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.001, 3),
        (0.5, 1),
        (0.25, 2),
        (2.5, 1),
        (-0.125, 3),
        (1e-7, 7),
        (1, 0),
        (0, 0),
    ],
)
def test_get_decimal_places(value: float, expected: int) -> None:
    assert get_decimal_places(value) == expected


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_get_decimal_places_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        get_decimal_places(value)


def test_reverse_decimal_places() -> None:
    assert reverse_decimal_places(3) == 0.001
