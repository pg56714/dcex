"""Unit tests for small utility modules."""
# ruff: noqa: D103

from collections.abc import Callable

import pytest

from dcex.utils.decimal_utils import get_decimal_places, reverse_decimal_places
from dcex.utils.timeframe_utils import (
    bitmart_convert_timeframe,
    bybit_convert_timeframe,
    kucoin_convert_timeframe,
)


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


@pytest.mark.parametrize(
    ("timeframe", "expected"),
    [
        ("1m", 1),
        ("5m", 5),
        ("1h", 60),
        ("1d", 1440),
        ("1w", 10080),
        ("1M", 43200),
    ],
)
def test_bitmart_convert_timeframe(timeframe: str, expected: int) -> None:
    assert bitmart_convert_timeframe(timeframe) == expected


@pytest.mark.parametrize(
    ("timeframe", "expected"),
    [
        ("1m", "1min"),
        ("5m", "5min"),
        ("1h", "1hour"),
        ("1d", "1day"),
        ("1w", "1week"),
    ],
)
def test_kucoin_convert_timeframe(timeframe: str, expected: str) -> None:
    assert kucoin_convert_timeframe(timeframe) == expected


@pytest.mark.parametrize(
    "converter",
    [bybit_convert_timeframe, bitmart_convert_timeframe, kucoin_convert_timeframe],
)
def test_timeframe_converters_reject_unknown_values(
    converter: Callable[[str], str | int],
) -> None:
    with pytest.raises(ValueError, match="timeframe not supported"):
        converter("2d")


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
