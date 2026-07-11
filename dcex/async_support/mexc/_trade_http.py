"""MEXC private trading async HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for MEXC private trading APIs."""

    async def test_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Validate a MEXC Spot order without placing it."""
        return await self._native_private(
            "test_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                price=price,
                timeInForce=timeInForce,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot order."""
        return await self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                price=price,
                timeInForce=timeInForce,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit order."""
        return await self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                price=price,
                timeInForce=timeInForce,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit buy order."""
        return await self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit sell order."""
        return await self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit order."""
        return await self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit buy order."""
        return await self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit sell order."""
        return await self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market order."""
        return await self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        quoteOrderQty: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market buy order by quote quantity."""
        return await self._native_private(
            "place_spot_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                quoteOrderQty=quoteOrderQty,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market sell order by base quantity."""
        return await self._native_private(
            "place_spot_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def place_spot_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place MEXC Spot batch orders."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(batchOrders=batchOrders, recvWindow=recvWindow),
        )

    async def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        origClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Spot order."""
        return await self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def cancel_spot_open_orders(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all MEXC Spot open orders for a symbol."""
        return await self._native_private(
            "cancel_spot_open_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    async def get_spot_order(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        origClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Spot order."""
        return await self._native_private(
            "get_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    async def get_spot_open_orders(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot open orders."""
        return await self._native_private(
            "get_spot_open_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    async def get_spot_all_orders(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Spot orders for a symbol."""
        return await self._native_private(
            "get_spot_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    async def get_spot_my_trades(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot account trade fills."""
        return await self._native_private(
            "get_spot_my_trades",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    async def place_contract_order(
        self,
        product_symbol: str,
        side: int,
        type_: int,
        openType: int,
        vol: int | str,
        price: str | None = None,
        leverage: int | None = None,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
        stopLossPrice: str | None = None,
        takeProfitPrice: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract order."""
        return await self._native_private(
            "place_contract_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                openType=openType,
                vol=vol,
                price=price,
                leverage=leverage,
                externalOid=externalOid,
                positionMode=positionMode,
                reduceOnly=reduceOnly,
                stopLossPrice=stopLossPrice,
                takeProfitPrice=takeProfitPrice,
            ),
        )

    async def place_contract_limit_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract limit order."""
        return await self._native_private(
            "place_contract_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                price=price,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_contract_limit_buy_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract limit buy order."""
        return await self._native_private(
            "place_contract_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                price=price,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
            ),
        )

    async def place_contract_limit_sell_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract limit sell order."""
        return await self._native_private(
            "place_contract_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                price=price,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
            ),
        )

    async def place_contract_post_only_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract post-only order."""
        return await self._native_private(
            "place_contract_post_only_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                price=price,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_contract_post_only_buy_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract post-only buy order."""
        return await self._native_private(
            "place_contract_post_only_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                price=price,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
            ),
        )

    async def place_contract_post_only_sell_order(
        self,
        product_symbol: str,
        price: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract post-only sell order."""
        return await self._native_private(
            "place_contract_post_only_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                price=price,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
            ),
        )

    async def place_contract_market_order(
        self,
        product_symbol: str,
        side: int,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market order."""
        return await self._native_private(
            "place_contract_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_contract_market_buy_order(
        self,
        product_symbol: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market buy order."""
        return await self._native_private(
            "place_contract_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
            ),
        )

    async def place_contract_market_sell_order(
        self,
        product_symbol: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market sell order."""
        return await self._native_private(
            "place_contract_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                vol=vol,
                leverage=leverage,
                openType=openType,
                externalOid=externalOid,
                positionMode=positionMode,
            ),
        )

    async def cancel_contract_orders(
        self,
        orders: list[str | int | dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Cancel MEXC Contract orders by order id list."""
        return await self._native_private(
            "cancel_contract_orders",
            self._native_params(orders=orders),
        )

    async def cancel_contract_order(self, order_id: str | int) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Contract order by order id."""
        return await self._native_private(
            "cancel_contract_order",
            self._native_params(order_id=order_id),
        )

    async def cancel_contract_order_with_external_id(
        self,
        product_symbol: str,
        externalOid: str,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Contract order by external order id."""
        return await self._native_private(
            "cancel_contract_order_with_external_id",
            self._native_params(product_symbol=product_symbol, externalOid=externalOid),
        )

    async def cancel_all_contract_orders(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Cancel all MEXC Contract orders for a symbol."""
        return await self._native_private(
            "cancel_all_contract_orders",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_contract_open_orders(
        self,
        product_symbol: str,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract open orders."""
        return await self._native_private(
            "get_contract_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_contract_history_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        category: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical orders."""
        return await self._native_private(
            "get_contract_history_orders",
            self._native_params(
                product_symbol=product_symbol,
                states=states,
                category=category,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_contract_order_by_external_id(
        self,
        product_symbol: str,
        external_oid: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract order by external order id."""
        return await self._native_private(
            "get_contract_order_by_external_id",
            self._native_params(product_symbol=product_symbol, external_oid=external_oid),
        )

    async def get_contract_order(self, order_id: str | int) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract order by order id."""
        return await self._native_private(
            "get_contract_order",
            self._native_params(order_id=order_id),
        )

    async def get_contract_orders(
        self,
        order_ids: list[str | int] | str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract orders by order ids."""
        return await self._native_private(
            "get_contract_orders",
            self._native_params(order_ids=order_ids),
        )

    async def get_contract_order_deal_details(
        self,
        order_id: str | int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract order deal details."""
        return await self._native_private(
            "get_contract_order_deal_details",
            self._native_params(order_id=order_id),
        )

    async def get_contract_order_deals(
        self,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract order deals."""
        return await self._native_private(
            "get_contract_order_deals",
            self._native_params(
                product_symbol=product_symbol,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def get_contract_plan_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract trigger orders."""
        return await self._native_private(
            "get_contract_plan_orders",
            self._native_params(
                product_symbol=product_symbol,
                states=states,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    async def place_contract_plan_order(
        self,
        product_symbol: str,
        vol: str,
        side: str,
        openType: str,
        triggerPrice: str,
        triggerType: str,
        executeCycle: str,
        orderType: str,
        trend: str,
        price: str | None = None,
        leverage: str | None = None,
        externalOid: str | None = None,
    ) -> dict[str, Any]:
        """Create an MEXC contract trigger plan order."""
        return await self._native_private(
            "place_contract_plan_order",
            self._native_params(
                product_symbol=product_symbol,
                vol=vol,
                side=side,
                openType=openType,
                triggerPrice=triggerPrice,
                triggerType=triggerType,
                executeCycle=executeCycle,
                orderType=orderType,
                trend=trend,
                price=price,
                leverage=leverage,
                externalOid=externalOid,
            ),
        )

    async def cancel_contract_plan_orders(self, orders: str) -> dict[str, Any]:
        """Cancel one or more MEXC contract trigger plan orders."""
        return await self._native_private(
            "cancel_contract_plan_orders", self._native_params(orders=orders)
        )

    async def cancel_all_contract_plan_orders(
        self, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Cancel all MEXC contract trigger plan orders, optionally for one contract."""
        return await self._native_private(
            "cancel_all_contract_plan_orders", self._native_params(product_symbol=product_symbol)
        )

    async def get_contract_stop_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract Stop-Limit orders."""
        return await self._native_private(
            "get_contract_stop_orders",
            self._native_params(
                product_symbol=product_symbol,
                states=states,
                page_num=page_num,
                page_size=page_size,
            ),
        )
