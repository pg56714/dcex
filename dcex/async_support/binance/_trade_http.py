from ...enums import OrderSide
from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade
from .enums import BinanceProductType


class TradeHTTP(HTTPManager):
    """HTTP client for Binance trading API endpoints."""

    def _is_spot_product(self, product_symbol: str) -> bool:
        return (
            str(self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol))
            == BinanceProductType.SPOT.value
        )

    def _order_endpoint(
        self, product_symbol: str, *, test: bool = False
    ) -> SpotTrade | FuturesTrade:
        if self._is_spot_product(product_symbol):
            return SpotTrade.TEST_ORDER if test else SpotTrade.PLACE_CANCEL_QUERY_ORDER
        return FuturesTrade.TEST_ORDER if test else FuturesTrade.PLACE_CANCEL_QUERY_ORDER

    def _build_order_payload(
        self,
        product_symbol: str,
        side: OrderSide | str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
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
    ) -> dict[str, str]:
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
            "side": OrderSide.from_any(side).to_exchange(Common.BINANCE),
            "type": type_,
        }

        if quantity is not None:
            payload["quantity"] = quantity
        if quoteOrderQty is not None:
            payload["quoteOrderQty"] = quoteOrderQty
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

        return payload

    def _build_futures_algo_order_payload(
        self,
        product_symbol: str,
        side: OrderSide | str,
        type_: str,
        quantity: str | None = None,
        triggerPrice: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        positionSide: str | None = None,
        closePosition: str | None = None,
        priceProtect: str | None = None,
        reduceOnly: str | None = None,
        activatePrice: str | None = None,
        callbackRate: str | None = None,
        clientAlgoId: str | None = None,
        newOrderRespType: str | None = None,
        workingType: str | None = None,
        priceMatch: str | None = None,
        selfTradePreventionMode: str | None = None,
        goodTillDate: int | None = None,
        algoType: str = "CONDITIONAL",
    ) -> dict[str, str]:
        payload = {
            "algoType": algoType,
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
            "side": OrderSide.from_any(side).to_exchange(Common.BINANCE),
            "type": type_,
        }

        if quantity is not None:
            payload["quantity"] = quantity
        if triggerPrice is not None:
            payload["triggerPrice"] = triggerPrice
        if price is not None:
            payload["price"] = price
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if positionSide is not None:
            payload["positionSide"] = positionSide
        if closePosition is not None:
            payload["closePosition"] = closePosition
        if priceProtect is not None:
            payload["priceProtect"] = priceProtect
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if activatePrice is not None:
            payload["activatePrice"] = activatePrice
        if callbackRate is not None:
            payload["callbackRate"] = callbackRate
        if clientAlgoId is not None:
            payload["clientAlgoId"] = clientAlgoId
        if newOrderRespType is not None:
            payload["newOrderRespType"] = newOrderRespType
        if workingType is not None:
            payload["workingType"] = workingType
        if priceMatch is not None:
            payload["priceMatch"] = priceMatch
        if selfTradePreventionMode is not None:
            payload["selfTradePreventionMode"] = selfTradePreventionMode
        if goodTillDate is not None:
            payload["goodTillDate"] = str(goodTillDate)

        return payload

    async def set_leverage(
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

        res = await self._request(
            method="POST",
            path=FuturesTrade.SET_LEVERAGE,
            query=payload,
        )
        return res

    async def place_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
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
            quoteOrderQty: Quote asset quantity for spot market orders
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
        payload = self._build_order_payload(
            product_symbol=product_symbol,
            side=side,
            type_=type_,
            quantity=quantity,
            quoteOrderQty=quoteOrderQty,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
            stopPrice=stopPrice,
            closePosition=closePosition,
            activationPrice=activationPrice,
            callbackRate=callbackRate,
            workingType=workingType,
            priceProtect=priceProtect,
            newClientOrderId=newClientOrderId,
            newOrderRespType=newOrderRespType,
            priceMatch=priceMatch,
            selfTradePreventionMode=selfTradePreventionMode,
            goodTillDate=goodTillDate,
        )
        res = await self._request(
            method="POST",
            path=self._order_endpoint(product_symbol),
            query=payload,
        )
        return res

    async def test_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
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
        Validate order parameters without placing a live order.

        Returns:
            dict: Empty response or commission information, depending on Binance options.
        """
        payload = self._build_order_payload(
            product_symbol=product_symbol,
            side=side,
            type_=type_,
            quantity=quantity,
            quoteOrderQty=quoteOrderQty,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
            stopPrice=stopPrice,
            closePosition=closePosition,
            activationPrice=activationPrice,
            callbackRate=callbackRate,
            workingType=workingType,
            priceProtect=priceProtect,
            newClientOrderId=newClientOrderId,
            newOrderRespType=newOrderRespType,
            priceMatch=priceMatch,
            selfTradePreventionMode=selfTradePreventionMode,
            goodTillDate=goodTillDate,
        )
        return await self._request(
            method="POST",
            path=self._order_endpoint(product_symbol, test=True),
            query=payload,
        )

    async def place_futures_algo_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        type_: str,
        quantity: str | None = None,
        triggerPrice: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        positionSide: str | None = None,
        closePosition: str | None = None,
        priceProtect: str | None = None,
        reduceOnly: str | None = None,
        activatePrice: str | None = None,
        callbackRate: str | None = None,
        clientAlgoId: str | None = None,
        newOrderRespType: str | None = None,
        workingType: str | None = None,
        priceMatch: str | None = None,
        selfTradePreventionMode: str | None = None,
        goodTillDate: int | None = None,
        algoType: str = "CONDITIONAL",
    ) -> dict:
        """
        Place a USD-M futures conditional algo order.

        This endpoint is used by Binance for futures TP/SL and trailing stop orders.
        """
        payload = self._build_futures_algo_order_payload(
            product_symbol=product_symbol,
            side=side,
            type_=type_,
            quantity=quantity,
            triggerPrice=triggerPrice,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            closePosition=closePosition,
            priceProtect=priceProtect,
            reduceOnly=reduceOnly,
            activatePrice=activatePrice,
            callbackRate=callbackRate,
            clientAlgoId=clientAlgoId,
            newOrderRespType=newOrderRespType,
            workingType=workingType,
            priceMatch=priceMatch,
            selfTradePreventionMode=selfTradePreventionMode,
            goodTillDate=goodTillDate,
            algoType=algoType,
        )
        return await self._request(
            method="POST",
            path=FuturesTrade.PLACE_CANCEL_QUERY_ALGO_ORDER,
            query=payload,
        )

    async def cancel_futures_algo_order(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict:
        """
        Cancel a USD-M futures conditional algo order.
        """
        payload = self._algo_order_id_payload(algoId=algoId, clientAlgoId=clientAlgoId)
        return await self._request(
            method="DELETE",
            path=FuturesTrade.PLACE_CANCEL_QUERY_ALGO_ORDER,
            query=payload,
        )

    async def get_futures_algo_order(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict:
        """
        Get a USD-M futures conditional algo order.
        """
        payload = self._algo_order_id_payload(algoId=algoId, clientAlgoId=clientAlgoId)
        return await self._request(
            method="GET",
            path=FuturesTrade.PLACE_CANCEL_QUERY_ALGO_ORDER,
            query=payload,
        )

    def _algo_order_id_payload(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict[str, str]:
        if algoId is None and clientAlgoId is None:
            raise ValueError("Either algoId or clientAlgoId is required.")

        payload = {}
        if algoId is not None:
            payload["algoId"] = str(algoId)
        if clientAlgoId is not None:
            payload["clientAlgoId"] = clientAlgoId
        return payload

    async def get_all_open_futures_algo_orders(
        self,
        product_symbol: str | None = None,
        algoType: str | None = None,
        algoId: int | str | None = None,
    ) -> dict:
        """
        Get open USD-M futures conditional algo orders.
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if algoType is not None:
            payload["algoType"] = algoType
        if algoId is not None:
            payload["algoId"] = str(algoId)

        return await self._request(
            method="GET",
            path=FuturesTrade.OPEN_ALGO_ORDERS,
            query=payload,
        )

    async def get_all_futures_algo_orders(
        self,
        product_symbol: str,
        algoId: int | str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get historical USD-M futures conditional algo orders.
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if algoId is not None:
            payload["algoId"] = str(algoId)
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if limit is not None:
            payload["limit"] = str(limit)

        return await self._request(
            method="GET",
            path=FuturesTrade.ALL_ALGO_ORDERS,
            query=payload,
        )

    async def cancel_all_open_futures_algo_orders(self, product_symbol: str) -> dict:
        """
        Cancel all open USD-M futures conditional algo orders for a symbol.
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        return await self._request(
            method="DELETE",
            path=FuturesTrade.CANCEL_ALL_OPEN_ALGO_ORDERS,
            query=payload,
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        newOrderRespType: str | None = None,
    ) -> dict:
        """
        Place a market order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("BUY" or "SELL")
            quantity: Order quantity
            positionSide: Position side for futures (optional)
            reduceOnly: Reduce only flag for futures (optional)
            newOrderRespType: Response type ("ACK", "RESULT", "FULL")

        Returns:
            dict: Order placement result
        """
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            type_="MARKET",
            quantity=quantity,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
            newOrderRespType=newOrderRespType,
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        newOrderRespType: str | None = None,
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
        return await self.place_market_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
            newOrderRespType=newOrderRespType,
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        newOrderRespType: str | None = None,
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
        return await self.place_market_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
            newOrderRespType=newOrderRespType,
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
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
        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            type_="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self.place_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        if self._is_spot_product(product_symbol):
            return await self.place_order(
                product_symbol=product_symbol,
                side=side,
                type_="LIMIT_MAKER",
                quantity=quantity,
                price=price,
            )

        return await self.place_order(
            product_symbol=product_symbol,
            side=side,
            type_="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce="GTX",  # GTX = Post Only
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    async def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self.place_post_only_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            reduceOnly=reduceOnly,
        )

    async def cancel_order(
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

        res = await self._request(
            method="DELETE",
            path=SpotTrade.PLACE_CANCEL_QUERY_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.PLACE_CANCEL_QUERY_ORDER,
            query=payload,
        )
        return res

    async def get_order(
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

        res = await self._request(
            method="GET",
            path=SpotTrade.PLACE_CANCEL_QUERY_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.PLACE_CANCEL_QUERY_ORDER,
            query=payload,
        )
        return res

    async def get_open_orders(
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

        path: SpotTrade | FuturesTrade = SpotTrade.OPEN_ORDER
        if not self._is_spot_product(product_symbol):
            if orderId is not None:
                payload["orderId"] = orderId
                path = FuturesTrade.QUERY_OPEN_ORDER
            elif origClientOrderId is not None:
                payload["origClientOrderId"] = origClientOrderId
                path = FuturesTrade.QUERY_OPEN_ORDER
            else:
                path = FuturesTrade.OPEN_ORDERS

        res = await self._request(
            method="GET",
            path=path,
            query=payload,
        )
        return res

    async def get_all_open_orders(
        self,
        product_symbol: str | None = None,
        market_type: str = BinanceProductType.SPOT,
    ) -> dict:
        """
        Get all open orders for a product or for the selected market.

        Args:
            product_symbol: Optional product symbol. If omitted, Binance returns all open orders.
            market_type: Market type used when product_symbol is omitted ("spot" or "swap").

        Returns:
            dict: Open order list.
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
            path: SpotTrade | FuturesTrade = (
                SpotTrade.OPEN_ORDER
                if self._is_spot_product(product_symbol)
                else FuturesTrade.OPEN_ORDERS
            )
        else:
            path = (
                SpotTrade.OPEN_ORDER
                if str(market_type) == BinanceProductType.SPOT.value
                else FuturesTrade.OPEN_ORDERS
            )

        return await self._request(method="GET", path=path, query=payload)

    async def cancel_all_open_orders(
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

        res = await self._request(
            method="DELETE",
            path=SpotTrade.OPEN_ORDER
            if self.ptm.get_product_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesTrade.CANCEL_ALL_OPEN_ORDERS,
            query=payload,
        )
        return res

    async def get_future_all_order(
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
        return await self.get_all_orders(
            product_symbol=product_symbol,
            orderId=orderId,
            startTime=startTime,
            endTime=endTime,
            limit=limit,
        )

    async def get_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get historical orders for spot or futures.

        Args:
            product_symbol: Trading pair symbol.
            orderId: Order ID to start from.
            startTime: Start time in milliseconds.
            endTime: End time in milliseconds.
            limit: Number of orders to return.

        Returns:
            dict: Historical order data.
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

        res = await self._request(
            method="GET",
            path=SpotTrade.ALL_ORDERS
            if self._is_spot_product(product_symbol)
            else FuturesTrade.QUERY_ALL_ORDERS,
            query=payload,
        )
        return res

    async def get_account_trades(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get account trade fills for spot or futures.

        Args:
            product_symbol: Trading pair symbol.
            orderId: Spot order ID filter.
            startTime: Start time in milliseconds.
            endTime: End time in milliseconds.
            fromId: Trade ID to fetch from.
            limit: Number of trades to return.

        Returns:
            dict: Account trade fills.
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if orderId is not None and self._is_spot_product(product_symbol):
            payload["orderId"] = str(orderId)
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if fromId is not None:
            payload["fromId"] = str(fromId)
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=SpotTrade.ACCOUNT_TRADES
            if self._is_spot_product(product_symbol)
            else FuturesTrade.ACCOUNT_TRADES,
            query=payload,
        )
        return res

    async def get_future_position(
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

        res = await self._request(
            method="GET",
            path=FuturesTrade.POSITION_INFO,
            query=payload,
        )
        return res
