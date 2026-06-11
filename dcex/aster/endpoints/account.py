"""Aster V3 private account API endpoints."""

from enum import Enum


class SpotAccount(str, Enum):
    """Aster spot account endpoints."""

    ACCOUNT = "/api/v3/account"
    TRANSACTION_HISTORY = "/api/v3/transactionHistory"
    TRANSFER = "/api/v3/asset/wallet/transfer"
    LISTEN_KEY = "/api/v3/listenKey"

    def __str__(self) -> str:
        return self.value


class FuturesAccount(str, Enum):
    """Aster futures account endpoints."""

    POSITION_MODE = "/fapi/v3/positionSide/dual"
    STP_MODE = "/fapi/v3/stpMode"
    MULTI_ASSETS_MODE = "/fapi/v3/multiAssetsMargin"
    TRANSFER = "/fapi/v3/asset/wallet/transfer"
    BALANCE = "/fapi/v3/balance"
    ACCOUNT = "/fapi/v3/accountWithJoinMargin"
    POSITION_MARGIN = "/fapi/v3/positionMargin"
    POSITION_MARGIN_HISTORY = "/fapi/v3/positionMargin/history"
    POSITION_RISK = "/fapi/v3/positionRisk"
    USER_TRADES = "/fapi/v3/userTrades"
    INCOME = "/fapi/v3/income"
    LEVERAGE_BRACKET = "/fapi/v3/leverageBracket"
    ADL_QUANTILE = "/fapi/v3/adlQuantile"
    FORCE_ORDERS = "/fapi/v3/forceOrders"
    COMMISSION_RATE = "/fapi/v3/commissionRate"
    MMP = "/fapi/v3/mmp"
    MMP_RESET = "/fapi/v3/mmpReset"
    LISTEN_KEY = "/fapi/v3/listenKey"

    def __str__(self) -> str:
        return self.value
