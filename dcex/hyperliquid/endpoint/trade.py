"""Trading-related API endpoints for Hyperliquid exchange."""

from enum import Enum


class Trade(str, Enum):
    """
    Trading-related API endpoints for Hyperliquid exchange.

    This enum defines all trading-related API endpoints including order management,
    cancellation, modification, leverage adjustment, TWAP orders, and other trading functions.
    """

    ORDER = "order"
    CANCEL = "cancel"
    CANCELBYCLOID = "cancelByCloid"
    SCHEDULECANCEL = "scheduleCancel"
    MODIFY = "modify"
    BATCHMODIFY = "batchModify"
    UPDATELEVERAGE = "updateLeverage"
    UPDATEISOLATEMARGIN = "updateIsolatedMargin"
    TWAPORDER = "twapOrder"
    TWAPCANCEL = "twapCancel"

    def __str__(self) -> str:
        return self.value
