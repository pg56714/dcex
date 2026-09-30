"""Fund movement and batch endpoint mixins."""

from json import dumps
from typing import Any

from ...binance._batch import encode_batch_orders
from ._http_manager import HTTPManager


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    _native_private: Any

    _params: Any

    async def place_options_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place options orders; inspect both the ok and errors result arrays."""
        return await self._native_private(
            "place_options_batch_orders",
            self._params(orders=encode_batch_orders(orders)),
        )

    async def cancel_options_batch_orders(
        self,
        product_symbol: str,
        *,
        orderIds: list[int] | None = None,
        clientOrderIds: list[str] | None = None,
    ) -> dict[str, Any]:
        """Cancel options orders; inspect both the ok and errors result arrays."""
        return await self._native_private(
            "cancel_options_batch_orders",
            self._params(
                product_symbol=product_symbol,
                orderIds=dumps(orderIds) if orderIds is not None else None,
                clientOrderIds=dumps(clientOrderIds) if clientOrderIds is not None else None,
            ),
        )

    async def place_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Place a futures batch and return separate ``ok`` and ``errors`` lists.

        Each entry has its zero-based request ``index`` and full ``response``.
        Always inspect ``errors``: HTTP 200 does not mean every item succeeded.
        Quantity and price fields require decimal strings or ``Decimal`` values.
        Conditional orders must use the market's REST algo endpoint.
        """
        return await self._native_private(
            "place_futures_batch_orders",
            self._params(batchOrders=encode_batch_orders(orders), recvWindow=recv_window),
        )

    async def amend_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Amend a futures batch and return separate ``ok`` and ``errors`` lists.

        Each entry has its zero-based request ``index`` and full ``response``.
        Always inspect ``errors``: HTTP 200 does not mean every item succeeded.
        Quantity and price fields require decimal strings or ``Decimal`` values.
        Conditional orders must use the market's REST algo endpoint.
        """
        return await self._native_private(
            "amend_futures_batch_orders",
            self._params(batchOrders=encode_batch_orders(orders), recvWindow=recv_window),
        )

    async def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        *,
        order_ids: list[int] | None = None,
        client_order_ids: list[str] | None = None,
        recv_window: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Cancel a futures batch and return separate ``ok`` and ``errors`` lists.

        Each entry has its zero-based request ``index`` and full ``response``.
        Always inspect ``errors``: HTTP 200 does not mean every item succeeded.
        Conditional orders must use the market's REST algo endpoint.
        """
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._params(
                product_symbol=product_symbol,
                orderIdList=dumps(order_ids) if order_ids is not None else None,
                origClientOrderIdList=dumps(client_order_ids)
                if client_order_ids is not None
                else None,
                recvWindow=recv_window,
            ),
        )

    async def place_coin_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Place a coin_futures batch and return separate ``ok`` and ``errors`` lists.

        Each entry has its zero-based request ``index`` and full ``response``.
        Always inspect ``errors``: HTTP 200 does not mean every item succeeded.
        Quantity and price fields require decimal strings or ``Decimal`` values.
        Conditional orders must use the market's REST algo endpoint.
        """
        return await self._native_private(
            "place_coin_futures_batch_orders",
            self._params(batchOrders=encode_batch_orders(orders), recvWindow=recv_window),
        )

    async def amend_coin_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Amend a coin_futures batch and return separate ``ok`` and ``errors`` lists.

        Each entry has its zero-based request ``index`` and full ``response``.
        Always inspect ``errors``: HTTP 200 does not mean every item succeeded.
        Quantity and price fields require decimal strings or ``Decimal`` values.
        Conditional orders must use the market's REST algo endpoint.
        """
        return await self._native_private(
            "amend_coin_futures_batch_orders",
            self._params(batchOrders=encode_batch_orders(orders), recvWindow=recv_window),
        )

    async def cancel_coin_futures_batch_orders(
        self,
        product_symbol: str,
        *,
        order_ids: list[int] | None = None,
        client_order_ids: list[str] | None = None,
        recv_window: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Cancel a coin_futures batch and return separate ``ok`` and ``errors`` lists.

        Each entry has its zero-based request ``index`` and full ``response``.
        Always inspect ``errors``: HTTP 200 does not mean every item succeeded.
        Conditional orders must use the market's REST algo endpoint.
        """
        return await self._native_private(
            "cancel_coin_futures_batch_orders",
            self._params(
                product_symbol=product_symbol,
                orderIdList=dumps(order_ids) if order_ids is not None else None,
                origClientOrderIdList=dumps(client_order_ids)
                if client_order_ids is not None
                else None,
                recvWindow=recv_window,
            ),
        )
