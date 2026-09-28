# ruff: noqa: ANN401
"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    async def place_batch_orders(self, orders: list[dict[str, object]]) -> Any:
        return await self._native_private("place_batch_orders", orders=orders)

    async def batch_cancel_orders(self, orderIDs: list[str]) -> Any:
        """Ondo expects one comma-separated orderIDs query value."""
        if not orderIDs or any(not order_id or "," in order_id for order_id in orderIDs):
            raise ValueError("orderIDs must contain nonempty IDs without commas.")
        return await self._native_private("batch_cancel_orders", orderIDs=",".join(orderIDs))
