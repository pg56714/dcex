"""Bitget account API endpoints."""

from enum import Enum


class CommonAccount(str, Enum):
    """Enumeration of Bitget common private account endpoints."""

    ALL_ACCOUNT_BALANCE = "/api/v2/account/all-account-balance"
    FUNDING_ASSETS = "/api/v2/account/funding-assets"

    def __str__(self) -> str:
        return self.value


class SpotAccount(str, Enum):
    """Enumeration of Bitget spot private account endpoints."""

    INFO = "/api/v2/spot/account/info"
    ASSETS = "/api/v2/spot/account/assets"
    BILLS = "/api/v2/spot/account/bills"
    TRANSFER_RECORDS = "/api/v2/spot/account/transferRecords"
    TRANSFER = "/api/v2/spot/wallet/transfer"
    TRANSFER_COIN_INFO = "/api/v2/spot/wallet/transfer-coin-info"
    DEPOSIT_RECORDS = "/api/v2/spot/wallet/deposit-records"

    def __str__(self) -> str:
        return self.value


class FuturesAccount(str, Enum):
    """Enumeration of Bitget futures private account endpoints."""

    ACCOUNT = "/api/v2/mix/account/account"
    ACCOUNTS = "/api/v2/mix/account/accounts"
    BILLS = "/api/v2/mix/account/bill"
    SET_LEVERAGE = "/api/v2/mix/account/set-leverage"
    SET_MARGIN_MODE = "/api/v2/mix/account/set-margin-mode"
    SET_POSITION_MODE = "/api/v2/mix/account/set-position-mode"
    ALL_POSITIONS = "/api/v2/mix/position/all-position"
    SINGLE_POSITION = "/api/v2/mix/position/single-position"

    def __str__(self) -> str:
        return self.value


class UtaAccount(str, Enum):
    """Enumeration of Bitget UTA private account endpoints."""

    ASSETS = "/api/v3/account/assets"
    INFO = "/api/v3/account/info"
    SET_LEVERAGE = "/api/v3/account/set-leverage"
    SET_HOLD_MODE = "/api/v3/account/set-hold-mode"

    def __str__(self) -> str:
        return self.value
