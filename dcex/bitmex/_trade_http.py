"""
BitMEX Trade HTTP client for order management operations.

This module provides functionality for managing trading orders on the BitMEX
exchange, including placing, amending, canceling orders and querying order information.
"""

from typing import Any

import msgspec

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.order import Order


class TradeHTTP(HTTPManager):
    """
    BitMEX Trade HTTP client for order management operations.

    This class provides methods for managing trading orders including placing,
    amending, canceling orders and querying order information on the BitMEX exchange.
    """

    def place_order(
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
        Place a new order on the BitMEX exchange.

        Creates a new trading order with the specified parameters. Supports various
        order types including limit, market, stop, and conditional orders.

        Args:
            product_symbol: Trading symbol (required)
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            ordType: Order type - "Limit", "Market", "Stop", "StopLimit",
                    "MarketIfTouched", "LimitIfTouched", "Pegged", "Block",
                    "MarketWithLeftOverAsLimit" (default: "Limit")
            price: Limit price for Limit, StopLimit, LimitIfTouched orders
            stopPx: Trigger price for Stop, StopLimit, MarketIfTouched, LimitIfTouched orders
            clOrdID: Client order ID (max 36 characters)
            clOrdLinkID: Client order link ID for order relationships
            contingencyType: Contingency order type - "OneCancelsTheOther", "OneTriggersTheOther"
            displayQty: Display quantity (0 for fully hidden)
            execInst: Execution instructions - "ParticipateDoNotInitiate", "AllOrNone",
                     "MarkPrice", "IndexPrice", "LastPrice", "Close", "ReduceOnly",
                     "Fixed", "LastWithinMark"
            pegOffsetValue: Peg offset value
            pegPriceType: Peg price type - "MarketPeg", "PrimaryPeg", "TrailingStopPeg",
                         "MidPricePeg", "LastPeg"
            timeInForce: Time in force - "Day", "GoodTillCancel", "ImmediateOrCancel",
                        "FillOrKill", "AtTheClose"
            text: Order annotation
            targetAccountId: Target account ID

        Returns:
            Dictionary containing the order information

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

        res = self._request(
            method="POST",
            path=Order.PLACE_ORDER,
            query=payload,
        )
        return res

    def place_market_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market order on the BitMEX exchange.

        Creates a market order that executes immediately at the best available price.

        Args:
            product_symbol: Trading symbol
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderQty=orderQty,
            ordType="Market",
            clOrdID=clOrdID,
        )

    def place_market_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market buy order on the BitMEX exchange.

        Creates a market buy order that executes immediately at the best available price.

        Args:
            product_symbol: Trading symbol
            orderQty: Order quantity in contracts
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_market_order(
            product_symbol=product_symbol,
            side="Buy",
            orderQty=orderQty,
            clOrdID=clOrdID,
        )

    def place_market_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market sell order on the BitMEX exchange.

        Creates a market sell order that executes immediately at the best available price.

        Args:
            product_symbol: Trading symbol
            orderQty: Order quantity in contracts
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_market_order(
            product_symbol=product_symbol,
            side="Sell",
            orderQty=orderQty,
            clOrdID=clOrdID,
        )

    def place_limit_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
        timeInForce: str = "GoodTillCancel",
    ) -> dict[str, Any]:
        """
        Place a limit order on the BitMEX exchange.

        Creates a limit order that executes at the specified price or better.

        Args:
            product_symbol: Trading symbol
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)
            timeInForce: Time in force (default: "GoodTillCancel")

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderQty=orderQty,
            ordType="Limit",
            price=price,
            clOrdID=clOrdID,
            timeInForce=timeInForce,
        )

    def place_limit_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit buy order on the BitMEX exchange.

        Creates a limit buy order that executes at the specified price or better.

        Args:
            product_symbol: Trading symbol
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_limit_order(
            product_symbol=product_symbol,
            side="Buy",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    def place_limit_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit sell order on the BitMEX exchange.

        Creates a limit sell order that executes at the specified price or better.

        Args:
            product_symbol: Trading symbol
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_limit_order(
            product_symbol=product_symbol,
            side="Sell",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    def place_post_only_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
        execInst: str = "ParticipateDoNotInitiate",
    ) -> dict[str, Any]:
        """
        Place a post-only order on the BitMEX exchange.

        Creates a limit order that only adds liquidity to the order book.
        The order will be rejected if it would immediately match.

        Args:
            product_symbol: Trading symbol
            side: Order side ("Buy" or "Sell")
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)
            execInst: Execution instruction (default: "ParticipateDoNotInitiate")

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            orderQty=orderQty,
            ordType="Limit",
            price=price,
            clOrdID=clOrdID,
            execInst=execInst,
        )

    def place_post_only_buy_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only buy order on the BitMEX exchange.

        Creates a limit buy order that only adds liquidity to the order book.

        Args:
            product_symbol: Trading symbol
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_post_only_order(
            product_symbol=product_symbol,
            side="Buy",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    def place_post_only_sell_order(
        self,
        product_symbol: str,
        orderQty: int,
        price: float,
        clOrdID: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only sell order on the BitMEX exchange.

        Creates a limit sell order that only adds liquidity to the order book.

        Args:
            product_symbol: Trading symbol
            orderQty: Order quantity in contracts
            price: Limit price
            clOrdID: Client order ID (optional)

        Returns:
            Dictionary containing the order information

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_post_only_order(
            product_symbol=product_symbol,
            side="Sell",
            orderQty=orderQty,
            price=price,
            clOrdID=clOrdID,
        )

    def amend_order(
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
        Amend an existing order on the BitMEX exchange.

        Modifies an existing order with new parameters. Either orderID or origClOrdID
        must be provided to identify the order to amend.

        Args:
            orderID: Order ID to amend (required if origClOrdID not provided)
            origClOrdID: Client Order ID to amend (required if orderID not provided)
            product_symbol: Instrument symbol (e.g., 'XBTUSD')
            clOrdID: Optional new Client Order ID (requires origClOrdID)
            leavesQty: Optional leaves quantity for partially filled orders
            orderQty: Optional new order quantity
            price: Optional new limit price for Limit, StopLimit, LimitIfTouched orders
            stopPx: Optional new trigger price for Stop, StopLimit, MarketIfTouched,
                   LimitIfTouched orders
            pegOffsetValue: Optional new trailing offset for Stop, StopLimit,
                          MarketIfTouched, LimitIfTouched orders
            text: Optional order annotation (e.g., 'Take profit')
            targetAccountId: Target account ID

        Returns:
            Dictionary containing the amended order information

        Raises:
            ValueError: If neither orderID nor origClOrdID is provided
            FailedRequestError: If the API request fails
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

        res = self._request(
            method="PUT",
            path=Order.AMEND_ORDER,
            query=payload,
        )
        return res

    def cancel_order(
        self,
        orderID: str | list[str] | None = None,
        clOrdID: str | list[str] | None = None,
        targetAccountId: int | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel one or more orders on the BitMEX exchange.

        Cancels existing orders by their order ID(s) or client order ID(s).

        Args:
            orderID: Order ID(s) to cancel
            clOrdID: Client Order ID(s) to cancel
            targetAccountId: Account ID on which to cancel these orders
            text: Optional cancellation annotation (e.g., 'Take profit')

        Returns:
            Dictionary containing cancellation results

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

        res = self._request(
            method="DELETE",
            path=Order.CANCEL_ORDER,
            query=payload,
        )
        return res

    def cancel_all_orders(
        self,
        product_symbol: str | None = None,
        filter: dict | None = None,
        targetAccountId: int | None = None,
        targetAccountIds: list | None = None,
        text: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all orders on the BitMEX exchange.

        Cancels all open orders, optionally filtered by symbol or other criteria.

        Args:
            product_symbol: Trading symbol to filter cancellations
            filter: Optional filter for cancellation (e.g., {"side": "Buy"})
            targetAccountId: Target account ID
            targetAccountIds: List of target account IDs
            text: Optional cancellation annotation (e.g., 'Spread Exceeded')

        Returns:
            Dictionary containing cancellation results

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

        res = self._request(
            method="DELETE",
            path=Order.CANCEL_ALL_ORDERS,
            query=payload,
        )
        return res

    def get_order(
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
        targetAccountIds_array: list | None = None,
    ) -> dict[str, Any]:
        """
        Get order information from the BitMEX exchange.

        Retrieves order information with optional filtering and pagination.

        Args:
            product_symbol: Trading symbol to filter by
            targetAccountId: Target account ID
            filter: Filter criteria for orders
            columns: Specific columns to return
            count: Maximum number of results to return (default: 100)
            start: Starting index for pagination (default: 0)
            reverse: Whether to reverse the order of results (default: False)
            startTime: Start time for the query (ISO format)
            endTime: End time for the query (ISO format)
            targetAccountIds: Target account IDs as string
            targetAccountIds_array: Target account IDs as list

        Returns:
            Dictionary containing order information

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

        res = self._request(
            method="GET",
            path=Order.QUERY_ORDER,
            query=payload,
        )
        return res
