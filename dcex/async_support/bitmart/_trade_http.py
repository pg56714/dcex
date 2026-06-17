"""BitMart async private trading HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for BitMart private trading APIs."""

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        type: str,  # noqa: A002
        size: str | None = None,
        price: str | None = None,
        notional: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot order."""
        return await self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type=type,
                size=size,
                price=price,
                notional=notional,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str | None = None,
        notional: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot market order."""
        return await self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                notional=notional,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        notional: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot market buy order."""
        return await self._native_private(
            "place_spot_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                notional=notional,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot market sell order."""
        return await self._native_private(
            "place_spot_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot limit order."""
        return await self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot limit buy order."""
        return await self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot limit sell order."""
        return await self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot post-only limit order."""
        return await self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot post-only limit buy order."""
        return await self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                client_order_id=client_order_id,
            ),
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart Spot post-only limit sell order."""
        return await self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                client_order_id=client_order_id,
            ),
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Alias for BitMart Spot post-only limit sell order."""
        return await self.place_spot_post_only_limit_sell_order(
            product_symbol=product_symbol,
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
        """Cancel a BitMart Spot order."""
        return await self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                order_id=order_id,
                client_order_id=client_order_id,
            ),
        )

    async def cancel_spot_all_order(
        self,
        product_symbol: str | None = None,
        side: str | None = None,
    ) -> dict[str, Any]:
        """Cancel BitMart Spot open orders."""
        return await self._native_private(
            "cancel_spot_all_order",
            self._native_params(product_symbol=product_symbol, side=side),
        )

    async def get_spot_order_by_order_id(
        self,
        orderId: str,
        queryState: str | None = None,
    ) -> dict[str, Any]:
        """Get a BitMart Spot order by order id."""
        return await self._native_private(
            "get_spot_order_by_order_id",
            self._native_params(orderId=orderId, queryState=queryState),
        )

    async def get_spot_order_by_order_client_id(
        self,
        clientOrderId: str,
        queryState: str | None = None,
    ) -> dict[str, Any]:
        """Get a BitMart Spot order by client order id."""
        return await self._native_private(
            "get_spot_order_by_order_client_id",
            self._native_params(clientOrderId=clientOrderId, queryState=queryState),
        )

    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart Spot open orders."""
        return await self._native_private(
            "get_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderMode=orderMode,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_account_orders(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart Spot order history."""
        return await self._native_private(
            "get_spot_account_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderMode=orderMode,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_account_trade_list(
        self,
        product_symbol: str | None = None,
        orderMode: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart Spot trade history."""
        return await self._native_private(
            "get_spot_account_trade_list",
            self._native_params(
                product_symbol=product_symbol,
                orderMode=orderMode,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_order_trade_list(self, orderId: str) -> dict[str, Any]:
        """Get BitMart Spot trades for an order."""
        return await self._native_private(
            "get_spot_order_trade_list",
            self._native_params(orderId=orderId),
        )

    async def place_contract_order(
        self,
        product_symbol: str,
        side: int,
        size: int,
        price: str | None = None,
        client_order_id: str | None = None,
        type: str | None = None,  # noqa: A002
        leverage: str | None = None,
        open_type: str | None = None,
        mode: int | None = None,
        preset_take_profit_price_type: str | None = None,
        preset_stop_loss_price_type: str | None = None,
        preset_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        stp_mode: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart contract order."""
        return await self._native_private(
            "place_contract_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                client_order_id=client_order_id,
                type=type,
                leverage=leverage,
                open_type=open_type,
                mode=mode,
                preset_take_profit_price_type=preset_take_profit_price_type,
                preset_stop_loss_price_type=preset_stop_loss_price_type,
                preset_take_profit_price=preset_take_profit_price,
                preset_stop_loss_price=preset_stop_loss_price,
                stp_mode=stp_mode,
            ),
        )

    async def place_contract_market_order(
        self,
        product_symbol: str,
        side: int,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart contract market order."""
        return await self._native_private(
            "place_contract_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                client_order_id=client_order_id,
            ),
        )

    async def place_contract_market_buy_order(
        self,
        product_symbol: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """Place a BitMart contract market buy order, closing shorts first."""
        positions = await self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        short_size = sum(
            int(position.get("current_amount", 0))
            for position in positions_list
            if position.get("position_type") == 2
        )
        if short_size == 0:
            return await self.place_contract_market_order(
                product_symbol=product_symbol,
                side=1,
                size=size,
                client_order_id=client_order_id,
            )
        excess_size = size - short_size
        if excess_size <= 0:
            return await self.place_contract_market_order(
                product_symbol=product_symbol,
                side=2,
                size=size,
                client_order_id=client_order_id,
            )
        close_result = await self.place_contract_market_order(
            product_symbol=product_symbol,
            side=2,
            size=short_size,
            client_order_id=client_order_id,
        )
        open_result = await self.place_contract_market_order(
            product_symbol=product_symbol,
            side=1,
            size=excess_size,
            client_order_id=client_order_id,
        )
        return close_result, open_result

    async def place_contract_market_sell_order(
        self,
        product_symbol: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """Place a BitMart contract market sell order, closing longs first."""
        positions = await self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        long_size = sum(
            int(position.get("current_amount", 0))
            for position in positions_list
            if position.get("position_type") == 1
        )
        if long_size == 0:
            return await self.place_contract_market_order(
                product_symbol=product_symbol,
                side=4,
                size=size,
                client_order_id=client_order_id,
            )
        excess_size = size - long_size
        if excess_size <= 0:
            return await self.place_contract_market_order(
                product_symbol=product_symbol,
                side=3,
                size=size,
                client_order_id=client_order_id,
            )
        close_result = await self.place_contract_market_order(
            product_symbol=product_symbol,
            side=3,
            size=long_size,
            client_order_id=client_order_id,
        )
        open_result = await self.place_contract_market_order(
            product_symbol=product_symbol,
            side=4,
            size=excess_size,
            client_order_id=client_order_id,
        )
        return close_result, open_result

    async def place_contract_limit_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        size: int,
        client_order_id: str | None = None,
        mode: int | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart contract limit order."""
        return await self._native_private(
            "place_contract_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                price=price,
                size=size,
                client_order_id=client_order_id,
                mode=mode,
            ),
        )

    async def place_contract_post_only_order(
        self,
        product_symbol: str,
        side: int,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Place a BitMart contract post-only order."""
        return await self._native_private(
            "place_contract_post_only_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                price=price,
                size=size,
                client_order_id=client_order_id,
            ),
        )

    async def place_contract_post_only_buy_order(
        self,
        product_symbol: str,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """Place a BitMart contract post-only buy order, closing shorts first."""
        positions = await self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        short_size = sum(
            int(position.get("current_amount", 0))
            for position in positions_list
            if position.get("position_type") == 2
        )
        if short_size == 0:
            return await self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=1,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )
        excess_size = size - short_size
        if excess_size <= 0:
            return await self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=2,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )
        close_result = await self.place_contract_post_only_order(
            product_symbol=product_symbol,
            side=2,
            price=price,
            size=short_size,
            client_order_id=client_order_id,
        )
        open_result = await self.place_contract_post_only_order(
            product_symbol=product_symbol,
            side=1,
            price=price,
            size=excess_size,
            client_order_id=client_order_id,
        )
        return close_result, open_result

    async def place_contract_post_only_sell_order(
        self,
        product_symbol: str,
        price: str,
        size: int,
        client_order_id: str | None = None,
    ) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
        """Place a BitMart contract post-only sell order, closing longs first."""
        positions = await self.get_contract_position(product_symbol)
        positions_list = positions.get("data", []) if isinstance(positions, dict) else positions
        long_size = sum(
            int(position.get("current_amount", 0))
            for position in positions_list
            if position.get("position_type") == 1
        )
        if long_size == 0:
            return await self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=4,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )
        excess_size = size - long_size
        if excess_size <= 0:
            return await self.place_contract_post_only_order(
                product_symbol=product_symbol,
                side=3,
                price=price,
                size=size,
                client_order_id=client_order_id,
            )
        close_result = await self.place_contract_post_only_order(
            product_symbol=product_symbol,
            side=3,
            price=price,
            size=long_size,
            client_order_id=client_order_id,
        )
        open_result = await self.place_contract_post_only_order(
            product_symbol=product_symbol,
            side=4,
            price=price,
            size=excess_size,
            client_order_id=client_order_id,
        )
        return close_result, open_result

    async def modify_limit_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
        price: str | None = None,
        size: int | None = None,
    ) -> dict[str, Any]:
        """Modify a BitMart contract limit order."""
        return await self._native_private(
            "modify_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                order_id=order_id,
                client_order_id=client_order_id,
                price=price,
                size=size,
            ),
        )

    async def cancel_contract_order(
        self,
        product_symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a BitMart contract order."""
        return await self._native_private(
            "cancel_contract_order",
            self._native_params(
                product_symbol=product_symbol,
                order_id=order_id,
                client_order_id=client_order_id,
            ),
        )

    async def cancel_all_contract_order(self, product_symbol: str) -> dict[str, Any]:
        """Cancel BitMart contract open orders."""
        return await self._native_private(
            "cancel_all_contract_order",
            self._native_params(product_symbol=product_symbol),
        )

    async def transfer_contract(self, amount: str, type: str) -> dict[str, Any]:  # noqa: A002
        """Transfer USDT between BitMart Spot and contract accounts."""
        return await self._native_private(
            "transfer_contract",
            self._native_params(amount=amount, type=type),
        )

    async def submit_leverage(
        self,
        product_symbol: str,
        leverage: str | None = None,
        open_type: str | None = None,
    ) -> dict[str, Any]:
        """Submit BitMart contract leverage."""
        return await self._native_private(
            "submit_leverage",
            self._native_params(
                product_symbol=product_symbol,
                leverage=leverage,
                open_type=open_type,
            ),
        )

    async def get_contract_order_detail(self, product_symbol: str, order_id: str) -> dict[str, Any]:
        """Get BitMart contract order detail."""
        return await self._native_private(
            "get_contract_order_detail",
            self._native_params(product_symbol=product_symbol, order_id=order_id),
        )

    async def get_contract_order_history(
        self,
        product_symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart contract order history."""
        return await self._native_private(
            "get_contract_order_history",
            self._native_params(
                product_symbol=product_symbol,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    async def get_contract_open_order(
        self,
        product_symbol: str | None = None,
        type: str | None = None,  # noqa: A002
        order_state: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart contract open orders."""
        return await self._native_private(
            "get_contract_open_order",
            self._native_params(
                product_symbol=product_symbol,
                type=type,
                order_state=order_state,
                limit=limit,
            ),
        )

    async def get_contract_position(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Get BitMart contract positions."""
        return await self._native_private(
            "get_contract_position",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_contract_trade(
        self,
        product_symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart contract trades."""
        return await self._native_private(
            "get_contract_trade",
            self._native_params(
                product_symbol=product_symbol,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    async def get_contract_transaction_history(
        self,
        product_symbol: str | None = None,
        flow_type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart contract transaction history."""
        return await self._native_private(
            "get_contract_transaction_history",
            self._native_params(
                product_symbol=product_symbol,
                flow_type=flow_type,
                start_time=start_time,
                end_time=end_time,
                page_size=page_size,
            ),
        )

    async def get_contract_transfer_list(
        self,
        page: int,
        limit: int,
        currency: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """Get BitMart contract transfer history."""
        return await self._native_private(
            "get_contract_transfer_list",
            self._native_params(
                page=page,
                limit=limit,
                currency=currency,
                time_start=start_time,
                time_end=end_time,
            ),
        )
