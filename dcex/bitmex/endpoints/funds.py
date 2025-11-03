"""
BitMEX Account/Funds API endpoints.

This module contains the API endpoint definitions for account-related operations
on the BitMEX exchange, including wallet information retrieval.
"""

from enum import Enum


class Account(str, Enum):
    """
    BitMEX Account API endpoints.

    This enum contains all the API endpoint paths for account-related operations
    such as retrieving wallet information and account details.
    """

    ACCOUNT_INFO = "/api/v1/user/wallet"

    def __str__(self) -> str:
        return self.value
