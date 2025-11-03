"""KuCoin Spot Account API endpoints."""

from enum import Enum


class SpotAccount(str, Enum):
    """
    Enumeration of KuCoin Spot Account API endpoints.

    This class defines the available endpoints for spot account operations
    on the KuCoin exchange, including balance retrieval and account management.
    """

    ACCOUNT_BALANCE = "/api/v1/accounts"

    def __str__(self) -> str:
        return self.value
