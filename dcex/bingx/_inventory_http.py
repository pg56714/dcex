"""Additional BingX endpoints from the official request tables."""

from typing import Any

from dcex._operation_guards import require_scope

from ._market_http import MarketHTTP


class InventoryHTTP(MarketHTTP):
    """Versioned market, copy-trading, agent and dual-currency methods."""

    def get_agent_v1_asset_partner_data(
        self,
        *,
        uid: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query partner information.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Query%20partner%20information
        """
        return self._native_private(
            "get_agent_v1_asset_partner_data",
            self._native_params(
                **{
                    "uid": uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }
            ),
        )

    def post_cswap_v2_trade_order(
        self,
        *,
        symbol: str,
        type_: str,
        side: str,
        position_side: str,
        price: str | None = None,
        quantity: str | None = None,
        stop_price: str | None = None,
        working_type: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        client_order_id: str | None = None,
        recv_window: int | None = None,
        time_in_force: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Trade order.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Coin-M%20Futures/Trades%20Endpoints/Trade%20order
        """
        return self._native_private(
            "post_cswap_v2_trade_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "type": type_,
                    "side": side,
                    "positionSide": position_side,
                    "price": price,
                    "quantity": quantity,
                    "stopPrice": stop_price,
                    "workingType": working_type,
                    "stopLoss": stop_loss,
                    "takeProfit": take_profit,
                    "clientOrderId": client_order_id,
                    "recvWindow": recv_window,
                    "timeInForce": time_in_force,
                }
            ),
        )

    def get_spot_v2_quote_price(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """
        Symbol Price Ticker.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Symbol%20Price%20Ticker
        """
        return self._native_public(
            "get_spot_v2_quote_price", self._native_params(**{"symbol": symbol})
        )

    def post_copy_trading_v1_swap_trace_set_tpsl(
        self,
        *,
        position_id: int,
        take_profit_mark_price: str,
        stop_loss_mark_price: str,
        recv_window: int,
    ) -> Any:  # noqa: ANN401
        """
        Traders set take profit and stop loss based on order numbers.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Traders%20set%20take%20profit%20and%20stop%20loss%20based%20on%20order%20numbers
        """
        return self._native_private(
            "post_copy_trading_v1_swap_trace_set_tpsl",
            self._native_params(
                **{
                    "positionId": position_id,
                    "takeProfitMarkPrice": take_profit_mark_price,
                    "stopLossMarkPrice": stop_loss_mark_price,
                    "recvWindow": recv_window,
                }
            ),
        )

    def delete_cswap_v1_trade_all_open_orders(
        self,
        *,
        symbol: str | None = None,
        recv_window: int | None = None,
        all_symbols: bool = False,
    ) -> Any:  # noqa: ANN401
        """
        Cancel all orders.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Coin-M%20Futures/Trades%20Endpoints/Cancel%20all%20orders
        """
        require_scope(symbol, all_symbols)
        return self._native_private(
            "delete_cswap_v1_trade_all_open_orders",
            self._native_params(
                **{"symbol": symbol, "recvWindow": recv_window, "all_symbols": all_symbols}
            ),
        )

    def get_copy_trading_v1_p_futures_trading_pairs(self, *, contract_type: str) -> Any:  # noqa: ANN401
        """
        Trader Gets Copy Trading Pairs.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Trader%20Gets%20Copy%20Trading%20Pairs
        """
        return self._native_private(
            "get_copy_trading_v1_p_futures_trading_pairs",
            self._native_params(**{"contractType": contract_type}),
        )

    def get_wealth_v1_product_dual_currency_order_records(
        self, *, page_id: int, page_size: int, order_no: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Dual-Currency Order Records.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Order%20Records
        """
        return self._native_private(
            "get_wealth_v1_product_dual_currency_order_records",
            self._native_params(**{"pageId": page_id, "pageSize": page_size, "orderNo": order_no}),
        )

    def get_spot_v2_quote_book_ticker(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """
        Symbol Order Book Ticker.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Symbol%20Order%20Book%20Ticker
        """
        return self._native_public(
            "get_spot_v2_quote_book_ticker", self._native_params(**{"symbol": symbol})
        )

    def get_wealth_v1_product_dual_currency_position(self, *, order_no: str | None = None) -> Any:  # noqa: ANN401
        """
        Dual-Currency Position Query.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Position%20Query
        """
        return self._native_private(
            "get_wealth_v1_product_dual_currency_position",
            self._native_params(**{"orderNo": order_no}),
        )

    def get_copy_trading_v1_p_futures_profit_history_summarys(self) -> Any:  # noqa: ANN401
        """
        Profit Overview.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Profit%20Overview
        """
        return self._native_private(
            "get_copy_trading_v1_p_futures_profit_history_summarys", self._native_params(**{})
        )

    def get_copy_trading_v1_p_futures_profit_detail(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Profit Details.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Profit%20Details
        """
        return self._native_private(
            "get_copy_trading_v1_p_futures_profit_detail",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    def get_copy_trading_v1_p_futures_trader_detail(self, *, day_size: int | None = None) -> Any:  # noqa: ANN401
        """
        Personal Trading Overview.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Personal%20Trading%20Overview
        """
        return self._native_private(
            "get_copy_trading_v1_p_futures_trader_detail",
            self._native_params(**{"daySize": day_size}),
        )

    def get_copy_trading_v1_spot_trader_detail(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Personal Trading Overview.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Personal%20Trading%20Overview
        """
        return self._native_private(
            "get_copy_trading_v1_spot_trader_detail",
            self._native_params(**{"recvWindow": recv_window}),
        )

    def get_spot_v2_quote_depth(self, *, symbol: str, type_: str, limit: int | None = None) -> Any:  # noqa: ANN401
        """
        Order Book aggregation.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Order%20Book%20aggregation
        """
        return self._native_public(
            "get_spot_v2_quote_depth",
            self._native_params(**{"symbol": symbol, "type": type_, "limit": limit}),
        )

    def get_agent_v2_reward_commission_data_list(
        self,
        *,
        start_time: str,
        end_time: str,
        page_index: int,
        page_size: int,
        recv_window: int,
        uid: int | None = None,
        invitation_code: str | None = None,
        business_type: str | None = None,
        distance_type: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Daily commission details.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Daily%20commission%20details
        """
        return self._native_private(
            "get_agent_v2_reward_commission_data_list",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                    "uid": uid,
                    "invitationCode": invitation_code,
                    "businessType": business_type,
                    "distanceType": distance_type,
                }
            ),
        )

    def post_wealth_v1_product_dual_currency_invest_asset_list(
        self,
        *,
        page_index: int | None = None,
        page_size: int | None = None,
        begin_duration: int | None = None,
        end_duration: int | None = None,
        duration: int | None = None,
        investment_asset: str | None = None,
        exercise_asset: str | None = None,
        direction: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Dual-Currency Product List.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Product%20List
        """
        return self._native_private(
            "post_wealth_v1_product_dual_currency_invest_asset_list",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "beginDuration": begin_duration,
                    "endDuration": end_duration,
                    "duration": duration,
                    "investmentAsset": investment_asset,
                    "exerciseAsset": exercise_asset,
                    "direction": direction,
                }
            ),
        )

    def get_wallets_v1_capital_deposit_query_sub_address(
        self,
        *,
        coin: str,
        sub_uid: int,
        network: str,
        wallet_type: int,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Sub-account Deposit Address.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Account%20and%20Wallet/Sub-account%20Management/Query%20Sub-account%20Deposit%20Address
        """
        return self._native_private(
            "get_wallets_v1_capital_deposit_query_sub_address",
            self._native_params(
                **{
                    "coin": coin,
                    "subUid": sub_uid,
                    "network": network,
                    "walletType": wallet_type,
                    "recvWindow": recv_window,
                }
            ),
        )

    def post_wealth_v1_product_dual_currency_order(
        self,
        *,
        amount: str,
        sku: str,
        product_id: int,
        strike_price: str,
        quote_id: str,
        investment_asset: str | None = None,
        exercise_asset: str | None = None,
        select_accounts: list[Any] | None = None,
        settle_target_account: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Dual-Currency Place Order.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Place%20Order
        """
        return self._native_private(
            "post_wealth_v1_product_dual_currency_order",
            self._native_params(
                **{
                    "amount": amount,
                    "sku": sku,
                    "productId": product_id,
                    "strikePrice": strike_price,
                    "quoteId": quote_id,
                    "investmentAsset": investment_asset,
                    "exerciseAsset": exercise_asset,
                    "selectAccounts": select_accounts,
                    "settleTargetAccount": settle_target_account,
                }
            ),
        )

    def get_agent_v1_reward_third_commission_data_list(
        self,
        *,
        commission_biz_type: int,
        start_time: str,
        end_time: str,
        page_index: int,
        page_size: int,
        uid: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query API transaction commission （non-invitation relationship）.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Query%20API%20transaction%20commission%20%EF%BC%88non-invitation%20relationship%EF%BC%89
        """
        return self._native_private(
            "get_agent_v1_reward_third_commission_data_list",
            self._native_params(
                **{
                    "commissionBizType": commission_biz_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "uid": uid,
                    "recvWindow": recv_window,
                }
            ),
        )

    def get_spot_v2_quote_historical_trades(
        self, *, symbol: str, limit: int | None = None, from_id: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        Historical Trades.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Historical%20Trades
        """
        return self._native_public(
            "get_spot_v2_quote_historical_trades",
            self._native_params(**{"symbol": symbol, "limit": limit, "fromId": from_id}),
        )

    def get_copy_trading_v1_spot_profit_detail(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Profit Details.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Profit%20Details
        """
        return self._native_private(
            "get_copy_trading_v1_spot_profit_detail",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    def get_spot_v2_quote_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Kline/Candlestick Data.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Kline%2FCandlestick%20Data
        """
        return self._native_public(
            "get_spot_v2_quote_klines",
            self._native_params(
                **{
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "timeZone": time_zone,
                    "limit": limit,
                }
            ),
        )

    def get_copy_trading_v1_spot_history_order(
        self,
        *,
        page_index: int,
        page_size: int,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Historical Orders.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Query%20Historical%20Orders
        """
        return self._native_private(
            "get_copy_trading_v1_spot_history_order",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "symbol": symbol,
                    "startTime": start_time,
                    "endTime": end_time,
                    "recvWindow": recv_window,
                }
            ),
        )

    def get_wealth_v1_product_dual_currency_pre_order(
        self, *, sku: str, strike_price: str, product_id: int
    ) -> Any:  # noqa: ANN401
        """
        Dual-Currency Pre-Order Quote.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Pre-Order%20Quote
        """
        return self._native_private(
            "get_wealth_v1_product_dual_currency_pre_order",
            self._native_params(
                **{"sku": sku, "strikePrice": strike_price, "productId": product_id}
            ),
        )

    def post_copy_trading_v1_spot_trader_sell_order(self, *, order_id: int) -> Any:  # noqa: ANN401
        """
        Trader sells spot assets based on buy order number.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Trader%20sells%20spot%20assets%20based%20on%20buy%20order%20number
        """
        return self._native_private(
            "post_copy_trading_v1_spot_trader_sell_order",
            self._native_params(**{"orderId": order_id}),
        )

    def get_agent_v1_commission_data_list_referral_code(
        self,
        *,
        direct_invitation: str,
        referral_code: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Invitation code data.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Invitation%20code%20data
        """
        return self._native_private(
            "get_agent_v1_commission_data_list_referral_code",
            self._native_params(
                **{
                    "directInvitation": direct_invitation,
                    "referralCode": referral_code,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }
            ),
        )

    def get_spot_v2_quote_ticker(self, *, symbol: str | None = None) -> Any:  # noqa: ANN401
        """
        24hr Ticker Price Change Statistics.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/24hr%20Ticker%20Price%20Change%20Statistics
        """
        return self._native_public(
            "get_spot_v2_quote_ticker", self._native_params(**{"symbol": symbol})
        )

    def post_copy_trading_v1_p_futures_set_commission(self, *, new_commission: str) -> Any:  # noqa: ANN401
        """
        Set Commission Rate.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/USDT-M%20Perpetual%20Contracts/Set%20Commission%20Rate
        """
        return self._native_private(
            "post_copy_trading_v1_p_futures_set_commission",
            self._native_params(**{"newCommission": new_commission}),
        )

    def get_spot_v2_quote_historical_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Historical K-line.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Historical%20K-line
        """
        return self._native_public(
            "get_spot_v2_quote_historical_klines",
            self._native_params(
                **{
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    def get_copy_trading_v1_spot_profit_history_summarys(self) -> Any:  # noqa: ANN401
        """
        Profit Summary.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://bingx-api.github.io/docs-v3/#/en/Copy%20Trade/Spot%20Trading/Profit%20Summary
        """
        return self._native_private(
            "get_copy_trading_v1_spot_profit_history_summarys", self._native_params(**{})
        )

    def get_agent_v1_account_invite_account_list(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
        last_uid: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        1. Query Invited Users.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L14
        """
        return self._native_private(
            "get_agent_v1_account_invite_account_list",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                    "lastUid": last_uid,
                }
            ),
        )

    def get_agent_v1_account_invite_relation_check(self, *, uid: int) -> Any:  # noqa: ANN401
        """
        3. Query Agent User Information.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L115
        """
        return self._native_private(
            "get_agent_v1_account_invite_relation_check", self._native_params(**{"uid": uid})
        )

    def get_agent_v1_asset_deposit_detail_list(
        self,
        *,
        uid: int,
        biz_type: int,
        start_time: int,
        end_time: int,
        page_index: int,
        page_size: int,
    ) -> Any:  # noqa: ANN401
        """
        6. Query Deposit Details of Invited Users.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L242
        """
        return self._native_private(
            "get_agent_v1_asset_deposit_detail_list",
            self._native_params(
                **{
                    "uid": uid,
                    "bizType": biz_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                }
            ),
        )

    def get_agent_v1_account_superior_check(self, *, uid: int) -> Any:  # noqa: ANN401
        """
        8. Superior Verification.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L333
        """
        return self._native_private(
            "get_agent_v1_account_superior_check", self._native_params(**{"uid": uid})
        )

    def get_content_v1_announcement(
        self,
        *,
        content_type: str | None = None,
        language: str | None = None,
        page: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        1. Get Announcements.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/announcement/api-reference.md#L7
        """
        return self._native_public(
            "get_content_v1_announcement",
            self._native_params(
                **{"contentType": content_type, "language": language, "page": page}
            ),
        )

    def post_api_lindorm_v1_ai_kline_query(
        self,
        *,
        indicator_type: str,
        access_token: str,
        proxy_user: str,
        symbol: str | None = None,
        interval: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        offset: str | None = None,
        size: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Internal Lindorm Query.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/bingx-trading-plan/api-reference.md#L3
        """
        return self._native_private(
            "post_api_lindorm_v1_ai_kline_query",
            self._native_params(
                **{
                    "indicatorType": indicator_type,
                    "access_token": access_token,
                    "proxy_user": proxy_user,
                    "symbol": symbol,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                    "offset": offset,
                    "size": size,
                }
            ),
        )

    def get_copy_trading_v1_swap_trace_current_track(
        self, *, symbol: str, offset: int | None = None, limit: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        1. Trader's Current Orders.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/copytrade-swap/api-reference.md#L16
        """
        return self._native_private(
            "get_copy_trading_v1_swap_trace_current_track",
            self._native_params(**{"symbol": symbol, "offset": offset, "limit": limit}),
        )

    def post_copy_trading_v1_swap_trace_close_track_order(self, *, position_id: int) -> Any:  # noqa: ANN401
        """
        2. Close Position by Order Number.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
                Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/copytrade-swap/api-reference.md#L91
        """
        return self._native_private(
            "post_copy_trading_v1_swap_trace_close_track_order",
            self._native_params(**{"positionId": position_id}),
        )
