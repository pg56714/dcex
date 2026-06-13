"""Bitget trade API endpoints."""

from enum import Enum


class SpotTrade(str, Enum):
    """Enumeration of Bitget spot private trade endpoints."""

    PLACE_ORDER = "/api/v2/spot/trade/place-order"
    BATCH_PLACE_ORDER = "/api/v2/spot/trade/batch-orders"
    CANCEL_ORDER = "/api/v2/spot/trade/cancel-order"
    BATCH_CANCEL_ORDER = "/api/v2/spot/trade/batch-cancel-order"
    ORDER_INFO = "/api/v2/spot/trade/orderInfo"
    UNFILLED_ORDERS = "/api/v2/spot/trade/unfilled-orders"
    HISTORY_ORDERS = "/api/v2/spot/trade/history-orders"
    FILLS = "/api/v2/spot/trade/fills"

    def __str__(self) -> str:
        return self.value


class FuturesTrade(str, Enum):
    """Enumeration of Bitget futures private trade endpoints."""

    PLACE_ORDER = "/api/v2/mix/order/place-order"
    BATCH_PLACE_ORDER = "/api/v2/mix/order/batch-place-order"
    CANCEL_ORDER = "/api/v2/mix/order/cancel-order"
    BATCH_CANCEL_ORDERS = "/api/v2/mix/order/batch-cancel-orders"
    ORDER_DETAIL = "/api/v2/mix/order/detail"
    PENDING_ORDERS = "/api/v2/mix/order/orders-pending"
    HISTORY_ORDERS = "/api/v2/mix/order/orders-history"
    FILLS = "/api/v2/mix/order/fills"

    def __str__(self) -> str:
        return self.value


class UtaTrade(str, Enum):
    """Enumeration of Bitget UTA private trade endpoints."""

    PLACE_ORDER = "/api/v3/trade/place-order"
    BATCH_PLACE_ORDER = "/api/v3/trade/place-batch"
    CANCEL_ORDER = "/api/v3/trade/cancel-order"
    BATCH_CANCEL_ORDERS = "/api/v3/trade/cancel-batch"
    ORDER_DETAIL = "/api/v3/trade/order-info"
    PENDING_ORDERS = "/api/v3/trade/unfilled-orders"
    HISTORY_ORDERS = "/api/v3/trade/history-orders"
    FILLS = "/api/v3/trade/fills"
    POSITIONS = "/api/v3/position/current-position"

    def __str__(self) -> str:
        return self.value
