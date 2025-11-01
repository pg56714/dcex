from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade
from .enums import BinanceProductType


class TradeHTTP(HTTPManager):
    """HTTP client for Binance trading API endpoints."""

    def set_leverage(
        self,
        product_symbol: str,
        leverage: int,
    ) -> dict:
        """
        Set leverage for futures trading.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            leverage: Leverage value (1-125)

        Returns:
            dict: Leverage setting result
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
            "leverage": leverage,
        }

        res = self._request(
            method="POST",
            path=FuturesTrade.SET_LEVERAGE,
            query=payload,
        )
        return res

    def place_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        stopPrice: str | None = None,
        closePosition: str | None = None,
        activationPrice: str | None = None,
        callbackRate: str | None = None,
        workingType: str | None = None,
        priceProtect: str | None = None,
        newClientOrderId: str | None = None,
        newOrderRespType: str | None = None,
        priceMatch: str | None = None,
        selfTradePreventionMode: str | None = None,
        goodTillDate: int | None = None,
    ) -> dict:
        """
        Place an order (spot or futures).

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("BUY" or "SELL")
            type_: Order type ("MARKET", "LIMIT", "STOP", "STOP_MARKET", etc.)
            quantity: Order quantity
            price: Order price (required for limit orders)
            timeInForce: Time in force ("GTC", "IOC", "FOK")
            positionSide: Position side for futures ("BOTH", "LONG", "SHORT")
            reduceOnly: Reduce only flag for futures
            stopPrice: Stop price for stop orders
            closePosition: Close position flag for futures
            activationPrice: Activation price for conditional orders
            callbackRate: Callback rate for trailing orders
            workingType: Working type for stop orders
            priceProtect: Price protection flag
            newClientOrderId: Custom order ID
            newOrderRespType: Response type ("ACK", "RESULT", "FULL")
            priceMatch: Price match mode
            selfTradePreventionMode: Self trade prevention mode
            goodTillDate: Good till date timestamp

        Returns:
            dict: Order placement result
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
            "side": side,
            "type": type_,
        }

        if quantity is not None:
            payload["quantity"] = quantity
        if price is not None:
            payload["price"] = price
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if positionSide is not None:
            payload["positionSide"] = positionSide
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if stopPrice is not None:
            payload["stopPrice"] = stopPrice
        if closePosition is not None:
            payload["closePosition"] = closePosition
        if activationPrice is not None:
            payload["activationPrice"] = activationPrice
        if callbackRate is not None:
            payload["callbackRate"] = callbackRate
        if workingType is not None:
            payload["workingType"] = workingType
        if priceProtect is not None:
            payload["priceProtect"] = priceProtect
        if newClientOrderId is not None:
            payload["newClientOrderId"] = newClientOrderId
        if newOrderRespType is not None:
            payload["newOrderRespType"] = newOrderRespType
        if priceMatch is not None:
            payload["priceMatch"] = priceMatch
        if selfTradePreventionMode is not None:
            payload["selfTradePreventionMode"] = selfTradePreventionMode
        if goodTillDate is not None:
            payload["goodTillDate"] = str(goodTillDate)

        res = self._request(
            method="POST",
            path=SpotTrade.PLACE_CANCEL_QUERY_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.PLACE_CANCEL_QUERY_ORDER,
            query=payload,
        )
        return res

    def place_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a market order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("BUY" or "SELL")
            quantity: Order quantity
            positionSide: Position side for futures (optional)
            reduceOnly: Reduce only flag for futures (optional)

        Returns:
            dict: Order placement result
        """
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            type_="MARKET",
            quantity=quantity,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_market_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a market buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            quantity: Order quantity
            positionSide: Position side for futures (optional)
            reduceOnly: Reduce only flag for futures (optional)

        Returns:
            dict: Order placement result
        """
        return self.place_market_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_market_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a market sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            quantity: Order quantity
            positionSide: Position side for futures (optional)
            reduceOnly: Reduce only flag for futures (optional)

        Returns:
            dict: Order placement result
        """
        return self.place_market_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a limit order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("BUY" or "SELL")
            quantity: Order quantity
            price: Order price
            timeInForce: Time in force (default: "GTC")
            positionSide: Position side for futures (optional)
            reduceOnly: Reduce only flag for futures (optional)

        Returns:
            dict: Order placement result
        """
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            type_="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self.place_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self.place_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self.place_order(
            product_symbol=product_symbol,
            side=side,
            type_="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce="GTX",  # GTX = Post Only
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    def cancel_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict:
        """
        Cancel an order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderId: Order ID to cancel
            origClientOrderId: Original client order ID to cancel

        Returns:
            dict: Cancellation result
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if origClientOrderId is not None:
            payload["origClientOrderId"] = origClientOrderId

        res = self._request(
            method="DELETE",
            path=SpotTrade.PLACE_CANCEL_QUERY_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.PLACE_CANCEL_QUERY_ORDER,
            query=payload,
        )
        return res

    def get_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict:
        """
        Get order information.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderId: Order ID to query
            origClientOrderId: Original client order ID to query

        Returns:
            dict: Order information
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if origClientOrderId is not None:
            payload["origClientOrderId"] = origClientOrderId

        res = self._request(
            method="GET",
            path=SpotTrade.PLACE_CANCEL_QUERY_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.PLACE_CANCEL_QUERY_ORDER,
            query=payload,
        )
        return res

    def get_open_orders(
        self,
        product_symbol: str,
        orderId: str | None = None,
        origClientOrderId: str | None = None,
    ) -> dict:
        """
        Get open orders for a trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: List of open orders
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        path = SpotTrade.OPEN_ORDER

        if (
            self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SWAP
        ):
            path = FuturesTrade.QUERY_OPEN_ORDER
            if orderId is not None:
                payload["orderId"] = orderId
            elif origClientOrderId is not None:
                payload["origClientOrderId"] = origClientOrderId

        res = self._request(
            method="GET",
            path=path,
            query=payload,
        )
        return res

    def cancel_all_open_orders(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Cancel all open orders for a trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Cancellation result
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }

        res = self._request(
            method="DELETE",
            path=SpotTrade.OPEN_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.CANCEL_ALL_OPEN_ORDERS,
            query=payload,
        )
        return res

    def get_future_all_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get all futures orders.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderId: Order ID to start from
            startTime: Start time in milliseconds
            endTime: End time in milliseconds
            limit: Number of orders to return (max 1000)

        Returns:
            dict: All orders data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=FuturesTrade.QUERY_ALL_ORDERS,
            query=payload,
        )
        return res

    def get_future_position(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Get futures position information.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Position information
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }

        res = self._request(
            method="GET",
            path=FuturesTrade.POSITION_INFO,
            query=payload,
        )
        return res
