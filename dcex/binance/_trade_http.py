# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
from json import dumps
from typing import Any

from dcex._schema_codec import encode_json, normalize_params

from .._native_http import request_native_json
from ..enums import OrderSide
from ..utils.errors import FailedRequestError
from ..utils.helpers import generate_timestamp
from ._batch_http import TradeHTTPBatchHTTP
from ._http_manager import HTTPManager
from ._transfers_http import TradeHTTPTransfersHTTP
from ._withdrawals_http import TradeHTTPWithdrawalsHTTP


class TradeHTTP(TradeHTTPBatchHTTP, TradeHTTPTransfersHTTP, TradeHTTPWithdrawalsHTTP, HTTPManager):
    """HTTP client for Binance trading API endpoints."""

    def place_coin_futures_algo_order(self, fields: dict[str, Any]) -> Any:
        """
        Place a COIN-M algo order using explicit exchange field names.

        Official specification incomplete; not verified live. The migration note
        names /dapi/v1/algoOrder but provides no standalone parameter contract.
        fields is forwarded without inferring USD-M field names. Authentication
        fields are added by the client and must not be supplied here.
        """
        return self._native_private(
            "place_coin_futures_algo_order", self._params(fields=encode_json(fields))
        )

    def cancel_coin_futures_algo_order(self, fields: dict[str, Any]) -> Any:
        """
        Cancel a COIN-M algo order using explicit exchange field names.

        Official specification incomplete; not verified live. The migration note
        names /dapi/v1/algoOrder but provides no standalone parameter contract.
        fields is forwarded without inferring USD-M field names. Authentication
        fields are added by the client and must not be supplied here.
        """
        return self._native_private(
            "cancel_coin_futures_algo_order", self._params(fields=encode_json(fields))
        )

    def get_coin_futures_algo_order(self, fields: dict[str, Any]) -> Any:
        """
        Get a COIN-M algo order using explicit exchange field names.

        Official specification incomplete; not verified live. The migration note
        names /dapi/v1/algoOrder but provides no standalone parameter contract.
        fields is forwarded without inferring USD-M field names. Authentication
        fields are added by the client and must not be supplied here.
        """
        return self._native_private(
            "get_coin_futures_algo_order", self._params(fields=encode_json(fields))
        )

    def get_dual_investment_product_list(
        self,
        *,
        option_type: str,
        exercised_coin: str,
        invest_coin: str,
        page_size: int | None = None,
        page_index: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/dci/product/list.

        Sent signed with the API key; Binance rejects it unauthenticated (-2014).
        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/market-data#get-dual-investment-product-list
        """
        return self._native_private(
            "get_dual_investment_product_list",
            self._params(
                optionType=option_type,
                exercisedCoin=exercised_coin,
                investCoin=invest_coin,
                pageSize=page_size,
                pageIndex=page_index,
                recvWindow=recv_window,
            ),
        )

    def place_equity_order(
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
        return self._native_private(
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

    def cancel_equity_order(self, order_id: str) -> dict:
        """Cancel one stock order."""
        return self._native_private("cancel_equity_order", self._params(orderId=order_id))

    def cancel_all_equity_orders(self) -> dict:
        """Cancel all open stock orders."""
        return self._native_private("cancel_all_equity_orders", [])

    def get_equity_order_detail(self, order_id: str) -> dict:
        """Get one stock order."""
        return self._native_private("get_equity_order_detail", self._params(orderId=order_id))

    def get_open_equity_orders(self) -> dict:
        """Get open stock orders."""
        return self._native_private("get_open_equity_orders", [])

    def get_equity_order_history(self, start_time: int, end_time: int) -> dict:
        """Get stock order history for a time range."""
        return self._native_private(
            "get_equity_order_history",
            self._params(startTime=start_time, endTime=end_time),
        )

    def get_equity_trade_history(
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
        return self._native_private(
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

    def mint_equity_token(
        self, underlying_asset: str, amount: str, client_order_id: str | None = None
    ) -> dict:
        """Convert an underlying asset into its stock token."""
        return self._native_private(
            "mint_equity_token",
            self._params(
                underlyingAsset=underlying_asset,
                underlyingAssetAmount=amount,
                clientOrderId=client_order_id,
            ),
        )

    def redeem_equity_token(
        self, tokenized_asset: str, amount: str, client_order_id: str | None = None
    ) -> dict:
        """Redeem a stock token into its underlying asset."""
        return self._native_private(
            "redeem_equity_token",
            self._params(
                tokenizedAsset=tokenized_asset,
                tokenizedAssetAmount=amount,
                clientOrderId=client_order_id,
            ),
        )

    def get_equity_convert_status(self, issuer_request_id: str, convert_type: str) -> dict:
        """Get one stock-token conversion status."""
        return self._native_private(
            "get_equity_convert_status",
            self._params(issuerRequestId=issuer_request_id, convertType=convert_type),
        )

    def get_equity_convert_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        last_id: int | None = None,
        size: int | None = None,
    ) -> dict:
        """Get stock-token conversion history."""
        return self._native_private(
            "get_equity_convert_history",
            self._params(startTime=start_time, endTime=end_time, lastId=last_id, size=size),
        )

    def sign_equity_disclaimer(self) -> dict:
        """Accept the stock trading disclaimer."""
        return self._native_private("sign_equity_disclaimer", [])

    def create_or_renew_equity_listen_key(self) -> dict:
        """Create or renew the stock user-data listen key."""
        return self._native_private("create_or_renew_equity_listen_key", [])

    def place_options_order(
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
        return self._native_private(
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

    def get_options_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        clientOrderId: str | None = None,
    ) -> dict[str, Any]:
        """Get one Binance Options order."""
        return self._native_private(
            "get_options_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOrderId=clientOrderId,
            ),
        )

    def cancel_options_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        clientOrderId: str | None = None,
    ) -> dict[str, Any]:
        """Cancel one Binance Options order."""
        return self._native_private(
            "cancel_options_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOrderId=clientOrderId,
            ),
        )

    def cancel_all_options_orders(self, product_symbol: str) -> dict[str, Any]:
        """Cancel all open option orders for one symbol."""
        return self._native_private(
            "cancel_all_options_orders", self._params(product_symbol=product_symbol)
        )

    def cancel_all_options_orders_by_underlying(self, underlying: str) -> dict[str, Any]:
        """Cancel all open option orders for one underlying."""
        return self._native_private(
            "cancel_all_options_orders_by_underlying",
            self._params(underlying=underlying),
        )

    def get_options_positions(self, product_symbol: str | None = None) -> list[dict[str, Any]]:
        """Get current Binance Options positions."""
        return self._native_private(
            "get_options_positions", self._params(product_symbol=product_symbol)
        )

    def get_open_options_orders(
        self,
        product_symbol: str | None = None,
        *,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get current open Binance Options orders."""
        return self._native_private(
            "get_open_options_orders",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_options_order_history(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get completed Binance Options orders."""
        return self._native_private(
            "get_options_order_history",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_options_account_trades(
        self,
        product_symbol: str,
        *,
        fromId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get Binance Options account trades."""
        return self._native_private(
            "get_options_account_trades",
            self._params(
                product_symbol=product_symbol,
                fromId=fromId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_options_commission(self) -> dict[str, Any]:
        """Get Binance Options commission rates."""
        return self._native_private("get_options_commission", [])

    def get_options_exercise_records(
        self,
        product_symbol: str | None = None,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get the account's Binance Options exercise records."""
        return self._native_private(
            "get_options_exercise_records",
            self._params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for private trade methods.")
        try:
            response, data = request_native_json(
                self._native_client,
                "private_request",
                method_name,
                params,
            )
        except RuntimeError as exc:
            raise FailedRequestError(
                request=f"BINANCE {method_name} | Params: {params}",
                message=str(exc),
                status_code=getattr(exc, "status_code", None),
                response_data=getattr(exc, "response_data", None),
                resp_headers=dict(getattr(exc, "resp_headers", [])),
                time=str(generate_timestamp(iso_format=True)),
            ) from exc
        self._store_response_headers(response)
        return data

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        kwargs = normalize_params(kwargs)
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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

    def create_oco_order(self, product_symbol: str, **params: object) -> dict:
        """Create a Binance spot one-cancels-the-other order list."""
        return self._native_private(
            "create_oco_order", self._params(product_symbol=product_symbol, **params)
        )

    def create_oto_order(self, product_symbol: str, **params: object) -> dict:
        """Create a Binance spot one-triggers-the-other order list."""
        return self._native_private(
            "create_oto_order", self._params(product_symbol=product_symbol, **params)
        )

    def create_otoco_order(self, product_symbol: str, **params: object) -> dict:
        """Create a Binance spot one-triggers-an-OCO order list."""
        return self._native_private(
            "create_otoco_order", self._params(product_symbol=product_symbol, **params)
        )

    def get_prevented_matches(self, product_symbol: str, **params: object) -> dict:
        """Retrieve spot self-trade-prevention match records."""
        return self._native_private(
            "get_prevented_matches", self._params(product_symbol=product_symbol, **params)
        )

    def get_allocations(self, product_symbol: str, **params: object) -> dict:
        """Retrieve spot allocation records."""
        return self._native_private(
            "get_allocations", self._params(product_symbol=product_symbol, **params)
        )

    def get_order_rate_limit(self, **params: object) -> dict:
        """Retrieve the account's current spot order-count limits."""
        return self._native_private("get_order_rate_limit", self._params(**params))

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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
        """
        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).
        """
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
        """
        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).
        """
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
        """
        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).
        """
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
        """
        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).
        """
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
        """
        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).
        """
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
        newClientOrderId: str | None = None,
        cancelRestrictions: str | None = None,
    ) -> dict:
        """
        Cancel an order.

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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
                newClientOrderId=newClientOrderId,
                cancelRestrictions=cancelRestrictions,
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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderId: Spot and USD-M return that single open order. For Options, Binance treats
                orderId as a starting point and returns that order and the ones after it.
            origClientOrderId: Spot and USD-M only; Options rejects it.

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
        market_type: str | None = None,
    ) -> dict:
        """
        Get all open orders for a product or for the selected market.

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT) or
        market_type.

        Args:
            product_symbol: Optional product symbol. If omitted, Binance returns all open orders.
            market_type: Market type ("spot" or "swap"). Narrows product_symbol resolution;
                defaults to "spot" when product_symbol is omitted.

        Returns:
            dict: Open order list.
        """
        return self._native_private(
            "get_all_open_orders",
            self._params(
                product_symbol=product_symbol,
                market_type=None if market_type is None else str(market_type),
            ),
        )

    def cancel_all_open_orders(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Cancel all open orders for a trading pair.

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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

        With a loaded product table, a native symbol shared by Spot and USD-M (e.g. BTCUSDT) is
        ambiguous; pass the unified product symbol (e.g. BTC-USDT-SWAP / BTC-USDT-SPOT).

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
        product_symbol: str | None = None,
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

    def place_margin_order(
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
        return self._native_private(
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

    def cancel_margin_order(
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
        return self._native_private(
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

    def get_margin_order(
        self,
        product_symbol: str,
        *,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        """Query one Binance Margin order."""
        return self._native_private(
            "get_margin_order",
            self._params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    def get_open_margin_orders(
        self,
        *,
        product_symbol: str | None = None,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query open cross- or isolated-margin orders."""
        return self._native_private(
            "get_open_margin_orders",
            self._params(
                product_symbol=product_symbol,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    def cancel_all_open_margin_orders(
        self,
        product_symbol: str,
        *,
        isIsolated: bool = False,
        recvWindow: int | None = None,
    ) -> list[dict[str, Any]]:
        """Cancel every open Binance Margin order on one symbol."""
        return self._native_private(
            "cancel_all_open_margin_orders",
            self._params(
                product_symbol=product_symbol,
                isIsolated=isIsolated,
                recvWindow=recvWindow,
            ),
        )

    def get_all_margin_orders(
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
        return self._native_private(
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

    def get_margin_account_trades(
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
        return self._native_private(
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

    def get_pm_um_open_orders(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict:
        """Return open Portfolio Margin USD-M orders."""
        return self._native_private(
            "get_pm_um_open_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_pm_um_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Look up one Portfolio Margin USD-M order."""
        return self._native_private(
            "get_pm_um_order",
            self._params(
                product_symbol=product_symbol,
                orderId=order_id,
                origClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_pm_um_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel one Portfolio Margin USD-M order."""
        return self._native_private(
            "cancel_pm_um_order",
            self._params(
                product_symbol=product_symbol,
                orderId=order_id,
                origClientOrderId=client_order_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_all_pm_um_orders(
        self, product_symbol: str, *, recv_window: int | None = None
    ) -> dict:
        """Cancel all active Portfolio Margin USD-M orders for a symbol."""
        return self._native_private(
            "cancel_all_pm_um_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def place_pm_um_order(
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
        return self._native_private(
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

    def place_pm_um_algo_order(
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
        return self._native_private(
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

    def get_pm_um_algo_order(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Look up a Portfolio Margin USD-M conditional order."""
        return self._native_private(
            "get_pm_um_algo_order",
            self._params(
                algoId=algo_id,
                clientAlgoId=client_algo_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_pm_um_algo_order(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin USD-M conditional order."""
        return self._native_private(
            "cancel_pm_um_algo_order",
            self._params(
                algoId=algo_id,
                clientAlgoId=client_algo_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_all_pm_um_algo_orders(
        self,
        product_symbol: str,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel all active conditional orders for a Portfolio Margin USD-M symbol."""
        return self._native_private(
            "cancel_all_pm_um_algo_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_pm_um_open_algo_orders(
        self,
        product_symbol: str | None = None,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Get open Portfolio Margin USD-M conditional orders."""
        return self._native_private(
            "get_pm_um_open_algo_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_pm_um_algo_order_history(
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
        return self._native_private(
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

    def get_pm_um_all_orders(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin um all orders."""
        return self._native_private(
            "get_pm_um_all_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_um_user_trades(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin um user trades."""
        return self._native_private(
            "get_pm_um_user_trades", self._params(product_symbol=product_symbol)
        )

    def get_pm_cm_open_orders(self, product_symbol: str | None = None) -> dict:
        """Query Binance Portfolio Margin cm open orders."""
        return self._native_private(
            "get_pm_cm_open_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_cm_all_orders(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin cm all orders."""
        return self._native_private(
            "get_pm_cm_all_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_cm_user_trades(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin cm user trades."""
        return self._native_private(
            "get_pm_cm_user_trades", self._params(product_symbol=product_symbol)
        )

    def get_pm_margin_open_orders(self, product_symbol: str | None = None) -> dict:
        """Query Binance Portfolio Margin margin open orders."""
        return self._native_private(
            "get_pm_margin_open_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_margin_all_orders(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin margin all orders."""
        return self._native_private(
            "get_pm_margin_all_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_margin_trades(self, product_symbol: str) -> dict:
        """Query Binance Portfolio Margin margin trades."""
        return self._native_private(
            "get_pm_margin_trades", self._params(product_symbol=product_symbol)
        )

    def place_pm_cm_order(
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
        return self._native_private(
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

    def get_pm_cm_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Get a Portfolio Margin CM order."""
        return self._native_private(
            "get_pm_cm_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    def cancel_pm_cm_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin CM order."""
        return self._native_private(
            "cancel_pm_cm_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    def cancel_all_pm_cm_orders(self, product_symbol: str) -> dict:
        """Cancel all active Portfolio Margin CM orders for a symbol."""
        return self._native_private(
            "cancel_all_pm_cm_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_margin_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Get a Portfolio Margin MARGIN order."""
        return self._native_private(
            "get_pm_margin_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    def cancel_pm_margin_order(
        self,
        product_symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin MARGIN order."""
        return self._native_private(
            "cancel_pm_margin_order",
            self._params(
                product_symbol=product_symbol, orderId=order_id, origClientOrderId=client_order_id
            ),
        )

    def cancel_all_pm_margin_orders(self, product_symbol: str) -> dict:
        """Cancel all active Portfolio Margin MARGIN orders for a symbol."""
        return self._native_private(
            "cancel_all_pm_margin_orders", self._params(product_symbol=product_symbol)
        )

    def place_pm_margin_order(
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
        return self._native_private(
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

    def modify_pm_um_order(
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
        return self._native_private(
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

    def modify_pm_cm_order(
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
        return self._native_private(
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

    def place_pm_cm_conditional_order(
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
        return self._native_private(
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

    def cancel_pm_cm_conditional_order(
        self,
        product_symbol: str,
        *,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel a Portfolio Margin COIN-M conditional order."""
        return self._native_private(
            "cancel_pm_cm_conditional_order",
            self._params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                newClientStrategyId=client_strategy_id,
                recvWindow=recv_window,
            ),
        )

    def cancel_all_pm_cm_conditional_orders(
        self,
        product_symbol: str,
        *,
        recv_window: int | None = None,
    ) -> dict:
        """Cancel all COIN-M conditional orders for a Portfolio Margin symbol."""
        return self._native_private(
            "cancel_all_pm_cm_conditional_orders",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_pm_cm_conditional_order(
        self,
        product_symbol: str,
        *,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
    ) -> dict:
        """Look up an open Portfolio Margin COIN-M conditional order."""
        return self._native_private(
            "get_pm_cm_conditional_order",
            self._params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                newClientStrategyId=client_strategy_id,
            ),
        )

    def get_pm_cm_conditional_order_history(
        self,
        product_symbol: str,
        *,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
    ) -> dict:
        """Look up Portfolio Margin COIN-M conditional order history."""
        return self._native_private(
            "get_pm_cm_conditional_order_history",
            self._params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                newClientStrategyId=client_strategy_id,
            ),
        )

    def get_pm_cm_open_conditional_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """List active Portfolio Margin COIN-M conditional orders."""
        return self._native_private(
            "get_pm_cm_open_conditional_orders", self._params(product_symbol=product_symbol)
        )

    def get_pm_cm_all_conditional_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """List Portfolio Margin COIN-M conditional orders."""
        return self._native_private(
            "get_pm_cm_all_conditional_orders", self._params(product_symbol=product_symbol)
        )

    def place_pm_margin_oco(
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
        return self._native_private(
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

    def get_pm_margin_oco(self, order_list_id: int) -> dict:
        """Get a Portfolio Margin OCO order list."""
        return self._native_private("get_pm_margin_oco", self._params(orderListId=order_list_id))

    def cancel_pm_margin_oco(
        self,
        product_symbol: str,
        order_list_id: int,
    ) -> dict:
        """Cancel a Portfolio Margin OCO order list."""
        return self._native_private(
            "cancel_pm_margin_oco",
            self._params(product_symbol=product_symbol, orderListId=order_list_id),
        )

    def get_pm_margin_open_oco(self) -> dict:
        """List open Portfolio Margin OCO order lists."""
        return self._native_private("get_pm_margin_open_oco", self._params())

    def get_pm_margin_all_oco(self) -> dict:
        """List Portfolio Margin OCO order history."""
        return self._native_private("get_pm_margin_all_oco", self._params())

    def get_pm_um_order_amendments(
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
        return self._native_private(
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

    def get_pm_cm_order_amendments(
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
        return self._native_private(
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

    def get_spot_order_list(
        self,
        *,
        order_list_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /api/v3/orderList`` with signed authentication."""
        return self._native_private(
            "get_spot_order_list",
            self._params(
                orderListId=order_list_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def get_spot_all_order_lists(
        self,
        *,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /api/v3/allOrderList`` with signed authentication."""
        return self._native_private(
            "get_spot_all_order_lists",
            self._params(
                fromId=from_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_spot_open_order_lists(
        self, *, recv_window: str | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /api/v3/openOrderList`` with signed authentication."""
        return self._native_private(
            "get_spot_open_order_lists", self._params(recvWindow=recv_window)
        )

    def cancel_spot_order_list(
        self,
        product_symbol: str,
        *,
        order_list_id: int | None = None,
        list_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``DELETE /api/v3/orderList`` with signed authentication."""
        return self._native_private(
            "cancel_spot_order_list",
            self._params(
                product_symbol=product_symbol,
                orderListId=order_list_id,
                listClientOrderId=list_client_order_id,
                newClientOrderId=new_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def amend_spot_order_keep_priority(
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
        return self._native_private(
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

    def get_futures_position_mode(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /fapi/v1/positionSide/dual`` with signed authentication."""
        return self._native_private(
            "get_futures_position_mode", self._params(recvWindow=recv_window)
        )

    def set_futures_position_mode(
        self, dual_side_position: bool, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /fapi/v1/positionSide/dual`` with signed authentication."""
        return self._native_private(
            "set_futures_position_mode",
            self._params(dualSidePosition=dual_side_position, recvWindow=recv_window),
        )

    def set_futures_margin_type(
        self, product_symbol: str, margin_type: str, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /fapi/v1/marginType`` with signed authentication."""
        return self._native_private(
            "set_futures_margin_type",
            self._params(
                product_symbol=product_symbol, marginType=margin_type, recvWindow=recv_window
            ),
        )

    def set_futures_cancel_countdown(
        self, product_symbol: str, countdown_time: int, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /fapi/v1/countdownCancelAll`` with signed authentication."""
        return self._native_private(
            "set_futures_cancel_countdown",
            self._params(
                product_symbol=product_symbol, countdownTime=countdown_time, recvWindow=recv_window
            ),
        )

    def get_futures_leverage_brackets(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /fapi/v1/leverageBracket`` with signed authentication."""
        return self._native_private(
            "get_futures_leverage_brackets",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def amend_futures_order(
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
        return self._native_private(
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

    def get_coin_futures_position_mode(
        self, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v1/positionSide/dual`` with signed authentication."""
        return self._native_private(
            "get_coin_futures_position_mode", self._params(recvWindow=recv_window)
        )

    def set_coin_futures_position_mode(
        self, dual_side_position: bool, *, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/positionSide/dual`` with signed authentication."""
        return self._native_private(
            "set_coin_futures_position_mode",
            self._params(dualSidePosition=dual_side_position, recvWindow=recv_window),
        )

    def set_coin_futures_margin_type(
        self,
        product_symbol: str,
        margin_type: str | None = None,
        *,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/marginType`` with signed authentication."""
        return self._native_private(
            "set_coin_futures_margin_type",
            self._params(
                product_symbol=product_symbol,
                marginType=margin_type,
                recvWindow=recv_window,
            ),
        )

    def set_coin_futures_cancel_countdown(
        self,
        product_symbol: str,
        countdown_time: int | None = None,
        *,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/countdownCancelAll`` with signed authentication."""
        return self._native_private(
            "set_coin_futures_cancel_countdown",
            self._params(
                product_symbol=product_symbol,
                countdownTime=countdown_time,
                recvWindow=recv_window,
            ),
        )

    def get_coin_futures_leverage_brackets(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v2/leverageBracket`` with signed authentication."""
        return self._native_private(
            "get_coin_futures_leverage_brackets",
            self._params(symbol=symbol, recvWindow=recv_window),
        )

    def amend_coin_futures_order(
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
        return self._native_private(
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

    def set_coin_futures_leverage(
        self,
        product_symbol: str,
        leverage: int | None = None,
        *,
        recv_window: int | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``POST /dapi/v1/leverage`` with signed authentication."""
        return self._native_private(
            "set_coin_futures_leverage",
            self._params(
                product_symbol=product_symbol,
                leverage=leverage,
                recvWindow=recv_window,
            ),
        )

    def get_coin_futures_pair_leverage_brackets(
        self, *, pair: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Call ``GET /dapi/v1/leverageBracket`` with signed authentication."""
        return self._native_private(
            "get_coin_futures_pair_leverage_brackets",
            self._params(pair=pair, recvWindow=recv_window),
        )

    def get_coin_futures_all_orders(
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
        return self._native_private(
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

    def get_coin_futures_account_trades(
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
        return self._native_private(
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

    def create_futures_listen_key(self) -> dict[str, Any]:
        """Create a USD-M Futures user-data stream listen key."""
        return self._native_private("create_futures_listen_key", [])

    def keep_alive_futures_listen_key(self) -> dict[str, Any]:
        """Keep the USD-M Futures user-data stream alive."""
        return self._native_private("keep_alive_futures_listen_key", [])

    def close_futures_listen_key(self) -> dict[str, Any]:
        """Close the USD-M Futures user-data stream."""
        return self._native_private("close_futures_listen_key", [])

    def create_coin_futures_listen_key(self) -> dict[str, Any]:
        """POST /dapi/v1/listenKey; uses the account API key without a signature."""
        return self._native_private("create_coin_futures_listen_key", [])

    def keep_alive_coin_futures_listen_key(self) -> dict[str, Any]:
        """PUT /dapi/v1/listenKey; uses the account API key without a signature."""
        return self._native_private("keep_alive_coin_futures_listen_key", [])

    def close_coin_futures_listen_key(self) -> dict[str, Any]:
        """DELETE /dapi/v1/listenKey; uses the account API key without a signature."""
        return self._native_private("close_coin_futures_listen_key", [])

    def create_pm_listen_key(self) -> dict[str, Any]:
        """POST /papi/v1/listenKey; uses the account API key without a signature."""
        return self._native_private("create_pm_listen_key", [])

    def keep_alive_pm_listen_key(self) -> dict[str, Any]:
        """PUT /papi/v1/listenKey; uses the account API key without a signature."""
        return self._native_private("keep_alive_pm_listen_key", [])

    def close_pm_listen_key(self) -> dict[str, Any]:
        """DELETE /papi/v1/listenKey; uses the account API key without a signature."""
        return self._native_private("close_pm_listen_key", [])

    def cancel_replace_spot_order(
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
        return self._native_private(
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

    def get_coin_futures_income_history(
        self,
        *,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /dapi/v1/income.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-income-history

        """
        return self._native_private(
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

    def get_coin_futures_commission_rate(
        self, *, symbol: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /dapi/v1/commissionRate.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#user-commission-rate

        """
        return self._native_private(
            "get_coin_futures_commission_rate", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def adjust_coin_futures_position_margin(
        self,
        *,
        symbol: str,
        amount: str,
        kind_type: int,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /dapi/v1/positionMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#modify-isolated-position-margin

        """
        return self._native_private(
            "adjust_coin_futures_position_margin",
            self._params(
                symbol=symbol,
                amount=amount,
                type=kind_type,
                positionSide=position_side,
                recvWindow=recv_window,
            ),
        )

    def get_coin_futures_adl_quantiles(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /dapi/v1/adlQuantile.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#position-adl-quantile-estimation

        """
        return self._native_private(
            "get_coin_futures_adl_quantiles", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def get_coin_futures_force_orders(
        self,
        *,
        symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /dapi/v1/forceOrders.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#users-force-orders

        """
        return self._native_private(
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

    def get_pm_coin_income_history(
        self,
        *,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/cm/income.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-cm-income-history

        """
        return self._native_private(
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

    def get_pm_margin_interest_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        archived: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/margin/marginInterestHistory.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-margin-borrow-loan-interest-history

        """
        return self._native_private(
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

    def get_pm_futures_income_history(
        self,
        *,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/um/income.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-income-history

        """
        return self._native_private(
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

    def get_pm_coin_commission_rate(self, *, symbol: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/cm/commissionRate.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-user-commission-rate-for-cm

        """
        return self._native_private(
            "get_pm_coin_commission_rate", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def get_pm_futures_commission_rate(
        self, *, product_symbol: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/um/commissionRate.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-user-commission-rate-for-um

        """
        return self._native_private(
            "get_pm_futures_commission_rate",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_pm_margin_loan_records(
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
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/margin/marginLoan.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-loan-record

        """
        return self._native_private(
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

    def get_pm_margin_repayment_records(
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
    ) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/margin/repayLoan.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-repay-record

        """
        return self._native_private(
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

    def get_pm_order_rate_limits(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /papi/v1/rateLimit/order.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-user-rate-limit

        """
        return self._native_private(
            "get_pm_order_rate_limits", self._params(recvWindow=recv_window)
        )

    def get_futures_account_config(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/accountConfig.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-account-configuration

        """
        return self._native_private(
            "get_futures_account_config", self._params(recvWindow=recv_window)
        )

    def get_futures_trading_status(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/apiTradingStatus.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-trading-quantitative-rules-indicators

        """
        return self._native_private(
            "get_futures_trading_status",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_futures_multi_assets_mode(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/multiAssetsMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-current-multi-assets-mode

        """
        return self._native_private(
            "get_futures_multi_assets_mode", self._params(recvWindow=recv_window)
        )

    def get_futures_order_rate_limits(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/rateLimit/order.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#query-user-rate-limit

        """
        return self._native_private(
            "get_futures_order_rate_limits", self._params(recvWindow=recv_window)
        )

    def get_futures_symbol_config(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/symbolConfig.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#symbol-configuration

        """
        return self._native_private(
            "get_futures_symbol_config",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def set_futures_multi_assets_mode(
        self, *, multi_assets_margin: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /fapi/v1/multiAssetsMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#change-multi-assets-mode

        """
        return self._native_private(
            "set_futures_multi_assets_mode",
            self._params(multiAssetsMargin=multi_assets_margin, recvWindow=recv_window),
        )

    def adjust_futures_position_margin(
        self,
        *,
        product_symbol: str,
        amount: str,
        kind_type: int,
        position_side: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /fapi/v1/positionMargin.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#modify-isolated-position-margin

        """
        return self._native_private(
            "adjust_futures_position_margin",
            self._params(
                product_symbol=product_symbol,
                amount=amount,
                type=kind_type,
                positionSide=position_side,
                recvWindow=recv_window,
            ),
        )

    def get_futures_adl_quantiles(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/adlQuantile.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#position-adl-quantile-estimation

        """
        return self._native_private(
            "get_futures_adl_quantiles",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_futures_force_orders(
        self,
        *,
        product_symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /fapi/v1/forceOrders.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#users-force-orders

        """
        return self._native_private(
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

    def get_margin_risk_coefficients(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/tradeCoeff.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#get-summary-of-margin-account

        """
        return self._native_private(
            "get_margin_risk_coefficients", self._params(recvWindow=recv_window)
        )

    def get_margin_capital_flow(
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
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/capital-flow.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-cross-isolated-margin-capital-flow

        """
        return self._native_private(
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

    def get_margin_liquidation_records(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        isolated_symbol: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/forceLiquidationRec.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-force-liquidation-record

        """
        return self._native_private(
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

    def cancel_margin_order_list(
        self,
        *,
        product_symbol: str,
        is_isolated: str | None = None,
        order_list_id: int | None = None,
        list_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        DELETE /sapi/v1/margin/orderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-cancel-oco

        """
        return self._native_private(
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

    def get_margin_order_rate_limits(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/rateLimit/order.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-current-margin-order-count-usage

        """
        return self._native_private(
            "get_margin_order_rate_limits",
            self._params(
                isIsolated=is_isolated, product_symbol=product_symbol, recvWindow=recv_window
            ),
        )

    def get_margin_all_order_lists(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/allOrderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-all-oco

        """
        return self._native_private(
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

    def get_margin_order_list(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        order_list_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/orderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-oco

        """
        return self._native_private(
            "get_margin_order_list",
            self._params(
                isIsolated=is_isolated,
                product_symbol=product_symbol,
                orderListId=order_list_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def get_margin_open_order_lists(
        self,
        *,
        is_isolated: str | None = None,
        product_symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/margin/openOrderList.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-margin-accounts-open-oco

        """
        return self._native_private(
            "get_margin_open_order_lists",
            self._params(
                isIsolated=is_isolated, product_symbol=product_symbol, recvWindow=recv_window
            ),
        )

    def close_margin_listen_key(self) -> Any:  # noqa: ANN401
        """
        DELETE /sapi/v1/margin/listen-key.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream#close-user-data-stream

        """
        return self._native_private("close_margin_listen_key", self._params())

    def keep_alive_margin_listen_key(self, *, listen_key: str) -> Any:  # noqa: ANN401
        """
        PUT /sapi/v1/margin/listen-key.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream#keepalive-user-data-stream

        """
        return self._native_private(
            "keep_alive_margin_listen_key", self._params(listenKey=listen_key)
        )

    def create_margin_listen_key(self) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/margin/listen-key.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream#start-user-data-stream

        """
        return self._native_private("create_margin_listen_key", self._params())

    def get_account_trading_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/account/apiTradingStatus.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-api-trading-status

        """
        return self._native_private(
            "get_account_trading_status", self._params(recvWindow=recv_window)
        )

    def get_account_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/account/status.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-status

        """
        return self._native_private("get_account_status", self._params(recvWindow=recv_window))

    def get_api_key_permissions(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/account/apiRestrictions.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#get-api-key-permission

        """
        return self._native_private("get_api_key_permissions", self._params(recvWindow=recv_window))

    def get_spot_trade_fees(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/asset/tradeFee.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#trade-fee

        """
        return self._native_private(
            "get_spot_trade_fees",
            self._params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_user_assets(
        self,
        *,
        asset: str | None = None,
        need_btc_valuation: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v3/asset/getUserAsset.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#user-asset

        """
        return self._native_private(
            "get_user_assets",
            self._params(asset=asset, needBtcValuation=need_btc_valuation, recvWindow=recv_window),
        )

    def get_coin_network_config(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/config/getall.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#all-coins-information

        """
        return self._native_private("get_coin_network_config", self._params(recvWindow=recv_window))

    def get_deposit_address(
        self,
        *,
        coin: str,
        network: str | None = None,
        amount: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/deposit/address.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#deposit-address

        """
        return self._native_private(
            "get_deposit_address",
            self._params(coin=coin, network=network, amount=amount, recvWindow=recv_window),
        )

    def get_deposit_history(
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
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/deposit/hisrec.

        Decimal amounts are strings; timestamps are milliseconds.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#deposit-history

        """
        return self._native_private(
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

    def place_margin_oco(
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
    ) -> Any:  # noqa: ANN401
        """
        Both legs share quantity; cancelling either leg cancels the entire list.

        POST /sapi/v1/margin/order/oco. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-oco

        """
        return self._native_private(
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

    def place_margin_oto(
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
    ) -> Any:  # noqa: ANN401
        """
        Pending orders activate only after the working order fully fills.

        POST /sapi/v1/margin/order/oto. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-oto

        """
        return self._native_private(
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

    def place_margin_otoco(
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
    ) -> Any:  # noqa: ANN401
        """
        Pending orders activate only after the working order fully fills.

        POST /sapi/v1/margin/order/otoco. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-new-otoco

        """
        return self._native_private(
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

    def place_spot_opo(
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
    ) -> Any:  # noqa: ANN401
        """
        Working BUY must fully fill before pending SELL orders use its received funds; no
        pending quantity is accepted.

        POST /api/v3/orderList/opo. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-opo

        """
        return self._native_private(
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

    def place_spot_opoco(
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
    ) -> Any:  # noqa: ANN401
        """
        Working BUY must fully fill before pending SELL orders use its received funds; no
        pending quantity is accepted.

        POST /api/v3/orderList/opoco. Decimal values are strings.
        Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-opoco

        """
        return self._native_private(
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

    def get_coin_futures_download_id_for_futures_order_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For Futures Order History (USER_DATA).

        GET /dapi/v1/order/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-download-id-for-futures-order-history

        """
        return self._native_private(
            "get_coin_futures_download_id_for_futures_order_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_coin_futures_download_id_for_futures_trade_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For Futures Trade History (USER_DATA).

        GET /dapi/v1/trade/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-download-id-for-futures-trade-history

        """
        return self._native_private(
            "get_coin_futures_download_id_for_futures_trade_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_coin_futures_download_id_for_futures_transaction_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For Futures Transaction History (USER_DATA).

        GET /dapi/v1/income/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-download-id-for-futures-transaction-history

        """
        return self._native_private(
            "get_coin_futures_download_id_for_futures_transaction_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_coin_futures_futures_order_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Futures Order History Download Link by Id (USER_DATA).

        GET /dapi/v1/order/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-order-history-download-link-by-id

        """
        return self._native_private(
            "get_coin_futures_futures_order_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_coin_futures_futures_trade_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Futures Trade Download Link by Id (USER_DATA).

        GET /dapi/v1/trade/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-trade-download-link-by-id

        """
        return self._native_private(
            "get_coin_futures_futures_trade_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_coin_futures_futures_transaction_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Futures Transaction History Download Link by Id (USER_DATA).

        GET /dapi/v1/income/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/account#get-futures-transaction-history-download-link-by-id

        """
        return self._native_private(
            "get_coin_futures_futures_transaction_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_coin_futures_order_modify_history(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Order Modify History (USER_DATA).

        GET /dapi/v1/orderAmendment. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#get-order-modify-history

        """
        return self._native_private(
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

    def get_coin_futures_position_margin_change_history(
        self,
        *,
        symbol: str,
        kind_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Position Margin Change History (TRADE).

        GET /dapi/v1/positionMargin/history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#get-position-margin-change-history

        """
        return self._native_private(
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

    def query_coin_futures_current_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Current Open Order (USER_DATA).

        GET /dapi/v1/openOrder. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#query-current-open-order

        """
        return self._native_private(
            "query_coin_futures_current_open_order",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def change_pm_auto_repay_futures_status(
        self, *, auto_repay: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Change Auto-repay-futures Status (TRADE).

        POST /papi/v1/repay-futures-switch. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#change-auto-repay-futures-status

        """
        return self._native_private(
            "change_pm_auto_repay_futures_status",
            self._params(autoRepay=auto_repay, recvWindow=recv_window),
        )

    def pm_fund_auto_collection(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Fund Auto-collection (TRADE).

        POST /papi/v1/auto-collection. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#fund-auto-collection

        """
        return self._native_private("pm_fund_auto_collection", self._params(recvWindow=recv_window))

    def pm_fund_collection_by_asset(self, *, asset: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Fund Collection by Asset (TRADE).

        POST /papi/v1/asset-collection. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#fund-collection-by-asset

        """
        return self._native_private(
            "pm_fund_collection_by_asset", self._params(asset=asset, recvWindow=recv_window)
        )

    def get_pm_auto_repay_futures_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Auto-repay-futures Status (USER_DATA).

        GET /papi/v1/repay-futures-switch. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-auto-repay-futures-status

        """
        return self._native_private(
            "get_pm_auto_repay_futures_status", self._params(recvWindow=recv_window)
        )

    def get_pm_download_id_for_um_futures_order_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For UM Futures Order History (USER_DATA).

        GET /papi/v1/um/order/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-download-id-for-um-futures-order-history

        """
        return self._native_private(
            "get_pm_download_id_for_um_futures_order_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_pm_download_id_for_um_futures_trade_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For UM Futures Trade History (USER_DATA).

        GET /papi/v1/um/trade/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-download-id-for-um-futures-trade-history

        """
        return self._native_private(
            "get_pm_download_id_for_um_futures_trade_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_pm_download_id_for_um_futures_transaction_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For UM Futures Transaction History (USER_DATA).

        GET /papi/v1/um/income/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-download-id-for-um-futures-transaction-history

        """
        return self._native_private(
            "get_pm_download_id_for_um_futures_transaction_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_pm_um_account_detail_v2(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get UM Account Detail V2 (USER_DATA).

        GET /papi/v2/um/account. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-account-detail-v2

        """
        return self._native_private(
            "get_pm_um_account_detail_v2", self._params(recvWindow=recv_window)
        )

    def get_pm_um_futures_order_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get UM Futures Order Download Link by Id (USER_DATA).

        GET /papi/v1/um/order/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-order-download-link-by-id

        """
        return self._native_private(
            "get_pm_um_futures_order_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_pm_um_futures_trade_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get UM Futures Trade Download Link by Id (USER_DATA).

        GET /papi/v1/um/trade/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-trade-download-link-by-id

        """
        return self._native_private(
            "get_pm_um_futures_trade_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_pm_um_futures_transaction_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get UM Futures Transaction Download Link by Id (USER_DATA).

        GET /papi/v1/um/income/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-futures-transaction-download-link-by-id

        """
        return self._native_private(
            "get_pm_um_futures_transaction_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def query_pm_portfolio_margin_negative_balance_interest_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Portfolio Margin Negative Balance Interest History (USER_DATA).

        GET /papi/v1/portfolio/interest-history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-portfolio-margin-negative-balance-interest-history

        """
        return self._native_private(
            "query_pm_portfolio_margin_negative_balance_interest_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def query_pm_user_negative_balance_auto_exchange_record(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query User Negative Balance Auto Exchange Record (USER_DATA).

        GET /papi/v1/portfolio/negative-balance-exchange-record. Native exchange symbols;
        decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-user-negative-balance-auto-exchange-record

        """
        return self._native_private(
            "query_pm_user_negative_balance_auto_exchange_record",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def repay_pm_futures_negative_balance(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Repay futures Negative Balance (USER_DATA).

        POST /papi/v1/repay-futures-negative-balance. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#repay-futures-negative-balance

        """
        return self._native_private(
            "repay_pm_futures_negative_balance", self._params(recvWindow=recv_window)
        )

    def pm_futures_tradfi_perps_contract(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Futures TradFi Perps Contract (USER_DATA).

        POST /papi/v1/um/stock/contract. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#futures-tradfi-perps-contract

        """
        return self._native_private(
            "pm_futures_tradfi_perps_contract", self._params(recvWindow=recv_window)
        )

    def get_pm_um_futures_bnb_burn_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get UM Futures BNB Burn Status (USER_DATA).

        GET /papi/v1/um/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#get-um-futures-bnb-burn-status

        """
        return self._native_private(
            "get_pm_um_futures_bnb_burn_status", self._params(recvWindow=recv_window)
        )

    def query_pm_current_cm_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Current CM Open Order (USER_DATA).

        GET /papi/v1/cm/openOrder. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-current-cm-open-order

        """
        return self._native_private(
            "query_pm_current_cm_open_order",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def query_pm_current_um_open_order(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Current UM Open Order (USER_DATA).

        GET /papi/v1/um/openOrder. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-current-um-open-order

        """
        return self._native_private(
            "query_pm_current_um_open_order",
            self._params(
                symbol=symbol,
                orderId=order_id,
                origClientOrderId=orig_client_order_id,
                recvWindow=recv_window,
            ),
        )

    def toggle_pm_bnb_burn_on_um_futures_trade(
        self, *, fee_burn: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Toggle BNB Burn On UM Futures Trade (TRADE).

        POST /papi/v1/um/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#toggle-bnb-burn-on-um-futures-trade

        """
        return self._native_private(
            "toggle_pm_bnb_burn_on_um_futures_trade",
            self._params(feeBurn=fee_burn, recvWindow=recv_window),
        )

    def get_futures_bnb_burn_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get BNB Burn Status (USER_DATA).

        GET /fapi/v1/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-bnb-burn-status

        """
        return self._native_private(
            "get_futures_bnb_burn_status", self._params(recvWindow=recv_window)
        )

    def get_futures_download_id_for_futures_order_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For Futures Order History (USER_DATA).

        GET /fapi/v1/order/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-order-history

        """
        return self._native_private(
            "get_futures_download_id_for_futures_order_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_futures_download_id_for_futures_trade_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For Futures Trade History (USER_DATA).

        GET /fapi/v1/trade/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-trade-history

        """
        return self._native_private(
            "get_futures_download_id_for_futures_trade_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_futures_download_id_for_futures_transaction_history(
        self, *, start_time: int, end_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Download Id For Futures Transaction History (USER_DATA).

        GET /fapi/v1/income/asyn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-transaction-history

        """
        return self._native_private(
            "get_futures_download_id_for_futures_transaction_history",
            self._params(startTime=start_time, endTime=end_time, recvWindow=recv_window),
        )

    def get_futures_futures_order_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Futures Order History Download Link by Id (USER_DATA).

        GET /fapi/v1/order/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-order-history-download-link-by-id

        """
        return self._native_private(
            "get_futures_futures_order_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_futures_futures_trade_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Futures Trade Download Link by Id (USER_DATA).

        GET /fapi/v1/trade/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-trade-download-link-by-id

        """
        return self._native_private(
            "get_futures_futures_trade_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def get_futures_futures_transaction_history_download_link_by_id(
        self, *, download_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Futures Transaction History Download Link by Id (USER_DATA).

        GET /fapi/v1/income/asyn/id. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-transaction-history-download-link-by-id

        """
        return self._native_private(
            "get_futures_futures_transaction_history_download_link_by_id",
            self._params(downloadId=download_id, recvWindow=recv_window),
        )

    def toggle_futures_bnb_burn_on_futures_trade(
        self, *, fee_burn: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Toggle BNB Burn On Futures Trade (TRADE).

        POST /fapi/v1/feeBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#toggle-bnb-burn-on-futures-trade

        """
        return self._native_private(
            "toggle_futures_bnb_burn_on_futures_trade",
            self._params(feeBurn=fee_burn, recvWindow=recv_window),
        )

    def futures_accept_the_offered_quote(
        self, *, quote_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Accept the offered quote (USER_DATA).

        POST /fapi/v1/convert/acceptQuote. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#accept-the-offered-quote

        """
        return self._native_private(
            "futures_accept_the_offered_quote",
            self._params(quoteId=quote_id, recvWindow=recv_window),
        )

    def futures_order_status(
        self, *, order_id: str | None = None, quote_id: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Order status (USER_DATA).

        GET /fapi/v1/convert/orderStatus. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#order-status

        """
        return self._native_private(
            "futures_order_status", self._params(orderId=order_id, quoteId=quote_id)
        )

    def futures_send_quote_request(
        self,
        *,
        from_asset: str,
        to_asset: str,
        from_amount: str | None = None,
        to_amount: str | None = None,
        valid_time: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Send Quote Request (USER_DATA).

        POST /fapi/v1/convert/getQuote. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#send-quote-request

        """
        return self._native_private(
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

    def futures_classic_portfolio_margin_account_information(
        self, *, asset: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Classic Portfolio Margin Account Information (USER_DATA).

        GET /fapi/v1/pmAccountInfo. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/portfolio-margin-endpoints#classic-portfolio-margin-account-information

        """
        return self._native_private(
            "futures_classic_portfolio_margin_account_information",
            self._params(asset=asset, recvWindow=recv_window),
        )

    def sign_futures_tradfi_perps_contract(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Futures TradFi Perps Contract (USER_DATA).

        POST /fapi/v1/stock/contract. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#futures-tradfi-perps-contract

        """
        return self._native_private(
            "sign_futures_tradfi_perps_contract", self._params(recvWindow=recv_window)
        )

    def get_futures_order_modify_history(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Order Modify History (USER_DATA).

        GET /fapi/v1/orderAmendment. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#get-order-modify-history

        """
        return self._native_private(
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

    def get_futures_position_margin_change_history(
        self,
        *,
        symbol: str,
        kind_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Position Margin Change History (TRADE).

        GET /fapi/v1/positionMargin/history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#get-position-margin-change-history

        """
        return self._native_private(
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

    def adjust_margin_cross_margin_max_leverage(self, *, max_leverage: int) -> Any:  # noqa: ANN401
        """
        Adjust cross margin max leverage (USER_DATA).

        POST /sapi/v1/margin/max-leverage. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#adjust-cross-margin-max-leverage

        """
        return self._native_private(
            "adjust_margin_cross_margin_max_leverage", self._params(maxLeverage=max_leverage)
        )

    def get_margin_bnb_burn_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get BNB Burn Status (USER_DATA).

        GET /sapi/v1/bnbBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#get-bnb-burn-status

        """
        return self._native_private(
            "get_margin_bnb_burn_status", self._params(recvWindow=recv_window)
        )

    def query_margin_cross_margin_fee_data(
        self,
        *,
        vip_level: int | None = None,
        coin: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Cross Margin Fee Data (USER_DATA).

        GET /sapi/v1/margin/crossMarginData. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-cross-margin-fee-data

        """
        return self._native_private(
            "query_margin_cross_margin_fee_data",
            self._params(vipLevel=vip_level, coin=coin, recvWindow=recv_window),
        )

    def query_margin_enabled_isolated_margin_account_limit(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Enabled Isolated Margin Account Limit (USER_DATA).

        GET /sapi/v1/margin/isolated/accountLimit. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-enabled-isolated-margin-account-limit

        """
        return self._native_private(
            "query_margin_enabled_isolated_margin_account_limit",
            self._params(recvWindow=recv_window),
        )

    def query_margin_isolated_margin_fee_data(
        self,
        *,
        vip_level: int | None = None,
        symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Isolated Margin Fee Data (USER_DATA).

        GET /sapi/v1/margin/isolatedMarginData. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-isolated-margin-fee-data

        """
        return self._native_private(
            "query_margin_isolated_margin_fee_data",
            self._params(vipLevel=vip_level, symbol=symbol, recvWindow=recv_window),
        )

    def get_margin_future_hourly_interest_rate(self, *, assets: str, is_isolated: str) -> Any:  # noqa: ANN401
        """
        Get future hourly interest rate (USER_DATA).

        GET /sapi/v1/margin/next-hourly-interest-rate. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/borrow-repay#get-future-hourly-interest-rate

        """
        return self._native_private(
            "get_margin_future_hourly_interest_rate",
            self._params(assets=assets, isIsolated=is_isolated),
        )

    def query_margin_margin_interest_rate_history(
        self,
        *,
        asset: str,
        vip_level: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Margin Interest Rate History (USER_DATA).

        GET /sapi/v1/margin/interestRateHistory. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/borrow-repay#query-margin-interest-rate-history

        """
        return self._native_private(
            "query_margin_margin_interest_rate_history",
            self._params(
                asset=asset,
                vipLevel=vip_level,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    def query_margin_isolated_margin_tier_data(
        self, *, symbol: str, tier: int | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Isolated Margin Tier Data (USER_DATA).

        GET /sapi/v1/margin/isolatedMarginTier. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#query-isolated-margin-tier-data

        """
        return self._native_private(
            "query_margin_isolated_margin_tier_data",
            self._params(symbol=symbol, tier=tier, recvWindow=recv_window),
        )

    def query_margin_margin_available_inventory(self, *, kind_type: str) -> Any:  # noqa: ANN401
        """
        Query Margin Available Inventory (USER_DATA).

        GET /sapi/v1/margin/available-inventory. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#query-margin-available-inventory

        """
        return self._native_private(
            "query_margin_margin_available_inventory", self._params(type=kind_type)
        )

    def create_margin_special_key(
        self,
        *,
        api_name: str,
        symbol: str | None = None,
        ip: str | None = None,
        public_key: str | None = None,
        permission_mode: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Create Special Key(Low-Latency Trading) (TRADE).

        POST /sapi/v1/margin/apiKey. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#create-special-key

        Warning: the response contains an API secret. Do not log the response.
        """
        return self._native_private(
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

    def delete_margin_special_key(
        self,
        *,
        api_name: str | None = None,
        symbol: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Delete Special Key(Low-Latency Trading) (TRADE).

        DELETE /sapi/v1/margin/apiKey. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#delete-special-key

        """
        return self._native_private(
            "delete_margin_special_key",
            self._params(apiName=api_name, symbol=symbol, recvWindow=recv_window),
        )

    def edit_margin_ip_for_special_key(
        self, *, ip: str, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Edit ip for Special Key(Low-Latency Trading) (TRADE).

        PUT /sapi/v1/margin/apiKey/ip. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#edit-ip-for-special-key

        """
        return self._native_private(
            "edit_margin_ip_for_special_key",
            self._params(ip=ip, symbol=symbol, recvWindow=recv_window),
        )

    def margin_exit_special_key_mode(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Exit Special Key Mode (TRADE).

        POST /sapi/v1/margin/exit-special-key-mode. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#exit-special-key-mode

        """
        return self._native_private(
            "margin_exit_special_key_mode", self._params(recvWindow=recv_window)
        )

    def get_margin_small_liability_exchange_coin_list(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Small Liability Exchange Coin List (USER_DATA).

        GET /sapi/v1/margin/exchange-small-liability. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-small-liability-exchange-coin-list

        """
        return self._native_private(
            "get_margin_small_liability_exchange_coin_list", self._params(recvWindow=recv_window)
        )

    def get_margin_small_liability_exchange_history(
        self,
        *,
        current: int,
        size: int,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Small Liability Exchange History (USER_DATA).

        GET /sapi/v1/margin/exchange-small-liability-history. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-small-liability-exchange-history

        """
        return self._native_private(
            "get_margin_small_liability_exchange_history",
            self._params(
                current=current,
                size=size,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    def margin_liquidation_loan_repay(
        self, *, asset: str, amount: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Liquidation Loan Repay (MARGIN).

        POST /sapi/v1/margin/liquidation-loan/repay. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#liquidation-loan-repay

        """
        return self._native_private(
            "margin_liquidation_loan_repay",
            self._params(asset=asset, amount=amount, recvWindow=recv_window),
        )

    def liquidate_margin_account(
        self, *, kind_type: str, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Margin Manual Liquidation (TRADE).

        POST /sapi/v1/margin/manual-liquidation. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-manual-liquidation

        """
        return self._native_private(
            "liquidate_margin_account",
            self._params(type=kind_type, symbol=symbol, recvWindow=recv_window),
        )

    def query_margin_liquidation_loan(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Query Liquidation Loan (USER_DATA).

        GET /sapi/v1/margin/liquidation-loan. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-liquidation-loan

        """
        return self._native_private(
            "query_margin_liquidation_loan", self._params(recvWindow=recv_window)
        )

    def query_margin_liquidation_loan_repay_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Liquidation Loan Repay History (USER_DATA).

        GET /sapi/v1/margin/liquidation-loan/repay-history. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-liquidation-loan-repay-history

        """
        return self._native_private(
            "query_margin_liquidation_loan_repay_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def query_margin_prevented_matches(
        self,
        *,
        symbol: str,
        prevented_match_id: int | None = None,
        order_id: int | None = None,
        from_prevented_match_id: int | None = None,
        is_isolated: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Prevented Matches (USER_DATA).

        GET /sapi/v1/margin/myPreventedMatches. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-prevented-matches

        """
        return self._native_private(
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

    def query_margin_special_key(
        self, *, api_key: str, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Special key(Low Latency Trading) (TRADE).

        GET /sapi/v1/margin/apiKey. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-special-key

        """
        return self._native_private(
            "query_margin_special_key",
            self._params(apiKey=api_key, symbol=symbol, recvWindow=recv_window),
        )

    def query_margin_special_key_list(
        self, *, symbol: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Special key List(Low Latency Trading) (TRADE).

        GET /sapi/v1/margin/api-key-list. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#query-special-key-list

        """
        return self._native_private(
            "query_margin_special_key_list", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def margin_small_liability_exchange(
        self, *, asset_names: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Small Liability Exchange (MARGIN).

        POST /sapi/v1/margin/exchange-small-liability. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#small-liability-exchange

        """
        return self._native_private(
            "margin_small_liability_exchange",
            self._params(assetNames=asset_names, recvWindow=recv_window),
        )

    def spot_my_filters(self, *, symbol: str, recv_window: str | None = None) -> Any:  # noqa: ANN401
        """
        Query relevant filters (USER_DATA).

        GET /api/v3/myFilters. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/account#my-filters

        """
        return self._native_private(
            "spot_my_filters", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def spot_order_amendments(
        self,
        *,
        symbol: str,
        order_id: int,
        from_execution_id: int | None = None,
        limit: int | None = None,
        recv_window: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Order Amendments (USER_DATA).

        GET /api/v3/order/amendments. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/account#order-amendments

        """
        return self._native_private(
            "spot_order_amendments",
            self._params(
                symbol=symbol,
                orderId=order_id,
                fromExecutionId=from_execution_id,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def place_spot_sor_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
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
    ) -> Any:  # noqa: ANN401
        """
        New order using SOR (TRADE).

        POST /api/v3/sor/order. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#sor-order

        """
        return self._native_private(
            "place_spot_sor_order",
            self._params(
                symbol=symbol,
                side=side,
                type=order_type,
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

    def test_spot_sor_order(
        self,
        *,
        symbol: str,
        side: str,
        order_type: str,
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
    ) -> Any:  # noqa: ANN401
        """
        Test new order using SOR (TRADE).

        POST /api/v3/sor/order/test. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#sor-order-test

        """
        return self._native_private(
            "test_spot_sor_order",
            self._params(
                symbol=symbol,
                side=side,
                type=order_type,
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

    def wallet_account_info(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Account info (USER_DATA).

        GET /sapi/v1/account/info. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#account-info

        """
        return self._native_private("wallet_account_info", self._params(recvWindow=recv_window))

    def wallet_daily_account_snapshot(
        self,
        *,
        kind_type: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Daily Account Snapshot (USER_DATA).

        GET /sapi/v1/accountSnapshot. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/account#daily-account-snapshot

        """
        return self._native_private(
            "wallet_daily_account_snapshot",
            self._params(
                type=kind_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def wallet_asset_detail(
        self, *, asset: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Asset Detail (USER_DATA).

        GET /sapi/v1/asset/assetDetail. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#asset-detail

        """
        return self._native_private(
            "wallet_asset_detail", self._params(asset=asset, recvWindow=recv_window)
        )

    def wallet_asset_dividend_record(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Asset Dividend Record (USER_DATA).

        GET /sapi/v1/asset/assetDividend. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#asset-dividend-record

        """
        return self._native_private(
            "wallet_asset_dividend_record",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def wallet_dust_convert(
        self,
        *,
        asset: str,
        account_type: str | None = None,
        client_id: str | None = None,
        target_asset: str | None = None,
        third_party_client_id: str | None = None,
        dust_quota_asset_to_target_asset_price: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Dust Convert (USER_DATA).

        POST /sapi/v1/asset/dust-convert/convert. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-convert

        """
        return self._native_private(
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

    def wallet_dust_convertible_assets(
        self,
        *,
        target_asset: str,
        account_type: str | None = None,
        dust_quota_asset_to_target_asset_price: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Dust Convertible Assets (USER_DATA).

        POST /sapi/v1/asset/dust-convert/query-convertible-assets. Native exchange symbols;
        decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-convertible-assets

        """
        return self._native_private(
            "wallet_dust_convertible_assets",
            self._params(
                targetAsset=target_asset,
                accountType=account_type,
                dustQuotaAssetToTargetAssetPrice=dust_quota_asset_to_target_asset_price,
            ),
        )

    def wallet_dustlog(
        self,
        *,
        account_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        DustLog (USER_DATA).

        GET /sapi/v1/asset/dribblet. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dustlog

        """
        return self._native_private(
            "wallet_dustlog",
            self._params(
                accountType=account_type,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    def get_wallet_assets_that_can_be_converted_into_bnb(
        self, *, account_type: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Assets That Can Be Converted Into BNB (USER_DATA).

        POST /sapi/v1/asset/dust-btc. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-assets-that-can-be-converted-into-bnb

        """
        return self._native_private(
            "get_wallet_assets_that_can_be_converted_into_bnb",
            self._params(accountType=account_type, recvWindow=recv_window),
        )

    def toggle_wallet_bnb_burn_on_spot_trade_and_margin_interest(
        self,
        *,
        spot_bnb_burn: str | None = None,
        interest_bnb_burn: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Toggle BNB Burn On Spot Trade And Margin Interest (USER_DATA).

        POST /sapi/v1/bnbBurn. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#toggle-bnb-burn-on-spot-trade-and-margin-interest

        """
        return self._native_private(
            "toggle_wallet_bnb_burn_on_spot_trade_and_margin_interest",
            self._params(
                spotBNBBurn=spot_bnb_burn, interestBNBBurn=interest_bnb_burn, recvWindow=recv_window
            ),
        )

    def wallet_fetch_deposit_address_list_with_network(
        self, *, coin: str, network: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Fetch deposit address list with network (USER_DATA).

        GET /sapi/v1/capital/deposit/address/list. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#fetch-deposit-address-list-with-network

        """
        return self._native_private(
            "wallet_fetch_deposit_address_list_with_network",
            self._params(coin=coin, network=network),
        )

    def wallet_one_click_arrival_deposit_apply(
        self,
        *,
        deposit_id: int | None = None,
        tx_id: str | None = None,
        sub_account_id: str | None = None,
        sub_user_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        One click arrival deposit apply (for expired address deposit) (USER_DATA).

        POST /sapi/v1/capital/deposit/credit-apply. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#one-click-arrival-deposit-apply

        """
        return self._native_private(
            "wallet_one_click_arrival_deposit_apply",
            self._params(
                depositId=deposit_id, txId=tx_id, subAccountId=sub_account_id, subUserId=sub_user_id
            ),
        )

    def algo_cancel_algo_order_future_algo(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Cancel Futures Algo Order (TRADE).

        DELETE /sapi/v1/algo/futures/order. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#cancel-algo-order-future-algo

        """
        return self._native_private(
            "algo_cancel_algo_order_future_algo",
            self._params(algoId=algo_id, clientAlgoId=client_algo_id, recvWindow=recv_window),
        )

    def query_algo_current_algo_open_orders_future_algo(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Current Futures Algo Open Orders (USER_DATA).

        GET /sapi/v1/algo/futures/openOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#query-current-algo-open-orders-future-algo

        """
        return self._native_private(
            "query_algo_current_algo_open_orders_future_algo", self._params(recvWindow=recv_window)
        )

    def query_algo_historical_algo_orders_future_algo(
        self,
        *,
        symbol: str | None = None,
        side: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Historical Futures Algo Orders (USER_DATA).

        GET /sapi/v1/algo/futures/historicalOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#query-historical-algo-orders-future-algo

        """
        return self._native_private(
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

    def query_algo_sub_orders_future_algo(
        self,
        *,
        algo_id: int,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Futures Sub Orders (USER_DATA).

        GET /sapi/v1/algo/futures/subOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#query-sub-orders-future-algo

        """
        return self._native_private(
            "query_algo_sub_orders_future_algo",
            self._params(algoId=algo_id, page=page, pageSize=page_size, recvWindow=recv_window),
        )

    def algo_time_weighted_average_price_future_algo(
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
    ) -> Any:  # noqa: ANN401
        """
        Time-Weighted Futures Average Price (Twap) New Order (TRADE).

        POST /sapi/v1/algo/futures/newOrderTwap. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#time-weighted-average-price-future-algo

        """
        return self._native_private(
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

    def algo_volume_participation_future_algo(
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
    ) -> Any:  # noqa: ANN401
        """
        Volume Participation (VP) New Order (TRADE).

        POST /sapi/v1/algo/futures/newOrderVp. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/future-algo#volume-participation-future-algo

        """
        return self._native_private(
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

    def algo_cancel_algo_order_spot_algo(
        self,
        *,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Cancel Spot Algo Order (TRADE).

        DELETE /sapi/v1/algo/spot/order. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#cancel-algo-order-spot-algo

        """
        return self._native_private(
            "algo_cancel_algo_order_spot_algo",
            self._params(algoId=algo_id, clientAlgoId=client_algo_id, recvWindow=recv_window),
        )

    def query_algo_current_algo_open_orders_spot_algo(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Current Spot Algo Open Orders (USER_DATA).

        GET /sapi/v1/algo/spot/openOrders. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#query-current-algo-open-orders-spot-algo

        """
        return self._native_private(
            "query_algo_current_algo_open_orders_spot_algo", self._params(recvWindow=recv_window)
        )

    def query_algo_historical_algo_orders_spot_algo(
        self,
        *,
        symbol: str | None = None,
        side: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Historical Spot Algo Orders (USER_DATA).

        GET /sapi/v1/algo/spot/historicalOrders. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#query-historical-algo-orders-spot-algo

        """
        return self._native_private(
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

    def query_algo_sub_orders_spot_algo(
        self,
        *,
        algo_id: int,
        page: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Spot Sub Orders (USER_DATA).

        GET /sapi/v1/algo/spot/subOrders. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#query-sub-orders-spot-algo

        """
        return self._native_private(
            "query_algo_sub_orders_spot_algo",
            self._params(algoId=algo_id, page=page, pageSize=page_size, recvWindow=recv_window),
        )

    def algo_time_weighted_average_price_spot_algo(
        self,
        *,
        symbol: str,
        side: str,
        quantity: str,
        duration: int,
        client_algo_id: str | None = None,
        limit_price: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Time-Weighted Spot Average Price(Twap) New Order (TRADE).

        POST /sapi/v1/algo/spot/newOrderTwap. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-algo-trading/api/rest-api/spot-algo#time-weighted-average-price-spot-algo

        """
        return self._native_private(
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

    def change_pm_pro_auto_repay_futures_status(
        self, *, auto_repay: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Change Auto-repay-futures Status (TRADE).

        POST /sapi/v1/portfolio/repay-futures-switch. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#change-auto-repay-futures-status

        """
        return self._native_private(
            "change_pm_pro_auto_repay_futures_status",
            self._params(autoRepay=auto_repay, recvWindow=recv_window),
        )

    def delete_pm_pro_margin_call_level(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Delete Margin Call Level (USER_DATA).

        DELETE /sapi/v1/portfolio/margin-call-level. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#delete-margin-call-level

        """
        return self._native_private(
            "delete_pm_pro_margin_call_level", self._params(recvWindow=recv_window)
        )

    def pm_pro_fund_auto_collection(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Fund Auto-collection (USER_DATA).

        POST /sapi/v1/portfolio/auto-collection. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#fund-auto-collection

        """
        return self._native_private(
            "pm_pro_fund_auto_collection", self._params(recvWindow=recv_window)
        )

    def pm_pro_fund_collection_by_asset(self, *, asset: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Fund Collection by Asset (USER_DATA).

        POST /sapi/v1/portfolio/asset-collection. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#fund-collection-by-asset

        """
        return self._native_private(
            "pm_pro_fund_collection_by_asset", self._params(asset=asset, recvWindow=recv_window)
        )

    def get_pm_pro_auto_repay_futures_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Auto-repay-futures Status (USER_DATA).

        GET /sapi/v1/portfolio/repay-futures-switch. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-auto-repay-futures-status

        """
        return self._native_private(
            "get_pm_pro_auto_repay_futures_status", self._params(recvWindow=recv_window)
        )

    def get_pm_pro_delta_mode_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Delta Mode Status (USER_DATA).

        GET /sapi/v1/portfolio/delta-mode. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-delta-mode-status

        """
        return self._native_private(
            "get_pm_pro_delta_mode_status", self._params(recvWindow=recv_window)
        )

    def get_pm_pro_margin_call_level(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Margin Call Level (USER_DATA).

        GET /sapi/v1/portfolio/margin-call-level. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-margin-call-level

        """
        return self._native_private(
            "get_pm_pro_margin_call_level", self._params(recvWindow=recv_window)
        )

    def get_pm_pro_portfolio_margin_pro_account_balance(
        self, *, asset: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Portfolio Margin Pro Account Balance (USER_DATA).

        GET /sapi/v1/portfolio/balance. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-account-balance

        """
        return self._native_private(
            "get_pm_pro_portfolio_margin_pro_account_balance",
            self._params(asset=asset, recvWindow=recv_window),
        )

    def get_pm_pro_portfolio_margin_pro_account_info(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Portfolio Margin Pro Account Info (USER_DATA).

        GET /sapi/v1/portfolio/account. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-account-info

        """
        return self._native_private(
            "get_pm_pro_portfolio_margin_pro_account_info", self._params(recvWindow=recv_window)
        )

    def get_pm_pro_portfolio_margin_pro_span_account_info(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Portfolio Margin Pro SPAN Account Info (USER_DATA).

        GET /sapi/v2/portfolio/account. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-span-account-info

        """
        return self._native_private(
            "get_pm_pro_portfolio_margin_pro_span_account_info",
            self._params(recvWindow=recv_window),
        )

    def pm_pro_portfolio_margin_pro_bankruptcy_loan_repay(
        self, *, var_from: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Portfolio Margin Pro Bankruptcy Loan Repay (TRADE).

        POST /sapi/v1/portfolio/repay. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#portfolio-margin-pro-bankruptcy-loan-repay

        """
        return self._native_private(
            "pm_pro_portfolio_margin_pro_bankruptcy_loan_repay",
            self._params(**{"from": var_from}, recvWindow=recv_window),
        )

    def query_pm_pro_portfolio_margin_pro_bankruptcy_loan_amount(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Portfolio Margin Pro Bankruptcy Loan Amount (USER_DATA).

        GET /sapi/v1/portfolio/pmLoan. Native exchange symbols; decimal amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-bankruptcy-loan-amount

        """
        return self._native_private(
            "query_pm_pro_portfolio_margin_pro_bankruptcy_loan_amount",
            self._params(recvWindow=recv_window),
        )

    def query_pm_pro_portfolio_margin_pro_bankruptcy_loan_repay_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        size: int | None = None,
        current: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Portfolio Margin Pro Bankruptcy Loan Repay History (USER_DATA).

        GET /sapi/v1/portfolio/pmloan-history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-bankruptcy-loan-repay-history

        """
        return self._native_private(
            "query_pm_pro_portfolio_margin_pro_bankruptcy_loan_repay_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                size=size,
                current=current,
                recvWindow=recv_window,
            ),
        )

    def query_pm_pro_portfolio_margin_pro_negative_balance_interest_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Portfolio Margin Pro Negative Balance Interest History (USER_DATA).

        GET /sapi/v1/portfolio/interest-history. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#query-portfolio-margin-pro-negative-balance-interest-history

        """
        return self._native_private(
            "query_pm_pro_portfolio_margin_pro_negative_balance_interest_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def repay_pm_pro_futures_negative_balance(
        self, *, var_from: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Repay futures Negative Balance (USER_DATA).

        POST /sapi/v1/portfolio/repay-futures-negative-balance. Native exchange symbols; decimal
        amounts are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#repay-futures-negative-balance

        """
        return self._native_private(
            "repay_pm_pro_futures_negative_balance",
            self._params(**{"from": var_from}, recvWindow=recv_window),
        )

    def set_pm_pro_margin_call_level(
        self, *, margin_call_level: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Set Margin Call Level (USER_DATA).

        POST /sapi/v1/portfolio/margin-call-level. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#set-margin-call-level

        """
        return self._native_private(
            "set_pm_pro_margin_call_level",
            self._params(marginCallLevel=margin_call_level, recvWindow=recv_window),
        )

    def pm_pro_switch_delta_mode(
        self, *, delta_enabled: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Switch Delta Mode (TRADE).

        POST /sapi/v1/portfolio/delta-mode. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#switch-delta-mode

        """
        return self._native_private(
            "pm_pro_switch_delta_mode",
            self._params(deltaEnabled=delta_enabled, recvWindow=recv_window),
        )

    def get_pm_pro_portfolio_margin_asset_leverage(self) -> Any:  # noqa: ANN401
        """
        Get Portfolio Margin Asset Leverage (USER_DATA).

        GET /sapi/v1/portfolio/margin-asset-leverage. Native exchange symbols; decimal amounts
        are strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#get-portfolio-margin-asset-leverage

        """
        return self._native_private("get_pm_pro_portfolio_margin_asset_leverage", self._params())

    def pm_pro_portfolio_margin_pro_tiered_collateral_rate(
        self, *, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Portfolio Margin Pro Tiered Collateral Rate (USER_DATA).

        GET /sapi/v2/portfolio/collateralRate. Native exchange symbols; decimal amounts are
        strings.
        Timestamps are milliseconds. Source:
        https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#portfolio-margin-pro-tiered-collateral-rate

        """
        return self._native_private(
            "pm_pro_portfolio_margin_pro_tiered_collateral_rate",
            self._params(recvWindow=recv_window),
        )

    def tradfi_options_contract(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /eapi/v1/stock/contract.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/trade#tradfi-options-contract
        """
        return self._native_private("tradfi_options_contract", self._params(recvWindow=recv_window))

    def get_cloud_mining_payment_and_refund_history(
        self,
        *,
        start_time: int,
        end_time: int,
        tran_id: int | None = None,
        client_tran_id: str | None = None,
        asset: str | None = None,
        current: int | None = None,
        size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/asset/ledger-transfer/cloud-mining/queryByPage.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#get-cloud-mining-payment-and-refund-history
        """
        return self._native_private(
            "get_cloud_mining_payment_and_refund_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                tranId=tran_id,
                clientTranId=client_tran_id,
                asset=asset,
                current=current,
                size=size,
            ),
        )

    def query_user_delegation_history(
        self,
        *,
        email: str,
        start_time: int,
        end_time: int,
        type_: str | None = None,
        asset: str | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/asset/custody/transfer-history.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#query-user-delegation-history
        """
        return self._native_private(
            "query_user_delegation_history",
            self._params(
                email=email,
                startTime=start_time,
                endTime=end_time,
                type=type_,
                asset=asset,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def check_questionnaire_requirements(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/localentity/questionnaire-requirements.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#check-questionnaire-requirements
        """
        return self._native_private(
            "check_questionnaire_requirements", self._params(recvWindow=recv_window)
        )

    def get_travel_rule_deposit_history(
        self,
        *,
        tr_id: str | None = None,
        tx_id: str | None = None,
        tran_id: str | None = None,
        network: str | None = None,
        coin: str | None = None,
        travel_rule_status: int | None = None,
        pending_questionnaire: bool | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/localentity/deposit/history.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#deposit-history-travel-rule
        """
        return self._native_private(
            "get_travel_rule_deposit_history",
            self._params(
                trId=tr_id,
                txId=tx_id,
                tranId=tran_id,
                network=network,
                coin=coin,
                travelRuleStatus=travel_rule_status,
                pendingQuestionnaire=pending_questionnaire,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
            ),
        )

    def get_travel_rule_deposit_history_v2(
        self,
        *,
        deposit_id: int | None = None,
        tx_id: str | None = None,
        network: str | None = None,
        coin: str | None = None,
        retrieve_questionnaire: bool | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v2/localentity/deposit/history.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#deposit-history-v2
        """
        return self._native_private(
            "get_travel_rule_deposit_history_v2",
            self._params(
                depositId=deposit_id,
                txId=tx_id,
                network=network,
                coin=coin,
                retrieveQuestionnaire=retrieve_questionnaire,
                startTime=start_time,
                endTime=end_time,
                offset=offset,
                limit=limit,
            ),
        )

    def fetch_address_verification_list(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/addressVerify/list.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#fetch-address-verification-list
        """
        return self._native_private(
            "fetch_address_verification_list", self._params(recvWindow=recv_window)
        )

    def get_country_list(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/localentity/country/list.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#get-country-list
        """
        return self._native_private("get_country_list", self._params(recvWindow=recv_window))

    def get_region_list(self, *, country_code: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/localentity/region/list.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#get-region-list
        """
        return self._native_private(
            "get_region_list", self._params(countryCode=country_code, recvWindow=recv_window)
        )

    def submit_deposit_questionnaire_travel_rule(self, *, tran_id: int, questionnaire: str) -> Any:  # noqa: ANN401
        """
        PUT /sapi/v1/localentity/deposit/provide-info.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#submit-deposit-questionnaire-travel-rule
        """
        return self._native_private(
            "submit_deposit_questionnaire_travel_rule",
            self._params(tranId=tran_id, questionnaire=questionnaire),
        )

    def submit_deposit_questionnaire_v2(self, *, deposit_id: int, questionnaire: str) -> Any:  # noqa: ANN401
        """
        PUT /sapi/v2/localentity/deposit/provide-info.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#submit-deposit-questionnaire-v2
        """
        return self._native_private(
            "submit_deposit_questionnaire_v2",
            self._params(depositId=deposit_id, questionnaire=questionnaire),
        )

    def vasp_list(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/localentity/vasp.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#vasp-list
        """
        return self._native_private("vasp_list", self._params(recvWindow=recv_window))

    def get_futures_lead_trader_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/copyTrading/futures/userStatus.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-copy-trading/api/rest-api/future-copy-trading#get-futures-lead-trader-status
        """
        return self._native_private(
            "get_futures_lead_trader_status", self._params(recvWindow=recv_window)
        )

    def get_futures_lead_trading_symbol_whitelist(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/copyTrading/futures/leadSymbol.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-copy-trading/api/rest-api/future-copy-trading#get-futures-lead-trading-symbol-whitelist
        """
        return self._native_private(
            "get_futures_lead_trading_symbol_whitelist", self._params(recvWindow=recv_window)
        )

    def change_auto_compound_status(
        self, *, position_id: str, auto_compound_plan: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/dci/product/auto_compound/edit-status.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/trade#change-auto-compound-status
        """
        return self._native_private(
            "change_auto_compound_status",
            self._params(
                positionId=position_id, autoCompoundPlan=auto_compound_plan, recvWindow=recv_window
            ),
        )

    def check_dual_investment_accounts(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/dci/product/accounts.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/trade#check-dual-investment-accounts
        """
        return self._native_private(
            "check_dual_investment_accounts", self._params(recvWindow=recv_window)
        )

    def get_dual_investment_positions(
        self,
        *,
        status: str | None = None,
        page_size: int | None = None,
        page_index: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/dci/product/positions.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/trade#get-dual-investment-positions
        """
        return self._native_private(
            "get_dual_investment_positions",
            self._params(
                status=status, pageSize=page_size, pageIndex=page_index, recvWindow=recv_window
            ),
        )

    def subscribe_dual_investment_products(
        self,
        *,
        id: str,
        order_id: str,
        deposit_amount: str,
        auto_compound_plan: str,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/dci/product/subscribe.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/trade#subscribe-dual-investment-products
        """
        return self._native_private(
            "subscribe_dual_investment_products",
            self._params(
                id=id,
                orderId=order_id,
                depositAmount=deposit_amount,
                autoCompoundPlan=auto_compound_plan,
                recvWindow=recv_window,
            ),
        )

    def get_bfusd_account(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/bfusd/account.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-account
        """
        return self._native_private("get_bfusd_account", self._params(recvWindow=recv_window))

    def get_bfusd_quota_details(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/bfusd/quota.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-quota-details
        """
        return self._native_private("get_bfusd_quota_details", self._params(recvWindow=recv_window))

    def get_bfusd_rate_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/bfusd/history/rateHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-rate-history
        """
        return self._native_private(
            "get_bfusd_rate_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_bfusd_redemption_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/bfusd/history/redemptionHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-redemption-history
        """
        return self._native_private(
            "get_bfusd_redemption_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_bfusd_rewards_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/bfusd/history/rewardsHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-rewards-history
        """
        return self._native_private(
            "get_bfusd_rewards_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_bfusd_subscription_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/bfusd/history/subscriptionHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-subscription-history
        """
        return self._native_private(
            "get_bfusd_subscription_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def redeem_bfusd(self, *, amount: str, type_: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/bfusd/redeem.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#redeem-bfusd
        """
        return self._native_private(
            "redeem_bfusd", self._params(amount=amount, type=type_, recvWindow=recv_window)
        )

    def subscribe_bfusd(self, *, asset: str, amount: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/bfusd/subscribe.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#subscribe-bfusd
        """
        return self._native_private(
            "subscribe_bfusd", self._params(asset=asset, amount=amount, recvWindow=recv_window)
        )

    def get_collateral_record(
        self,
        *,
        product_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/simple-earn/flexible/history/collateralRecord.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-collateral-record
        """
        return self._native_private(
            "get_collateral_record",
            self._params(
                productId=product_id,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_flexible_personal_left_quota(
        self, *, product_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/simple-earn/flexible/personalLeftQuota.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-flexible-personal-left-quota
        """
        return self._native_private(
            "get_flexible_personal_left_quota",
            self._params(productId=product_id, recvWindow=recv_window),
        )

    def get_flexible_subscription_preview(
        self, *, product_id: str, amount: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/simple-earn/flexible/subscriptionPreview.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-flexible-subscription-preview
        """
        return self._native_private(
            "get_flexible_subscription_preview",
            self._params(productId=product_id, amount=amount, recvWindow=recv_window),
        )

    def get_locked_personal_left_quota(
        self, *, project_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/simple-earn/locked/personalLeftQuota.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-locked-personal-left-quota
        """
        return self._native_private(
            "get_locked_personal_left_quota",
            self._params(projectId=project_id, recvWindow=recv_window),
        )

    def get_locked_subscription_preview(
        self,
        *,
        project_id: str,
        amount: str,
        auto_subscribe: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/simple-earn/locked/subscriptionPreview.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-locked-subscription-preview
        """
        return self._native_private(
            "get_locked_subscription_preview",
            self._params(
                projectId=project_id,
                amount=amount,
                autoSubscribe=auto_subscribe,
                recvWindow=recv_window,
            ),
        )

    def get_flexible_rate_history(
        self,
        *,
        product_id: str,
        apr_period: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/simple-earn/flexible/history/rateHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-rate-history
        """
        return self._native_private(
            "get_flexible_rate_history",
            self._params(
                productId=product_id,
                aprPeriod=apr_period,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def set_flexible_auto_subscribe(
        self, *, product_id: str, auto_subscribe: bool, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/simple-earn/flexible/setAutoSubscribe.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#set-flexible-auto-subscribe
        """
        return self._native_private(
            "set_flexible_auto_subscribe",
            self._params(
                productId=product_id, autoSubscribe=auto_subscribe, recvWindow=recv_window
            ),
        )

    def set_locked_auto_subscribe(
        self, *, position_id: str, auto_subscribe: bool, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/simple-earn/locked/setAutoSubscribe.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#set-locked-auto-subscribe
        """
        return self._native_private(
            "set_locked_auto_subscribe",
            self._params(
                positionId=position_id, autoSubscribe=auto_subscribe, recvWindow=recv_window
            ),
        )

    def set_locked_product_redeem_option(
        self, *, position_id: str, redeem_to: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/simple-earn/locked/setRedeemOption.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#set-locked-product-redeem-option
        """
        return self._native_private(
            "set_locked_product_redeem_option",
            self._params(positionId=position_id, redeemTo=redeem_to, recvWindow=recv_window),
        )

    def get_rwusd_account(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/rwusd/account.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-account
        """
        return self._native_private("get_rwusd_account", self._params(recvWindow=recv_window))

    def get_rwusd_quota_details(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/rwusd/quota.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-quota-details
        """
        return self._native_private("get_rwusd_quota_details", self._params(recvWindow=recv_window))

    def get_rwusd_rate_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/rwusd/history/rateHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-rate-history
        """
        return self._native_private(
            "get_rwusd_rate_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_rwusd_redemption_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/rwusd/history/redemptionHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-redemption-history
        """
        return self._native_private(
            "get_rwusd_redemption_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_rwusd_rewards_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/rwusd/history/rewardsHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-rewards-history
        """
        return self._native_private(
            "get_rwusd_rewards_history",
            self._params(
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_rwusd_subscription_history(
        self,
        *,
        asset: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/rwusd/history/subscriptionHistory.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#get-rwusd-subscription-history
        """
        return self._native_private(
            "get_rwusd_subscription_history",
            self._params(
                asset=asset,
                startTime=start_time,
                endTime=end_time,
                current=current,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def redeem_rwusd(self, *, amount: str, type_: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/rwusd/redeem.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#redeem-rwusd
        """
        return self._native_private(
            "redeem_rwusd", self._params(amount=amount, type=type_, recvWindow=recv_window)
        )

    def subscribe_rwusd(self, *, asset: str, amount: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/rwusd/subscribe.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/rwusd#subscribe-rwusd
        """
        return self._native_private(
            "subscribe_rwusd", self._params(asset=asset, amount=amount, recvWindow=recv_window)
        )

    def get_yield_arena_activities(
        self, *, lang: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/earn/arena/activities.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/yield-arena#get-yield-arena-activities
        """
        return self._native_private(
            "get_yield_arena_activities", self._params(lang=lang, recvWindow=recv_window)
        )

    def create_a_virtual_sub_account(
        self, *, sub_account_string: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/sub-account/virtualSubAccount.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/account-management#create-avirtual-sub-account
        """
        return self._native_private(
            "create_a_virtual_sub_account",
            self._params(subAccountString=sub_account_string, recvWindow=recv_window),
        )

    def enable_futures_for_sub_account(self, *, email: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/sub-account/futures/enable.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/account-management#enable-futures-for-sub-account
        """
        return self._native_private(
            "enable_futures_for_sub_account", self._params(email=email, recvWindow=recv_window)
        )

    def enable_options_for_sub_account(self, *, email: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/sub-account/eoptions/enable.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/account-management#enable-options-for-sub-account
        """
        return self._native_private(
            "enable_options_for_sub_account", self._params(email=email, recvWindow=recv_window)
        )

    def add_ip_restriction_for_sub_account_api_key(
        self,
        *,
        email: str,
        sub_account_api_key: str,
        status: int,
        ip_address: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v2/sub-account/subAccountApi/ipRestriction.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#add-ip-restriction-for-sub-account-api-key
        """
        return self._native_private(
            "add_ip_restriction_for_sub_account_api_key",
            self._params(
                email=email,
                subAccountApiKey=sub_account_api_key,
                status=status,
                ipAddress=ip_address,
                recvWindow=recv_window,
            ),
        )

    def create_sub_account_api_key(
        self,
        *,
        email: str,
        api_name: str,
        status: int,
        can_trade: bool | None = None,
        can_margin_loan_repay: bool | None = None,
        can_futures_trade: bool | None = None,
        can_universal_transfer: bool | None = None,
        can_vanilla_options: bool | None = None,
        ip_address: str | None = None,
        third_party_name: str | None = None,
        public_key: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/sub-account/subAccountApi.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#create-sub-account-api-key
        """
        return self._native_private(
            "create_sub_account_api_key",
            self._params(
                email=email,
                apiName=api_name,
                status=status,
                canTrade=can_trade,
                canMarginLoanRepay=can_margin_loan_repay,
                canFuturesTrade=can_futures_trade,
                canUniversalTransfer=can_universal_transfer,
                canVanillaOptions=can_vanilla_options,
                ipAddress=ip_address,
                thirdPartyName=third_party_name,
                publicKey=public_key,
                recvWindow=recv_window,
            ),
        )

    def delete_ip_list_for_a_sub_account_api_key(
        self,
        *,
        email: str,
        sub_account_api_key: str,
        ip_address: str,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        DELETE /sapi/v1/sub-account/subAccountApi/ipRestriction/ipList.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#delete-ip-list-for-asub-account-api-key
        """
        return self._native_private(
            "delete_ip_list_for_a_sub_account_api_key",
            self._params(
                email=email,
                subAccountApiKey=sub_account_api_key,
                ipAddress=ip_address,
                recvWindow=recv_window,
            ),
        )

    def delete_sub_account_api_key(
        self, *, email: str, sub_account_api_key: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        DELETE /sapi/v1/sub-account/subAccountApi.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#delete-sub-account-api-key
        """
        return self._native_private(
            "delete_sub_account_api_key",
            self._params(email=email, subAccountApiKey=sub_account_api_key, recvWindow=recv_window),
        )

    def get_ip_restriction_for_a_sub_account_api_key(
        self, *, email: str, sub_account_api_key: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/sub-account/subAccountApi/ipRestriction.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#get-ip-restriction-for-asub-account-api-key
        """
        return self._native_private(
            "get_ip_restriction_for_a_sub_account_api_key",
            self._params(email=email, subAccountApiKey=sub_account_api_key, recvWindow=recv_window),
        )

    def modify_sub_account_api_key_permission(
        self,
        *,
        email: str,
        sub_account_api_key: str,
        can_trade: bool | None = None,
        can_margin_loan_repay: bool | None = None,
        can_futures_trade: bool | None = None,
        can_universal_transfer: bool | None = None,
        can_vanilla_options: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/sub-account/subAccountApiPermission.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#modify-sub-account-api-key-permission
        """
        return self._native_private(
            "modify_sub_account_api_key_permission",
            self._params(
                email=email,
                subAccountApiKey=sub_account_api_key,
                canTrade=can_trade,
                canMarginLoanRepay=can_margin_loan_repay,
                canFuturesTrade=can_futures_trade,
                canUniversalTransfer=can_universal_transfer,
                canVanillaOptions=can_vanilla_options,
                recvWindow=recv_window,
            ),
        )

    def query_sub_account_api_key(
        self,
        *,
        email: str,
        sub_account_api_key: str | None = None,
        page: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/sub-account/subAccountApi.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/api-management#query-sub-account-api-key
        """
        return self._native_private(
            "query_sub_account_api_key",
            self._params(
                email=email,
                subAccountApiKey=sub_account_api_key,
                page=page,
                size=size,
                recvWindow=recv_window,
            ),
        )

    def get_move_position_history_for_sub_account(
        self,
        *,
        symbol: str,
        page: int,
        rows: int,
        product_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/sub-account/futures/move-position.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#get-move-position-history-for-sub-account
        """
        return self._native_private(
            "get_move_position_history_for_sub_account",
            self._params(
                symbol=symbol,
                page=page,
                rows=rows,
                productType=product_type,
                startTime=start_time,
                endTime=end_time,
                recvWindow=recv_window,
            ),
        )

    def get_sub_account_deposit_address(
        self,
        *,
        email: str,
        coin: str,
        network: str | None = None,
        amount: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/deposit/subAddress.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#get-sub-account-deposit-address
        """
        return self._native_private(
            "get_sub_account_deposit_address",
            self._params(
                email=email, coin=coin, network=network, amount=amount, recvWindow=recv_window
            ),
        )

    def get_sub_account_deposit_history(
        self,
        *,
        email: str,
        include_source: bool | None = None,
        coin: str | None = None,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        recv_window: int | None = None,
        tx_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/capital/deposit/subHisrec.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#get-sub-account-deposit-history
        """
        return self._native_private(
            "get_sub_account_deposit_history",
            self._params(
                email=email,
                includeSource=include_source,
                coin=coin,
                status=status,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                offset=offset,
                recvWindow=recv_window,
                txId=tx_id,
            ),
        )

    def move_position_for_sub_account(
        self,
        *,
        from_user_email: str,
        to_user_email: str,
        product_type: str,
        order_args: list[dict[str, Any]],
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/sub-account/futures/move-position.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#move-position-for-sub-account
        """
        return self._native_private(
            "move_position_for_sub_account",
            self._params(
                fromUserEmail=from_user_email,
                toUserEmail=to_user_email,
                productType=product_type,
                orderArgs=dumps(order_args, separators=(",", ":"), allow_nan=False)
                if order_args is not None
                else None,
                recvWindow=recv_window,
            ),
        )

    def deposit_assets_into_the_managed_sub_account(
        self, *, to_email: str, asset: str, amount: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /sapi/v1/managed-subaccount/deposit.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#deposit-assets-into-the-managed-sub-account
        """
        return self._native_private(
            "deposit_assets_into_the_managed_sub_account",
            self._params(toEmail=to_email, asset=asset, amount=amount, recvWindow=recv_window),
        )

    def get_managed_sub_account_deposit_address(
        self,
        *,
        email: str,
        coin: str,
        network: str | None = None,
        amount: str | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/deposit/address.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#get-managed-sub-account-deposit-address
        """
        return self._native_private(
            "get_managed_sub_account_deposit_address",
            self._params(
                email=email, coin=coin, network=network, amount=amount, recvWindow=recv_window
            ),
        )

    def query_managed_sub_account_asset_details(
        self, *, email: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/asset.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-asset-details
        """
        return self._native_private(
            "query_managed_sub_account_asset_details",
            self._params(email=email, recvWindow=recv_window),
        )

    def query_managed_sub_account_futures_asset_details(
        self, *, email: str, account_type: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/fetch-future-asset.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-futures-asset-details
        """
        return self._native_private(
            "query_managed_sub_account_futures_asset_details",
            self._params(email=email, accountType=account_type),
        )

    def query_managed_sub_account_list(
        self,
        *,
        email: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/info.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-list
        """
        return self._native_private(
            "query_managed_sub_account_list",
            self._params(email=email, page=page, limit=limit, recvWindow=recv_window),
        )

    def query_managed_sub_account_margin_asset_details(
        self, *, email: str, account_type: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/marginAsset.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-margin-asset-details
        """
        return self._native_private(
            "query_managed_sub_account_margin_asset_details",
            self._params(email=email, accountType=account_type),
        )

    def query_managed_sub_account_snapshot(
        self,
        *,
        email: str,
        type_: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /sapi/v1/managed-subaccount/accountSnapshot.

        Native symbols; decimal amounts are strings. Exchange eligibility applies.
        Source: https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#query-managed-sub-account-snapshot
        """
        return self._native_private(
            "query_managed_sub_account_snapshot",
            self._params(
                email=email,
                type=type_,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def enable_isolated_margin_account(
        self, *, symbol: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Change availability of an existing isolated margin account for a symbol."""
        return self._native_private(
            "enable_isolated_margin_account", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def disable_isolated_margin_account(
        self, *, symbol: str, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Change availability of an existing isolated margin account for a symbol."""
        return self._native_private(
            "disable_isolated_margin_account", self._params(symbol=symbol, recvWindow=recv_window)
        )

    def get_options_cancel_countdown(
        self, *, underlying: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """Get active options automatic-cancellation timers; disabled timers are omitted."""
        return self._native_private(
            "get_options_cancel_countdown",
            self._params(underlying=underlying, recvWindow=recv_window),
        )

    def set_options_cancel_countdown(
        self, *, underlying: str, countdown_time: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Set the options disconnection timer in milliseconds; 0 disables, minimum 5000.

        Send recurring heartbeats before expiry. Expiry cancels all open orders for
        this underlying and rejects new orders until a heartbeat or timer disable."""
        return self._native_private(
            "set_options_cancel_countdown",
            self._params(
                underlying=underlying, countdownTime=countdown_time, recvWindow=recv_window
            ),
        )

    def send_options_cancel_heartbeat(
        self, *, underlyings: str | list[str], recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Refresh the options cancellation timers for comma-separated underlying symbols.

        The response lists only successfully refreshed symbols; inspect every result."""
        if isinstance(underlyings, list):
            underlyings = ",".join(underlyings)
        return self._native_private(
            "send_options_cancel_heartbeat",
            self._params(underlyings=underlyings, recvWindow=recv_window),
        )

    def get_options_mmp_config(self, *, underlying: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """Get market-maker protection settings for the native underlying symbol."""
        return self._native_private(
            "get_options_mmp_config",
            self._params(underlying=underlying, recvWindow=recv_window),
        )

    def reset_options_mmp(self, *, underlying: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """Reset triggered options market-maker protection and permit new MMP orders."""
        return self._native_private(
            "reset_options_mmp", self._params(underlying=underlying, recvWindow=recv_window)
        )

    def set_options_mmp_config(
        self,
        *,
        underlying: str,
        window_time: int,
        frozen_time: int,
        qty_limit: str,
        delta_limit: str,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Set options MMP limits; window_time is 0..5000 milliseconds.

        frozen_time=0 requires a manual reset after MMP triggers. Only MMP orders
        are cancelled when these limits trigger. Quantity/delta limits are decimals."""
        return self._native_private(
            "set_options_mmp_config",
            self._params(
                underlying=underlying,
                windowTimeInMilliseconds=window_time,
                frozenTimeInMilliseconds=frozen_time,
                qtyLimit=qty_limit,
                deltaLimit=delta_limit,
                recvWindow=recv_window,
            ),
        )

    def accept_options_block_order(
        self,
        *,
        block_order_matching_key: str,
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /eapi/v1/block/order/execute.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#accept-block-trade-order
        """
        return self._native_private(
            "accept_options_block_order",
            self._params(
                blockOrderMatchingKey=block_order_matching_key,
                recvWindow=recv_window,
            ),
        )

    def get_options_account_block_trades(
        self,
        *,
        end_time: int | None = None,
        start_time: int | None = None,
        underlying: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """
        GET /eapi/v1/block/user-trades.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#account-block-trade-list
        """
        return self._native_private(
            "get_options_account_block_trades",
            self._params(
                endTime=end_time,
                startTime=start_time,
                underlying=underlying,
                recvWindow=recv_window,
            ),
        )

    def cancel_options_block_order(
        self,
        *,
        block_order_matching_key: str,
        recv_window: int | None = None,
    ) -> dict:
        """
        DELETE /eapi/v1/block/order/create.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#cancel-block-trade-order
        """
        return self._native_private(
            "cancel_options_block_order",
            self._params(
                blockOrderMatchingKey=block_order_matching_key,
                recvWindow=recv_window,
            ),
        )

    def extend_options_block_order(
        self,
        *,
        block_order_matching_key: str,
        recv_window: int | None = None,
    ) -> dict:
        """
        PUT /eapi/v1/block/order/create.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#extend-block-trade-order
        """
        return self._native_private(
            "extend_options_block_order",
            self._params(
                blockOrderMatchingKey=block_order_matching_key,
                recvWindow=recv_window,
            ),
        )

    def create_options_block_order(
        self,
        *,
        liquidity: str,
        legs: list[dict[str, Any]],
        recv_window: int | None = None,
    ) -> dict:
        """
        POST /eapi/v1/block/order/create.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#new-block-trade-order
        """
        return self._native_private(
            "create_options_block_order",
            self._params(
                liquidity=liquidity,
                legs=dumps(legs, separators=(",", ":"), allow_nan=False),
                recvWindow=recv_window,
            ),
        )

    def get_options_block_order_details(
        self,
        *,
        block_order_matching_key: str,
        recv_window: int | None = None,
    ) -> dict:
        """
        GET /eapi/v1/block/order/execute.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#query-block-trade-details
        """
        return self._native_private(
            "get_options_block_order_details",
            self._params(
                blockOrderMatchingKey=block_order_matching_key,
                recvWindow=recv_window,
            ),
        )

    def get_options_block_orders(
        self,
        *,
        block_order_matching_key: str | None = None,
        end_time: int | None = None,
        start_time: int | None = None,
        underlying: str | None = None,
        recv_window: int | None = None,
    ) -> dict:
        """
        GET /eapi/v1/block/order/orders.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/market-maker-block-trade#query-block-trade-order
        """
        return self._native_private(
            "get_options_block_orders",
            self._params(
                blockOrderMatchingKey=block_order_matching_key,
                endTime=end_time,
                startTime=start_time,
                underlying=underlying,
                recvWindow=recv_window,
            ),
        )

    def submit_broker_deposit_questionnaire(
        self,
        *,
        sub_account_id: str,
        deposit_id: int,
        questionnaire: dict[str, Any],
        beneficiary_pii: dict[str, Any],
        network: str | None = None,
        coin: str | None = None,
        amount: str | None = None,
        address: str | None = None,
        address_tag: str | None = None,
    ) -> dict:
        """
        PUT /sapi/v1/localentity/broker/deposit/provide-info.
        Pass JSON objects; URL encoding is applied exactly once by the transport.

        https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#submit-deposit-questionnaire
        """
        return self._native_private(
            "submit_broker_deposit_questionnaire",
            self._params(
                subAccountId=sub_account_id,
                depositId=deposit_id,
                questionnaire=dumps(questionnaire, separators=(",", ":"), allow_nan=False),
                beneficiaryPii=dumps(beneficiary_pii, separators=(",", ":"), allow_nan=False),
                network=network,
                coin=coin,
                amount=amount,
                address=address,
                addressTag=address_tag,
            ),
        )
