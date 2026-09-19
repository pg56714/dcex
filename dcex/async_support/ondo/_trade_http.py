"""Asynchronous authenticated Ondo order methods."""

# ruff: noqa: ANN401

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    async def get_orders(
        self,
        market: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:
        return await self._native_private(
            "get_orders",
            market=market,
            status=status,
            limit=limit,
            cursor=cursor,
        )

    async def get_open_orders(self, market: str | None = None) -> Any:
        return await self._native_private("get_open_orders", market=market)

    async def get_fills_by_order(self, orderID: str) -> Any:
        return await self._native_private("get_fills_by_order", orderID=orderID)

    async def cancel_open_orders(self, market: str | None = None) -> Any:
        return await self._native_private("cancel_open_orders", market=market)

    async def place_batch_orders(self, orders: list[dict[str, object]]) -> Any:
        return await self._native_private("place_batch_orders", orders=orders)

    async def batch_cancel_orders(self, orderIDs: list[str]) -> Any:
        """Ondo expects one comma-separated orderIDs query value."""
        if not orderIDs or any(not order_id or "," in order_id for order_id in orderIDs):
            raise ValueError("orderIDs must contain nonempty IDs without commas.")
        return await self._native_private("batch_cancel_orders", orderIDs=",".join(orderIDs))

    async def place_twap_order(
        self,
        market: str,
        side: str,
        size: str,
        runningTime: int,
        frequency: int,
        reduceOnly: bool | None = None,
        maxPrice: str | None = None,
        minPrice: str | None = None,
    ) -> Any:
        return await self._native_private(
            "place_twap_order",
            market=market,
            side=side,
            size=size,
            runningTime=runningTime,
            frequency=frequency,
            reduceOnly=reduceOnly,
            maxPrice=maxPrice,
            minPrice=minPrice,
        )

    async def get_twap_order(self, orderID: str) -> Any:
        return await self._native_private("get_twap_order", orderID=orderID)

    async def cancel_twap_order(self, orderID: str) -> Any:
        return await self._native_private("cancel_twap_order", orderID=orderID)

    async def get_twap_order_fills(self, orderID: str) -> Any:
        return await self._native_private("get_twap_order_fills", orderID=orderID)

    async def get_running_twap_orders(self, market: str | None = None) -> Any:
        return await self._native_private("get_running_twap_orders", market=market)

    async def get_twap_order_history(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return await self._native_private(
            "get_twap_order_history",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    async def export_orders_csv(
        self,
        market: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return await self._native_private(
            "export_orders_csv",
            market=market,
            status=status,
            startTime=startTime,
            endTime=endTime,
        )

    async def export_fills_csv(
        self,
        market: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return await self._native_private(
            "export_fills_csv",
            market=market,
            startTime=startTime,
            endTime=endTime,
        )

    async def get_stop_orders(self) -> Any:
        return await self._native_private("get_stop_orders")

    async def set_stop_order(
        self,
        market: str,
        positionDirection: str,
        type: str,
        triggerPrice: str,
        quantity: str | None = None,
        builderCode: dict[str, object] | None = None,
    ) -> Any:
        return await self._native_private(
            "set_stop_order",
            market=market,
            positionDirection=positionDirection,
            type=type,
            triggerPrice=triggerPrice,
            quantity=quantity,
            builderCode=builderCode,
        )

    async def remove_stop_order(self, market: str, type: str | None = None) -> Any:
        return await self._native_private("remove_stop_order", market=market, type=type)

    async def get_order(self, orderID: str) -> Any:
        return await self._native_private("get_order", orderID=orderID)

    async def place_order(self, **order: object) -> Any:
        return await self._native_private("place_order", **order)

    async def cancel_order(self, orderID: str) -> Any:
        return await self._native_private("cancel_order", orderID=orderID)

    async def cancel_all_orders(self, market: str | None = None) -> Any:
        return await self._native_private("cancel_all_orders", market=market)

    async def get_fills(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Any:
        return await self._native_private(
            "get_fills",
            market=market,
            limit=limit,
            cursor=cursor,
        )
