"""Asynchronous authenticated Ondo Spot trading, transfer and builder-code methods."""

# ruff: noqa: ANN401

from typing import Any

from ..._operation_guards import require_scope
from ._http_manager import HTTPManager


class SpotTradeHTTP(HTTPManager):
    async def place_spot_order(
        self,
        market: str,
        side: str,
        size: str,
        price: str | None = None,
        type: str | None = None,  # noqa: A002
        timeInForce: str | None = None,
        postOnly: bool | None = None,
        clientOrderId: str | None = None,
    ) -> Any:
        """
        POST /v1/spot/orders: market, side and base ``size``; limit orders need ``price``.

        Spot orders take no quoteSize. Client order IDs are not idempotency keys.
        """
        return await self._native_private(
            "place_spot_order",
            market=market,
            side=side,
            size=size,
            price=price,
            type=type,
            timeInForce=timeInForce,
            postOnly=postOnly,
            clientOrderId=clientOrderId,
        )

    async def place_spot_order_delayed(
        self,
        market: str,
        side: str,
        size: str,
        price: str | None = None,
        type: str | None = None,  # noqa: A002
        timeInForce: str | None = None,
        postOnly: bool | None = None,
        clientOrderId: str | None = None,
    ) -> Any:
        """POST /v1/spot/orders/delayed, when the server directs delayed placement."""
        return await self._native_private(
            "place_spot_order_delayed",
            market=market,
            side=side,
            size=size,
            price=price,
            type=type,
            timeInForce=timeInForce,
            postOnly=postOnly,
            clientOrderId=clientOrderId,
        )

    async def place_spot_batch_orders(self, orders: list[dict[str, Any]]) -> Any:
        """POST /v1/spot/orders/batch with 1 to 20 orders; inspect addedOrders and failedOrders."""
        return await self._native_private("place_spot_batch_orders", orders=orders)

    async def place_spot_batch_orders_delayed(self, orders: list[dict[str, Any]]) -> Any:
        """POST /v1/spot/orders/batch/delayed with 1 to 20 orders."""
        return await self._native_private("place_spot_batch_orders_delayed", orders=orders)

    async def cancel_spot_batch_orders(self, orderIDs: list[str] | str) -> Any:
        """DELETE /v1/spot/orders/batch; IDs may use the ``client:`` prefix."""
        return await self._native_private("cancel_spot_batch_orders", orderIDs=orderIDs)

    async def get_spot_orders(
        self,
        market: str | None = None,
        status: str | None = None,
        orderType: str | None = None,
        hasFill: bool | None = None,
        activeOnly: bool | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        """GET /v1/spot/orders."""
        return await self._native_private(
            "get_spot_orders",
            market=market,
            status=status,
            orderType=orderType,
            hasFill=hasFill,
            activeOnly=activeOnly,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    async def cancel_spot_orders(self, market: str | None = None, all_symbols: bool = False) -> Any:
        """DELETE /v1/spot/orders for one market, or every open Spot order with all_symbols=True."""
        require_scope(market, all_symbols)
        return await self._native_private(
            "cancel_spot_orders", market=market, all_symbols=all_symbols
        )

    async def get_spot_order(self, orderID: str) -> Any:
        """GET /v1/spot/orders/{orderID}."""
        return await self._native_private("get_spot_order", orderID=orderID)

    async def cancel_spot_order(self, orderID: str) -> Any:
        """DELETE /v1/spot/orders/{orderID}."""
        return await self._native_private("cancel_spot_order", orderID=orderID)

    async def get_spot_order_fills(self, orderID: str) -> Any:
        """GET /v1/spot/orders/{orderID}/fills."""
        return await self._native_private("get_spot_order_fills", orderID=orderID)

    async def get_spot_fills(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        """GET /v1/spot/fills."""
        return await self._native_private(
            "get_spot_fills",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    async def export_spot_orders_csv(
        self,
        market: str | None = None,
        status: str | None = None,
        orderType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        """GET /v1/spot/orders/csv."""
        return await self._native_private(
            "export_spot_orders_csv",
            market=market,
            status=status,
            orderType=orderType,
            startTime=startTime,
            endTime=endTime,
        )

    async def export_spot_fills_csv(
        self,
        market: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        """GET /v1/spot/fills/csv."""
        return await self._native_private(
            "export_spot_fills_csv",
            market=market,
            status=status,
            startTime=startTime,
            endTime=endTime,
        )

    async def get_spot_candles(
        self,
        market: str,
        resolution: str,
        to_time: int,
        from_time: int | None = None,
        countback: int | None = None,
    ) -> Any:
        """GET /v1/spot/candles up to ``to_time``; give exactly one of from_time or countback."""
        return await self._native_private(
            "get_spot_candles",
            market=market,
            resolution=resolution,
            countback=countback,
            **{"from": from_time, "to": to_time},
        )

    async def get_spot_balances(self) -> Any:
        """GET /v1/spot/balances."""
        return await self._native_private("get_spot_balances")

    async def get_spot_transfers(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        """GET /v1/spot/transfers."""
        return await self._native_private(
            "get_spot_transfers", limit=limit, cursor=cursor, startTime=startTime, endTime=endTime
        )

    async def create_spot_transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        symbol: str,
        amount: str,
        account_id: str | None = None,
    ) -> Any:
        """
        POST /v1/spot/transfers between spot and the main or margin wallet of one account.

        No idempotency key exists: reconcile balances after an uncertain result before retrying.
        """
        side = {"id": account_id} if account_id is not None else {}
        return await self._native_private(
            "create_spot_transfer",
            from_wallet={**side, "wallet": from_wallet},
            to_wallet={**side, "wallet": to_wallet},
            symbol=symbol,
            amount=amount,
        )

    async def get_builder_code_stats(self, startTime: int, endTime: int | None = None) -> Any:
        """GET /v1/builder_code/stats for the builder code owned by this account."""
        return await self._native_private(
            "get_builder_code_stats", startTime=startTime, endTime=endTime
        )

    async def get_builder_code_fills(self) -> Any:
        """GET /v1/builder_code/fills: up to the 200 most recent builder-code fills."""
        return await self._native_private("get_builder_code_fills")
