"""Aster V3 private trading API endpoints."""

from enum import Enum


class SpotTrade(str, Enum):
    """Aster spot order endpoints."""

    ORDER = "/api/v3/order"
    OPEN_ORDER = "/api/v3/openOrder"
    OPEN_ORDERS = "/api/v3/openOrders"
    ALL_OPEN_ORDERS = "/api/v3/allOpenOrders"
    ALL_ORDERS = "/api/v3/allOrders"
    USER_TRADES = "/api/v3/userTrades"

    def __str__(self) -> str:
        return self.value


class FuturesTrade(str, Enum):
    """Aster futures order and position endpoints."""

    ORDER = "/fapi/v3/order"
    CHASE = "/fapi/v3/chase"
    BATCH_ORDERS = "/fapi/v3/batchOrders"
    ALL_OPEN_ORDERS = "/fapi/v3/allOpenOrders"
    COUNTDOWN_CANCEL_ALL = "/fapi/v3/countdownCancelAll"
    OPEN_ORDER = "/fapi/v3/openOrder"
    OPEN_ORDERS = "/fapi/v3/openOrders"
    ALL_ORDERS = "/fapi/v3/allOrders"
    LEVERAGE = "/fapi/v3/leverage"
    MARGIN_TYPE = "/fapi/v3/marginType"
    PLACE_STRATEGY_ORDER = "/fapi/v3/placeStrategyOrder"
    UPDATE_STRATEGY_ORDER = "/fapi/v3/updateStrategyOrder"
    STRATEGY_OPEN_ORDER = "/fapi/v3/strategyOpenOrder"
    STRATEGY_HISTORY_ORDER = "/fapi/v3/strategyHistoryOrder"

    def __str__(self) -> str:
        return self.value
