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


def bitmart_convert_timeframe(timeframe: str) -> int:
    """
    Convert timeframe to Bitmart format.

    Args:
        timeframe: Standard timeframe string (e.g., "1m", "1h", "1d")

    Returns:
        int: Bitmart-specific timeframe in minutes

    Raises:
        ValueError: If timeframe is not supported
    """
    return _native.bitmart_convert_timeframe(timeframe)


def kucoin_convert_timeframe(timeframe: str) -> str:
    """
    Convert timeframe to KuCoin format.

    Args:
        timeframe: Standard timeframe string (e.g., "1m", "1h", "1d")

    Returns:
        str: KuCoin-specific timeframe format

    Raises:
        ValueError: If timeframe is not supported
    """
    return _native.kucoin_convert_timeframe(timeframe)
