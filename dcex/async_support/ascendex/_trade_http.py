from ...utils.common import Common
from ...utils.helpers import generate_timestamp
from ._http_manager import HTTPManager
from .endpoints.order import SpotOrder


class TradeHTTP(HTTPManager):
    """HTTP client for Ascendex trading API endpoints."""

    async def place_spot_order(
        self,
        product_symbol: str,
        orderQty: str,
        orderType: str,
        side: str,
        time: int | str = generate_timestamp(),
        id: str | None = None,
        orderPrice: str | None = None,
        stopPrice: str | None = None,
        postOnly: bool | None = None,
        timeInForce: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            orderType: Order type ("market", "limit", "stop_market", "stop_limit")
            side: Order side ("buy", "sell")
            time: Timestamp in milliseconds (defaults to current time)
            id: Custom order ID (>=9 chars, optional)
            orderPrice: Order price (required for limit orders)
            stopPrice: Stop price (required for stop orders)
            postOnly: Post-only flag (optional)
            timeInForce: Time in force ("GTC", "IOC", "FOK")
            respInst: Response instruction ("ACK", "ACCEPT", "DONE")

        Returns:
            dict: Order placement result
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
            "orderQty": orderQty,
            "orderType": orderType,
            "side": side,
            "time": time,
        }
        if id is not None:
            payload["id"] = id
        if orderPrice is not None:
            payload["orderPrice"] = orderPrice
        if stopPrice is not None:
            payload["stopPrice"] = stopPrice
        if postOnly is not None:
            payload["postOnly"] = postOnly
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if respInst is not None:
            payload["respInst"] = respInst

        res = await self._request(
            method="POST",
            path=SpotOrder.PLACE_ORDER.route,
            hash_path=SpotOrder.PLACE_ORDER.hash,
            query=payload,
        )
        return res

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: str,
        id: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot market order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("buy", "sell")
            orderQty: Order quantity
            id: Custom order ID (optional)
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            orderQty=orderQty,
            orderType="market",
            side=side,
            id=id,
            respInst=respInst,
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        orderQty: str,
        id: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot market buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            id: Custom order ID (optional)
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="buy",
            orderQty=orderQty,
            id=id,
            respInst=respInst,
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        orderQty: str,
        id: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot market sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            id: Custom order ID (optional)
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="sell",
            orderQty=orderQty,
            id=id,
            respInst=respInst,
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: str,
        orderPrice: str,
        id: str | None = None,
        timeInForce: str = "GTC",
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot limit order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("buy", "sell")
            orderQty: Order quantity
            orderPrice: Order price
            id: Custom order ID (optional)
            timeInForce: Time in force (default: "GTC")
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            orderQty=orderQty,
            orderType="limit",
            side=side,
            orderPrice=orderPrice,
            id=id,
            timeInForce=timeInForce,
            respInst=respInst,
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        orderQty: str,
        orderPrice: str,
        id: str | None = None,
        timeInForce: str = "GTC",
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot limit buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            orderPrice: Order price
            id: Custom order ID (optional)
            timeInForce: Time in force (default: "GTC")
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="buy",
            orderQty=orderQty,
            orderPrice=orderPrice,
            id=id,
            timeInForce=timeInForce,
            respInst=respInst,
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        orderQty: str,
        orderPrice: str,
        id: str | None = None,
        timeInForce: str = "GTC",
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot limit sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            orderPrice: Order price
            id: Custom order ID (optional)
            timeInForce: Time in force (default: "GTC")
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="sell",
            orderQty=orderQty,
            orderPrice=orderPrice,
            id=id,
            timeInForce=timeInForce,
            respInst=respInst,
        )

    async def place_spot_post_only_order(
        self,
        product_symbol: str,
        side: str,
        orderQty: str,
        orderPrice: str,
        id: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot post-only order (maker order).

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ("buy", "sell")
            orderQty: Order quantity
            orderPrice: Order price
            id: Custom order ID (optional)
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            orderQty=orderQty,
            orderType="limit",
            side=side,
            orderPrice=orderPrice,
            postOnly=True,
            id=id,
            respInst=respInst,
        )

    async def place_spot_post_only_buy_order(
        self,
        product_symbol: str,
        orderQty: str,
        orderPrice: str,
        id: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot post-only buy order (maker order).

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            orderPrice: Order price
            id: Custom order ID (optional)
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_post_only_order(
            product_symbol=product_symbol,
            side="buy",
            orderQty=orderQty,
            orderPrice=orderPrice,
            id=id,
            respInst=respInst,
        )

    async def place_spot_post_only_sell_order(
        self,
        product_symbol: str,
        orderQty: str,
        orderPrice: str,
        id: str | None = None,
        respInst: str | None = None,
    ) -> dict:
        """
        Place a spot post-only sell order (maker order).

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            orderQty: Order quantity
            orderPrice: Order price
            id: Custom order ID (optional)
            respInst: Response instruction (optional)

        Returns:
            dict: Order placement result
        """
        return await self.place_spot_post_only_order(
            product_symbol=product_symbol,
            side="sell",
            orderQty=orderQty,
            orderPrice=orderPrice,
            id=id,
            respInst=respInst,
        )

    async def cancel_spot_order(
        self,
        orderId: str,
        product_symbol: str,
        time: int | str = generate_timestamp(),
        id: str | None = None,
    ) -> dict:
        """
        Cancel a spot order.

        Args:
            orderId: Order ID to cancel
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            time: Timestamp in milliseconds (defaults to current time)
            id: Custom request ID (optional)

        Returns:
            dict: Cancellation result
        """
        payload = {
            "orderId": orderId,
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
            "time": time,
        }
        if id is not None:
            payload["id"] = id

        res = await self._request(
            method="DELETE",
            path=SpotOrder.CANCEL_ORDER.route,
            hash_path=SpotOrder.CANCEL_ORDER.hash,
            query=payload,
        )
        return res

    async def cancel_all_spot_orders(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Cancel all spot orders for a trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Cancellation result
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
        }

        res = await self._request(
            method="DELETE",
            path=SpotOrder.CANCEL_ALL_ORDERS.route,
            hash_path=SpotOrder.CANCEL_ALL_ORDERS.hash,
            query=payload,
        )
        return res

    async def place_spot_batch_orders(
        self,
        orders: list,
    ) -> dict:
        """
        Place multiple spot orders in batch.

        Args:
            orders: List of order objects

        Returns:
            dict: Batch order placement result
        """
        payload = {
            "orders": orders,
        }

        res = await self._request(
            method="POST",
            path=SpotOrder.PLACE_BATCH_ORDERS.route,
            hash_path=SpotOrder.PLACE_BATCH_ORDERS.hash,
            query=payload,
        )
        return res

    async def cancel_spot_batch_orders(
        self,
        orders: list,
    ) -> dict:
        """
        Cancel multiple spot orders in batch.

        Args:
            orders: List of order objects to cancel

        Returns:
            dict: Batch cancellation result
        """
        payload = {
            "orders": orders,
        }

        res = await self._request(
            method="DELETE",
            path=SpotOrder.CANCEL_BATCH_ORDERS.route,
            hash_path=SpotOrder.CANCEL_BATCH_ORDERS.hash,
            query=payload,
        )
        return res

    async def get_order_status(
        self,
        orderId: str | None = None,
    ) -> dict:
        """
        Get order status.

        Args:
            orderId: Order ID to query (optional, if None returns all orders)

        Returns:
            dict: Order status information
        """
        payload = {}
        if orderId is not None:
            payload["orderId"] = orderId

        res = await self._request(
            method="GET",
            path=SpotOrder.QUERY_ORDER.route,
            hash_path=SpotOrder.QUERY_ORDER.hash,
            query=payload,
        )
        return res

    async def get_list_open_orders(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Get list of open orders for a trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: List of open orders
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=SpotOrder.LIST_OPEN_ORDERS.route,
            hash_path=SpotOrder.LIST_OPEN_ORDERS.hash,
            query=payload,
        )
        return res

    async def get_list_order_history(
        self,
        product_symbol: str,
        account: str = "cash",
        start_time: int | None = None,
        end_time: int | None = None,
        seqNum: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get order history for a trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            account: Account type ("cash", "margin", "future")
            start_time: Start time in milliseconds (optional)
            end_time: End time in milliseconds (optional)
            seqNum: Sequence number for pagination (optional)
            limit: Maximum number of orders to return (optional)

        Returns:
            dict: Order history data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
            "account": account,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if seqNum is not None:
            payload["seqNum"] = str(seqNum)
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=SpotOrder.LIST_ORDER_HISTORY.route,
            hash_path=SpotOrder.LIST_ORDER_HISTORY.hash,
            query=payload,
        )
        return res
