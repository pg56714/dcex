"""Async Bybit trade HTTP client backed by Rust."""

from typing import Any

from ...enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Bybit trading operations."""

    async def place_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderType: str,
        qty: str,
        price: str | None = None,
        isLeverage: int | None = None,
        marketUnit: str | None = None,
        rpiTakerAccess: bool | None = None,
        slippageToleranceType: str | None = None,
        slippageTolerance: str | None = None,
        triggerDirection: int | None = None,
        orderFilter: str | None = None,
        triggerPrice: str | None = None,
        triggerBy: str | None = None,
        orderIv: str | None = None,
        timeInForce: str | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        reduceOnly: bool | None = None,
        closeOnTrigger: bool | None = None,
        tpslMode: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
        tpOrderType: str | None = None,
        slOrderType: str | None = None,
        positionIdx: int | None = None,
        orderLinkId: str | None = None,
        smpType: str | None = None,
        mmp: bool | None = None,
        bboSideType: str | None = None,
        bboLevel: int | None = None,
    ) -> dict[str, Any]:
        """Place an order."""
        return await self._native_private(
            "place_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                price=price,
                isLeverage=isLeverage,
                marketUnit=marketUnit,
                rpiTakerAccess=rpiTakerAccess,
                slippageToleranceType=slippageToleranceType,
                slippageTolerance=slippageTolerance,
                triggerDirection=triggerDirection,
                orderFilter=orderFilter,
                triggerPrice=triggerPrice,
                triggerBy=triggerBy,
                orderIv=orderIv,
                timeInForce=timeInForce,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                tpTriggerBy=tpTriggerBy,
                slTriggerBy=slTriggerBy,
                reduceOnly=reduceOnly,
                closeOnTrigger=closeOnTrigger,
                tpslMode=tpslMode,
                tpLimitPrice=tpLimitPrice,
                slLimitPrice=slLimitPrice,
                tpOrderType=tpOrderType,
                slOrderType=slOrderType,
                positionIdx=positionIdx,
                orderLinkId=orderLinkId,
                smpType=smpType,
                mmp=mmp,
                bboSideType=bboSideType,
                bboLevel=bboLevel,
            ),
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market order."""
        return await self._native_private(
            "place_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market buy order."""
        return await self._native_private(
            "place_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market sell order."""
        return await self._native_private(
            "place_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a limit order."""
        return await self._native_private(
            "place_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                timeInForce=timeInForce,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a limit buy order."""
        return await self._native_private(
            "place_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                timeInForce=timeInForce,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a limit sell order."""
        return await self._native_private(
            "place_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                timeInForce=timeInForce,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit order."""
        return await self._native_private(
            "place_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit buy order."""
        return await self._native_private(
            "place_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit sell order."""
        return await self._native_private(
            "place_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def amend_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderIv: str | None = None,
        triggerPrice: str | None = None,
        qty: str | None = None,
        price: str | None = None,
        tpslMode: str | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        triggerBy: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
    ) -> dict[str, Any]:
        """Amend an existing order."""
        return await self._native_private(
            "amend_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderIv=orderIv,
                triggerPrice=triggerPrice,
                qty=qty,
                price=price,
                tpslMode=tpslMode,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                tpTriggerBy=tpTriggerBy,
                slTriggerBy=slTriggerBy,
                triggerBy=triggerBy,
                tpLimitPrice=tpLimitPrice,
                slLimitPrice=slLimitPrice,
            ),
        )

    async def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderFilter: str | None = None,
    ) -> dict[str, Any]:
        """Cancel an order."""
        return await self._native_private(
            "cancel_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderFilter=orderFilter,
            ),
        )

    async def get_open_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        settleCoin: str | None = None,
        baseCoin: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        openOnly: int | None = None,
        orderFilter: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get open orders."""
        return await self._native_private(
            "get_open_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                settleCoin=settleCoin,
                baseCoin=baseCoin,
                orderId=orderId,
                orderLinkId=orderLinkId,
                openOnly=openOnly,
                orderFilter=orderFilter,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def cancel_batch_orders(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Cancel multiple orders in batch."""
        return await self._native_private(
            "cancel_batch_orders",
            self._native_params(request=request, category=category),
        )

    async def cancel_all_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        orderFilter: str | None = None,
        stopOrderType: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all orders."""
        return await self._native_private(
            "cancel_all_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                orderFilter=orderFilter,
                stopOrderType=stopOrderType,
            ),
        )

    async def get_order_history(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderFilter: str | None = None,
        orderStatus: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get order history."""
        return await self._native_private(
            "get_order_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderFilter=orderFilter,
                orderStatus=orderStatus,
                startTime=startTime,
                endTime=endTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def get_execution_list(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        execType: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get execution list."""
        return await self._native_private(
            "get_execution_list",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                orderId=orderId,
                orderLinkId=orderLinkId,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                startTime=startTime,
                endTime=endTime,
                execType=execType,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def place_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Place multiple orders in batch."""
        return await self._native_private(
            "place_batch_order",
            self._native_params(request=request, category=category),
        )

    async def amend_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Amend multiple orders in batch."""
        return await self._native_private(
            "amend_batch_order",
            self._native_params(request=request, category=category),
        )

    async def get_borrow_quota(
        self,
        product_symbol: str,
        side: OrderSide | str,
    ) -> dict[str, Any]:
        """Get borrow quota for spot trading."""
        return await self._native_private(
            "get_borrow_quota",
            self._native_params(product_symbol=product_symbol, side=side),
        )

    async def get_vip_margin_data(
        self,
        vipLevel: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get VIP margin data."""
        return await self._native_private(
            "get_vip_margin_data",
            self._native_params(vipLevel=vipLevel, currency=currency),
        )

    async def get_collateral(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get collateral information."""
        return await self._native_private(
            "get_collateral",
            self._native_params(currency=currency),
        )

    async def get_historical_interest_rate(
        self,
        currency: str,
        vipLevel: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get historical interest rate."""
        return await self._native_private(
            "get_historical_interest_rate",
            self._native_params(
                currency=currency,
                vipLevel=vipLevel,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_status_and_leverage(self) -> dict[str, Any]:
        """Get spot margin trading status and leverage."""
        return await self._native_private("get_status_and_leverage", [])

    async def pre_check_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderType: str,
        qty: str,
        **params: object,
    ) -> dict[str, Any]:
        """Preview UTA margin impact before submitting a Bybit order."""
        return await self._native_private(
            "pre_check_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                **params,
            ),
        )

    async def set_disconnected_cancel_all(
        self,
        timeWindow: int,
        product: str | None = None,
    ) -> dict[str, Any]:
        """Configure Bybit disconnect protection without placing an order."""
        return await self._native_private(
            "set_disconnected_cancel_all",
            self._native_params(timeWindow=timeWindow, product=product),
        )
