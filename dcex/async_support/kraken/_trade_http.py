"""Kraken private trade async HTTP client."""
# ruff: noqa: ASYNC109

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Kraken private trading operations."""

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        ordertype: str,
        volume: str,
        price: str | None = None,
        price2: str | None = None,
        displayvol: str | None = None,
        leverage: str | None = None,
        oflags: str | None = None,
        timeinforce: str | None = None,
        expiretm: str | None = None,
        starttm: str | None = None,
        asset_class: str | None = None,
        trigger: str | None = None,
        stptype: str | None = None,
        reduce_only: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
        deadline: str | None = None,
        broker: str | None = None,
        close_ordertype: str | None = None,
        close_price: str | None = None,
        close_price2: str | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot order."""
        if userref is not None and cl_ord_id is not None:
            raise ValueError("userref and cl_ord_id are mutually exclusive.")
        return await self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                ordertype=ordertype,
                volume=volume,
                price=price,
                price2=price2,
                displayvol=displayvol,
                leverage=leverage,
                oflags=oflags,
                timeinforce=timeinforce,
                expiretm=expiretm,
                starttm=starttm,
                asset_class=asset_class,
                trigger=trigger,
                stptype=stptype,
                reduce_only=reduce_only,
                userref=userref,
                cl_ord_id=cl_ord_id,
                validate=validate,
                deadline=deadline,
                broker=broker,
                **{
                    "close[ordertype]": close_ordertype,
                    "close[price]": close_price,
                    "close[price2]": close_price2,
                },
            ),
        )

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market order."""
        return await self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                volume=volume,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market buy order."""
        return await self._native_private(
            "place_spot_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        volume: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot market sell order."""
        return await self._native_private(
            "place_spot_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        oflags: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit order."""
        return await self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                volume=volume,
                price=price,
                timeinforce=timeinforce,
                oflags=oflags,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit buy order."""
        return await self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                timeinforce=timeinforce,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        timeinforce: str | None = None,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot limit sell order."""
        return await self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                timeinforce=timeinforce,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit order."""
        return await self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                volume=volume,
                price=price,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit buy order."""
        return await self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        volume: str,
        price: str,
        cl_ord_id: str | None = None,
        validate: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken spot post-only limit sell order."""
        return await self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                volume=volume,
                price=price,
                cl_ord_id=cl_ord_id,
                validate=validate,
            ),
        )

    async def get_spot_open_orders(
        self,
        trades: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot open orders."""
        return await self._native_private(
            "get_spot_open_orders",
            self._native_params(
                trades=trades,
                userref=userref,
                cl_ord_id=cl_ord_id,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    async def get_spot_closed_orders(
        self,
        trades: bool | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        closetime: str | None = None,
        consolidate_taker: bool | None = None,
        without_count: bool | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot closed orders."""
        return await self._native_private(
            "get_spot_closed_orders",
            self._native_params(
                trades=trades,
                userref=userref,
                cl_ord_id=cl_ord_id,
                start=start,
                end=end,
                ofs=ofs,
                closetime=closetime,
                consolidate_taker=consolidate_taker,
                without_count=without_count,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    async def get_spot_orders(
        self,
        txid: str,
        trades: bool | None = None,
        userref: int | None = None,
        consolidate_taker: bool | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Query Kraken spot order info by transaction id."""
        return await self._native_private(
            "get_spot_orders",
            self._native_params(
                txid=txid,
                trades=trades,
                userref=userref,
                consolidate_taker=consolidate_taker,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    async def get_spot_trade_history(
        self,
        type_: str | None = None,
        trades: bool | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        without_count: bool | None = None,
        consolidate_taker: bool | None = None,
        ledgers: bool | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trades/fills history."""
        return await self._native_private(
            "get_spot_trade_history",
            self._native_params(
                type_=type_,
                trades=trades,
                start=start,
                end=end,
                ofs=ofs,
                without_count=without_count,
                consolidate_taker=consolidate_taker,
                ledgers=ledgers,
                rebase_multiplier=rebase_multiplier,
            ),
        )

    async def cancel_spot_order(
        self,
        txid: str | None = None,
        userref: int | None = None,
        cl_ord_id: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Kraken spot order."""
        if sum(value is not None for value in (txid, userref, cl_ord_id)) != 1:
            raise ValueError("Specify exactly one of txid, userref, or cl_ord_id.")
        return await self._native_private(
            "cancel_spot_order",
            self._native_params(txid=txid, userref=userref, cl_ord_id=cl_ord_id),
        )

    async def cancel_spot_all_orders(self) -> dict[str, Any]:
        """Cancel all Kraken spot open orders."""
        return await self._native_private("cancel_spot_all_orders", [])

    async def cancel_spot_all_orders_after(  # noqa: ASYNC109
        self, timeout: str
    ) -> dict[str, Any]:
        """Set Kraken's spot cancel-all dead-man switch timeout in seconds."""
        return await self._native_private(
            "cancel_spot_all_orders_after", self._native_params(timeout=timeout)
        )

    async def get_spot_websocket_token(self) -> dict[str, Any]:
        """Retrieve a Kraken authenticated WebSocket token."""
        return await self._native_private("get_spot_websocket_token", [])

    async def place_futures_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: int | str,
        limitPrice: str | None = None,
        stopPrice: str | None = None,
        cliOrdId: str | None = None,
        triggerSignal: str | None = None,
        reduceOnly: bool | None = None,
        processBefore: str | None = None,
        trailingStopMaxDeviation: str | None = None,
        trailingStopDeviationUnit: str | None = None,
        limitPriceOffsetValue: str | None = None,
        limitPriceOffsetUnit: str | None = None,
        broker: str | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures order."""
        return await self._native_private(
            "place_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                size=size,
                limitPrice=limitPrice,
                stopPrice=stopPrice,
                cliOrdId=cliOrdId,
                triggerSignal=triggerSignal,
                reduceOnly=reduceOnly,
                processBefore=processBefore,
                trailingStopMaxDeviation=trailingStopMaxDeviation,
                trailingStopDeviationUnit=trailingStopDeviationUnit,
                limitPriceOffsetValue=limitPriceOffsetValue,
                limitPriceOffsetUnit=limitPriceOffsetUnit,
                broker=broker,
            ),
        )

    async def place_futures_market_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market order."""
        return await self._native_private(
            "place_futures_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_market_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market buy order."""
        return await self._native_private(
            "place_futures_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures market sell order."""
        return await self._native_private(
            "place_futures_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit order."""
        return await self._native_private(
            "place_futures_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit buy order."""
        return await self._native_private(
            "place_futures_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures limit sell order."""
        return await self._native_private(
            "place_futures_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit order."""
        return await self._native_private(
            "place_futures_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit buy order."""
        return await self._native_private(
            "place_futures_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        cliOrdId: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a Kraken Futures post-only limit sell order."""
        return await self._native_private(
            "place_futures_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                cliOrdId=cliOrdId,
                reduceOnly=reduceOnly,
            ),
        )

    async def get_futures_open_orders(self) -> dict[str, Any]:
        """Retrieve Kraken Futures open orders."""
        return await self._native_private("get_futures_open_orders", [])

    async def get_futures_order_status(
        self,
        orderIds: list[str] | None = None,
        cliOrdIds: list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures order status for specific order IDs."""
        return await self._native_private(
            "get_futures_order_status",
            self._native_params(orderIds=orderIds, cliOrdIds=cliOrdIds),
        )

    async def cancel_futures_order(
        self,
        order_id: str | None = None,
        cliOrdId: str | None = None,
        processBefore: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Kraken Futures order."""
        if sum(value is not None for value in (order_id, cliOrdId)) != 1:
            raise ValueError("Specify exactly one of order_id or cliOrdId.")
        return await self._native_private(
            "cancel_futures_order",
            self._native_params(
                order_id=order_id,
                cliOrdId=cliOrdId,
                processBefore=processBefore,
            ),
        )

    async def cancel_futures_all_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all Kraken Futures open orders, optionally filtered by product."""
        return await self._native_private(
            "cancel_futures_all_orders",
            self._native_params(product_symbol=product_symbol),
        )
