"""Utility functions for Ethereum address handling."""

from .. import _native


def address_to_bytes(address: str) -> bytes:
    """
    Convert an Ethereum address to bytes.

    Args:
        address: Ethereum address string (with or without 0x prefix)

    Returns:
        bytes: The address as bytes
    """
    return _native.address_to_bytes(address)
