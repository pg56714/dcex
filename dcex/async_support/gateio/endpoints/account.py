"""
Gate.io account management API endpoints module.

This module contains the account-related endpoint enums for different
trading types (Future, Delivery, Spot) in the Gate.io API.
"""

from enum import Enum


class FutureAccount(str, Enum):
    """
    Gate.io futures account management API endpoints.

    This enum contains all futures account-related endpoints for the Gate.io API,
    including account queries and account book operations.
    """

    QUERY_FUTURES_ACCOUNT = "/futures/{settle}/accounts"
    QUERY_ACCOUNT_BOOK = "/futures/{settle}/account_book"

    def __str__(self) -> str:
        return self.value


class DeliveryAccount(str, Enum):
    """
    Gate.io delivery account management API endpoints.

    This enum contains all delivery account-related endpoints for the Gate.io API,
    including account queries and account book operations.
    """

    QUERY_DELIVERY_ACCOUNT = "/delivery/{settle}/accounts"
    QUERY_ACCOUNT_BOOK = "/delivery/{settle}/account_book"

    def __str__(self) -> str:
        return self.value


class SpotAccount(str, Enum):
    """
    Gate.io spot account management API endpoints.

    This enum contains all spot account-related endpoints for the Gate.io API,
    including account queries and account book operations.
    """

    QUERY_SPOT_ACCOUNT = "/spot/accounts"
    QUERY_ACCOUNT_BOOK = "/spot/account_book"

    def __str__(self) -> str:
        return self.value
