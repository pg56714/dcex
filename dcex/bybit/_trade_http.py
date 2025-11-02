"""
Bybit Trade HTTP client.

This module provides HTTP client functionality for trading operations
on the Bybit exchange, including order management, execution queries,
and spot margin trading functionality.
"""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import SpotMarginTrade, Trade


class TradeHTTP(HTTPManager):
    """
    HTTP client for Bybit trading operations.

    This class handles all trading-related API requests including:
    - Order placement and management
    - Order cancellation (single and batch)
    - Order history and execution queries
    - Borrow quota checks
    - Spot margin trading operations
    """

    def place_order(
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
            product_symbol: Product symbol to trade
            side: Order side ("Buy" or "Sell")
            orderType: Order type ("Market", "Limit", etc.)
            qty: Order quantity
            price: Order price (required for limit orders)
            isLeverage: Whether to use leverage (0 or 1)
            marketUnit: Market unit for the order
            triggerDirection: Trigger direction for conditional orders
            orderFilter: Order filter
            triggerPrice: Trigger price for conditional orders
            triggerBy: Trigger by price type
            orderIv: Order implied volatility
            timeInForce: Time in force ("GTC", "IOC", "FOK")
            takeProfit: Take profit price
            stopLoss: Stop loss price
            tpTriggerBy: Take profit trigger by
            slTriggerBy: Stop loss trigger by
            reduceOnly: Whether this is a reduce-only order
            closeOnTrigger: Whether to close on trigger
            tpslMode: TP/SL mode
            tpLimitPrice: Take profit limit price
            slLimitPrice: Stop loss limit price
            tpOrderType: Take profit order type
            slOrderType: Stop loss order type
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
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

        return self._request(
            method="POST",
            path=Trade.PLACE_ORDER,
            query=payload,
        )

    def place_market_order(
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
            product_symbol: Product symbol to trade
            side: Order side ("Buy" or "Sell")
            qty: Order quantity
            reduceOnly: Whether this is a reduce-only order
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderType="Market",
            qty=qty,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    def place_market_buy_order(
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
            product_symbol: Product symbol to buy
            qty: Order quantity
            reduceOnly: Whether this is a reduce-only order
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_market_order(
            product_symbol=product_symbol,
            side="Buy",
            qty=qty,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    def place_market_sell_order(
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
            product_symbol: Product symbol to sell
            qty: Order quantity
            reduceOnly: Whether this is a reduce-only order
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_market_order(
            product_symbol=product_symbol,
            side="Sell",
            qty=qty,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    def place_limit_order(
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
            product_symbol: Product symbol to trade
            side: Order side ("Buy" or "Sell")
            qty: Order quantity
            price: Order price
            reduceOnly: Whether this is a reduce-only order
            timeInForce: Time in force ("GTC", "IOC", "FOK")
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_order(
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
        """
        Place a limit buy order.

        Args:
            product_symbol: Product symbol to buy
            qty: Order quantity
            price: Order price
            reduceOnly: Whether this is a reduce-only order
            timeInForce: Time in force ("GTC", "IOC", "FOK")
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_limit_order(
            product_symbol=product_symbol,
            side="Buy",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce=timeInForce,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
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
        """
        Place a limit sell order.

        Args:
            product_symbol: Product symbol to sell
            qty: Order quantity
            price: Order price
            reduceOnly: Whether this is a reduce-only order
            timeInForce: Time in force ("GTC", "IOC", "FOK")
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_limit_order(
            product_symbol=product_symbol,
            side="Sell",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce=timeInForce,
            isLeverage=isLeverage,
            positionIdx=positionIdx,
        )

    def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        timeInForce: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only limit order.

        Args:
            product_symbol: Product symbol to trade
            side: Order side ("Buy" or "Sell")
            qty: Order quantity
            price: Order price
            reduceOnly: Whether this is a reduce-only order
            isLeverage: Whether to use leverage (0 or 1)
            timeInForce: Time in force (defaults to "PostOnly")

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_limit_order(
            product_symbol=product_symbol,
            side=side,
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            timeInForce="PostOnly",
            isLeverage=isLeverage,
            positionIdx=None,
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
        """
        Place a post-only limit buy order.

        Args:
            product_symbol: Product symbol to buy
            qty: Order quantity
            price: Order price
            reduceOnly: Whether this is a reduce-only order
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="Buy",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
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
        """
        Place a post-only limit sell order.

        Args:
            product_symbol: Product symbol to sell
            qty: Order quantity
            price: Order price
            reduceOnly: Whether this is a reduce-only order
            isLeverage: Whether to use leverage (0 or 1)
            positionIdx: Position index

        Returns:
            dict[str, Any]: API response containing order information
        """
        return self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="Sell",
            qty=qty,
            price=price,
            reduceOnly=reduceOnly,
            isLeverage=isLeverage,
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
        """
        Amend an existing order.

        Args:
            product_symbol: Product symbol
            orderId: Order ID to amend
            orderLinkId: Order link ID to amend
            orderIv: Order implied volatility
            triggerPrice: Trigger price for conditional orders
            qty: New order quantity
            price: New order price
            tpslMode: TP/SL mode
            takeProfit: Take profit price
            stopLoss: Stop loss price
            tpTriggerBy: Take profit trigger by
            slTriggerBy: Stop loss trigger by
            triggerBy: Trigger by price type
            tpLimitPrice: Take profit limit price
            slLimitPrice: Stop loss limit price

        Returns:
            dict[str, Any]: API response confirming the amendment
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
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

        return self._request(
            method="POST",
            path=Trade.AMEND_ORDER,
            query=payload,
        )

    def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel an order.

        Args:
            product_symbol: Product symbol
            orderId: Order ID to cancel

        Returns:
            dict[str, Any]: API response confirming the cancellation
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = orderId

        return self._request(
            method="POST",
            path=Trade.CANCEL_ORDER,
            query=payload,
        )

    def get_open_orders(
        self,
        product_symbol: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get open orders.

        Args:
            product_symbol: Product symbol to filter by
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing open orders
        """
        payload: dict[str, Any] = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)

        res = self._request(
            method="GET",
            path=Trade.GET_OPEN_ORDERS,
            query=payload,
        )
        return res

    def cancel_batch_orders(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Cancel multiple orders in batch.

        Args:
            request: List of order cancellation requests
            category: Product category (linear, option, spot, inverse)

        Returns:
            dict[str, Any]: API response confirming batch cancellations
        """
        payload: dict[str, Any] = {
            "category": category,
            "request": request,
        }

        return self._request(
            method="POST",
            path=Trade.CANCEL_BATCH_ORDERS,
            query=payload,
        )

    def cancel_all_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all orders.

        Args:
            category: Product category (linear, option, spot, inverse)
            product_symbol: Product symbol to cancel orders for

        Returns:
            dict[str, Any]: API response confirming all cancellations
        """
        payload: dict[str, Any] = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)

        return self._request(
            method="POST",
            path=Trade.CANCEL_ALL_ORDERS,
            query=payload,
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
        """
        Get order history.

        Args:
            category: Product category (linear, option, spot, inverse)
            product_symbol: Product symbol to filter by
            orderId: Order ID to filter by
            startTime: Start timestamp in milliseconds
            cursor: Cursor for pagination
            limit: Maximum number of records to return

        Returns:
            dict[str, Any]: API response containing order history
        """
        payload: dict[str, Any] = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if orderId is not None:
            payload["orderId"] = orderId
        if startTime is not None:
            payload["startTime"] = startTime
        if cursor is not None:
            payload["cursor"] = cursor
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="GET",
            path=Trade.GET_ORDER_HISTORY,
            query=payload,
        )
        return res

    def get_execution_list(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Get execution list.

        Args:
            category: Product category (linear, option, spot, inverse)
            product_symbol: Product symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 50)

        Returns:
            dict[str, Any]: API response containing execution list
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

        res = self._request(
            method="GET",
            path=Trade.GET_EXECUTION_LIST,
            query=payload,
        )
        return res

    def place_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Place multiple orders in batch.

        Args:
            request: List of order placement requests
            category: Product category (linear, option, spot, inverse)

        Returns:
            dict[str, Any]: API response containing batch order results
        """
        payload: dict[str, Any] = {
            "category": category,
            "request": request,
        }

        return self._request(
            method="POST",
            path=Trade.BATCH_PLACE_ORDER,
            query=payload,
        )

    def amend_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """
        Amend multiple orders in batch.

        Args:
            request: List of order amendment requests
            category: Product category (linear, option, spot, inverse)

        Returns:
            dict[str, Any]: API response containing batch amendment results
        """
        payload: dict[str, Any] = {
            "category": category,
            "request": request,
        }

        return self._request(
            method="POST",
            path=Trade.BATCH_AMEND_ORDER,
            query=payload,
        )

    def get_borrow_quota(
        self,
        product_symbol: str,
        side: str,
    ) -> dict[str, Any]:
        """
        Get borrow quota for spot trading.

        Args:
            product_symbol: Product symbol
            side: Order side ("Buy" or "Sell")

        Returns:
            dict[str, Any]: API response containing borrow quota information
        """
        payload = {
            "category": "spot",
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "side": side,
        }

        res = self._request(
            method="GET",
            path=Trade.GET_BORROW_QUOTA,
            query=payload,
        )
        return res

    # Spot margin trade methods
    def get_vip_margin_data(
        self,
        vipLevel: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Get VIP margin data.

        Args:
            vipLevel: VIP level to query
            currency: Currency symbol to filter by

        Returns:
            dict[str, Any]: API response containing VIP margin data
        """
        payload: dict[str, Any] = {}
        if vipLevel is not None:
            payload["vipLevel"] = vipLevel
        if currency is not None:
            payload["currency"] = currency

        res = self._request(
            method="GET",
            path=SpotMarginTrade.VIP_MARGIN_DATA,
            query=payload,
        )
        return res

    def get_collateral(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Get collateral information.

        Args:
            currency: Currency symbol to get collateral info for

        Returns:
            dict[str, Any]: API response containing collateral information
        """
        payload: dict[str, Any] = {}
        if currency is not None:
            payload["currency"] = currency

        res = self._request(
            method="GET",
            path=SpotMarginTrade.GET_COLLATERAL,
            query=payload,
        )
        return res

    def get_historical_interest_rate(
        self,
        currency: str,
        vipLevel: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get historical interest rate.

        Args:
            currency: Currency symbol
            vipLevel: VIP level to query
            startTime: Start timestamp in milliseconds
            endTime: End timestamp in milliseconds

        Returns:
            dict[str, Any]: API response containing historical interest rates
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

        res = self._request(
            method="GET",
            path=SpotMarginTrade.HISTORICAL_INTEREST,
            query=payload,
        )
        return res

    def spot_margin_trade_toggle_margin_trade(
        self,
        spotMarginMode: str,
    ) -> dict[str, Any]:
        """
        Toggle spot margin trading mode.

        Args:
            spotMarginMode: Margin mode ("1" to open, "0" to close)

        Returns:
            dict[str, Any]: API response confirming the mode toggle
        """
        payload = {
            "spotMarginMode": spotMarginMode,
        }

        return self._request(
            method="POST",
            path=SpotMarginTrade.TOGGLE_MARGIN_TRADE,
            query=payload,
        )

    def spot_margin_trade_set_leverage(self, leverage: str) -> dict[str, Any]:
        """
        Set spot margin trading leverage.

        Args:
            leverage: Leverage value (2-10)

        Returns:
            dict[str, Any]: API response confirming the leverage setting
        """
        payload = {
            "leverage": leverage,
        }

        return self._request(
            method="POST",
            path=SpotMarginTrade.SET_LEVERAGE,
            query=payload,
        )

    def get_status_and_leverage(self) -> dict[str, Any]:
        """
        Get spot margin trading status and leverage.

        Returns:
            dict[str, Any]: API response containing status and leverage information
        """
        res = self._request(
            method="GET",
            path=SpotMarginTrade.STATUS_AND_LEVERAGE,
            query={},
        )
        return res
