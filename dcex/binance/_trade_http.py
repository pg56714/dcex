from typing import Any

from .._native_http import NativeResponse
from ..enums import OrderSide
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class TradeHTTP(HTTPManager):
    """HTTP client for Binance trading API endpoints."""

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for private trade methods.")
        try:
            status, headers, body = self._native_client.private_request(method_name, params)
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BINANCE {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, bool):
                value = str(value).lower()
            params.append((key, str(value)))
        return params

    @staticmethod
    def _side(side: OrderSide | str) -> str:
        return OrderSide.from_any(side).value

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
        return self._native_private(
            "set_leverage",
            self._params(product_symbol=product_symbol, leverage=leverage),
        )

    def place_order(
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
        return self._native_private(
            "place_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
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
            ),
        )

    def test_order(
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
        return self._native_private(
            "test_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
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
            ),
        )

    def place_futures_algo_order(
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
        return self._native_private(
            "place_futures_algo_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
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
            ),
        )

    def cancel_futures_algo_order(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict:
        """
        Cancel a USD-M futures conditional algo order.
        """
        return self._native_private(
            "cancel_futures_algo_order",
            self._params(algoId=algoId, clientAlgoId=clientAlgoId),
        )

    def get_futures_algo_order(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict:
        """
        Get a USD-M futures conditional algo order.
        """
        return self._native_private(
            "get_futures_algo_order",
            self._params(algoId=algoId, clientAlgoId=clientAlgoId),
        )

    def get_all_open_futures_algo_orders(
        self,
        product_symbol: str | None = None,
        algoType: str | None = None,
        algoId: int | str | None = None,
    ) -> dict:
        """
        Get open USD-M futures conditional algo orders.
        """
        return self._native_private(
            "get_all_open_futures_algo_orders",
            self._params(
                product_symbol=product_symbol,
                algoType=algoType,
                algoId=algoId,
            ),
        )

    def get_all_futures_algo_orders(
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
        return self._native_private(
            "get_all_futures_algo_orders",
            self._params(
                product_symbol=product_symbol,
                algoId=algoId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def cancel_all_open_futures_algo_orders(self, product_symbol: str) -> dict:
        """
        Cancel all open USD-M futures conditional algo orders for a symbol.
        """
        return self._native_private(
            "cancel_all_open_futures_algo_orders",
            self._params(product_symbol=product_symbol),
        )

    def place_market_order(
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
        return self._native_private(
            "place_market_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                quantity=quantity,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
                newOrderRespType=newOrderRespType,
            ),
        )

    def place_market_buy_order(
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
        return self._native_private(
            "place_market_buy_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
                newOrderRespType=newOrderRespType,
            ),
        )

    def place_market_sell_order(
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
        return self._native_private(
            "place_market_sell_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
                newOrderRespType=newOrderRespType,
            ),
        )

    def place_limit_order(
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
        return self._native_private(
            "place_limit_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                quantity=quantity,
                price=price,
                timeInForce=timeInForce,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
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
        return self._native_private(
            "place_limit_buy_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                timeInForce=timeInForce,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
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
        return self._native_private(
            "place_limit_sell_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                timeInForce=timeInForce,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
        )

    def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self._native_private(
            "place_post_only_limit_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                quantity=quantity,
                price=price,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
        )

    def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self._native_private(
            "place_post_only_limit_buy_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
        )

    def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return self._native_private(
            "place_post_only_limit_sell_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
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
        return self._native_private(
            "cancel_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

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
        return self._native_private(
            "get_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

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
        return self._native_private(
            "get_open_orders",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def get_all_open_orders(
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
        return self._native_private(
            "get_all_open_orders",
            self._params(
                product_symbol=product_symbol,
                market_type=str(market_type),
            ),
        )

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
        return self._native_private(
            "cancel_all_open_orders",
            self._params(product_symbol=product_symbol),
        )

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
        return self._native_private(
            "get_future_all_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_all_orders(
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
        return self._native_private(
            "get_all_orders",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_account_trades(
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
        return self._native_private(
            "get_account_trades",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                fromId=fromId,
                limit=limit,
            ),
        )

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
        return self._native_private(
            "get_future_position",
            self._params(product_symbol=product_symbol),
        )
