"""Bitmart trading HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """
    Trading HTTP client for Bitmart.

    This class provides methods for spot and futures trading operations
    including order placement, cancellation, querying, and position management.
    """

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type: str,
        size: str | None = None,
        price: str | None = None,
        notional: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot trading order.

        Args:
            product_symbol: Trading pair symbol
            side: Order side ("buy" or "sell")
            type: Order type ("limit", "market", "limit_maker", "ioc")
            size: Order size (optional)
            price: Order price (optional)
            notional: Order notional amount (optional)
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "side": side,
            "type": type,
        }
        if size is not None:
            payload["size"] = size
        if price is not None:
            payload["price"] = price
        if notional is not None:
            payload["notional"] = notional
        if client_order_id is not None:
            payload["client_order_id"] = client_order_id

        return self._request(
            method="POST",
            path=SpotTrade.SUBMIT_ORDER,
            query=payload,
        )

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str | None = None,
        notional: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot market order.

        Args:
            product_symbol: Trading pair symbol
            side: Order side ("buy" or "sell")
            size: Order size (optional)
            notional: Order notional amount (optional)
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type="market",
            size=size,
            notional=notional,
            client_order_id=client_order_id,
        )

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        notional: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot market buy order.

        Args:
            product_symbol: Trading pair symbol
            notional: Order notional amount
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_market_order(
            product_symbol=product_symbol,
            side="buy",
            notional=notional,
            client_order_id=client_order_id,
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot market sell order.

        Args:
            product_symbol: Trading pair symbol
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_market_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            client_order_id=client_order_id,
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot limit order.

        Args:
            product_symbol: Trading pair symbol
            side: Order side ("buy" or "sell")
            size: Order size
            price: Order price
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type="limit",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot limit buy order.

        Args:
            product_symbol: Trading pair symbol
            size: Order size
            price: Order price
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot limit sell order.

        Args:
            product_symbol: Trading pair symbol
            size: Order size
            price: Order price
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot post-only limit order.

        Args:
            product_symbol: Trading pair symbol
            side: Order side ("buy" or "sell")
            size: Order size
            price: Order price
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type="limit_maker",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot post-only limit buy order.

        Args:
            product_symbol: Trading pair symbol
            size: Order size
            price: Order price
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot post-only limit sell order.

        Args:
            product_symbol: Trading pair symbol
            size: Order size
            price: Order price
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    def cancel_spot_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel a spot order.

        Args:
            product_symbol: Trading pair symbol
            order_id: Order ID (optional)
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing cancellation result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if order_id is not None:
            payload["order_id"] = order_id
        if client_order_id is not None:
            payload["client_order_id"] = client_order_id

        return self._request(
            method="POST",
            path=SpotTrade.CANCEL_ORDER,
            query=payload,
        )

    def cancel_spot_all_order(
        self,
        product_symbol: str | None = None,
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all spot orders.

        Args:
            product_symbol: Trading pair symbol (optional)
            side: Order side (optional)

        Returns:
            Dict containing cancellation result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if side is not None:
            payload["side"] = side

        return self._request(
            method="POST",
            path=SpotTrade.CANCEL_ALL_ORDERS,
            query=payload,
        )

    def place_margin_order(
        self,
        product_symbol: str,
        side: str,
        type: str,
        size: str | None = None,
        price: str | None = None,
        notional: str | None = None,
        clientOrderId: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a margin trading order.

        Args:
            product_symbol: Trading pair symbol
            side: Order side ("buy" or "sell")
            type: Order type ("limit", "market", "limit_maker", "ioc")
            size: Order size (optional)
            price: Order price (optional)
            notional: Order notional amount (optional)
            clientOrderId: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "side": side,
            "type": type,
        }
        if clientOrderId is not None:
            payload["clientOrderId"] = clientOrderId
        if size is not None:
            payload["size"] = size
        if price is not None:
            payload["price"] = price
        if notional is not None:
            payload["notional"] = notional

        return self._request(
            method="POST",
            path=SpotTrade.NEW_MARGIN_ORDER,
            query=payload,
        )

    def get_spot_order_by_order_id(
        self,
        orderId: str,
        queryState: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot order details by order ID.

        Args:
            orderId: Order ID
            queryState: Query state ("open" or "history", optional)

        Returns:
            Dict containing order details

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "orderId": orderId,
        }
        if queryState is not None:
            payload["queryState"] = queryState

        res = self._request(
            method="POST",
            path=SpotTrade.QUERY_ORDER_BY_ID,
            query=payload,
        )

        return res

    def get_spot_order_by_order_client_id(
        self,
        clientOrderId: str,
        queryState: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot order details by client order ID.

        Args:
            clientOrderId: Client order ID
            queryState: Query state ("open" or "history", optional)

        Returns:
            Dict containing order details

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "clientOrderId": clientOrderId,
        }
        if queryState is not None:
            payload["queryState"] = queryState

        res = self._request(
            method="POST",
            path=SpotTrade.QUERY_ORDER_BY_CLIENT_ORDER_ID,
            query=payload,
        )

        return res

    def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get current open spot orders.

        Args:
            product_symbol: Trading pair symbol (optional)
            orderMode: Order mode ("spot" or "iso_margin", optional)
            startTime: Start timestamp (optional)
            endTime: End timestamp (optional)
            limit: Maximum number of records (optional)

        Returns:
            Dict containing open orders information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if orderMode is not None:
            payload["orderMode"] = orderMode
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="POST",
            path=SpotTrade.CURRENT_OPEN_ORDERS,
            query=payload,
        )

        return res

    def get_spot_account_orders(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get spot account order history.

        Args:
            product_symbol: Trading pair symbol (optional)
            orderMode: Order mode ("spot" or "iso_margin", optional)
            startTime: Start timestamp (optional)
            endTime: End timestamp (optional)
            limit: Maximum number of records (optional)

        Returns:
            Dict containing order history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if orderMode is not None:
            payload["orderMode"] = orderMode
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="POST",
            path=SpotTrade.ACCOUNT_ORDERS,
            query=payload,
        )

        return res

    def get_spot_account_trade_list(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get spot account trade history.

        Args:
            product_symbol: Trading pair symbol (optional)
            orderMode: Order mode ("spot" or "iso_margin", optional)
            startTime: Start timestamp (optional)
            endTime: End timestamp (optional)
            limit: Maximum number of records (optional)

        Returns:
            Dict containing trade history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if orderMode is not None:
            payload["orderMode"] = orderMode
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="POST",
            path=SpotTrade.ACCOUNT_TRADE_LIST,
            query=payload,
        )

        return res

    def get_spot_order_trade_list(
        self,
        orderId: str,
    ) -> dict[str, Any]:
        """
        Get trade list for a specific spot order.

        Args:
            orderId: Order ID

        Returns:
            Dict containing trade list for the order

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "orderId": orderId,
        }

        res = self._request(
            method="POST",
            path=SpotTrade.ORDER_TRADE_LIST,
            query=payload,
        )

        return res

    def place_contract_order(
        self,
        product_symbol: str,
        side: int,
        size: int,
        price: str | None = None,
        client_order_id: str | None = None,
        type: str | None = None,
        leverage: str | None = None,
        open_type: str | None = None,
        mode: int | None = None,
        preset_take_profit_price_type: int | None = None,
        preset_stop_loss_price_type: int | None = None,
        preset_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        stp_mode: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a futures contract order.

        Args:
            product_symbol: Contract symbol
            side: Order side (1=buy_open_long, 2=buy_close_short,
                3=sell_close_long, 4=sell_open_short)
            size: Order size
            price: Order price (optional)
            client_order_id: Client order ID (optional)
            type: Order type ("limit" or "market", optional)
            leverage: Leverage (optional)
            open_type: Open type ("cross" or "isolated", optional)
            mode: Order mode (1=GTC, 2=FOK, 3=IOC, 4=Maker Only, optional)
            preset_take_profit_price_type: Pre-set TP price type
                (1=last_price, 2=fair_price, optional)
            preset_stop_loss_price_type: Pre-set SL price type
                (1=last_price, 2=fair_price, optional)
            preset_take_profit_price: Pre-set TP price (optional)
            preset_stop_loss_price: Pre-set SL price (optional)
            stp_mode: STP mode (1: cancel_maker, 2: cancel_taker,
                3: cancel_both, optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "side": side,
            "size": size,
        }
        if price is not None:
            payload["price"] = price
        if client_order_id is not None:
            payload["client_order_id"] = client_order_id
        if type is not None:
            payload["type"] = type
        if leverage is not None:
            payload["leverage"] = leverage
        if open_type is not None:
            payload["open_type"] = open_type
        if mode is not None:
            payload["mode"] = mode
        if preset_take_profit_price_type is not None:
            payload["preset_take_profit_price_type"] = preset_take_profit_price_type
        if preset_stop_loss_price_type is not None:
            payload["preset_stop_loss_price_type"] = preset_stop_loss_price_type
        if preset_take_profit_price is not None:
            payload["preset_take_profit_price"] = preset_take_profit_price
        if preset_stop_loss_price is not None:
            payload["preset_stop_loss_price"] = preset_stop_loss_price
        if stp_mode is not None:
            payload["stp_mode"] = stp_mode

        return self._request(
            method="POST",
            path=FuturesTrade.SUBMIT_ORDER,
            query=payload,
        )

    def place_contract_market_order(
        self,
        product_symbol: str,
        side: int,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a futures contract market order.

        Args:
            product_symbol: Contract symbol
            side: Order side (1=buy_open_long, 2=buy_close_short,
                3=sell_close_long, 4=sell_open_short)
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type="market",
            size=size,
            client_order_id=client_order_id,
        )

    def place_contract_market_buy_order(
        self,
        product_symbol: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """
        Place a futures contract market buy order with position management.

        Args:
            product_symbol: Contract symbol
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result or tuple of results

        Raises:
            FailedRequestError: If the API request fails
        """
        positions = self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        short_size = sum(
            int(p.get("current_amount", 0)) for p in positions_list if p.get("position_type") == 2
        )

        if short_size != 0:
            excess_size = size - short_size
            if excess_size <= 0:
                return self.place_contract_market_order(
                    product_symbol=product_symbol,
                    side=2,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return (
                    self.place_contract_market_order(
                        product_symbol=product_symbol,
                        side=2,
                        size=short_size,
                        client_order_id=client_order_id,
                    ),
                    self.place_contract_market_order(
                        product_symbol=product_symbol,
                        side=1,
                        size=excess_size,
                        client_order_id=client_order_id,
                    ),
                )
        else:
            return self.place_contract_market_order(
                product_symbol=product_symbol,
                side=1,
                size=size,
                client_order_id=client_order_id,
            )

    def place_contract_market_sell_order(
        self,
        product_symbol: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """
        Place a futures contract market sell order with position management.

        Args:
            product_symbol: Contract symbol
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result or tuple of results

        Raises:
            FailedRequestError: If the API request fails
        """
        positions = self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        long_size = sum(
            int(p.get("current_amount", 0)) for p in positions_list if p.get("position_type") == 1
        )

        if long_size != 0:
            excess_size = size - long_size
            if excess_size <= 0:
                return self.place_contract_market_order(
                    product_symbol=product_symbol,
                    side=3,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return (
                    self.place_contract_market_order(
                        product_symbol=product_symbol,
                        side=3,
                        size=long_size,
                        client_order_id=client_order_id,
                    ),
                    self.place_contract_market_order(
                        product_symbol=product_symbol,
                        side=4,
                        size=excess_size,
                        client_order_id=client_order_id,
                    ),
                )
        else:
            return self.place_contract_market_order(
                product_symbol=product_symbol,
                side=4,
                size=size,
                client_order_id=client_order_id,
            )

    def place_contract_limit_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        size: int,
        client_order_id: str | None = None,
        mode: int | None = None,
    ) -> dict[str, Any]:
        """
        Place a futures contract limit order.

        Args:
            product_symbol: Contract symbol
            side: Order side (1=buy_open_long, 2=buy_close_short,
                3=sell_close_long, 4=sell_open_short)
            price: Order price
            size: Order size
            client_order_id: Client order ID (optional)
            mode: Order mode (1=GTC, 2=FOK, 3=IOC, 4=Maker Only, optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type="limit",
            price=price,
            size=size,
            client_order_id=client_order_id,
            mode=mode,
        )

    def place_contract_post_only_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a futures contract post-only order.

        Args:
            product_symbol: Contract symbol
            side: Order side (1=buy_open_long, 2=buy_close_short,
                3=sell_close_long, 4=sell_open_short)
            price: Order price
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result

        Raises:
            FailedRequestError: If the API request fails
        """
        return self.place_contract_limit_order(
            product_symbol=product_symbol,
            side=side,
            price=price,
            size=size,
            client_order_id=client_order_id,
            mode=4,
        )

    def place_contract_post_only_buy_order(
        self,
        product_symbol: str,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """
        Place a futures contract post-only buy order with position management.

        Args:
            product_symbol: Contract symbol
            price: Order price
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result or tuple of results

        Raises:
            FailedRequestError: If the API request fails
        """
        positions = self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        short_size = sum(
            int(p.get("current_amount", 0)) for p in positions_list if p.get("position_type") == 2
        )

        if short_size != 0:
            excess_size = size - short_size
            if excess_size <= 0:
                return self.place_contract_post_only_order(
                    product_symbol=product_symbol,
                    side=2,
                    price=price,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return (
                    self.place_contract_post_only_order(
                        product_symbol=product_symbol,
                        side=2,
                        price=price,
                        size=short_size,
                        client_order_id=client_order_id,
                    ),
                    self.place_contract_post_only_order(
                        product_symbol=product_symbol,
                        side=1,
                        price=price,
                        size=excess_size,
                        client_order_id=client_order_id,
                    ),
                )
        else:
            return self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=1,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )

    def place_contract_post_only_sell_order(
        self,
        product_symbol: str,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """
        Place a futures contract post-only sell order with position management.

        Args:
            product_symbol: Contract symbol
            price: Order price
            size: Order size
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing order placement result or tuple of results

        Raises:
            FailedRequestError: If the API request fails
        """
        positions = self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        long_size = sum(
            int(p.get("current_amount", 0)) for p in positions_list if p.get("position_type") == 1
        )

        if long_size != 0:
            excess_size = size - long_size
            if excess_size <= 0:
                return self.place_contract_post_only_order(
                    product_symbol=product_symbol,
                    side=3,
                    price=price,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return (
                    self.place_contract_post_only_order(
                        product_symbol=product_symbol,
                        side=3,
                        price=price,
                        size=long_size,
                        client_order_id=client_order_id,
                    ),
                    self.place_contract_post_only_order(
                        product_symbol=product_symbol,
                        side=4,
                        price=price,
                        size=excess_size,
                        client_order_id=client_order_id,
                    ),
                )
        else:
            return self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=4,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )

    def modify_limit_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
        price: int | None = None,
        size: int | None = None,
    ) -> dict[str, Any]:
        """
        Modify a futures contract limit order.

        Args:
            product_symbol: Contract symbol
            order_id: Order ID (optional)
            client_order_id: Client order ID (optional)
            price: New order price (optional)
            size: New order size (optional)

        Returns:
            Dict containing modification result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if order_id is not None:
            payload["order_id"] = order_id
        if client_order_id is not None:
            payload["client_order_id"] = client_order_id
        if price is not None:
            payload["price"] = str(price)
        if size is not None:
            payload["size"] = str(size)

        return self._request(
            method="POST",
            path=FuturesTrade.MODIFY_LIMIT_ORDER,
            query=payload,
        )

    def cancel_contract_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel a futures contract order.

        Args:
            product_symbol: Contract symbol
            order_id: Order ID (optional)
            client_order_id: Client order ID (optional)

        Returns:
            Dict containing cancellation result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if order_id is not None:
            payload["order_id"] = order_id
        if client_order_id is not None:
            payload["client_order_id"] = client_order_id

        return self._request(
            method="POST",
            path=FuturesTrade.CANCEL_ORDER,
            query=payload,
        )

    def cancel_all_contract_order(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Cancel all futures contract orders.

        Args:
            product_symbol: Contract symbol

        Returns:
            Dict containing cancellation result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        return self._request(
            method="POST",
            path=FuturesTrade.CANCEL_ALL_ORDERS,
            query=payload,
        )

    def transfer_contract(
        self,
        amount: str,
        type: str,
    ) -> dict[str, Any]:
        """
        Transfer funds between spot and futures accounts.

        Args:
            amount: Transfer amount
            type: Transfer type ("spot_to_contract" or "contract_to_spot")

        Returns:
            Dict containing transfer result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "currency": "USDT",
            "amount": amount,
            "type": type,
        }

        return self._request(
            method="POST",
            path=FuturesTrade.TRANSFER,
            query=payload,
        )

    def submit_leverage(
        self,
        product_symbol: str,
        leverage: str | None = None,
        open_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Submit leverage settings for futures contract.

        Args:
            product_symbol: Contract symbol
            leverage: Leverage value (optional)
            open_type: Open type ("cross" or "isolated", optional)

        Returns:
            Dict containing leverage submission result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if leverage is not None:
            payload["leverage"] = leverage
        if open_type is not None:
            payload["open_type"] = open_type

        return self._request(
            method="POST",
            path=FuturesTrade.SUBMIT_LEVERAGE,
            query=payload,
        )

    def get_contract_order_detail(
        self,
        product_symbol: str,
        order_id: str,
    ) -> dict[str, Any]:
        """
        Get futures contract order details.

        Args:
            product_symbol: Contract symbol
            order_id: Order ID

        Returns:
            Dict containing order details

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "order_id": order_id,
        }

        res = self._request(
            method="GET",
            path=FuturesTrade.GET_ORDER_DETAIL,
            query=payload,
        )

        return res

    def get_contract_order_history(
        self,
        product_symbol: str,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures contract order history.

        Args:
            product_symbol: Contract symbol
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)

        Returns:
            Dict containing order history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time

        res = self._request(
            method="GET",
            path=FuturesTrade.GET_ORDER_HISTORY,
            query=payload,
        )

        return res

    def get_contract_open_order(
        self,
        product_symbol: str | None = None,
        type: str | None = None,
        order_state: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get current open futures contract orders.

        Args:
            product_symbol: Contract symbol (optional)
            type: Order type ("limit", "market", "trailing", optional)
            order_state: Order state ("all" or "partially_filled", optional)
            limit: Maximum number of records (optional)

        Returns:
            Dict containing open orders information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if type is not None:
            payload["type"] = type
        if order_state is not None:
            payload["order_state"] = order_state
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="GET",
            path=FuturesTrade.GET_ALL_OPEN_ORDERS,
            query=payload,
        )

        return res

    def get_contract_position(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get current futures contract positions.

        Args:
            product_symbol: Contract symbol (optional)

        Returns:
            Dict containing position information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)

        res = self._request(
            method="GET",
            path=FuturesTrade.GET_CURRENT_POSITION,
            query=payload,
        )
        return res

    def get_contract_trade(
        self,
        product_symbol: str,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures contract trade history.

        Args:
            product_symbol: Contract symbol
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)

        Returns:
            Dict containing trade history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time

        res = self._request(
            method="GET",
            path=FuturesTrade.GET_ORDER_TRADE,
            query=payload,
        )
        return res

    def get_contract_transaction_history(
        self,
        product_symbol: str | None = None,
        flow_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Get futures contract transaction history.

        Args:
            product_symbol: Contract symbol (optional)
            flow_type: Flow type (0=All, 1=Transfer, 2=Realized PNL,
                3=Funding Fee, 4=Commission Fee, 5=Liquidation, optional)
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)
            page_size: Page size (optional)

        Returns:
            Dict containing transaction history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if flow_type is not None:
            payload["flow_type"] = flow_type
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time
        if page_size is not None:
            payload["page_size"] = page_size

        res = self._request(
            method="GET",
            path=FuturesTrade.GET_TRANSACTION_HISTORY,
            query=payload,
        )
        return res

    def get_contract_transfer_list(
        self,
        page: int,
        limit: int,
        currency: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """
        Get futures contract transfer list.

        Args:
            page: Page number
            limit: Number of records per page
            currency: Currency symbol (optional)
            start_time: Start timestamp (optional)
            end_time: End timestamp (optional)

        Returns:
            Dict containing transfer list

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "page": page,
            "limit": limit,
        }
        if currency is not None:
            payload["currency"] = str(currency)
        if start_time is not None:
            payload["time_start"] = start_time
        if end_time is not None:
            payload["time_end"] = end_time

        res = self._request(
            method="POST",
            path=FuturesTrade.GET_TRANSFER_LIST,
            query=payload,
        )
        return res
