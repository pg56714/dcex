"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    async def place_spot_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place MEXC Spot batch orders."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(batchOrders=batchOrders, recvWindow=recvWindow),
        )

    async def cancel_contract_batch_orders_by_external_id(
        self, *, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        POST /api/v1/private/order/batch_cancel_with_external.

        Inspect every returned item for individual failures.
        """
        return await self._native_private(
            "cancel_contract_batch_orders_by_external_id", self._native_params(orders=orders)
        )

    async def get_contract_batch_orders_by_external_id(
        self, *, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        POST /api/v1/private/order/batch_query_with_external.

        Inspect every returned item for individual failures.
        """
        return await self._native_private(
            "get_contract_batch_orders_by_external_id", self._native_params(orders=orders)
        )

    async def place_contract_batch_orders(self, orders: list[dict[str, Any]]) -> Any:  # noqa: ANN401
        """
        Submit up to 50 native-symbol futures orders.

        Previously documented as under maintenance; the current official page restricts
        this endpoint to market maker accounts. Inspect each item errorCode in the response.
        Decimal prices and quantities must be plain strings.
        Source: https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/batch-place-order
        """
        return await self._native_private(
            "place_contract_batch_orders", self._native_params(orders=orders)
        )
