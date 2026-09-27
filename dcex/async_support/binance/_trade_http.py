# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
from json import dumps
from typing import Any

from ..._native_http import request_native_json_async
from ...enums import OrderSide
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class TradeHTTP(HTTPManager):
    """HTTP client for Binance trading API endpoints."""

    async def place_equity_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_type: str,
        *,
        quantity: str | None = None,
        notional: str | None = None,
        price: str | None = None,
        trading_session: str | None = None,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Place a stock order; the native client validates the order matrix."""
        return await self._native_private(
            "place_equity_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                orderType=order_type,
                quantity=quantity,
                notional=notional,
                price=price,
                tradingSession=trading_session,
                timeInForce=time_in_force,
                clientOrderId=client_order_id,
            ),
        )

    async def cancel_equity_order(self, order_id: str) -> dict:
        """Cancel one stock order."""
        return await self._native_private("cancel_equity_order", self._params(orderId=order_id))

    async def cancel_all_equity_orders(self) -> dict:
        """Cancel all open stock orders."""
        return await self._native_private("cancel_all_equity_orders", [])

    async def get_equity_order_detail(self, order_id: str) -> dict:
        """Get one stock order."""
        return await self._native_private("get_equity_order_detail", self._params(orderId=order_id))

    async def get_open_equity_orders(self) -> dict:
        """Get open stock orders."""
        return await self._native_private("get_open_equity_orders", [])

    async def get_equity_order_history(self, start_time: int, end_time: int) -> dict:
        """Get stock order history for a time range."""
        return await self._native_private(
            "get_equity_order_history",
            self._params(startTime=start_time, endTime=end_time),
        )

    async def get_equity_trade_history(
        self,
        start_time: int,
        end_time: int,
        *,
        product_symbol: str | None = None,
        side: OrderSide | str | None = None,
        order_id: str | None = None,
        current: int | None = None,
        size: int | None = None,
    ) -> dict:
        """Get stock fills in a time range."""
        return await self._native_private(
            "get_equity_trade_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                product_symbol=product_symbol,
                side=self._side(side) if side is not None else None,
                orderId=order_id,
                current=current,
                size=size,
            ),
        )

    async def mint_equity_token(
        self, underlying_asset: str, amount: str, client_order_id: str | None = None
    ) -> dict:
        """Convert an underlying asset into its stock token."""
        return await self._native_private(
            "mint_equity_token",
            self._params(
                underlyingAsset=underlying_asset,
                underlyingAssetAmount=amount,
                clientOrderId=client_order_id,
            ),
        )

    async def redeem_equity_token(
        self, tokenized_asset: str, amount: str, client_order_id: str | None = None
    ) -> dict:
        """Redeem a stock token into its underlying asset."""
        return await self._native_private(
            "redeem_equity_token",
            self._params(
                tokenizedAsset=tokenized_asset,
                tokenizedAssetAmount=amount,
                clientOrderId=client_order_id,
            ),
        )

    async def get_equity_convert_status(self, issuer_request_id: str, convert_type: str) -> dict:
        """Get one stock-token conversion status."""
        return await self._native_private(
            "get_equity_convert_status",
            self._params(issuerRequestId=issuer_request_id, convertType=convert_type),
        )

    async def get_equity_convert_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        last_id: int | None = None,
        size: int | None = None,
    ) -> dict:
        """Get stock-token conversion history."""
        return await self._native_private(
            "get_equity_convert_history",
            self._params(startTime=start_time, endTime=end_time, lastId=last_id, size=size),
        )

    async def sign_equity_disclaimer(self) -> dict:
        """Accept the stock trading disclaimer."""
        return await self._native_private("sign_equity_disclaimer", [])

    async def create_or_renew_equity_listen_key(self) -> dict:
        """Create or renew the stock user-data listen key."""
        return await self._native_private("create_or_renew_equity_listen_key", [])

    async def place_options_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        quantity: str,
        price: str,
        *,
        timeInForce: str = "GTC",
        reduceOnly: bool | None = None,
        postOnly: bool | None = None,
        newOrderRespType: str | None = None,
        clientOrderId: str | None = None,
        selfTradePreventionMode: str | None = None,
    ) -> dict[str, Any]:
        """Place a Binance Options limit order."""
        return await self._native_private(
            "place_options_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce=timeInForce,
                reduceOnly=reduceOnly,
                postOnly=postOnly,
                newOrderRespType=newOrderRespType,
                clientOrderId=clientOrderId,
                selfTradePreventionMode=selfTradePreventionMode,
            ),
        )

    async def place_options_batch_orders(
        self, orders: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Place multiple Binance Options orders in one request."""
        return await self._native_private(
            "place_options_batch_orders",
            self._params(orders=dumps(orders, separators=(",", ":"))),
        )

    async def cancel_options_batch_orders(
        self,
        product_symbol: str,
        *,
        orderIds: list[int] | None = None,
        clientOrderIds: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Cancel multiple Binance Options orders."""
        return await self._native_private(
            "cancel_options_batch_orders",
            self._params(
                product_symbol=product_symbol,
                orderIds=dumps(orderIds) if orderIds is not None else None,
                clientOrderIds=dumps(clientOrderIds) if clientOrderIds is not None else None,
            ),
        )

    async def get_options_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        clientOrderId: str | None = None,
    ) -> dict[str, Any]:
        """Get one Binance Options order."""
        return await self._native_private(
            "get_options_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOrderId=clientOrderId,
            ),
        )

    async def cancel_options_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        clientOrderId: str | None = None,
    ) -> dict[str, Any]:
        """Cancel one Binance Options order."""
        return await self._native_private(
            "cancel_options_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOrderId=clientOrderId,
            ),
        )

    async def cancel_all_options_orders(self, product_symbol: str) -> dict[str, Any]:
        """Cancel all open option orders for one symbol."""
        return await self._native_private(
            "cancel_all_options_orders", self._params(product_symbol=product_symbol)
        )

    async def cancel_all_options_orders_by_underlying(self, underlying: str) -> dict[str, Any]:
        """Cancel all open option orders for one underlying."""
        return await self._native_private(
            "cancel_all_options_orders_by_underlying",
            self._params(underlying=underlying),
        )

    async def get_options_positions(
        self, product_symbol: str | None = None
    ) -> list[dict[str, Any]]:
        """Get current Binance Options positions."""
        return await self._native_private(
            "get_options_positions", self._params(product_symbol=product_symbol)
        )

    async def get_open_options_orders(
        self,
        product_symbol: str | None = None,
        *,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get current open Binance Options orders."""
        return await self._native_private(
            "get_open_options_orders",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_options_order_history(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get completed Binance Options orders."""
        return await self._native_private(
            "get_options_order_history",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_options_account_trades(
        self,
        product_symbol: str,
        *,
        fromId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get Binance Options account trades."""
        return await self._native_private(
            "get_options_account_trades",
            self._params(
                product_symbol=product_symbol,
                fromId=fromId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_options_commission(self) -> dict[str, Any]:
        """Get Binance Options commission rates."""
        return await self._native_private("get_options_commission", [])

    async def get_options_exercise_records(
        self,
        product_symbol: str | None = None,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get the account's Binance Options exercise records."""
        return await self._native_private(
            "get_options_exercise_records",
            self._params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for private trade methods.")
        try:
            response, data = await request_native_json_async(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BINANCE {method_name} | Params: {params}",
                message=str(exc),
                status_code="Unknown",
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            if isinstance(value, list):
                params.extend((key, str(item)) for item in value)
                continue
            if isinstance(value, bool):
                value = str(value).lower()
            params.append((key, str(value)))
        return params

    @staticmethod
    def _side(side: OrderSide | str) -> str:
        return OrderSide.from_any(side).value

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
        return await self._native_private(
            "set_leverage",
            self._params(product_symbol=product_symbol, leverage=leverage),
        )

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
        strategyId: int | None = None,
        strategyType: int | None = None,
        trailingDelta: int | None = None,
        icebergQty: str | None = None,
        pegPriceType: str | None = None,
        pegOffsetValue: int | None = None,
        pegOffsetType: str | None = None,
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
        return await self._native_private(
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
                strategyId=strategyId,
                strategyType=strategyType,
                trailingDelta=trailingDelta,
                icebergQty=icebergQty,
                pegPriceType=pegPriceType,
                pegOffsetValue=pegOffsetValue,
                pegOffsetType=pegOffsetType,
                priceMatch=priceMatch,
                selfTradePreventionMode=selfTradePreventionMode,
                goodTillDate=goodTillDate,
            ),
        )

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
        strategyId: int | None = None,
        strategyType: int | None = None,
        trailingDelta: int | None = None,
        icebergQty: str | None = None,
        pegPriceType: str | None = None,
        pegOffsetValue: int | None = None,
        pegOffsetType: str | None = None,
        computeCommissionRates: bool | None = None,
        priceMatch: str | None = None,
        selfTradePreventionMode: str | None = None,
        goodTillDate: int | None = None,
    ) -> dict:
        """
        Validate order parameters without placing a live order.

        Returns:
            dict: Empty response or commission information, depending on Binance options.
        """
        return await self._native_private(
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
                strategyId=strategyId,
                strategyType=strategyType,
                trailingDelta=trailingDelta,
                icebergQty=icebergQty,
                pegPriceType=pegPriceType,
                pegOffsetValue=pegOffsetValue,
                pegOffsetType=pegOffsetType,
                computeCommissionRates=computeCommissionRates,
                priceMatch=priceMatch,
                selfTradePreventionMode=selfTradePreventionMode,
                goodTillDate=goodTillDate,
            ),
        )

    async def create_oco_order(self, product_symbol: str, **params: object) -> dict:
        """Create a Binance spot one-cancels-the-other order list."""
        return await self._native_private(
            "create_oco_order", self._params(product_symbol=product_symbol, **params)
        )

    async def create_oto_order(self, product_symbol: str, **params: object) -> dict:
        """Create a Binance spot one-triggers-the-other order list."""
        return await self._native_private(
            "create_oto_order", self._params(product_symbol=product_symbol, **params)
        )

    async def create_otoco_order(self, product_symbol: str, **params: object) -> dict:
        """Create a Binance spot one-triggers-an-OCO order list."""
        return await self._native_private(
            "create_otoco_order", self._params(product_symbol=product_symbol, **params)
        )

    async def get_prevented_matches(self, product_symbol: str, **params: object) -> dict:
        """Retrieve spot self-trade-prevention match records."""
        return await self._native_private(
            "get_prevented_matches", self._params(product_symbol=product_symbol, **params)
        )

    async def get_allocations(self, product_symbol: str, **params: object) -> dict:
        """Retrieve spot allocation records."""
        return await self._native_private(
            "get_allocations", self._params(product_symbol=product_symbol, **params)
        )

    async def get_order_rate_limit(self, **params: object) -> dict:
        """Retrieve the account's current spot order-count limits."""
        return await self._native_private("get_order_rate_limit", self._params(**params))

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
        return await self._native_private(
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

    async def cancel_futures_algo_order(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict:
        """
        Cancel a USD-M futures conditional algo order.
        """
        return await self._native_private(
            "cancel_futures_algo_order",
            self._params(algoId=algoId, clientAlgoId=clientAlgoId),
        )

    async def get_futures_algo_order(
        self,
        algoId: int | str | None = None,
        clientAlgoId: str | None = None,
    ) -> dict:
        """
        Get a USD-M futures conditional algo order.
        """
        return await self._native_private(
            "get_futures_algo_order",
            self._params(algoId=algoId, clientAlgoId=clientAlgoId),
        )

    async def get_all_open_futures_algo_orders(
        self,
        product_symbol: str | None = None,
        algoType: str | None = None,
        algoId: int | str | None = None,
    ) -> dict:
        """
        Get open USD-M futures conditional algo orders.
        """
        return await self._native_private(
            "get_all_open_futures_algo_orders",
            self._params(
                product_symbol=product_symbol,
                algoType=algoType,
                algoId=algoId,
            ),
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
        return await self._native_private(
            "get_all_futures_algo_orders",
            self._params(
                product_symbol=product_symbol,
                algoId=algoId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def cancel_all_open_futures_algo_orders(self, product_symbol: str) -> dict:
        """
        Cancel all open USD-M futures conditional algo orders for a symbol.
        """
        return await self._native_private(
            "cancel_all_open_futures_algo_orders",
            self._params(product_symbol=product_symbol),
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
        return await self._native_private(
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
        return await self._native_private(
            "place_market_buy_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
                newOrderRespType=newOrderRespType,
            ),
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
        return await self._native_private(
            "place_market_sell_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
                newOrderRespType=newOrderRespType,
            ),
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
        return await self._native_private(
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

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self._native_private(
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

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self._native_private(
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

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self._native_private(
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

    async def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self._native_private(
            "place_post_only_limit_buy_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        return await self._native_private(
            "place_post_only_limit_sell_order",
            self._params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                positionSide=positionSide,
                reduceOnly=reduceOnly,
            ),
        )

    async def cancel_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        cancelRestrictions: str | None = None,
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
        return await self._native_private(
            "cancel_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                newClientOrderId=newClientOrderId,
                cancelRestrictions=cancelRestrictions,
            ),
        )

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
        return await self._native_private(
            "get_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

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
        return await self._native_private(
            "get_open_orders",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

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
        return await self._native_private(
            "get_all_open_orders",
            self._params(
                product_symbol=product_symbol,
                market_type=str(market_type),
            ),
        )

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
        return await self._native_private(
            "cancel_all_open_orders",
            self._params(product_symbol=product_symbol),
        )

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
        return await self._native_private(
            "get_future_all_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
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
        return await self._native_private(
            "get_all_orders",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

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
        return await self._native_private(
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

    async def get_future_position(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get futures position information.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Position information
        """
        return await self._native_private(
            "get_future_position",
            self._params(product_symbol=product_symbol),
        )

    async def place_margin_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        type_: str,
        *,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        stopPrice: str | None = None,
        timeInForce: str | None = None,
        newClientOrderId: str | None = None,
        icebergQty: str | None = None,
        newOrderRespType: str | None = None,
        sideEffectType: str = "NO_SIDE_EFFECT",
        isIsolated: bool = False,
        selfTradePreventionMode: str | None = None,
        autoRepayAtCancel: bool | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Place a margin order with optional automatic borrowing or repayment."""
        return await self._native_private(
            "place_margin_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                type=type_,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                price=price,
                stopPrice=stopPrice,
                timeInForce=timeInForce,
                newClientOrderId=newClientOrderId,
                icebergQty=icebergQty,
                newOrderRespType=newOrderRespType,
                sideEffectType=sideEffectType,
                isIsolated=isIsolated,
                selfTradePreventionMode=selfTradePreventionMode,
                autoRepayAtCancel=autoRepayAtCancel,
                recvWindow=recvWindow,
            ),
        )

    async def cancel_margin_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Cancel one Binance Margin order."""
        return await self._native_private(
            "cancel_margin_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                newClientOrderId=newClientOrderId,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    async def get_margin_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Query one Binance Margin order."""
        return await self._native_private(
            "get_margin_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    async def get_open_margin_orders(
        self,
        *,
        product_symbol: str | None = None,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query open cross- or isolated-margin orders."""
        return await self._native_private(
            "get_open_margin_orders",
            self._params(
                product_symbol=product_symbol,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    async def cancel_all_open_margin_orders(
        self,
        product_symbol: str,
        *,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> list[dict[str, Any]]:
        """Cancel every open Binance Margin order on one symbol."""
        return await self._native_private(
            "cancel_all_open_margin_orders",
            self._params(
                product_symbol=product_symbol,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    async def get_all_margin_orders(
        self,
        product_symbol: str,
        *,
        isIsolated: bool = False,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query Binance Margin order history."""
        return await self._native_private(
            "get_all_margin_orders",
            self._params(
                product_symbol=product_symbol,
                isIsolated=isIsolated,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    async def get_margin_account_trades(
        self,
        product_symbol: str,
        *,
        isIsolated: bool = False,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query Binance Margin account fills."""
        return await self._native_private(
            "get_margin_account_trades",
            self._params(
                product_symbol=product_symbol,
                isIsolated=isIsolated,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                fromId=fromId,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    async def get_pm_um_open_orders(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict:
        """Return open Portfolio Margin USD-M orders."""
        return await self._native_private(
            "get_pm_um_open_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_pm_um_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Look up one Portfolio Margin USD-M order."""
        return await self._native_private(
            "get_pm_um_order",
            self._params(
                product_symbol=product_symbol,
                orderId=order_id,
                origClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_pm_um_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel one Portfolio Margin USD-M order."""
        return await self._native_private(
            "cancel_pm_um_order",
            self._params(
                product_symbol=product_symbol,
                orderId=order_id,
                origClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_all_pm_um_orders(
        self, product_symbol: str, *, recv_window: int | None = None
    ) -> dict:
        """Cancel all active Portfolio Margin USD-M orders for a symbol."""
        return await self._native_private(
            "cancel_all_pm_um_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def place_pm_um_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_type: str,
        quantity: str,
        *,
        price: str | None = None,
        time_in_force: str | None = None,
        position_side: str | None = None,
        reduce_only: bool | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Place a Portfolio Margin USD-M LIMIT or MARKET order."""
        return await self._native_private(
            "place_pm_um_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                type_=order_type,
                quantity=quantity,
                price=price,
                timeInForce=time_in_force,
                positionSide=position_side,
                reduceOnly=reduce_only,
                newClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def place_pm_um_algo_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_type: str,
        *,
        quantity: str | None = None,
        trigger_price: str | None = None,
        price: str | None = None,
        close_position: bool | None = None,
        position_side: str | None = None,
        reduce_only: bool | None = None,
        time_in_force: str | None = None,
        callback_rate: str | None = None,
        activate_price: str | None = None,
        client_algo_id: str | None = None,
        working_type: str | None = None,
        price_protect: bool | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Place a Portfolio Margin USD-M conditional order on the current algo route."""
        return await self._native_private(
            "place_pm_um_algo_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                type_=order_type,
                quantity=quantity,
                triggerPrice=trigger_price,
                price=price,
                closePosition=close_position,
                positionSide=position_side,
                reduceOnly=reduce_only,
                timeInForce=time_in_force,
                callbackRate=callback_rate,
                activatePrice=activate_price,
                clientAlgoId=client_algo_id,
                workingType=working_type,
                priceProtect=price_protect,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_um_algo_order(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Look up a Portfolio Margin USD-M conditional order."""
        return await self._native_private(
            "get_pm_um_algo_order",
            self._params(
                algoId=algo_id,
                clientAlgoId=client_algo_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_pm_um_algo_order(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin USD-M conditional order."""
        return await self._native_private(
            "cancel_pm_um_algo_order",
            self._params(
                algoId=algo_id,
                clientAlgoId=client_algo_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_all_pm_um_algo_orders(
        self,
        product_symbol: str,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel all active conditional orders for a Portfolio Margin USD-M symbol."""
        return await self._native_private(
            "cancel_all_pm_um_algo_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_pm_um_open_algo_orders(
        self,
        product_symbol: str | None = None,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Get open Portfolio Margin USD-M conditional orders."""
        return await self._native_private(
            "get_pm_um_open_algo_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_pm_um_algo_order_history(
        self,
        product_symbol: str,
        *,
        algo_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Get Portfolio Margin USD-M conditional order history."""
        return await self._native_private(
            "get_pm_um_algo_order_history",
            self._params(
                product_symbol=product_symbol,
                algoId=algo_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_um_all_orders(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin um all orders."""
        return await self._native_private(
            "get_pm_um_all_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_um_user_trades(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin um user trades."""
        return await self._native_private(
            "get_pm_um_user_trades", self._params(product_symbol=product_symbol)
        )

    async def get_pm_cm_open_orders(self, product_symbol: str | None = None) -> dict:
        """Query Binance Portfolio Margin cm open orders."""
        return await self._native_private(
            "get_pm_cm_open_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_cm_all_orders(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin cm all orders."""
        return await self._native_private(
            "get_pm_cm_all_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_cm_user_trades(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin cm user trades."""
        return await self._native_private(
            "get_pm_cm_user_trades", self._params(product_symbol=product_symbol)
        )

    async def get_pm_margin_open_orders(self, product_symbol: str | None = None) -> dict:
        """Query Binance Portfolio Margin margin open orders."""
        return await self._native_private(
            "get_pm_margin_open_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_margin_all_orders(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin margin all orders."""
        return await self._native_private(
            "get_pm_margin_all_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_margin_trades(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin margin trades."""
        return await self._native_private(
            "get_pm_margin_trades", self._params(product_symbol=product_symbol)
        )

    async def place_pm_cm_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_type: str,
        quantity: str,
        *,
        price: str | None = None,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Place a Portfolio Margin CM LIMIT or MARKET order."""
        return await self._native_private(
            "place_pm_cm_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                type_=order_type,
                quantity=quantity,
                price=price,
                timeInForce=time_in_force,
                newClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_cm_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Get a Portfolio Margin CM order."""
        return await self._native_private(
            "get_pm_cm_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    async def cancel_pm_cm_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin CM order."""
        return await self._native_private(
            "cancel_pm_cm_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    async def cancel_all_pm_cm_orders(self, product_symbol: str) -> dict:
        """Cancel all active Portfolio Margin CM orders for a symbol."""
        return await self._native_private(
            "cancel_all_pm_cm_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_margin_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Get a Portfolio Margin MARGIN order."""
        return await self._native_private(
            "get_pm_margin_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    async def cancel_pm_margin_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin MARGIN order."""
        return await self._native_private(
            "cancel_pm_margin_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    async def cancel_all_pm_margin_orders(self, product_symbol: str) -> dict:
        """Cancel all active Portfolio Margin MARGIN orders for a symbol."""
        return await self._native_private(
            "cancel_all_pm_margin_orders", self._params(product_symbol=product_symbol)
        )

    async def place_pm_margin_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_type: str,
        quantity: str,
        *,
        price: str | None = None,
        time_in_force: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Place a Portfolio Margin MARGIN LIMIT or MARKET order."""
        return await self._native_private(
            "place_pm_margin_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                type_=order_type,
                quantity=quantity,
                price=price,
                timeInForce=time_in_force,
                newClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def modify_pm_um_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_id: int,
        quantity: str,
        price: str,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Modify a Portfolio Margin USD-M LIMIT order."""
        return await self._native_private(
            "modify_pm_um_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                orderId=order_id,
                quantity=quantity,
                price=price,
                recvWindow=recv_window,
            ),
        )

    async def modify_pm_cm_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        order_id: int,
        quantity: str,
        price: str,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Modify a Portfolio Margin COIN-M LIMIT order."""
        return await self._native_private(
            "modify_pm_cm_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                orderId=order_id,
                quantity=quantity,
                price=price,
                recvWindow=recv_window,
            ),
        )

    async def place_pm_cm_conditional_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        strategy_type: str,
        *,
        quantity: str | None = None,
        price: str | None = None,
        stop_price: str | None = None,
        callback_rate: str | None = None,
        position_side: str | None = None,
        reduce_only: bool | None = None,
        client_strategy_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Place a Portfolio Margin COIN-M conditional order."""
        return await self._native_private(
            "place_pm_cm_conditional_order",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                strategyType=strategy_type,
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                callbackRate=callback_rate,
                positionSide=position_side,
                reduceOnly=reduce_only,
                newClientStrategyId=client_strategy_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_pm_cm_conditional_order(
        self,
        product_symbol: str,
        *,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin COIN-M conditional order."""
        return await self._native_private(
            "cancel_pm_cm_conditional_order",
            self._params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                newClientStrategyId=client_strategy_id,
                recvWindow=recv_window,
            ),
        )

    async def cancel_all_pm_cm_conditional_orders(
        self,
        product_symbol: str,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel all COIN-M conditional orders for a Portfolio Margin symbol."""
        return await self._native_private(
            "cancel_all_pm_cm_conditional_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_pm_cm_conditional_order(
        self,
        product_symbol: str,
        *,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
    ) -> dict:
        """Look up an open Portfolio Margin COIN-M conditional order."""
        return await self._native_private(
            "get_pm_cm_conditional_order",
            self._params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                newClientStrategyId=client_strategy_id,
            ),
        )

    async def get_pm_cm_conditional_order_history(
        self,
        product_symbol: str,
        *,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
    ) -> dict:
        """Look up Portfolio Margin COIN-M conditional order history."""
        return await self._native_private(
            "get_pm_cm_conditional_order_history",
            self._params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                newClientStrategyId=client_strategy_id,
            ),
        )

    async def get_pm_cm_open_conditional_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """List active Portfolio Margin COIN-M conditional orders."""
        return await self._native_private(
            "get_pm_cm_open_conditional_orders", self._params(product_symbol=product_symbol)
        )

    async def get_pm_cm_all_conditional_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """List Portfolio Margin COIN-M conditional orders."""
        return await self._native_private(
            "get_pm_cm_all_conditional_orders", self._params(product_symbol=product_symbol)
        )

    async def place_pm_margin_oco(
        self,
        product_symbol: str,
        side: OrderSide | str,
        quantity: str,
        price: str,
        stop_price: str,
        *,
        stop_limit_price: str | None = None,
        stop_limit_time_in_force: str | None = None,
    ) -> dict:
        """Place a Portfolio Margin OCO order."""
        return await self._native_private(
            "place_pm_margin_oco",
            self._params(
                product_symbol=product_symbol,
                side=self._side(side),
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                stopLimitPrice=stop_limit_price,
                stopLimitTimeInForce=stop_limit_time_in_force,
            ),
        )

    async def get_pm_margin_oco(self, order_list_id: int) -> dict:
        """Get a Portfolio Margin OCO order list."""
        return await self._native_private(
            "get_pm_margin_oco", self._params(orderListId=order_list_id)
        )

    async def cancel_pm_margin_oco(
        self,
        product_symbol: str,
        order_list_id: int,
    ) -> dict:
        """Cancel a Portfolio Margin OCO order list."""
        return await self._native_private(
            "cancel_pm_margin_oco",
            self._params(product_symbol=product_symbol, orderListId=order_list_id),
        )

    async def get_pm_margin_open_oco(self) -> dict:
        """List open Portfolio Margin OCO order lists."""
        return await self._native_private("get_pm_margin_open_oco", self._params())

    async def get_pm_margin_all_oco(self) -> dict:
        """List Portfolio Margin OCO order history."""
        return await self._native_private("get_pm_margin_all_oco", self._params())

    async def get_pm_um_order_amendments(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get Portfolio Margin USD-M order amendment history."""
        return await self._native_private(
            "get_pm_um_order_amendments",
            self._params(
                product_symbol=product_symbol,
                orderId=order_id,
                origClientOrderId=client_order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_pm_cm_order_amendments(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get Portfolio Margin COIN-M order amendment history."""
        return await self._native_private(
            "get_pm_cm_order_amendments",
            self._params(
                product_symbol=product_symbol,
                orderId=order_id,
                origClientOrderId=client_order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_spot_order_list(
        self,
        *,
        order_list_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /api/v3/orderList`` with signed authentication."""
        return await self._native_private(
            "get_spot_order_list",
            self._params(
                orderListId=order_list_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def get_spot_all_order_lists(
        self,
        *,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /api/v3/allOrderList`` with signed authentication."""
        return await self._native_private(
            "get_spot_all_order_lists",
            self._params(
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_spot_open_order_lists(
        self, *, recv_window: str | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /api/v3/openOrderList`` with signed authentication."""
        return await self._native_private(
            "get_spot_open_order_lists", self._params(recvWindow=recv_window)
        )

    async def cancel_spot_order_list(
        self,
        product_symbol: str,
        *,
        order_list_id: int | None = None,
        list_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``DELETE /api/v3/orderList`` with signed authentication."""
        return await self._native_private(
            "cancel_spot_order_list",
            self._params(
                product_symbol=product_symbol,
                orderListId=order_list_id,
                listClientOrderId=list_client_order_id,
                newClientOrderId=new_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def amend_spot_order_keep_priority(
        self,
        product_symbol: str,
        new_quantity: str,
        *,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``PUT /api/v3/order/amend/keepPriority`` with signed authentication."""
        return await self._native_private(
            "amend_spot_order_keep_priority",
            self._params(
                product_symbol=product_symbol,
                newQty=new_quantity,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                newClientOrderId=new_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def get_futures_position_mode(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /fapi/v1/positionSide/dual`` with signed authentication."""
        return await self._native_private(
            "get_futures_position_mode", self._params(recvWindow=recv_window)
        )

    async def set_futures_position_mode(
        self, dual_side_position: bool, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /fapi/v1/positionSide/dual`` with signed authentication."""
        return await self._native_private(
            "set_futures_position_mode",
            self._params(dualSidePosition=dual_side_position, recvWindow=recv_window),
        )

    async def set_futures_margin_type(
        self, product_symbol: str, margin_type: str, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /fapi/v1/marginType`` with signed authentication."""
        return await self._native_private(
            "set_futures_margin_type",
            self._params(
                product_symbol=product_symbol, marginType=margin_type, recvWindow=recv_window
            ),
        )

    async def set_futures_cancel_countdown(
        self, product_symbol: str, countdown_time: int, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /fapi/v1/countdownCancelAll`` with signed authentication."""
        return await self._native_private(
            "set_futures_cancel_countdown",
            self._params(
                product_symbol=product_symbol, countdownTime=countdown_time, recvWindow=recv_window
            ),
        )

    async def get_futures_leverage_brackets(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /fapi/v1/leverageBracket`` with signed authentication."""
        return await self._native_private(
            "get_futures_leverage_brackets",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def amend_futures_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str | None = None,
        *,
        price_match: str | None = None,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        modify_id: int | None = None,
        reduce_only: bool | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``PUT /fapi/v1/order`` with signed authentication."""
        return await self._native_private(
            "amend_futures_order",
            self._params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                price=price,
                priceMatch=price_match,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                modifyId=modify_id,
                reduceOnly=reduce_only,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_position_mode(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v1/positionSide/dual`` with signed authentication."""
        return await self._native_private(
            "get_coin_futures_position_mode", self._params(recvWindow=recv_window)
        )

    async def set_coin_futures_position_mode(
        self, dual_side_position: bool, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/positionSide/dual`` with signed authentication."""
        return await self._native_private(
            "set_coin_futures_position_mode",
            self._params(dualSidePosition=dual_side_position, recvWindow=recv_window),
        )

    async def set_coin_futures_margin_type(
        self, symbol: str, margin_type: str, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/marginType`` with signed authentication."""
        return await self._native_private(
            "set_coin_futures_margin_type",
            self._params(symbol=symbol, marginType=margin_type, recvWindow=recv_window),
        )

    async def set_coin_futures_cancel_countdown(
        self, symbol: str, countdown_time: int, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/countdownCancelAll`` with signed authentication."""
        return await self._native_private(
            "set_coin_futures_cancel_countdown",
            self._params(symbol=symbol, countdownTime=countdown_time, recvWindow=recv_window),
        )

    async def get_coin_futures_leverage_brackets(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v2/leverageBracket`` with signed authentication."""
        return await self._native_private(
            "get_coin_futures_leverage_brackets",
            self._params(symbol=symbol, recvWindow=recv_window),
        )

    async def amend_coin_futures_order(
        self,
        symbol: str,
        side: str,
        quantity: str,
        price: str | None = None,
        *,
        price_match: str | None = None,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        modify_id: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``PUT /dapi/v1/order`` with signed authentication."""
        return await self._native_private(
            "amend_coin_futures_order",
            self._params(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                priceMatch=price_match,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                modifyId=modify_id,
                recvWindow=recv_window,
            ),
        )

    async def set_coin_futures_leverage(
        self, symbol: str, leverage: int, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/leverage`` with signed authentication."""
        return await self._native_private(
            "set_coin_futures_leverage",
            self._params(symbol=symbol, leverage=leverage, recvWindow=recv_window),
        )

    async def get_coin_futures_pair_leverage_brackets(
        self, *, pair: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v1/leverageBracket`` with signed authentication."""
        return await self._native_private(
            "get_coin_futures_pair_leverage_brackets",
            self._params(pair=pair, recvWindow=recv_window),
        )

    async def get_coin_futures_all_orders(
        self,
        *,
        symbol: str | None = None,
        pair: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v1/allOrders`` with signed authentication."""
        return await self._native_private(
            "get_coin_futures_all_orders",
            self._params(
                symbol=symbol,
                pair=pair,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_account_trades(
        self,
        *,
        symbol: str | None = None,
        pair: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v1/userTrades`` with signed authentication."""
        return await self._native_private(
            "get_coin_futures_account_trades",
            self._params(
                symbol=symbol,
                pair=pair,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                fromId=from_id,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def place_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> list[dict[str, Any]]:
        """Place a futures batch; each response item may independently fail."""
        return await self._native_private(
            "place_futures_batch_orders",
            self._params(batchOrders=dumps(orders), recvWindow=recv_window),
        )

    async def amend_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> list[dict[str, Any]]:
        """Amend a futures batch; each response item may independently fail."""
        return await self._native_private(
            "amend_futures_batch_orders",
            self._params(batchOrders=dumps(orders), recvWindow=recv_window),
        )

    async def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        *,
        order_ids: list[int] | None = None,
        client_order_ids: list[str] | None = None,
        recv_window: int | None = None,
    ) -> list[dict[str, Any]]:
        """Cancel a futures batch; each response item may independently fail."""
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._params(
                product_symbol=product_symbol,
                orderIdList=dumps(order_ids) if order_ids is not None else None,
                origClientOrderIdList=dumps(client_order_ids)
                if client_order_ids is not None
                else None,
                recvWindow=recv_window,
            ),
        )

    async def place_coin_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> list[dict[str, Any]]:
        """Place a coin_futures batch; each response item may independently fail."""
        return await self._native_private(
            "place_coin_futures_batch_orders",
            self._params(batchOrders=dumps(orders), recvWindow=recv_window),
        )

    async def amend_coin_futures_batch_orders(
        self, orders: list[dict[str, Any]], *, recv_window: int | None = None
    ) -> list[dict[str, Any]]:
        """Amend a coin_futures batch; each response item may independently fail."""
        return await self._native_private(
            "amend_coin_futures_batch_orders",
            self._params(batchOrders=dumps(orders), recvWindow=recv_window),
        )

    async def cancel_coin_futures_batch_orders(
        self,
        symbol: str,
        *,
        order_ids: list[int] | None = None,
        client_order_ids: list[str] | None = None,
        recv_window: int | None = None,
    ) -> list[dict[str, Any]]:
        """Cancel a coin_futures batch; each response item may independently fail."""
        return await self._native_private(
            "cancel_coin_futures_batch_orders",
            self._params(
                symbol=symbol,
                orderIdList=dumps(order_ids) if order_ids is not None else None,
                origClientOrderIdList=dumps(client_order_ids)
                if client_order_ids is not None
                else None,
                recvWindow=recv_window,
            ),
        )

    async def create_coin_futures_listen_key(self) -> dict[str, Any]:
        """POST /dapi/v1/listenKey; uses the account API key without a signature."""
        return await self._native_private("create_coin_futures_listen_key", [])

    async def keep_alive_coin_futures_listen_key(self) -> dict[str, Any]:
        """PUT /dapi/v1/listenKey; uses the account API key without a signature."""
        return await self._native_private("keep_alive_coin_futures_listen_key", [])

    async def close_coin_futures_listen_key(self) -> dict[str, Any]:
        """DELETE /dapi/v1/listenKey; uses the account API key without a signature."""
        return await self._native_private("close_coin_futures_listen_key", [])

    async def create_pm_listen_key(self) -> dict[str, Any]:
        """POST /papi/v1/listenKey; uses the account API key without a signature."""
        return await self._native_private("create_pm_listen_key", [])

    async def keep_alive_pm_listen_key(self) -> dict[str, Any]:
        """PUT /papi/v1/listenKey; uses the account API key without a signature."""
        return await self._native_private("keep_alive_pm_listen_key", [])

    async def close_pm_listen_key(self) -> dict[str, Any]:
        """DELETE /papi/v1/listenKey; uses the account API key without a signature."""
        return await self._native_private("close_pm_listen_key", [])

    async def cancel_replace_spot_order(
        self,
        product_symbol: str,
        side: str,
        order_type: str,
        cancel_replace_mode: str,
        *,
        time_in_force: str | None = None,
        quantity: str | None = None,
        quote_order_qty: str | None = None,
        price: str | None = None,
        cancel_new_client_order_id: str | None = None,
        cancel_orig_client_order_id: str | None = None,
        cancel_order_id: int | None = None,
        new_client_order_id: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        stop_price: str | None = None,
        trailing_delta: int | None = None,
        iceberg_qty: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        cancel_restrictions: str | None = None,
        order_rate_limit_exceeded_mode: str | None = None,
        peg_price_type: str | None = None,
        peg_offset_value: int | None = None,
        peg_offset_type: str | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any]:
        """Cancel and replace an order; partial failures include both outcomes in the error."""
        return await self._native_private(
            "cancel_replace_spot_order",
            self._params(
                product_symbol=product_symbol,
                side=side,
                type=order_type,
                cancelReplaceMode=cancel_replace_mode,
                timeInForce=time_in_force,
                quantity=quantity,
                quoteOrderQty=quote_order_qty,
                price=price,
                cancelNewClientOrderId=cancel_new_client_order_id,
                cancelOrigClientOrderId=cancel_orig_client_order_id,
                cancelOrderId=cancel_order_id,
                newClientOrderId=new_client_order_id,
                strategyId=strategy_id,
                strategyType=strategy_type,
                stopPrice=stop_price,
                trailingDelta=trailing_delta,
                icebergQty=iceberg_qty,
                newOrderRespType=new_order_resp_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                cancelRestrictions=cancel_restrictions,
                orderRateLimitExceededMode=order_rate_limit_exceeded_mode,
                pegPriceType=peg_price_type,
                pegOffsetValue=peg_offset_value,
                pegOffsetType=peg_offset_type,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_income_history(
        self,
        *,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/income.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-income-history

        """
        return await self._native_private(
            "get_coin_futures_income_history",
            self._params(
                symbol=symbol,
                incomeType=income_type,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_commission_rate(
        self, *, symbol: str, recv_window: int | None = None
    ) -> Any:
        """

        GET /dapi/v1/commissionRate.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#user-commission-rate

        """
        return await self._native_private(
            "get_coin_futures_commission_rate", self._params(symbol=symbol, recvWindow=recv_window)
        )

    async def adjust_coin_futures_position_margin(
        self,
        *,
        symbol: str,
        amount: str,
        kind_type: int,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        POST /dapi/v1/positionMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#modify-isolated-position-margin

        """
        return await self._native_private(
            "adjust_coin_futures_position_margin",
            self._params(
                symbol=symbol,
                amount=amount,
                type=kind_type,
                positionSide=position_side,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_adl_quantiles(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        GET /dapi/v1/adlQuantile.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#position-adl-quantile-estimation

        """
        return await self._native_private(
            "get_coin_futures_adl_quantiles", self._params(symbol=symbol, recvWindow=recv_window)
        )

    async def get_coin_futures_force_orders(
        self,
        *,
        symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /dapi/v1/forceOrders.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#users-force-orders

        """
        return await self._native_private(
            "get_coin_futures_force_orders",
            self._params(
                symbol=symbol,
                autoCloseType=auto_close_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_coin_income_history(
        self,
        *,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /papi/v1/cm/income.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-cm-income-history

        """
        return await self._native_private(
            "get_pm_coin_income_history",
            self._params(
                symbol=symbol,
                incomeType=income_type,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_margin_interest_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        archived: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /papi/v1/margin/marginInterestHistory.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-margin-borrow-loan-interest-history

        """
        return await self._native_private(
            "get_pm_margin_interest_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                archived=archived,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_futures_income_history(
        self,
        *,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /papi/v1/um/income.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-income-history

        """
        return await self._native_private(
            "get_pm_futures_income_history",
            self._params(
                product_symbol=product_symbol,
                incomeType=income_type,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_coin_commission_rate(
        self, *, symbol: str, recv_window: int | None = None
    ) -> Any:
        """

        GET /papi/v1/cm/commissionRate.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-user-commission-rate-for-cm

        """
        return await self._native_private(
            "get_pm_coin_commission_rate", self._params(symbol=symbol, recvWindow=recv_window)
        )

    async def get_pm_futures_commission_rate(
        self, *, product_symbol: str, recv_window: int | None = None
    ) -> Any:
        """

        GET /papi/v1/um/commissionRate.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-user-commission-rate-for-um

        """
        return await self._native_private(
            "get_pm_futures_commission_rate",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_pm_margin_loan_records(
        self,
        *,
        asset: str,
        tx_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        archived: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /papi/v1/margin/marginLoan.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-loan-record

        """
        return await self._native_private(
            "get_pm_margin_loan_records",
            self._params(
                asset=asset,
                txId=tx_id,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                archived=archived,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_margin_transferable_amount(
        self, *, asset: str, recv_window: int | None = None
    ) -> Any:
        """

        GET /papi/v1/margin/maxWithdraw.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-max-withdraw

        """
        return await self._native_private(
            "get_pm_margin_transferable_amount", self._params(asset=asset, recvWindow=recv_window)
        )

    async def get_pm_margin_repayment_records(
        self,
        *,
        asset: str,
        tx_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        archived: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /papi/v1/margin/repayLoan.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-repay-record

        """
        return await self._native_private(
            "get_pm_margin_repayment_records",
            self._params(
                asset=asset,
                txId=tx_id,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                archived=archived,
                recvWindow=recv_window,
            ),
        )

    async def get_pm_order_rate_limits(self, *, recv_window: int | None = None) -> Any:
        """

        GET /papi/v1/rateLimit/order.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-user-rate-limit

        """
        return await self._native_private(
            "get_pm_order_rate_limits", self._params(recvWindow=recv_window)
        )

    async def get_futures_account_config(self, *, recv_window: int | None = None) -> Any:
        """

        GET /fapi/v1/accountConfig.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-account-configuration

        """
        return await self._native_private(
            "get_futures_account_config", self._params(recvWindow=recv_window)
        )

    async def get_futures_trading_status(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        GET /fapi/v1/apiTradingStatus.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-trading-quantitative-rules-indicators

        """
        return await self._native_private(
            "get_futures_trading_status",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_futures_multi_assets_mode(self, *, recv_window: int | None = None) -> Any:
        """

        GET /fapi/v1/multiAssetsMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-current-multi-assets-mode

        """
        return await self._native_private(
            "get_futures_multi_assets_mode", self._params(recvWindow=recv_window)
        )

    async def get_futures_order_rate_limits(self, *, recv_window: int | None = None) -> Any:
        """

        GET /fapi/v1/rateLimit/order.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#query-user-rate-limit

        """
        return await self._native_private(
            "get_futures_order_rate_limits", self._params(recvWindow=recv_window)
        )

    async def get_futures_symbol_config(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        GET /fapi/v1/symbolConfig.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#symbol-configuration

        """
        return await self._native_private(
            "get_futures_symbol_config",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def set_futures_multi_assets_mode(
        self, *, multi_assets_margin: str, recv_window: int | None = None
    ) -> Any:
        """

        POST /fapi/v1/multiAssetsMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#change-multi-assets-mode

        """
        return await self._native_private(
            "set_futures_multi_assets_mode",
            self._params(multiAssetsMargin=multi_assets_margin, recvWindow=recv_window),
        )

    async def adjust_futures_position_margin(
        self,
        *,
        product_symbol: str,
        amount: str,
        kind_type: int,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        POST /fapi/v1/positionMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#modify-isolated-position-margin

        """
        return await self._native_private(
            "adjust_futures_position_margin",
            self._params(
                product_symbol=product_symbol,
                amount=amount,
                type=kind_type,
                positionSide=position_side,
                recvWindow=recv_window,
            ),
        )

    async def get_futures_adl_quantiles(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        GET /fapi/v1/adlQuantile.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#position-adl-quantile-estimation

        """
        return await self._native_private(
            "get_futures_adl_quantiles",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_futures_force_orders(
        self,
        *,
        product_symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /fapi/v1/forceOrders.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#users-force-orders

        """
        return await self._native_private(
            "get_futures_force_orders",
            self._params(
                product_symbol=product_symbol,
                autoCloseType=auto_close_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_margin_risk_coefficients(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/margin/tradeCoeff.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#get-summary-of-margin-account

        """
        return await self._native_private(
            "get_margin_risk_coefficients", self._params(recvWindow=recv_window)
        )

    async def get_margin_capital_flow(
        self,
        *,
        asset: str | None = None,
        product_symbol: str | None = None,
        kind_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/margin/capital-flow.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-cross-isolated-margin-capital-flow

        """
        return await self._native_private(
            "get_margin_capital_flow",
            self._params(
                asset=asset,
                product_symbol=product_symbol,
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                fromId=from_id,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_margin_liquidation_records(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        isolated_symbol: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/margin/forceLiquidationRec.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-force-liquidation-record

        """
        return await self._native_private(
            "get_margin_liquidation_records",
            self._params(
                startTime=start_time,
                endTime=end_time,
                isolatedSymbol=isolated_symbol,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    async def cancel_margin_order_list(
        self,
        *,
        product_symbol: str,
        is_isolated: str | None = None,
        order_list_id: int | None = None,
        list_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        DELETE /sapi/v1/margin/orderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-cancel-oco

        """
        return await self._native_private(
            "cancel_margin_order_list",
            self._params(
                product_symbol=product_symbol,
                isIsolated=is_isolated,
                orderListId=order_list_id,
                listClientOrderId=list_client_order_id,
                newClientOrderId=new_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def get_margin_order_rate_limits(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/margin/rateLimit/order.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-current-margin-order-count-usage

        """
        return await self._native_private(
            "get_margin_order_rate_limits",
            self._params(
                isIsolated=is_isolated, product_symbol=product_symbol, recvWindow=recv_window
            ),
        )

    async def get_margin_all_order_lists(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/margin/allOrderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-all-oco

        """
        return await self._native_private(
            "get_margin_all_order_lists",
            self._params(
                isIsolated=is_isolated,
                product_symbol=product_symbol,
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_margin_order_list(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        order_list_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/margin/orderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-oco

        """
        return await self._native_private(
            "get_margin_order_list",
            self._params(
                isIsolated=is_isolated,
                product_symbol=product_symbol,
                orderListId=order_list_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def get_margin_open_order_lists(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/margin/openOrderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-open-oco

        """
        return await self._native_private(
            "get_margin_open_order_lists",
            self._params(
                isIsolated=is_isolated, product_symbol=product_symbol, recvWindow=recv_window
            ),
        )

    async def close_margin_listen_key(self) -> Any:
        """

        DELETE /sapi/v1/margin/listen-key.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream#close-user-data-stream

        """
        return await self._native_private("close_margin_listen_key", self._params())

    async def keep_alive_margin_listen_key(self, *, listen_key: str) -> Any:
        """

        PUT /sapi/v1/margin/listen-key.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream#keepalive-user-data-stream

        """
        return await self._native_private(
            "keep_alive_margin_listen_key", self._params(listenKey=listen_key)
        )

    async def create_margin_listen_key(self) -> Any:
        """

        POST /sapi/v1/margin/listen-key.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream#start-user-data-stream

        """
        return await self._native_private("create_margin_listen_key", self._params())

    async def get_account_trading_status(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/account/apiTradingStatus.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-api-trading-status

        """
        return await self._native_private(
            "get_account_trading_status", self._params(recvWindow=recv_window)
        )

    async def get_account_status(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/account/status.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-status

        """
        return await self._native_private(
            "get_account_status", self._params(recvWindow=recv_window)
        )

    async def get_api_key_permissions(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/account/apiRestrictions.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#get-api-key-permission

        """
        return await self._native_private(
            "get_api_key_permissions", self._params(recvWindow=recv_window)
        )

    async def get_spot_trade_fees(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        GET /sapi/v1/asset/tradeFee.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#trade-fee

        """
        return await self._native_private(
            "get_spot_trade_fees",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    async def get_user_assets(
        self,
        *,
        asset: str | None = None,
        need_btc_valuation: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        POST /sapi/v3/asset/getUserAsset.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#user-asset

        """
        return await self._native_private(
            "get_user_assets",
            self._params(asset=asset, needBtcValuation=need_btc_valuation, recvWindow=recv_window),
        )

    async def get_coin_network_config(self, *, recv_window: int | None = None) -> Any:
        """

        GET /sapi/v1/capital/config/getall.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#all-coins-information

        """
        return await self._native_private(
            "get_coin_network_config", self._params(recvWindow=recv_window)
        )

    async def get_deposit_address(
        self,
        *,
        coin: str,
        network: str | None = None,
        amount: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        GET /sapi/v1/capital/deposit/address.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#deposit-address

        """
        return await self._native_private(
            "get_deposit_address",
            self._params(coin=coin, network=network, amount=amount, recvWindow=recv_window),
        )

    async def get_deposit_history(
        self,
        *,
        include_source: bool | None = None,
        coin: str | None = None,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
        tx_id: str | None = None,
    ) -> Any:
        """

        GET /sapi/v1/capital/deposit/hisrec.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#deposit-history

        """
        return await self._native_private(
            "get_deposit_history",
            self._params(
                includeSource=include_source,
                coin=coin,
                status=status,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
                recvWindow=recv_window,
                txId=tx_id,
            ),
        )

    async def place_margin_oco(
        self,
        *,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        stop_price: str,
        is_isolated: str | None = None,
        list_client_order_id: str | None = None,
        limit_client_order_id: str | None = None,
        limit_iceberg_qty: str | None = None,
        stop_client_order_id: str | None = None,
        stop_limit_price: str | None = None,
        stop_iceberg_qty: str | None = None,
        stop_limit_time_in_force: str | None = None,
        new_order_resp_type: str | None = None,
        side_effect_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        auto_repay_at_cancel: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Both legs share quantity; cancelling either leg cancels the entire list.

        POST /sapi/v1/margin/order/oco. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-oco

        """
        return await self._native_private(
            "place_margin_oco",
            self._params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                isIsolated=is_isolated,
                listClientOrderId=list_client_order_id,
                limitClientOrderId=limit_client_order_id,
                limitIcebergQty=limit_iceberg_qty,
                stopClientOrderId=stop_client_order_id,
                stopLimitPrice=stop_limit_price,
                stopIcebergQty=stop_iceberg_qty,
                stopLimitTimeInForce=stop_limit_time_in_force,
                newOrderRespType=new_order_resp_type,
                sideEffectType=side_effect_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                autoRepayAtCancel=auto_repay_at_cancel,
                recvWindow=recv_window,
            ),
        )

    async def place_margin_oto(
        self,
        *,
        product_symbol: str,
        working_type: str,
        working_side: str,
        working_price: str,
        working_quantity: str,
        working_iceberg_qty: str,
        pending_type: str,
        pending_side: str,
        pending_quantity: str,
        is_isolated: str | None = None,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        side_effect_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        auto_repay_at_cancel: bool | None = None,
        working_client_order_id: str | None = None,
        working_time_in_force: str | None = None,
        pending_client_order_id: str | None = None,
        pending_price: str | None = None,
        pending_stop_price: str | None = None,
        pending_trailing_delta: int | None = None,
        pending_iceberg_qty: str | None = None,
        pending_time_in_force: str | None = None,
    ) -> Any:
        """

        Pending orders activate only after the working order fully fills.

        POST /sapi/v1/margin/order/oto. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-oto

        """
        return await self._native_private(
            "place_margin_oto",
            self._params(
                product_symbol=product_symbol,
                workingType=working_type,
                workingSide=working_side,
                workingPrice=working_price,
                workingQuantity=working_quantity,
                workingIcebergQty=working_iceberg_qty,
                pendingType=pending_type,
                pendingSide=pending_side,
                pendingQuantity=pending_quantity,
                isIsolated=is_isolated,
                listClientOrderId=list_client_order_id,
                newOrderRespType=new_order_resp_type,
                sideEffectType=side_effect_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                autoRepayAtCancel=auto_repay_at_cancel,
                workingClientOrderId=working_client_order_id,
                workingTimeInForce=working_time_in_force,
                pendingClientOrderId=pending_client_order_id,
                pendingPrice=pending_price,
                pendingStopPrice=pending_stop_price,
                pendingTrailingDelta=pending_trailing_delta,
                pendingIcebergQty=pending_iceberg_qty,
                pendingTimeInForce=pending_time_in_force,
            ),
        )

    async def place_margin_otoco(
        self,
        *,
        product_symbol: str,
        working_type: str,
        working_side: str,
        working_price: str,
        working_quantity: str,
        pending_side: str,
        pending_quantity: str,
        pending_above_type: str,
        is_isolated: str | None = None,
        side_effect_type: str | None = None,
        auto_repay_at_cancel: bool | None = None,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: str | None = None,
        working_time_in_force: str | None = None,
        pending_above_client_order_id: str | None = None,
        pending_above_price: str | None = None,
        pending_above_stop_price: str | None = None,
        pending_above_trailing_delta: int | None = None,
        pending_above_iceberg_qty: str | None = None,
        pending_above_time_in_force: str | None = None,
        pending_below_type: str | None = None,
        pending_below_client_order_id: str | None = None,
        pending_below_price: str | None = None,
        pending_below_stop_price: str | None = None,
        pending_below_trailing_delta: int | None = None,
        pending_below_iceberg_qty: str | None = None,
        pending_below_time_in_force: str | None = None,
    ) -> Any:
        """

        Pending orders activate only after the working order fully fills.

        POST /sapi/v1/margin/order/otoco. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-otoco

        """
        return await self._native_private(
            "place_margin_otoco",
            self._params(
                product_symbol=product_symbol,
                workingType=working_type,
                workingSide=working_side,
                workingPrice=working_price,
                workingQuantity=working_quantity,
                pendingSide=pending_side,
                pendingQuantity=pending_quantity,
                pendingAboveType=pending_above_type,
                isIsolated=is_isolated,
                sideEffectType=side_effect_type,
                autoRepayAtCancel=auto_repay_at_cancel,
                listClientOrderId=list_client_order_id,
                newOrderRespType=new_order_resp_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                workingClientOrderId=working_client_order_id,
                workingIcebergQty=working_iceberg_qty,
                workingTimeInForce=working_time_in_force,
                pendingAboveClientOrderId=pending_above_client_order_id,
                pendingAbovePrice=pending_above_price,
                pendingAboveStopPrice=pending_above_stop_price,
                pendingAboveTrailingDelta=pending_above_trailing_delta,
                pendingAboveIcebergQty=pending_above_iceberg_qty,
                pendingAboveTimeInForce=pending_above_time_in_force,
                pendingBelowType=pending_below_type,
                pendingBelowClientOrderId=pending_below_client_order_id,
                pendingBelowPrice=pending_below_price,
                pendingBelowStopPrice=pending_below_stop_price,
                pendingBelowTrailingDelta=pending_below_trailing_delta,
                pendingBelowIcebergQty=pending_below_iceberg_qty,
                pendingBelowTimeInForce=pending_below_time_in_force,
            ),
        )

    async def place_spot_opo(
        self,
        *,
        product_symbol: str,
        working_type: str,
        working_side: str,
        working_price: str,
        working_quantity: str,
        pending_type: str,
        pending_side: str,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: str | None = None,
        working_time_in_force: str | None = None,
        working_strategy_id: int | None = None,
        working_strategy_type: int | None = None,
        working_peg_price_type: str | None = None,
        working_peg_offset_type: str | None = None,
        working_peg_offset_value: int | None = None,
        pending_client_order_id: str | None = None,
        pending_price: str | None = None,
        pending_stop_price: str | None = None,
        pending_trailing_delta: int | None = None,
        pending_iceberg_qty: str | None = None,
        pending_time_in_force: str | None = None,
        pending_strategy_id: int | None = None,
        pending_strategy_type: int | None = None,
        pending_peg_price_type: str | None = None,
        pending_peg_offset_type: str | None = None,
        pending_peg_offset_value: int | None = None,
        recv_window: str | None = None,
    ) -> Any:
        """

        Working BUY must fully fill before pending SELL orders use its received funds; no
        pending quantity is accepted.

        POST /api/v3/orderList/opo. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-opo

        """
        return await self._native_private(
            "place_spot_opo",
            self._params(
                product_symbol=product_symbol,
                workingType=working_type,
                workingSide=working_side,
                workingPrice=working_price,
                workingQuantity=working_quantity,
                pendingType=pending_type,
                pendingSide=pending_side,
                listClientOrderId=list_client_order_id,
                newOrderRespType=new_order_resp_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                workingClientOrderId=working_client_order_id,
                workingIcebergQty=working_iceberg_qty,
                workingTimeInForce=working_time_in_force,
                workingStrategyId=working_strategy_id,
                workingStrategyType=working_strategy_type,
                workingPegPriceType=working_peg_price_type,
                workingPegOffsetType=working_peg_offset_type,
                workingPegOffsetValue=working_peg_offset_value,
                pendingClientOrderId=pending_client_order_id,
                pendingPrice=pending_price,
                pendingStopPrice=pending_stop_price,
                pendingTrailingDelta=pending_trailing_delta,
                pendingIcebergQty=pending_iceberg_qty,
                pendingTimeInForce=pending_time_in_force,
                pendingStrategyId=pending_strategy_id,
                pendingStrategyType=pending_strategy_type,
                pendingPegPriceType=pending_peg_price_type,
                pendingPegOffsetType=pending_peg_offset_type,
                pendingPegOffsetValue=pending_peg_offset_value,
                recvWindow=recv_window,
            ),
        )

    async def place_spot_opoco(
        self,
        *,
        product_symbol: str,
        working_type: str,
        working_side: str,
        working_price: str,
        working_quantity: str,
        pending_side: str,
        pending_above_type: str,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: str | None = None,
        working_time_in_force: str | None = None,
        working_strategy_id: int | None = None,
        working_strategy_type: int | None = None,
        working_peg_price_type: str | None = None,
        working_peg_offset_type: str | None = None,
        working_peg_offset_value: int | None = None,
        pending_above_client_order_id: str | None = None,
        pending_above_price: str | None = None,
        pending_above_stop_price: str | None = None,
        pending_above_trailing_delta: int | None = None,
        pending_above_iceberg_qty: str | None = None,
        pending_above_time_in_force: str | None = None,
        pending_above_strategy_id: int | None = None,
        pending_above_strategy_type: int | None = None,
        pending_above_peg_price_type: str | None = None,
        pending_above_peg_offset_type: str | None = None,
        pending_above_peg_offset_value: int | None = None,
        pending_below_type: str | None = None,
        pending_below_client_order_id: str | None = None,
        pending_below_price: str | None = None,
        pending_below_stop_price: str | None = None,
        pending_below_trailing_delta: int | None = None,
        pending_below_iceberg_qty: str | None = None,
        pending_below_time_in_force: str | None = None,
        pending_below_strategy_id: int | None = None,
        pending_below_strategy_type: int | None = None,
        pending_below_peg_price_type: str | None = None,
        pending_below_peg_offset_type: str | None = None,
        pending_below_peg_offset_value: int | None = None,
        recv_window: str | None = None,
    ) -> Any:
        """

        Working BUY must fully fill before pending SELL orders use its received funds; no
        pending quantity is accepted.

        POST /api/v3/orderList/opoco. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-opoco

        """
        return await self._native_private(
            "place_spot_opoco",
            self._params(
                product_symbol=product_symbol,
                workingType=working_type,
                workingSide=working_side,
                workingPrice=working_price,
                workingQuantity=working_quantity,
                pendingSide=pending_side,
                pendingAboveType=pending_above_type,
                listClientOrderId=list_client_order_id,
                newOrderRespType=new_order_resp_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                workingClientOrderId=working_client_order_id,
                workingIcebergQty=working_iceberg_qty,
                workingTimeInForce=working_time_in_force,
                workingStrategyId=working_strategy_id,
                workingStrategyType=working_strategy_type,
                workingPegPriceType=working_peg_price_type,
                workingPegOffsetType=working_peg_offset_type,
                workingPegOffsetValue=working_peg_offset_value,
                pendingAboveClientOrderId=pending_above_client_order_id,
                pendingAbovePrice=pending_above_price,
                pendingAboveStopPrice=pending_above_stop_price,
                pendingAboveTrailingDelta=pending_above_trailing_delta,
                pendingAboveIcebergQty=pending_above_iceberg_qty,
                pendingAboveTimeInForce=pending_above_time_in_force,
                pendingAboveStrategyId=pending_above_strategy_id,
                pendingAboveStrategyType=pending_above_strategy_type,
                pendingAbovePegPriceType=pending_above_peg_price_type,
                pendingAbovePegOffsetType=pending_above_peg_offset_type,
                pendingAbovePegOffsetValue=pending_above_peg_offset_value,
                pendingBelowType=pending_below_type,
                pendingBelowClientOrderId=pending_below_client_order_id,
                pendingBelowPrice=pending_below_price,
                pendingBelowStopPrice=pending_below_stop_price,
                pendingBelowTrailingDelta=pending_below_trailing_delta,
                pendingBelowIcebergQty=pending_below_iceberg_qty,
                pendingBelowTimeInForce=pending_below_time_in_force,
                pendingBelowStrategyId=pending_below_strategy_id,
                pendingBelowStrategyType=pending_below_strategy_type,
                pendingBelowPegPriceType=pending_below_peg_price_type,
                pendingBelowPegOffsetType=pending_below_peg_offset_type,
                pendingBelowPegOffsetValue=pending_below_peg_offset_value,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_download_id_for_futures_order_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For Futures Order History (USER_DATA).

        GET /dapi/v1/order/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-download-id-for-futures-order-history

        """
        return await self._native_private(
            "get_coin_futures_download_id_for_futures_order_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_coin_futures_download_id_for_futures_trade_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For Futures Trade History (USER_DATA).

        GET /dapi/v1/trade/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-download-id-for-futures-trade-history

        """
        return await self._native_private(
            "get_coin_futures_download_id_for_futures_trade_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_coin_futures_download_id_for_futures_transaction_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For Futures Transaction History (USER_DATA).

        GET /dapi/v1/income/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-download-id-for-futures-transaction-history

        """
        return await self._native_private(
            "get_coin_futures_download_id_for_futures_transaction_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_coin_futures_futures_order_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get Futures Order History Download Link by Id (USER_DATA).

        GET /dapi/v1/order/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-order-history-download-link-by-id

        """
        return await self._native_private(
            "get_coin_futures_futures_order_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_coin_futures_futures_trade_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get Futures Trade Download Link by Id (USER_DATA).

        GET /dapi/v1/trade/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-trade-download-link-by-id

        """
        return await self._native_private(
            "get_coin_futures_futures_trade_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_coin_futures_futures_transaction_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get Futures Transaction History Download Link by Id (USER_DATA).

        GET /dapi/v1/income/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-transaction-history-download-link-by-id

        """
        return await self._native_private(
            "get_coin_futures_futures_transaction_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_coin_futures_order_modify_history(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Get Order Modify History (USER_DATA).

        GET /dapi/v1/orderAmendment. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#get-order-modify-history

        """
        return await self._native_private(
            "get_coin_futures_order_modify_history",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_coin_futures_position_margin_change_history(
        self,
        *,
        symbol: str,
        kind_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Get Position Margin Change History (TRADE).

        GET /dapi/v1/positionMargin/history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#get-position-margin-change-history

        """
        return await self._native_private(
            "get_coin_futures_position_margin_change_history",
            self._params(
                symbol=symbol,
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def query_coin_futures_current_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Current Open Order (USER_DATA).

        GET /dapi/v1/openOrder. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#query-current-open-order

        """
        return await self._native_private(
            "query_coin_futures_current_open_order",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def pm_bnb_transfer(
        self, *, amount: str, transfer_side: str, recv_window: int | None = None
    ) -> Any:
        """

        BNB transfer (TRADE).

        POST /papi/v1/bnb-transfer. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#bnb-transfer

        """
        return await self._native_private(
            "pm_bnb_transfer",
            self._params(amount=amount, transferSide=transfer_side, recvWindow=recv_window),
        )

    async def change_pm_auto_repay_futures_status(
        self, *, auto_repay: str, recv_window: int | None = None
    ) -> Any:
        """

        Change Auto-repay-futures Status (TRADE).

        POST /papi/v1/repay-futures-switch. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#change-auto-repay-futures-status

        """
        return await self._native_private(
            "change_pm_auto_repay_futures_status",
            self._params(autoRepay=auto_repay, recvWindow=recv_window),
        )

    async def pm_fund_auto_collection(self, *, recv_window: int | None = None) -> Any:
        """

        Fund Auto-collection (TRADE).

        POST /papi/v1/auto-collection. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#fund-auto-collection

        """
        return await self._native_private(
            "pm_fund_auto_collection", self._params(recvWindow=recv_window)
        )

    async def pm_fund_collection_by_asset(
        self, *, asset: str, recv_window: int | None = None
    ) -> Any:
        """

        Fund Collection by Asset (TRADE).

        POST /papi/v1/asset-collection. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#fund-collection-by-asset

        """
        return await self._native_private(
            "pm_fund_collection_by_asset", self._params(asset=asset, recvWindow=recv_window)
        )

    async def get_pm_auto_repay_futures_status(self, *, recv_window: int | None = None) -> Any:
        """

        Get Auto-repay-futures Status (USER_DATA).

        GET /papi/v1/repay-futures-switch. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-auto-repay-futures-status

        """
        return await self._native_private(
            "get_pm_auto_repay_futures_status", self._params(recvWindow=recv_window)
        )

    async def get_pm_download_id_for_um_futures_order_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For UM Futures Order History (USER_DATA).

        GET /papi/v1/um/order/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-download-id-for-um-futures-order-history

        """
        return await self._native_private(
            "get_pm_download_id_for_um_futures_order_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_pm_download_id_for_um_futures_trade_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For UM Futures Trade History (USER_DATA).

        GET /papi/v1/um/trade/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-download-id-for-um-futures-trade-history

        """
        return await self._native_private(
            "get_pm_download_id_for_um_futures_trade_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_pm_download_id_for_um_futures_transaction_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For UM Futures Transaction History (USER_DATA).

        GET /papi/v1/um/income/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-download-id-for-um-futures-transaction-history

        """
        return await self._native_private(
            "get_pm_download_id_for_um_futures_transaction_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_pm_um_account_detail_v2(self, *, recv_window: int | None = None) -> Any:
        """

        Get UM Account Detail V2 (USER_DATA).

        GET /papi/v2/um/account. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-account-detail-v2

        """
        return await self._native_private(
            "get_pm_um_account_detail_v2", self._params(recvWindow=recv_window)
        )

    async def get_pm_um_futures_order_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get UM Futures Order Download Link by Id (USER_DATA).

        GET /papi/v1/um/order/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-order-download-link-by-id

        """
        return await self._native_private(
            "get_pm_um_futures_order_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_pm_um_futures_trade_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get UM Futures Trade Download Link by Id (USER_DATA).

        GET /papi/v1/um/trade/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-trade-download-link-by-id

        """
        return await self._native_private(
            "get_pm_um_futures_trade_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_pm_um_futures_transaction_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get UM Futures Transaction Download Link by Id (USER_DATA).

        GET /papi/v1/um/income/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-transaction-download-link-by-id

        """
        return await self._native_private(
            "get_pm_um_futures_transaction_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def query_pm_portfolio_margin_negative_balance_interest_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Portfolio Margin Negative Balance Interest History (USER_DATA).

        GET /papi/v1/portfolio/interest-history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-portfolio-margin-negative-balance-interest-history

        """
        return await self._native_private(
            "query_pm_portfolio_margin_negative_balance_interest_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                size=size,
                recvWindow=recv_window,
            ),
        )

    async def query_pm_user_negative_balance_auto_exchange_record(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Query User Negative Balance Auto Exchange Record (USER_DATA).

        GET /papi/v1/portfolio/negative-balance-exchange-record. Native exchange symbols;
        decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-user-negative-balance-auto-exchange-record

        """
        return await self._native_private(
            "query_pm_user_negative_balance_auto_exchange_record",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def repay_pm_futures_negative_balance(self, *, recv_window: int | None = None) -> Any:
        """

        Repay futures Negative Balance (USER_DATA).

        POST /papi/v1/repay-futures-negative-balance. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#repay-futures-negative-balance

        """
        return await self._native_private(
            "repay_pm_futures_negative_balance", self._params(recvWindow=recv_window)
        )

    async def pm_futures_tradfi_perps_contract(self, *, recv_window: int | None = None) -> Any:
        """

        Futures TradFi Perps Contract (USER_DATA).

        POST /papi/v1/um/stock/contract. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#futures-tradfi-perps-contract

        """
        return await self._native_private(
            "pm_futures_tradfi_perps_contract", self._params(recvWindow=recv_window)
        )

    async def get_pm_um_futures_bnb_burn_status(self, *, recv_window: int | None = None) -> Any:
        """

        Get UM Futures BNB Burn Status (USER_DATA).

        GET /papi/v1/um/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#get-um-futures-bnb-burn-status

        """
        return await self._native_private(
            "get_pm_um_futures_bnb_burn_status", self._params(recvWindow=recv_window)
        )

    async def query_pm_current_cm_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Current CM Open Order (USER_DATA).

        GET /papi/v1/cm/openOrder. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-current-cm-open-order

        """
        return await self._native_private(
            "query_pm_current_cm_open_order",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def query_pm_current_um_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Current UM Open Order (USER_DATA).

        GET /papi/v1/um/openOrder. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-current-um-open-order

        """
        return await self._native_private(
            "query_pm_current_um_open_order",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    async def toggle_pm_bnb_burn_on_um_futures_trade(
        self, *, fee_burn: str, recv_window: int | None = None
    ) -> Any:
        """

        Toggle BNB Burn On UM Futures Trade (TRADE).

        POST /papi/v1/um/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#toggle-bnb-burn-on-um-futures-trade

        """
        return await self._native_private(
            "toggle_pm_bnb_burn_on_um_futures_trade",
            self._params(feeBurn=fee_burn, recvWindow=recv_window),
        )

    async def get_futures_bnb_burn_status(self, *, recv_window: int | None = None) -> Any:
        """

        Get BNB Burn Status (USER_DATA).

        GET /fapi/v1/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-bnb-burn-status

        """
        return await self._native_private(
            "get_futures_bnb_burn_status", self._params(recvWindow=recv_window)
        )

    async def get_futures_download_id_for_futures_order_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For Futures Order History (USER_DATA).

        GET /fapi/v1/order/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-order-history

        """
        return await self._native_private(
            "get_futures_download_id_for_futures_order_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_futures_download_id_for_futures_trade_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For Futures Trade History (USER_DATA).

        GET /fapi/v1/trade/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-trade-history

        """
        return await self._native_private(
            "get_futures_download_id_for_futures_trade_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_futures_download_id_for_futures_transaction_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:
        """

        Get Download Id For Futures Transaction History (USER_DATA).

        GET /fapi/v1/income/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-transaction-history

        """
        return await self._native_private(
            "get_futures_download_id_for_futures_transaction_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    async def get_futures_futures_order_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get Futures Order History Download Link by Id (USER_DATA).

        GET /fapi/v1/order/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-order-history-download-link-by-id

        """
        return await self._native_private(
            "get_futures_futures_order_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_futures_futures_trade_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get Futures Trade Download Link by Id (USER_DATA).

        GET /fapi/v1/trade/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-trade-download-link-by-id

        """
        return await self._native_private(
            "get_futures_futures_trade_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def get_futures_futures_transaction_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Get Futures Transaction History Download Link by Id (USER_DATA).

        GET /fapi/v1/income/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-transaction-history-download-link-by-id

        """
        return await self._native_private(
            "get_futures_futures_transaction_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    async def toggle_futures_bnb_burn_on_futures_trade(
        self, *, fee_burn: str, recv_window: int | None = None
    ) -> Any:
        """

        Toggle BNB Burn On Futures Trade (TRADE).

        POST /fapi/v1/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#toggle-bnb-burn-on-futures-trade

        """
        return await self._native_private(
            "toggle_futures_bnb_burn_on_futures_trade",
            self._params(feeBurn=fee_burn, recvWindow=recv_window),
        )

    async def futures_accept_the_offered_quote(
        self, *, quote_id: str, recv_window: int | None = None
    ) -> Any:
        """

        Accept the offered quote (USER_DATA).

        POST /fapi/v1/convert/acceptQuote. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#accept-the-offered-quote

        """
        return await self._native_private(
            "futures_accept_the_offered_quote",
            self._params(quoteId=quote_id, recvWindow=recv_window),
        )

    async def futures_order_status(
        self, *, order_id: str | None = None, quote_id: str | None = None
    ) -> Any:
        """

        Order status (USER_DATA).

        GET /fapi/v1/convert/orderStatus. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#order-status

        """
        return await self._native_private(
            "futures_order_status", self._params(orderId=order_id, quoteId=quote_id)
        )

    async def futures_send_quote_request(
        self,
        *,
        from_asset: str,
        to_asset: str,
        from_amount: str | None = None,
        to_amount: str | None = None,
        valid_time: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Send Quote Request (USER_DATA).

        POST /fapi/v1/convert/getQuote. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#send-quote-request

        """
        return await self._native_private(
            "futures_send_quote_request",
            self._params(
                fromAsset=from_asset,
                toAsset=to_asset,
                fromAmount=from_amount,
                toAmount=to_amount,
                validTime=valid_time,
                recvWindow=recv_window,
            ),
        )

    async def futures_classic_portfolio_margin_account_information(
        self, *, asset: str, recv_window: int | None = None
    ) -> Any:
        """

        Classic Portfolio Margin Account Information (USER_DATA).

        GET /fapi/v1/pmAccountInfo. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/portfolio-margin-endpoints#classic-portfolio-margin-account-information

        """
        return await self._native_private(
            "futures_classic_portfolio_margin_account_information",
            self._params(asset=asset, recvWindow=recv_window),
        )

    async def futures_futures_tradfi_perps_contract(self, *, recv_window: int | None = None) -> Any:
        """

        Futures TradFi Perps Contract (USER_DATA).

        POST /fapi/v1/stock/contract. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#futures-tradfi-perps-contract

        """
        return await self._native_private(
            "futures_futures_tradfi_perps_contract", self._params(recvWindow=recv_window)
        )

    async def get_futures_order_modify_history(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Get Order Modify History (USER_DATA).

        GET /fapi/v1/orderAmendment. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#get-order-modify-history

        """
        return await self._native_private(
            "get_futures_order_modify_history",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def get_futures_position_margin_change_history(
        self,
        *,
        symbol: str,
        kind_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Get Position Margin Change History (TRADE).

        GET /fapi/v1/positionMargin/history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#get-position-margin-change-history

        """
        return await self._native_private(
            "get_futures_position_margin_change_history",
            self._params(
                symbol=symbol,
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def adjust_margin_cross_margin_max_leverage(self, *, max_leverage: int) -> Any:
        """

        Adjust cross margin max leverage (USER_DATA).

        POST /sapi/v1/margin/max-leverage. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#adjust-cross-margin-max-leverage

        """
        return await self._native_private(
            "adjust_margin_cross_margin_max_leverage", self._params(maxLeverage=max_leverage)
        )

    async def get_margin_bnb_burn_status(self, *, recv_window: int | None = None) -> Any:
        """

        Get BNB Burn Status (USER_DATA).

        GET /sapi/v1/bnbBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#get-bnb-burn-status

        """
        return await self._native_private(
            "get_margin_bnb_burn_status", self._params(recvWindow=recv_window)
        )

    async def query_margin_cross_margin_fee_data(
        self,
        *,
        vip_level: int | None = None,
        coin: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Cross Margin Fee Data (USER_DATA).

        GET /sapi/v1/margin/crossMarginData. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-cross-margin-fee-data

        """
        return await self._native_private(
            "query_margin_cross_margin_fee_data",
            self._params(vipLevel=vip_level, coin=coin, recvWindow=recv_window),
        )

    async def query_margin_enabled_isolated_margin_account_limit(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Query Enabled Isolated Margin Account Limit (USER_DATA).

        GET /sapi/v1/margin/isolated/accountLimit. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-enabled-isolated-margin-account-limit

        """
        return await self._native_private(
            "query_margin_enabled_isolated_margin_account_limit",
            self._params(recvWindow=recv_window),
        )

    async def query_margin_isolated_margin_fee_data(
        self,
        *,
        vip_level: int | None = None,
        symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Isolated Margin Fee Data (USER_DATA).

        GET /sapi/v1/margin/isolatedMarginData. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-isolated-margin-fee-data

        """
        return await self._native_private(
            "query_margin_isolated_margin_fee_data",
            self._params(vipLevel=vip_level, symbol=symbol, recvWindow=recv_window),
        )

    async def get_margin_future_hourly_interest_rate(self, *, assets: str, is_isolated: str) -> Any:
        """

        Get future hourly interest rate (USER_DATA).

        GET /sapi/v1/margin/next-hourly-interest-rate. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/borrow-repay#get-future-hourly-interest-rate

        """
        return await self._native_private(
            "get_margin_future_hourly_interest_rate",
            self._params(assets=assets, isIsolated=is_isolated),
        )

    async def query_margin_margin_interest_rate_history(
        self,
        *,
        asset: str,
        vip_level: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Margin Interest Rate History (USER_DATA).

        GET /sapi/v1/margin/interestRateHistory. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/borrow-repay#query-margin-interest-rate-history

        """
        return await self._native_private(
            "query_margin_margin_interest_rate_history",
            self._params(
                asset=asset,
                vipLevel=vip_level,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def query_margin_isolated_margin_tier_data(
        self, *, symbol: str, tier: int | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Query Isolated Margin Tier Data (USER_DATA).

        GET /sapi/v1/margin/isolatedMarginTier. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#query-isolated-margin-tier-data

        """
        return await self._native_private(
            "query_margin_isolated_margin_tier_data",
            self._params(symbol=symbol, tier=tier, recvWindow=recv_window),
        )

    async def query_margin_margin_available_inventory(self, *, kind_type: str) -> Any:
        """

        Query Margin Available Inventory (USER_DATA).

        GET /sapi/v1/margin/available-inventory. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#query-margin-available-inventory

        """
        return await self._native_private(
            "query_margin_margin_available_inventory", self._params(type=kind_type)
        )

    async def create_margin_special_key(
        self,
        *,
        api_name: str,
        symbol: str | None = None,
        ip: str | None = None,
        public_key: str | None = None,
        permission_mode: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Create Special Key(Low-Latency Trading) (TRADE).

        POST /sapi/v1/margin/apiKey. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#create-special-key

        """
        return await self._native_private(
            "create_margin_special_key",
            self._params(
                apiName=api_name,
                symbol=symbol,
                ip=ip,
                publicKey=public_key,
                permissionMode=permission_mode,
                recvWindow=recv_window,
            ),
        )

    async def delete_margin_special_key(
        self,
        *,
        api_name: str | None = None,
        symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Delete Special Key(Low-Latency Trading) (TRADE).

        DELETE /sapi/v1/margin/apiKey. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#delete-special-key

        """
        return await self._native_private(
            "delete_margin_special_key",
            self._params(apiName=api_name, symbol=symbol, recvWindow=recv_window),
        )

    async def edit_margin_ip_for_special_key(
        self, *, ip: str, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Edit ip for Special Key(Low-Latency Trading) (TRADE).

        PUT /sapi/v1/margin/apiKey/ip. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#edit-ip-for-special-key

        """
        return await self._native_private(
            "edit_margin_ip_for_special_key",
            self._params(ip=ip, symbol=symbol, recvWindow=recv_window),
        )

    async def margin_exit_special_key_mode(self, *, recv_window: int | None = None) -> Any:
        """

        Exit Special Key Mode (TRADE).

        POST /sapi/v1/margin/exit-special-key-mode. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#exit-special-key-mode

        """
        return await self._native_private(
            "margin_exit_special_key_mode", self._params(recvWindow=recv_window)
        )

    async def get_margin_small_liability_exchange_coin_list(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Get Small Liability Exchange Coin List (USER_DATA).

        GET /sapi/v1/margin/exchange-small-liability. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-small-liability-exchange-coin-list

        """
        return await self._native_private(
            "get_margin_small_liability_exchange_coin_list", self._params(recvWindow=recv_window)
        )

    async def get_margin_small_liability_exchange_history(
        self,
        *,
        current: int,
        size: int,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Get Small Liability Exchange History (USER_DATA).

        GET /sapi/v1/margin/exchange-small-liability-history. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-small-liability-exchange-history

        """
        return await self._native_private(
            "get_margin_small_liability_exchange_history",
            self._params(
                current=current,
                size=size,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def margin_liquidation_loan_repay(
        self, *, asset: str, amount: str, recv_window: int | None = None
    ) -> Any:
        """

        Liquidation Loan Repay (MARGIN).

        POST /sapi/v1/margin/liquidation-loan/repay. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#liquidation-loan-repay

        """
        return await self._native_private(
            "margin_liquidation_loan_repay",
            self._params(asset=asset, amount=amount, recvWindow=recv_window),
        )

    async def margin_margin_manual_liquidation(
        self, *, kind_type: str, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Margin Manual Liquidation (TRADE).

        POST /sapi/v1/margin/manual-liquidation. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-manual-liquidation

        """
        return await self._native_private(
            "margin_margin_manual_liquidation",
            self._params(type=kind_type, symbol=symbol, recvWindow=recv_window),
        )

    async def query_margin_liquidation_loan(self, *, recv_window: int | None = None) -> Any:
        """

        Query Liquidation Loan (USER_DATA).

        GET /sapi/v1/margin/liquidation-loan. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-liquidation-loan

        """
        return await self._native_private(
            "query_margin_liquidation_loan", self._params(recvWindow=recv_window)
        )

    async def query_margin_liquidation_loan_repay_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Liquidation Loan Repay History (USER_DATA).

        GET /sapi/v1/margin/liquidation-loan/repay-history. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-liquidation-loan-repay-history

        """
        return await self._native_private(
            "query_margin_liquidation_loan_repay_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    async def query_margin_prevented_matches(
        self,
        *,
        symbol: str,
        prevented_match_id: int | None = None,
        order_id: int | None = None,
        from_prevented_match_id: int | None = None,
        is_isolated: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Prevented Matches (USER_DATA).

        GET /sapi/v1/margin/myPreventedMatches. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-prevented-matches

        """
        return await self._native_private(
            "query_margin_prevented_matches",
            self._params(
                symbol=symbol,
                preventedMatchId=prevented_match_id,
                orderId=order_id,
                fromPreventedMatchId=from_prevented_match_id,
                isIsolated=is_isolated,
                recvWindow=recv_window,
            ),
        )

    async def query_margin_special_key(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Query Special key(Low Latency Trading) (TRADE).

        GET /sapi/v1/margin/apiKey. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-special-key

        """
        return await self._native_private(
            "query_margin_special_key", self._params(symbol=symbol, recvWindow=recv_window)
        )

    async def query_margin_special_key_list(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Query Special key List(Low Latency Trading) (TRADE).

        GET /sapi/v1/margin/api-key-list. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-special-key-list

        """
        return await self._native_private(
            "query_margin_special_key_list", self._params(symbol=symbol, recvWindow=recv_window)
        )

    async def margin_small_liability_exchange(
        self, *, asset_names: str, recv_window: int | None = None
    ) -> Any:
        """

        Small Liability Exchange (MARGIN).

        POST /sapi/v1/margin/exchange-small-liability. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#small-liability-exchange

        """
        return await self._native_private(
            "margin_small_liability_exchange",
            self._params(assetNames=asset_names, recvWindow=recv_window),
        )

    async def get_margin_cross_margin_transfer_history(
        self,
        *,
        asset: str | None = None,
        kind_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        isolated_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Get Cross Margin Transfer History (USER_DATA).

        GET /sapi/v1/margin/transfer. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/transfer#get-cross-margin-transfer-history

        """
        return await self._native_private(
            "get_margin_cross_margin_transfer_history",
            self._params(
                asset=asset,
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                isolatedSymbol=isolated_symbol,
                recvWindow=recv_window,
            ),
        )

    async def spot_my_filters(self, *, symbol: str, recv_window: str | None = None) -> Any:
        """

        Query relevant filters (USER_DATA).

        GET /api/v3/myFilters. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/account#my-filters

        """
        return await self._native_private(
            "spot_my_filters", self._params(symbol=symbol, recvWindow=recv_window)
        )

    async def spot_order_amendments(
        self,
        *,
        symbol: str,
        order_id: int,
        from_execution_id: int | None = None,
        limit: int | None = None,
        recv_window: str | None = None,
    ) -> Any:
        """

        Query Order Amendments (USER_DATA).

        GET /api/v3/order/amendments. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/account#order-amendments

        """
        return await self._native_private(
            "spot_order_amendments",
            self._params(
                symbol=symbol,
                orderId=order_id,
                fromExecutionId=from_execution_id,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def spot_sor_order(
        self,
        *,
        symbol: str,
        side: str,
        kind_type: str,
        quantity: str,
        time_in_force: str | None = None,
        price: str | None = None,
        new_client_order_id: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        iceberg_qty: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        recv_window: str | None = None,
    ) -> Any:
        """

        New order using SOR (TRADE).

        POST /api/v3/sor/order. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#sor-order

        """
        return await self._native_private(
            "spot_sor_order",
            self._params(
                symbol=symbol,
                side=side,
                type=kind_type,
                quantity=quantity,
                timeInForce=time_in_force,
                price=price,
                newClientOrderId=new_client_order_id,
                strategyId=strategy_id,
                strategyType=strategy_type,
                icebergQty=iceberg_qty,
                newOrderRespType=new_order_resp_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                recvWindow=recv_window,
            ),
        )

    async def spot_sor_order_test(
        self,
        *,
        symbol: str,
        side: str,
        kind_type: str,
        quantity: str,
        compute_commission_rates: bool | None = None,
        time_in_force: str | None = None,
        price: str | None = None,
        new_client_order_id: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        iceberg_qty: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        recv_window: str | None = None,
    ) -> Any:
        """

        Test new order using SOR (TRADE).

        POST /api/v3/sor/order/test. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#sor-order-test

        """
        return await self._native_private(
            "spot_sor_order_test",
            self._params(
                symbol=symbol,
                side=side,
                type=kind_type,
                quantity=quantity,
                computeCommissionRates=compute_commission_rates,
                timeInForce=time_in_force,
                price=price,
                newClientOrderId=new_client_order_id,
                strategyId=strategy_id,
                strategyType=strategy_type,
                icebergQty=iceberg_qty,
                newOrderRespType=new_order_resp_type,
                selfTradePreventionMode=self_trade_prevention_mode,
                recvWindow=recv_window,
            ),
        )

    async def wallet_account_info(self, *, recv_window: int | None = None) -> Any:
        """

        Account info (USER_DATA).

        GET /sapi/v1/account/info. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-info

        """
        return await self._native_private(
            "wallet_account_info", self._params(recvWindow=recv_window)
        )

    async def wallet_daily_account_snapshot(
        self,
        *,
        kind_type: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Daily Account Snapshot (USER_DATA).

        GET /sapi/v1/accountSnapshot. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#daily-account-snapshot

        """
        return await self._native_private(
            "wallet_daily_account_snapshot",
            self._params(
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def wallet_asset_detail(
        self, *, asset: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Asset Detail (USER_DATA).

        GET /sapi/v1/asset/assetDetail. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#asset-detail

        """
        return await self._native_private(
            "wallet_asset_detail", self._params(asset=asset, recvWindow=recv_window)
        )

    async def wallet_asset_dividend_record(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Asset Dividend Record (USER_DATA).

        GET /sapi/v1/asset/assetDividend. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#asset-dividend-record

        """
        return await self._native_private(
            "wallet_asset_dividend_record",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    async def wallet_dust_convert(
        self,
        *,
        asset: str,
        account_type: str | None = None,
        client_id: str | None = None,
        target_asset: str | None = None,
        third_party_client_id: str | None = None,
        dust_quota_asset_to_target_asset_price: str | None = None,
    ) -> Any:
        """

        Dust Convert (USER_DATA).

        POST /sapi/v1/asset/dust-convert/convert. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-convert

        """
        return await self._native_private(
            "wallet_dust_convert",
            self._params(
                asset=asset,
                accountType=account_type,
                clientId=client_id,
                targetAsset=target_asset,
                thirdPartyClientId=third_party_client_id,
                dustQuotaAssetToTargetAssetPrice=dust_quota_asset_to_target_asset_price,
            ),
        )

    async def wallet_dust_convertible_assets(
        self,
        *,
        target_asset: str,
        account_type: str | None = None,
        dust_quota_asset_to_target_asset_price: str | None = None,
    ) -> Any:
        """

        Dust Convertible Assets (USER_DATA).

        POST /sapi/v1/asset/dust-convert/query-convertible-assets. Native exchange symbols;
        decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-convertible-assets

        """
        return await self._native_private(
            "wallet_dust_convertible_assets",
            self._params(
                targetAsset=target_asset,
                accountType=account_type,
                dustQuotaAssetToTargetAssetPrice=dust_quota_asset_to_target_asset_price,
            ),
        )

    async def wallet_dust_transfer(
        self, *, asset: str, account_type: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Dust Transfer (USER_DATA).

        POST /sapi/v1/asset/dust. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-transfer

        """
        return await self._native_private(
            "wallet_dust_transfer",
            self._params(asset=asset, accountType=account_type, recvWindow=recv_window),
        )

    async def wallet_dustlog(
        self,
        *,
        account_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        DustLog (USER_DATA).

        GET /sapi/v1/asset/dribblet. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dustlog

        """
        return await self._native_private(
            "wallet_dustlog",
            self._params(
                accountType=account_type,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    async def get_wallet_assets_that_can_be_converted_into_bnb(
        self, *, account_type: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Get Assets That Can Be Converted Into BNB (USER_DATA).

        POST /sapi/v1/asset/dust-btc. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-assets-that-can-be-converted-into-bnb

        """
        return await self._native_private(
            "get_wallet_assets_that_can_be_converted_into_bnb",
            self._params(accountType=account_type, recvWindow=recv_window),
        )

    async def toggle_wallet_bnb_burn_on_spot_trade_and_margin_interest(
        self,
        *,
        spot_bnb_burn: str | None = None,
        interest_bnb_burn: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Toggle BNB Burn On Spot Trade And Margin Interest (USER_DATA).

        POST /sapi/v1/bnbBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#toggle-bnb-burn-on-spot-trade-and-margin-interest

        """
        return await self._native_private(
            "toggle_wallet_bnb_burn_on_spot_trade_and_margin_interest",
            self._params(
                spotBNBBurn=spot_bnb_burn, interestBNBBurn=interest_bnb_burn, recvWindow=recv_window
            ),
        )

    async def wallet_fetch_deposit_address_list_with_network(
        self, *, coin: str, network: str | None = None
    ) -> Any:
        """

        Fetch deposit address list with network (USER_DATA).

        GET /sapi/v1/capital/deposit/address/list. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#fetch-deposit-address-list-with-network

        """
        return await self._native_private(
            "wallet_fetch_deposit_address_list_with_network",
            self._params(coin=coin, network=network),
        )

    async def wallet_one_click_arrival_deposit_apply(
        self,
        *,
        deposit_id: int | None = None,
        tx_id: str | None = None,
        sub_account_id: str | None = None,
        sub_user_id: int | None = None,
    ) -> Any:
        """

        One click arrival deposit apply (for expired address deposit) (USER_DATA).

        POST /sapi/v1/capital/deposit/credit-apply. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#one-click-arrival-deposit-apply

        """
        return await self._native_private(
            "wallet_one_click_arrival_deposit_apply",
            self._params(
                depositId=deposit_id, txId=tx_id, subAccountId=sub_account_id, subUserId=sub_user_id
            ),
        )

    async def algo_cancel_algo_order_future_algo(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Cancel Futures Algo Order (TRADE).

        DELETE /sapi/v1/algo/futures/order. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#cancel-algo-order-future-algo

        """
        return await self._native_private(
            "algo_cancel_algo_order_future_algo",
            self._params(algoId=algo_id, clientAlgoId=client_algo_id, recvWindow=recv_window),
        )

    async def query_algo_current_algo_open_orders_future_algo(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Query Current Futures Algo Open Orders (USER_DATA).

        GET /sapi/v1/algo/futures/openOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#query-current-algo-open-orders-future-algo

        """
        return await self._native_private(
            "query_algo_current_algo_open_orders_future_algo", self._params(recvWindow=recv_window)
        )

    async def query_algo_historical_algo_orders_future_algo(
        self,
        *,
        symbol: str | None = None,
        side: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Historical Futures Algo Orders (USER_DATA).

        GET /sapi/v1/algo/futures/historicalOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#query-historical-algo-orders-future-algo

        """
        return await self._native_private(
            "query_algo_historical_algo_orders_future_algo",
            self._params(
                symbol=symbol,
                side=side,
                startTime=start_time,
                endTime=end_time,
                page=page,
                pageSize=page_size,
                recvWindow=recv_window,
            ),
        )

    async def query_algo_sub_orders_future_algo(
        self,
        *,
        algo_id: int,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Futures Sub Orders (USER_DATA).

        GET /sapi/v1/algo/futures/subOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#query-sub-orders-future-algo

        """
        return await self._native_private(
            "query_algo_sub_orders_future_algo",
            self._params(algoId=algo_id, page=page, pageSize=page_size, recvWindow=recv_window),
        )

    async def algo_time_weighted_average_price_future_algo(
        self,
        *,
        symbol: str,
        side: str,
        quantity: str,
        duration: int,
        position_side: str | None = None,
        client_algo_id: str | None = None,
        reduce_only: bool | None = None,
        limit_price: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Time-Weighted Futures Average Price (Twap) New Order (TRADE).

        POST /sapi/v1/algo/futures/newOrderTwap. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#time-weighted-average-price-future-algo

        """
        return await self._native_private(
            "algo_time_weighted_average_price_future_algo",
            self._params(
                symbol=symbol,
                side=side,
                quantity=quantity,
                duration=duration,
                positionSide=position_side,
                clientAlgoId=client_algo_id,
                reduceOnly=reduce_only,
                limitPrice=limit_price,
                recvWindow=recv_window,
            ),
        )

    async def algo_volume_participation_future_algo(
        self,
        *,
        symbol: str,
        side: str,
        quantity: str,
        urgency: str,
        position_side: str | None = None,
        client_algo_id: str | None = None,
        reduce_only: bool | None = None,
        limit_price: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Volume Participation (VP) New Order (TRADE).

        POST /sapi/v1/algo/futures/newOrderVp. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#volume-participation-future-algo

        """
        return await self._native_private(
            "algo_volume_participation_future_algo",
            self._params(
                symbol=symbol,
                side=side,
                quantity=quantity,
                urgency=urgency,
                positionSide=position_side,
                clientAlgoId=client_algo_id,
                reduceOnly=reduce_only,
                limitPrice=limit_price,
                recvWindow=recv_window,
            ),
        )

    async def algo_cancel_algo_order_spot_algo(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Cancel Spot Algo Order (TRADE).

        DELETE /sapi/v1/algo/spot/order. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#cancel-algo-order-spot-algo

        """
        return await self._native_private(
            "algo_cancel_algo_order_spot_algo",
            self._params(algoId=algo_id, clientAlgoId=client_algo_id, recvWindow=recv_window),
        )

    async def query_algo_current_algo_open_orders_spot_algo(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Query Current Spot Algo Open Orders (USER_DATA).

        GET /sapi/v1/algo/spot/openOrders. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#query-current-algo-open-orders-spot-algo

        """
        return await self._native_private(
            "query_algo_current_algo_open_orders_spot_algo", self._params(recvWindow=recv_window)
        )

    async def query_algo_historical_algo_orders_spot_algo(
        self,
        *,
        symbol: str | None = None,
        side: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Historical Spot Algo Orders (USER_DATA).

        GET /sapi/v1/algo/spot/historicalOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#query-historical-algo-orders-spot-algo

        """
        return await self._native_private(
            "query_algo_historical_algo_orders_spot_algo",
            self._params(
                symbol=symbol,
                side=side,
                startTime=start_time,
                endTime=end_time,
                page=page,
                pageSize=page_size,
                recvWindow=recv_window,
            ),
        )

    async def query_algo_sub_orders_spot_algo(
        self,
        *,
        algo_id: int,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Spot Sub Orders (USER_DATA).

        GET /sapi/v1/algo/spot/subOrders. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#query-sub-orders-spot-algo

        """
        return await self._native_private(
            "query_algo_sub_orders_spot_algo",
            self._params(algoId=algo_id, page=page, pageSize=page_size, recvWindow=recv_window),
        )

    async def algo_time_weighted_average_price_spot_algo(
        self,
        *,
        symbol: str,
        side: str,
        quantity: str,
        duration: int,
        client_algo_id: str | None = None,
        limit_price: str | None = None,
    ) -> Any:
        """

        Time-Weighted Spot Average Price(Twap) New Order (TRADE).

        POST /sapi/v1/algo/spot/newOrderTwap. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#time-weighted-average-price-spot-algo

        """
        return await self._native_private(
            "algo_time_weighted_average_price_spot_algo",
            self._params(
                symbol=symbol,
                side=side,
                quantity=quantity,
                duration=duration,
                clientAlgoId=client_algo_id,
                limitPrice=limit_price,
            ),
        )

    async def pm_pro_bnb_transfer(
        self, *, amount: str, transfer_side: str, recv_window: int | None = None
    ) -> Any:
        """

        BNB transfer (USER_DATA).

        POST /sapi/v1/portfolio/bnb-transfer. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#bnb-transfer

        """
        return await self._native_private(
            "pm_pro_bnb_transfer",
            self._params(amount=amount, transferSide=transfer_side, recvWindow=recv_window),
        )

    async def change_pm_pro_auto_repay_futures_status(
        self, *, auto_repay: str, recv_window: int | None = None
    ) -> Any:
        """

        Change Auto-repay-futures Status (TRADE).

        POST /sapi/v1/portfolio/repay-futures-switch. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#change-auto-repay-futures-status

        """
        return await self._native_private(
            "change_pm_pro_auto_repay_futures_status",
            self._params(autoRepay=auto_repay, recvWindow=recv_window),
        )

    async def delete_pm_pro_margin_call_level(self, *, recv_window: int | None = None) -> Any:
        """

        Delete Margin Call Level (USER_DATA).

        DELETE /sapi/v1/portfolio/margin-call-level. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#delete-margin-call-level

        """
        return await self._native_private(
            "delete_pm_pro_margin_call_level", self._params(recvWindow=recv_window)
        )

    async def pm_pro_fund_auto_collection(self, *, recv_window: int | None = None) -> Any:
        """

        Fund Auto-collection (USER_DATA).

        POST /sapi/v1/portfolio/auto-collection. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#fund-auto-collection

        """
        return await self._native_private(
            "pm_pro_fund_auto_collection", self._params(recvWindow=recv_window)
        )

    async def pm_pro_fund_collection_by_asset(
        self, *, asset: str, recv_window: int | None = None
    ) -> Any:
        """

        Fund Collection by Asset (USER_DATA).

        POST /sapi/v1/portfolio/asset-collection. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#fund-collection-by-asset

        """
        return await self._native_private(
            "pm_pro_fund_collection_by_asset", self._params(asset=asset, recvWindow=recv_window)
        )

    async def get_pm_pro_auto_repay_futures_status(self, *, recv_window: int | None = None) -> Any:
        """

        Get Auto-repay-futures Status (USER_DATA).

        GET /sapi/v1/portfolio/repay-futures-switch. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-auto-repay-futures-status

        """
        return await self._native_private(
            "get_pm_pro_auto_repay_futures_status", self._params(recvWindow=recv_window)
        )

    async def get_pm_pro_delta_mode_status(self, *, recv_window: int | None = None) -> Any:
        """

        Get Delta Mode Status (USER_DATA).

        GET /sapi/v1/portfolio/delta-mode. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-delta-mode-status

        """
        return await self._native_private(
            "get_pm_pro_delta_mode_status", self._params(recvWindow=recv_window)
        )

    async def get_pm_pro_margin_call_level(self, *, recv_window: int | None = None) -> Any:
        """

        Get Margin Call Level (USER_DATA).

        GET /sapi/v1/portfolio/margin-call-level. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-margin-call-level

        """
        return await self._native_private(
            "get_pm_pro_margin_call_level", self._params(recvWindow=recv_window)
        )

    async def get_pm_pro_portfolio_margin_pro_account_balance(
        self, *, asset: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Get Portfolio Margin Pro Account Balance (USER_DATA).

        GET /sapi/v1/portfolio/balance. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-account-balance

        """
        return await self._native_private(
            "get_pm_pro_portfolio_margin_pro_account_balance",
            self._params(asset=asset, recvWindow=recv_window),
        )

    async def get_pm_pro_portfolio_margin_pro_account_info(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Get Portfolio Margin Pro Account Info (USER_DATA).

        GET /sapi/v1/portfolio/account. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-account-info

        """
        return await self._native_private(
            "get_pm_pro_portfolio_margin_pro_account_info", self._params(recvWindow=recv_window)
        )

    async def get_pm_pro_portfolio_margin_pro_span_account_info(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Get Portfolio Margin Pro SPAN Account Info (USER_DATA).

        GET /sapi/v2/portfolio/account. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-span-account-info

        """
        return await self._native_private(
            "get_pm_pro_portfolio_margin_pro_span_account_info",
            self._params(recvWindow=recv_window),
        )

    async def pm_pro_portfolio_margin_pro_bankruptcy_loan_repay(
        self, *, var_from: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Portfolio Margin Pro Bankruptcy Loan Repay (TRADE).

        POST /sapi/v1/portfolio/repay. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#portfolio-margin-pro-bankruptcy-loan-repay

        """
        return await self._native_private(
            "pm_pro_portfolio_margin_pro_bankruptcy_loan_repay",
            self._params(**{"from": var_from}, recvWindow=recv_window),
        )

    async def query_pm_pro_portfolio_margin_pro_bankruptcy_loan_amount(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Query Portfolio Margin Pro Bankruptcy Loan Amount (USER_DATA).

        GET /sapi/v1/portfolio/pmLoan. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-bankruptcy-loan-amount

        """
        return await self._native_private(
            "query_pm_pro_portfolio_margin_pro_bankruptcy_loan_amount",
            self._params(recvWindow=recv_window),
        )

    async def query_pm_pro_portfolio_margin_pro_bankruptcy_loan_repay_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        size: int | None = None,
        current: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Portfolio Margin Pro Bankruptcy Loan Repay History (USER_DATA).

        GET /sapi/v1/portfolio/pmloan-history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-bankruptcy-loan-repay-history

        """
        return await self._native_private(
            "query_pm_pro_portfolio_margin_pro_bankruptcy_loan_repay_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                size=size,
                current=current,
                recvWindow=recv_window,
            ),
        )

    async def query_pm_pro_portfolio_margin_pro_negative_balance_interest_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:
        """

        Query Portfolio Margin Pro Negative Balance Interest History (USER_DATA).

        GET /sapi/v1/portfolio/interest-history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-negative-balance-interest-history

        """
        return await self._native_private(
            "query_pm_pro_portfolio_margin_pro_negative_balance_interest_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                size=size,
                recvWindow=recv_window,
            ),
        )

    async def repay_pm_pro_futures_negative_balance(
        self, *, var_from: str | None = None, recv_window: int | None = None
    ) -> Any:
        """

        Repay futures Negative Balance (USER_DATA).

        POST /sapi/v1/portfolio/repay-futures-negative-balance. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#repay-futures-negative-balance

        """
        return await self._native_private(
            "repay_pm_pro_futures_negative_balance",
            self._params(**{"from": var_from}, recvWindow=recv_window),
        )

    async def set_pm_pro_margin_call_level(
        self, *, margin_call_level: str, recv_window: int | None = None
    ) -> Any:
        """

        Set Margin Call Level (USER_DATA).

        POST /sapi/v1/portfolio/margin-call-level. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#set-margin-call-level

        """
        return await self._native_private(
            "set_pm_pro_margin_call_level",
            self._params(marginCallLevel=margin_call_level, recvWindow=recv_window),
        )

    async def pm_pro_switch_delta_mode(
        self, *, delta_enabled: str, recv_window: int | None = None
    ) -> Any:
        """

        Switch Delta Mode (TRADE).

        POST /sapi/v1/portfolio/delta-mode. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#switch-delta-mode

        """
        return await self._native_private(
            "pm_pro_switch_delta_mode",
            self._params(deltaEnabled=delta_enabled, recvWindow=recv_window),
        )

    async def get_pm_pro_portfolio_margin_asset_leverage(self) -> Any:
        """

        Get Portfolio Margin Asset Leverage (USER_DATA).

        GET /sapi/v1/portfolio/margin-asset-leverage. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#get-portfolio-margin-asset-leverage

        """
        return await self._native_private(
            "get_pm_pro_portfolio_margin_asset_leverage", self._params()
        )

    async def pm_pro_portfolio_margin_pro_tiered_collateral_rate(
        self, *, recv_window: int | None = None
    ) -> Any:
        """

        Portfolio Margin Pro Tiered Collateral Rate (USER_DATA).

        GET /sapi/v2/portfolio/collateralRate. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#portfolio-margin-pro-tiered-collateral-rate

        """
        return await self._native_private(
            "pm_pro_portfolio_margin_pro_tiered_collateral_rate",
            self._params(recvWindow=recv_window),
        )
