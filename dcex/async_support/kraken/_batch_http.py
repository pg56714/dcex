"""Fund movement and batch endpoint mixins."""

from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    async def place_spot_batch_orders(
        self,
        product_symbol: str,
        orders: list[dict[str, Any]],
        *,
        validate: bool | None = None,
        deadline: str | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Submit 2..15 orders for one pair as a signed JSON batch."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                orders=dumps(orders),
                validate=validate,
                deadline=deadline,
                asset_class=asset_class,
            ),
        )

    async def cancel_spot_batch_orders(
        self, *, orders: list[str | int] | None = None, cl_ord_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """Cancel up to 50 txids/userrefs or client order identifiers."""
        return await self._native_private(
            "cancel_spot_batch_orders",
            self._native_params(
                orders=dumps(orders) if orders is not None else None,
                cl_ord_ids=dumps(cl_ord_ids) if cl_ord_ids is not None else None,
            ),
        )

    async def manage_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, process_before: str | None = None
    ) -> dict[str, Any]:
        """Send, edit or cancel 1 to 500 instructions; price and size fields are JSON numbers."""
        return await self._native_private(
            "manage_futures_batch_orders",
            self._native_params(orders=dumps(orders), processBefore=process_before),
        )
