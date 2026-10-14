"""Utility functions for converting timeframes between different exchange formats."""

from .. import _native


def bybit_convert_timeframe(timeframe: str) -> str:
    """
    Convert timeframe to Bybit format.

    Args:
        timeframe: Standard timeframe string (e.g., "1m", "1h", "1d")

    Returns:
        str: Bybit-specific timeframe format

    Raises:
        ValueError: If timeframe is not supported
    """
    return _native.bybit_convert_timeframe(timeframe)
