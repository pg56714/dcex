"""Authenticated Ondo order methods; no implicit live-trading calls."""

# ruff: noqa: ANN401

from typing import Any

from ._batch_http import TradeHTTPBatchHTTP
from ._http_manager import HTTPManager


class TradeHTTP(TradeHTTPBatchHTTP, HTTPManager):
    def get_orders(
        self,
        market: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "get_orders",
            market=market,
            status=status,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    def get_open_orders(self, market: str | None = None) -> Any:
        return self._native_private("get_open_orders", market=market)

    def get_fills_by_order(self, orderID: str) -> Any:
        return self._native_private("get_fills_by_order", orderID=orderID)

    def cancel_open_orders(self, market: str | None = None) -> Any:
        return self._native_private("cancel_open_orders", market=market)

    def place_twap_order(
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
        return self._native_private(
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

    def get_twap_order(self, orderID: str) -> Any:
        return self._native_private("get_twap_order", orderID=orderID)

    def cancel_twap_order(self, orderID: str) -> Any:
        return self._native_private("cancel_twap_order", orderID=orderID)

    def get_twap_order_fills(self, orderID: str) -> Any:
        return self._native_private("get_twap_order_fills", orderID=orderID)

    def get_running_twap_orders(self, market: str | None = None) -> Any:
        return self._native_private("get_running_twap_orders", market=market)

    def get_twap_order_history(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "get_twap_order_history",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    def export_orders_csv(
        self,
        market: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "export_orders_csv",
            market=market,
            status=status,
            startTime=startTime,
            endTime=endTime,
        )

    def export_fills_csv(
        self,
        market: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "export_fills_csv",
            market=market,
            startTime=startTime,
            endTime=endTime,
        )

    def get_stop_orders(self) -> Any:
        return self._native_private("get_stop_orders")

    def set_stop_order(
        self,
        market: str,
        positionDirection: str,
        type: str,
        triggerPrice: str,
        quantity: str | None = None,
        builderCode: dict[str, object] | None = None,
    ) -> Any:
        return self._native_private(
            "set_stop_order",
            market=market,
            positionDirection=positionDirection,
            type=type,
            triggerPrice=triggerPrice,
            quantity=quantity,
            builderCode=builderCode,
        )

    def remove_stop_order(self, market: str, type: str | None = None) -> Any:
        return self._native_private("remove_stop_order", market=market, type=type)

    def get_order(self, orderID: str) -> Any:
        return self._native_private("get_order", orderID=orderID)

    def place_order(self, **order: object) -> Any:
        return self._native_private("place_order", **order)

    def cancel_order(self, orderID: str) -> Any:
        return self._native_private("cancel_order", orderID=orderID)

    def cancel_all_orders(self, market: str | None = None) -> Any:
        return self._native_private("cancel_all_orders", market=market)

    def get_fills(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "get_fills",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )
