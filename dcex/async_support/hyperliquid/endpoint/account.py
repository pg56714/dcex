"""Account-related API endpoints for Hyperliquid exchange."""

from enum import Enum


class Account(str, Enum):
    """
    Account-related API endpoints for Hyperliquid exchange.

    This enum defines all account-related API endpoints including clearinghouse state,
    order management, user fills, portfolio, and other account functions.
    """

    CLEARINGHOUSESTATE = "clearinghouseState"
    OPENORDERS = "openOrders"
    USERFILLS = "userFills"
    USERRATELIMIT = "userRateLimit"
    ORDERSTATUS = "orderStatus"
    HISTORICALORDERS = "historicalOrders"
    SUBACCOUNTS = "subAccounts"
    USERROLE = "userRole"
    PORTFOLIO = "portfolio"

    def __str__(self) -> str:
        return self.value
