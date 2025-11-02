"""
Bybit trading HTTP client module.

This module provides the TradeHTTP class for interacting with Bybit's
trading API endpoints, including order placement, modification, cancellation,
order history, execution lists, and spot margin trading functionality.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import SpotMarginTrade, Trade


class TradeHTTP(HTTPManager):
    """
    Bybit trading HTTP client.

    This class provides methods for interacting with Bybit's trading API
    endpoints, including:
    - Order placement (market, limit, post-only)
    - Order modification and cancellation
    - Order history and execution lists
    - Batch order operations
    - Spot margin trading functionality

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
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "side": side,
            "orderType": orderType,
            "qty": qty,
        }
        if price is not None:
            payload["price"] = price
        if isLeverage is not None:
            payload["isLeverage"] = str(isLeverage)
        if marketUnit is not None:
            payload["marketUnit"] = marketUnit
        if triggerDirection is not None:
            payload["triggerDirection"] = str(triggerDirection)
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
            payload["reduceOnly"] = str(reduceOnly)
        if closeOnTrigger is not None:
            payload["closeOnTrigger"] = str(closeOnTrigger)
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
            payload["positionIdx"] = str(positionIdx)

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
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if orderLinkId is not None:
            payload["orderLinkId"] = str(orderLinkId)
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
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)

        return await self._request(
            method="POST",
            path=Trade.CANCEL_ORDER,
            query=payload,
        )

    async def get_open_orders(
        self,
        product_symbol: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get open orders.

        Args:
            product_symbol: Optional product symbol to filter results
            limit: Maximum number of orders to return (default: 20)

        Returns:
            Dict containing open orders
        """
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)

        res = await self._request(
            method="GET",
            path=Trade.GET_OPEN_ORDERS,
            query=payload,
        )
        return res

    async def cancel_batch_orders(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Cancel multiple orders in batch.

        Args:
            request: List of order cancellation requests
            category: Order category (linear, option, spot, inverse)

        Returns:
            Dict containing batch cancellation results
        """
        payload = {
            "category": category,
            "request": request,
        }

        return await self._request(
            method="POST",
            path=Trade.CANCEL_BATCH_ORDERS,
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
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)

        return await self._request(
            method="POST",
            path=Trade.CANCEL_ALL_ORDERS,
            query=payload,
        )

    async def get_order_history(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        orderId: str | None = None,
        startTime: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get order history.

        Args:
            category: Order category (linear, option, spot, inverse)
            product_symbol: Optional product symbol to filter results
            orderId: Optional order ID to filter results
            startTime: Optional start time timestamp
            cursor: Optional cursor for pagination
            limit: Optional maximum number of records

        Returns:
            Dict containing order history
        """
        payload: dict[str, Any] = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if startTime is not None:
            payload["startTime"] = startTime
        if cursor is not None:
            payload["cursor"] = cursor
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=Trade.GET_ORDER_HISTORY,
            query=payload,
        )
        return res

    async def get_execution_list(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Get execution list.

        Args:
            category: Order category (linear, option, spot, inverse)
            product_symbol: Optional product symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of executions to return (default: 50)

        Returns:
            Dict containing execution list
        """
        payload: dict[str, Any] = {
            "category": category,
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Trade.GET_EXECUTION_LIST,
            query=payload,
        )
        return res

    async def place_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Place multiple orders in batch.

        Args:
            request: List of order placement requests
            category: Order category (linear, option, spot, inverse)

        Returns:
            Dict containing batch order placement results
        """
        payload = {
            "category": category,
            "request": request,
        }

        return await self._request(
            method="POST",
            path=Trade.BATCH_PLACE_ORDER,
            query=payload,
        )

    async def amend_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Amend multiple orders in batch.

        Args:
            request: List of order amendment requests
            category: Order category (linear, option, spot, inverse)

        Returns:
            Dict containing batch order amendment results
        """
        payload = {
            "category": category,
            "request": request,
        }

        return await self._request(
            method="POST",
            path=Trade.BATCH_AMEND_ORDER,
            query=payload,
        )

    async def get_borrow_quota(
        self,
        product_symbol: str,
        side: str,
    ) -> dict[str, Any]:
        """
        Get borrow quota information.

        Args:
            product_symbol: Product symbol
            side: Order side (Buy/Sell)

        Returns:
            Dict containing borrow quota information
        """
        payload = {
            "category": "spot",
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "side": side,
        }

        res = await self._request(
            method="GET",
            path=Trade.GET_BORROW_QUOTA,
            query=payload,
        )
        return res

    # spot margin trade http
    async def get_vip_margin_data(
        self,
        vipLevel: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Get VIP margin data.

        Args:
            vipLevel: Optional VIP level
            currency: Optional currency

        Returns:
            Dict containing VIP margin data
        """
        payload = {}
        if vipLevel is not None:
            payload["vipLevel"] = vipLevel
        if currency is not None:
            payload["currency"] = currency

        res = await self._request(
            method="GET",
            path=SpotMarginTrade.VIP_MARGIN_DATA,
            query=payload,
        )
        return res

    async def get_collateral(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Get collateral information.

        Args:
            currency: Optional currency

        Returns:
            Dict containing collateral information
        """
        payload = {}
        if currency is not None:
            payload["currency"] = currency

        res = await self._request(
            method="GET",
            path=SpotMarginTrade.GET_COLLATERAL,
            query=payload,
        )
        return res

    async def get_historical_interest_rate(
        self,
        currency: str,
        vipLevel: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get historical interest rate.

        Args:
            currency: Currency
            vipLevel: Optional VIP level
            startTime: Optional start time timestamp
            endTime: Optional end time timestamp

        Returns:
            Dict containing historical interest rate data
        """
        payload: dict[str, Any] = {
            "currency": currency,
        }
        if vipLevel is not None:
            payload["vipLevel"] = vipLevel
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime

        res = await self._request(
            method="GET",
            path=SpotMarginTrade.HISTORICAL_INTEREST,
            query=payload,
        )
        return res

    async def spot_margin_trade_toggle_margin_trade(
        self,
        spotMarginMode: str,
    ) -> dict[str, Any]:
        """
        Toggle spot margin trade mode.

        Args:
            spotMarginMode: Spot margin mode (1: open, 0: close)

        Returns:
            Dict containing toggle result
        """
        payload = {
            "spotMarginMode": spotMarginMode,
        }

        return await self._request(
            method="POST",
            path=SpotMarginTrade.TOGGLE_MARGIN_TRADE,
            query=payload,
        )

    async def spot_margin_trade_set_leverage(self, leverage: str) -> dict[str, Any]:
        """
        Set spot margin trade leverage.

        Args:
            leverage: Leverage value (2-10)

        Returns:
            Dict containing leverage setting result
        """
        payload = {
            "leverage": leverage,
        }

        return await self._request(
            method="POST",
            path=SpotMarginTrade.SET_LEVERAGE,
            query=payload,
        )

    async def get_status_and_leverage(self) -> dict[str, Any]:
        """
        Get spot margin trade status and leverage.

        Returns:
            Dict containing status and leverage information
        """
        res = await self._request(
            method="GET",
            path=SpotMarginTrade.STATUS_AND_LEVERAGE,
            query=None,
        )
        return res
