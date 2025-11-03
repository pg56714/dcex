"""
Gate.io trading HTTP client module.

This module provides the TradeHTTP class for interacting with Gate.io's
trading API endpoints, including futures, delivery, and spot trading
operations such as order placement, position management, and trading history.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import DeliveryTrade, FutureTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """
    Gate.io trading HTTP client.

    This class provides methods for interacting with Gate.io's trading API
    endpoints, including:
    - Futures position management and trading
    - Delivery position management and trading
    - Spot order placement and management
    - Order modification, cancellation, and history
    - Trading history and position close history

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_futures_all_positions(
        self,
        ccy: str = "usdt",  # or "btc"
        holding: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """
        Get all futures positions.

        Args:
            ccy: Settlement currency (usdt or btc)
            holding: Whether to show only holding positions
            limit: Optional maximum number of positions
            offset: Optional offset for pagination

        Returns:
            Dict containing futures positions information
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "holding": holding,
        }
        if limit:
            payload["limit"] = limit
        if offset:
            payload["offset"] = offset

        res = await self._request(
            method="GET",
            path=FutureTrade.GET_ALL_POSITIONS,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_contract_single_positions(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc" (futures)
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param ccy: str
        """
        path_params = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if path == "futures":
            path_ = FutureTrade.GET_SINGLE_POSITION
        elif path == "delivery":
            path_ = DeliveryTrade.GET_SINGLE_POSITION
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
        )
        return res

    async def update_futures_positions_leverage(
        self,
        product_symbol: str,
        leverage: str,
        ccy: str = "usdt",  # or "btc"
        cross_leverage_limit: str | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param leverage: str
        :param ccy: str
        :param cross_leverage_limit: str (Cross margin leverage(valid only when leverage is 0))
        """
        path_params = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        payload: dict[str, Any] = {
            "leverage": leverage,
        }

        if cross_leverage_limit:
            payload["cross_leverage_limit"] = cross_leverage_limit

        res = await self._request(
            method="POST",
            path=FutureTrade.UPDATE_POSITION_LEVERAGE,
            path_params=path_params,
            query=payload,
        )
        return res

    async def future_dual_mode_switch(
        self,
        dual_mode: bool,
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        :param dual_mode: bool
        :param ccy: str
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "dual_mode": dual_mode,
        }

        res = await self._request(
            method="POST",
            path=FutureTrade.DUAL_MODE_SWITCH,
            path_params=path_params,
            query=payload,
        )
        return res

    async def place_contract_order(
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
            product_symbol: Product symbol
            size: Order size
            ccy: Settlement currency (usdt or btc)
            path: Contract type (futures or delivery)
            iceberg: Optional iceberg order size
            price: Optional order price
            close: Whether to close position
            reduce_only: Whether to reduce position only
            tif: Time in force (gtc, ioc, poc, fok)
            text: Optional order text
            auto_size: Optional auto size
            stp_act: Optional self-trade prevention action

        Returns:
            Dict containing order placement result
        """

        path_params = {
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

        res = await self._request(
            method="POST",
            path=path_,
            path_params=path_params,
            body=body,
        )
        return res

    async def place_contract_market_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_order(
            product_symbol=product_symbol,
            size=size,
            price="0",
            tif="ioc",
            ccy=ccy,
            path=path,
        )

    async def place_contract_market_buy_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_market_order(
            product_symbol=product_symbol,
            size=abs(size),
            ccy=ccy,
            path=path,
        )

    async def place_contract_market_sell_order(
        self,
        product_symbol: str,
        size: int,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_market_order(
            product_symbol=product_symbol,
            size=-abs(size),  # negative size for sell
            ccy=ccy,
            path=path,
        )

    async def place_contract_limit_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_order(
            product_symbol=product_symbol,
            size=size,
            price=price,
            tif="gtc",
            ccy=ccy,
            path=path,
        )

    async def place_contract_limit_buy_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_limit_order(
            product_symbol=product_symbol,
            size=abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    async def place_contract_limit_sell_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_limit_order(
            product_symbol=product_symbol,
            size=-abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    async def place_contract_post_only_limit_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_order(
            product_symbol=product_symbol,
            size=size,
            price=price,
            tif="poc",
            ccy=ccy,
            path=path,
        )

    async def place_contract_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_post_only_limit_order(
            product_symbol=product_symbol,
            size=abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    async def place_contract_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: int,
        price: str,
        ccy: str = "usdt",
        path: str = "futures",
    ) -> dict[str, Any]:
        return await self.place_contract_post_only_limit_order(
            product_symbol=product_symbol,
            size=-abs(size),
            price=price,
            ccy=ccy,
            path=path,
        )

    async def place_futures_batch_order(
        self,
        orders: list[dict[str, Any]],
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        :param orders: list[dict]
        :param ccy: str
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

        path_params = {
            "settle": ccy,
        }

        res = await self._request(
            method="POST",
            path=FutureTrade.BATCH_FUTURES_ORDERS,
            path_params=path_params,
            body={"orders": orders},
        )
        return res

    async def get_contract_order_list(
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
        :param status: str
        :param ccy: str
        :param path: str
        :param product_symbol: str
        :param limit: int
        :param offset: int
        :param last_id: str
        :param count_total: int
        """
        path_params = {
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

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
        )
        return res

    async def cancel_contract_all_order_matched(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param ccy: str
        :param path: str
        :param side: str
        """
        path_params = {
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

        res = await self._request(
            method="DELETE",
            path=path_,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_contract_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        :param order_id: str
        :param ccy: str
        :param path: str
        """
        path_params = {
            "settle": ccy,
            "order_id": order_id,
        }

        if path == "futures":
            path_ = FutureTrade.SINGLE_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.SINGLE_ORDER
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
        )
        return res

    async def cancel_contract_single_order(
        self,
        order_id: str,
        ccy: str = "usdt",  # or "btc"
        path: str = "futures",
    ) -> dict[str, Any]:
        """
        :param order_id: str
        :param ccy: str
        :param path: str
        """
        path_params = {
            "settle": ccy,
            "order_id": order_id,
        }

        if path == "futures":
            path_ = FutureTrade.SINGLE_ORDER
        elif path == "delivery":
            path_ = DeliveryTrade.SINGLE_ORDER
        else:
            raise ValueError(f"Unsupported path: {path}")

        res = await self._request(
            method="DELETE",
            path=path_,
            path_params=path_params,
        )
        return res

    async def amend_futures_single_order(
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
        :param order_id: str
        :param ccy: str
        :param size: int
        :param price: str
        :param amend_text: str
        :param biz_info: str
        :param bbo: str
        """
        path_params = {
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

        res = await self._request(
            method="PUT",
            path=FutureTrade.SINGLE_ORDER,
            path_params=path_params,
            body=body,
        )
        return res

    async def get_trading_history(
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
        :param product_symbol: str
        :param ccy: str
        :param path: str
        :param order: str
        :param limit: int
        :param offset: int
        :param late_id: str
        :param count_total: int
        """
        path_params = {
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

        res = await self._request(
            method="GET",
            path=path_,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_futures_position_close_history(
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
        :param product_symbol: str
        :param ccy: str
        :param limit: int
        :param offset: int
        :param from_timestamp: int
        :param to_timestamp: int
        :param side: str
        :param pnl: str
        """
        path_params = {
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

        res = await self._request(
            method="GET",
            path=FutureTrade.LIST_POSITION_CLOSE_HISTORY,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_futures_auto_deleveraging_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
        at_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param ccy: str
        :param limit: int
        :param at_timestamp: int
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if limit is not None:
            payload["limit"] = limit
        if at_timestamp is not None:
            payload["at"] = at_timestamp

        res = await self._request(
            method="GET",
            path=FutureTrade.LIST_AUTODELEVERAGING_HISTORY,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_delivery_all_positions(
        self,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """
        :param ccy: str
        """
        path_params = {
            "settle": ccy,
        }

        res = await self._request(
            method="GET",
            path=DeliveryTrade.GET_ALL_POSITIONS,
            path_params=path_params,
        )
        return res

    async def update_delivery_positions_leverage(
        self,
        product_symbol: str,
        leverage: str,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param leverage: str
        :param ccy: str
        """
        path_params = {
            "settle": ccy,
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        payload: dict[str, Any] = {
            "leverage": leverage,
        }

        res = await self._request(
            method="POST",
            path=DeliveryTrade.UPDATE_POSITION_LEVERAGE,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_delivery_position_close_history(
        self,
        product_symbol: str,
        ccy: str = "usdt",  # or "btc"
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param ccy: str
        :param limit: int
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {
            "contract": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }

        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=DeliveryTrade.LIST_POSITION_CLOSE_HISTORY,
            path_params=path_params,
            query=payload,
        )
        return res

    async def place_spot_order(
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
            product_symbol: Product symbol
            side: Order side (buy or sell)
            amount: Order amount
            text: Optional order text
            order_type: Order type (limit or market)
            account: Account type (spot, margin, unified)
            price: Optional order price
            time_in_force: Time in force (gtc, ioc, poc, fok)
            iceberg: Optional iceberg order size
            auto_borrow: Whether to auto borrow
            auto_repay: Whether to auto repay
            stp_act: Optional self-trade prevention action
            action_mode: Action mode (ACK, RESULT, FULL)

        Returns:
            Dict containing order placement result
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

        res = await self._request(
            method="POST",
            path=SpotTrade.SPOT_ORDER,
            body=body,
        )
        return res

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
    ) -> dict[str, Any]:
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            order_type="market",
            time_in_force="ioc",
            amount=amount,
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        amount: str,
    ) -> dict[str, Any]:
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="buy",
            amount=amount,
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        amount: str,
    ) -> dict[str, Any]:
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="sell",
            amount=amount,
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            order_type="limit",
            amount=amount,
            price=price,
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="buy",
            amount=amount,
            price=price,
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="sell",
            amount=amount,
            price=price,
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            order_type="limit",
            time_in_force="poc",
            amount=amount,
            price=price,
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="buy",
            amount=amount,
            price=price,
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        amount: str,
        price: str,
    ) -> dict[str, Any]:
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="sell",
            amount=amount,
            price=price,
        )

    async def get_spot_open_orders(
        self,
        page: str | None = None,
        limit: str | None = None,
        account: str | None = None,
    ) -> dict[str, Any]:
        """
        :param page: str
        :param limit: str
        :param account: str
        """

        payload = {}

        if page is not None:
            payload["page"] = page
        if limit is not None:
            payload["limit"] = limit
        if account is not None:
            payload["account"] = account

        res = await self._request(
            method="GET",
            path=SpotTrade.GET_OPEN_ORDER,
            query=payload,
        )
        return res

    async def get_spot_order_list(
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
        :param product_symbol: str
        :param status: str
        :param page: str
        :param limit: str
        :param account: str
        :param from_timestamp: str
        :param to_timestamp: str
        :param side: str
        """

        payload = {
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

        res = await self._request(
            method="GET",
            path=SpotTrade.SPOT_ORDER,
            query=payload,
        )
        return res

    async def cancel_spot_order(
        self,
        product_symbol: str | None = None,
        side: str | None = None,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param side: str
        :param account: str
        :param action_mode: str
        """
        payload = {}
        if product_symbol is not None:
            payload["currency_pair"] = self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol)
        if side is not None:
            payload["side"] = side
        if account is not None:
            payload["account"] = account
        if action_mode is not None:
            payload["action_mode"] = action_mode

        res = await self._request(
            method="DELETE",
            path=SpotTrade.SPOT_ORDER,
            query=payload,
        )
        return res

    async def get_spot_single_order(
        self,
        order_id: str,
        product_symbol: str,
        account: str | None = None,
    ) -> dict[str, Any]:
        """
        :param order_id: str
        :param product_symbol: str
        :param account: str
        """
        path_params = {
            "order_id": order_id,
        }

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if account is not None:
            payload["account"] = account

        res = await self._request(
            method="GET",
            path=SpotTrade.SINGLE_ORDER,
            path_params=path_params,
            query=payload,
        )
        return res

    async def cancel_spot_single_order(
        self,
        order_id: str,
        product_symbol: str,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        :param order_id: str
        :param product_symbol: str
        :param account: str
        :param action_mode: str
        """
        path_params = {
            "order_id": order_id,
        }

        payload: dict[str, Any] = {
            "currency_pair": self.ptm.get_exchange_symbol(Common.GATEIO, product_symbol),
        }
        if account is not None:
            payload["account"] = account
        if action_mode is not None:
            payload["action_mode"] = action_mode

        res = await self._request(
            method="DELETE",
            path=SpotTrade.SINGLE_ORDER,
            path_params=path_params,
            query=payload,
        )
        return res

    async def amend_spot_single_order(
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
        :param order_id: str
        :param product_symbol: int
        :param account: str
        :param amount: str
        :param price: str
        :param amend_text: str
        :param action_mode: str
        """
        path_params = {
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

        res = await self._request(
            method="PATCH",
            path=SpotTrade.SINGLE_ORDER,
            path_params=path_params,
            body=body,
        )
        return res

    async def get_spot_trading_history(
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
        :param product_symbol: str
        :param limit: int
        :param page: int
        :param order_id: str
        :param account: str
        :param from_timestamp: int
        :param to_timestamp: int
        """
        payload = {}
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

        res = await self._request(
            method="GET",
            path=SpotTrade.LIST_PERSONAL_TRADING_HISTORY,
            query=payload,
        )
        return res
