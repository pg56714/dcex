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
    ACCOUNT_INFO = "/fapi/v3/account"
    INCOME_HISTORY = "/fapi/v1/income"
    USER_DATA_STREAM = "/fapi/v1/listenKey"

    def __str__(self) -> str:
        return self.value
