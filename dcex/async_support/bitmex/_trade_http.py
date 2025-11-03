from typing import Any

import msgspec

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.order import Order


class TradeHTTP(HTTPManager):
    """
    HTTP client for BitMEX trading API endpoints.

    This class provides methods to manage trading operations on BitMEX,
    including order placement, modification, cancellation, and querying.
    """

    async def place_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int | None = None,
        ordType: str = "Limit",
        price: float | None = None,
        stopPx: float | None = None,
        clOrdID: str | None = None,
        clOrdLinkID: str | None = None,
        contingencyType: str | None = None,
        displayQty: int | None = None,
        execInst: str | None = None,
        pegOffsetValue: float | None = None,
        pegPriceType: str | None = None,
        timeInForce: str | None = None,
        text: str | None = None,
        targetAccountId: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a new order on BitMEX.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            ordType: Order type ("Limit", "Market", "Stop", etc.)
            price: Limit price for limit orders
            stopPx: Trigger price for stop orders
            clOrdID: Client order ID (max 36 characters)
            clOrdLinkID: Client order link ID for order relationships
            contingencyType: Contingency order type ("OneCancelsTheOther", "OneTriggersTheOther")
            displayQty: Display quantity (0 for fully hidden)
            execInst: Execution instructions ("ParticipateDoNotInitiate", "AllOrNone", etc.)
            pegOffsetValue: Peg offset value
            pegPriceType: Peg price type ("MarketPeg", "PrimaryPeg", etc.)
            timeInForce: Time in force ("Day", "GoodTillCancel", "ImmediateOrCancel", etc.)
            text: Order annotation
            targetAccountId: Target account ID

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        payload["side"] = side
        payload["ordType"] = ordType

        if orderQty is not None:
            payload["orderQty"] = orderQty
        if price is not None:
            payload["price"] = price
        if stopPx is not None:
            payload["stopPx"] = stopPx
        if clOrdID is not None:
            payload["clOrdID"] = clOrdID
        if clOrdLinkID is not None:
            payload["clOrdLinkID"] = clOrdLinkID
        if contingencyType is not None:
            payload["contingencyType"] = contingencyType
        if displayQty is not None:
            payload["displayQty"] = displayQty
        if execInst is not None:
            payload["execInst"] = execInst
        if pegOffsetValue is not None:
            payload["pegOffsetValue"] = pegOffsetValue
        if pegPriceType is not None:
            payload["pegPriceType"] = pegPriceType
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if text is not None:
            payload["text"] = text
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId

        res = await self._request(
            method="POST",
            path=Order.PLACE_ORDER,
            query=payload,
        )
        return res

    async def place_market_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market order.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderQty=orderQty,
            ordType="Market",
            clOrdID=clOrdID,
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market buy order.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            orderQty: Order quantity in contracts
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_market_order(
            product_symbol=product_symbol,
            side="Buy",
            orderQty=orderQty,
            clOrdID=clOrdID,
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market sell order.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            orderQty: Order quantity in contracts
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_market_order(
            product_symbol=product_symbol,
            side="Sell",
            orderQty=orderQty,
            clOrdID=clOrdID,
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
        timeInForce: str = "GoodTillCancel",
    ) -> dict[str, Any]:
        """
        Place a limit order.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)
            timeInForce: Time in force (default: "GoodTillCancel")

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderQty=orderQty,
            ordType="Limit",
            price=price,
            clOrdID=clOrdID,
            timeInForce=timeInForce,
        )

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit buy order.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side="Buy",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit sell order.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side="Sell",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    async def place_post_only_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
        execInst: str = "ParticipateDoNotInitiate",
    ) -> dict[str, Any]:
        """
        Place a post-only order (maker only).

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)
            execInst: Execution instruction (default: "ParticipateDoNotInitiate")

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderQty=orderQty,
            ordType="Limit",
            price=price,
            clOrdID=clOrdID,
            execInst=execInst,
        )

    async def place_post_only_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only buy order (maker only).

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_post_only_order(
            product_symbol=product_symbol,
            side="Buy",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    async def place_post_only_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only sell order (maker only).

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            dict: Order placement response

        Raises:
            FailedRequestError: If the API request fails
        """
        return await self.place_post_only_order(
            product_symbol=product_symbol,
            side="Sell",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    async def amend_order(
        self,
        orderID: str | None = None,
        origClOrdID: str | None = None,
        product_symbol: str | None = None,
        clOrdID: str | None = None,
        leavesQty: int | None = None,
        orderQty: int | None = None,
        price: float | None = None,
        stopPx: float | None = None,
        pegOffsetValue: float | None = None,
        text: str | None = None,
        targetAccountId: int | None = None,
    ) -> dict[str, Any]:
        """
        Amend an existing order.

        Args:
            orderID: Order ID to amend (required if origClOrdID not provided)
            origClOrdID: Client Order ID to amend (required if orderID not provided)
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            clOrdID: New Client Order ID (requires origClOrdID)
            leavesQty: Leaves quantity for partially filled orders
            orderQty: New order quantity
            price: New limit price
            stopPx: New trigger price
            pegOffsetValue: New trailing offset
            text: Order annotation
            targetAccountId: Target account ID

        Returns:
            dict: Order amendment response

        Raises:
            FailedRequestError: If the API request fails
            ValueError: If neither orderID nor origClOrdID is provided
        """
        if orderID is None and origClOrdID is None:
            raise ValueError("Either orderID or origClOrdID must be provided")

        payload: dict[str, str | int | list[str] | float | bool] = {}

        if orderID is not None:
            payload["orderID"] = orderID
        if origClOrdID is not None:
            payload["origClOrdID"] = origClOrdID
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if clOrdID is not None:
            payload["clOrdID"] = clOrdID
        if leavesQty is not None:
            payload["leavesQty"] = leavesQty
        if orderQty is not None:
            payload["orderQty"] = orderQty
        if price is not None:
            payload["price"] = price
        if stopPx is not None:
            payload["stopPx"] = stopPx
        if pegOffsetValue is not None:
            payload["pegOffsetValue"] = pegOffsetValue
        if text is not None:
            payload["text"] = text
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId

        res = await self._request(
            method="PUT",
            path=Order.AMEND_ORDER,
            query=payload,
        )
        return res

    async def cancel_order(
        self,
        orderID: str | list[str] | None = None,
        clOrdID: str | list[str] | None = None,
        targetAccountId: int | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel one or more orders.

        Args:
            orderID: Order ID(s) to cancel
            clOrdID: Client Order ID(s) to cancel
            targetAccountId: Account ID to target
            text: Cancellation annotation

        Returns:
            dict: Order cancellation response

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if orderID is not None:
            payload["orderID"] = orderID
        if clOrdID is not None:
            payload["clOrdID"] = clOrdID
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId
        if text is not None:
            payload["text"] = text

        res = await self._request(
            method="DELETE",
            path=Order.CANCEL_ORDER,
            query=payload,
        )
        return res

    async def cancel_all_orders(
        self,
        product_symbol: str | None = None,
        filter: dict[str, Any] | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: list[str] | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all orders.

        Args:
            product_symbol: Trading symbol to filter orders
            filter: Filter criteria for selective cancellation
            targetAccountId: Account ID to target
            targetAccountIds: List of account IDs to target
            text: Cancellation annotation

        Returns:
            dict: Order cancellation response

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if filter is not None:
            payload["filter"] = msgspec.json.encode(filter).decode("utf-8")
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId
        if targetAccountIds is not None:
            payload["targetAccountIds"] = targetAccountIds
        if text is not None:
            payload["text"] = text

        res = await self._request(
            method="DELETE",
            path=Order.CANCEL_ALL_ORDERS,
            query=payload,
        )
        return res

    async def get_order(
        self,
        product_symbol: str | None = None,
        targetAccountId: int | None = None,
        filter: str | None = None,
        columns: str | None = None,
        count: int | None = 100,
        start: int | None = 0,
        reverse: bool | None = False,
        startTime: str | None = None,
        endTime: str | None = None,
        targetAccountIds: str | None = None,
        targetAccountIds_array: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get order information.

        Args:
            product_symbol: Trading symbol to filter orders
            targetAccountId: Account ID to query
            filter: Filter criteria as a string
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            start: Starting index for pagination
            reverse: Whether to reverse the order of results
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)
            targetAccountIds: Account IDs as a string
            targetAccountIds_array: List of account IDs

        Returns:
            dict: Order information data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol)
        if targetAccountId is not None:
            payload["targetAccountId"] = targetAccountId
        if filter is not None:
            payload["filter"] = filter
        if columns is not None:
            payload["columns"] = columns
        if count is not None:
            payload["count"] = count
        if start is not None:
            payload["start"] = start
        if reverse is not None:
            payload["reverse"] = reverse
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if targetAccountIds is not None:
            payload["targetAccountIds"] = targetAccountIds
        if targetAccountIds_array is not None:
            payload["targetAccountIds[]"] = targetAccountIds_array

        res = await self._request(
            method="GET",
            path=Order.QUERY_ORDER,
            query=payload,
        )
        return res
