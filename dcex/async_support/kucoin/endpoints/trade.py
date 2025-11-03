"""KuCoin Spot Trade API endpoints."""

from enum import Enum


class SpotTrade(str, Enum):
    """
    Enumeration of KuCoin Spot Trade API endpoints.

    This class defines the available endpoints for spot trading operations
    on the KuCoin exchange, including order placement, cancellation,
    order management, and trade history retrieval.
    """

    PLACE_ORDER = "/api/v1/hf/orders"
    BATCH_ORDERS = "/api/v1/hf/orders/multi"
    CANCEL_ORDER = "/api/v1/hf/orders/{orderId}"
    CANCEL_ALL_ORDERS_BY_SYMBOL = "/api/v1/hf/orders"
    CANCEL_ALL_ORDERS = "/api/v1/hf/orders/cancelAll"
    GET_OPEN_ORDERS = "/api/v1/hf/orders/active"
    GET_TRADE_HISTORY = "/api/v1/hf/fills"

    def __str__(self) -> str:
        return self.value
