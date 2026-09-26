"""KuCoin trading HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for KuCoin spot and futures trading APIs."""

    def set_dcp(
        self,
        timeout: int,
        symbols: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Arm, refresh, or unset (timeout=-1) the spot disconnection protection.

        ``symbols`` lists up to 50 pairs; omitted or empty means all pairs.
        """
        return self._native_private(
            "set_dcp", self._native_params(timeout=timeout, symbols=symbols)
        )

    def get_dcp(self) -> dict[str, Any]:
        """Read the active spot disconnection protection settings."""
        return self._native_private("get_dcp", [])

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        size: str | None = None,
        funds: str | None = None,
        price: str | None = None,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str | None = None,
        cancelAfter: int | None = None,
        postOnly: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a new KuCoin spot order."""
        return self._native_private(
            "place_spot_order",
            self._native_params(**locals()),
        )

    def test_spot_order(
        self,
        product_symbol: str,
        side: str,
        type_: str,
        size: str | None = None,
        funds: str | None = None,
        price: str | None = None,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str | None = None,
        cancelAfter: int | None = None,
        postOnly: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Validate a spot order without entering the matching engine."""
        return self._native_private(
            "test_spot_order",
            self._native_params(**locals()),
        )

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str | None = None,
        funds: str | None = None,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot market order."""
        return self._native_private(
            "place_spot_market_order",
            self._native_params(**locals()),
        )

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        size: str | None = None,
        funds: str | None = None,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot market buy order."""
        return self._native_private(
            "place_spot_market_buy_order",
            self._native_params(**locals()),
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str | None = None,
        funds: str | None = None,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot market sell order."""
        return self._native_private(
            "place_spot_market_sell_order",
            self._native_params(**locals()),
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str = "GTC",
        cancelAfter: int | None = None,
        postOnly: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot limit order."""
        return self._native_private(
            "place_spot_limit_order",
            self._native_params(**locals()),
        )

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str = "GTC",
        cancelAfter: int | None = None,
        postOnly: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot limit buy order."""
        return self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(**locals()),
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str = "GTC",
        cancelAfter: int | None = None,
        postOnly: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot limit sell order."""
        return self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(**locals()),
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str = "GTC",
        cancelAfter: int | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot post-only limit order."""
        return self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(**locals()),
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str = "GTC",
        cancelAfter: int | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot post-only limit buy order."""
        return self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(**locals()),
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
        stp: str | None = None,
        tags: str | None = None,
        remark: str | None = None,
        timeInForce: str = "GTC",
        cancelAfter: int | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: str | None = None,
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin spot post-only limit sell order."""
        return self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(**locals()),
        )

    def place_spot_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch orders."""
        return self._native_private(
            "place_spot_batch_orders",
            self._native_params(orders=orders),
        )

    def place_spot_batch_limit_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch limit orders."""
        return self._native_private(
            "place_spot_batch_limit_orders",
            self._native_params(orders=orders),
        )

    def place_spot_batch_market_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch market orders."""
        return self._native_private(
            "place_spot_batch_market_orders",
            self._native_params(orders=orders),
        )

    def alter_spot_order(
        self,
        product_symbol: str,
        orderId: str | None = None,  # noqa: N803
        clientOid: str | None = None,  # noqa: N803
        newPrice: str | None = None,  # noqa: N803
        newSize: str | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Cancel and replace the specified spot order with a new price or size."""
        return self._native_private("alter_spot_order", self._native_params(**locals()))

    def cancel_spot_order(self, orderId: str, product_symbol: str) -> dict[str, Any]:
        """Cancel a KuCoin spot order."""
        return self._native_private(
            "cancel_spot_order",
            self._native_params(orderId=orderId, product_symbol=product_symbol),
        )

    def cancel_spot_all_orders_by_symbol(self, product_symbol: str) -> dict[str, Any]:
        """Cancel all KuCoin spot orders for one symbol."""
        return self._native_private(
            "cancel_spot_all_orders_by_symbol",
            self._native_params(product_symbol=product_symbol),
        )

    def cancel_spot_all_orders(self) -> dict[str, Any]:
        """Cancel all KuCoin spot open orders."""
        return self._native_private("cancel_spot_all_orders", [])

    def get_spot_open_orders(
        self,
        product_symbol: str,
        pageNum: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve a page of KuCoin spot open orders."""
        return self._native_private(
            "get_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                pageNum=pageNum,
                pageSize=pageSize,
            ),
        )

    def get_spot_trade_history(
        self,
        product_symbol: str,
        orderId: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        lastId: int | None = None,
        startAt: int | None = None,
        endAt: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin spot trade history."""
        return self._native_private(
            "get_spot_trade_history",
            self._native_params(**locals()),
        )

    def place_futures_order(
        self,
        product_symbol: str,
        side: str | None = None,
        type_: str = "limit",
        size: int | str | None = None,
        price: str | None = None,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        timeInForce: str | None = None,
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
        closeOrder: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: int | str | None = None,
        stop: str | None = None,
        stopPriceType: str | None = None,
        stopPrice: str | None = None,
        stp: str | None = None,
        remark: str | None = None,
        qty: str | None = None,
        valueQty: str | None = None,
        forceHold: bool | None = None,
    ) -> dict[str, Any]:
        """Place a new KuCoin futures order."""
        return self._native_private(
            "place_futures_order",
            self._native_params(**locals()),
        )

    def test_futures_order(
        self,
        product_symbol: str,
        side: str | None = None,
        type_: str = "limit",
        size: int | str | None = None,
        price: str | None = None,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        timeInForce: str | None = None,
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
        closeOrder: bool | None = None,
        hidden: bool | None = None,
        iceberg: bool | None = None,
        visibleSize: int | str | None = None,
        stop: str | None = None,
        stopPriceType: str | None = None,
        stopPrice: str | None = None,
        stp: str | None = None,
        remark: str | None = None,
        qty: str | None = None,
        valueQty: str | None = None,
        forceHold: bool | None = None,
    ) -> dict[str, Any]:
        """Validate a futures order without entering the matching engine."""
        return self._native_private(
            "test_futures_order",
            self._native_params(**locals()),
        )

    def place_futures_market_order(
        self,
        product_symbol: str,
        side: str | None = None,
        size: int | str | None = None,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        reduceOnly: bool | None = None,
        closeOrder: bool | None = None,
        qty: str | None = None,
        valueQty: str | None = None,
        forceHold: bool | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures market order."""
        return self._native_private(
            "place_futures_market_order",
            self._native_params(**locals()),
        )

    def place_futures_market_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures market buy order."""
        return self._native_private(
            "place_futures_market_buy_order",
            self._native_params(**locals()),
        )

    def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures market sell order."""
        return self._native_private(
            "place_futures_market_sell_order",
            self._native_params(**locals()),
        )

    def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        timeInForce: str = "GTC",
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures limit order."""
        return self._native_private(
            "place_futures_limit_order",
            self._native_params(**locals()),
        )

    def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        timeInForce: str = "GTC",
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures limit buy order."""
        return self._native_private(
            "place_futures_limit_buy_order",
            self._native_params(**locals()),
        )

    def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
        timeInForce: str = "GTC",
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures limit sell order."""
        return self._native_private(
            "place_futures_limit_sell_order",
            self._native_params(**locals()),
        )

    def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: int | str,
        price: str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures post-only limit order."""
        return self._native_private(
            "place_futures_post_only_limit_order",
            self._native_params(**locals()),
        )

    def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures post-only limit buy order."""
        return self._native_private(
            "place_futures_post_only_limit_buy_order",
            self._native_params(**locals()),
        )

    def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int | str,
        price: str,
        clientOid: str | None = None,
        leverage: int | str | None = None,
        marginMode: str | None = None,
        positionSide: str | None = None,
    ) -> dict[str, Any]:
        """Place a KuCoin futures post-only limit sell order."""
        return self._native_private(
            "place_futures_post_only_limit_sell_order",
            self._native_params(**locals()),
        )

    def get_futures_order_list(
        self,
        product_symbol: str | None = None,
        status: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        startAt: int | None = None,
        endAt: int | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures order list."""
        return self._native_private(
            "get_futures_order_list",
            self._native_params(**locals()),
        )

    def get_futures_order(self, orderId: str) -> dict[str, Any]:
        """Retrieve a KuCoin futures order by order ID."""
        return self._native_private(
            "get_futures_order",
            self._native_params(orderId=orderId),
        )

    def get_futures_order_by_client_oid(
        self,
        clientOid: str,
    ) -> dict[str, Any]:
        """Retrieve a KuCoin futures order by client order ID."""
        return self._native_private(
            "get_futures_order_by_client_oid",
            self._native_params(clientOid=clientOid),
        )

    def cancel_futures_order(self, orderId: str) -> dict[str, Any]:
        """Cancel a KuCoin futures order by order ID."""
        return self._native_private(
            "cancel_futures_order",
            self._native_params(orderId=orderId),
        )

    def cancel_futures_order_by_client_oid(
        self,
        clientOid: str,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Cancel a KuCoin futures order by client order ID."""
        return self._native_private(
            "cancel_futures_order_by_client_oid",
            self._native_params(clientOid=clientOid, product_symbol=product_symbol),
        )

    def cancel_futures_all_orders(self, product_symbol: str) -> dict[str, Any]:
        """Cancel KuCoin futures open orders."""
        return self._native_private(
            "cancel_futures_all_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_open_order_value(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures open order value."""
        return self._native_private(
            "get_futures_open_order_value",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_trade_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        tradeTypes: str | None = None,
        startAt: int | None = None,
        endAt: int | None = None,
        currentPage: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures fills."""
        return self._native_private(
            "get_futures_trade_history",
            self._native_params(**locals()),
        )

    def get_futures_recent_trade_history(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve recent KuCoin futures fills."""
        return self._native_private(
            "get_futures_recent_trade_history",
            self._native_params(product_symbol=product_symbol),
        )

    def place_uta_order(
        self,
        trade_type: str,
        product_symbol: str,
        side: str,
        order_type: str,
        size: str,
        *,
        size_unit: str,
        price: str | None = None,
        client_oid: str | None = None,
        time_in_force: str | None = None,
        margin_mode: str | None = None,
        position_side: str | None = None,
        leverage: str | None = None,
        post_only: bool | None = None,
        reduce_only: bool | None = None,
        trigger_direction: str | None = None,
        trigger_price_type: str | None = None,
        trigger_price: str | None = None,
        stp: str | None = None,
        cancel_after: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a KuCoin UTA V2 spot, margin, or futures order.

        ``size_unit`` is required by KuCoin: ``BASECCY`` or ``QUOTECCY`` (spot
        market), ``BASECCY`` (spot limit), ``BASECCY`` or ``UNIT`` (futures).
        """
        return self._native_private(
            "place_uta_order",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                side=side,
                orderType=order_type,
                size=size,
                price=price,
                sizeUnit=size_unit,
                clientOid=client_oid,
                timeInForce=time_in_force,
                marginMode=margin_mode,
                positionSide=position_side,
                leverage=leverage,
                postOnly=post_only,
                reduceOnly=reduce_only,
                triggerDirection=trigger_direction,
                triggerPriceType=trigger_price_type,
                triggerPrice=trigger_price,
                stp=stp,
                cancelAfter=cancel_after,
            ),
        )

    def cancel_uta_order(
        self,
        trade_type: str,
        product_symbol: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a KuCoin UTA V2 order by exactly one identifier."""
        return self._native_private(
            "cancel_uta_order",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderId=order_id,
                clientOid=client_oid,
            ),
        )

    def amend_uta_order(
        self,
        product_symbol: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        new_price: str | None = None,
        new_size: str | None = None,
        size_unit: str | None = None,
        cxl_on_fail: bool | None = None,
        tp_trigger_price: str | None = None,
        tp_trigger_price_type: str | None = None,
        sl_trigger_price: str | None = None,
        sl_trigger_price_type: str | None = None,
    ) -> dict[str, Any]:
        """Amend a KuCoin UTA V2 futures order (KuCoin supports futures only)."""
        return self._native_private(
            "amend_uta_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=order_id,
                clientOid=client_oid,
                newPrice=new_price,
                newSize=new_size,
                sizeUnit=size_unit,
                cxlOnFail=cxl_on_fail,
                tpTriggerPrice=tp_trigger_price,
                tpTriggerPriceType=tp_trigger_price_type,
                slTriggerPrice=sl_trigger_price,
                slTriggerPriceType=sl_trigger_price_type,
            ),
        )

    def get_uta_order_detail(
        self,
        trade_type: str,
        product_symbol: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Look up one KuCoin UTA V2 order."""
        return self._native_private(
            "get_uta_order_detail",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderId=order_id,
                clientOid=client_oid,
            ),
        )

    def get_uta_open_orders(
        self,
        trade_type: str,
        *,
        product_symbol: str | None = None,
        order_filter: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """List KuCoin UTA V2 open orders."""
        return self._native_private(
            "get_uta_open_orders",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderFilter=order_filter,
                pageNumber=page_number,
                pageSize=page_size,
            ),
        )

    def get_uta_order_history(
        self,
        trade_type: str,
        *,
        product_symbol: str | None = None,
        side: str | None = None,
        order_filter: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """List KuCoin UTA V2 order history."""
        return self._native_private(
            "get_uta_order_history",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                side=side,
                orderFilter=order_filter,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                pageSize=page_size,
            ),
        )

    def get_uta_trade_history(
        self,
        trade_type: str,
        *,
        product_symbol: str | None = None,
        order_id: str | None = None,
        side: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """List KuCoin UTA V2 executions."""
        return self._native_private(
            "get_uta_trade_history",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderId=order_id,
                side=side,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                pageSize=page_size,
            ),
        )
