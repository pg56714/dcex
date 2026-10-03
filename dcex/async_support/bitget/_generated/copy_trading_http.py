"""Generated bitget copy trading HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._market_http import MarketHTTP


class GeneratedCopyTradingHTTP(MarketHTTP):
    """Copy trading API methods."""

    async def copy_trading_follower_create_copy(
        self,
        *,
        project_id: str,
        type_: str,
        amount: str,
        account_type: str | None = None,
        trading_pair_list: str | None = None,
        margin_per_order: str | None = None,
        auto_copy: str | None = None,
        leverage: str | None = None,
        max_entry_slippage: str | None = None,
        max_margin_ratio: str | None = None,
        max_postion_value: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Copy.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#create-copy
        """
        return await self._native_private(
            "copy_trading_follower_create_copy",
            self._native_params(
                **{
                    "projectId": project_id,
                    "type": type_,
                    "amount": amount,
                    "accountType": account_type,
                    "tradingPairList": trading_pair_list,
                    "marginPerOrder": margin_per_order,
                    "autoCopy": auto_copy,
                    "leverage": leverage,
                    "maxEntrySlippage": max_entry_slippage,
                    "maxMarginRatio": max_margin_ratio,
                    "maxPostionValue": max_postion_value,
                }
            ),
        )

    async def copy_trading_follower_modify_settings(
        self,
        *,
        project_id: str,
        trading_pair_list: str | None = None,
        margin_per_order: str | None = None,
        auto_copy: str | None = None,
        leverage: str | None = None,
        max_entry_slippage: str | None = None,
        max_margin_ratio: str | None = None,
        max_postion_value: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Follower Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#modify-follower-settings
        """
        return await self._native_private(
            "copy_trading_follower_modify_settings",
            self._native_params(
                **{
                    "projectId": project_id,
                    "tradingPairList": trading_pair_list,
                    "marginPerOrder": margin_per_order,
                    "autoCopy": auto_copy,
                    "leverage": leverage,
                    "maxEntrySlippage": max_entry_slippage,
                    "maxMarginRatio": max_margin_ratio,
                    "maxPostionValue": max_postion_value,
                }
            ),
        )

    async def copy_trading_follower_unfollow(
        self, *, project_id: str, close_type: str | None = None
    ) -> dict[str, Any]:
        """
        Unfollow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#unfollow
        """
        return await self._native_private(
            "copy_trading_follower_unfollow",
            self._native_params(**{"projectId": project_id, "closeType": close_type}),
        )

    async def copy_trading_follower_get_copy_settings(self, *, project_id: str) -> dict[str, Any]:
        """
        Get Copy Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-settings
        """
        return await self._native_private(
            "copy_trading_follower_get_copy_settings",
            self._native_params(**{"projectId": project_id}),
        )

    async def copy_trading_follower_get_current_copy(self, *, project_id: str) -> dict[str, Any]:
        """
        Get Current Copy.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-current-copy
        """
        return await self._native_private(
            "copy_trading_follower_get_current_copy",
            self._native_params(**{"projectId": project_id}),
        )

    async def copy_trading_follower_get_copy_profit_details(
        self,
        *,
        project_id: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Copy Profit Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-profit-details
        """
        return await self._native_private(
            "copy_trading_follower_get_copy_profit_details",
            self._native_params(
                **{
                    "projectId": project_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def copy_trading_follower_close_positions(
        self, *, project_id: str, symbol: str, qty: str, hold_side: str
    ) -> dict[str, Any]:
        """
        Close Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#close-positions
        """
        return await self._native_private(
            "copy_trading_follower_close_positions",
            self._native_params(
                **{"projectId": project_id, "symbol": symbol, "qty": qty, "holdSide": hold_side}
            ),
        )

    async def copy_trading_follower_close_all(
        self, *, project_id: str, confirm: bool = False
    ) -> dict[str, Any]:
        """
        Close All.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#close-all
        """
        require_confirmation(confirm)
        return await self._native_private(
            "copy_trading_follower_close_all",
            self._native_params(**{"projectId": project_id, "confirm": confirm}),
        )

    async def copy_trading_follower_get_current_positions(
        self, *, project_id: str, symbol: str | None = None, pos_side: str | None = None
    ) -> dict[str, Any]:
        """
        Get Current Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-current-positions
        """
        return await self._native_private(
            "copy_trading_follower_get_current_positions",
            self._native_params(**{"projectId": project_id, "symbol": symbol, "posSide": pos_side}),
        )

    async def copy_trading_follower_place_tpsl(
        self,
        *,
        project_id: str,
        position_id: str,
        tp_trigger_by: str,
        sl_trigger_by: str,
        take_profit: str,
        stop_loss: str,
    ) -> dict[str, Any]:
        """
        Place TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#place-tpsl
        """
        return await self._native_private(
            "copy_trading_follower_place_tpsl",
            self._native_params(
                **{
                    "projectId": project_id,
                    "positionId": position_id,
                    "tpTriggerBy": tp_trigger_by,
                    "slTriggerBy": sl_trigger_by,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    async def copy_trading_follower_modify_tpsl(
        self,
        *,
        project_id: str,
        strategy_id: str,
        tp_trigger_by: str,
        sl_trigger_by: str,
        take_profit: str,
        stop_loss: str,
    ) -> dict[str, Any]:
        """
        Modify TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#modify-tpsl
        """
        return await self._native_private(
            "copy_trading_follower_modify_tpsl",
            self._native_params(
                **{
                    "projectId": project_id,
                    "strategyId": strategy_id,
                    "tpTriggerBy": tp_trigger_by,
                    "slTriggerBy": sl_trigger_by,
                    "takeProfit": take_profit,
                    "stopLoss": stop_loss,
                }
            ),
        )

    async def copy_trading_follower_cancel_tpsl(
        self, *, project_id: str, strategy_id: str
    ) -> dict[str, Any]:
        """
        Cancel TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#cancel-tpsl
        """
        return await self._native_private(
            "copy_trading_follower_cancel_tpsl",
            self._native_params(**{"projectId": project_id, "strategyId": strategy_id}),
        )

    async def copy_trading_follower_get_current_tpsl_orders(
        self, *, project_id: str
    ) -> dict[str, Any]:
        """
        Get Current TPSL Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-current-tpsl-orders
        """
        return await self._native_private(
            "copy_trading_follower_get_current_tpsl_orders",
            self._native_params(**{"projectId": project_id}),
        )

    async def copy_trading_follower_get_tpsl_order_history(
        self,
        *,
        project_id: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TPSL Order History.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-tpsl-order-history
        """
        return await self._native_private(
            "copy_trading_follower_get_tpsl_order_history",
            self._native_params(
                **{
                    "projectId": project_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    async def copy_trading_public_private_get_position_summary(self) -> dict[str, Any]:
        """
        Get Position Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-position-summary
        """
        return await self._native_private(
            "copy_trading_public_private_get_position_summary", self._native_params(**{})
        )

    async def copy_trading_public_private_get_trading_pairs(self) -> dict[str, Any]:
        """
        Get Trading Pairs.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-trading-pairs
        """
        return await self._native_private(
            "copy_trading_public_private_get_trading_pairs", self._native_params(**{})
        )

    async def copy_trading_public_private_get_current_followers(
        self, *, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get Current Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-current-followers
        """
        return await self._native_private(
            "copy_trading_public_private_get_current_followers",
            self._native_params(**{"limit": limit, "cursor": cursor}),
        )

    async def copy_trading_public_private_get_history_followers(
        self, *, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get History Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-history-followers
        """
        return await self._native_private(
            "copy_trading_public_private_get_history_followers",
            self._native_params(**{"limit": limit, "cursor": cursor}),
        )

    async def copy_trading_public_private_get_profit_summary(self) -> dict[str, Any]:
        """
        Get Profit Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-profit-summary
        """
        return await self._native_private(
            "copy_trading_public_private_get_profit_summary", self._native_params(**{})
        )

    async def copy_trading_public_private_get_profit_details(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Profit Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-profit-details
        """
        return await self._native_private(
            "copy_trading_public_private_get_profit_details",
            self._native_params(
                **{"startTime": start_time, "endTime": end_time, "limit": limit, "cursor": cursor}
            ),
        )

    async def copy_trading_public_private_get_portfolio_overview(
        self, *, period: str
    ) -> dict[str, Any]:
        """
        Get Portfolio Overview.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-portfolio-overview
        """
        return await self._native_private(
            "copy_trading_public_private_get_portfolio_overview",
            self._native_params(**{"period": period}),
        )
