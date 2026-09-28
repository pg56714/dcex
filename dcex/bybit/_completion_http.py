"""Additional Bybit V5 endpoints from reviewed official request schemas."""

from typing import Any

from ._market_http import MarketHTTP


class CompletionHTTP(MarketHTTP):
    """Explicit additional V5 endpoint wrappers."""

    def get_mmp_state(
        self,
        *,
        base_coin: str,
    ) -> dict[str, Any]:
        """
        Get MMP State. GET /v5/account/mmp-state.

        Source: https://bybit-exchange.github.io/docs/v5/account/get-mmp-state

        Args:
            base_coin: Base coin, uppercase only
        """
        return self._native_private(
            "get_mmp_state",
            self._native_params(
                **{
                    "baseCoin": base_coin,
                }
            ),
        )

    def reset_mmp(
        self,
        *,
        base_coin: str,
    ) -> dict[str, Any]:
        """
        Reset MMP. POST /v5/account/mmp-reset.

        Source: https://bybit-exchange.github.io/docs/v5/account/reset-mmp

        Args:
            base_coin: Base coin, uppercase only
        """
        return self._native_private(
            "reset_mmp",
            self._native_params(
                **{
                    "baseCoin": base_coin,
                }
            ),
        )

    def set_mmp_config(
        self,
        *,
        base_coin: str,
        window: str,
        frozen_period: str,
        qty_limit: str,
        delta_limit: str,
        vega_limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Set MMP. POST /v5/account/mmp-modify.

        Source: https://bybit-exchange.github.io/docs/v5/account/set-mmp

        Args:
            base_coin: Base coin, uppercase only
            window: Time window (ms)
            frozen_period: Frozen period (ms). "0" means the trade will remain frozen until manually
                reset
            qty_limit: Trade qty limit (positive and up to 2 decimal places)
            delta_limit: Delta limit (positive and up to 2 decimal places)
            vega_limit: Vega limit (positive and up to 2 decimal places). Default: `500000
        """
        return self._native_private(
            "set_mmp_config",
            self._native_params(
                **{
                    "baseCoin": base_coin,
                    "window": window,
                    "frozenPeriod": frozen_period,
                    "qtyLimit": qty_limit,
                    "deltaLimit": delta_limit,
                    "vegaLimit": vega_limit,
                }
            ),
        )

    def get_user_aff_customer_info(
        self,
        *,
        uid: str,
        coin: str | None = None,
        business: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Affiliate User Info. GET /v5/user/aff-customer-info.

        Source: https://bybit-exchange.github.io/docs/v5/affiliate/affiliate-info

        Args:
            uid: The master account UID of affiliate's client
            coin: Coin type for filtering, e.g., `USDT
            business: Business line filter. `1`: Derivatives, `2`: Spot, `3`: ByFi, `4`: USDC, `5`:
                Options
        """
        return self._native_private(
            "get_user_aff_customer_info",
            self._native_params(
                **{
                    "uid": uid,
                    "coin": coin,
                    "business": business,
                }
            ),
        )

    def get_affiliate_affiliate_sub_list(
        self,
        *,
        cursor: str | None = None,
        size: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        sub_aff_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Affiliate Sub-Affiliate List. GET /v5/affiliate/affiliate-sub-list.

        Source: https://bybit-exchange.github.io/docs/v5/affiliate/affiliate-sub-list

        Args:
            cursor: Cursor. Use the `nextPageCursor` token from the response to retrieve the next
                page of the result set
            size: Limit for data size per page. [`0`, `100`]. Default: `0
            start_date: Start date of the query period, format `YYYY-MM-DD`. The range between
                "startDate" and "endTime" cannot exceed 3 months
            end_date: End date of the query period, format `YYYY-MM-DD`. "startDate" and "endDate"
                must either both be provided or both be omitted. If both are omitted, it returns T-1
                data by default
            sub_aff_id: Sub-affiliate ID for exact lookup. Pass `0` or omit to return all
                sub-affiliates without filtering
        """
        return self._native_private(
            "get_affiliate_affiliate_sub_list",
            self._native_params(
                **{
                    "cursor": cursor,
                    "size": size,
                    "startDate": start_date,
                    "endDate": end_date,
                    "subAffId": sub_aff_id,
                }
            ),
        )

    def get_affiliate_aff_user_list(
        self,
        *,
        size: int | None = None,
        cursor: str | None = None,
        need_deposit: bool | None = None,
        need30: bool | None = None,
        need365: bool | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Affiliate User List. GET /v5/affiliate/aff-user-list.

        Source: https://bybit-exchange.github.io/docs/v5/affiliate/affiliate-user-list

        Args:
            size: Limit for data size per page. [`0`, `100`]. Default: `0
            cursor: Cursor. Use the `nextPageCursor` token from the response to retrieve the next
                page of the result set
            need_deposit: true`: return deposit info; `false`(default): does not return deposit info
            need30: true`: return 30 days trading info; `false`(default): does not return 30 days
                trading info
            need365: true`: return 365 days trading info; `false`(default): does not return 365 days
                trading info
            start_date: Start date of the query period, format `YYYY-MM-DD
            end_date: End date of the query period, format `YYYY-MM-DD
        """
        return self._native_private(
            "get_affiliate_aff_user_list",
            self._native_params(
                **{
                    "size": size,
                    "cursor": cursor,
                    "needDeposit": need_deposit,
                    "need30": need30,
                    "need365": need365,
                    "startDate": start_date,
                    "endDate": end_date,
                }
            ),
        )

    def get_alpha_lp_order_list(
        self,
        *,
        order_type: int | None = None,
        token_code: str | None = None,
        order_status: list[Any] | None = None,
        days: int | None = None,
        limit: int | None = None,
        page_index: int | None = None,
        pool_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Get LP Order List. POST /v5/alpha/lp/order-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/order-list

        Args:
            order_type: Filter by order type. `0`: All (default), `1`: Stake, `2`: Redeem
            token_code: Filter by token code
            order_status: Filter by order status (multiple values allowed). `1`: Processing, `2`:
                Success, `3`: Failed
            days: Query last N days. Default: `90`, Max: `365
            limit: Results per page. Default: `20`, Max: `100
            page_index: Page number (1-based). Default: `1
            pool_address: Filter by pool contract address
        """
        return self._native_private(
            "get_alpha_lp_order_list",
            self._native_params(
                **{
                    "orderType": order_type,
                    "tokenCode": token_code,
                    "orderStatus": order_status,
                    "days": days,
                    "limit": limit,
                    "pageIndex": page_index,
                    "poolAddress": pool_address,
                }
            ),
        )

    def get_alpha_lp_pay_token_list(
        self,
        *,
        chain_code: str | None = None,
        token_address: str | None = None,
    ) -> dict[str, Any]:
        """
        Get LP Pay Token List. POST /v5/alpha/lp/pay-token-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/pay-token-list

        Args:
            chain_code: Filter by blockchain identifier
            token_address: Filter by token contract address
        """
        return self._native_private(
            "get_alpha_lp_pay_token_list",
            self._native_params(
                **{
                    "chainCode": chain_code,
                    "tokenAddress": token_address,
                }
            ),
        )

    def get_alpha_lp_pay_token_price(
        self,
        *,
        token_code: list[Any],
        chain_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get LP Pay Token Price. POST /v5/alpha/lp/pay-token-price.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/pay-token-price

        Args:
            token_code: Array of token codes to query, e.g. `["CEX_1", "CEX_2"]`. Max 50 items
            chain_code: Filter by blockchain identifier
        """
        return self._native_private(
            "get_alpha_lp_pay_token_price",
            self._native_params(
                **{
                    "tokenCode": token_code,
                    "chainCode": chain_code,
                }
            ),
        )

    def get_alpha_lp_pool_info(
        self,
        *,
        pool_address: str,
    ) -> dict[str, Any]:
        """
        Get LP Pool Info. POST /v5/alpha/lp/pool-info.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/pool-info

        Args:
            pool_address: Pool contract address
        """
        return self._native_private(
            "get_alpha_lp_pool_info",
            self._native_params(
                **{
                    "poolAddress": pool_address,
                }
            ),
        )

    def get_alpha_lp_pool_list(
        self,
        *,
        token_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get LP Pool List. POST /v5/alpha/lp/pool-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/pool-list

        Args:
            token_symbol: Search pools containing this token symbol, e.g. `ETH`, `USDC
        """
        return self._native_private(
            "get_alpha_lp_pool_list",
            self._native_params(
                **{
                    "tokenSymbol": token_symbol,
                }
            ),
        )

    def get_alpha_lp_position_list(
        self,
    ) -> dict[str, Any]:
        """
        Get LP Position List. POST /v5/alpha/lp/position-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/position-list
        """
        return self._native_private(
            "get_alpha_lp_position_list",
            [],
        )

    def redeem_alpha_lp(
        self,
        *,
        position_id: int,
        pool_address: str,
        derc_ratio: str,
        receive_token_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute LP Redeem. POST /v5/alpha/lp/redeem.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/redeem

        Args:
            position_id: Position ID (from Get LP Position List)
            pool_address: Pool contract address
            derc_ratio: Reduction ratio (0–1). `"0.25"` = redeem 25%, `"0.5"` = redeem 50%, `"1"` =
                close entire position
            receive_token_code: Token code for receiving the redeemed amount
        """
        return self._native_private(
            "redeem_alpha_lp",
            self._native_params(
                **{
                    "positionId": position_id,
                    "poolAddress": pool_address,
                    "dercRatio": derc_ratio,
                    "receiveTokenCode": receive_token_code,
                }
            ),
        )

    def stake_alpha_lp(
        self,
        *,
        position_id: int,
        pool_address: str,
        pay_token_amount: str,
        pay_token_code: str,
        range_upper: str | None = None,
        range_lower: str | None = None,
        price_upper: str | None = None,
        price_lower: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute LP Stake. POST /v5/alpha/lp/stake.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/lp/stake

        Args:
            position_id: Position ID. Use `0` to create a new position, or provide an existing
                position ID to add liquidity
            pool_address: Pool contract address
            pay_token_amount: Payment token amount (positive decimal as string)
            pay_token_code: Payment token code, e.g. `CEX_1` for USDT
            range_upper: Range order upper limit. Use this OR `priceUpper`, not both
            range_lower: Range order lower limit. Use this OR `priceLower`, not both
            price_upper: Price order upper limit (price priority). Use this OR `rangeUpper`, not
                both
            price_lower: Price order lower limit (price priority). Use this OR `rangeLower`, not
                both
        """
        return self._native_private(
            "stake_alpha_lp",
            self._native_params(
                **{
                    "positionId": position_id,
                    "poolAddress": pool_address,
                    "payTokenAmount": pay_token_amount,
                    "payTokenCode": pay_token_code,
                    "rangeUpper": range_upper,
                    "rangeLower": range_lower,
                    "priceUpper": price_upper,
                    "priceLower": price_lower,
                }
            ),
        )

    def buy_alpha_prediction(
        self,
        *,
        token_id: str,
        amount: str,
        pay_token_code: str,
        order_type: int,
        slippage: str,
        event_id: str,
    ) -> dict[str, Any]:
        """
        Execute Buy. POST /v5/alpha/prediction/buy.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/buy

        Args:
            token_id: Outcome token ID to buy (from Get Event Detail)
            amount: USDC amount to invest (positive decimal as string)
            pay_token_code: Payment token code. Phase 1 fixed to `USDC
            order_type: Order type. Refer to predictionOrderType. Phase 1: `1` (FOK) only
            slippage: Maximum acceptable price slippage as decimal. `0.05` = 5% tolerance
            event_id: Event ID associated with the token
        """
        return self._native_private(
            "buy_alpha_prediction",
            self._native_params(
                **{
                    "tokenId": token_id,
                    "amount": amount,
                    "payTokenCode": pay_token_code,
                    "orderType": order_type,
                    "slippage": slippage,
                    "eventId": event_id,
                }
            ),
        )

    def get_alpha_prediction_engine_status(
        self,
    ) -> dict[str, Any]:
        """
        Get Engine Status. GET /v5/alpha/prediction/engine-status.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/engine-status
        """
        return self._native_private(
            "get_alpha_prediction_engine_status",
            [],
        )

    def get_alpha_prediction_event_detail(
        self,
        *,
        event_id: str | None = None,
        slug: str | None = None,
        has_more_markets: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get Event Detail. POST /v5/alpha/prediction/event-detail.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/event-detail

        Args:
            event_id: Event ID. Use `slug` when available
            slug: URL-friendly event slug. Takes priority over `eventId
            has_more_markets: Whether to include markets from related sub-events. Default: `false
        """
        return self._native_private(
            "get_alpha_prediction_event_detail",
            self._native_params(
                **{
                    "eventId": event_id,
                    "slug": slug,
                    "hasMoreMarkets": has_more_markets,
                }
            ),
        )

    def request_alpha_prediction_order_book(
        self,
        *,
        token_ids: list[Any],
    ) -> dict[str, Any]:
        """
        Get Order Book. POST /v5/alpha/prediction/order-book.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/order-book

        Args:
            token_ids: List of outcome token IDs. Maximum 20
        """
        return self._native_private(
            "request_alpha_prediction_order_book",
            self._native_params(
                **{
                    "tokenIds": token_ids,
                }
            ),
        )

    def request_alpha_prediction_order_estimate(
        self,
        *,
        token_id: str,
        side: int,
        event_id: str,
        amount: str,
        order_type: int,
        pay_token_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Order Estimate. POST /v5/alpha/prediction/order-estimate.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/order-estimate

        Args:
            token_id: Outcome token ID (from Get Event Detail)
            side: Trade direction. Refer to predictionSide
            event_id: Event ID associated with the token
            amount: BUY: USDC to invest. SELL: number of shares to sell (positive decimal as string)
            order_type: Order type. Refer to predictionOrderType. Phase 1: `1` (FOK) only
            pay_token_code: Payment token code. Required for BUY. Phase 1 fixed to `USDC
        """
        return self._native_private(
            "request_alpha_prediction_order_estimate",
            self._native_params(
                **{
                    "tokenId": token_id,
                    "side": side,
                    "eventId": event_id,
                    "amount": amount,
                    "orderType": order_type,
                    "payTokenCode": pay_token_code,
                }
            ),
        )

    def get_alpha_prediction_order_list(
        self,
        *,
        status: int | None = None,
        token_id: str | None = None,
        event_id: str | None = None,
        side: int | None = None,
        days: int | None = None,
        limit: int | None = None,
        page_index: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Order List. POST /v5/alpha/prediction/order-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/order-list

        Args:
            status: Filter by order status. Refer to predictionOrderStatus
            token_id: Filter by outcome token ID
            event_id: Filter by event ID
            side: Filter by trade direction. Refer to predictionSide
            days: Look back N days. Max: `90
            limit: Number of records per page
            page_index: Page number starting from `1
        """
        return self._native_private(
            "get_alpha_prediction_order_list",
            self._native_params(
                **{
                    "status": status,
                    "tokenId": token_id,
                    "eventId": event_id,
                    "side": side,
                    "days": days,
                    "limit": limit,
                    "pageIndex": page_index,
                }
            ),
        )

    def get_alpha_prediction_pay_token_list(
        self,
    ) -> dict[str, Any]:
        """
        Get Payment Token List. GET /v5/alpha/prediction/pay-token-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/pay-token-list
        """
        return self._native_private(
            "get_alpha_prediction_pay_token_list",
            [],
        )

    def get_alpha_prediction_portfolio_summary(
        self,
        *,
        event_type: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Portfolio Summary. POST /v5/alpha/prediction/portfolio-summary.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/portfolio-summary

        Args:
            event_type: Filter by event type. Refer to predictionEventType
        """
        return self._native_private(
            "get_alpha_prediction_portfolio_summary",
            self._native_params(
                **{
                    "eventType": event_type,
                }
            ),
        )

    def get_alpha_prediction_position_history(
        self,
        *,
        token_id: str | None = None,
        event_id: str | None = None,
        result: int | None = None,
        days: int | None = None,
        limit: int | None = None,
        page_index: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Position History. POST /v5/alpha/prediction/position-history.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/position-history

        Args:
            token_id: Filter by outcome token ID
            event_id: Filter by event ID
            result: Filter by position outcome. Refer to predictionPositionResult
            days: Look back N days. Max: `90
            limit: Number of records per page
            page_index: Page number starting from `1
        """
        return self._native_private(
            "get_alpha_prediction_position_history",
            self._native_params(
                **{
                    "tokenId": token_id,
                    "eventId": event_id,
                    "result": result,
                    "days": days,
                    "limit": limit,
                    "pageIndex": page_index,
                }
            ),
        )

    def get_alpha_prediction_position_list(
        self,
        *,
        token_id: str | None = None,
        event_id: str | None = None,
        limit: int | None = None,
        page_index: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Position List. POST /v5/alpha/prediction/position-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/position-list

        Args:
            token_id: Filter by outcome token ID
            event_id: Filter by event ID
            limit: Number of records per page
            page_index: Page number starting from `1
        """
        return self._native_private(
            "get_alpha_prediction_position_list",
            self._native_params(
                **{
                    "tokenId": token_id,
                    "eventId": event_id,
                    "limit": limit,
                    "pageIndex": page_index,
                }
            ),
        )

    def get_alpha_prediction_price_history(
        self,
        *,
        token_id: str,
        interval: str,
    ) -> dict[str, Any]:
        """
        Get Price History. POST /v5/alpha/prediction/price-history.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/price-history

        Args:
            token_id: Outcome token ID
            interval: Time interval. Refer to predictionPriceInterval
        """
        return self._native_private(
            "get_alpha_prediction_price_history",
            self._native_params(
                **{
                    "tokenId": token_id,
                    "interval": interval,
                }
            ),
        )

    def sell_alpha_prediction(
        self,
        *,
        token_id: str,
        size: str,
        order_type: int,
        slippage: str,
        event_id: str,
        to_token_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute Sell. POST /v5/alpha/prediction/sell.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/sell

        Args:
            token_id: Outcome token ID to sell (from Get Position List)
            size: Number of shares to sell (positive decimal as string)
            order_type: Order type. Refer to predictionOrderType. Phase 1: `1` (FOK) only
            slippage: Maximum acceptable price slippage as decimal. `0.05` = 5% tolerance
            event_id: Event ID associated with the token
            to_token_code: Destination token code. Phase 1 fixed to `USDC
        """
        return self._native_private(
            "sell_alpha_prediction",
            self._native_params(
                **{
                    "tokenId": token_id,
                    "size": size,
                    "orderType": order_type,
                    "slippage": slippage,
                    "eventId": event_id,
                    "toTokenCode": to_token_code,
                }
            ),
        )

    def get_alpha_prediction_side_market_list(
        self,
        *,
        event_id: str,
        sort_by: str | None = None,
        market_type: int | None = None,
        limit: int | None = None,
        page_index: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Side Market List. POST /v5/alpha/prediction/side-market-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/side-market-list

        Args:
            event_id: Event ID to query markets for
            sort_by: Sort field. Refer to predictionSortBy
            market_type: Filter by market type. Refer to predictionMarketType
            limit: Number of records per page
            page_index: Page number starting from `1
        """
        return self._native_private(
            "get_alpha_prediction_side_market_list",
            self._native_params(
                **{
                    "eventId": event_id,
                    "sortBy": sort_by,
                    "marketType": market_type,
                    "limit": limit,
                    "pageIndex": page_index,
                }
            ),
        )

    def get_alpha_prediction_sports_group_stage_detail(
        self,
        *,
        event_type: int,
        group_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Sports Group Stage Detail. POST /v5/alpha/prediction/sports/group-stage-detail.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/sports-group-stage-detail

        Args:
            event_type: Sports event type. Refer to predictionEventType. Phase 1: `1` (FIFA_2026)
            group_name: Filter by group name (e.g., `A`, `B`, … `L` for FIFA 2026)
        """
        return self._native_private(
            "get_alpha_prediction_sports_group_stage_detail",
            self._native_params(
                **{
                    "eventType": event_type,
                    "groupName": group_name,
                }
            ),
        )

    def get_alpha_prediction_sports_match_list(
        self,
        *,
        event_type: int,
        status: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        stage_code: str | None = None,
        limit: int | None = None,
        page_index: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Sports Match List. POST /v5/alpha/prediction/sports/match-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/sports-match-list

        Args:
            event_type: Sports event type. Refer to predictionEventType. Phase 1: `1` (FIFA_2026)
            status: Match status filter. Refer to predictionMatchStatus
            start_time: Filter matches starting after this timestamp (UTC milliseconds)
            end_time: Filter matches starting before this timestamp (UTC milliseconds)
            stage_code: Filter by tournament stage. Refer to predictionStageCode
            limit: Number of records per page
            page_index: Page number starting from `1
        """
        return self._native_private(
            "get_alpha_prediction_sports_match_list",
            self._native_params(
                **{
                    "eventType": event_type,
                    "status": status,
                    "startTime": start_time,
                    "endTime": end_time,
                    "stageCode": stage_code,
                    "limit": limit,
                    "pageIndex": page_index,
                }
            ),
        )

    def get_alpha_prediction_sports_timeline_stages(
        self,
        *,
        event_type: int,
    ) -> dict[str, Any]:
        """
        Get Sports Timeline Stages. GET /v5/alpha/prediction/sports/timeline-stages.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/sports-timeline-stages

        Args:
            event_type: Sports event type. Refer to predictionEventType. Phase 1: `1` (FIFA_2026)
        """
        return self._native_private(
            "get_alpha_prediction_sports_timeline_stages",
            self._native_params(
                **{
                    "eventType": event_type,
                }
            ),
        )

    def get_alpha_prediction_token_price(
        self,
        *,
        token_ids: list[Any],
    ) -> dict[str, Any]:
        """
        Get Token Price. POST /v5/alpha/prediction/token-price.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/prediction/token-price

        Args:
            token_ids: List of outcome token IDs to query. Maximum 20
        """
        return self._native_private(
            "get_alpha_prediction_token_price",
            self._native_params(
                **{
                    "tokenIds": token_ids,
                }
            ),
        )

    def get_alpha_trade_asset_detail(
        self,
        *,
        chain_code: str,
        token_address: str,
    ) -> dict[str, Any]:
        """
        Get Asset Detail. POST /v5/alpha/trade/asset-detail.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/asset-detail

        Args:
            chain_code: Blockchain code, e.g. `ETH`, `SOL`, `BSC
            token_address: Token contract address on the specified chain
        """
        return self._native_private(
            "get_alpha_trade_asset_detail",
            self._native_params(
                **{
                    "chainCode": chain_code,
                    "tokenAddress": token_address,
                }
            ),
        )

    def get_alpha_trade_asset_list(
        self,
    ) -> dict[str, Any]:
        """
        Get Asset List. POST /v5/alpha/trade/asset-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/asset-list
        """
        return self._native_private(
            "get_alpha_trade_asset_list",
            [],
        )

    def request_alpha_trade_biz_token_details(
        self,
        *,
        chain_code: str,
        token_address: str,
    ) -> dict[str, Any]:
        """
        Get Token Details. POST /v5/alpha/trade/biz-token-details.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/biz-token-details

        Args:
            chain_code: Blockchain code, e.g. `ETH`, `SOL`, `BSC
            token_address: Token contract address on the specified chain
        """
        return self._native_private(
            "request_alpha_trade_biz_token_details",
            self._native_params(
                **{
                    "chainCode": chain_code,
                    "tokenAddress": token_address,
                }
            ),
        )

    def get_alpha_trade_biz_token_list(
        self,
        *,
        token_tag: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Biz Token List. POST /v5/alpha/trade/biz-token-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/biz-token-list

        Args:
            token_tag: Token tag filter. `0`: All (default), `1`: New token sniping, `2`: On-chain
                hot token
        """
        return self._native_private(
            "get_alpha_trade_biz_token_list",
            self._native_params(
                **{
                    "tokenTag": token_tag,
                }
            ),
        )

    def get_alpha_trade_biz_token_price_list(
        self,
        *,
        token_address_info: list[Any],
    ) -> dict[str, Any]:
        """
        Get Token Price List. POST /v5/alpha/trade/biz-token-price-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/biz-token-price-list

        Args:
            token_address_info: List of token identifiers to query. Maximum 20 items per request
        """
        return self._native_private(
            "get_alpha_trade_biz_token_price_list",
            self._native_params(
                **{
                    "tokenAddressInfo": token_address_info,
                }
            ),
        )

    def get_alpha_trade_order_list(
        self,
        *,
        trade_type: int | None = None,
        token_code: str | None = None,
        order_status: list[Any] | None = None,
        days: int | None = None,
        limit: int,
        page_index: int,
        direction: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Order List. POST /v5/alpha/trade/order-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/order-list

        Args:
            trade_type: Filter by trade type. `0`: All (default), `1`: Purchase, `2`: Redeem
            token_code: Filter by token code
            order_status: Filter by order status (multiple values allowed). `1`: Processing, `2`:
                Success, `3`: Failed
            days: Query last N days. Range: [0, 90]. `0` uses system default (90 days). Default: `0
            limit: Results per page. Range: [1, 100]
            page_index: Page number (1-based)
            direction: Pagination direction. `prev`, `next
        """
        return self._native_private(
            "get_alpha_trade_order_list",
            self._native_params(
                **{
                    "tradeType": trade_type,
                    "tokenCode": token_code,
                    "orderStatus": order_status,
                    "days": days,
                    "limit": limit,
                    "pageIndex": page_index,
                    "direction": direction,
                }
            ),
        )

    def get_alpha_trade_pay_token_list(
        self,
        *,
        chain_code: str,
        token_address: str,
    ) -> dict[str, Any]:
        """
        Get Payment Token List. POST /v5/alpha/trade/pay-token-list.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/pay-token-list

        Args:
            chain_code: Blockchain code, e.g. `SOL`, `MANTLE
            token_address: Token contract address on the specified chain
        """
        return self._native_private(
            "get_alpha_trade_pay_token_list",
            self._native_params(
                **{
                    "chainCode": chain_code,
                    "tokenAddress": token_address,
                }
            ),
        )

    def purchase_alpha_trade(
        self,
        *,
        from_token_code: str,
        from_token_amount: str,
        to_token_code: str,
        slippage: str,
        quote_data: str,
        gas: str,
        quote_mode: int,
        correcting_code: str,
        tenant: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute Purchase. POST /v5/alpha/trade/purchase.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/trade-purchase

        Args:
            from_token_code: Payment token code (`CEX_`), e.g. `CEX_1` for USDT. Must match the
                quote request
            from_token_amount: Payment amount (positive decimal as string). Must match the quote
                request
            to_token_code: Target on-chain token code (`DEX_`), e.g. `DEX_123`. Must match the quote
                request
            slippage: Slippage tolerance as decimal. `0.005` = 0.5%, `0.01` = 1%, `0.05` = 5%
            quote_data: Base64-encoded quote data. Must pass as-is from the `/quote` response
            gas: Estimated gas fee. Must pass as-is from the `/quote` response
            quote_mode: Quote mode. Must be consistent with the `/quote` request. `0`: Auto, `1`:
                Price Priority, `2`: Success Rate Priority
            correcting_code: MD5 checksum for data integrity. Must pass as-is from the `/quote`
                response
            tenant: Optional tenant identifier
        """
        return self._native_private(
            "purchase_alpha_trade",
            self._native_params(
                **{
                    "fromTokenCode": from_token_code,
                    "fromTokenAmount": from_token_amount,
                    "toTokenCode": to_token_code,
                    "slippage": slippage,
                    "quoteData": quote_data,
                    "gas": gas,
                    "quoteMode": quote_mode,
                    "correctingCode": correcting_code,
                    "tenant": tenant,
                }
            ),
        )

    def request_alpha_trade_quote(
        self,
        *,
        trade_type: int,
        from_token_code: str,
        from_token_amount: str,
        to_token_code: str,
        quote_mode: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Trade Quote. POST /v5/alpha/trade/quote.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/trade-quote

        Args:
            trade_type: Trade type. `1`: Purchase (buy on-chain token with payment token), `2`:
                Redeem (sell on-chain token for payment token)
            from_token_code: Source token code (`CEX_` or `DEX_`). Purchase: CEX token (e.g. `CEX_1`
                for USDT); Redeem: DEX token (e.g. `DEX_123`)
            from_token_amount: Amount to pay, string-formatted positive decimal. Must be greater
                than 0
            to_token_code: Target token code (`CEX_` or `DEX_`). Purchase: DEX token; Redeem: CEX
                token (e.g. `CEX_1` for USDT)
            quote_mode: Quote mode. `0`: Auto (default), `1`: Price Priority, `2`: Success Rate
                Priority
        """
        return self._native_private(
            "request_alpha_trade_quote",
            self._native_params(
                **{
                    "tradeType": trade_type,
                    "fromTokenCode": from_token_code,
                    "fromTokenAmount": from_token_amount,
                    "toTokenCode": to_token_code,
                    "quoteMode": quote_mode,
                }
            ),
        )

    def redeem_alpha_trade(
        self,
        *,
        from_token_code: str,
        from_token_amount: str,
        to_token_code: str,
        slippage: str,
        quote_data: str,
        gas: str,
        quote_mode: int,
        correcting_code: str,
        tenant: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute Redeem. POST /v5/alpha/trade/redeem.

        Source: https://bybit-exchange.github.io/docs/v5/alpha/trade/trade-redeem

        Args:
            from_token_code: On-chain token to sell (`DEX_`). Must match the quote request, e.g.
                `DEX_123
            from_token_amount: Amount to sell (positive decimal as string). Must match the quote
                request
            to_token_code: Payment token to receive (`CEX_`), e.g. `CEX_1` for USDT. Must match the
                quote request
            slippage: Slippage tolerance as decimal. `0.005` = 0.5%, `0.01` = 1%, `0.05` = 5%
            quote_data: Base64-encoded quote data. Must pass as-is from the `/quote` response
            gas: Estimated gas fee. Must pass as-is from the `/quote` response
            quote_mode: Quote mode. Must be consistent with the `/quote` request. `0`: Auto, `1`:
                Price Priority, `2`: Success Rate Priority
            correcting_code: MD5 checksum for data integrity. Must pass as-is from the `/quote`
                response
            tenant: Optional tenant identifier
        """
        return self._native_private(
            "redeem_alpha_trade",
            self._native_params(
                **{
                    "fromTokenCode": from_token_code,
                    "fromTokenAmount": from_token_amount,
                    "toTokenCode": to_token_code,
                    "slippage": slippage,
                    "quoteData": quote_data,
                    "gas": gas,
                    "quoteMode": quote_mode,
                    "correctingCode": correcting_code,
                    "tenant": tenant,
                }
            ),
        )

    def get_fiat_balance_query(
        self,
        *,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Balance. GET /v5/fiat/balance-query.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/balance-query

        Args:
            currency: Fiat`: fiat currency code (ISO 4217) etc: KZT. not set will query all fiat
                balance list
        """
        return self._native_private(
            "get_fiat_balance_query",
            self._native_params(
                **{
                    "currency": currency,
                }
            ),
        )

    def request_fiat_trade_execute(
        self,
        *,
        quote_tx_id: str,
        sub_user_id: str,
        webhook_url: str | None = None,
        merchant_request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Confirm a Quote . POST /v5/fiat/trade-execute.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/confirm-quote

        Args:
            quote_tx_id: The quote tx ID from Request a Quote
            sub_user_id: The user's sub userId in bybit
            webhook_url: API URL to call when order is successful or failed (max 256 characters)
            merchant_request_id: Customised request ID(maximum length of 36)Generally it is useless,
                but it is convenient to track the quote request internally if you fill this field
        """
        return self._native_private(
            "request_fiat_trade_execute",
            self._native_params(
                **{
                    "quoteTxId": quote_tx_id,
                    "subUserId": sub_user_id,
                    "webhookUrl": webhook_url,
                    "MerchantRequestId": merchant_request_id,
                }
            ),
        )

    def get_fiat_query_coin_list(
        self,
        *,
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Trading Pair List. GET /v5/fiat/query-coin-list.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/query-coin-list

        Args:
            side: 0`: buy, buy crypto sell fiat; `1`: sell, sell crypto buy fiat
        """
        return self._native_private(
            "get_fiat_query_coin_list",
            self._native_params(
                **{
                    "side": side,
                }
            ),
        )

    def get_fiat_query_trade_history(
        self,
        *,
        index: int | None = None,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Convert History. GET /v5/fiat/query-trade-history.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/query-trade-history

        Args:
            index: Page number,started from 1, default 1
            limit: Page Size [20-100] 20 records by default,up to 100 records, return 100 when
                exceeds 100
            start_time: Query start time(Millisecond timestamp)
            end_time: Query end time(Millisecond timestamp)
        """
        return self._native_private(
            "get_fiat_query_trade_history",
            self._native_params(
                **{
                    "index": index,
                    "limit": limit,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    def get_fiat_trade_query(
        self,
        *,
        trade_no: str | None = None,
        merchant_request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Convert Status. GET /v5/fiat/trade-query.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/query-trade

        Args:
            trade_no: Trade order No,tradeNo or merchantRequestId must be provided
            merchant_request_id: Customised request ID,tradeNo or merchantRequestId must be provided
        """
        return self._native_private(
            "get_fiat_trade_query",
            self._native_params(
                **{
                    "tradeNo": trade_no,
                    "merchantRequestId": merchant_request_id,
                }
            ),
        )

    def request_fiat_quote_apply(
        self,
        *,
        from_coin: str,
        from_coin_type: str,
        to_coin: str,
        to_coin_type: str,
        request_amount: str,
        request_coin_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Request a Quote . POST /v5/fiat/quote-apply.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/quote-apply

        Args:
            from_coin: Convert from coin (coin to sell)
            from_coin_type: fiat` or `crypto
            to_coin: Convert to coin (coin to buy)
            to_coin_type: fiat` or `crypto
            request_amount: request coin amount (the amount you want to sell)
            request_coin_type: coinType you want to sell, `fiat` or `crypto`, default to `fiat
        """
        return self._native_private(
            "request_fiat_quote_apply",
            self._native_params(
                **{
                    "fromCoin": from_coin,
                    "fromCoinType": from_coin_type,
                    "toCoin": to_coin,
                    "toCoinType": to_coin_type,
                    "requestAmount": request_amount,
                    "requestCoinType": request_coin_type,
                }
            ),
        )

    def get_fiat_reference_price(
        self,
        *,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Get Reference Price. GET /v5/fiat/reference-price.

        Source: https://bybit-exchange.github.io/docs/v5/asset/fiat-convert/reference-price

        Args:
            symbol: Coin Pair, such as EUR-USDT
        """
        return self._native_private(
            "get_fiat_reference_price",
            self._native_params(
                **{
                    "symbol": symbol,
                }
            ),
        )

    def cancel_withdrawal(
        self,
        *,
        id: str,
    ) -> dict[str, Any]:
        """
        Cancel Withdrawal. POST /v5/asset/withdraw/cancel.

        Source: https://bybit-exchange.github.io/docs/v5/asset/withdraw/cancel-withdraw

        Args:
            id: Withdrawal ID
        """
        return self._native_private(
            "cancel_withdrawal",
            self._native_params(
                **{
                    "id": id,
                }
            ),
        )

    def create_withdrawal(
        self,
        *,
        coin: str,
        chain: str | None = None,
        address: str,
        tag: str | None = None,
        amount: str,
        timestamp: int,
        force_chain: int | None = None,
        account_type: str,
        fee_type: int | None = None,
        request_id: str | None = None,
        transaction_purpose: str | None = None,
        questionnaire: str | None = None,
        beneficiary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Withdraw. POST /v5/asset/withdraw/create.

        API withdrawals have no second confirmation; they execute on submit.
        Source: https://bybit-exchange.github.io/docs/v5/asset/withdraw/withdraw

        Args:
            coin: Coin, uppercase only
            chain: Chain `forceChain`=0 or 1: this field is **required**`forceChain`=2: this field
                can be null
            address: forceChain`=0 or 1: fill wallet address, and make sure you add address in the
                address book first. Please note that the address is case sensitive, so use the exact
                same address added in address book`forceChain`=2: fill Bybit UID, and it can only be
                another Bybit **main** account UID. Make sure you add UID in the address book first
            tag: Tag **Required** if tag exists in the wallet address list.**Note**: please do not
                set a tag/memo in the address book if the chain does not support tag
            amount: Withdraw amount
            timestamp: Current timestamp (ms). Used for preventing from withdraw replay
            force_chain: Whether or not to force an on-chain withdrawal`0`(default): If the address
                is parsed out to be an internal address, then internal transfer (**Bybit main
                account only**)`1`: Force the withdrawal to occur on-chain`2`: Use UID to withdraw
            account_type: Select the wallet to be withdrawn from `FUND`: Funding wallet`UTA`: System
                transfers the funds to Funding wallet to withdraw`EARN`: some coins may not support
                to be withdrawn via Earn account, please transfer it to Funding wallet then
                withdraw`FUND,UTA,EARN`: For combo withdrawals, funds will be deducted from the
                Funding wallet first. If the balance is insufficient, the remaining amount will be
                deducted from the UTA wallet and Earn account.
            fee_type: Handling fee option `0`(default): input amount is the actual amount received,
                so you have to calculate handling fee manually`1`: input amount is not the actual
                amount you received, the system will help to deduct the handling fee automatically
            request_id: Customised ID, globally unique, it is used for idempotent verification A
                combination of letters (case sensitive) and numbers, which can be pure letters or
                pure numbers and the length must be between 1 and 32 digits
            transaction_purpose: Purpose of the withdrawal transaction, need at least 20 characters,
                Required for Bybit Turkey site users
            questionnaire: Travel Rule questionnaire info, JSON string, ≤16384 bytes. Supersedes
                `beneficiary` and `transactionPurpose` when both are present. **New integrations are
                always recommended to use this field to submit travel rule**. See Questionnaire for
                field structure by compliance zone
            beneficiary: Travel rule info. It is required for kyc/kyb=KOR (Korean), kyc=IND (India)
                users, and users who registered in Bybit Turkey(TR), Bybit Kazakhstan(KZ), Bybit
                Indonesia (ID)
        """
        return self._native_private(
            "create_withdrawal",
            self._native_params(
                **{
                    "coin": coin,
                    "chain": chain,
                    "address": address,
                    "tag": tag,
                    "amount": amount,
                    "timestamp": timestamp,
                    "forceChain": force_chain,
                    "accountType": account_type,
                    "feeType": fee_type,
                    "requestId": request_id,
                    "transactionPurpose": transaction_purpose,
                    "questionnaire": questionnaire,
                    "beneficiary": beneficiary,
                }
            ),
        )

    def request_dca_close_bot(
        self,
        *,
        bot_id: str,
        close_mode: str,
    ) -> dict[str, Any]:
        """
        Close DCA Bot. POST /v5/dca/close-bot.

        Source: https://bybit-exchange.github.io/docs/v5/bot/dca/close

        Args:
            bot_id: DCA bot ID to close, obtained from Create Spot DCA Bot response
            close_mode: Asset settlement mode: `2` Base token, `3` Quote token (e.g. USDT)
        """
        return self._native_private(
            "request_dca_close_bot",
            self._native_params(
                **{
                    "bot_id": bot_id,
                    "close_mode": close_mode,
                }
            ),
        )

    def request_dca_create_bot(
        self,
        *,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create DCA Bot. POST /v5/dca/create-bot.

        Source: https://bybit-exchange.github.io/docs/v5/bot/dca/create

        Args:
            parameters: DCA bot configuration object (see below)
        """
        return self._native_private(
            "request_dca_create_bot",
            self._native_params(
                **{
                    "parameters": parameters,
                }
            ),
        )

    def close_fcombobot(
        self,
        *,
        bot_id: str,
    ) -> dict[str, Any]:
        """
        Close Bot. POST /v5/fcombobot/close.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-combo/close

        Args:
            bot_id: Bot ID to close, obtained from Create Futures Combo Bot response
        """
        return self._native_private(
            "close_fcombobot",
            self._native_params(
                **{
                    "bot_id": bot_id,
                }
            ),
        )

    def create_fcombobot(
        self,
        *,
        leverage: str,
        init_margin: str,
        adjust_position_mode: int,
        symbol_settings: list[Any],
        adjust_position_percent: str | None = None,
        adjust_position_time_interval: int | None = None,
        sl_percent: str | None = None,
        tp_percent: str | None = None,
        trailing_stop_percent: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Bot. POST /v5/fcombobot/create.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-combo/create

        Args:
            leverage: Position leverage multiplier (e.g. `"5"` means 5x). Must be >= 1
            init_margin: Initial investment in quote currency (decimal string, e.g. `"1000"` for
                1000 USDT)
            adjust_position_mode: Rebalancing trigger mode: `1` Time, `2` Percentage, `3` Time or
                Percentage, `4` Manual, `5` On settings change, `6` On transfer
            symbol_settings: Per-symbol portfolio configuration. At least one entry required. All
                `target_position_percent` must sum to 1
            adjust_position_percent: Rebalancing drift threshold as percentage, range: [0.01, 0.5]
                (e.g. `"0.05"` means rebalance when allocation drifts 5%). **Required** when mode
                includes percentage
            adjust_position_time_interval: Rebalancing time interval **in seconds**. **Required**
                when mode includes time. `30M`, `1H`, `4H`, `8H`, `12H`, `1D`, `3D`, `7D`, `14D`,
                `28D` convert to seconds
            sl_percent: Stop-loss as percentage of total margin (e.g. `"0.2"` means close when loss
                reaches 20%)
            tp_percent: Take-profit as percentage of total margin (e.g. `"0.5"` means close when
                profit reaches 50%)
            trailing_stop_percent: Trailing stop callback as percentage (e.g. `"0.05"` means 5%)
        """
        return self._native_private(
            "create_fcombobot",
            self._native_params(
                **{
                    "leverage": leverage,
                    "init_margin": init_margin,
                    "adjust_position_mode": adjust_position_mode,
                    "symbol_settings": symbol_settings,
                    "adjust_position_percent": adjust_position_percent,
                    "adjust_position_time_interval": adjust_position_time_interval,
                    "sl_percent": sl_percent,
                    "tp_percent": tp_percent,
                    "trailing_stop_percent": trailing_stop_percent,
                }
            ),
        )

    def get_fcombobot_detail(
        self,
        *,
        bot_id: str,
    ) -> dict[str, Any]:
        """
        Get Bot Detail. POST /v5/fcombobot/detail.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-combo/get-detail

        Args:
            bot_id: Bot ID to query
        """
        return self._native_private(
            "get_fcombobot_detail",
            self._native_params(
                **{
                    "bot_id": bot_id,
                }
            ),
        )

    def get_fcombobot_getlimit(
        self,
        *,
        leverage: str,
        init_margin: str,
        adjust_position_mode: int,
        symbol_settings: list[Any],
        adjust_position_percent: str | None = None,
        adjust_position_time_interval: int | None = None,
        sl_percent: str | None = None,
        tp_percent: str | None = None,
        trailing_stop_percent: str | None = None,
        need_to_slippage: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get Bot Parameter Limit. POST /v5/fcombobot/getlimit.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-combo/get-limit

        Args:
            leverage: Position leverage multiplier (e.g. `"5"` means 5x). Must be >= 1
            init_margin: Initial investment in quote currency (decimal string)
            adjust_position_mode: Rebalancing trigger mode: `1` Time, `2` Percentage, `3` Time or %,
                `4` Manual, `5` On settings change, `6` On transfer
            symbol_settings: Per-symbol portfolio configuration
            adjust_position_percent: Rebalancing drift threshold as percentage
            adjust_position_time_interval: Rebalancing time interval in seconds
            sl_percent: Stop-loss as percentage (e.g. `"0.2"` means 20%)
            tp_percent: Take-profit as percentage (e.g. `"0.5"` means 50%)
            trailing_stop_percent: Trailing stop callback as percentage (e.g. `"0.05"` means 5%)
            need_to_slippage: Whether to include slippage calculation
        """
        return self._native_private(
            "get_fcombobot_getlimit",
            self._native_params(
                **{
                    "leverage": leverage,
                    "init_margin": init_margin,
                    "adjust_position_mode": adjust_position_mode,
                    "symbol_settings": symbol_settings,
                    "adjust_position_percent": adjust_position_percent,
                    "adjust_position_time_interval": adjust_position_time_interval,
                    "sl_percent": sl_percent,
                    "tp_percent": tp_percent,
                    "trailing_stop_percent": trailing_stop_percent,
                    "need_to_slippage": need_to_slippage,
                }
            ),
        )

    def close_fgridbot(
        self,
        *,
        bot_id: str,
    ) -> dict[str, Any]:
        """
        Close Grid Bot. POST /v5/fgridbot/close.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-grid/close

        Args:
            bot_id: Bot ID to close, obtained from Create Futures Grid Bot response
        """
        return self._native_private(
            "close_fgridbot",
            self._native_params(
                **{
                    "bot_id": bot_id,
                }
            ),
        )

    def create_fgridbot(
        self,
        *,
        symbol: str,
        grid_mode: int,
        min_price: str,
        max_price: str,
        cell_number: int,
        leverage: str,
        grid_type: int,
        total_investment: str,
        take_profit_per: str | None = None,
        stop_loss_per: str | None = None,
        take_profit_price: str | None = None,
        stop_loss_price: str | None = None,
        tp_sl_type: int | None = None,
        entry_price: str | None = None,
        trailing_stop_per: str | None = None,
        move_up_price: str | None = None,
        move_down_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Grid Bot. POST /v5/fgridbot/create.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-grid/create

        Args:
            symbol: Trading pair symbol, uppercase only (e.g. `BTCUSDT`)
            grid_mode: Strategy direction: `1` Neutral, `2` Long, `3` Short
            min_price: Lower price bound of the grid range (decimal string)
            max_price: Upper price bound of the grid range (decimal string)
            cell_number: Number of grid levels, minimum 2
            leverage: Position leverage multiplier (e.g. `"5"` means 5x). Must be >= 1
            grid_type: Grid spacing type: `1` Arithmetic, `2` Geometric
            total_investment: Initial investment in quote currency (decimal string, e.g. `"1000"`
                for 1000 USDT)
            take_profit_per: Take-profit as percentage (e.g. `"0.2"` means 20%). Used when
                `tp_sl_type` includes percentage-based TP
            stop_loss_per: Stop-loss as percentage (e.g. `"0.1"` means 10%). Used when `tp_sl_type`
                includes percentage-based SL
            take_profit_price: Take-profit trigger price (decimal string). Used when `tp_sl_type`
                includes price-based TP
            stop_loss_price: Stop-loss trigger price (decimal string). Used when `tp_sl_type`
                includes price-based SL
            tp_sl_type: TP/SL trigger mode: `1` Both by %, `2` Both by price, `3` TP price+SL %, `4`
                TP %+SL price
            entry_price: Optional entry trigger price for delayed activation (decimal string)
            trailing_stop_per: Trailing stop exit as percentage (e.g. `"0.05"` means 5%)
            move_up_price: Move-up price for grid shifting, not applicable when "grid_type"=`2
            move_down_price: Move-down price for grid shifting, not applicable when "grid_type"=`2
        """
        return self._native_private(
            "create_fgridbot",
            self._native_params(
                **{
                    "symbol": symbol,
                    "grid_mode": grid_mode,
                    "min_price": min_price,
                    "max_price": max_price,
                    "cell_number": cell_number,
                    "leverage": leverage,
                    "grid_type": grid_type,
                    "total_investment": total_investment,
                    "take_profit_per": take_profit_per,
                    "stop_loss_per": stop_loss_per,
                    "take_profit_price": take_profit_price,
                    "stop_loss_price": stop_loss_price,
                    "tp_sl_type": tp_sl_type,
                    "entry_price": entry_price,
                    "trailing_stop_per": trailing_stop_per,
                    "move_up_price": move_up_price,
                    "move_down_price": move_down_price,
                }
            ),
        )

    def get_fgridbot_detail(
        self,
        *,
        bot_id: str,
    ) -> dict[str, Any]:
        """
        Get Grid Bot Detail. POST /v5/fgridbot/detail.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-grid/get-detail

        Args:
            bot_id: Bot ID to query
        """
        return self._native_private(
            "get_fgridbot_detail",
            self._native_params(
                **{
                    "bot_id": bot_id,
                }
            ),
        )

    def request_fgridbot_validate(
        self,
        *,
        symbol: str,
        cell_number: int,
        min_price: str,
        max_price: str,
        leverage: str,
        grid_type: int,
        grid_mode: int,
        stop_loss_price: str | None = None,
        take_profit_price: str | None = None,
        tp_sl_type: int | None = None,
        entry_price: str | None = None,
        stop_loss_per: str | None = None,
        take_profit_per: str | None = None,
        trailing_stop_per: str | None = None,
        init_margin: str | None = None,
        move_up_price: str | None = None,
        move_down_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate Grid Input. POST /v5/fgridbot/validate.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-grid/validate-input

        Args:
            symbol: Trading pair symbol, uppercase only (e.g. `BTCUSDT`)
            cell_number: Number of grid levels, minimum 2
            min_price: Lower price bound of the grid range (decimal string)
            max_price: Upper price bound of the grid range (decimal string)
            leverage: Position leverage, must be >= 1 (e.g. `"5"`)
            grid_type: Grid spacing type: `1` Arithmetic, `2` Geometric
            grid_mode: Strategy direction: `1` Neutral, `2` Long, `3` Short
            stop_loss_price: Stop-loss trigger price (decimal string). Used when `tp_sl_type`
                includes price-based SL
            take_profit_price: Take-profit trigger price (decimal string). Used when `tp_sl_type`
                includes price-based TP
            tp_sl_type: TP/SL trigger mode: `1` Both %, `2` Both price, `3` TP price+SL %, `4` TP
                %+SL price
            entry_price: Entry trigger price for delayed activation (decimal string)
            stop_loss_per: Stop-loss as percentage (e.g. `"10"` means 10%). Used when `tp_sl_type`
                includes percentage-based SL
            take_profit_per: Take-profit as percentage (e.g. `"20"` means 20%). Used when
                `tp_sl_type` includes percentage-based TP
            trailing_stop_per: Trailing stop callback as percentage (e.g. `"5"` means 5%)
            init_margin: Initial margin amount in quote currency (decimal string)
            move_up_price: Move-up price for grid shifting
            move_down_price: Move-down price for grid shifting
        """
        return self._native_private(
            "request_fgridbot_validate",
            self._native_params(
                **{
                    "symbol": symbol,
                    "cell_number": cell_number,
                    "min_price": min_price,
                    "max_price": max_price,
                    "leverage": leverage,
                    "grid_type": grid_type,
                    "grid_mode": grid_mode,
                    "stop_loss_price": stop_loss_price,
                    "take_profit_price": take_profit_price,
                    "tp_sl_type": tp_sl_type,
                    "entry_price": entry_price,
                    "stop_loss_per": stop_loss_per,
                    "take_profit_per": take_profit_per,
                    "trailing_stop_per": trailing_stop_per,
                    "init_margin": init_margin,
                    "move_up_price": move_up_price,
                    "move_down_price": move_down_price,
                }
            ),
        )

    def close_fmartingalebot(
        self,
        *,
        bot_id: str,
    ) -> dict[str, Any]:
        """
        Close Martingale Bot. POST /v5/fmartingalebot/close.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-martingale/close

        Args:
            bot_id: Bot ID to close, obtained from Create Futures Martingale Bot response
        """
        return self._native_private(
            "close_fmartingalebot",
            self._native_params(
                **{
                    "bot_id": bot_id,
                }
            ),
        )

    def create_fmartingalebot(
        self,
        *,
        symbol: str,
        martingale_mode: int,
        leverage: str,
        price_float_percent: str,
        add_position_percent: str,
        add_position_num: int,
        init_margin: str,
        round_tp_percent: str,
        auto_cycle_toggle: int | None = None,
        sl_percent: str | None = None,
        entry_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Martingale Bot. POST /v5/fmartingalebot/create.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-martingale/create

        Args:
            symbol: Trading pair symbol, uppercase only (e.g. `BTCUSDT`)
            martingale_mode: Strategy direction: `1` Long (buy dips), `2` Short (sell rallies)
            leverage: Position leverage multiplier (e.g. `"5"` means 5x). Must be >= 1
            price_float_percent: Price movement percentage to trigger a position add (e.g. `"0.015"`
                means add when price moves 1.5% against the position)
            add_position_percent: Position add scaling as percentage of base position size (e.g.
                `"1.1"` = 1.1x base; `"2"` = 2x base)
            add_position_num: Maximum number of position adds per round
            init_margin: Initial investment in quote currency (decimal string, e.g. `"1000"` for
                1000 USDT)
            round_tp_percent: Single round take-profit as percentage (e.g. `"0.03"` means close when
                profit reaches 3%)
            auto_cycle_toggle: Auto-cycle mode: `1` Enable (restart after TP), `2` Disable (stop
                after single TP)
            sl_percent: Stop-loss as percentage of total margin (e.g. `"0.2"` means close when loss
                reaches 20%). Leave empty if not set
            entry_price: Entry trigger price as absolute price (decimal string). Leave empty if not
                set
        """
        return self._native_private(
            "create_fmartingalebot",
            self._native_params(
                **{
                    "symbol": symbol,
                    "martingale_mode": martingale_mode,
                    "leverage": leverage,
                    "price_float_percent": price_float_percent,
                    "add_position_percent": add_position_percent,
                    "add_position_num": add_position_num,
                    "init_margin": init_margin,
                    "round_tp_percent": round_tp_percent,
                    "auto_cycle_toggle": auto_cycle_toggle,
                    "sl_percent": sl_percent,
                    "entry_price": entry_price,
                }
            ),
        )

    def get_fmartingalebot_detail(
        self,
        *,
        bot_id: str,
    ) -> dict[str, Any]:
        """
        Get Martingale Bot Detail. POST /v5/fmartingalebot/detail.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-martingale/get-detail

        Args:
            bot_id: Bot ID to query
        """
        return self._native_private(
            "get_fmartingalebot_detail",
            self._native_params(
                **{
                    "bot_id": bot_id,
                }
            ),
        )

    def get_fmartingalebot_getlimit(
        self,
        *,
        symbol: str,
        martingale_mode: int,
        leverage: str,
        price_float_percent: str | None = None,
        add_position_percent: str | None = None,
        add_position_num: int | None = None,
        init_margin: str | None = None,
        round_tp_percent: str | None = None,
        sl_percent: str | None = None,
        entry_price: str | None = None,
        need_to_slippage: bool | None = None,
        auto_cycle_toggle: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Bot Parameter Limit. POST /v5/fmartingalebot/getlimit.

        Source: https://bybit-exchange.github.io/docs/v5/bot/futures-martingale/get-limit

        Args:
            symbol: Trading pair symbol, uppercase only (e.g. `BTCUSDT`)
            martingale_mode: Strategy direction: `1` Long, `2` Short
            leverage: Position leverage multiplier (e.g. `"5"` means 5x). Must be >= 1
            price_float_percent: Price movement trigger as percentage (e.g. `"0.015"` means 1.5%)
            add_position_percent: Position add scaling as percentage of base position (e.g. `"1"` =
                1x)
            add_position_num: Maximum number of position adds per round
            init_margin: Initial investment in quote currency (decimal string)
            round_tp_percent: Single round take-profit as percentage (e.g. `"0.03"` means 3%)
            sl_percent: Stop-loss as percentage (e.g. `"0.2"` means 20%)
            entry_price: Entry trigger price (decimal string)
            need_to_slippage: Whether to include slippage calculation
            auto_cycle_toggle: Repeat cycles switch; official HTTP example uses integer 1.
        """
        return self._native_private(
            "get_fmartingalebot_getlimit",
            self._native_params(
                **{
                    "symbol": symbol,
                    "martingale_mode": martingale_mode,
                    "leverage": leverage,
                    "price_float_percent": price_float_percent,
                    "add_position_percent": add_position_percent,
                    "add_position_num": add_position_num,
                    "init_margin": init_margin,
                    "round_tp_percent": round_tp_percent,
                    "sl_percent": sl_percent,
                    "entry_price": entry_price,
                    "need_to_slippage": need_to_slippage,
                    "auto_cycle_toggle": auto_cycle_toggle,
                }
            ),
        )

    def request_grid_close_grid(
        self,
        *,
        grid_id: str,
        close_mode: str,
    ) -> dict[str, Any]:
        """
        Close Grid Bot. POST /v5/grid/close-grid.

        Official spec incomplete; not verified live. Uses documented grid_id/close_mode; the
        published example instead uses bot_id.
        Source: https://bybit-exchange.github.io/docs/v5/bot/spot-grid/close

        Args:
            grid_id: Grid bot ID to close, obtained from Create Spot Grid Bot response
            close_mode: Asset settlement mode: `2` Base token, `3` Quote token (e.g. USDT), `4` Base
                + Quote token
        """
        return self._native_private(
            "request_grid_close_grid",
            self._native_params(
                **{
                    "grid_id": grid_id,
                    "close_mode": close_mode,
                }
            ),
        )

    def request_grid_create_grid(
        self,
        *,
        symbol: str,
        max_price: str,
        min_price: str,
        cell_number: int,
        invest_mode: int | None = None,
        base_investment: str | None = None,
        quote_investment: str | None = None,
        entry_price: str | None = None,
        stop_loss_price: str | None = None,
        take_profit_price: str | None = None,
        ts_percent: str | None = None,
        enable_trailing: bool | None = None,
        limit_up_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Create Grid Bot. POST /v5/grid/create-grid.

        Source: https://bybit-exchange.github.io/docs/v5/bot/spot-grid/create

        Args:
            symbol: Trading pair symbol, uppercase only (e.g. `BTCUSDT`)
            max_price: Upper bound of the grid price range (decimal string)
            min_price: Lower bound of the grid price range (decimal string)
            cell_number: Number of grid intervals, minimum 2
            invest_mode: Investment mode. `0`: Quote only (default), `1`: Base only, `2`: Base +
                Quote
            base_investment: Investment in base token (decimal string). **Required** when
                `invest_mode` is `1` or `2
            quote_investment: Investment in quote token (decimal string). **Required** when
                `invest_mode` is `0` or `2
            entry_price: Entry trigger price (decimal string). Bot activates when market price
                reaches this level
            stop_loss_price: Stop-loss trigger price (decimal string)
            take_profit_price: Take-profit trigger price (decimal string)
            ts_percent: Trailing stop callback ratio, range `[0, 0.99]` (e.g. `"0.05"` means 5%)
            enable_trailing: Enable grid trailing (auto-shift). Requires `cell_number >= 5`.
                Default: `false
            limit_up_price: Upper limit price for grid trailing (decimal string), usd when
                "enable_trailing"=`true
        """
        return self._native_private(
            "request_grid_create_grid",
            self._native_params(
                **{
                    "symbol": symbol,
                    "max_price": max_price,
                    "min_price": min_price,
                    "cell_number": cell_number,
                    "invest_mode": invest_mode,
                    "base_investment": base_investment,
                    "quote_investment": quote_investment,
                    "entry_price": entry_price,
                    "stop_loss_price": stop_loss_price,
                    "take_profit_price": take_profit_price,
                    "ts_percent": ts_percent,
                    "enable_trailing": enable_trailing,
                    "limit_up_price": limit_up_price,
                }
            ),
        )

    def get_grid_query_grid_detail(
        self,
        *,
        grid_id: str,
    ) -> dict[str, Any]:
        """
        Get Grid Bot Detail. POST /v5/grid/query-grid-detail.

        Source: https://bybit-exchange.github.io/docs/v5/bot/spot-grid/get-detail

        Args:
            grid_id: Grid bot ID to query
        """
        return self._native_private(
            "get_grid_query_grid_detail",
            self._native_params(
                **{
                    "grid_id": grid_id,
                }
            ),
        )

    def request_grid_validate_input(
        self,
        *,
        symbol: str,
        cell_number: int,
        min_price: str,
        max_price: str,
        invest_mode: int | None = None,
        base_investment: str | None = None,
        quote_investment: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        entry_price: str | None = None,
        ts_percent: str | None = None,
        enable_trailing: bool | None = None,
        limit_up_price: str | None = None,
    ) -> dict[str, Any]:
        """
        Validate Grid Input. POST /v5/grid/validate-input.

        Source: https://bybit-exchange.github.io/docs/v5/bot/spot-grid/validate-input

        Args:
            symbol: Trading pair symbol, uppercase only (e.g. `BTCUSDT`)
            cell_number: Number of grid intervals, minimum 2
            min_price: Lower bound of the grid price range (decimal string)
            max_price: Upper bound of the grid price range. Must be greater than `min_price`
                (decimal string)
            invest_mode: Investment mode: `0` Quote only (default), `1` Base only, `2` Base + Quote
            base_investment: Investment in base token (decimal string). **Required** when
                `invest_mode` is `1` or `2
            quote_investment: Investment in quote token (decimal string). **Required** when
                `invest_mode` is `0` or `2
            stop_loss: Stop-loss as absolute price (decimal string)
            take_profit: Take-profit as absolute price (decimal string)
            entry_price: Entry trigger as absolute price (decimal string)
            ts_percent: Trailing stop callback ratio, range `[0, 0.99]` (e.g. `"0.05"` means 5%)
            enable_trailing: Whether to enable grid trailing. Requires `cell_number >= 5
            limit_up_price: Upper limit price for grid trailing (decimal string)
        """
        return self._native_public(
            "request_grid_validate_input",
            self._native_params(
                **{
                    "symbol": symbol,
                    "cell_number": cell_number,
                    "min_price": min_price,
                    "max_price": max_price,
                    "invest_mode": invest_mode,
                    "base_investment": base_investment,
                    "quote_investment": quote_investment,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "entry_price": entry_price,
                    "ts_percent": ts_percent,
                    "enable_trailing": enable_trailing,
                    "limit_up_price": limit_up_price,
                }
            ),
        )

    def get_broker_ip_changelog(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Broker IP Change Log. GET /v5/broker/ip/changelog.

        Source: https://bybit-exchange.github.io/docs/v5/broker/api-broker/ip-changelog

        Args:
            start_time: Filter start time, Unix timestamp in milliseconds
            end_time: Filter end time, Unix timestamp in milliseconds
            limit: Records per page. Range: [1, 50]. Default: 20
            cursor: Pagination cursor. Use the `nextPageCursor` value from the previous response
        """
        return self._native_private(
            "get_broker_ip_changelog",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_broker_whitelist_ip(
        self,
    ) -> dict[str, Any]:
        """
        Get Broker Whitelist IP. GET /v5/broker/whitelist/ip.

        Source: https://bybit-exchange.github.io/docs/v5/broker/api-broker/whitelist-ip
        """
        return self._native_public(
            "get_broker_whitelist_ip",
            [],
        )

    def get_broker_account_info(
        self,
    ) -> dict[str, Any]:
        """
        Get Account Info. GET /v5/broker/account-info.

        Source: https://bybit-exchange.github.io/docs/v5/broker/exchange-broker/account-info
        """
        return self._native_private(
            "get_broker_account_info",
            [],
        )

    def get_broker_earnings_info(
        self,
        *,
        biz_type: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        uid: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Earning. GET /v5/broker/earnings-info.

        Source: https://bybit-exchange.github.io/docs/v5/broker/exchange-broker/exchange-earning

        Args:
            biz_type: Business type. `SPOT`, `DERIVATIVES`, `OPTIONS`, `CONVERT`, `FIAT_CONVERT
            begin: Begin date, in the format of YYYYMMDD, e.g, 20231201, search the data from 1st
                Dec 2023 00:00:00 UTC (include)
            end: End date, in the format of YYYYMMDD, e.g, 20231201, search the data before 2nd Dec
                2023 00:00:00 UTC (exclude)
            uid: To get results for a specific subaccount: Enter the subaccount UIDTo get results
                for all subaccounts: Leave the field empty
            limit: Limit for data size per page. [`1`, `1000`]. Default: `1000
            cursor: Cursor. Use the `nextPageCursor` token from the response to retrieve the next
                page of the result set
        """
        return self._native_private(
            "get_broker_earnings_info",
            self._native_params(
                **{
                    "bizType": biz_type,
                    "begin": begin,
                    "end": end,
                    "uid": uid,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_broker_apilimit_query_all(
        self,
        *,
        limit: str | None = None,
        cursor: str | None = None,
        uids: str | None = None,
    ) -> dict[str, Any]:
        """
        Get All Rate Limits. GET /v5/broker/apilimit/query-all.

        Source: https://bybit-exchange.github.io/docs/v5/broker/exchange-broker/rate-limit/query-all

        Args:
            limit: Limit for data size per page. [`1`, `1000`]. Default: `1000
            cursor: Cursor. Use the `nextPageCursor` token from the response to retrieve the next
                page of the result set
            uids: Multiple UIDs across different master accounts, separated by commas. Returns all
                subaccounts by default
        """
        return self._native_private(
            "get_broker_apilimit_query_all",
            self._native_params(
                **{
                    "limit": limit,
                    "cursor": cursor,
                    "uids": uids,
                }
            ),
        )

    def get_broker_apilimit_query_cap(
        self,
    ) -> dict[str, Any]:
        """
        Get Rate Limit Cap. GET /v5/broker/apilimit/query-cap.

        Source: https://bybit-exchange.github.io/docs/v5/broker/exchange-broker/rate-limit/query-cap
        """
        return self._native_private(
            "get_broker_apilimit_query_cap",
            [],
        )

    def set_broker_apilimit(
        self,
        *,
        list_: list[Any],
    ) -> dict[str, Any]:
        """
        Set Rate Limit. POST /v5/broker/apilimit/set.

        Source: https://bybit-exchange.github.io/docs/v5/broker/exchange-broker/rate-limit/set

        Args:
            list_: Object
        """
        return self._native_private(
            "set_broker_apilimit",
            self._native_params(
                **{
                    "list": list_,
                }
            ),
        )

    def get_broker_asset_query_sub_member_deposit_record(
        self,
        *,
        id: str | None = None,
        tx_id: str | None = None,
        sub_member_id: str | None = None,
        coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Sub Account Deposit Records. GET /v5/broker/asset/query-sub-member-deposit-record.

        Source: https://bybit-exchange.github.io/docs/v5/broker/exchange-broker/sub-deposit-record

        Args:
            id: Internal ID: Can be used to uniquely identify and filter the deposit. When combined
                with other parameters, this field takes the highest priority
            tx_id: Transaction ID: Please note that data generated before Jan 1, 2024 cannot be
                queried using txID
            sub_member_id: Sub UID
            coin: Coin, uppercase only
            start_time: The start timestamp (ms) _Note: the query logic is actually effective based
                on **second** level_
            end_time: The end timestamp (ms) _Note: the query logic is actually effective based on
                **second** level_
            limit: Limit for data size per page. [`1`, `50`]. Default: `50
            cursor: Cursor. Use the `nextPageCursor` token from the response to retrieve the next
                page of the result set
        """
        return self._native_private(
            "get_broker_asset_query_sub_member_deposit_record",
            self._native_params(
                **{
                    "id": id,
                    "txID": tx_id,
                    "subMemberId": sub_member_id,
                    "coin": coin,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def request_broker_award_distribution_record(
        self,
        *,
        account_id: str,
        award_id: str,
        spec_code: str,
        with_used_amount: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get Issued Voucher. POST /v5/broker/award/distribution-record.

        Source: https://bybit-exchange.github.io/docs/v5/broker/reward/get-issue-voucher

        Args:
            account_id: User ID
            award_id: Voucher ID
            spec_code: Customised unique spec code, up to 8 characters
            with_used_amount: Whether or not to return the amount used by the user `true``false`
                (default)
        """
        return self._native_private(
            "request_broker_award_distribution_record",
            self._native_params(
                **{
                    "accountId": account_id,
                    "awardId": award_id,
                    "specCode": spec_code,
                    "withUsedAmount": with_used_amount,
                }
            ),
        )

    def request_broker_award_distribute_award(
        self,
        *,
        account_id: str,
        award_id: str,
        spec_code: str,
        amount: str,
        broker_id: str,
    ) -> dict[str, Any]:
        """
        Issue Voucher. POST /v5/broker/award/distribute-award.

        Source: https://bybit-exchange.github.io/docs/v5/broker/reward/issue-voucher

        Args:
            account_id: User ID
            award_id: Voucher ID
            spec_code: Customised unique spec code, up to 8 characters
            amount: Issue amount Spot airdrop supports up to 16 decimalsOther types supports up to 4
                decimals
            broker_id: Broker ID
        """
        return self._native_private(
            "request_broker_award_distribute_award",
            self._native_params(
                **{
                    "accountId": account_id,
                    "awardId": award_id,
                    "specCode": spec_code,
                    "amount": amount,
                    "brokerId": broker_id,
                }
            ),
        )

    def get_broker_award_info(
        self,
        *,
        id: str,
    ) -> dict[str, Any]:
        """
        Get Voucher Spec. POST /v5/broker/award/info.

        Source: https://bybit-exchange.github.io/docs/v5/broker/reward/voucher

        Args:
            id: Voucher ID
        """
        return self._native_private(
            "get_broker_award_info",
            self._native_params(
                **{
                    "id": id,
                }
            ),
        )

    def get_card_transaction_query_asset_records(
        self,
        *,
        status_code: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        pan4: str | None = None,
        create_begin_time: int | None = None,
        create_end_time: int | None = None,
        merch_name: str | None = None,
        type_: str | None = None,
        txn_id: str | None = None,
        card_token: str | None = None,
        order_no: str | None = None,
    ) -> dict[str, Any]:
        """
        Query Asset Records. POST /v5/card/transaction/query-asset-records.

        Source: https://bybit-exchange.github.io/docs/v5/bybit-card/asset-records

        Args:
            status_code: Transaction status code. `0`: Pending, `1`: Cleared, `2`: Declined
            limit: Number of items per page. Default: `100`. Range: [`1`, `500`]
            page: Page number. Default: `1`. Min: `1
            pan4: Last 2/4 digits of card number, used to filter transactions of a specific card
            create_begin_time: Start time of transaction (Unix ms timestamp)
            create_end_time: End time of transaction (Unix ms timestamp)
            merch_name: Merchant name. Supports fuzzy search
            type_: Query type.`SIDE_QUERY_AUTH`: Authorization`SIDE_QUERY_FINANCIAL`: Clearing.
                Requires `txnId` and `orderNo`.`SIDE_QUERY_REFUND`: Refund. Requires `txnId` and
                `orderNo`.The following query types are available to all
                users:`SIDE_QUERY_AUTH_ALL`: All authorization
                transactions`SIDE_QUERY_AUTH_REVERSAL`: Authorization
                reversals`SIDE_QUERY_FINANCIAL_ALL`: All clearing
                transactions`SIDE_QUERY_FINANCIAL_REFUND`: Clearing refunds
            txn_id: Transaction ID. Exact match
            card_token: Card token, used to identify a specific card
            order_no: Order number. Exact match
        """
        return self._native_private(
            "get_card_transaction_query_asset_records",
            self._native_params(
                **{
                    "statusCode": status_code,
                    "limit": limit,
                    "page": page,
                    "pan4": pan4,
                    "createBeginTime": create_begin_time,
                    "createEndTime": create_end_time,
                    "merchName": merch_name,
                    "type": type_,
                    "txnId": txn_id,
                    "cardToken": card_token,
                    "orderNo": order_no,
                }
            ),
        )

    def get_card_reward_points_balance(
        self,
    ) -> dict[str, Any]:
        """
        Query Point Balance. POST /v5/card/reward/points/balance.

        Source: https://bybit-exchange.github.io/docs/v5/bybit-card/point/balance
        """
        return self._native_private(
            "get_card_reward_points_balance",
            [],
        )

    def get_card_reward_point_cashback_detail(
        self,
        *,
        biz_txn_id: str,
    ) -> dict[str, Any]:
        """
        Query Cashback Detail. POST /v5/card/reward/point/cashback/detail.

        Source: https://bybit-exchange.github.io/docs/v5/bybit-card/point/cashback-detail

        Args:
            biz_txn_id: Order ID
        """
        return self._native_private(
            "get_card_reward_point_cashback_detail",
            self._native_params(
                **{
                    "bizTxnId": biz_txn_id,
                }
            ),
        )

    def get_card_reward_mall_item_list(
        self,
        *,
        page_no: int | None = None,
        page_size: int | None = None,
        item_type: int | None = None,
        item_biz_type: int | None = None,
        order_by: int | None = None,
        asc: bool | None = None,
        source: int | None = None,
    ) -> dict[str, Any]:
        """
        Query Mall Item List. POST /v5/card/reward/mall/item/list.

        Source: https://bybit-exchange.github.io/docs/v5/bybit-card/point/item-list

        Args:
            page_no: Page number. Default: `1`. Min: `1
            page_size: Number of items per page. Default: `10`. Min: `1
            item_type: Item type. `1`: Virtual item, `2`: Physical item
            item_biz_type: Item sub-type. `1`: POINTS, `2`: CURRENCY
            order_by: Sort type. `1`: Priority, `2`: Listing time, `3`: Price
            asc: Whether to sort in ascending order
            source: Query source. `0`: Default, `1`: VIP item list
        """
        return self._native_private(
            "get_card_reward_mall_item_list",
            self._native_params(
                **{
                    "pageNo": page_no,
                    "pageSize": page_size,
                    "itemType": item_type,
                    "itemBizType": item_biz_type,
                    "orderBy": order_by,
                    "asc": asc,
                    "source": source,
                }
            ),
        )

    def get_card_reward_points_records(
        self,
        *,
        type_: str | None = None,
        page_size: int | None = None,
        page_no: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        out_order_id: str | None = None,
        biz_id: str | None = None,
        biz_txn_id: str | None = None,
        side: str | None = None,
    ) -> dict[str, Any]:
        """
        Query Point Records. POST /v5/card/reward/points/records.

        Source: https://bybit-exchange.github.io/docs/v5/bybit-card/point/records

        Args:
            type_: Point type filter
            page_size: Number of items per page. Default: `10`. Min: `1
            page_no: Page number. Default: `1`. Min: `1
            start_time: Start time (Unix timestamp)
            end_time: End time (Unix timestamp)
            out_order_id: External order ID
            biz_id: Point order ID
            biz_txn_id: consumeIdLifecycle
            side: Point direction. `1`: Earn points, `2`: Deduct points
        """
        return self._native_private(
            "get_card_reward_points_records",
            self._native_params(
                **{
                    "type": type_,
                    "pageSize": page_size,
                    "pageNo": page_no,
                    "startTime": start_time,
                    "endTime": end_time,
                    "outOrderId": out_order_id,
                    "bizId": biz_id,
                    "bizTxnId": biz_txn_id,
                    "side": side,
                }
            ),
        )

    def get_card_reward_points_tier(
        self,
    ) -> dict[str, Any]:
        """
        Query Tier Info. POST /v5/card/reward/points/tier.

        Source: https://bybit-exchange.github.io/docs/v5/bybit-card/point/tier
        """
        return self._native_private(
            "get_card_reward_points_tier",
            [],
        )

    def request_demo_funds(
        self,
        *,
        adjust_type: int | None = None,
        uta_demo_apply_money: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        Demo Trading Service. POST /v5/account/demo-apply-money.

        Source: https://bybit-exchange.github.io/docs/v5/demo

        Args:
            adjust_type: 0`(default): add demo funds; `1`: reduce demo funds
            uta_demo_apply_money:
        """
        return self._native_private(
            "request_demo_funds",
            self._native_params(
                **{
                    "adjustType": adjust_type,
                    "utaDemoApplyMoney": uta_demo_apply_money,
                }
            ),
        )

    def create_demo_member(
        self,
    ) -> dict[str, Any]:
        """
        Demo Trading Service. POST /v5/user/create-demo-member.

        Source: https://bybit-exchange.github.io/docs/v5/demo
        """
        return self._native_private(
            "create_demo_member",
            [],
        )

    def get_event_instruments_info(
        self,
        *,
        symbol: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Instrument Info. GET /v5/event/instruments-info.

        Source: https://bybit-exchange.github.io/docs/v5/event/market/instrument-info

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
            status: PreLaunch`, `Trading`, `Delivering`, `Closed
            limit: Items per page. Default: `50`, range: [`1`, `100`]
            cursor: Pagination cursor. Use `nextPageCursor` from the previous response
        """
        return self._native_public(
            "get_event_instruments_info",
            self._native_params(
                **{
                    "symbol": symbol,
                    "status": status,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_event_orderbook(
        self,
        *,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Get Orderbook. GET /v5/event/orderbook.

        Source: https://bybit-exchange.github.io/docs/v5/event/market/orderbook

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
        """
        return self._native_public(
            "get_event_orderbook",
            self._native_params(
                **{
                    "symbol": symbol,
                }
            ),
        )

    def cancel_event_quote(
        self,
        *,
        order_link_id: str | None = None,
        order_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel Quote. POST /v5/event/cancel.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/cancel-quote

        Args:
            order_link_id: User-defined order ID (Quote ID)
            order_id: Order ID
        """
        return self._native_private(
            "cancel_event_quote",
            self._native_params(
                **{
                    "orderLinkId": order_link_id,
                    "orderId": order_id,
                }
            ),
        )

    def get_event_trades(
        self,
        *,
        symbol: str,
        order_id: str | None = None,
        order_link_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Event Contract Trade History. GET /v5/event/trades.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/execution

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
            order_id: Order ID filter
            order_link_id: User-defined order ID
            start_time: Start time in milliseconds. Default: 7 days ago
            end_time: End time in milliseconds. Default: now
            limit: Number of items per page. Default: `50`, Range: [`1`, `100`]
            cursor: Pagination cursor
        """
        return self._native_private(
            "get_event_trades",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderId": order_id,
                    "orderLinkId": order_link_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_event_order_realtime(
        self,
        *,
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Event Contract Active Orders. GET /v5/event/order-realtime.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/open-order

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
            order_id: Order ID. If both `orderId` and `orderLinkId` are passed, `orderId` takes
                priority
            order_link_id: User-defined order ID
            limit: Number of items per page. Default: `20`, Range: [`1`, `50`]
            cursor: Pagination cursor. Use `nextPageCursor` from the response to retrieve the next
                page
        """
        return self._native_private(
            "get_event_order_realtime",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderId": order_id,
                    "orderLinkId": order_link_id,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_event_order_list(
        self,
        *,
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Event Contract Order History. GET /v5/event/order-list.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/order-list

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
            order_id: Order ID
            order_link_id: User-defined order ID
            start_time: Start time in milliseconds. Default: 7 days ago
            end_time: End time in milliseconds. Default: now
            limit: Number of items per page. Default: `50`, Range: [`1`, `100`]
            cursor: Pagination cursor
        """
        return self._native_private(
            "get_event_order_list",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderId": order_id,
                    "orderLinkId": order_link_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_event_positions(
        self,
        *,
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Event Contract Position Info. GET /v5/event/positions.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/position

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT`. If not passed, returns all
                Event Contract positions
            base_coin: Base coin filter, e.g. `BTC
            settle_coin: Settle coin filter, e.g. `USDT
            limit: Number of items per page. Default: `20`, Range: [`1`, `50`]
            cursor: Pagination cursor. Use `nextPageCursor` from the response to retrieve the next
                page
        """
        return self._native_private(
            "get_event_positions",
            self._native_params(
                **{
                    "symbol": symbol,
                    "baseCoin": base_coin,
                    "settleCoin": settle_coin,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_event_settlements(
        self,
        *,
        symbol: str,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Event Contract Settlement Records. GET /v5/event/settlements.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/settlement

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
            order_id: Order ID filter
            start_time: Start time in milliseconds. Default: 7 days ago
            end_time: End time in milliseconds. Default: now
            limit: Number of items per page. Default: `50`, Range: [`1`, `100`]
            cursor: Pagination cursor
        """
        return self._native_private(
            "get_event_settlements",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderId": order_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def submit_event_quote(
        self,
        *,
        symbol: str,
        order_link_id: str,
        gross_payout_ratio: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        Submit Quote. POST /v5/event/quotes.

        Source: https://bybit-exchange.github.io/docs/v5/event/trade/submit-quote

        Args:
            symbol: Symbol name, e.g. `ETHUSDT-28AUG26-2450-2570-OUT
            order_link_id: User-defined order ID
            gross_payout_ratio: Gross payout ratio reported by the institution
            amount: Amount for this quote (settle coin)
        """
        return self._native_private(
            "submit_event_quote",
            self._native_params(
                **{
                    "symbol": symbol,
                    "orderLinkId": order_link_id,
                    "grossPayoutRatio": gross_payout_ratio,
                    "amount": amount,
                }
            ),
        )

    def request_file_get_file_upload_sign(
        self,
        *,
        file_type: str,
        file_md5: str,
        file_len: int,
        file_name: str,
        file_mime_type: str,
    ) -> dict[str, Any]:
        """
        Get File Upload Sign. POST /v5/file/get-file-upload-sign.

        Source: https://bybit-exchange.github.io/docs/v5/file/file-upload-sign

        Args:
            file_type: File business type: `fiat-pdf`, `fiat-image`, `fiat-video
            file_md5: Base64-encoded MD5 of the file content. Formula: `base64(md5(file_content))`,
                MD5 is **raw binary (16 bytes), not hex**.Golden cases for self-verification:Empty
                string `""` → `1B2M2Y8AsgTpgAmY7PhCfg==``"abc"` (3 bytes) →
                `kAFQmDzST7DWlj99KOF/cg==
            file_len: Current file size in bytes. Upper limit: `fiat-pdf` / `fiat-image` /
                `fiat-video` all `104857600` (100 MB)
            file_name: Full file name, e.g. `evidence.pdf`, `screenshot.png`, `video.mp4
            file_mime_type: File `Content-Type`.`fiat-pdf`: `application/pdf``fiat-image`:
                `image/jpeg`, `image/png`, `image/jpg``fiat-video`: `video/mp4`, `video/quicktime`,
                `video/3gpp`, `video/x-msvideo`, `video/avi`, `video/rm`, `video/rmvb`, `video/wmv
        """
        return self._native_private(
            "request_file_get_file_upload_sign",
            self._native_params(
                **{
                    "fileType": file_type,
                    "fileMd5": file_md5,
                    "fileLen": file_len,
                    "fileName": file_name,
                    "fileMimeType": file_mime_type,
                }
            ),
        )

    def request_file_report_file_upload(
        self,
        *,
        resource_id: str,
    ) -> dict[str, Any]:
        """
        Report File Upload. POST /v5/file/report-file-upload.

        Source: https://bybit-exchange.github.io/docs/v5/file/report-file-upload

        Args:
            resource_id: Resource ID returned by Get File Upload Sign
        """
        return self._native_private(
            "request_file_report_file_upload",
            self._native_params(
                **{
                    "resourceId": resource_id,
                }
            ),
        )

    def get_earn_pwm_asset_manager_all_funds(
        self,
        *,
        coin: str | None = None,
        fund_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get All Funds. GET /v5/earn/pwm/asset-manager/all-funds.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/all-funds

        Args:
            coin: Filter by coin
            fund_id: Filter by fund ID. Only funds created by the institution via Open API can be
                queried
            status: Filter by status: `PendingSubscribe` / `Active` / `Closing` / `Closed
            limit: Page size. Default: `20`, max: `50
            cursor: Pagination cursor (uses fund ID as cursor)
        """
        return self._native_private(
            "get_earn_pwm_asset_manager_all_funds",
            self._native_params(
                **{
                    "coin": coin,
                    "fundId": fund_id,
                    "status": status,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_earn_pwm_asset_manager_all_order(
        self,
        *,
        fund_id: str | None = None,
        order_type: str | None = None,
        status: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get All Fund Orders. GET /v5/earn/pwm/asset-manager/all-order.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/all-order

        Args:
            fund_id: Filter by fund ID. Returns orders for all managed funds if omitted
            order_type: Order type filter: `Subscribe` / `Redeem`. Returns all if omitted
            status: Order status filter: `Pending Review` / `Processing` / `Completed` / `Rejected`
                / `Failed`. Returns all if omitted
            start_time: Start time in milliseconds. See time range rules below
            end_time: End time in milliseconds. See time range rules below
            limit: Page size. Default: `20`, max: `50
            cursor: Pagination cursor (uses order `orderId` as cursor)
        """
        return self._native_private(
            "get_earn_pwm_asset_manager_all_order",
            self._native_params(
                **{
                    "fundId": fund_id,
                    "orderType": order_type,
                    "status": status,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def request_earn_pwm_asset_manager_create_fund(
        self,
        *,
        fund_name: str,
        coin: str,
        profit_share_rate: str,
        management_fee_rate: str,
        fund_introduction: str | None = None,
        req_link_id: str,
    ) -> dict[str, Any]:
        """
        Create Fund (Pending Subscription). POST /v5/earn/pwm/asset-manager/create-fund.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/create-fund

        Args:
            fund_name: Fund name, 1–50 characters
            coin: Base coin. Supported values: `BTC`, `ETH`, `USDT`, `USDC`, `SOL`, `MNT`, `XRP
            profit_share_rate: High-watermark profit sharing rate (%), range: 0–100
            management_fee_rate: Management fee rate (annualized %), range: 0–100
            fund_introduction: Fund introduction ID (must be in the institution's allowed list)
            req_link_id: User-defined request ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "request_earn_pwm_asset_manager_create_fund",
            self._native_params(
                **{
                    "fundName": fund_name,
                    "coin": coin,
                    "profitShareRate": profit_share_rate,
                    "managementFeeRate": management_fee_rate,
                    "fundIntroduction": fund_introduction,
                    "reqLinkId": req_link_id,
                }
            ),
        )

    def request_earn_pwm_asset_manager_create_investment_plan(
        self,
        *,
        account_uid: str,
        plan_name: str,
        plan_type: str,
        investment_distribution: list[Any],
        req_link_id: str,
    ) -> dict[str, Any]:
        """
        Create Investment Plan. POST /v5/earn/pwm/asset-manager/create-investment-plan.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/create-investment-plan

        Args:
            account_uid: Target user UID
            plan_name: Investment plan name, max 50 characters
            plan_type: Plan type: `stable` / `advanced
            investment_distribution: Fund configuration list. At least 1 fund required
            req_link_id: User-defined request ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "request_earn_pwm_asset_manager_create_investment_plan",
            self._native_params(
                **{
                    "accountUid": account_uid,
                    "planName": plan_name,
                    "planType": plan_type,
                    "investmentDistribution": investment_distribution,
                    "reqLinkId": req_link_id,
                }
            ),
        )

    def request_earn_pwm_asset_manager_create_sub_account(
        self,
        *,
        fund_id: str,
        req_link_id: str,
    ) -> dict[str, Any]:
        """
        Create Fund Sub-Account. POST /v5/earn/pwm/asset-manager/create-sub-account.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/create-sub-account

        Args:
            fund_id: Fund ID
            req_link_id: User-defined request ID, used to prevent duplicate creation
        """
        return self._native_private(
            "request_earn_pwm_asset_manager_create_sub_account",
            self._native_params(
                **{
                    "fundId": fund_id,
                    "reqLinkId": req_link_id,
                }
            ),
        )

    def get_earn_pwm_asset_manager_get_investment_plan(
        self,
        *,
        plan_id: str | None = None,
        status: str | None = None,
        subscription_uid: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Investment Plans. GET /v5/earn/pwm/asset-manager/get-investment-plan.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/get-investment-plan

        Args:
            plan_id: Investment plan ID. Returns all plans if omitted. Only plans created by the
                institution via Open API can be queried
            status: Filter by status: `PendingSubscription` / `Active` / `Closed` / `Deleted`.
                Returns all if omitted
            subscription_uid: UID of the user who subscribed to the investment plan
            limit: Page size. Default: `20`, max: `50
            cursor: Pagination cursor
        """
        return self._native_private(
            "get_earn_pwm_asset_manager_get_investment_plan",
            self._native_params(
                **{
                    "planId": plan_id,
                    "status": status,
                    "subscriptionUid": subscription_uid,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def request_earn_pwm_asset_manager_manage_investment_plan(
        self,
        *,
        plan_id: str,
        update_status: str | None = None,
        update_funds: list[Any] | None = None,
        req_link_id: str,
    ) -> dict[str, Any]:
        """
        Manage Investment Plan. POST /v5/earn/pwm/asset-manager/manage-investment-plan.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/manage-investment-plan

        Args:
            plan_id: Investment plan ID
            update_status: Update plan status. Options: `Closed` / `Deleted`. Status is unchanged if
                omitted
            update_funds: Fund list to update. If a matching `fundId` exists, the amount is updated;
                otherwise a new fund is added. Max 10 entries. Returns an error if duplicate
                `fundId` entries are present
            req_link_id: User-defined request ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "request_earn_pwm_asset_manager_manage_investment_plan",
            self._native_params(
                **{
                    "planId": plan_id,
                    "updateStatus": update_status,
                    "updateFunds": update_funds,
                    "reqLinkId": req_link_id,
                }
            ),
        )

    def request_earn_pwm_asset_manager_manage_order(
        self,
        *,
        order_id: str,
        action: str,
        req_link_id: str,
    ) -> dict[str, Any]:
        """
        Manage Order. POST /v5/earn/pwm/asset-manager/manage-order.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/manage-order

        Args:
            order_id: Order ID. Must be in `Pending Review` status
            action: Action to perform: `approve` / `reject
            req_link_id: User-defined request ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "request_earn_pwm_asset_manager_manage_order",
            self._native_params(
                **{
                    "orderId": order_id,
                    "action": action,
                    "reqLinkId": req_link_id,
                }
            ),
        )

    def request_earn_pwm_asset_manager_settle_profit(
        self,
        *,
        fund_id: str,
        req_link_id: str,
    ) -> dict[str, Any]:
        """
        Settle Fund Profit. POST /v5/earn/pwm/asset-manager/settle-profit.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/asset-manager/settle-profit

        Args:
            fund_id: Fund ID
            req_link_id: User-defined request ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "request_earn_pwm_asset_manager_settle_profit",
            self._native_params(
                **{
                    "fundId": fund_id,
                    "reqLinkId": req_link_id,
                }
            ),
        )

    def create_earn_pwm_customize_plan(
        self,
        *,
        account_type: str | None = None,
        products: list[Any],
    ) -> dict[str, Any]:
        """
        Create Customize Investment Plan. POST /v5/earn/pwm/customize-plan/create.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/customize-plan/create

        Args:
            account_type: Source account type. Default: `FUND
            products: Product configuration list. At least 1 item required
        """
        return self._native_private(
            "create_earn_pwm_customize_plan",
            self._native_params(
                **{
                    "accountType": account_type,
                    "products": products,
                }
            ),
        )

    def get_earn_pwm_customize_plan_product(
        self,
    ) -> dict[str, Any]:
        """
        Get Subscribable Product Info. GET /v5/earn/pwm/customize-plan/product.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/customize-plan/product
        """
        return self._native_public(
            "get_earn_pwm_customize_plan_product",
            [],
        )

    def request_earn_pwm_fund_transfer(
        self,
        *,
        transfer_id: str,
        from_user_id: int,
        to_user_id: int,
        amount: str,
        coin: str,
    ) -> dict[str, Any]:
        """
        Fund Transfer Between Sub-Accounts. POST /v5/earn/pwm/fund-transfer.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/fund-transfer

        Args:
            transfer_id: Transfer request ID
            from_user_id: Source UID. Must be a custodian sub-account of the current fund
            to_user_id: Destination UID. Must be a custodian sub-account of the current fund
            amount: Transfer amount
            coin: Coin name
        """
        return self._native_private(
            "request_earn_pwm_fund_transfer",
            self._native_params(
                **{
                    "transferId": transfer_id,
                    "fromUserId": from_user_id,
                    "toUserId": to_user_id,
                    "amount": amount,
                    "coin": coin,
                }
            ),
        )

    def get_earn_pwm_investment_plan_all(
        self,
        *,
        plan_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get All Investment Plans. GET /v5/earn/pwm/investment-plan/all.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/all

        Args:
            plan_id: Investment plan ID. Returns all plans if omitted
            status: Filter by status: `PendingSubscription` / `Active` / `Closed`. Returns all if
                omitted
            limit: Page size. Default: `20`, max: `50
            cursor: Pagination cursor
        """
        return self._native_private(
            "get_earn_pwm_investment_plan_all",
            self._native_params(
                **{
                    "planId": plan_id,
                    "status": status,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_earn_pwm_investment_plan_asset_trend(
        self,
        *,
        plan_id: str,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Asset Trend. GET /v5/earn/pwm/investment-plan/asset-trend.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/asset-trend

        Args:
            plan_id: Investment plan ID
            start_time: Start timestamp (ms). Default: current time minus 7 days
            end_time: End timestamp (ms). Default: current time
        """
        return self._native_private(
            "get_earn_pwm_investment_plan_asset_trend",
            self._native_params(
                **{
                    "planId": plan_id,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    def claim_earn_pwm_investment_plan(
        self,
        *,
        plan_id: str,
        to_account_type: str | None = None,
        order_link_id: str,
    ) -> dict[str, Any]:
        """
        Claim Withdrawable Funds. POST /v5/earn/pwm/investment-plan/claim.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/claim

        Args:
            plan_id: Investment plan ID. Must be in `Active` status
            to_account_type: Target account type. Default: `FUND
            order_link_id: User-defined order ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "claim_earn_pwm_investment_plan",
            self._native_params(
                **{
                    "planId": plan_id,
                    "toAccountType": to_account_type,
                    "orderLinkId": order_link_id,
                }
            ),
        )

    def get_earn_pwm_investment_plan_detail(
        self,
        *,
        plan_id: str,
    ) -> dict[str, Any]:
        """
        Get Investment Plan Detail. GET /v5/earn/pwm/investment-plan/detail.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/detail

        Args:
            plan_id: Investment plan ID. Must be in `Active` or `Closed` status
        """
        return self._native_private(
            "get_earn_pwm_investment_plan_detail",
            self._native_params(
                **{
                    "planId": plan_id,
                }
            ),
        )

    def get_earn_pwm_investment_plan_fund_nav(
        self,
        *,
        fund_id: str,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Fund Historical NAV. GET /v5/earn/pwm/investment-plan/fund-nav.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/fund-nav

        Args:
            fund_id: Fund ID
            start_time: Start timestamp (ms). Default: current time minus 7 days
            end_time: End timestamp (ms). Default: current time
        """
        return self._native_private(
            "get_earn_pwm_investment_plan_fund_nav",
            self._native_params(
                **{
                    "fundId": fund_id,
                    "startTime": start_time,
                    "endTime": end_time,
                }
            ),
        )

    def request_earn_pwm_investment_plan_invest_more(
        self,
        *,
        plan_id: str,
        account_type: str | None = None,
        category: str,
        product_id: str,
        amount: str,
        order_link_id: str,
    ) -> dict[str, Any]:
        """
        Invest More. POST /v5/earn/pwm/investment-plan/invest-more.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/invest-more

        Args:
            plan_id: Investment plan ID. Must be in `Active` status
            account_type: Source account type. Default: `FUND
            category: Product type
            product_id: Product ID
            amount: Additional investment amount (base coin)
            order_link_id: User-defined order ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "request_earn_pwm_investment_plan_invest_more",
            self._native_params(
                **{
                    "planId": plan_id,
                    "accountType": account_type,
                    "category": category,
                    "productId": product_id,
                    "amount": amount,
                    "orderLinkId": order_link_id,
                }
            ),
        )

    def get_earn_pwm_investment_plan_new_plan(
        self,
        *,
        plan_id: str,
    ) -> dict[str, Any]:
        """
        Get Pending Investment Plan Detail. GET /v5/earn/pwm/investment-plan/new-plan.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/new-plan

        Args:
            plan_id: Investment plan ID. Must be in `PendingSubscription` status
        """
        return self._native_private(
            "get_earn_pwm_investment_plan_new_plan",
            self._native_params(
                **{
                    "planId": plan_id,
                }
            ),
        )

    def get_earn_pwm_investment_plan_order(
        self,
        *,
        plan_id: str | None = None,
        category: str | None = None,
        type_: str | None = None,
        status: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        order_link_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Investment Plan Orders. GET /v5/earn/pwm/investment-plan/order.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/order

        Args:
            plan_id: Investment plan ID. Returns orders for all plans if omitted
            category: Product type filter: `flexibleSavings` / `fundPool` / `fundPoolPremium` /
                `equityFund` / `onchainEarn`. Returns all if omitted
            type_: Order type filter: `Subscribe` / `Redeem`. Returns all if omitted
            status: Order status filter: `Completed` / `Pending` / `Failed`. Returns all if omitted
            start_time: Start time in milliseconds. No lower limit if omitted
            end_time: End time in milliseconds. Defaults to current time if omitted
            limit: Page size. Default: `20`, max: `50
            cursor: Pagination cursor
            order_link_id: User-defined order ID, max 36 characters
        """
        return self._native_private(
            "get_earn_pwm_investment_plan_order",
            self._native_params(
                **{
                    "planId": plan_id,
                    "category": category,
                    "type": type_,
                    "status": status,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                    "orderLinkId": order_link_id,
                }
            ),
        )

    def redeem_earn_pwm_investment_plan(
        self,
        *,
        plan_id: str,
        category: str,
        product_id: str,
        shares: str | None = None,
        amount: str | None = None,
        order_link_id: str,
        position_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Redeem. POST /v5/earn/pwm/investment-plan/redeem.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/redeem

        Args:
            plan_id: Investment plan ID
            category: Product type
            product_id: Product ID. Pass `fundId` for fund products
            shares: Number of shares to redeem. Required for fund products
            amount: Redemption amount. Required for non-fund products
            order_link_id: User-defined order ID, max 36 characters, used for idempotency
            position_id: Position ID to redeem. Required for FundPool and On-chain Earn products
        """
        return self._native_private(
            "redeem_earn_pwm_investment_plan",
            self._native_params(
                **{
                    "planId": plan_id,
                    "category": category,
                    "productId": product_id,
                    "shares": shares,
                    "amount": amount,
                    "orderLinkId": order_link_id,
                    "positionId": position_id,
                }
            ),
        )

    def subscribe_earn_pwm_investment_plan(
        self,
        *,
        plan_id: str,
        account_type: str | None = None,
        order_link_id: str,
    ) -> dict[str, Any]:
        """
        Subscribe Investment Plan. POST /v5/earn/pwm/investment-plan/subscribe.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/investment-plan/subscribe

        Args:
            plan_id: Investment plan ID. Must be in `PendingSubscription` status
            account_type: Source account type. Default: `FUND
            order_link_id: User-defined order ID, max 36 characters, used for idempotency
        """
        return self._native_private(
            "subscribe_earn_pwm_investment_plan",
            self._native_params(
                **{
                    "planId": plan_id,
                    "accountType": account_type,
                    "orderLinkId": order_link_id,
                }
            ),
        )

    def get_earn_pwm_query_fund_transfer_result(
        self,
        *,
        transfer_id: str | None = None,
        from_user_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Fund Transfer Records. GET /v5/earn/pwm/query-fund-transfer-result.

        Source: https://bybit-exchange.github.io/docs/v5/finance/pwm/query-fund-transfer-result

        Args:
            transfer_id: Transfer request ID. If omitted, returns up to the 20 most recent
                non-terminal transfer records within the past month. Records older than one month
                may have been archived
            from_user_id: Source UID
        """
        return self._native_private(
            "get_earn_pwm_query_fund_transfer_result",
            self._native_params(
                **{
                    "transferId": transfer_id,
                    "fromUserId": from_user_id,
                }
            ),
        )

    def get_ins_ip_changelog(
        self,
        *,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Institution IP Change Log. GET /v5/ins/ip/changelog.

        Source: https://bybit-exchange.github.io/docs/v5/institution/ip-changelog

        Args:
            start_time: Filter start time, Unix timestamp in milliseconds
            end_time: Filter end time, Unix timestamp in milliseconds
            limit: Records per page. Range: [1, 50]. Default: 20
            cursor: Pagination cursor. Use the `nextPageCursor` value from the previous response
        """
        return self._native_private(
            "get_ins_ip_changelog",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "cursor": cursor,
                }
            ),
        )

    def get_ins_whitelist_ip(
        self,
    ) -> dict[str, Any]:
        """
        Get Institution Whitelist IP. GET /v5/ins/whitelist/ip.

        Source: https://bybit-exchange.github.io/docs/v5/institution/whitelist-ip
        """
        return self._native_private(
            "get_ins_whitelist_ip",
            [],
        )

    def get_spot_lever_token_info(
        self,
        *,
        lt_coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Leverage Token Info. GET /v5/spot-lever-token/info.

        Source: https://bybit-exchange.github.io/docs/v5/lt/leverage-token-info

        Args:
            lt_coin: Abbreviation of the LT, such as `BTC3L
        """
        return self._native_public(
            "get_spot_lever_token_info",
            self._native_params(
                **{
                    "ltCoin": lt_coin,
                }
            ),
        )

    def request_ins_loan_association_uid(
        self,
        *,
        uid: str,
        operate: str,
    ) -> dict[str, Any]:
        """
        Bind Or Unbind UID. POST /v5/ins-loan/association-uid.

        Source: https://bybit-exchange.github.io/docs/v5/otc/bind-uid

        Args:
            uid: UID Binda) the key used must be from one of UIDs in the risk unit; b) input UID
                must not have an INS loanUnbinda) the key used must be from one of UIDs in the risk
                unit; b) input UID cannot be the same as the UID used to access the API
            operate: 0`: bind, `1`: unbind
        """
        return self._native_private(
            "request_ins_loan_association_uid",
            self._native_params(
                **{
                    "uid": uid,
                    "operate": operate,
                }
            ),
        )

    def get_ins_loan_coin_delta_amount(
        self,
        *,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Coin Delta Amount. GET /v5/ins-loan/coin-delta-amount.

        Source: https://bybit-exchange.github.io/docs/v5/otc/coin-delta-amount

        Args:
            coin: Coin name, uppercase only. e.g. `BTC`. If not passed, returns all coins
        """
        return self._native_private(
            "get_ins_loan_coin_delta_amount",
            self._native_params(
                **{
                    "coin": coin,
                }
            ),
        )

    def get_ins_loan_delay_liq_status(
        self,
    ) -> dict[str, Any]:
        """
        Get Delay Liquidation Status. GET /v5/ins-loan/delay-liq-status.

        Source: https://bybit-exchange.github.io/docs/v5/otc/delay-liq-status
        """
        return self._native_private(
            "get_ins_loan_delay_liq_status",
            [],
        )

    def get_ins_loan_loan_order(
        self,
        *,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Loan Orders. GET /v5/ins-loan/loan-order.

        Source: https://bybit-exchange.github.io/docs/v5/otc/loan-info

        Args:
            order_id: Loan order ID. If not passed, returns all orders sorted by `loanTime` in
                descending order
            start_time: The start timestamp (ms)
            end_time: The end timestamp (ms)
            limit: Limit for data size. [`1`, `100`], Default: `10
        """
        return self._native_private(
            "get_ins_loan_loan_order",
            self._native_params(
                **{
                    "orderId": order_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    def get_ins_loan_ltv_convert(
        self,
    ) -> dict[str, Any]:
        """
        Get LTV. GET /v5/ins-loan/ltv-convert.

        Source: https://bybit-exchange.github.io/docs/v5/otc/ltv-convert
        """
        return self._native_private(
            "get_ins_loan_ltv_convert",
            [],
        )

    def get_ins_loan_ensure_tokens_convert(
        self,
        *,
        product_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Margin Coin Info. GET /v5/ins-loan/ensure-tokens-convert.

        Source: https://bybit-exchange.github.io/docs/v5/otc/margin-coin-convert-info

        Args:
            product_id: Product ID. If not passed, returns all margin products. For spot, it returns
                coins with a `convertRatio` greater than 0.
        """
        return self._native_public(
            "get_ins_loan_ensure_tokens_convert",
            self._native_params(
                **{
                    "productId": product_id,
                }
            ),
        )

    def get_ins_loan_product_infos(
        self,
        *,
        product_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Product Info. GET /v5/ins-loan/product-infos.

        Source: https://bybit-exchange.github.io/docs/v5/otc/margin-product-info

        Args:
            product_id: Product ID. If not passed, returns all products
        """
        return self._native_public(
            "get_ins_loan_product_infos",
            self._native_params(
                **{
                    "productId": product_id,
                }
            ),
        )

    def get_ins_loan_repaid_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Repayment Orders. GET /v5/ins-loan/repaid-history.

        Source: https://bybit-exchange.github.io/docs/v5/otc/repay-info

        Args:
            start_time: The start timestamp (ms)
            end_time: The end timestamp (ms)
            limit: Limit for data size. [`1`, `100`]. Default: `100
        """
        return self._native_private(
            "get_ins_loan_repaid_history",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }
            ),
        )

    def request_ins_loan_repay_loan(
        self,
        *,
        token: str,
        quantity: str,
    ) -> dict[str, Any]:
        """
        Repay. POST /v5/ins-loan/repay-loan.

        Source: https://bybit-exchange.github.io/docs/v5/otc/repay

        Args:
            token: Coin name
            quantity: The qty to be repaid
        """
        return self._native_private(
            "request_ins_loan_repay_loan",
            self._native_params(
                **{
                    "token": token,
                    "quantity": quantity,
                }
            ),
        )

    def cancel_stock_order(
        self,
        *,
        order_no: str,
    ) -> dict[str, Any]:
        """
        Cancel Stock Order. POST /v5/rwa/stocks/order/cancel.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/cancel-order

        Args:
            order_no: System order number
        """
        return self._native_private(
            "cancel_stock_order",
            self._native_params(
                **{
                    "orderNo": order_no,
                }
            ),
        )

    def get_rwa_stocks_convert_detail(
        self,
        *,
        order_no: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Convert Detail. GET /v5/rwa/stocks/convert/detail.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/convert-detail

        Args:
            order_no: Convert order number. Either `orderNo` or `requestId` is **required
            request_id: Idempotency key used at submission. Either `orderNo` or `requestId` is
                **required
        """
        return self._native_private(
            "get_rwa_stocks_convert_detail",
            self._native_params(
                **{
                    "orderNo": order_no,
                    "requestId": request_id,
                }
            ),
        )

    def get_rwa_stocks_convert_list(
        self,
        *,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Convert List. GET /v5/rwa/stocks/convert/list.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/convert-list

        Args:
            symbol: Filter by symbol, e.g. `AAPL-US`. Returns all supported symbols if omitted
        """
        return self._native_private(
            "get_rwa_stocks_convert_list",
            self._native_params(
                **{
                    "symbol": symbol,
                }
            ),
        )

    def submit_rwa_stocks_convert(
        self,
        *,
        convert_type: str,
        symbol: str,
        input_amount: str,
        front_multiplier: str,
        account_type: str | None = None,
        request_id: str,
        contract_addr: str | None = None,
        flow: str,
        burn_scene: str | None = None,
    ) -> dict[str, Any]:
        """
        Submit Convert. POST /v5/rwa/stocks/convert/submit.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/convert-submit

        Args:
            convert_type: Direction. `MINT`, `REDEEM
            symbol: Underlying stock symbol, e.g. `AAPL-US
            input_amount: Input amount. Number of underlying shares when `MINT`; number of Tokens
                when `REDEEM
            front_multiplier: Conversion ratio from the front-end snapshot
            account_type: Only effective when `REDEEM`. `all` (default), `uta`, `fund
            request_id: Idempotency key. Length ≤ 36. Alphanumeric plus `-` `_`. Must be unique
                within 24 hours for the same MM account
            contract_addr: Token receive address when `MINT`; Token provide address when `REDEEM`.
                **Do not send when `flow=DEX` and `burnScene=NDP
            flow: CEX`, `DEX`. `MINT` flows are identical across CEX/DEX (mint to the specified
                address). `REDEEM` (burn) flows differ between CEX and DEX
            burn_scene: Scene for **DEX `REDEEM` (burn)**: `DEP` (through Bybit main site), `NDP`
                (not through Bybit main site)
        """
        return self._native_private(
            "submit_rwa_stocks_convert",
            self._native_params(
                **{
                    "convertType": convert_type,
                    "symbol": symbol,
                    "inputAmount": input_amount,
                    "frontMultiplier": front_multiplier,
                    "accountType": account_type,
                    "requestId": request_id,
                    "contractAddr": contract_addr,
                    "flow": flow,
                    "burnScene": burn_scene,
                }
            ),
        )

    def get_rwa_stocks_market_session(
        self,
        *,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Market Session. GET /v5/rwa/stocks/market/session.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/market-session

        Args:
            symbol: Stock symbol, e.g. `AAPL-US
        """
        return self._native_private(
            "get_rwa_stocks_market_session",
            self._native_params(
                **{
                    "symbol": symbol,
                }
            ),
        )

    def get_rwa_stocks_market_get_multiplier_list(
        self,
        *,
        symbol: str | None = None,
        current: int,
        page_size: int,
    ) -> dict[str, Any]:
        """
        Get Multiplier List. GET /v5/rwa/stocks/market/getMultiplierList.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/multiplier-list

        Args:
            symbol: Stock symbol, e.g. `AAPL-US`. Filter by symbol; returns all symbols if omitted
            current: Current page number
            page_size: Page size. Default `10
        """
        return self._native_private(
            "get_rwa_stocks_market_get_multiplier_list",
            self._native_params(
                **{
                    "symbol": symbol,
                    "current": current,
                    "pageSize": page_size,
                }
            ),
        )

    def get_rwa_stocks_order_detail(
        self,
        *,
        order_no: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Stock Order Detail. GET /v5/rwa/stocks/order/detail.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/order-detail

        Args:
            order_no: System order number. Either `orderNo` or `requestId` is **required
            request_id: Client idempotency key. Either `orderNo` or `requestId` is **required
        """
        return self._native_private(
            "get_rwa_stocks_order_detail",
            self._native_params(
                **{
                    "orderNo": order_no,
                    "requestId": request_id,
                }
            ),
        )

    def place_stock_order(
        self,
        *,
        symbol: str,
        quote_token: str,
        side: str,
        order_type: str,
        qty: str | None = None,
        notional: str | None = None,
        limit_price: str | None = None,
        stop_price: str | None = None,
        time_in_force: str,
        trading_session: str | None = None,
        tokenize: bool | None = None,
        order_time: int,
        request_id: str,
    ) -> dict[str, Any]:
        """
        Place Stock Order. POST /v5/rwa/stocks/order.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/place-order

        Args:
            symbol: Stock symbol, e.g. `TSLA-US`, `AAPL-US
            quote_token: Quote asset. Currently only `USDC` is supported
            side: BUY`, `SELL
            order_type: Order type. `MARKET`, `LIMIT`, `STOP`, `STOP_LIMIT
            qty: Order quantity. **Required** for `SELL`; **required** for `BUY` with
                `type=LIMIT`/`STOP`/`STOP_LIMIT`. Mutually exclusive with `notional
            notional: Notional amount (USDC). Only valid when `side=BUY` and `type=MARKET`. Mutually
                exclusive with `qty
            limit_price: Limit price. **Required** when `type=LIMIT` or `STOP_LIMIT
            stop_price: Trigger price. **Required** when `type=STOP` or `STOP_LIMIT
            time_in_force: Time in force: `DAY` / `GTC` / `IOC`. `SELL` only supports `DAY` / `GTC`;
                `IOC` requires `type=LIMIT` + whole-share `qty` + `tradingSession=RTH
            trading_session: Trading session. `RTH` (default), `24H`. Non-`RTH` sessions accept
                `LIMIT` orders only
            tokenize: Whether to auto tokenize after the order is filled. Default: `false`. Only
                valid for `BUY
            order_time: Client order timestamp in milliseconds
            request_id: Idempotency key. Length ≤ 36. Alphanumeric plus `-` `_`. Must be unique
                within 24 hours for the same MM account
        """
        return self._native_private(
            "place_stock_order",
            self._native_params(
                **{
                    "symbol": symbol,
                    "quoteToken": quote_token,
                    "side": side,
                    "type": order_type,
                    "qty": qty,
                    "notional": notional,
                    "limitPrice": limit_price,
                    "stopPrice": stop_price,
                    "timeInForce": time_in_force,
                    "tradingSession": trading_session,
                    "tokenize": tokenize,
                    "orderTime": order_time,
                    "requestId": request_id,
                }
            ),
        )

    def get_rwa_stocks_positions(
        self,
        *,
        symbol: str | None = None,
        show_zero: bool | None = None,
    ) -> dict[str, Any]:
        """
        Get Stock Positions. GET /v5/rwa/stocks/positions.

        Source: https://bybit-exchange.github.io/docs/v5/stocks/positions

        Args:
            symbol: Stock symbol, e.g. `AAPL-US`. Filter by symbol; returns all positions if omitted
            show_zero: Whether to return zero-quantity positions. Default: `false
        """
        return self._native_private(
            "get_rwa_stocks_positions",
            self._native_params(
                **{
                    "symbol": symbol,
                    "showZero": show_zero,
                }
            ),
        )

    def commit_compliance_appeal(
        self,
        *,
        appeal_id: str,
        decision_type: int | None = None,
        items_data: list[Any],
    ) -> dict[str, Any]:
        """
        Commit Appeal. POST /v5/compliance/appeal/commit.

        Source: https://bybit-exchange.github.io/docs/v5/tm-onchain/appeal-commit

        Args:
            appeal_id: Appeal ID
            decision_type: 0` = normal submit (default); `1` = refuse submit, appeal will be disused
            items_data: Submission content per material, one element per material
        """
        return self._native_private(
            "commit_compliance_appeal",
            self._native_params(
                **{
                    "appealId": appeal_id,
                    "decisionType": decision_type,
                    "itemsData": items_data,
                }
            ),
        )

    def get_compliance_appeal_detail(
        self,
        *,
        appeal_id: str,
    ) -> dict[str, Any]:
        """
        Get Appeal Detail. GET /v5/compliance/appeal/detail.

        Source: https://bybit-exchange.github.io/docs/v5/tm-onchain/appeal-detail

        Args:
            appeal_id: Appeal ID, obtained from the list endpoint or the WebSocket push
        """
        return self._native_private(
            "get_compliance_appeal_detail",
            self._native_params(
                **{
                    "appealId": appeal_id,
                }
            ),
        )

    def get_compliance_appeal_list(
        self,
        *,
        appeal_types: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """
        Get Appeal List. GET /v5/compliance/appeal/list.

        Official spec incomplete; not verified live. appeal_types is passed through because array
        query encoding is unspecified.
        Source: https://bybit-exchange.github.io/docs/v5/tm-onchain/appeal-list

        Args:
            appeal_types: Raw query value. Official example uses TM_Onchain; multi-value encoding is
                not specified.
            page: Page number, starts from `1`, default `1
            page_size: Page size, default `20`, max `100
        """
        return self._native_private(
            "get_compliance_appeal_list",
            self._native_params(
                **{
                    "appealTypes": appeal_types,
                    "page": page,
                    "pageSize": page_size,
                }
            ),
        )

    def get_user_invitation_referrals(
        self,
        *,
        status: str | None = None,
        size: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Friend Referrals. GET /v5/user/invitation/referrals.

        Source: https://bybit-exchange.github.io/docs/v5/user/friend-referral

        Args:
            status: Invitation relationship status, `0`: alive; `1`: invalid. By default, returns
                all status
            size: Data size per page [1, 100]. Return 20 records by default
            cursor: Cursor. Use the `nextCursor` token from the response to retrieve the next page
                of the result set
        """
        return self._native_private(
            "get_user_invitation_referrals",
            self._native_params(
                **{
                    "status": status,
                    "size": size,
                    "cursor": cursor,
                }
            ),
        )

    def get_user_escrow_sub_members(
        self,
        *,
        page_size: str | None = None,
        next_cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Fund Custodial Sub Acct. GET /v5/user/escrow_sub_members.

        Source: https://bybit-exchange.github.io/docs/v5/user/fund-subuid-list

        Args:
            page_size: Data size per page. Return up to 100 records per request
            next_cursor: Cursor. Use the `nextCursor` token from the response to retrieve the next
                page of the result set
        """
        return self._native_private(
            "get_user_escrow_sub_members",
            self._native_params(
                **{
                    "pageSize": page_size,
                    "nextCursor": next_cursor,
                }
            ),
        )

    def get_user_invitation_code(
        self,
    ) -> dict[str, Any]:
        """
        Get Referral Code. GET /v5/user/invitation/code.

        Source: https://bybit-exchange.github.io/docs/v5/user/referral-code
        """
        return self._native_private(
            "get_user_invitation_code",
            [],
        )
