"""MEXC private trading HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for MEXC private trading APIs."""

    def test_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Validate a MEXC Spot order without placing it."""
        return self._native_private(
            "test_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot order."""
        return self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit order."""
        return self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit buy order."""
        return self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot limit sell order."""
        return self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit order."""
        return self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit buy order."""
        return self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot post-only limit sell order."""
        return self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                price=price,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market order."""
        return self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        quoteOrderQty: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market buy order by quote quantity."""
        return self._native_private(
            "place_spot_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                quoteOrderQty=quoteOrderQty,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        quantity: str,
        newClientOrderId: str | None = None,
        stpMode: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Spot market sell order by base quantity."""
        return self._native_private(
            "place_spot_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                quantity=quantity,
                newClientOrderId=newClientOrderId,
                stpMode=stpMode,
                recvWindow=recvWindow,
            ),
        )

    def place_spot_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place MEXC Spot batch orders."""
        return self._native_private(
            "place_spot_batch_orders",
            self._native_params(batchOrders=batchOrders, recvWindow=recvWindow),
        )

    def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        origClientOrderId: str | None = None,
        newClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Spot order."""
        return self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                newClientOrderId=newClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    def cancel_spot_open_orders(
        self,
        product_symbol: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all MEXC Spot open orders for a symbol."""
        return self._native_private(
            "cancel_spot_open_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    def get_spot_order(
        self,
        product_symbol: str | None = None,
        orderId: str | int | None = None,
        origClientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Spot order."""
        return self._native_private(
            "get_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                recvWindow=recvWindow,
            ),
        )

    def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot open orders."""
        return self._native_private(
            "get_spot_open_orders",
            self._native_params(product_symbol=product_symbol, recvWindow=recvWindow),
        )

    def get_spot_all_orders(
        self,
        product_symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve all MEXC Spot orders for a symbol."""
        return self._native_private(
            "get_spot_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                recvWindow=recvWindow,
            ),
        )

    def get_spot_my_trades(
        self,
        product_symbol: str,
        orderId: str | int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot account trade fills."""
        return self._native_private(
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

    def place_contract_order(
        self,
        product_symbol: str,
        side: int,
        type_: int,
        openType: int,
        vol: int | str,
        price: str | None = None,
        leverage: int | None = None,
        externalOid: str | None = None,
        positionId: int | None = None,
        positionMode: int | None = None,
        reduceOnly: bool | None = None,
        stopLossPrice: str | None = None,
        takeProfitPrice: str | None = None,
        lossTrend: int | None = None,
        profitTrend: int | None = None,
        priceProtect: int | None = None,
        marketCeiling: bool | None = None,
        flashClose: bool | None = None,
        bboTypeNum: int | None = None,
        stpMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract order."""
        return self._native_private(
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
                positionId=positionId,
                positionMode=positionMode,
                reduceOnly=reduceOnly,
                stopLossPrice=stopLossPrice,
                takeProfitPrice=takeProfitPrice,
                lossTrend=lossTrend,
                profitTrend=profitTrend,
                priceProtect=priceProtect,
                marketCeiling=marketCeiling,
                flashClose=flashClose,
                bboTypeNum=bboTypeNum,
                stpMode=stpMode,
            ),
        )

    def place_contract_limit_order(
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
        return self._native_private(
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

    def place_contract_limit_buy_order(
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
        return self._native_private(
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

    def place_contract_limit_sell_order(
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
        return self._native_private(
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

    def place_contract_post_only_order(
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
        return self._native_private(
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

    def place_contract_post_only_buy_order(
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
        return self._native_private(
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

    def place_contract_post_only_sell_order(
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
        return self._native_private(
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

    def place_contract_market_order(
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
        return self._native_private(
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

    def place_contract_market_buy_order(
        self,
        product_symbol: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market buy order."""
        return self._native_private(
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

    def place_contract_market_sell_order(
        self,
        product_symbol: str,
        vol: int | str,
        leverage: int | None = 50,
        openType: int = 2,
        externalOid: str | None = None,
        positionMode: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place a MEXC Contract market sell order."""
        return self._native_private(
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

    def cancel_contract_orders(
        self,
        orders: list[str | int | dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Cancel MEXC Contract orders by order id list."""
        return self._native_private(
            "cancel_contract_orders",
            self._native_params(orders=orders),
        )

    def cancel_contract_order(self, order_id: str | int) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Contract order by order id."""
        return self._native_private(
            "cancel_contract_order",
            self._native_params(order_id=order_id),
        )

    def cancel_contract_order_with_external_id(
        self,
        product_symbol: str,
        externalOid: str,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a MEXC Contract order by external order id."""
        return self._native_private(
            "cancel_contract_order_with_external_id",
            self._native_params(product_symbol=product_symbol, externalOid=externalOid),
        )

    def cancel_all_contract_orders(
        self, product_symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Cancel all MEXC Contract orders for a symbol."""
        return self._native_private(
            "cancel_all_contract_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_open_orders(
        self,
        product_symbol: str | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract open orders."""
        return self._native_private(
            "get_contract_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_contract_history_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        category: int | None = None,
        orderId: str | int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical orders."""
        return self._native_private(
            "get_contract_history_orders",
            self._native_params(
                product_symbol=product_symbol,
                states=states,
                category=category,
                orderId=orderId,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_contract_order_by_external_id(
        self,
        product_symbol: str,
        external_oid: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract order by external order id."""
        return self._native_private(
            "get_contract_order_by_external_id",
            self._native_params(product_symbol=product_symbol, external_oid=external_oid),
        )

    def get_contract_order(self, order_id: str | int) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract order by order id."""
        return self._native_private(
            "get_contract_order",
            self._native_params(order_id=order_id),
        )

    def get_contract_orders(self, order_ids: list[str | int] | str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract orders by order ids."""
        return self._native_private(
            "get_contract_orders",
            self._native_params(order_ids=order_ids),
        )

    def get_contract_order_deal_details(
        self,
        order_id: str | int,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract order deal details."""
        return self._native_private(
            "get_contract_order_deal_details",
            self._native_params(order_id=order_id),
        )

    def get_contract_order_deals(
        self,
        product_symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract order deals."""
        return self._native_private(
            "get_contract_order_deals",
            self._native_params(
                product_symbol=product_symbol,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_contract_plan_orders(
        self,
        product_symbol: str | None = None,
        states: str | None = None,
        side: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract trigger orders."""
        return self._native_private(
            "get_contract_plan_orders",
            self._native_params(
                product_symbol=product_symbol,
                states=states,
                side=side,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def place_contract_plan_order(
        self,
        product_symbol: str,
        vol: str,
        leverage: str,
        side: str,
        openType: str,
        triggerPrice: str,
        triggerType: str,
        executeCycle: str,
        orderType: str,
        trend: str,
        price: str | None = None,
        externalOid: str | None = None,
        priceProtect: int | None = None,
        positionMode: int | None = None,
        lossTrend: int | None = None,
        profitTrend: int | None = None,
        stopLossPrice: str | None = None,
        takeProfitPrice: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Create an MEXC contract trigger plan order."""
        return self._native_private(
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
                priceProtect=priceProtect,
                positionMode=positionMode,
                lossTrend=lossTrend,
                profitTrend=profitTrend,
                stopLossPrice=stopLossPrice,
                takeProfitPrice=takeProfitPrice,
                reduceOnly=reduceOnly,
            ),
        )

    def cancel_contract_plan_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel one or more MEXC contract trigger plan orders."""
        return self._native_private(
            "cancel_contract_plan_orders", self._native_params(orders=orders)
        )

    def cancel_all_contract_plan_orders(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Cancel all MEXC contract trigger plan orders, optionally for one contract."""
        return self._native_private(
            "cancel_all_contract_plan_orders", self._native_params(product_symbol=product_symbol)
        )

    def get_contract_stop_orders(
        self,
        product_symbol: str | None = None,
        is_finished: int | None = None,
        state: int | None = None,
        type_: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract Stop-Limit orders."""
        return self._native_private(
            "get_contract_stop_orders",
            self._native_params(
                product_symbol=product_symbol,
                is_finished=is_finished,
                state=state,
                type_=type_,
                start_time=start_time,
                end_time=end_time,
                page_num=page_num,
                page_size=page_size,
            ),
        )
