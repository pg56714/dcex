"""
Gate.io Account API endpoints.

This module contains all the API endpoints related to account management
operations on the Gate.io exchange, including spot, futures, and delivery
account operations.
"""

from enum import Enum


class FutureAccount(str, Enum):
    """
    Futures account-related API endpoints for Gate.io exchange.

    This enum contains all the futures account management endpoints including:
    - Account balance queries
    - Account transaction history
    - Settlement operations
    """

    QUERY_FUTURES_ACCOUNT = "/futures/{settle}/accounts"
    QUERY_ACCOUNT_BOOK = "/futures/{settle}/account_book"

    def __str__(self) -> str:
        return self.value


class DeliveryAccount(str, Enum):
    """
    Delivery account-related API endpoints for Gate.io exchange.

    This enum contains all the delivery account management endpoints including:
    - Account balance queries
    - Account transaction history
    - Settlement operations
    """

    QUERY_DELIVERY_ACCOUNT = "/delivery/{settle}/accounts"
    QUERY_ACCOUNT_BOOK = "/delivery/{settle}/account_book"

    def __str__(self) -> str:
        return self.value


class SpotAccount(str, Enum):
    """
    Spot account-related API endpoints for Gate.io exchange.

    This enum contains all the spot account management endpoints including:
    - Account balance queries
    - Account transaction history
    - Currency operations
    """

    QUERY_SPOT_ACCOUNT = "/spot/accounts"
    QUERY_ACCOUNT_BOOK = "/spot/account_book"

    def __str__(self) -> str:
        return self.value
