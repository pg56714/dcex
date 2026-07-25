"""KuCoin async trading HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for KuCoin spot and futures trading APIs."""

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
