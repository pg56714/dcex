"""
BitMEX order management API endpoints module.

This module contains the Order enum with all order-related
endpoints for the BitMEX API.
"""

from enum import Enum


class Order(str, Enum):
    """
    BitMEX order management API endpoints.

    This enum contains all the order-related endpoints for the BitMEX API,
    including order placement, modification, cancellation, and querying.
    """

    PLACE_ORDER = "/api/v2/order"
    AMEND_ORDER = "/api/v2/order"
    CANCEL_ORDER = "/api/v2/order"
    CANCEL_ALL_ORDERS = "/api/v2/order/all"
    QUERY_ORDER = "/api/v1/order"

    def __str__(self) -> str:
        return self.value
