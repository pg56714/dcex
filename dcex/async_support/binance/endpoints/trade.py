"""Binance trading endpoints for spot and futures trading."""

from enum import Enum


class SpotTrade(str, Enum):
    """Spot trading endpoints."""

    PLACE_CANCEL_QUERY_ORDER = "/api/v3/order"
    PLACE_SPOT_ORDER = "/api/v3/order"
    OPEN_ORDER = "/api/v3/openOrders"

    def __str__(self) -> str:
        return self.value


class FuturesTrade(str, Enum):
    """Futures trading endpoints."""

    SET_LEVERAGE = "/fapi/v1/leverage"
    PLACE_CANCEL_QUERY_ORDER = "/fapi/v1/order"
    CANCEL_ALL_OPEN_ORDERS = "/fapi/v1/allOpenOrders"
    QUERY_ALL_ORDERS = "/fapi/v1/allOrders"
    QUERY_OPEN_ORDER = "/fapi/v1/openOrder"
    POSITION_INFO = "/fapi/v3/positionRisk"

    def __str__(self) -> str:
        return self.value
