"""Kraken account API endpoints."""

from enum import Enum


class SpotAccount(str, Enum):
    """Enumeration of Kraken spot private account endpoints."""

    BALANCE = "/0/private/Balance"
    TRADE_BALANCE = "/0/private/TradeBalance"
    OPEN_POSITIONS = "/0/private/OpenPositions"
    LEDGERS = "/0/private/Ledgers"
    TRADE_VOLUME = "/0/private/TradeVolume"
    WALLET_TRANSFER = "/0/private/WalletTransfer"

    def __str__(self) -> str:
        return self.value


class FuturesAccount(str, Enum):
    """Enumeration of Kraken Futures private account endpoints."""

    ACCOUNTS = "/derivatives/api/v3/accounts"
    OPEN_POSITIONS = "/derivatives/api/v3/openpositions"
    FILLS = "/derivatives/api/v3/fills"
    TRANSFER = "/derivatives/api/v3/transfer"
    WITHDRAWAL = "/derivatives/api/v3/withdrawal"

    def __str__(self) -> str:
        return self.value
