"""
Gate.io Trade API endpoints.

This module contains all the API endpoints related to trading operations
on the Gate.io exchange, including spot, futures, and delivery trading
functionality.
"""

from enum import Enum


class FutureTrade(str, Enum):
    """
    Futures trading-related API endpoints for Gate.io exchange.

    This enum contains all the futures trading endpoints including:
    - Position management
    - Order operations (create, amend, cancel)
    - Trading history
    - Leverage management
    - Dual mode operations
    """

    GET_ALL_POSITIONS = "/futures/{settle}/positions"
    GET_SINGLE_POSITION = "/futures/{settle}/positions/{contract}"
    UPDATE_POSITION_LEVERAGE = "/futures/{settle}/positions/{contract}/leverage"
    DUAL_MODE_SWITCH = "/futures/{settle}/dual_mode"

    # "POST" Create a new order, "GET" get list, "DELETE" cancel all orders
    FUTURES_ORDER = "/futures/{settle}/orders"
    BATCH_FUTURES_ORDERS = "/futures/{settle}/batch_orders"

    # "GET" get order, "POST" amend order, "DELETE" cancel single order
    SINGLE_ORDER = "/futures/{settle}/orders/{order_id}"
    LIST_PERSONAL_TRADING_HISTORY = "/futures/{settle}/my_trades"
    LIST_POSITION_CLOSE_HISTORY = "/futures/{settle}/position_close"
    LIST_AUTODELEVERAGING_HISTORY = "/futures/{settle}/auto_deleverages"

    def __str__(self) -> str:
        return self.value


class DeliveryTrade(str, Enum):
    """
    Delivery trading-related API endpoints for Gate.io exchange.

    This enum contains all the delivery trading endpoints including:
    - Position management
    - Order operations (create, cancel)
    - Trading history
    - Leverage management
    """

    GET_ALL_POSITIONS = "/delivery/{settle}/positions"
    GET_SINGLE_POSITION = "/delivery/{settle}/positions/{contract}"
    UPDATE_POSITION_LEVERAGE = "/delivery/{settle}/positions/{contract}/leverage"

    # "POST" Create a new order, "GET" get list, "DELETE" cancel all orders
    FUTURES_ORDER = "/delivery/{settle}/orders"

    # "GET" get order, "DELETE" cancel single order
    SINGLE_ORDER = "/delivery/{settle}/orders/{order_id}"
    LIST_PERSONAL_TRADING_HISTORY = "/delivery/{settle}/my_trades"
    LIST_POSITION_CLOSE_HISTORY = "/delivery/{settle}/position_close"

    def __str__(self) -> str:
        return self.value


class SpotTrade(str, Enum):
    """
    Spot trading-related API endpoints for Gate.io exchange.

    This enum contains all the spot trading endpoints including:
    - Order management (create, amend, cancel)
    - Trading history
    - Open orders queries
    """

    GET_OPEN_ORDER = "/spot/open_orders"
    # "POST" Create a new order, "GET" get list, "DELETE" cancel all orders
    SPOT_ORDER = "/spot/orders"

    # "GET" get order, "POST" amend order, "DELETE" cancel single order
    SINGLE_ORDER = "/spot/orders/{order_id}"
    LIST_PERSONAL_TRADING_HISTORY = "/spot/my_trades"

    def __str__(self) -> str:
        return self.value
