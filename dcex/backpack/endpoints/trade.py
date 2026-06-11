"""Backpack private trade and position API endpoints."""

from enum import Enum


class Order(str, Enum):
    """Backpack private order endpoints."""

    ORDER = "/api/v1/order"
    ORDERS = "/api/v1/orders"
    FILLS = "/wapi/v1/history/fills"
    ORDER_HISTORY = "/wapi/v1/history/orders"

    def __str__(self) -> str:
        return self.value


class Position(str, Enum):
    """Backpack private position endpoints."""

    POSITION = "/api/v1/position"
    FUNDING = "/wapi/v1/history/funding"
    POSITION_HISTORY = "/wapi/v1/history/position"

    def __str__(self) -> str:
        return self.value
