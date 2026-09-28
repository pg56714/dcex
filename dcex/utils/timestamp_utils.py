"""Timestamp generation through the native core."""

from typing import overload

from .. import _native


@overload
def generate_timestamp(iso_format: bool = False) -> int: ...


@overload
def generate_timestamp(iso_format: bool = True) -> str: ...


def generate_timestamp(iso_format: bool = False) -> int | str:
    """
    Generate timestamp in milliseconds or ISO format.

    Args:
        iso_format: If True, return ISO format string, otherwise return milliseconds

    Returns:
        int | str: Timestamp in milliseconds or ISO format
    """
    return _native.generate_timestamp_iso() if iso_format else _native.generate_timestamp_ms()
