"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    async def place_batch_orders(
        self,
        orders: list[dict[str, Any]],
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place several orders in one signed ``order`` action.

        Each order uses the ``place_order`` keys (``product_symbol``, ``isBuy``,
        ``price``, ``size``, optional ``reduceOnly``, ``tif`` or
        ``isMarket``/``triggerPx``/``tpsl``, ``cloid``). ``grouping`` may be
        ``normalTpsl`` or ``positionTpsl`` to send an entry with its TP/SL orders.
        """
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return await self._native_private("place_batch_orders", self._native_params(**locals()))

    async def cancel_batch_orders(
        self,
        cancels: list[dict[str, Any]],
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel several orders (``product_symbol`` + ``oid`` each) in one action."""
        return await self._native_private("cancel_batch_orders", self._native_params(**locals()))

    async def cancel_batch_orders_by_cloid(
        self,
        cancels: list[dict[str, Any]],
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel several orders (``product_symbol`` + ``cloid`` each) in one action."""
        return await self._native_private(
            "cancel_batch_orders_by_cloid",
            self._native_params(**locals()),
        )

    async def modify_batch_orders(
        self,
        modifies: list,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Modify multiple orders in batch."""
        return await self._native_private(
            "modify_batch_orders",
            self._native_params(**locals()),
        )
