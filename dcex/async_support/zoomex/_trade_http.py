"""
Zoomex trading HTTP client module.

This module provides the TradeHTTP class for interacting with Zoomex's
trading API endpoints, including order placement, modification, cancellation,
and order management functionality.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import Trade


class TradeHTTP(HTTPManager):
    """
    Zoomex trading HTTP client.

    This class provides methods for interacting with Zoomex's trading API
    endpoints, including:
    - Order placement (market, limit, post-only)
    - Order modification and cancellation
    - Order management operations

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def place_order(
        self,
        product_symbol: str,
        side: str,
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
        """
        Place an order.

        Args:
            product_symbol: Product symbol
            side: Order side (Buy/Sell)
            orderType: Order type (Market/Limit/Stop/StopLimit)
            qty: Order quantity
            price: Optional order price (required for limit orders)
            isLeverage: Optional leverage flag
            marketUnit: Optional market unit
            triggerDirection: Optional trigger direction
            orderFilter: Optional order filter
            triggerPrice: Optional trigger price
            triggerBy: Optional trigger by
            orderIv: Optional order IV
            timeInForce: Optional time in force
            takeProfit: Optional take profit price
            stopLoss: Optional stop loss price
            tpTriggerBy: Optional TP trigger by
            slTriggerBy: Optional SL trigger by
            reduceOnly: Optional reduce only flag
            closeOnTrigger: Optional close on trigger flag
            tpslMode: Optional TP/SL mode
            tpLimitPrice: Optional TP limit price
            slLimitPrice: Optional SL limit price
            tpOrderType: Optional TP order type
            slOrderType: Optional SL order type
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.ZOOMEX, product_symbol),
            "side": side,
            "orderType": orderType,
            "qty": qty,
        }
        if product_symbol in {"BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP", "GMT-USDT-SWAP"}:
            payload["symbol"] = (
                self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol) + "-Perp"
            )
        else:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol)

        if price is not None:
            payload["price"] = price
        if isLeverage is not None:
            payload["isLeverage"] = isLeverage
        if marketUnit is not None:
            payload["marketUnit"] = marketUnit
        if triggerDirection is not None:
            payload["triggerDirection"] = triggerDirection
        if orderFilter is not None:
            payload["orderFilter"] = orderFilter
        if triggerPrice is not None:
            payload["triggerPrice"] = triggerPrice
        if triggerBy is not None:
            payload["triggerBy"] = triggerBy
        if orderIv is not None:
            payload["orderIv"] = orderIv
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if takeProfit is not None:
            payload["takeProfit"] = takeProfit
        if stopLoss is not None:
            payload["stopLoss"] = stopLoss
        if tpTriggerBy is not None:
            payload["tpTriggerBy"] = tpTriggerBy
        if slTriggerBy is not None:
            payload["slTriggerBy"] = slTriggerBy
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if closeOnTrigger is not None:
            payload["closeOnTrigger"] = closeOnTrigger
        if tpslMode is not None:
            payload["tpslMode"] = tpslMode
        if tpLimitPrice is not None:
            payload["tpLimitPrice"] = tpLimitPrice
        if slLimitPrice is not None:
            payload["slLimitPrice"] = slLimitPrice
        if tpOrderType is not None:
            payload["tpOrderType"] = tpOrderType
        if slOrderType is not None:
            payload["slOrderType"] = slOrderType
        if positionIdx is not None:
            payload["positionIdx"] = positionIdx

        return await self._request(
            method="POST",
            path=Trade.PLACE_ORDER,
            query=payload,
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a market order.

        Args:
            product_symbol: Product symbol
            side: Order side (Buy/Sell)
            qty: Order quantity
            reduceOnly: Optional reduce only flag
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderType="Market",
            qty=qty,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a market buy order.

        Args:
            product_symbol: Product symbol
            qty: Order quantity
            reduceOnly: Optional reduce only flag
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_market_order(
            product_symbol=product_symbol,
            side="Buy",
            qty=qty,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a market sell order.

        Args:
            product_symbol: Product symbol
            qty: Order quantity
            reduceOnly: Optional reduce only flag
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_market_order(
            product_symbol=product_symbol,
            side="Sell",
            qty=qty,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit order.

        Args:
            product_symbol: Product symbol
            side: Order side (Buy/Sell)
            qty: Order quantity
            price: Order price
            reduceOnly: Optional reduce only flag
            timeInForce: Optional time in force
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderType="Limit",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce=timeInForce,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
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
        """
        Place a limit buy order.

        Args:
            product_symbol: Product symbol
            qty: Order quantity
            price: Order price
            reduceOnly: Optional reduce only flag
            timeInForce: Optional time in force
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side="Buy",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce=timeInForce,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
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
        """
        Place a limit sell order.

        Args:
            product_symbol: Product symbol
            qty: Order quantity
            price: Order price
            reduceOnly: Optional reduce only flag
            timeInForce: Optional time in force
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side="Sell",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce=timeInForce,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only limit order.

        Args:
            product_symbol: Product symbol
            side: Order side (Buy/Sell)
            qty: Order quantity
            price: Order price
            reduceOnly: Optional reduce only flag
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side=side,
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce="PostOnly",
            isLeverage=isLeverage,
            positionIdx=positionIdx,
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
        """
        Place a post-only limit buy order.

        Args:
            product_symbol: Product symbol
            qty: Order quantity
            price: Order price
            reduceOnly: Optional reduce only flag
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="Buy",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
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
        """
        Place a post-only limit sell order.

        Args:
            product_symbol: Product symbol
            qty: Order quantity
            price: Order price
            reduceOnly: Optional reduce only flag
            isLeverage: Optional leverage flag
            positionIdx: Optional position index

        Returns:
            Dict containing order placement result
        """
        return await self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="Sell",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
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
        """
        Amend an existing order.

        Args:
            product_symbol: Product symbol
            orderId: Optional order ID
            orderLinkId: Optional order link ID
            orderIv: Optional order IV
            triggerPrice: Optional trigger price
            qty: Optional new quantity
            price: Optional new price
            tpslMode: Optional TP/SL mode
            takeProfit: Optional take profit price
            stopLoss: Optional stop loss price
            tpTriggerBy: Optional TP trigger by
            slTriggerBy: Optional SL trigger by
            triggerBy: Optional trigger by
            tpLimitPrice: Optional TP limit price
            slLimitPrice: Optional SL limit price

        Returns:
            Dict containing order amendment result
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.ZOOMEX, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = orderId
        if orderLinkId is not None:
            payload["orderLinkId"] = orderLinkId
        if orderIv is not None:
            payload["orderIv"] = orderIv
        if triggerPrice is not None:
            payload["triggerPrice"] = triggerPrice
        if qty is not None:
            payload["qty"] = qty
        if price is not None:
            payload["price"] = price
        if tpslMode is not None:
            payload["tpslMode"] = tpslMode
        if takeProfit is not None:
            payload["takeProfit"] = takeProfit
        if stopLoss is not None:
            payload["stopLoss"] = stopLoss
        if tpTriggerBy is not None:
            payload["tpTriggerBy"] = tpTriggerBy
        if slTriggerBy is not None:
            payload["slTriggerBy"] = slTriggerBy
        if triggerBy is not None:
            payload["triggerBy"] = triggerBy
        if tpLimitPrice is not None:
            payload["tpLimitPrice"] = tpLimitPrice
        if slLimitPrice is not None:
            payload["slLimitPrice"] = slLimitPrice

        return await self._request(
            method="POST",
            path=Trade.AMEND_ORDER,
            query=payload,
        )

    async def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel an existing order.

        Args:
            product_symbol: Product symbol
            orderId: Optional order ID to cancel

        Returns:
            Dict containing order cancellation result
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.ZOOMEX, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = orderId

        return await self._request(
            method="POST",
            path=Trade.CANCEL_ORDER,
            query=payload,
        )

    async def cancel_all_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all orders.

        Args:
            category: Order category (linear, option, spot, inverse)
            product_symbol: Optional product symbol to filter cancellation

        Returns:
            Dict containing cancellation result
        """
        payload: dict[str, Any] = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.ZOOMEX, product_symbol)

        return await self._request(
            method="POST",
            path=Trade.CANCEL_ALL_ORDERS,
            query=payload,
        )
