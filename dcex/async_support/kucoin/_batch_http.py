"""Fund movement and batch endpoint mixins."""

import json
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    async def place_spot_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch orders."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(orders=orders),
        )

    async def place_spot_batch_limit_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch limit orders."""
        return await self._native_private(
            "place_spot_batch_limit_orders",
            self._native_params(orders=orders),
        )

    async def place_spot_batch_market_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch market orders."""
        return await self._native_private(
            "place_spot_batch_market_orders",
            self._native_params(orders=orders),
        )

    async def batch_cancel_uta_orders(
        self,
        trade_type: str,
        cancel_order_list: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Cancel 1 to 20 UTA orders; each item needs symbol and orderId or clientOid."""
        return await self._native_private(
            "batch_cancel_uta_orders",
            self._native_params(
                tradeType=trade_type,
                cancelOrderList=json.dumps(cancel_order_list),
            ),
        )

    async def place_futures_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place 1 to 20 futures orders with native order fields or product_symbol."""
        return await self._native_private(
            "place_futures_batch_orders", self._native_params(orders=json.dumps(orders))
        )

    async def cancel_futures_batch_orders(
        self,
        *,
        order_ids: list[str] | None = None,
        client_orders: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Cancel up to 10 orders; provide exactly one of order_ids or client_orders."""
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                orderIdsList=json.dumps(order_ids) if order_ids is not None else None,
                clientOidsList=json.dumps(client_orders) if client_orders is not None else None,
            ),
        )

    async def set_futures_batch_margin_mode(
        self, margin_mode: str, symbols: list[str]
    ) -> dict[str, Any]:
        """Change margin mode for a list of contracts."""
        return await self._native_private(
            "set_futures_batch_margin_mode",
            self._native_params(marginMode=margin_mode, symbols=json.dumps(symbols)),
        )

    async def place_spot_batch_orders_sync(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place orders using the endpoint that waits for the matching result."""
        return await self._native_private(
            "place_spot_batch_orders_sync",
            self._native_params(orders=orders),
        )
