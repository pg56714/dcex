"""Binance trading endpoints for spot and futures trading."""

from enum import Enum


class SpotTrade(str, Enum):
    """Spot trading endpoints."""

    PLACE_CANCEL_QUERY_ORDER = "/api/v3/order"
    TEST_ORDER = "/api/v3/order/test"
    PLACE_SPOT_ORDER = "/api/v3/order"
    OPEN_ORDER = "/api/v3/openOrders"
    ALL_ORDERS = "/api/v3/allOrders"
    ACCOUNT_TRADES = "/api/v3/myTrades"

    def __str__(self) -> str:
        return self.value


class FuturesTrade(str, Enum):
    """Futures trading endpoints."""

    SET_LEVERAGE = "/fapi/v1/leverage"
    PLACE_CANCEL_QUERY_ORDER = "/fapi/v1/order"
    TEST_ORDER = "/fapi/v1/order/test"
    CANCEL_ALL_OPEN_ORDERS = "/fapi/v1/allOpenOrders"
    QUERY_ALL_ORDERS = "/fapi/v1/allOrders"
    QUERY_OPEN_ORDER = "/fapi/v1/openOrder"
    OPEN_ORDERS = "/fapi/v1/openOrders"
    PLACE_CANCEL_QUERY_ALGO_ORDER = "/fapi/v1/algoOrder"
    CANCEL_ALL_OPEN_ALGO_ORDERS = "/fapi/v1/algoOpenOrders"
    OPEN_ALGO_ORDERS = "/fapi/v1/openAlgoOrders"
    ALL_ALGO_ORDERS = "/fapi/v1/allAlgoOrders"
    ACCOUNT_TRADES = "/fapi/v1/userTrades"
    POSITION_INFO = "/fapi/v3/positionRisk"

    def __str__(self) -> str:
        return self.value
