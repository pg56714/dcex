"""Bybit trade HTTP client backed by Rust."""

from typing import Any

from ..enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for Bybit trading operations."""

    def place_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderType: str,
        qty: str,
        price: str | None = None,
        isLeverage: int | None = None,
        marketUnit: str | None = None,
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
    ) -> dict[str, Any]:
        """Place an order."""
        return self._native_private(
            "place_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                price=price,
                isLeverage=isLeverage,
                marketUnit=marketUnit,
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
            ),
        )

    def place_market_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market order."""
        return self._native_private(
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

    def place_market_buy_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market buy order."""
        return self._native_private(
            "place_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    def place_market_sell_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market sell order."""
        return self._native_private(
            "place_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    def place_limit_order(
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
        return self._native_private(
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

    def place_limit_buy_order(
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
        return self._native_private(
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

    def place_limit_sell_order(
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
        return self._native_private(
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

    def place_post_only_limit_order(
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
        return self._native_private(
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

    def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit buy order."""
        return self._native_private(
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

    def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit sell order."""
        return self._native_private(
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

    def amend_order(
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
        return self._native_private(
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

    def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
    ) -> dict[str, Any]:
        """Cancel an order."""
        return self._native_private(
            "cancel_order",
            self._native_params(product_symbol=product_symbol, orderId=orderId),
        )

    def get_open_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        settleCoin: str | None = None,
        baseCoin: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get open orders."""
        return self._native_private(
            "get_open_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                settleCoin=settleCoin,
                baseCoin=baseCoin,
                limit=limit,
            ),
        )

    def cancel_batch_orders(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Cancel multiple orders in batch."""
        return self._native_private(
            "cancel_batch_orders",
            self._native_params(request=request, category=category),
        )

    def cancel_all_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all orders."""
        return self._native_private(
            "cancel_all_orders",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    def get_order_history(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        orderId: str | None = None,
        startTime: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get order history."""
        return self._native_private(
            "get_order_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    def get_execution_list(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Get execution list."""
        return self._native_private(
            "get_execution_list",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=startTime,
                limit=limit,
            ),
        )

    def place_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Place multiple orders in batch."""
        return self._native_private(
            "place_batch_order",
            self._native_params(request=request, category=category),
        )

    def amend_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Amend multiple orders in batch."""
        return self._native_private(
            "amend_batch_order",
            self._native_params(request=request, category=category),
        )

    def get_borrow_quota(
        self,
        product_symbol: str,
        side: OrderSide | str,
    ) -> dict[str, Any]:
        """Get borrow quota for spot trading."""
        return self._native_private(
            "get_borrow_quota",
            self._native_params(product_symbol=product_symbol, side=side),
        )

    def get_vip_margin_data(
        self,
        vipLevel: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get VIP margin data."""
        return self._native_private(
            "get_vip_margin_data",
            self._native_params(vipLevel=vipLevel, currency=currency),
        )

    def get_collateral(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get collateral information."""
        return self._native_private(
            "get_collateral",
            self._native_params(currency=currency),
        )

    def get_historical_interest_rate(
        self,
        currency: str,
        vipLevel: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get historical interest rate."""
        return self._native_private(
            "get_historical_interest_rate",
            self._native_params(
                currency=currency,
                vipLevel=vipLevel,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_status_and_leverage(self) -> dict[str, Any]:
        """Get spot margin trading status and leverage."""
        return self._native_private("get_status_and_leverage", [])
