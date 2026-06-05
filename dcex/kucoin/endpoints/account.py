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


class FuturesAccount(str, Enum):
    """Enumeration of KuCoin Futures Account API endpoints."""

    ACCOUNT_OVERVIEW = "/api/v1/account-overview"
    POSITIONS = "/api/v1/positions"
    POSITION = "/api/v1/position"
    POSITION_MODE = "/api/v2/position/getPositionMode"

    def __str__(self) -> str:
        return self.value
