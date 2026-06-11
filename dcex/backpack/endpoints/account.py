"""Backpack private account and capital API endpoints."""

from enum import Enum


class Account(str, Enum):
    """Backpack private account endpoints."""

    ACCOUNT = "/api/v1/account"
    MAX_BORROW_QUANTITY = "/api/v1/account/limits/borrow"
    MAX_ORDER_QUANTITY = "/api/v1/account/limits/order"
    MAX_WITHDRAWAL_QUANTITY = "/api/v1/account/limits/withdrawal"

    def __str__(self) -> str:
        return self.value


class BorrowLend(str, Enum):
    """Backpack private borrow/lend endpoints."""

    POSITIONS = "/api/v1/borrowLend/positions"
    BORROW_HISTORY = "/wapi/v1/history/borrowLend"
    INTEREST_HISTORY = "/wapi/v1/history/interest"
    POSITION_HISTORY = "/wapi/v1/history/borrowLend/positions"

    def __str__(self) -> str:
        return self.value


class Capital(str, Enum):
    """Backpack private capital endpoints."""

    CONVERT_DUST = "/api/v1/account/convertDust"
    BALANCES = "/api/v1/capital"
    COLLATERAL = "/api/v1/capital/collateral"
    DEPOSITS = "/wapi/v1/capital/deposits"
    DEPOSIT_ADDRESS = "/wapi/v1/capital/deposit/address"
    WITHDRAWALS = "/wapi/v1/capital/withdrawals"
    DUST_CONVERSION_HISTORY = "/wapi/v1/history/dust"
    SETTLEMENT_HISTORY = "/wapi/v1/history/settlement"

    def __str__(self) -> str:
        return self.value
