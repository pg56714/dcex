from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import DeliveryTrade, FutureTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """
    Gate.io Trade HTTP client for trading operations.

    This class provides methods for trading operations including position management,
    order placement, order management, and trading history for spot, futures,
    and delivery markets.
    """

    def get_futures_all_positions(
        self,
        ccy: str = "usdt",  # or "btc"
        holding: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get all futures positions.

        Args:
            ccy: Settlement currency, either "usdt" or "btc"
            holding: Whether to include only positions with holdings
            limit: Maximum number of positions to return
            offset: Number of positions to skip

        Returns:
            dict[str, Any]: List of futures positions with their details
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "holding": holding,
        }
        if limit:
            payload["limit"] = limit
        if offset:
            payload["offset"] = offset

        res = self._request(
            method="GET",
            path=FutureTrade.GET_ALL_POSITIONS,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_contract_single_positions(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc" (futures)
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Get single contract position.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Position details for the specified contract
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if path == "futures":
            path_ = FutureTrade.GET_SINGLE_POSITION
        elif path == "delivery":
            path_ = DeliveryTrade.GET_SINGLE_POSITION
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
        )
        return res

    def update_futures_positions_leverage(
        self,
        product_symbol: str,
        leverage: str,
        ccy: str = "usdt",  # or "btc"
        cross_leverage_limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Update futures position leverage.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            leverage: New leverage value
            ccy: Settlement currency, either "usdt" or "btc"
            cross_leverage_limit: Cross margin leverage limit (valid only when leverage is 0)

        Returns:
            dict[str, Any]: Updated position information
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        payload: dict[str, Any] = {
            "leverage": leverage,
        }

        if cross_leverage_limit:
            payload["cross_leverage_limit"] = cross_leverage_limit

        res = self._request(
            method="POST",
            path=FutureTrade.UPDATE_POSITION_LEVERAGE,
            path_params=path_params,
            query=payload,
        )
        return res

    def future_dual_mode_switch(
        self,
        dual_mode: bool,
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        Switch futures dual mode.

        Args:
            dual_mode: Whether to enable dual mode
            ccy: Settlement currency, either "usdt" or "btc"

        Returns:
            dict[str, Any]: Dual mode status information
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "dual_mode": dual_mode,
        }

        res = self._request(
            method="POST",
            path=FutureTrade.DUAL_MODE_SWITCH,
            path_params=path_params,
            query=payload,
        )
        return res

    def place_contract_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        iceberg: int | None = None,
        price: str | None = None,
        close: bool | None = None,
        reduce_only: bool | None = None,
        tif: str | None = None,
        text: str | None = None,
        auto_size: str | None = None,
        stp_act: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a contract order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (positive for buy, negative for sell)
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"
            iceberg: Iceberg order size
            price: Order price (required for limit orders)
            close: Whether to close position
            reduce_only: Whether this is a reduce-only order
            tif: Time in force (gtc, ioc, poc, fok)
            text: Order text identifier
            auto_size: Auto size setting
            stp_act: Self-trade prevention action

        Returns:
            dict[str, Any]: Order information including order ID
        """

        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        body: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
            "size": size,
        }

        if iceberg is not None:
            body["iceberg"] = iceberg
        if price is not None:
            body["price"] = price
        if close is not None:
            body["close"] = close
        if reduce_only is not None:
            body["reduce_only"] = reduce_only
        if tif is not None:
            body["tif"] = tif
        if text is not None:
            body["text"] = text
        if auto_size is not None:
            body["auto_size"] = auto_size
        if stp_act is not None:
            body["stp_act"] = stp_act

        if path == "futures":
            path_ = FutureTrade.FUTURES_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.FUTURES_ORDER
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="POST",
            path=path_,
            path_params=path_params,
            body=body,
        )
        return res

    def place_contract_market_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a market order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (positive for buy, negative for sell)
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_order(
            product_symbol=product_symbol,
            size=size,
            price="0",
            tif="ioc",
            ccy=ccy,
            path=path,
        )

    def place_contract_market_buy_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a market buy order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (will be converted to positive)
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_market_order(
            product_symbol=product_symbol,
            size=abs(size),
            ccy=ccy,
            path=path,
        )

    def place_contract_market_sell_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a market sell order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (will be converted to negative)
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_market_order(
            product_symbol=product_symbol,
            size=-abs(size),  # negative size for sell
            ccy=ccy,
            path=path,
        )

    def place_contract_limit_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a limit order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (positive for buy, negative for sell)
            price: Order price
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_order(
            product_symbol=product_symbol,
            size=size,
            price=price,
            tif="gtc",
            ccy=ccy,
            path=path,
        )

    def place_contract_limit_buy_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a limit buy order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (will be converted to positive)
            price: Order price
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_limit_order(
            product_symbol=product_symbol,
            size=abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    def place_contract_limit_sell_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a limit sell order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (will be converted to negative)
            price: Order price
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_limit_order(
            product_symbol=product_symbol,
            size=-abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    def place_contract_post_only_limit_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a post-only limit order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (positive for buy, negative for sell)
            price: Order price
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_order(
            product_symbol=product_symbol,
            size=size,
            price=price,
            tif="poc",
            ccy=ccy,
            path=path,
        )

    def place_contract_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a post-only limit buy order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (will be converted to positive)
            price: Order price
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_post_only_limit_order(
            product_symbol=product_symbol,
            size=abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    def place_contract_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Place a post-only limit sell order for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            size: Order size (will be converted to negative)
            price: Order price
            ccy: Settlement currency
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_contract_post_only_limit_order(
            product_symbol=product_symbol,
            size=-abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    def place_futures_batch_order(
        self,
        orders: list[dict[str, Any]],
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        Place multiple futures orders in batch.

        Args:
            orders: List of order dictionaries (max 10 orders)
            ccy: Settlement currency, either "usdt" or "btc"

        Returns:
            dict[str, Any]: Batch order results

        Raises:
            TypeError: If orders is not a list of dictionaries
            ValueError: If more than 10 orders are provided
        """
        if not isinstance(orders, list) or not all(isinstance(o, dict) for o in orders):
            raise TypeError("Orders must be a list of dictionaries.")

        if len(orders) > 10:
            raise ValueError("The number of orders cannot exceed 10.")

        for order in orders:
            if "contract" not in order and "product_symbol" in order:
                order["contract"] = self.ptm.get_exchange_symbol(
                    Common.GATEIO, order["product_symbol"]
                )
                del order["product_symbol"]

        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        res = self._request(
            method="POST",
            path=FutureTrade.BATCH_FUTURES_ORDERS,
            path_params=path_params,
            body=orders,
        )
        return res

    def get_contract_order_list(
        self,
        status: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        product_symbol: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        last_id: str | None = None,
        count_total: int | None = None,
    ) -> dict[str, Any]:
        """
        Get contract order list.

        Args:
            status: Order status to filter by
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"
            product_symbol: Product symbol to filter by
            limit: Maximum number of orders to return
            offset: Number of orders to skip
            last_id: Last order ID for pagination
            count_total: Whether to include total count (delivery only)

        Returns:
            dict[str, Any]: List of orders matching the criteria
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "status": status,
        }
        if product_symbol is not None:
            payload["contract"] = self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol)
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset
        if last_id is not None:
            payload["last_id"] = last_id

        if path == "futures":
            path_ = FutureTrade.FUTURES_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.FUTURES_ORDER

            if count_total is not None:
                payload["count_total"] = count_total
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
        )
        return res

    def cancel_contract_all_order_matched(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all matched orders for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"
            side: Order side to filter by (buy/sell)

        Returns:
            dict[str, Any]: Cancellation results
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if side is not None:
            payload["side"] = side

        if path == "futures":
            path_ = FutureTrade.FUTURES_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.FUTURES_ORDER
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="DELETE",
            path=path_,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_contract_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Get a single contract order by ID.

        Args:
            order_id: Order ID
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Order details
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
            "order_id": order_id,
        }

        if path == "futures":
            path_ = FutureTrade.SINGLE_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.SINGLE_ORDER
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
        )
        return res

    def cancel_contract_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        Cancel a single contract order by ID.

        Args:
            order_id: Order ID
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"

        Returns:
            dict[str, Any]: Cancellation result
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
            "order_id": order_id,
        }

        if path == "futures":
            path_ = FutureTrade.SINGLE_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.SINGLE_ORDER
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="DELETE",
            path=path_,
            path_params=path_params,
        )
        return res

    def amend_futures_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",  # or "btc"
        size: int | None = None,
        price: str | None = None,
        amend_text: str | None = None,
        biz_info: str | None = None,
        bbo: str | None = None,
    ) -> dict[str, Any]:
        """
        Amend a futures order.

        Args:
            order_id: Order ID
            ccy: Settlement currency, either "usdt" or "btc"
            size: New order size
            price: New order price
            amend_text: Amendment text
            biz_info: Business information
            bbo: Best bid offer setting

        Returns:
            dict[str, Any]: Amended order information
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
            "order_id": order_id,
        }

        body: dict[str, Any] = {}
        if size is not None:
            body["size"] = size
        if price is not None:
            body["price"] = price
        if amend_text is not None:
            body["amend_text"] = amend_text
        if biz_info is not None:
            body["biz_info"] = biz_info
        if bbo is not None:
            body["bbo"] = bbo

        res = self._request(
            method="PUT",
            path=FutureTrade.SINGLE_ORDER,
            path_params=path_params,
            body=body,
        )
        return res

    def get_trading_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        order: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        late_id: str | None = None,
        count_total: int | None = None,
    ) -> dict[str, Any]:
        """
        Get trading history for a contract.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            path: Market type, either "futures" or "delivery"
            order: Order ID to filter by
            limit: Maximum number of trades to return
            offset: Number of trades to skip
            late_id: Last trade ID for pagination
            count_total: Whether to include total count (delivery only)

        Returns:
            dict[str, Any]: Trading history data
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if order is not None:
            payload["order"] = order
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset
        if late_id is not None:
            payload["late_id"] = late_id

        if path == "futures":
            path_ = FutureTrade.LIST_PERSONAL_TRADING_HISTORY
        elif path == "delivery":
            path_ = DeliveryTrade.LIST_PERSONAL_TRADING_HISTORY

            if count_total is not None:
                payload["count_total"] = count_total
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_futures_position_close_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        offset: int | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        side: str | None = None,
        pnl: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures position close history.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            limit: Maximum number of records to return
            offset: Number of records to skip
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds
            side: Position side to filter by
            pnl: PnL filter (positive/negative)

        Returns:
            dict[str, Any]: Position close history data
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset
        if from_timestamp is not None:
            payload["from"] = from_timestamp
        if to_timestamp is not None:
            payload["to"] = to_timestamp
        if side is not None:
            payload["side"] = side
        if pnl is not None:
            payload["pnl"] = pnl

        res = self._request(
            method="GET",
            path=FutureTrade.LIST_POSITION_CLOSE_HISTORY,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_futures_auto_deleveraging_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        at_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """
        Get futures auto deleveraging history.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, either "usdt" or "btc"
            limit: Maximum number of records to return
            at_timestamp: Specific timestamp to query

        Returns:
            dict[str, Any]: Auto deleveraging history data
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if limit is not None:
            payload["limit"] = limit
        if at_timestamp is not None:
            payload["at"] = at_timestamp

        res = self._request(
            method="GET",
            path=FutureTrade.LIST_AUTODELEVERAGING_HISTORY,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_delivery_all_positions(
        self,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """
        Get all delivery positions.

        Args:
            ccy: Settlement currency, typically "usdt"

        Returns:
            dict[str, Any]: List of delivery positions
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        res = self._request(
            method="GET",
            path=DeliveryTrade.GET_ALL_POSITIONS,
            path_params=path_params,
        )
        return res

    def update_delivery_positions_leverage(
        self,
        product_symbol: str,
        leverage: str,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """
        Update delivery position leverage.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            leverage: New leverage value
            ccy: Settlement currency, typically "usdt"

        Returns:
            dict[str, Any]: Updated position information
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        payload: dict[str, Any] = {
            "leverage": leverage,
        }

        res = self._request(
            method="POST",
            path=DeliveryTrade.UPDATE_POSITION_LEVERAGE,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_delivery_position_close_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get delivery position close history.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            ccy: Settlement currency, typically "usdt"
            limit: Maximum number of records to return

        Returns:
            dict[str, Any]: Delivery position close history data
        """
        path_params: dict[str, Any] = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="GET",
            path=DeliveryTrade.LIST_POSITION_CLOSE_HISTORY,
            path_params=path_params,
            query=payload,
        )
        return res

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
        text: str | None = None,
        order_type: str | None = None,  # limit or market
        account: str | None = None,  # spot, margin, unified
        price: str | None = None,
        time_in_force: str | None = None,  # gtc, ioc, poc, fok
        iceberg: str | None = None,
        auto_borrow: bool = False,
        auto_repay: bool = False,
        stp_act: str | None = None,
        action_mode: str | None = None,  # ACK, RESULT, FULL
    ) -> dict[str, Any]:
        """
        Place a spot order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            side: Order side ("buy" or "sell")
            amount: Order amount
            text: Order text identifier
            order_type: Order type ("limit" or "market")
            account: Account type ("spot", "margin", "unified")
            price: Order price (required for limit orders)
            time_in_force: Time in force ("gtc", "ioc", "poc", "fok")
            iceberg: Iceberg order amount
            auto_borrow: Whether to auto borrow
            auto_repay: Whether to auto repay
            stp_act: Self-trade prevention action
            action_mode: Action mode ("ACK", "RESULT", "FULL")

        Returns:
            dict[str, Any]: Order information including order ID
        """

        body: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
            "side": side,
            "amount": amount,
        }

        if text is not None:
            body["text"] = text
        if order_type is not None:
            body["type"] = order_type
        if account is not None:
            body["account"] = account
        if price is not None:
            body["price"] = price
        if time_in_force is not None:
            body["time_in_force"] = time_in_force
        if iceberg is not None:
            body["iceberg"] = iceberg
        if auto_borrow:
            body["auto_borrow"] = True
        if auto_repay:
            body["auto_repay"] = True
        if stp_act is not None:
            body["stp_act"] = stp_act
        if action_mode is not None:
            body["action_mode"] = action_mode

        res = self._request(
            method="POST",
            path=SpotTrade.SPOT_ORDER,
            body=body,
        )
        return res

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        Place a spot market order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            side: Order side ("buy" or "sell")
            amount: Order amount

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            order_type="market",
            time_in_force="ioc",
            amount=amount,
        )

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        Place a spot market buy order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            amount: Order amount

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_market_order(
            product_symbol=product_symbol,
            side="buy",
            amount=amount,
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        Place a spot market sell order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            amount: Order amount

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_market_order(
            product_symbol=product_symbol,
            side="sell",
            amount=amount,
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        """
        Place a spot limit order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            side: Order side ("buy" or "sell")
            amount: Order amount
            price: Order price

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            order_type="limit",
            amount=amount,
            price=price,
        )

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        """
        Place a spot limit buy order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            amount: Order amount
            price: Order price

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="buy",
            amount=amount,
            price=price,
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        """
        Place a spot limit sell order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            amount: Order amount
            price: Order price

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="sell",
            amount=amount,
            price=price,
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        """
        Place a spot post-only limit order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            side: Order side ("buy" or "sell")
            amount: Order amount
            price: Order price

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            order_type="limit",
            time_in_force="poc",
            amount=amount,
            price=price,
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        """
        Place a spot post-only limit buy order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            amount: Order amount
            price: Order price

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="buy",
            amount=amount,
            price=price,
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        """
        Place a spot post-only limit sell order.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            amount: Order amount
            price: Order price

        Returns:
            dict[str, Any]: Order information including order ID
        """
        return self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="sell",
            amount=amount,
            price=price,
        )

    def get_spot_open_orders(
        self,
        page: str | None = None,
        limit: str | None = None,
        account: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot open orders.

        Args:
            page: Page number for pagination
            limit: Maximum number of orders per page
            account: Account type to filter by

        Returns:
            dict[str, Any]: List of open spot orders
        """

        payload: dict[str, Any] = {}

        if page is not None:
            payload["page"] = page
        if limit is not None:
            payload["limit"] = limit
        if account is not None:
            payload["account"] = account

        res = self._request(
            method="GET",
            path=SpotTrade.GET_OPEN_ORDER,
            query=payload,
        )
        return res

    def get_spot_order_list(
        self,
        product_symbol: str,
        status: str,
        page: str | None = None,
        limit: str | None = None,
        account: str | None = None,
        from_timestamp: str | None = None,
        to_timestamp: str | None = None,
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot order list.

        Args:
            product_symbol: Product symbol (e.g., "BTC_USDT")
            status: Order status to filter by
            page: Page number for pagination
            limit: Maximum number of orders per page
            account: Account type to filter by
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds
            side: Order side to filter by

        Returns:
            dict[str, Any]: List of spot orders matching the criteria
        """

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
            "status": status,
        }

        if page is not None:
            payload["page"] = page
        if limit is not None:
            payload["limit"] = limit
        if account is not None:
            payload["account"] = account
        if from_timestamp is not None:
            payload["from"] = from_timestamp
        if to_timestamp is not None:
            payload["to"] = to_timestamp
        if side is not None:
            payload["side"] = side

        res = self._request(
            method="GET",
            path=SpotTrade.SPOT_ORDER,
            query=payload,
        )
        return res

    def cancel_spot_order(
        self,
        product_symbol: str | None = None,
        side: str | None = None,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel spot orders.

        Args:
            product_symbol: Product symbol to filter by
            side: Order side to filter by
            account: Account type to filter by
            action_mode: Action mode ("ACK", "RESULT", "FULL")

        Returns:
            dict[str, Any]: Cancellation results
        """
        payload: dict[str, Any] = {}
        if product_symbol is not None:
            payload["currency_pair"] = self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol)
        if side is not None:
            payload["side"] = side
        if account is not None:
            payload["account"] = account
        if action_mode is not None:
            payload["action_mode"] = action_mode

        res = self._request(
            method="DELETE",
            path=SpotTrade.SPOT_ORDER,
            query=payload,
        )
        return res

    def get_spot_single_order(
        self,
        order_id: str,
        product_symbol: str,
        account: str | None = None,
    ) -> dict[str, Any]:
        """
        Get a single spot order by ID.

        Args:
            order_id: Order ID
            product_symbol: Product symbol (e.g., "BTC_USDT")
            account: Account type to filter by

        Returns:
            dict[str, Any]: Order details
        """
        path_params: dict[str, Any] = {
            "order_id": order_id,
        }

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if account is not None:
            payload["account"] = account

        res = self._request(
            method="GET",
            path=SpotTrade.SINGLE_ORDER,
            path_params=path_params,
            query=payload,
        )
        return res

    def cancel_spot_single_order(
        self,
        order_id: str,
        product_symbol: str,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel a single spot order by ID.

        Args:
            order_id: Order ID
            product_symbol: Product symbol (e.g., "BTC_USDT")
            account: Account type to filter by
            action_mode: Action mode ("ACK", "RESULT", "FULL")

        Returns:
            dict[str, Any]: Cancellation result
        """
        path_params: dict[str, Any] = {
            "order_id": order_id,
        }

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if account is not None:
            payload["account"] = account
        if action_mode is not None:
            payload["action_mode"] = action_mode

        res = self._request(
            method="DELETE",
            path=SpotTrade.SINGLE_ORDER,
            path_params=path_params,
            query=payload,
        )
        return res

    def amend_spot_single_order(
        self,
        order_id: str,
        product_symbol: int | None = None,
        account: str | None = None,
        amount: str | None = None,
        price: str | None = None,
        amend_text: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Amend a spot order.

        Args:
            order_id: Order ID
            product_symbol: Product symbol (e.g., "BTC_USDT")
            account: Account type to filter by
            amount: New order amount
            price: New order price
            amend_text: Amendment text
            action_mode: Action mode ("ACK", "RESULT", "FULL")

        Returns:
            dict[str, Any]: Amended order information
        """
        path_params: dict[str, Any] = {
            "order_id": order_id,
        }

        body: dict[str, Any] = {}
        if product_symbol is not None:
            body["currency_pair"] = self.ptm.get_exchange_symbol(Common.GATEIO, str(product_symbol))
        if account is not None:
            body["account"] = account
        if amount is not None:
            body["amount"] = amount
        if price is not None:
            body["price"] = price
        if amend_text is not None:
            body["amend_text"] = amend_text
        if action_mode is not None:
            body["action_mode"] = action_mode

        res = self._request(
            method="PATCH",
            path=SpotTrade.SINGLE_ORDER,
            path_params=path_params,
            body=body,
        )
        return res

    def get_spot_trading_history(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        order_id: str | None = None,
        account: str | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """
        Get spot trading history.

        Args:
            product_symbol: Product symbol to filter by
            limit: Maximum number of trades to return
            page: Page number for pagination
            order_id: Order ID to filter by
            account: Account type to filter by
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds

        Returns:
            dict[str, Any]: Spot trading history data
        """
        payload: dict[str, Any] = {}
        if product_symbol is not None:
            payload["currency_pair"] = self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol)
        if limit is not None:
            payload["limit"] = limit
        if page is not None:
            payload["page"] = page
        if order_id is not None:
            payload["order_id"] = order_id
        if account is not None:
            payload["account"] = account
        if from_timestamp is not None:
            payload["from"] = from_timestamp
        if to_timestamp is not None:
            payload["to"] = to_timestamp

        res = self._request(
            method="GET",
            path=SpotTrade.LIST_PERSONAL_TRADING_HISTORY,
            query=payload,
        )
        return res
