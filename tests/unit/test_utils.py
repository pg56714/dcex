"""Unit tests for small utility modules."""
# ruff: noqa: D103

from collections.abc import Callable

import polars as pl
import pytest

from dcex.utils.common_dataframe import to_dataframe
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


def test_decimal_place_helpers() -> None:
    assert get_decimal_places(0.001) == 3
    assert get_decimal_places(1) == 0
    assert get_decimal_places(0) == 0
    assert reverse_decimal_places(3) == 0.001


def test_to_dataframe_handles_empty_input() -> None:
    assert to_dataframe(None).is_empty()
    assert to_dataframe([]).is_empty()
    assert to_dataframe({}).is_empty()


def test_to_dataframe_handles_dicts_and_rows() -> None:
    dict_frame = to_dataframe({"symbol": "BTC", "price": 1})
    assert dict_frame.to_dicts() == [{"symbol": "BTC", "price": 1}]

    list_frame = to_dataframe([{"symbol": "BTC"}, {"symbol": "ETH"}])
    assert list_frame["symbol"].to_list() == ["BTC", "ETH"]

    row_frame = to_dataframe([["BTC", 1], ["ETH", 2]], schema=["symbol", "price"])
    assert isinstance(row_frame, pl.DataFrame)
    assert row_frame.to_dicts() == [{"symbol": "BTC", "price": 1}, {"symbol": "ETH", "price": 2}]
