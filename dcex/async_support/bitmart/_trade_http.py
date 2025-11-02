import asyncio
from typing import Any, cast

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """HTTP client for BitMart trade-related API endpoints."""

    async def place_spot_order(
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
        Place a spot order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (buy, sell)
            type: Order type (limit, market, limit_maker, ioc)
            size: Order size
            price: Order price
            notional: Order notional
            client_order_id: Client order ID

        Returns:
            dict: Order data
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "side": side,
            "type": type,
        }
        if size is not None:
            payload["size"] = str(size)
        if price is not None:
            payload["price"] = str(price)
        if notional is not None:
            payload["notional"] = notional
        if client_order_id is not None:
            payload["client_order_id"] = str(client_order_id)

        return await self._request(
            method="POST",
            path=SpotTrade.SUBMIT_ORDER,
            query=payload,
        )

    async def place_spot_market_order(
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
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (buy, sell)
            size: Order size
            notional: Order notional
            client_order_id: Client order ID

        Returns:
            dict: Order data
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type="market",
            size=size,
            notional=notional,
            client_order_id=client_order_id,
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        notional: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot market buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            notional: Order notional
            client_order_id: Client order ID

        Returns:
            dict: Order data
        """
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="buy",
            notional=notional,
            client_order_id=client_order_id,
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a spot market sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            size: Order size
            client_order_id: Client order ID

        Returns:
            dict: Order data
        """
        return await self.place_spot_market_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            client_order_id=client_order_id,
        )

    async def place_spot_limit_order(
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
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (buy, sell)
            size: Order size
            price: Order price
            client_order_id: Client order ID

        Returns:
            dict: Order data
        """
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type="limit",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_spot_limit_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_spot_order(
            product_symbol=product_symbol,
            side=side,
            type="limit_maker",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="buy",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_spot_post_only_limit_order(
            product_symbol=product_symbol,
            side="sell",
            size=size,
            price=price,
            client_order_id=client_order_id,
        )

    async def cancel_spot_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel a spot order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            order_id: Order ID
            client_order_id: Client order ID

        Returns:
            dict: Cancel order response
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if order_id is not None:
            payload["order_id"] = str(order_id)
        if client_order_id is not None:
            payload["client_order_id"] = str(client_order_id)

        return await self._request(
            method="POST",
            path=SpotTrade.CANCEL_ORDER,
            query=payload,
        )

    async def cancel_spot_all_order(
        self,
        product_symbol: str | None = None,
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all spot orders.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (buy, sell)

        Returns:
            dict: Cancel all orders response
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)
        if side is not None:
            payload["side"] = side

        return await self._request(
            method="POST",
            path=SpotTrade.CANCEL_ALL_ORDERS,
            query=payload,
        )

    async def place_margin_order(
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
        :param product_symbol: str
        :param side: str (buy, sell)
        :param type: str (limit, market, limit_maker, ioc)
        :param size: str
        :param price: str
        :param clientOrderId: str
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "side": side,
            "type": type,
        }
        if clientOrderId is not None:
            payload["clientOrderId"] = clientOrderId
        if size is not None:
            payload["size"] = str(size)
        if price is not None:
            payload["price"] = str(price)
        if notional is not None:
            payload["notional"] = notional

        return await self._request(
            method="POST",
            path=SpotTrade.NEW_MARGIN_ORDER,
            query=payload,
        )

    async def get_spot_order_by_order_id(
        self,
        orderId: str,
        queryState: str | None = None,
    ) -> dict[str, Any]:
        """
        :param orderId: str
        :param queryState: str (open, history)
        """
        payload = {
            "orderId": orderId,
        }
        if queryState is not None:
            payload["queryState"] = queryState

        res = await self._request(
            method="POST",
            path=SpotTrade.QUERY_ORDER_BY_ID,
            query=payload,
        )

        return res

    async def get_spot_order_by_order_client_id(
        self,
        clientOrderId: str,
        queryState: str | None = None,
    ) -> dict[str, Any]:
        """
        :param clientOrderId: str
        :param queryState: str (open, history)
        """
        payload = {
            "clientOrderId": clientOrderId,
        }
        if queryState is not None:
            payload["queryState"] = queryState

        res = await self._request(
            method="POST",
            path=SpotTrade.QUERY_ORDER_BY_CLIENT_ORDER_ID,
            query=payload,
        )

        return res

    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param orderMode: str (spot, iso_margin)
        :param startTime: int
        :param endTime: int
        :param limit: int
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
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

        res = await self._request(
            method="POST",
            path=SpotTrade.CURRENT_OPEN_ORDERS,
            query=payload,
        )

        return res

    async def get_spot_account_orders(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param orderMode: str (spot, iso_margin)
        :param startTime: int
        :param endTime: int
        :param limit: int
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
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

        res = await self._request(
            method="POST",
            path=SpotTrade.ACCOUNT_ORDERS,
            query=payload,
        )

        return res

    async def get_spot_account_trade_list(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param orderMode: str (spot, iso_margin)
        :param startTime: int
        :param endTime: int
        :param limit: int
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

        res = await self._request(
            method="POST",
            path=SpotTrade.ACCOUNT_TRADE_LIST,
            query=payload,
        )

        return res

    async def get_spot_order_trade_list(
        self,
        orderId: str,
    ) -> dict[str, Any]:
        """
        :param orderId: str
        """
        payload = {
            "orderId": orderId,
        }

        res = await self._request(
            method="POST",
            path=SpotTrade.ORDER_TRADE_LIST,
            query=payload,
        )

        return res

    async def place_contract_order(
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
        Place a contract order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (1=buy_open_long, 2=buy_close_short,
                3=sell_close_long, 4=sell_open_short)
            size: Order size
            price: Order price
            client_order_id: Client order ID
            type: Order type (limit, market)
            leverage: Leverage
            open_type: Open type (cross, isolated)
            mode: Order mode (1=GTC, 2=FOK, 3=IOC, 4=Maker Only)
            preset_take_profit_price_type: Pre-set TP price type (1=last_price, 2=fair_price)
            preset_stop_loss_price_type: Pre-set SL price type (1=last_price, 2=fair_price)
            preset_take_profit_price: Pre-set TP price
            preset_stop_loss_price: Pre-set SL price
            stp_mode: STP mode (1: cancel_maker, 2: cancel_taker, 3: cancel_both)

        Returns:
            dict: Order data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "side": side,
            "size": size,
        }
        if price is not None:
            payload["price"] = str(price)
        if client_order_id is not None:
            payload["client_order_id"] = str(client_order_id)
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

        return await self._request(
            method="POST",
            path=FuturesTrade.SUBMIT_ORDER,
            query=payload,
        )

    async def place_contract_market_order(
        self,
        product_symbol: str,
        side: int,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type="market",
            size=size,
            client_order_id=client_order_id,
        )

    async def place_contract_market_buy_order(
        self,
        product_symbol: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        res = await self.get_contract_position(product_symbol)
        positions: list[dict[str, Any]] = res.get("data", [])
        short_size = sum(int(p["current_amount"]) for p in positions if p["position_type"] == 2)

        if short_size != 0:
            excess_size = size - short_size
            if excess_size <= 0:
                return await self.place_contract_market_order(
                    product_symbol=product_symbol,
                    side=2,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return await asyncio.gather(
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
            return await self.place_contract_market_order(
                product_symbol=product_symbol,
                side=1,
                size=size,
                client_order_id=client_order_id,
            )

    async def place_contract_market_sell_order(
        self,
        product_symbol: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        res = await self.get_contract_position(product_symbol)
        positions: list[dict[str, Any]] = res.get("data", [])
        long_size = sum(int(p["current_amount"]) for p in positions if p["position_type"] == 1)

        if long_size != 0:
            excess_size = size - long_size
            if excess_size <= 0:
                return await self.place_contract_market_order(
                    product_symbol=product_symbol,
                    side=3,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return await asyncio.gather(
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
            return await self.place_contract_market_order(
                product_symbol=product_symbol,
                side=4,
                size=size,
                client_order_id=client_order_id,
            )

    async def place_contract_limit_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        size: int,
        client_order_id: str | None = None,
        mode: int | None = None,
    ) -> dict[str, Any]:
        return await self.place_contract_order(
            product_symbol=product_symbol,
            side=side,
            type="limit",
            price=price,
            size=size,
            client_order_id=client_order_id,
            mode=mode,
        )

    async def place_contract_post_only_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.place_contract_limit_order(
            product_symbol=product_symbol,
            side=side,
            price=price,
            size=size,
            client_order_id=client_order_id,
            mode=4,
        )

    async def place_contract_post_only_buy_order(
        self,
        product_symbol: str,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        positions: list[dict[str, Any]] = cast(
            list[dict[str, Any]], await self.get_contract_position(product_symbol)
        )
        short_size = sum(int(p["current_amount"]) for p in positions if p["position_type"] == 2)

        if short_size != 0:
            excess_size = size - short_size
            if excess_size <= 0:
                return await self.place_contract_post_only_order(
                    product_symbol=product_symbol,
                    side=2,
                    price=price,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return await asyncio.gather(
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
            return await self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=1,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )

    async def place_contract_post_only_sell_order(
        self,
        product_symbol: str,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        positions: list[dict[str, Any]] = cast(
            list[dict[str, Any]], await self.get_contract_position(product_symbol)
        )
        long_size = sum(int(p["current_amount"]) for p in positions if p["position_type"] == 1)

        if long_size != 0:
            excess_size = size - long_size
            if excess_size <= 0:
                return await self.place_contract_post_only_order(
                    product_symbol=product_symbol,
                    side=3,
                    price=price,
                    size=size,
                    client_order_id=client_order_id,
                )
            else:
                return await asyncio.gather(
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
            return await self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=4,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )

    async def modify_limit_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
        price: int | None = None,
        size: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param order_id: str
        :param client_order_id: str
        :param price: int
        :param size: int
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if order_id is not None:
            payload["order_id"] = str(order_id)
        if client_order_id is not None:
            payload["client_order_id"] = str(client_order_id)
        if price is not None:
            payload["price"] = str(price)
        if size is not None:
            payload["size"] = str(size)

        return await self._request(
            method="POST",
            path=FuturesTrade.MODIFY_LIMIT_ORDER,
            query=payload,
        )

    async def cancel_contract_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel a contract order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            order_id: Order ID
            client_order_id: Client order ID

        Returns:
            dict: Cancel order response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if order_id is not None:
            payload["order_id"] = str(order_id)
        if client_order_id is not None:
            payload["client_order_id"] = str(client_order_id)

        return await self._request(
            method="POST",
            path=FuturesTrade.CANCEL_ORDER,
            query=payload,
        )

    async def cancel_all_contract_order(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }

        return await self._request(
            method="POST",
            path=FuturesTrade.CANCEL_ALL_ORDERS,
            query=payload,
        )

    async def transfer_contract(
        self,
        amount: str,
        type: str,
    ) -> dict[str, Any]:
        """
        :param currency: str
        :param amount: str
        :param type: str (spot_to_contract, contract_to_spot)
        """
        payload = {
            "currency": "USDT",
            "amount": amount,
            "type": type,
        }

        return await self._request(
            method="POST",
            path=FuturesTrade.TRANSFER,
            query=payload,
        )

    async def submit_leverage(
        self,
        product_symbol: str,
        leverage: str | None = None,
        open_type: str | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param leverage: str
        :param open_type: str (cross, isolated)
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if leverage is not None:
            payload["leverage"] = leverage
        if open_type is not None:
            payload["open_type"] = open_type

        return await self._request(
            method="POST",
            path=FuturesTrade.SUBMIT_LEVERAGE,
            query=payload,
        )

    async def get_contract_order_detail(
        self,
        product_symbol: str,
        order_id: str,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param order_id: str
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
            "order_id": order_id,
        }

        res = await self._request(
            method="GET",
            path=FuturesTrade.GET_ORDER_DETAIL,
            query=payload,
        )
        return res

    async def get_contract_order_history(
        self,
        product_symbol: str,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param start_time: str
        :param end_time: str
        """
        if self.ptm is None:
            raise RuntimeError("ProductTableManager not initialized")
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time

        res = await self._request(
            method="GET",
            path=FuturesTrade.GET_ORDER_HISTORY,
            query=payload,
        )
        return res

    async def get_contract_open_order(
        self,
        product_symbol: str | None = None,
        type: str | None = None,
        order_state: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param type: str (limit, market, trailing)
        :param order_state: str (all(async default), partially_filled)
        :param limit: int
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

        res = await self._request(
            method="GET",
            path=FuturesTrade.GET_ALL_OPEN_ORDERS,
            query=payload,
        )
        return res

    async def get_contract_position(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get contract position.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Contract position data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BITMART, product_symbol)

        res = await self._request(
            method="GET",
            path=FuturesTrade.GET_CURRENT_POSITION,
            query=payload,
        )
        return res

    async def get_contract_trade(
        self,
        product_symbol: str,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param start_time: str
        :param end_time: str
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMART, product_symbol),
        }
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time

        res = await self._request(
            method="GET",
            path=FuturesTrade.GET_ORDER_TRADE,
            query=payload,
        )

        return res

    async def get_contract_transaction_history(
        self,
        product_symbol: str | None = None,
        flow_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        :param product_symbol: str
        :param flow_type: int (0 = All (async default), 1 = Transfer, 2 = Realized PNL,
            3 = Funding Fee, 4 = Commission Fee, 5 = Liquidation)
        :param start_time: int
        :param end_time: int
        :param page_size: int
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

        res = await self._request(
            method="GET",
            path=FuturesTrade.GET_TRANSACTION_HISTORY,
            query=payload,
        )

        return res

    async def get_contract_transfer_list(
        self,
        page: int,
        limit: int,
        currency: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """
        :param page: int
        :param limit: int
        :param currency: str
        :param start_time: int
        :param end_time: int
        """
        payload: dict[str, Any] = {
            "page": page,
            "limit": limit,
        }
        if currency is not None:
            payload["currency"] = currency
        if start_time is not None:
            payload["time_start"] = start_time
        if end_time is not None:
            payload["time_end"] = end_time

        res = await self._request(
            method="POST",
            path=FuturesTrade.GET_TRANSFER_LIST,
            query=payload,
        )

        return res
