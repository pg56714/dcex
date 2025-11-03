"""KuCoin Spot Trade HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import SpotTrade


class TradeHTTP(HTTPManager):
    """
    HTTP client for KuCoin Spot Trade API operations.

    This class provides comprehensive methods for spot trading operations
    including order placement, cancellation, order management, and trade
    history retrieval. It supports various order types such as market,
    limit, post-only, and batch orders.
    """

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
        """
        Place a new order on KuCoin spot trading.

        Args:
            product_symbol: Product symbol (e.g., "BTC-USDT-SPOT").
            side: Order side, "buy" or "sell".
            type_: Order type, "limit" or "market".
            size: Order size (required for limit orders, optional for market orders).
            funds: Order funds (for market orders, use either size or funds).
            price: Order price (required for limit orders).
            clientOid: Client order ID (recommended to use UUID).
            stp: Self trade prevention: "DC", "CO", "CN", "CB".
            tags: Order tag (max 20 ASCII characters).
            remark: Order remark (max 20 ASCII characters).
            timeInForce: "GTC", "GTT", "IOC", "FOK" (default: "GTC").
            cancelAfter: Cancel after n seconds (for GTT strategy).
            postOnly: Passive order label (disabled for IOC/FOK).
            hidden: Hidden order (not shown in order book).
            iceberg: Iceberg order.
            visibleSize: Maximum visible quantity in iceberg orders.
            allowMaxTimeWindow: Order timeout in milliseconds.
            clientTimestamp: Client timestamp (equal to KC-API-TIMESTAMP).

        Returns:
            Order placement result from KuCoin API.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
            "side": side,
            "type": type_,
        }

        if size is not None:
            payload["size"] = size
        if funds is not None:
            payload["funds"] = funds
        if price is not None:
            payload["price"] = price
        if clientOid is not None:
            payload["clientOid"] = clientOid
        if stp is not None:
            payload["stp"] = stp
        if tags is not None:
            payload["tags"] = tags
        if remark is not None:
            payload["remark"] = remark
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if cancelAfter is not None:
            payload["cancelAfter"] = cancelAfter
        if postOnly is not None:
            payload["postOnly"] = postOnly
        if hidden is not None:
            payload["hidden"] = hidden
        if iceberg is not None:
            payload["iceberg"] = iceberg
        if visibleSize is not None:
            payload["visibleSize"] = visibleSize
        if allowMaxTimeWindow is not None:
            payload["allowMaxTimeWindow"] = allowMaxTimeWindow
        if clientTimestamp is not None:
            payload["clientTimestamp"] = clientTimestamp

        res = await self._request(
            method="POST",
            path=SpotTrade.PLACE_ORDER,
            query=payload,
        )
        return res

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
        """
        Place a market order on KuCoin spot trading.

        Args:
            product_symbol: Product symbol (e.g., "BTC-USDT-SPOT").
            side: Order side, "buy" or "sell".
            size: Order size (use either size or funds).
            funds: Order funds (use either size or funds).
            clientOid: Client order ID.
            stp: Self trade prevention.
            tags: Order tag.
            remark: Order remark.
            allowMaxTimeWindow: Order timeout in milliseconds.
            clientTimestamp: Client timestamp.

        Returns:
            Order placement result from KuCoin API.
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type_="market",
            size=size,
            funds=funds,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param size: str - Order size (use either size or funds)
        :param funds: str - Order funds (use either size or funds)
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            funds=funds,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param size: str - Order size (use either size or funds)
        :param funds: str - Order funds (use either size or funds)
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            funds=funds,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param side: str - "buy" or "sell"
        :param size: str - Order size
        :param price: str - Order price
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param timeInForce: str - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
        :param cancelAfter: int - Cancel after n seconds (for GTT strategy)
        :param postOnly: bool - Passive order label
        :param hidden: bool - Hidden order
        :param iceberg: bool - Iceberg order
        :param visibleSize: str - Maximum visible quantity in iceberg orders
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type_="limit",
            size=size,
            price=price,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            timeInForce=timeInForce,
            cancelAfter=cancelAfter,
            postOnly=postOnly,
            hidden=hidden,
            iceberg=iceberg,
            visibleSize=visibleSize,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param size: str - Order size
        :param price: str - Order price
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param timeInForce: str - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
        :param cancelAfter: int - Cancel after n seconds (for GTT strategy)
        :param postOnly: bool - Passive order label
        :param hidden: bool - Hidden order
        :param iceberg: bool - Iceberg order
        :param visibleSize: str - Maximum visible quantity in iceberg orders
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            price=price,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            timeInForce=timeInForce,
            cancelAfter=cancelAfter,
            postOnly=postOnly,
            hidden=hidden,
            iceberg=iceberg,
            visibleSize=visibleSize,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param size: str - Order size
        :param price: str - Order price
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param timeInForce: str - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
        :param cancelAfter: int - Cancel after n seconds (for GTT strategy)
        :param postOnly: bool - Passive order label
        :param hidden: bool - Hidden order
        :param iceberg: bool - Iceberg order
        :param visibleSize: str - Maximum visible quantity in iceberg orders
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            price=price,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            timeInForce=timeInForce,
            cancelAfter=cancelAfter,
            postOnly=postOnly,
            hidden=hidden,
            iceberg=iceberg,
            visibleSize=visibleSize,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param side: str - "buy" or "sell"
        :param size: str - Order size
        :param price: str - Order price
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param timeInForce: str - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
        :param cancelAfter: int - Cancel after n seconds (for GTT strategy)
        :param hidden: bool - Hidden order
        :param iceberg: bool - Iceberg order
        :param visibleSize: str - Maximum visible quantity in iceberg orders
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side=side,
            size=size,
            price=price,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            timeInForce=timeInForce,
            cancelAfter=cancelAfter,
            postOnly=True,  # Set postOnly to True
            hidden=hidden,
            iceberg=iceberg,
            visibleSize=visibleSize,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param size: str - Order size
        :param price: str - Order price
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param timeInForce: str - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
        :param cancelAfter: int - Cancel after n seconds (for GTT strategy)
        :param hidden: bool - Hidden order
        :param iceberg: bool - Iceberg order
        :param visibleSize: str - Maximum visible quantity in iceberg orders
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            price=price,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            timeInForce=timeInForce,
            cancelAfter=cancelAfter,
            hidden=hidden,
            iceberg=iceberg,
            visibleSize=visibleSize,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
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
        """
        :param product_symbol: str - Product symbol
        :param size: str - Order size
        :param price: str - Order price
        :param clientOid: str - Client order ID
        :param stp: str - Self trade prevention
        :param tags: str - Order tag
        :param remark: str - Order remark
        :param timeInForce: str - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
        :param cancelAfter: int - Cancel after n seconds (for GTT strategy)
        :param hidden: bool - Hidden order
        :param iceberg: bool - Iceberg order
        :param visibleSize: str - Maximum visible quantity in iceberg orders
        :param allowMaxTimeWindow: int - Order timeout in milliseconds
        :param clientTimestamp: int - Client timestamp
        """
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            price=price,
            clientOid=clientOid,
            stp=stp,
            tags=tags,
            remark=remark,
            timeInForce=timeInForce,
            cancelAfter=cancelAfter,
            hidden=hidden,
            iceberg=iceberg,
            visibleSize=visibleSize,
            allowMaxTimeWindow=allowMaxTimeWindow,
            clientTimestamp=clientTimestamp,
        )

    async def place_spot_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Place multiple orders in batch on KuCoin spot trading.

        Args:
            orders: List of order dictionaries, each containing:
                - symbol: Trading pair symbol (required).
                - type: "limit" or "market" (required).
                - side: "buy" or "sell" (required).
                - size: Order size (required for limit, optional for market).
                - funds: Order funds (optional for market, use either size or funds).
                - price: Order price (required for limit).
                - clientOid: Client order ID (optional).
                - stp: Self trade prevention: "CN", "CO", "CB", "DC" (optional).
                - tags: Order tag, max 20 ASCII characters (optional).
                - remark: Order remark, max 20 ASCII characters (optional).
                - timeInForce: "GTC", "GTT", "IOC", "FOK" (optional, default: "GTC").
                - cancelAfter: Cancel after n seconds for GTT strategy (optional).
                - postOnly: Passive order label (optional).
                - hidden: Hidden order (optional).
                - iceberg: Iceberg order (optional).
                - visibleSize: Maximum visible quantity in iceberg orders (optional).

        Returns:
            Batch order placement result from KuCoin API.

        Raises:
            ValueError: If orders list is empty or contains more than 20 orders.

        Example:
            orders = [
                {
                    "symbol": "BTC-USDT",
                    "type": "limit",
                    "side": "buy",
                    "size": "0.001",
                    "price": "45000",
                    "clientOid": "uuid1"
                },
                {
                    "symbol": "ETH-USDT",
                    "type": "market",
                    "side": "sell",
                    "size": "0.01",
                    "clientOid": "uuid2"
                }
            ]
        """
        if not orders:
            raise ValueError("Orders list cannot be empty")

        if len(orders) > 20:
            raise ValueError("Maximum 20 orders can be placed simultaneously")

        processed_orders = []
        for order in orders:
            processed_order = order.copy()
            if "symbol" in processed_order:
                processed_order["symbol"] = self.ptm.get_exchange_symbol(
                    Common.KUCOIN, processed_order["symbol"]
                )
            processed_orders.append(processed_order)

        payload: dict[str, Any] = {"orderList": processed_orders}

        res = await self._request(
            method="POST",
            path=SpotTrade.BATCH_ORDERS,
            query=payload,
        )
        return res

    async def place_spot_batch_limit_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        :param orders: list - List of limit order dictionaries, each containing:
            - symbol: str (required) - Trading pair symbol
            - side: str (required) - "buy" or "sell"
            - size: str (required) - Order size
            - price: str (required) - Order price
            - clientOid: str (optional) - Client order ID
            - stp: str (optional) - Self trade prevention
            - tags: str (optional) - Order tag
            - remark: str (optional) - Order remark
            - timeInForce: str (optional) - "GTC", "GTT", "IOC", "FOK" (default: "GTC")
            - cancelAfter: int (optional) - Cancel after n seconds (for GTT strategy)
            - postOnly: bool (optional) - Passive order label
            - hidden: bool (optional) - Hidden order
            - iceberg: bool (optional) - Iceberg order
            - visibleSize: str (optional) - Maximum visible quantity in iceberg orders
        """
        # Add type="limit" to all orders
        processed_orders = []
        for order in orders:
            processed_order = order.copy()
            processed_order["type"] = "limit"
            processed_orders.append(processed_order)

        return await self.place_spot_batch_orders(processed_orders)

    async def place_spot_batch_market_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        :param orders: list - List of market order dictionaries, each containing:
            - symbol: str (required) - Trading pair symbol
            :param side: str (required) - "buy" or "sell"
            - size: str (optional) - Order size (use either size or funds)
            - funds: str (optional) - Order funds (use either size or funds)
            - clientOid: str (optional) - Client order ID
            - stp: str (optional) - Self trade prevention
            - tags: str (optional) - Order tag
            - remark: str (optional) - Order remark
        """
        # Add type="market" to all orders
        processed_orders = []
        for order in orders:
            processed_order = order.copy()
            processed_order["type"] = "market"
            processed_orders.append(processed_order)

        return await self.place_spot_batch_orders(processed_orders)

    async def cancel_spot_order(
        self,
        orderId: str,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Cancel a specific order by order ID.

        Args:
            orderId: The unique order ID generated by the trading system.
            product_symbol: Product symbol (e.g., "BTC-USDT-SPOT").

        Returns:
            Order cancellation result from KuCoin API.
        """
        # Format the path with orderId
        path = SpotTrade.CANCEL_ORDER.format(orderId=orderId)

        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }

        res = await self._request(
            method="DELETE",
            path=path,
            query=payload,
        )
        return res

    async def cancel_spot_all_orders_by_symbol(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Cancel all orders for a specific trading symbol.

        Args:
            product_symbol: Product symbol (e.g., "BTC-USDT-SPOT").

        Returns:
            Order cancellation result from KuCoin API.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }
        res = await self._request(
            method="DELETE",
            path=SpotTrade.CANCEL_ALL_ORDERS_BY_SYMBOL,
            query=payload,
        )
        return res

    async def cancel_spot_all_orders(
        self,
    ) -> dict[str, Any]:
        """
        Cancel all open orders across all trading pairs.

        Returns:
            Order cancellation result from KuCoin API.
        """
        res = await self._request(
            method="DELETE",
            path=SpotTrade.CANCEL_ALL_ORDERS,
        )
        return res

    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve all active/open orders.

        Args:
            product_symbol: Optional product symbol filter (e.g., "BTC-USDT-SPOT").

        Returns:
            List of active orders from KuCoin API.
        """
        payload: dict[str, Any] = {}
        if product_symbol:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol)

        res = await self._request(
            method="GET",
            path=SpotTrade.GET_OPEN_ORDERS,
            query=payload,
        )
        return res

    async def get_spot_trade_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        startAt: int | None = None,
        endAt: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve trade history/fills.

        Args:
            product_symbol: Optional product symbol filter (e.g., "BTC-USDT-SPOT").
            orderId: Optional order ID filter.
            startAt: Start time in milliseconds.
            endAt: End time in milliseconds.
            limit: Number of records to return.

        Returns:
            Trade history/fills from KuCoin API.
        """
        payload: dict[str, Any] = {}
        if product_symbol:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol)
        if orderId:
            payload["orderId"] = orderId
        if startAt:
            payload["startAt"] = startAt
        if endAt:
            payload["endAt"] = endAt
        if limit:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=SpotTrade.GET_TRADE_HISTORY,
            query=payload,
        )
        return res
