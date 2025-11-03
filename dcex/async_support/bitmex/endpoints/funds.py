"""
BitMEX account-related API endpoints module.

This module contains the Account enum with all account and wallet related
endpoints for the BitMEX API.
"""

from enum import Enum


class Account(str, Enum):
    """
    BitMEX account-related API endpoints.

    This enum contains all the account and wallet related endpoints
    for the BitMEX API, including wallet information retrieval.
    """

    ACCOUNT_INFO = "/api/v1/user/wallet"

    def __str__(self) -> str:
        return self.value
