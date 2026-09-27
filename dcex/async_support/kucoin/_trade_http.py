"""KuCoin async trading HTTP client backed by Rust."""

import json
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for KuCoin spot and futures trading APIs."""

    async def set_dcp(
        self,
        timeout: int,  # noqa: ASYNC109
        symbols: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Arm, refresh, or unset (timeout=-1) the spot disconnection protection.

        ``symbols`` lists up to 50 pairs; omitted or empty means all pairs.
        """
        return await self._native_private(
            "set_dcp", self._native_params(timeout=timeout, symbols=symbols)
        )

    async def get_dcp(self) -> dict[str, Any]:
        """Read the active spot disconnection protection settings."""
        return await self._native_private("get_dcp", [])

    async def place_spot_order(
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
        return await self._native_private(
            "place_spot_order",
            self._native_params(**locals()),
        )

    async def test_spot_order(
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
        return await self._native_private(
            "test_spot_order",
            self._native_params(**locals()),
        )

    async def place_spot_market_order(
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
        return await self._native_private(
            "place_spot_market_order",
            self._native_params(**locals()),
        )

    async def place_spot_market_buy_order(
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
        return await self._native_private(
            "place_spot_market_buy_order",
            self._native_params(**locals()),
        )

    async def place_spot_market_sell_order(
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
        return await self._native_private(
            "place_spot_market_sell_order",
            self._native_params(**locals()),
        )

    async def place_spot_limit_order(
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
        return await self._native_private(
            "place_spot_limit_order",
            self._native_params(**locals()),
        )

    async def place_spot_limit_buy_order(
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
        return await self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(**locals()),
        )

    async def place_spot_limit_sell_order(
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
        return await self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(**locals()),
        )

    async def place_spot_post_only_limit_order(
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
        return await self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(**locals()),
        )

    async def place_spot_post_only_limit_buy_order(
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
        return await self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(**locals()),
        )

    async def place_spot_post_only_limit_sell_order(
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
        return await self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(**locals()),
        )

    async def place_spot_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch orders."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(orders=orders),
        )

    async def place_spot_batch_limit_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch limit orders."""
        return await self._native_private(
            "place_spot_batch_limit_orders",
            self._native_params(orders=orders),
        )

    async def place_spot_batch_market_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place KuCoin spot batch market orders."""
        return await self._native_private(
            "place_spot_batch_market_orders",
            self._native_params(orders=orders),
        )

    async def alter_spot_order(
        self,
        product_symbol: str,
        orderId: str | None = None,  # noqa: N803
        clientOid: str | None = None,  # noqa: N803
        newPrice: str | None = None,  # noqa: N803
        newSize: str | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Cancel and replace the specified spot order with a new price or size."""
        return await self._native_private("alter_spot_order", self._native_params(**locals()))

    async def cancel_spot_order(self, orderId: str, product_symbol: str) -> dict[str, Any]:
        """Cancel a KuCoin spot order."""
        return await self._native_private(
            "cancel_spot_order",
            self._native_params(orderId=orderId, product_symbol=product_symbol),
        )

    async def cancel_spot_all_orders_by_symbol(self, product_symbol: str) -> dict[str, Any]:
        """Cancel all KuCoin spot orders for one symbol."""
        return await self._native_private(
            "cancel_spot_all_orders_by_symbol",
            self._native_params(product_symbol=product_symbol),
        )

    async def cancel_spot_all_orders(self) -> dict[str, Any]:
        """Cancel all KuCoin spot open orders."""
        return await self._native_private("cancel_spot_all_orders", [])

    async def get_spot_open_orders(
        self,
        product_symbol: str,
        pageNum: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve a page of KuCoin spot open orders."""
        return await self._native_private(
            "get_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                pageNum=pageNum,
                pageSize=pageSize,
            ),
        )

    async def get_spot_trade_history(
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
        return await self._native_private(
            "get_spot_trade_history",
            self._native_params(**locals()),
        )

    async def place_futures_order(
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
        return await self._native_private(
            "place_futures_order",
            self._native_params(**locals()),
        )

    async def test_futures_order(
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
        return await self._native_private(
            "test_futures_order",
            self._native_params(**locals()),
        )

    async def place_futures_market_order(
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
        return await self._native_private(
            "place_futures_market_order",
            self._native_params(**locals()),
        )

    async def place_futures_market_buy_order(
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
        return await self._native_private(
            "place_futures_market_buy_order",
            self._native_params(**locals()),
        )

    async def place_futures_market_sell_order(
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
        return await self._native_private(
            "place_futures_market_sell_order",
            self._native_params(**locals()),
        )

    async def place_futures_limit_order(
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
        return await self._native_private(
            "place_futures_limit_order",
            self._native_params(**locals()),
        )

    async def place_futures_limit_buy_order(
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
        return await self._native_private(
            "place_futures_limit_buy_order",
            self._native_params(**locals()),
        )

    async def place_futures_limit_sell_order(
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
        return await self._native_private(
            "place_futures_limit_sell_order",
            self._native_params(**locals()),
        )

    async def place_futures_post_only_limit_order(
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
        return await self._native_private(
            "place_futures_post_only_limit_order",
            self._native_params(**locals()),
        )

    async def place_futures_post_only_limit_buy_order(
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
        return await self._native_private(
            "place_futures_post_only_limit_buy_order",
            self._native_params(**locals()),
        )

    async def place_futures_post_only_limit_sell_order(
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
        return await self._native_private(
            "place_futures_post_only_limit_sell_order",
            self._native_params(**locals()),
        )

    async def get_futures_order_list(
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
        return await self._native_private(
            "get_futures_order_list",
            self._native_params(**locals()),
        )

    async def get_futures_order(self, orderId: str) -> dict[str, Any]:
        """Retrieve a KuCoin futures order by order ID."""
        return await self._native_private(
            "get_futures_order",
            self._native_params(orderId=orderId),
        )

    async def get_futures_order_by_client_oid(
        self,
        clientOid: str,
    ) -> dict[str, Any]:
        """Retrieve a KuCoin futures order by client order ID."""
        return await self._native_private(
            "get_futures_order_by_client_oid",
            self._native_params(clientOid=clientOid),
        )

    async def cancel_futures_order(self, orderId: str) -> dict[str, Any]:
        """Cancel a KuCoin futures order by order ID."""
        return await self._native_private(
            "cancel_futures_order",
            self._native_params(orderId=orderId),
        )

    async def cancel_futures_order_by_client_oid(
        self,
        clientOid: str,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Cancel a KuCoin futures order by client order ID."""
        return await self._native_private(
            "cancel_futures_order_by_client_oid",
            self._native_params(clientOid=clientOid, product_symbol=product_symbol),
        )

    async def cancel_futures_all_orders(self, product_symbol: str) -> dict[str, Any]:
        """Cancel KuCoin futures open orders."""
        return await self._native_private(
            "cancel_futures_all_orders",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_open_order_value(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures open order value."""
        return await self._native_private(
            "get_futures_open_order_value",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_trade_history(
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
        return await self._native_private(
            "get_futures_trade_history",
            self._native_params(**locals()),
        )

    async def get_futures_recent_trade_history(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve recent KuCoin futures fills."""
        return await self._native_private(
            "get_futures_recent_trade_history",
            self._native_params(product_symbol=product_symbol),
        )

    async def place_uta_order(
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
        return await self._native_private(
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

    async def cancel_uta_order(
        self,
        trade_type: str,
        product_symbol: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a KuCoin UTA V2 order by exactly one identifier."""
        return await self._native_private(
            "cancel_uta_order",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderId=order_id,
                clientOid=client_oid,
            ),
        )

    async def amend_uta_order(
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
        return await self._native_private(
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

    async def get_uta_order_detail(
        self,
        trade_type: str,
        product_symbol: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Look up one KuCoin UTA V2 order."""
        return await self._native_private(
            "get_uta_order_detail",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderId=order_id,
                clientOid=client_oid,
            ),
        )

    async def get_uta_open_orders(
        self,
        trade_type: str,
        *,
        product_symbol: str | None = None,
        order_filter: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """List KuCoin UTA V2 open orders."""
        return await self._native_private(
            "get_uta_open_orders",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderFilter=order_filter,
                pageNumber=page_number,
                pageSize=page_size,
            ),
        )

    async def get_uta_order_history(
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
        return await self._native_private(
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

    async def get_uta_trade_history(
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
        return await self._native_private(
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

    async def batch_cancel_uta_orders(
        self,
        trade_type: str,
        cancel_order_list: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Cancel 1 to 20 UTA orders; each item needs symbol and orderId or clientOid."""
        return await self._native_private(
            "batch_cancel_uta_orders",
            self._native_params(
                tradeType=trade_type,
                cancelOrderList=json.dumps(cancel_order_list),
            ),
        )

    async def cancel_uta_orders_by_symbol(
        self,
        trade_type: str,
        product_symbol: str,
        order_filter: str,
        *,
        margin_mode: str | None = None,
    ) -> dict[str, Any]:
        """Cancel UTA orders for a symbol and NORMAL or ADVANCED order filter."""
        return await self._native_private(
            "cancel_uta_orders_by_symbol",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                orderFilter=order_filter,
                marginMode=margin_mode,
            ),
        )

    async def get_uta_margin_mode(
        self,
        *,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Query UTA futures margin modes."""
        return await self._native_private(
            "get_uta_margin_mode",
            self._native_params(
                product_symbol=product_symbol,
            ),
        )

    async def set_uta_margin_mode(
        self,
        product_symbol: str,
        margin_mode: str,
    ) -> dict[str, Any]:
        """Set CROSS or ISOLATED margin mode for a UTA futures symbol."""
        return await self._native_private(
            "set_uta_margin_mode",
            self._native_params(
                product_symbol=product_symbol,
                marginMode=margin_mode,
            ),
        )

    async def modify_uta_position_margin(
        self,
        product_symbol: str,
        type_: str,
        amount: str,
    ) -> dict[str, Any]:
        """Add (DEPOSIT) or reduce (WITHDRAW) isolated UTA futures position margin."""
        return await self._native_private(
            "modify_uta_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                type=type_,
                amount=amount,
            ),
        )

    async def get_uta_max_order_quantity(
        self,
        trade_type: str,
        product_symbol: str,
        *,
        price: str | None = None,
    ) -> dict[str, Any]:
        """Query maximum UTA buy and sell size at an optional order price."""
        return await self._native_private(
            "get_uta_max_order_quantity",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                price=price,
            ),
        )

    async def get_uta_leverage(
        self,
        trade_type: str,
        *,
        product_symbol: str | None = None,
        currency: str | None = None,
        margin_mode: str | None = None,
    ) -> dict[str, Any]:
        """Query UTA leverage for FUTURES or MARGIN."""
        return await self._native_private(
            "get_uta_leverage",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                currency=currency,
                marginMode=margin_mode,
            ),
        )

    async def modify_uta_futures_leverage(
        self,
        product_symbol: str,
        leverage: str,
    ) -> dict[str, Any]:
        """Modify UTA futures leverage."""
        return await self._native_private(
            "modify_uta_futures_leverage",
            self._native_params(
                product_symbol=product_symbol,
                leverage=leverage,
            ),
        )

    async def modify_uta_cross_margin_leverage(
        self,
        leverage: str,
        *,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Modify UTA cross margin leverage for an optional currency."""
        return await self._native_private(
            "modify_uta_cross_margin_leverage",
            self._native_params(
                leverage=leverage,
                currency=currency,
            ),
        )

    async def get_uta_position_history(
        self,
        *,
        product_symbol: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve UTA position history with cursor pagination."""
        return await self._native_private(
            "get_uta_position_history",
            self._native_params(
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                pageSize=page_size,
            ),
        )

    async def get_uta_funding_history(
        self,
        *,
        product_symbol: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve UTA private funding fee history with cursor pagination."""
        return await self._native_private(
            "get_uta_funding_history",
            self._native_params(
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                pageSize=page_size,
            ),
        )

    async def cancel_spot_order_by_client_oid(
        self, product_symbol: str, client_oid: str
    ) -> dict[str, Any]:
        """DELETE /api/v1/hf/orders/client-order/{clientOid}; classic trading account."""
        return await self._native_private(
            "cancel_spot_order_by_client_oid",
            self._native_params(product_symbol=product_symbol, clientOid=client_oid),
        )

    async def cancel_spot_partial_order(
        self, product_symbol: str, cancel_size: str, order_id: str
    ) -> dict[str, Any]:
        """DELETE /api/v1/hf/orders/cancel/{orderId}; classic trading account."""
        return await self._native_private(
            "cancel_spot_partial_order",
            self._native_params(
                product_symbol=product_symbol, cancelSize=cancel_size, orderId=order_id
            ),
        )

    async def get_spot_order(self, product_symbol: str, order_id: str) -> dict[str, Any]:
        """GET /api/v1/hf/orders/{orderId}; classic trading account."""
        return await self._native_private(
            "get_spot_order", self._native_params(product_symbol=product_symbol, orderId=order_id)
        )

    async def get_spot_order_by_client_oid(
        self, product_symbol: str, client_oid: str
    ) -> dict[str, Any]:
        """GET /api/v1/hf/orders/client-order/{clientOid}; classic trading account."""
        return await self._native_private(
            "get_spot_order_by_client_oid",
            self._native_params(product_symbol=product_symbol, clientOid=client_oid),
        )

    async def get_spot_active_order_symbols(self) -> dict[str, Any]:
        """GET /api/v1/hf/orders/active/symbols; classic trading account."""
        return await self._native_private("get_spot_active_order_symbols", self._native_params())

    async def get_spot_active_orders(self, product_symbol: str) -> dict[str, Any]:
        """GET /api/v1/hf/orders/active; classic trading account."""
        return await self._native_private(
            "get_spot_active_orders", self._native_params(product_symbol=product_symbol)
        )

    async def get_spot_closed_orders(
        self,
        product_symbol: str,
        *,
        side: str | None = None,
        type_: str | None = None,
        last_id: int | None = None,
        limit: int | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v1/hf/orders/done; classic trading account."""
        return await self._native_private(
            "get_spot_closed_orders",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type=type_,
                lastId=last_id,
                limit=limit,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def place_spot_stop_order(
        self,
        side: str,
        product_symbol: str,
        type_: str,
        stop_price: str,
        *,
        client_oid: str | None = None,
        remark: str | None = None,
        stp: str | None = None,
        price: str | None = None,
        size: str | None = None,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        cancel_after: int | None = None,
        funds: str | None = None,
        trade_type: str | None = None,
        stop: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/v1/stop-order; classic trading account."""
        return await self._native_private(
            "place_spot_stop_order",
            self._native_params(
                side=side,
                product_symbol=product_symbol,
                type=type_,
                stopPrice=stop_price,
                clientOid=client_oid,
                remark=remark,
                stp=stp,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                cancelAfter=cancel_after,
                funds=funds,
                tradeType=trade_type,
                stop=stop,
            ),
        )

    async def cancel_spot_stop_order_by_client_oid(
        self, client_oid: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """DELETE /api/v1/stop-order/cancelOrderByClientOid; classic trading account."""
        return await self._native_private(
            "cancel_spot_stop_order_by_client_oid",
            self._native_params(clientOid=client_oid, product_symbol=product_symbol),
        )

    async def cancel_spot_stop_order(self, order_id: str) -> dict[str, Any]:
        """DELETE /api/v1/stop-order/{orderId}; classic trading account."""
        return await self._native_private(
            "cancel_spot_stop_order", self._native_params(orderId=order_id)
        )

    async def cancel_spot_stop_orders(
        self,
        *,
        product_symbol: str | None = None,
        trade_type: str | None = None,
        order_ids: str | None = None,
    ) -> dict[str, Any]:
        """DELETE /api/v1/stop-order/cancel; classic trading account."""
        return await self._native_private(
            "cancel_spot_stop_orders",
            self._native_params(
                product_symbol=product_symbol, tradeType=trade_type, orderIds=order_ids
            ),
        )

    async def get_spot_stop_orders(
        self,
        *,
        product_symbol: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        trade_type: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        order_ids: str | None = None,
        page_size: int | None = None,
        stop: str | None = None,
    ) -> dict[str, Any]:
        """GET /api/v1/stop-order; classic trading account."""
        return await self._native_private(
            "get_spot_stop_orders",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type=type_,
                tradeType=trade_type,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                orderIds=order_ids,
                pageSize=page_size,
                stop=stop,
            ),
        )

    async def get_spot_stop_order(self, order_id: str) -> dict[str, Any]:
        """GET /api/v1/stop-order/{orderId}; classic trading account."""
        return await self._native_private(
            "get_spot_stop_order", self._native_params(orderId=order_id)
        )

    async def place_spot_oco_order(
        self,
        client_oid: str,
        side: str,
        product_symbol: str,
        price: str,
        size: str,
        stop_price: str,
        limit_price: str,
        *,
        remark: str | None = None,
        trade_type: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/v3/oco/order; classic trading account."""
        return await self._native_private(
            "place_spot_oco_order",
            self._native_params(
                clientOid=client_oid,
                side=side,
                product_symbol=product_symbol,
                price=price,
                size=size,
                stopPrice=stop_price,
                limitPrice=limit_price,
                remark=remark,
                tradeType=trade_type,
            ),
        )

    async def cancel_spot_oco_order(self, order_id: str) -> dict[str, Any]:
        """DELETE /api/v3/oco/order/{orderId}; classic trading account."""
        return await self._native_private(
            "cancel_spot_oco_order", self._native_params(orderId=order_id)
        )

    async def cancel_spot_oco_order_by_client_oid(self, client_oid: str) -> dict[str, Any]:
        """DELETE /api/v3/oco/client-order/{clientOid}; classic trading account."""
        return await self._native_private(
            "cancel_spot_oco_order_by_client_oid", self._native_params(clientOid=client_oid)
        )

    async def cancel_spot_oco_orders(
        self, *, order_ids: str | None = None, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """DELETE /api/v3/oco/orders; classic trading account."""
        return await self._native_private(
            "cancel_spot_oco_orders",
            self._native_params(orderIds=order_ids, product_symbol=product_symbol),
        )

    async def get_spot_oco_order(self, order_id: str) -> dict[str, Any]:
        """GET /api/v3/oco/order/{orderId}; classic trading account."""
        return await self._native_private(
            "get_spot_oco_order", self._native_params(orderId=order_id)
        )

    async def get_spot_oco_order_by_client_oid(self, client_oid: str) -> dict[str, Any]:
        """GET /api/v3/oco/client-order/{clientOid}; classic trading account."""
        return await self._native_private(
            "get_spot_oco_order_by_client_oid", self._native_params(clientOid=client_oid)
        )

    async def get_spot_oco_order_details(self, order_id: str) -> dict[str, Any]:
        """GET /api/v3/oco/order/details/{orderId}; classic trading account."""
        return await self._native_private(
            "get_spot_oco_order_details", self._native_params(orderId=order_id)
        )

    async def get_spot_oco_orders(
        self,
        *,
        product_symbol: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        order_ids: str | None = None,
        page_size: int | None = None,
        current_page: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v3/oco/orders; classic trading account."""
        return await self._native_private(
            "get_spot_oco_orders",
            self._native_params(
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                orderIds=order_ids,
                pageSize=page_size,
                currentPage=current_page,
            ),
        )

    async def place_margin_order(
        self,
        client_oid: str,
        side: str,
        product_symbol: str,
        *,
        type_: str | None = None,
        stp: str | None = None,
        price: str | None = None,
        size: str | None = None,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        cancel_after: int | None = None,
        funds: str | None = None,
        is_isolated: bool | None = None,
        auto_borrow: bool | None = None,
        auto_repay: bool | None = None,
    ) -> dict[str, Any]:
        """POST /api/v3/hf/margin/order; classic trading account."""
        return await self._native_private(
            "place_margin_order",
            self._native_params(
                clientOid=client_oid,
                side=side,
                product_symbol=product_symbol,
                type=type_,
                stp=stp,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                cancelAfter=cancel_after,
                funds=funds,
                isIsolated=is_isolated,
                autoBorrow=auto_borrow,
                autoRepay=auto_repay,
            ),
        )

    async def test_margin_order(
        self,
        client_oid: str,
        side: str,
        product_symbol: str,
        *,
        type_: str | None = None,
        stp: str | None = None,
        price: str | None = None,
        size: str | None = None,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        cancel_after: int | None = None,
        funds: str | None = None,
        is_isolated: bool | None = None,
        auto_borrow: bool | None = None,
        auto_repay: bool | None = None,
    ) -> dict[str, Any]:
        """POST /api/v3/hf/margin/order/test; classic trading account."""
        return await self._native_private(
            "test_margin_order",
            self._native_params(
                clientOid=client_oid,
                side=side,
                product_symbol=product_symbol,
                type=type_,
                stp=stp,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                cancelAfter=cancel_after,
                funds=funds,
                isIsolated=is_isolated,
                autoBorrow=auto_borrow,
                autoRepay=auto_repay,
            ),
        )

    async def cancel_margin_order(self, product_symbol: str, order_id: str) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/orders/{orderId}; classic trading account."""
        return await self._native_private(
            "cancel_margin_order",
            self._native_params(product_symbol=product_symbol, orderId=order_id),
        )

    async def cancel_margin_order_by_client_oid(
        self, product_symbol: str, client_oid: str
    ) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/orders/client-order/{clientOid}; classic trading account."""
        return await self._native_private(
            "cancel_margin_order_by_client_oid",
            self._native_params(product_symbol=product_symbol, clientOid=client_oid),
        )

    async def cancel_margin_orders_by_symbol(
        self, product_symbol: str, trade_type: str
    ) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/orders; classic trading account."""
        return await self._native_private(
            "cancel_margin_orders_by_symbol",
            self._native_params(product_symbol=product_symbol, tradeType=trade_type),
        )

    async def get_margin_active_order_symbols(self, trade_type: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/order/active/symbols; classic trading account."""
        return await self._native_private(
            "get_margin_active_order_symbols", self._native_params(tradeType=trade_type)
        )

    async def get_margin_open_orders(self, product_symbol: str, trade_type: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/orders/active; classic trading account."""
        return await self._native_private(
            "get_margin_open_orders",
            self._native_params(product_symbol=product_symbol, tradeType=trade_type),
        )

    async def get_margin_closed_orders(
        self,
        product_symbol: str,
        trade_type: str,
        *,
        side: str | None = None,
        type_: str | None = None,
        last_id: int | None = None,
        limit: int | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v3/hf/margin/orders/done; classic trading account."""
        return await self._native_private(
            "get_margin_closed_orders",
            self._native_params(
                product_symbol=product_symbol,
                tradeType=trade_type,
                side=side,
                type=type_,
                lastId=last_id,
                limit=limit,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def get_margin_trade_history(
        self,
        product_symbol: str,
        trade_type: str,
        *,
        order_id: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        last_id: int | None = None,
        limit: int | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v3/hf/margin/fills; classic trading account."""
        return await self._native_private(
            "get_margin_trade_history",
            self._native_params(
                product_symbol=product_symbol,
                tradeType=trade_type,
                orderId=order_id,
                side=side,
                type=type_,
                lastId=last_id,
                limit=limit,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def get_margin_order(self, product_symbol: str, order_id: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/orders/{orderId}; classic trading account."""
        return await self._native_private(
            "get_margin_order", self._native_params(product_symbol=product_symbol, orderId=order_id)
        )

    async def get_margin_order_by_client_oid(
        self, product_symbol: str, client_oid: str
    ) -> dict[str, Any]:
        """GET /api/v3/hf/margin/orders/client-order/{clientOid}; classic trading account."""
        return await self._native_private(
            "get_margin_order_by_client_oid",
            self._native_params(product_symbol=product_symbol, clientOid=client_oid),
        )

    async def place_margin_stop_order(
        self,
        client_oid: str,
        side: str,
        product_symbol: str,
        is_isolated: bool,
        auto_borrow: bool,
        auto_repay: bool,
        stop_price: str,
        *,
        type_: str | None = None,
        stp: str | None = None,
        price: str | None = None,
        size: str | None = None,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        cancel_after: int | None = None,
        funds: str | None = None,
        remark: str | None = None,
        stop: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/v3/hf/margin/stop-order; classic trading account."""
        return await self._native_private(
            "place_margin_stop_order",
            self._native_params(
                clientOid=client_oid,
                side=side,
                product_symbol=product_symbol,
                isIsolated=is_isolated,
                autoBorrow=auto_borrow,
                autoRepay=auto_repay,
                stopPrice=stop_price,
                type=type_,
                stp=stp,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                cancelAfter=cancel_after,
                funds=funds,
                remark=remark,
                stop=stop,
            ),
        )

    async def cancel_margin_stop_order_by_client_oid(self, client_oid: str) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/stop-order/cancel-by-clientOid; classic trading account."""
        return await self._native_private(
            "cancel_margin_stop_order_by_client_oid", self._native_params(clientOid=client_oid)
        )

    async def cancel_margin_stop_orders(
        self, trade_type: str, *, product_symbol: str | None = None, order_ids: str | None = None
    ) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/stop-order/cancel; classic trading account."""
        return await self._native_private(
            "cancel_margin_stop_orders",
            self._native_params(
                tradeType=trade_type, product_symbol=product_symbol, orderIds=order_ids
            ),
        )

    async def get_margin_stop_orders(
        self,
        *,
        product_symbol: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        trade_type: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        order_ids: str | None = None,
        page_size: int | None = None,
        stop: str | None = None,
    ) -> dict[str, Any]:
        """GET /api/v3/hf/margin/stop-orders; classic trading account."""
        return await self._native_private(
            "get_margin_stop_orders",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type=type_,
                tradeType=trade_type,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                orderIds=order_ids,
                pageSize=page_size,
                stop=stop,
            ),
        )

    async def get_margin_stop_order(self, order_id: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/stop-order/orderId; classic trading account."""
        return await self._native_private(
            "get_margin_stop_order", self._native_params(orderId=order_id)
        )

    async def get_margin_stop_order_by_client_oid(self, client_oid: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/stop-order/clientOid; classic trading account."""
        return await self._native_private(
            "get_margin_stop_order_by_client_oid", self._native_params(clientOid=client_oid)
        )

    async def place_margin_oco_order(
        self,
        client_oid: str,
        side: str,
        product_symbol: str,
        price: str,
        size: str,
        stop_price: str,
        limit_price: str,
        is_isolated: bool,
        *,
        auto_repay: bool | None = None,
        auto_borrow: bool | None = None,
    ) -> dict[str, Any]:
        """POST /api/v3/hf/margin/oco-order; classic trading account."""
        return await self._native_private(
            "place_margin_oco_order",
            self._native_params(
                clientOid=client_oid,
                side=side,
                product_symbol=product_symbol,
                price=price,
                size=size,
                stopPrice=stop_price,
                limitPrice=limit_price,
                isIsolated=is_isolated,
                autoRepay=auto_repay,
                autoBorrow=auto_borrow,
            ),
        )

    async def cancel_margin_oco_order(self, order_id: str) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/oco-order/cancel-by-id; classic trading account."""
        return await self._native_private(
            "cancel_margin_oco_order", self._native_params(orderId=order_id)
        )

    async def cancel_margin_oco_order_by_client_oid(self, client_oid: str) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/oco-order/cancel-by-clientOid; classic trading account."""
        return await self._native_private(
            "cancel_margin_oco_order_by_client_oid", self._native_params(clientOid=client_oid)
        )

    async def cancel_margin_oco_orders(
        self,
        *,
        order_ids: str | None = None,
        product_symbol: str | None = None,
        trade_type: str | None = None,
    ) -> dict[str, Any]:
        """DELETE /api/v3/hf/margin/oco-order/cancel; classic trading account."""
        return await self._native_private(
            "cancel_margin_oco_orders",
            self._native_params(
                orderIds=order_ids, product_symbol=product_symbol, tradeType=trade_type
            ),
        )

    async def get_margin_oco_order(self, order_id: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/oco-order/orderId; classic trading account."""
        return await self._native_private(
            "get_margin_oco_order", self._native_params(orderId=order_id)
        )

    async def get_margin_oco_order_by_client_oid(self, client_oid: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/oco-order/clientOid; classic trading account."""
        return await self._native_private(
            "get_margin_oco_order_by_client_oid", self._native_params(clientOid=client_oid)
        )

    async def get_margin_oco_order_details(self, order_id: str) -> dict[str, Any]:
        """GET /api/v3/hf/margin/oco-order/detail/orderId; classic trading account."""
        return await self._native_private(
            "get_margin_oco_order_details", self._native_params(orderId=order_id)
        )

    async def get_margin_oco_orders(
        self,
        page_size: int,
        current_page: str,
        *,
        product_symbol: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        order_ids: str | None = None,
        trade_type: str | None = None,
    ) -> dict[str, Any]:
        """GET /api/v3/hf/margin/oco-orders; classic trading account."""
        return await self._native_private(
            "get_margin_oco_orders",
            self._native_params(
                pageSize=page_size,
                currentPage=current_page,
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                orderIds=order_ids,
                tradeType=trade_type,
            ),
        )

    async def place_futures_tpsl_order(
        self,
        client_oid: str,
        product_symbol: str,
        *,
        side: str | None = None,
        leverage: int | None = None,
        type_: str | None = None,
        remark: str | None = None,
        stop_price_type: str | None = None,
        reduce_only: bool | None = None,
        close_order: bool | None = None,
        force_hold: bool | None = None,
        stp: str | None = None,
        margin_mode: str | None = None,
        price: str | None = None,
        size: int | None = None,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        trigger_stop_up_price: str | None = None,
        trigger_stop_down_price: str | None = None,
        qty: str | None = None,
        value_qty: str | None = None,
        position_side: str | None = None,
    ) -> dict[str, Any]:
        """POST /api/v1/st-orders; classic trading account."""
        return await self._native_private(
            "place_futures_tpsl_order",
            self._native_params(
                clientOid=client_oid,
                product_symbol=product_symbol,
                side=side,
                leverage=leverage,
                type=type_,
                remark=remark,
                stopPriceType=stop_price_type,
                reduceOnly=reduce_only,
                closeOrder=close_order,
                forceHold=force_hold,
                stp=stp,
                marginMode=margin_mode,
                price=price,
                size=size,
                timeInForce=time_in_force,
                postOnly=post_only,
                triggerStopUpPrice=trigger_stop_up_price,
                triggerStopDownPrice=trigger_stop_down_price,
                qty=qty,
                valueQty=value_qty,
                positionSide=position_side,
            ),
        )

    async def cancel_futures_stop_orders(
        self, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """DELETE /api/v1/stopOrders; classic trading account."""
        return await self._native_private(
            "cancel_futures_stop_orders", self._native_params(product_symbol=product_symbol)
        )

    async def get_futures_recent_closed_orders(
        self, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """GET /api/v1/recentDoneOrders; classic trading account."""
        return await self._native_private(
            "get_futures_recent_closed_orders", self._native_params(product_symbol=product_symbol)
        )

    async def get_futures_stop_orders(
        self,
        *,
        product_symbol: str | None = None,
        side: str | None = None,
        type_: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v1/stopOrders; classic trading account."""
        return await self._native_private(
            "get_futures_stop_orders",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type=type_,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    async def get_futures_margin_mode(self, product_symbol: str) -> dict[str, Any]:
        """GET /api/v2/position/getMarginMode; classic trading account."""
        return await self._native_private(
            "get_futures_margin_mode", self._native_params(product_symbol=product_symbol)
        )

    async def set_futures_margin_mode(
        self, product_symbol: str, margin_mode: str
    ) -> dict[str, Any]:
        """POST /api/v2/position/changeMarginMode; classic trading account."""
        return await self._native_private(
            "set_futures_margin_mode",
            self._native_params(product_symbol=product_symbol, marginMode=margin_mode),
        )

    async def set_futures_position_mode(self, position_mode: str) -> dict[str, Any]:
        """POST /api/v2/position/switchPositionMode; classic trading account."""
        return await self._native_private(
            "set_futures_position_mode", self._native_params(positionMode=position_mode)
        )

    async def get_futures_max_open_size(
        self, product_symbol: str, price: str, leverage: int
    ) -> dict[str, Any]:
        """GET /api/v2/getMaxOpenSize; classic trading account."""
        return await self._native_private(
            "get_futures_max_open_size",
            self._native_params(product_symbol=product_symbol, price=price, leverage=leverage),
        )

    async def get_futures_position_history(
        self,
        *,
        product_symbol: str | None = None,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        page_id: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v1/history-positions; classic trading account."""
        return await self._native_private(
            "get_futures_position_history",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                pageId=page_id,
                **{"from": from_, "to": to},
            ),
        )

    async def get_futures_max_withdraw_margin(
        self, product_symbol: str, *, position_side: str | None = None
    ) -> dict[str, Any]:
        """GET /api/v1/margin/maxWithdrawMargin; classic trading account."""
        return await self._native_private(
            "get_futures_max_withdraw_margin",
            self._native_params(product_symbol=product_symbol, positionSide=position_side),
        )

    async def add_futures_isolated_margin(
        self, product_symbol: str, margin: str, biz_no: str, *, position_side: str | None = None
    ) -> dict[str, Any]:
        """POST /api/v1/position/margin/deposit-margin; classic trading account."""
        return await self._native_private(
            "add_futures_isolated_margin",
            self._native_params(
                product_symbol=product_symbol,
                margin=margin,
                bizNo=biz_no,
                positionSide=position_side,
            ),
        )

    async def remove_futures_isolated_margin(
        self, product_symbol: str, withdraw_amount: str, *, position_side: str | None = None
    ) -> dict[str, Any]:
        """POST /api/v1/margin/withdrawMargin; classic trading account."""
        return await self._native_private(
            "remove_futures_isolated_margin",
            self._native_params(
                product_symbol=product_symbol,
                withdrawAmount=withdraw_amount,
                positionSide=position_side,
            ),
        )

    async def get_futures_cross_margin_risk_limit(
        self, product_symbol: str, *, total_margin: str | None = None, leverage: int | None = None
    ) -> dict[str, Any]:
        """GET /api/v2/batchGetCrossOrderLimit; classic trading account."""
        return await self._native_private(
            "get_futures_cross_margin_risk_limit",
            self._native_params(
                product_symbol=product_symbol, totalMargin=total_margin, leverage=leverage
            ),
        )

    async def get_futures_cross_margin_requirement(
        self, product_symbol: str, position_value: str, *, leverage: str | None = None
    ) -> dict[str, Any]:
        """POST /api/v2/getCrossModeMarginRequirement; classic trading account."""
        return await self._native_private(
            "get_futures_cross_margin_requirement",
            self._native_params(
                product_symbol=product_symbol, positionValue=position_value, leverage=leverage
            ),
        )

    async def get_futures_isolated_margin_risk_limit(self, product_symbol: str) -> dict[str, Any]:
        """GET /api/v1/contracts/risk-limit/{symbol}; classic trading account."""
        return await self._native_private(
            "get_futures_isolated_margin_risk_limit",
            self._native_params(product_symbol=product_symbol),
        )

    async def set_futures_isolated_margin_risk_limit(
        self, product_symbol: str, level: int
    ) -> dict[str, Any]:
        """POST /api/v1/position/risk-limit-level/change; classic trading account."""
        return await self._native_private(
            "set_futures_isolated_margin_risk_limit",
            self._native_params(product_symbol=product_symbol, level=level),
        )

    async def get_futures_funding_history(
        self,
        product_symbol: str,
        *,
        start_at: int | None = None,
        end_at: int | None = None,
        reverse: bool | None = None,
        offset: int | None = None,
        forward: bool | None = None,
        max_count: int | None = None,
    ) -> dict[str, Any]:
        """GET /api/v1/funding-history; classic trading account."""
        return await self._native_private(
            "get_futures_funding_history",
            self._native_params(
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                reverse=reverse,
                offset=offset,
                forward=forward,
                maxCount=max_count,
            ),
        )

    async def place_futures_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place 1 to 20 futures orders with native order fields or product_symbol."""
        return await self._native_private(
            "place_futures_batch_orders", self._native_params(orders=json.dumps(orders))
        )

    async def cancel_futures_batch_orders(
        self,
        *,
        order_ids: list[str] | None = None,
        client_orders: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Cancel up to 10 orders; order_ids takes precedence when both lists are given."""
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                orderIdsList=json.dumps(order_ids) if order_ids is not None else None,
                clientOidsList=json.dumps(client_orders) if client_orders is not None else None,
            ),
        )

    async def set_futures_batch_margin_mode(
        self, margin_mode: str, symbols: list[str]
    ) -> dict[str, Any]:
        """Change margin mode for a list of contracts."""
        return await self._native_private(
            "set_futures_batch_margin_mode",
            self._native_params(marginMode=margin_mode, symbols=json.dumps(symbols)),
        )

    async def get_spot_stop_order_by_client_oid(
        self, client_oid: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Query a spot stop order by client ID."""
        return await self._native_private(
            "get_spot_stop_order_by_client_oid",
            self._native_params(clientOid=client_oid, product_symbol=product_symbol),
        )

    async def get_futures_account_ledgers(
        self,
        *,
        currency: str | None = None,
        type_: str | None = None,
        offset: int | None = None,
        forward: bool | None = None,
        max_count: int | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v1/transaction-history``."""
        return await self._native_private(
            "get_futures_account_ledgers",
            self._native_params(
                currency=currency,
                type=type_,
                offset=offset,
                forward=forward,
                maxCount=max_count,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def get_margin_hf_account_ledgers(
        self,
        *,
        currency: str | None = None,
        direction: str | None = None,
        biz_type: str | None = None,
        last_id: int | None = None,
        limit: int | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/hf/margin/account/ledgers``."""
        return await self._native_private(
            "get_margin_hf_account_ledgers",
            self._native_params(
                currency=currency,
                direction=direction,
                bizType=biz_type,
                lastId=last_id,
                limit=limit,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def get_spot_account_ledgers(
        self,
        *,
        currency: str | None = None,
        direction: str | None = None,
        biz_type: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v1/accounts/ledgers``."""
        return await self._native_private(
            "get_spot_account_ledgers",
            self._native_params(
                currency=currency,
                direction=direction,
                bizType=biz_type,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    async def get_spot_hf_account_ledgers(
        self,
        *,
        currency: str | None = None,
        direction: str | None = None,
        biz_type: str | None = None,
        last_id: int | None = None,
        limit: int | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v1/hf/accounts/ledgers``."""
        return await self._native_private(
            "get_spot_hf_account_ledgers",
            self._native_params(
                currency=currency,
                direction=direction,
                bizType=biz_type,
                lastId=last_id,
                limit=limit,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def get_deposit_history(
        self,
        currency: str,
        *,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v1/deposits``."""
        return await self._native_private(
            "get_deposit_history",
            self._native_params(
                currency=currency,
                status=status,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    async def get_margin_currency_risk_limits(
        self,
        *,
        is_isolated: bool | None = None,
        currency: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/margin/currencies``."""
        return await self._native_private(
            "get_margin_currency_risk_limits",
            self._native_params(
                isIsolated=is_isolated, currency=currency, product_symbol=product_symbol
            ),
        )

    async def get_spot_full_orderbook(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/orderbook/level2``. Requires API authentication."""
        return await self._native_private(
            "get_spot_full_orderbook", self._native_params(product_symbol=product_symbol)
        )

    async def get_uta_account_ledgers(
        self,
        account_type: str,
        *,
        business_type: str | None = None,
        currency: str | None = None,
        direction: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page_size: int | None = None,
        last_id: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/ledger``."""
        return await self._native_private(
            "get_uta_account_ledgers",
            self._native_params(
                accountType=account_type,
                businessType=business_type,
                currency=currency,
                direction=direction,
                startAt=start_at,
                endAt=end_at,
                pageSize=page_size,
                lastId=last_id,
            ),
        )

    async def get_classic_account_balances_v2(
        self, account_type: str, *, account_subtype: str | None = None, currency: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/balance``."""
        return await self._native_private(
            "get_classic_account_balances_v2",
            self._native_params(
                accountSubtype=account_subtype, accountType=account_type, currency=currency
            ),
        )

    async def transfer_uta_accounts(
        self,
        client_oid: str,
        transfer_type: str,
        currency: str,
        amount: str,
        from_account_type: str,
        from_account_tag: str,
        to_account_type: str,
        to_account_tag: str,
        *,
        from_uid: str | None = None,
        to_uid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/ua/v2/account/transfer``."""
        return await self._native_private(
            "transfer_uta_accounts",
            self._native_params(
                clientOid=client_oid,
                transferType=transfer_type,
                currency=currency,
                amount=amount,
                fromUid=from_uid,
                fromAccountType=from_account_type,
                fromAccountTag=from_account_tag,
                toUid=to_uid,
                toAccountType=to_account_type,
                toAccountTag=to_account_tag,
            ),
        )

    async def get_uta_account_mode(self) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/mode``."""
        return await self._native_private("get_uta_account_mode", self._native_params())

    async def get_uta_all_rate_limits(self) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/rate-limit/query-all``."""
        return await self._native_private("get_uta_all_rate_limits", self._native_params())

    async def get_uta_rate_limits(self, uids: str) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/rate-limit/query``."""
        return await self._native_private("get_uta_rate_limits", self._native_params(uids=uids))

    async def get_uta_rate_limit_cap(self) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/rate-limit/query-cap``."""
        return await self._native_private("get_uta_rate_limit_cap", self._native_params())

    async def get_uta_borrowing_rates_limits(self, currency: str) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/interest-limits``."""
        return await self._native_private(
            "get_uta_borrowing_rates_limits", self._native_params(currency=currency)
        )

    async def get_uta_interest_history(
        self,
        account_type: str,
        *,
        currency: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/interest-history``."""
        return await self._native_private(
            "get_uta_interest_history",
            self._native_params(
                accountType=account_type,
                currency=currency,
                startTime=start_time,
                endTime=end_time,
                page=page,
                size=size,
            ),
        )

    async def get_uta_orderbook(
        self, trade_type: str, product_symbol: str, limit: str, *, rpi_filter: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/orderbook``. Requires API authentication."""
        return await self._native_private(
            "get_uta_orderbook",
            self._native_params(
                tradeType=trade_type,
                product_symbol=product_symbol,
                limit=limit,
                rpiFilter=rpi_filter,
            ),
        )

    async def get_uta_transfer_quota(
        self, account_type: str, currency: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/account/transfer-quota``."""
        return await self._native_private(
            "get_uta_transfer_quota",
            self._native_params(
                accountType=account_type, currency=currency, product_symbol=product_symbol
            ),
        )

    async def place_spot_order_sync(
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
        allowMaxTimeWindow: int | None = None,
        clientTimestamp: int | None = None,
    ) -> dict[str, Any]:
        """Place orders using the endpoint that waits for the matching result."""
        return await self._native_private(
            "place_spot_order_sync",
            self._native_params(**locals()),
        )

    async def place_spot_batch_orders_sync(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Place orders using the endpoint that waits for the matching result."""
        return await self._native_private(
            "place_spot_batch_orders_sync",
            self._native_params(orders=orders),
        )

    async def cancel_spot_order_sync(self, product_symbol: str, order_id: str) -> dict[str, Any]:
        """Cancel using the endpoint that returns the completed cancellation result."""
        return await self._native_private(
            "cancel_spot_order_sync",
            self._native_params(product_symbol=product_symbol, orderId=order_id),
        )

    async def cancel_spot_order_by_client_oid_sync(
        self, product_symbol: str, client_oid: str
    ) -> dict[str, Any]:
        """Cancel using the endpoint that returns the completed cancellation result."""
        return await self._native_private(
            "cancel_spot_order_by_client_oid_sync",
            self._native_params(product_symbol=product_symbol, clientOid=client_oid),
        )

    async def get_apikey_info(self) -> dict[str, Any]:
        """

        GET /api/v1/user/api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/account-funding/get-apikey-info

        """
        return await self._native_private("get_apikey_info", self._native_params())

    async def create_deposit_address_v3(
        self, *, currency: str, chain: str, to: str | None = None, amount: str | None = None
    ) -> dict[str, Any]:
        """

        POST /api/v3/deposit-address/create.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/deposit/add-deposit-address-v3

        """
        return await self._native_private(
            "create_deposit_address_v3",
            self._native_params(currency=currency, chain=chain, to=to, amount=amount),
        )

    async def get_deposit_addresses_v3(
        self, *, currency: str, chain: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v3/deposit-addresses.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/deposit/get-deposit-address-v3/en

        """
        return await self._native_private(
            "get_deposit_addresses_v3", self._native_params(currency=currency, chain=chain)
        )

    async def add_sub_account_api(
        self,
        *,
        passphrase: str,
        remark: str,
        sub_name: str,
        permission: str | None = None,
        ip_whitelist: str | None = None,
        expire: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v1/sub/api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/sub-account-api/add-subaccount-api

        """
        return await self._native_private(
            "add_sub_account_api",
            self._native_params(
                passphrase=passphrase,
                remark=remark,
                permission=permission,
                ipWhitelist=ip_whitelist,
                expire=expire,
                subName=sub_name,
            ),
        )

    async def delete_sub_account_api(
        self, *, api_key: str, sub_name: str, passphrase: str
    ) -> dict[str, Any]:
        """

        DELETE /api/v1/sub/api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/sub-account-api/delete-subaccount-api

        """
        return await self._native_private(
            "delete_sub_account_api",
            self._native_params(apiKey=api_key, subName=sub_name, passphrase=passphrase),
        )

    async def get_sub_account_api_list(
        self, *, sub_name: str, api_key: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v1/sub/api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/sub-account-api/get-subaccount-api-list

        """
        return await self._native_private(
            "get_sub_account_api_list", self._native_params(apiKey=api_key, subName=sub_name)
        )

    async def modify_sub_account_api(
        self,
        *,
        passphrase: str,
        sub_name: str,
        api_key: str,
        permission: str | None = None,
        ip_whitelist: str | None = None,
        expire: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v1/sub/api-key/update.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/sub-account-api/modify-subaccount-api

        """
        return await self._native_private(
            "modify_sub_account_api",
            self._native_params(
                passphrase=passphrase,
                permission=permission,
                ipWhitelist=ip_whitelist,
                expire=expire,
                subName=sub_name,
                apiKey=api_key,
            ),
        )

    async def add_sub_account_futures_permission(self, *, uid: str) -> dict[str, Any]:
        """

        POST /api/v3/sub/user/futures/enable.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/sub-account/add-subaccount-futures-permission

        """
        return await self._native_private(
            "add_sub_account_futures_permission", self._native_params(uid=uid)
        )

    async def add_sub_account_margin_permission(self, *, uid: str) -> dict[str, Any]:
        """

        POST /api/v3/sub/user/margin/enable.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/sub-account/add-subaccount-margin-permission

        """
        return await self._native_private(
            "add_sub_account_margin_permission", self._native_params(uid=uid)
        )

    async def get_basic_fee(self, *, currency_type: int | None = None) -> dict[str, Any]:
        """

        GET /api/v1/base-fee.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/trade-fee/get-basic-fee-spot-margin

        """
        return await self._native_private(
            "get_basic_fee", self._native_params(currencyType=currency_type)
        )

    async def add_convert_limit_order(
        self,
        *,
        client_order_id: str,
        from_currency: str,
        to_currency: str,
        from_currency_size: str,
        to_currency_size: str,
        account_type: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v1/convert/limit/order.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/add-convert-limit-order

        """
        return await self._native_private(
            "add_convert_limit_order",
            self._native_params(
                clientOrderId=client_order_id,
                accountType=account_type,
                fromCurrency=from_currency,
                toCurrency=to_currency,
                fromCurrencySize=from_currency_size,
                toCurrencySize=to_currency_size,
            ),
        )

    async def add_convert_order(
        self, *, client_order_id: str, quote_id: str, account_type: str | None = None
    ) -> dict[str, Any]:
        """

        POST /api/v1/convert/order.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/add-convert-order

        """
        return await self._native_private(
            "add_convert_order",
            self._native_params(
                clientOrderId=client_order_id, quoteId=quote_id, accountType=account_type
            ),
        )

    async def cancel_convert_limit_order(
        self, *, client_order_id: str | None = None, order_id: str | None = None
    ) -> dict[str, Any]:
        """

        DELETE /api/v1/convert/limit/order/cancel.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/cancel-convert-limit-order

        """
        return await self._native_private(
            "cancel_convert_limit_order",
            self._native_params(clientOrderId=client_order_id, orderId=order_id),
        )

    async def get_convert_limit_order_detail(
        self, *, client_order_id: str | None = None, order_id: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/limit/order/detail.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-limit-order-detail

        """
        return await self._native_private(
            "get_convert_limit_order_detail",
            self._native_params(clientOrderId=client_order_id, orderId=order_id),
        )

    async def get_convert_limit_order_detail_list(
        self,
        *,
        start_at: int | None = None,
        end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/limit/orders.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-limit-orders

        """
        return await self._native_private(
            "get_convert_limit_order_detail_list",
            self._native_params(
                startAt=start_at, endAt=end_at, page=page, pageSize=page_size, status=status
            ),
        )

    async def get_convert_limit_quote(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_currency_size: str | None = None,
        to_currency_size: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/limit/quote.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-limit-quote

        """
        return await self._native_private(
            "get_convert_limit_quote",
            self._native_params(
                fromCurrency=from_currency,
                toCurrency=to_currency,
                fromCurrencySize=from_currency_size,
                toCurrencySize=to_currency_size,
            ),
        )

    async def get_convert_order_detail(
        self, *, client_order_id: str | None = None, order_id: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/order/detail.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-order-detail

        """
        return await self._native_private(
            "get_convert_order_detail",
            self._native_params(clientOrderId=client_order_id, orderId=order_id),
        )

    async def get_convert_order_history(
        self,
        *,
        start_at: int | None = None,
        end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/order/history.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-order-history

        """
        return await self._native_private(
            "get_convert_order_history",
            self._native_params(
                startAt=start_at, endAt=end_at, page=page, pageSize=page_size, status=status
            ),
        )

    async def get_convert_quote(
        self,
        *,
        from_currency: str,
        to_currency: str,
        from_currency_size: str | None = None,
        to_currency_size: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/quote.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-quote

        """
        return await self._native_private(
            "get_convert_quote",
            self._native_params(
                fromCurrency=from_currency,
                toCurrency=to_currency,
                fromCurrencySize=from_currency_size,
                toCurrencySize=to_currency_size,
            ),
        )

    async def add_uta_sub_account(
        self,
        *,
        password: str,
        sub_name: str,
        access: str,
        remarks: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/ua/v2/user/sub/create-sub-account.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/add-sub-account

        """
        return await self._native_private(
            "add_uta_sub_account",
            self._native_params(
                password=password, remarks=remarks, subName=sub_name, access=access, mode=mode
            ),
        )

    async def add_uta_sub_account_api(
        self,
        *,
        sub_name: str,
        passphrase: str,
        remark: str,
        permission: str | None = None,
        ip_whitelist: str | None = None,
        expire: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/ua/v2/user/create-sub-api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/add-sub-api-key

        """
        return await self._native_private(
            "add_uta_sub_account_api",
            self._native_params(
                subName=sub_name,
                passphrase=passphrase,
                remark=remark,
                permission=permission,
                ipWhitelist=ip_whitelist,
                expire=expire,
            ),
        )

    async def get_uta_apikey_info(self) -> dict[str, Any]:
        """

        GET /api/ua/v2/user/api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/api-key

        """
        return await self._native_private("get_uta_apikey_info", self._native_params())

    async def delete_uta_sub_account_api(
        self, *, api_key: str, sub_name: str, passphrase: str
    ) -> dict[str, Any]:
        """

        DELETE /api/ua/v2/user/sub-api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/delete-sub-api-key

        """
        return await self._native_private(
            "delete_uta_sub_account_api",
            self._native_params(apiKey=api_key, subName=sub_name, passphrase=passphrase),
        )

    async def get_uta_deposit_address(
        self, *, currency: str, chain: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/ua/v2/asset/deposit/address.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/deposit-address

        """
        return await self._native_private(
            "get_uta_deposit_address", self._native_params(chain=chain, currency=currency)
        )

    async def get_uta_deposit_history(
        self,
        *,
        currency: str | None = None,
        id: str | None = None,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/ua/v2/asset/deposit/history.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/deposit-history

        """
        return await self._native_private(
            "get_uta_deposit_history",
            self._native_params(
                currency=currency,
                id=id,
                status=status,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    async def set_uta_kcs_fee_deduction(self, *, enabled: bool) -> dict[str, Any]:
        """

        GET /api/ua/v2/account/fee/kcs-deduct.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/kcs-deduct

        """
        return await self._native_private(
            "set_uta_kcs_fee_deduction", self._native_params(enabled=enabled)
        )

    async def modify_uta_sub_account_api(
        self,
        *,
        sub_name: str,
        api_key: str,
        passphrase: str,
        permission: str | None = None,
        ip_whitelist: str | None = None,
        expire: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/ua/v2/user/modify-sub-api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/modify-sub-api-key

        """
        return await self._native_private(
            "modify_uta_sub_account_api",
            self._native_params(
                subName=sub_name,
                apiKey=api_key,
                passphrase=passphrase,
                permission=permission,
                ipWhitelist=ip_whitelist,
                expire=expire,
            ),
        )

    async def set_uta_rate_limit(self, *, list: list[dict[str, Any]]) -> dict[str, Any]:
        """

        POST /api/ua/v2/rate-limit/set.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/set-sub-accounts-api-rate-limit

        """
        return await self._native_private("set_uta_rate_limit", self._native_params(list=list))

    async def get_uta_sub_account_api_list(self, *, api_key: str, sub_name: str) -> dict[str, Any]:
        """

        GET /api/ua/v2/user/sub-api-key.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/sub-api-keys

        """
        return await self._native_private(
            "get_uta_sub_account_api_list", self._native_params(apiKey=api_key, subName=sub_name)
        )

    async def set_uta_sub_account_transfer_permission(
        self, *, sub_uids: str, sub_to_sub: bool
    ) -> dict[str, Any]:
        """

        POST /api/ua/v2/sub-account/canTransferOut.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/transfer-permission

        """
        return await self._native_private(
            "set_uta_sub_account_transfer_permission",
            self._native_params(subUids=sub_uids, subToSub=sub_to_sub),
        )

    async def get_account_info(self) -> dict[str, Any]:
        """

        GET /api/v2/user-info.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/account-funding/get-account-summary-info

        """
        return await self._native_private("get_account_info", self._native_params())

    async def get_spot_account_type(self) -> dict[str, Any]:
        """

        GET /api/v1/hf/accounts/opened.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/account-funding/get-account-type-spot

        """
        return await self._native_private("get_spot_account_type", self._native_params())

    async def add_sub_account(
        self,
        *,
        password: str,
        sub_name: str,
        access: str,
        remarks: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v2/sub/user/created.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/3476608e0

        """
        return await self._native_private(
            "add_sub_account",
            self._native_params(
                password=password, remarks=remarks, subName=sub_name, access=access, mode=mode
            ),
        )

    async def get_withdrawal_history_by_id(self, *, withdrawal_id: str) -> dict[str, Any]:
        """
        GET /api/v1/withdrawals/{withdrawalId}.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-by-id
        """
        return await self._native_private(
            "get_withdrawal_history_by_id", self._native_params(withdrawalId=withdrawal_id)
        )

    async def get_withdrawal_history(
        self,
        *,
        currency: str,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v1/withdrawals.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-history
        """
        return await self._native_private(
            "get_withdrawal_history",
            self._native_params(
                currency=currency,
                status=status,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    async def get_withdrawal_quotas(
        self, *, currency: str, chain: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v1/withdrawals/quotas.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-quotas
        """
        return await self._native_private(
            "get_withdrawal_quotas", self._native_params(currency=currency, chain=chain)
        )

    async def get_loan_info(self) -> dict[str, Any]:
        """
        GET /api/v1/otc-loan/loan.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/vip-lending/get-account-detail
        """
        return await self._native_private("get_loan_info", self._native_params())

    async def get_accounts(self) -> dict[str, Any]:
        """
        GET /api/v1/otc-loan/accounts.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/vip-lending/get-accounts
        """
        return await self._native_private("get_accounts", self._native_params())

    async def get_discount_rate_configs(self) -> dict[str, Any]:
        """
        GET /api/v1/otc-loan/discount-rate-configs.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/rest/vip-lending/get-collateral-ratio
        """
        return await self._native_private("get_discount_rate_configs", self._native_params())

    async def get_uta_oes_custody_quota(
        self, *, custodian: str | None = None, currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/oes/custody-quota.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/get-oes-custody-quota
        """
        return await self._native_private(
            "get_uta_oes_custody_quota", self._native_params(custodian=custodian, currency=currency)
        )

    async def get_uta_accounts(self, *, account_type: str | None = None) -> dict[str, Any]:
        """
        GET /api/ua/v2/otc-loan/account.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-accounts
        """
        return await self._native_private(
            "get_uta_accounts", self._native_params(accountType=account_type)
        )

    async def get_uta_discount_rate_configs(
        self, *, account_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/otc-loan/discount-rate.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-collateral-ratio
        """
        return await self._native_private(
            "get_uta_discount_rate_configs", self._native_params(accountType=account_type)
        )

    async def get_uta_loan_info(self, *, account_type: str | None = None) -> dict[str, Any]:
        """
        GET /api/ua/v2/otc-loan/loan.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-loan-info
        """
        return await self._native_private(
            "get_uta_loan_info", self._native_params(accountType=account_type)
        )

    async def get_uta_withdrawal_history(
        self,
        *,
        currency: str | None = None,
        id: str | None = None,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/asset/withdrawal/history.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-history
        """
        return await self._native_private(
            "get_uta_withdrawal_history",
            self._native_params(
                currency=currency,
                id=id,
                status=status,
                startAt=start_at,
                endAt=end_at,
                currentPage=current_page,
                pageSize=page_size,
            ),
        )

    async def get_uta_withdrawal_quotas(
        self,
        *,
        currency: str,
        withdraw_type: str,
        chain: str | None = None,
        is_inner: bool | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/withdrawals/quotas.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-quota
        """
        return await self._native_private(
            "get_uta_withdrawal_quotas",
            self._native_params(
                chain=chain, currency=currency, isInner=is_inner, withdrawType=withdraw_type
            ),
        )

    async def set_uta_account_mode(self, *, account_type: str) -> dict[str, Any]:
        """Set the account mode; exchange migration eligibility applies."""
        return await self._native_private(
            "set_uta_account_mode", self._native_params(accountType=account_type)
        )
