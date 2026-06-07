"""MEXC private account API endpoints."""

from enum import Enum


class SpotAccount(str, Enum):
    """MEXC Spot V3 private account endpoints."""

    KYC_STATUS = "/api/v3/kyc/status"
    SELF_SYMBOLS = "/api/v3/selfSymbols"
    ACCOUNT = "/api/v3/account"
    MX_DEDUCT_ENABLE = "/api/v3/mxDeduct/enable"
    SYMBOL_COMMISSION = "/api/v3/tradeFee"
    CURRENCY_INFO = "/api/v3/capital/config/getall"
    DEPOSIT_HISTORY = "/api/v3/capital/deposit/hisrec"
    WITHDRAW_HISTORY = "/api/v3/capital/withdraw/history"
    DEPOSIT_ADDRESS = "/api/v3/capital/deposit/address"
    USER_UNIVERSAL_TRANSFER = "/api/v3/capital/transfer"
    USER_UNIVERSAL_TRANSFER_BY_ID = "/api/v3/capital/transfer/tranId"
    INTERNAL_TRANSFER_HISTORY = "/api/v3/capital/transfer/internal"

    def __str__(self) -> str:
        return self.value


class ContractAccount(str, Enum):
    """MEXC Contract V1 private account endpoints."""

    ASSETS = "/api/v1/private/account/assets"
    ASSET = "/api/v1/private/account/asset/{currency}"
    TRANSFER_RECORDS = "/api/v1/private/account/transfer_record"
    HISTORY_POSITIONS = "/api/v1/private/position/list/history_positions"
    OPEN_POSITIONS = "/api/v1/private/position/open_positions"
    FUNDING_RECORDS = "/api/v1/private/position/funding_records"
    RISK_LIMITS = "/api/v1/private/account/risk_limit"
    TRADING_FEE_RATE = "/api/v1/private/account/tiered_fee_rate"
    LEVERAGE = "/api/v1/private/position/leverage"
    CHANGE_MARGIN = "/api/v1/private/position/change_margin"
    CHANGE_LEVERAGE = "/api/v1/private/position/change_leverage"
    POSITION_MODE = "/api/v1/private/position/position_mode"
    CHANGE_POSITION_MODE = "/api/v1/private/position/change_position_mode"

    def __str__(self) -> str:
        return self.value
