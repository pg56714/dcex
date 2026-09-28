"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    async def place_batch_orders(
        self,
        orders: list[dict[str, Any]],
        brokerId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place Backpack batch orders."""
        return await self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders, brokerId=brokerId),
        )
