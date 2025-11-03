"""
BitMEX Order Management API endpoints.

This module contains the API endpoint definitions for order management operations
on the BitMEX exchange, including placing, amending, canceling orders and
querying order information.
"""

from enum import Enum


class Order(str, Enum):
    """
    BitMEX Order Management API endpoints.

    This enum contains all the API endpoint paths for order management operations
    such as placing new orders, amending existing orders, canceling orders,
    canceling all orders, and querying order information.
    """

    PLACE_ORDER = "/api/v2/order"
    AMEND_ORDER = "/api/v2/order"
    CANCEL_ORDER = "/api/v2/order"
    CANCEL_ALL_ORDERS = "/api/v2/order/all"
    QUERY_ORDER = "/api/v1/order"

    def __str__(self) -> str:
        return self.value
