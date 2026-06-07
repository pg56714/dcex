"""MEXC private trading API endpoints."""

from enum import Enum


class SpotTrade(str, Enum):
    """MEXC Spot V3 private trading endpoints."""

    TEST_ORDER = "/api/v3/order/test"
    ORDER = "/api/v3/order"
    BATCH_ORDERS = "/api/v3/batchOrders"
    OPEN_ORDERS = "/api/v3/openOrders"
    ALL_ORDERS = "/api/v3/allOrders"
    MY_TRADES = "/api/v3/myTrades"

    def __str__(self) -> str:
        return self.value


class ContractTrade(str, Enum):
    """MEXC Contract V1 private trading endpoints."""

    CREATE_ORDER = "/api/v1/private/order/create"
    CANCEL_ORDERS = "/api/v1/private/order/cancel"
    CANCEL_ORDER_WITH_EXTERNAL_ID = "/api/v1/private/order/cancel_with_external"
    CANCEL_ALL_ORDERS = "/api/v1/private/order/cancel_all"
    OPEN_ORDERS = "/api/v1/private/order/list/open_orders/{symbol}"
    HISTORY_ORDERS = "/api/v1/private/order/list/history_orders"
    EXTERNAL_ORDER = "/api/v1/private/order/external/{symbol}/{external_oid}"
    ORDER = "/api/v1/private/order/get/{order_id}"
    BATCH_QUERY = "/api/v1/private/order/batch_query"
    ORDER_DEAL_DETAILS = "/api/v1/private/order/deal_details/{order_id}"
    ORDER_DEALS = "/api/v1/private/order/list/order_deals"
    PLAN_ORDERS = "/api/v1/private/planorder/list/orders"
    STOP_ORDERS = "/api/v1/private/stoporder/list/orders"

    def __str__(self) -> str:
        return self.value
