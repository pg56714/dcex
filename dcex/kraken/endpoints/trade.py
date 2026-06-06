"""Kraken trade API endpoints."""

from enum import Enum


class SpotTrade(str, Enum):
    """Enumeration of Kraken spot private trade endpoints."""

    ADD_ORDER = "/0/private/AddOrder"
    CANCEL_ORDER = "/0/private/CancelOrder"
    CANCEL_ALL = "/0/private/CancelAll"
    OPEN_ORDERS = "/0/private/OpenOrders"
    CLOSED_ORDERS = "/0/private/ClosedOrders"
    QUERY_ORDERS = "/0/private/QueryOrders"
    TRADES_HISTORY = "/0/private/TradesHistory"

    def __str__(self) -> str:
        return self.value


class FuturesTrade(str, Enum):
    """Enumeration of Kraken Futures private trade endpoints."""

    SEND_ORDER = "/derivatives/api/v3/sendorder"
    CANCEL_ORDER = "/derivatives/api/v3/cancelorder"
    CANCEL_ALL = "/derivatives/api/v3/cancelallorders"
    OPEN_ORDERS = "/derivatives/api/v3/openorders"
    ORDER_STATUS = "/derivatives/api/v3/orders/status"

    def __str__(self) -> str:
        return self.value
