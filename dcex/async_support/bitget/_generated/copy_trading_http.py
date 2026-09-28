"""Generated bitget copy trading HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._market_http import MarketHTTP


class GeneratedCopyTradingHTTP(MarketHTTP):
    """Copy trading API methods."""

    async def classic_copytrading_future_copytrade_follower_copy_settings(
        self,
        *,
        trader_id: str,
        copy_amount: str,
        copy_all_postions: str | None = None,
        auto_copy: str | None = None,
        equity_guardian: str | None = None,
        equity_guardian_mode: str | None = None,
        equity: str | None = None,
        margin_mode: str | None = None,
        leverage: str | None = None,
        multiple: str | None = None,
    ) -> dict[str, Any]:
        """
        Copy settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#copy-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_copy_settings",
            self._native_params(
                **{
                    "traderId": trader_id,
                    "copyAmount": copy_amount,
                    "copyAllPostions": copy_all_postions,
                    "autoCopy": auto_copy,
                    "equityGuardian": equity_guardian,
                    "equityGuardianMode": equity_guardian_mode,
                    "equity": equity,
                    "marginMode": margin_mode,
                    "leverage": leverage,
                    "multiple": multiple,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_current_orders(
        self,
        *,
        product_type: str,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        symbol: str | None = None,
        trader_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-current-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_current_orders",
            self._native_params(
                **{
                    "productType": product_type,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "symbol": symbol,
                    "traderId": trader_id,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_history_orders(
        self,
        *,
        product_type: str,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        symbol: str | None = None,
        trader_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_history_orders",
            self._native_params(
                **{
                    "productType": product_type,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "symbol": symbol,
                    "traderId": trader_id,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_setting_tpsl(
        self,
        *,
        tracking_no: str,
        product_type: str,
        symbol: str | None = None,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Set TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#set-tpsl
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_setting_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "productType": product_type,
                    "symbol": symbol,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_close_positions(
        self,
        *,
        product_type: str,
        tracking_no: str | None = None,
        symbol: str | None = None,
        margin_coin: str | None = None,
        margin_mode: str | None = None,
        hold_side: str | None = None,
    ) -> dict[str, Any]:
        """
        Close Positions.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#close-positions
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_close_positions",
            self._native_params(
                **{
                    "productType": product_type,
                    "trackingNo": tracking_no,
                    "symbol": symbol,
                    "marginCoin": margin_coin,
                    "marginMode": margin_mode,
                    "holdSide": hold_side,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_settings(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Get Copy Trade Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-copy-trade-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_settings",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_future_copytrade_follower_settings(
        self,
        *,
        trader_id: str,
        settings: list[Any],
        auto_copy: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Set Copy Trade Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#set-copy-trade-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_settings",
            self._native_params(
                **{"traderId": trader_id, "settings": settings, "autoCopy": auto_copy, "mode": mode}
            ),
        )

    async def classic_copytrading_future_copytrade_follower_cancel_trader(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Unfollow the Trader.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#unfollow-the-trader
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_cancel_trader",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_future_copytrade_follower_query_traders(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        Get My Traders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-my-traders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_traders",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageNo": page_no,
                    "pageSize": page_size,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_follower_query_quantity_limit(
        self, *, product_type: str, symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Get Follow Limit.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-follower/classic-copytrading-future-copytrade-follower#get-follow-limit
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_follower_query_quantity_limit",
            self._native_params(**{"productType": product_type, "symbol": symbol}),
        )

    async def classic_copytrading_future_copytrade_trader_create_copy_api(
        self, *, passphrase: str
    ) -> dict[str, Any]:
        """
        Create Copy ApiKey.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#create-copy-apikey
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_create_copy_api",
            self._native_params(**{"passphrase": passphrase}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_current_track(
        self,
        *,
        product_type: str,
        symbol: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        id_greater_than: str | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-current-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_current_track",
            self._native_params(
                **{
                    "productType": product_type,
                    "symbol": symbol,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "idGreaterThan": id_greater_than,
                    "idLessThan": id_less_than,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_history_track(
        self,
        *,
        product_type: str,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        order: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_history_track",
            self._native_params(
                **{
                    "productType": product_type,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "order": order,
                    "symbol": symbol,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_close_positions(
        self, *, product_type: str, tracking_no: str | None = None, symbol: str | None = None
    ) -> dict[str, Any]:
        """
        Close Tracking Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#close-tracking-order
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_close_positions",
            self._native_params(
                **{"productType": product_type, "trackingNo": tracking_no, "symbol": symbol}
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_modify_tpsl(
        self,
        *,
        tracking_no: str,
        product_type: str,
        symbol: str | None = None,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Tracking Order TPSL.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#modify-tracking-order-tpsl
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_modify_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "productType": product_type,
                    "symbol": symbol,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_order_total_detail(
        self,
    ) -> dict[str, Any]:
        """
        Get Tracking Order Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-tracking-order-summary
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_order_total_detail",
            self._native_params(**{}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_profit_history_summarys(
        self,
    ) -> dict[str, Any]:
        """
        Get History Profit Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-history-profit-summary
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_profit_history_summarys",
            self._native_params(**{}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_profit_history_details(
        self,
        *,
        coin: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Profit Share Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-history-profit-share-detail
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_profit_history_details",
            self._native_params(
                **{
                    "coin": coin,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_trader_profit_details(
        self, *, coin: str | None = None, page_size: str | None = None, page_no: str | None = None
    ) -> dict[str, Any]:
        """
        Get Profit Share Detail.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-profit-share-detail
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_profit_details",
            self._native_params(**{"coin": coin, "pageSize": page_size, "pageNo": page_no}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_get_profits_group_coin_date(
        self, *, page_size: str | None = None, page_no: str | None = None
    ) -> dict[str, Any]:
        """
        Get Profit Share Group by Coin & Date.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-profit-share-group-by-coin-date
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_get_profits_group_coin_date",
            self._native_params(**{"pageSize": page_size, "pageNo": page_no}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_get_config_query_symbols(
        self, *, product_type: str
    ) -> dict[str, Any]:
        """
        Get Copy Trade Symbol Settings.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-copy-trade-symbol-settings
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_get_config_query_symbols",
            self._native_params(**{"productType": product_type}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_config_setting_symbols(
        self, *, setting_list: list[Any]
    ) -> dict[str, Any]:
        """
        Change Copy Trade Symbol Setting.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#change-copy-trade-symbol-setting
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_config_setting_symbols",
            self._native_params(**{"settingList": setting_list}),
        )

    async def classic_copytrading_future_copytrade_trader_trader_config_settings_base(
        self,
        *,
        enable: str | None = None,
        show_total_equity: str | None = None,
        show_tpsl: str | None = None,
    ) -> dict[str, Any]:
        """
        Change Global Copy Trade Setting.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#change-global-copy-trade-setting
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_trader_config_settings_base",
            self._native_params(
                **{"enable": enable, "showTotalEquity": show_total_equity, "showTpsl": show_tpsl}
            ),
        )

    async def classic_copytrading_future_copytrade_trader_config_query_followers(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get My Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#get-my-followers
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_config_query_followers",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def classic_copytrading_future_copytrade_trader_config_remove_follower(
        self, *, follower_uid: str
    ) -> dict[str, Any]:
        """
        Remove Follower.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-future-trader/classic-copytrading-future-copytrade-trader#remove-follower
        """
        return await self._native_private(
            "classic_copytrading_future_copytrade_trader_config_remove_follower",
            self._native_params(**{"followerUid": follower_uid}),
        )

    async def classic_copytrading_spot_copytrade_follower_cancel_trader(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Cancel Follow.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#cancel-follow
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_cancel_trader",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_spot_copytrade_follower_order_close_tracking(
        self, *, tracking_no_list: list[Any], symbol: str
    ) -> dict[str, Any]:
        """
        Sell And Sell in Batch.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#sell-and-sell-in-batch
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_order_close_tracking",
            self._native_params(**{"trackingNoList": tracking_no_list, "symbol": symbol}),
        )

    async def classic_copytrading_spot_copytrade_follower_query_current_orders(
        self,
        *,
        symbol: str | None = None,
        trader_id: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Copy Trade Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-current-copy-trade-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_current_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "traderId": trader_id,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_query_history_orders(
        self,
        *,
        symbol: str | None = None,
        trader_id: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_history_orders",
            self._native_params(
                **{
                    "symbol": symbol,
                    "traderId": trader_id,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_query_settings(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Get Follow Configuration.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-follow-configuration
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_settings",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_spot_copytrade_follower_query_trader_symbols(
        self, *, trader_id: str
    ) -> dict[str, Any]:
        """
        Get Trader's Current Trading Pair.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#get-traders-current-trading-pair
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_trader_symbols",
            self._native_params(**{"traderId": trader_id}),
        )

    async def classic_copytrading_spot_copytrade_follower_query_traders(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        My Trader List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#my-trader-list
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_query_traders",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_setting_tpsl(
        self,
        *,
        tracking_no: str,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Set Take Profit And Stop Loss.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#set-take-profit-and-stop-loss
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_setting_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_settings(
        self,
        *,
        trader_id: str,
        settings: list[Any],
        auto_copy: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Add or Modify Following Configurations.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#add-or-modify-following-configurations
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_settings",
            self._native_params(
                **{"traderId": trader_id, "settings": settings, "autoCopy": auto_copy, "mode": mode}
            ),
        )

    async def classic_copytrading_spot_copytrade_follower_stop_order(
        self, *, tracking_no_list: list[Any]
    ) -> dict[str, Any]:
        """
        Stop The Order.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-follower/classic-copytrading-spot-copytrade-follower#stop-the-order
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_follower_stop_order",
            self._native_params(**{"trackingNoList": tracking_no_list}),
        )

    async def classic_copytrading_spot_copytrade_trader_config_query_followers(
        self,
        *,
        page_no: str | None = None,
        page_size: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        My Follower List.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#my-follower-list
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_query_followers",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_config_query_settings(
        self,
    ) -> dict[str, Any]:
        """
        Get Copytrade Configuration.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-copytrade-configuration
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_query_settings",
            self._native_params(**{}),
        )

    async def classic_copytrading_spot_copytrade_trader_config_remove_follower(
        self, *, follower_uid: str
    ) -> dict[str, Any]:
        """
        Remove Followers.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#remove-followers
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_remove_follower",
            self._native_params(**{"followerUid": follower_uid}),
        )

    async def classic_copytrading_spot_copytrade_trader_config_setting_symbols(
        self, *, symbol_list: list[Any], setting_type: str
    ) -> dict[str, Any]:
        """
        Set Copytrade Symbols.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#set-copytrade-symbols
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_config_setting_symbols",
            self._native_params(**{"symbolList": symbol_list, "settingType": setting_type}),
        )

    async def classic_copytrading_spot_copytrade_trader_order_close_tracking(
        self, *, tracking_no_list: list[Any], symbol: str
    ) -> dict[str, Any]:
        """
        Sell And Sell in Batch.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#sell-and-sell-in-batch
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_close_tracking",
            self._native_params(**{"trackingNoList": tracking_no_list, "symbol": symbol}),
        )

    async def classic_copytrading_spot_copytrade_trader_order_current_track(
        self,
        *,
        symbol: str | None = None,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Current Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-current-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_current_track",
            self._native_params(
                **{
                    "symbol": symbol,
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_order_history_track(
        self,
        *,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Tracking Orders.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-history-tracking-orders
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_history_track",
            self._native_params(
                **{
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "symbol": symbol,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_order_modify_tpsl(
        self,
        *,
        tracking_no: str,
        stop_surplus_price: str | None = None,
        stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Modify Take Profit and Stop Loss.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#modify-take-profit-and-stop-loss
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_modify_tpsl",
            self._native_params(
                **{
                    "trackingNo": tracking_no,
                    "stopSurplusPrice": stop_surplus_price,
                    "stopLossPrice": stop_loss_price,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_order_total_detail(self) -> dict[str, Any]:
        """
        Get Data Indicator Statistics.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-data-indicator-statistics
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_order_total_detail",
            self._native_params(**{}),
        )

    async def classic_copytrading_spot_copytrade_trader_profit_details(
        self, *, coin: str | None = None, page_no: str | None = None, page_size: str | None = None
    ) -> dict[str, Any]:
        """
        Get Unrealized Profit Sharing Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-unrealized-profit-sharing-details
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_profit_details",
            self._native_params(**{"coin": coin, "pageNo": page_no, "pageSize": page_size}),
        )

    async def classic_copytrading_spot_copytrade_trader_profit_history_details(
        self,
        *,
        id_less_than: str | None = None,
        id_greater_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get History Profit Sharing Details.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-history-profit-sharing-details
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_profit_history_details",
            self._native_params(
                **{
                    "idLessThan": id_less_than,
                    "idGreaterThan": id_greater_than,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "coin": coin,
                }
            ),
        )

    async def classic_copytrading_spot_copytrade_trader_profit_summarys(self) -> dict[str, Any]:
        """
        Get Profit Summary.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#get-profit-summary
        """
        return await self._native_private(
            "classic_copytrading_spot_copytrade_trader_profit_summarys", self._native_params(**{})
        )

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

    async def copy_trading_follower_copy_transfer(
        self,
        *,
        project_id: str,
        type_: str,
        coin: str,
        amount: str,
        in_account_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Copy Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#copy-transfer
        """
        return await self._native_private(
            "copy_trading_follower_copy_transfer",
            self._native_params(
                **{
                    "projectId": project_id,
                    "type": type_,
                    "coin": coin,
                    "amount": amount,
                    "inAccountType": in_account_type,
                }
            ),
        )

    async def copy_trading_follower_get_copy_transfer_record(
        self, *, project_id: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        Get Copy Transfer Record.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/follower#get-copy-transfer-record
        """
        return await self._native_private(
            "copy_trading_follower_get_copy_transfer_record",
            self._native_params(**{"projectId": project_id, "limit": limit, "cursor": cursor}),
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

    async def copy_trading_public_private_get_max_transferable(
        self, *, coin: str
    ) -> dict[str, Any]:
        """
        Get Max Transferable.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-max-transferable
        """
        return await self._native_private(
            "copy_trading_public_private_get_max_transferable",
            self._native_params(**{"coin": coin}),
        )

    async def copy_trading_public_private_transfer(
        self, *, type_: str, coin: str, amount: str, in_account_type: str | None = None
    ) -> dict[str, Any]:
        """
        Transfer.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#transfer
        """
        return await self._native_private(
            "copy_trading_public_private_transfer",
            self._native_params(
                **{"type": type_, "coin": coin, "amount": amount, "inAccountType": in_account_type}
            ),
        )

    async def copy_trading_public_private_get_transfer_record(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Transfer Record.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/copy-trading/public-private#get-transfer-record
        """
        return await self._native_private(
            "copy_trading_public_private_get_transfer_record",
            self._native_params(
                **{"startTime": start_time, "endTime": end_time, "limit": limit, "cursor": cursor}
            ),
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
