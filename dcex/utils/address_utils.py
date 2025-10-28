"""Utility functions for Ethereum address handling."""


def address_to_bytes(address: str) -> bytes:
    """
    Convert an Ethereum address to bytes.

    Args:
        address: Ethereum address string (with or without 0x prefix)

    Returns:
        bytes: The address as bytes
    """
    return bytes.fromhex(address[2:] if address.startswith("0x") else address)
