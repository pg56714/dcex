"""Generated binance prediction HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedPredictionHTTP(MarketHTTP, TradeHTTP):
    """Prediction API methods."""

    def prediction_get_market_detail(self, *, market_topic_id: int) -> Any:  # noqa: ANN401
        """
        Get Market Detail.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#get-market-detail
        """
        return self._native_public(
            "prediction_get_market_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"marketTopicId": market_topic_id}).items()
                if value is not None
            ],
        )

    def prediction_list_prediction_categories(self) -> Any:  # noqa: ANN401
        """
        List Prediction Categories.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#list-prediction-categories
        """
        return self._native_public(
            "prediction_list_prediction_categories",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({}).items()
                if value is not None
            ],
        )

    def prediction_list_prediction_markets(
        self,
        *,
        l1_category: str | None = None,
        l2_category: str | None = None,
        sort_by: str | None = None,
        order_by: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        List Prediction Markets.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#list-prediction-markets
        """
        return self._native_public(
            "prediction_list_prediction_markets",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "l1Category": l1_category,
                        "l2Category": l2_category,
                        "sortBy": sort_by,
                        "orderBy": order_by,
                        "offset": offset,
                        "limit": limit,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_market_search(self, *, query: str, top_k: int | None = None) -> Any:  # noqa: ANN401
        """
        Market Search.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#market-search
        """
        return self._native_public(
            "prediction_market_search",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"query": query, "topK": top_k}).items()
                if value is not None
            ],
        )

    def prediction_query_last_trade_price(self, *, market_id: int) -> Any:  # noqa: ANN401
        """
        Query Last Trade Price.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#query-last-trade-price
        """
        return self._native_public(
            "prediction_query_last_trade_price",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"marketId": market_id}).items()
                if value is not None
            ],
        )

    def prediction_query_order_book(self, *, vendor: str, market_id: int, token_id: str) -> Any:  # noqa: ANN401
        """
        Query Order Book.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#query-order-book
        """
        return self._native_public(
            "prediction_query_order_book",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"vendor": vendor, "marketId": market_id, "tokenId": token_id}
                ).items()
                if value is not None
            ],
        )

    def prediction_create_otc_blocktrade(
        self,
        *,
        market_id: str,
        token_id: str,
        side: str,
        maker_amount: str,
        taker_amount: str,
        price_per_share: str,
        expiration: int,
    ) -> Any:  # noqa: ANN401
        """
        Create OTC Blocktrade (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#create-otc-blocktrade
        """
        return self._native_private(
            "prediction_create_otc_blocktrade",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "marketId": market_id,
                        "tokenId": token_id,
                        "side": side,
                        "makerAmount": maker_amount,
                        "takerAmount": taker_amount,
                        "pricePerShare": price_per_share,
                        "expiration": expiration,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_fulfil_otc_blocktrade(self, *, order_id: str, secret_token: str) -> Any:  # noqa: ANN401
        """
        Fulfil OTC Blocktrade (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#fulfil-otc-blocktrade
        """
        return self._native_private(
            "prediction_fulfil_otc_blocktrade",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"orderId": order_id, "secretToken": secret_token}
                ).items()
                if value is not None
            ],
        )

    def prediction_get_otc_blocktrade_detail(self, *, order_id: str) -> Any:  # noqa: ANN401
        """
        Get OTC Blocktrade Detail (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#get-otc-blocktrade-detail
        """
        return self._native_private(
            "prediction_get_otc_blocktrade_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"orderId": order_id}).items()
                if value is not None
            ],
        )

    def prediction_get_otc_blocktrade_events(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        event_types: list[Any] | None = None,
        market_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get OTC Blocktrade Events (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#get-otc-blocktrade-events
        """
        return self._native_private(
            "prediction_get_otc_blocktrade_events",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "first": first,
                        "after": after,
                        "eventTypes": event_types,
                        "marketId": market_id,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_get_otc_reserved_balances(self, *, assets: list[Any]) -> Any:  # noqa: ANN401
        """
        Get OTC Reserved Balances (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#get-otc-reserved-balances
        """
        return self._native_private(
            "prediction_get_otc_reserved_balances",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"assets": assets}).items()
                if value is not None
            ],
        )

    def prediction_list_otc_blocktrades(
        self, *, first: int | None = None, after: str | None = None, status: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        List OTC Blocktrades (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#list-otc-blocktrades
        """
        return self._native_private(
            "prediction_list_otc_blocktrades",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"first": first, "after": after, "status": status}
                ).items()
                if value is not None
            ],
        )

    def prediction_preview_otc_blocktrade(self, *, secret_token: str) -> Any:  # noqa: ANN401
        """
        Preview OTC Blocktrade (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#preview-otc-blocktrade
        """
        return self._native_private(
            "prediction_preview_otc_blocktrade",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"secretToken": secret_token}).items()
                if value is not None
            ],
        )

    def prediction_remove_otc_blocktrades(self, *, order_ids: list[Any]) -> Any:  # noqa: ANN401
        """
        Remove OTC Blocktrades (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#remove-otc-blocktrades
        """
        return self._native_private(
            "prediction_remove_otc_blocktrades",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"orderIds": order_ids}).items()
                if value is not None
            ],
        )

    def prediction_get_position_by_token(
        self, *, wallet_address: str, token_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Position by Token (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#get-position-by-token
        """
        return self._native_private(
            "prediction_get_position_by_token",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "tokenId": token_id,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_query_pn_l(
        self,
        *,
        wallet_address: str,
        token_id: str | None = None,
        market_id: int | None = None,
        market_topic_id: int | None = None,
        active_only: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query PnL (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-pn-l
        """
        return self._native_private(
            "prediction_query_pn_l",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "tokenId": token_id,
                        "marketId": market_id,
                        "marketTopicId": market_topic_id,
                        "activeOnly": active_only,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_query_positions(
        self,
        *,
        wallet_address: str,
        tab: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Positions (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-positions
        """
        return self._native_private(
            "prediction_query_positions",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "tab": tab,
                        "offset": offset,
                        "limit": limit,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_query_positions_by_filter(
        self,
        *,
        wallet_address: str | None = None,
        market_topic_id: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Positions by Filter (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-positions-by-filter
        """
        return self._native_private(
            "prediction_query_positions_by_filter",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "marketTopicId": market_topic_id,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_query_settled_position_history(
        self,
        *,
        wallet_address: str,
        l1_category: str | None = None,
        result: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Settled Position History (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-settled-position-history
        """
        return self._native_private(
            "prediction_query_settled_position_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "l1Category": l1_category,
                        "result": result,
                        "startDate": start_date,
                        "endDate": end_date,
                        "offset": offset,
                        "limit": limit,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_get_redeem_status(
        self, *, wallet_address: str, tx_hash: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Redeem Status (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/redeem#get-redeem-status
        """
        return self._native_private(
            "prediction_get_redeem_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"walletAddress": wallet_address, "txHash": tx_hash, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )

    def prediction_get_quote(
        self,
        *,
        wallet_address: str,
        token_id: str,
        side: str,
        amount_in: str,
        order_type: str,
        slippage_bps: int,
        price_limit: str | None = None,
        chain_id: str | None = None,
        fee_rate_bps: int | None = None,
        funding_source: str | None = None,
        fund_transfer_amount: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Quote (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#get-quote
        """
        return self._native_private(
            "prediction_get_quote",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "tokenId": token_id,
                        "side": side,
                        "amountIn": amount_in,
                        "orderType": order_type,
                        "slippageBps": slippage_bps,
                        "priceLimit": price_limit,
                        "chainId": chain_id,
                        "feeRateBps": fee_rate_bps,
                        "fundingSource": funding_source,
                        "fundTransferAmount": fund_transfer_amount,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_place_order(
        self,
        *,
        wallet_address: str,
        wallet_id: str,
        quote_id: str,
        time_in_force: str,
        account_type: str,
        order_type: str,
        slippage_bps: int,
        price_limit: str | None = None,
        funding_source: str | None = None,
        fund_transfer_amount: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Place Order (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#place-order
        """
        return self._native_private(
            "prediction_place_order",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "walletId": wallet_id,
                        "quoteId": quote_id,
                        "timeInForce": time_in_force,
                        "accountType": account_type,
                        "orderType": order_type,
                        "slippageBps": slippage_bps,
                        "priceLimit": price_limit,
                        "fundingSource": funding_source,
                        "fundTransferAmount": fund_transfer_amount,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_query_active_orders(
        self,
        *,
        wallet_address: str,
        trade_side: str | None = None,
        l1_category: str | None = None,
        market_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Active Orders (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#query-active-orders
        """
        return self._native_private(
            "prediction_query_active_orders",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "tradeSide": trade_side,
                        "l1Category": l1_category,
                        "marketId": market_id,
                        "offset": offset,
                        "limit": limit,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_query_order_history(
        self,
        *,
        wallet_address: str,
        l1_category: str | None = None,
        order_type: str | None = None,
        status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Order History (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#query-order-history
        """
        return self._native_private(
            "prediction_query_order_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "l1Category": l1_category,
                        "orderType": order_type,
                        "status": status,
                        "startDate": start_date,
                        "endDate": end_date,
                        "offset": offset,
                        "limit": limit,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_apply_mm_deposit(
        self,
        *,
        from_token: str,
        from_token_amount: str,
        to_token: str,
        account_type: str,
        chain_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Apply MM Deposit (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#apply-mm-deposit
        """
        return self._native_private(
            "prediction_apply_mm_deposit",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "fromToken": from_token,
                        "fromTokenAmount": from_token_amount,
                        "toToken": to_token,
                        "accountType": account_type,
                        "chainId": chain_id,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_get_portfolio(
        self,
        *,
        wallet_address: str,
        token_id: str | None = None,
        market_id: int | None = None,
        market_topic_id: int | None = None,
        active_only: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Portfolio (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#get-portfolio
        """
        return self._native_private(
            "prediction_get_portfolio",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "tokenId": token_id,
                        "marketId": market_id,
                        "marketTopicId": market_topic_id,
                        "activeOnly": active_only,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_get_quota_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Quota Status (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#get-quota-status
        """
        return self._native_private(
            "prediction_get_quota_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"recvWindow": recv_window}).items()
                if value is not None
            ],
        )

    def prediction_list_prediction_wallets(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        List Prediction Wallets (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#list-prediction-wallets
        """
        return self._native_private(
            "prediction_list_prediction_wallets",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"recvWindow": recv_window}).items()
                if value is not None
            ],
        )

    def prediction_query_payment_option_balances(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Query Payment Option Balances (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#query-payment-option-balances
        """
        return self._native_private(
            "prediction_query_payment_option_balances",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({"recvWindow": recv_window}).items()
                if value is not None
            ],
        )
