"""Binance account API endpoints for spot and futures trading."""

from enum import Enum


class SpotAccount(str, Enum):
    """Enumeration of Binance spot trading account API endpoints."""

    ACCOUNT_BALANCE = "/api/v3/account"

    def __str__(self) -> str:
        return self.value


class FuturesAccount(str, Enum):
    """Enumeration of Binance futures trading account API endpoints."""

    ACCOUNT_BALANCE = "/fapi/v3/balance"
    INCOME_HISTORY = "/fapi/v1/income"

    def __str__(self) -> str:
        return self.value
