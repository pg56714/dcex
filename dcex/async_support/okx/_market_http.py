"""OKX Market async HTTP client backed by Rust."""

from typing import Any

from dcex._schema_codec import normalize_params

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    "Async HTTP client for OKX market data operations."

    async def get_spread_spreads(
        self,
        *,
        base_ccy: str | None = None,
        inst_id: str | None = None,
        sprd_id: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        """List available Nitro Spreads."""
        return await self._native_public(
            "get_spread_spreads",
            self._params(baseCcy=base_ccy, instId=inst_id, sprdId=sprd_id, state=state),
        )

    async def get_spread_books(self, sprd_id: str, *, depth: int | None = None) -> dict[str, Any]:
        """Get a Nitro Spread order book."""
        return await self._native_public("get_spread_books", self._params(sprdId=sprd_id, sz=depth))

    async def get_spread_ticker(self, sprd_id: str) -> dict[str, Any]:
        """Get a Nitro Spread ticker."""
        return await self._native_public("get_spread_ticker", self._params(sprdId=sprd_id))

    async def get_spread_candles(
        self, sprd_id: str, *, bar: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Get recent Nitro Spread candlesticks."""
        return await self._native_public(
            "get_spread_candles", self._params(sprdId=sprd_id, bar=bar, limit=limit)
        )

    async def get_spread_history_candles(
        self, sprd_id: str, *, bar: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Get historical Nitro Spread candlesticks."""
        return await self._native_public(
            "get_spread_history_candles", self._params(sprdId=sprd_id, bar=bar, limit=limit)
        )

    async def get_spread_public_trades(self, sprd_id: str) -> dict[str, Any]:
        """Get public Nitro Spread trades."""
        return await self._native_public("get_spread_public_trades", self._params(sprdId=sprd_id))

    """Async HTTP client for OKX market data operations."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed OKX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("OKX native client is required for market methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        kwargs = normalize_params(kwargs)
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            params.append((key, str(value)))
        return params

    async def get_candles_ticks(
        self,
        product_symbol: str,
        bar: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
        adjust: str | None = None,
    ) -> dict[str, Any]:
        """Get candlestick data."""
        return await self._native_public(
            "get_candles_ticks",
            self._params(
                instId=product_symbol,
                bar=bar,
                after=after,
                before=before,
                limit=limit,
                adjust=adjust,
            ),
        )

    async def get_orderbook(
        self,
        product_symbol: str,
        sz: str | None = None,
    ) -> dict[str, Any]:
        """Get order book data."""
        return await self._native_public(
            "get_orderbook",
            self._params(instId=product_symbol, sz=sz),
        )

    async def get_tickers(
        self,
        instType: str,
        instFamily: str | None = None,
    ) -> dict[str, Any]:
        """Get ticker data."""
        return await self._native_public(
            "get_tickers",
            self._params(instType=instType, instFamily=instFamily),
        )

    async def get_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get public trades data."""
        return await self._native_public(
            "get_public_trades",
            self._params(instId=product_symbol, limit=limit),
        )

    async def get_option_family_trades(self, instFamily: str) -> dict[str, Any]:
        """Get option trades for an instrument family."""
        return await self._native_public(
            "get_option_family_trades", self._params(instFamily=instFamily)
        )

    async def get_price_limit(self, product_symbol: str) -> dict[str, Any]:
        """Get the current highest buy and lowest sell limit prices."""
        return await self._native_public(
            "get_price_limit", self._params(product_symbol=product_symbol)
        )

    async def get_mark_price(
        self,
        instrument_type: str,
        *,
        product_symbol: str | None = None,
        instrument_family: str | None = None,
    ) -> dict[str, Any]:
        """Get mark prices for MARGIN, SWAP, FUTURES, OPTION or EVENTS instruments."""
        return await self._native_public(
            "get_mark_price",
            self._params(
                instType=instrument_type,
                product_symbol=product_symbol,
                instFamily=instrument_family,
            ),
        )

    async def get_server_time(self) -> dict[str, Any]:
        """Get server time through ``GET /api/v5/public/time``."""
        return await self._native_public("get_server_time", self._params())

    async def get_ticker(self, product_symbol: str) -> dict[str, Any]:
        """Get ticker through ``GET /api/v5/market/ticker``."""
        return await self._native_public("get_ticker", self._params(product_symbol=product_symbol))

    async def get_full_orderbook(
        self, product_symbol: str, sz: str | None = None
    ) -> dict[str, Any]:
        """Get full orderbook through ``GET /api/v5/market/books-full``."""
        return await self._native_public(
            "get_full_orderbook", self._params(product_symbol=product_symbol, sz=sz)
        )

    async def get_candles_history(
        self,
        product_symbol: str,
        after: str | None = None,
        before: str | None = None,
        bar: str | None = None,
        limit: str | None = None,
        adjust: str | None = None,
    ) -> dict[str, Any]:
        """Get candles history through ``GET /api/v5/market/history-candles``."""
        return await self._native_public(
            "get_candles_history",
            self._params(
                product_symbol=product_symbol,
                after=after,
                before=before,
                bar=bar,
                limit=limit,
                adjust=adjust,
            ),
        )

    async def get_trades_history(
        self,
        product_symbol: str,
        type_: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get trades history through ``GET /api/v5/market/history-trades``."""
        return await self._native_public(
            "get_trades_history",
            self._params(
                product_symbol=product_symbol, type=type_, after=after, before=before, limit=limit
            ),
        )

    async def get_estimated_delivery_price(self, product_symbol: str) -> dict[str, Any]:
        """Get estimated delivery price through ``GET /api/v5/public/estimated-price``."""
        return await self._native_public(
            "get_estimated_delivery_price", self._params(product_symbol=product_symbol)
        )

    async def get_discount_rates(self, ccy: str | None = None) -> dict[str, Any]:
        """Get discount rates through ``GET /api/v5/public/discount-rate-interest-free-quota``."""
        return await self._native_public("get_discount_rates", self._params(ccy=ccy))

    async def convert_contract_coin(
        self,
        product_symbol: str,
        sz: str,
        type_: str | None = None,
        px: str | None = None,
        unit: str | None = None,
        op_type: str | None = None,
    ) -> dict[str, Any]:
        """Convert contract coin through ``GET /api/v5/public/convert-contract-coin``."""
        return await self._native_public(
            "convert_contract_coin",
            self._params(
                product_symbol=product_symbol, sz=sz, type=type_, px=px, unit=unit, opType=op_type
            ),
        )

    async def get_index_tickers(
        self, quote_ccy: str | None = None, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Get index tickers through ``GET /api/v5/market/index-tickers``."""
        return await self._native_public(
            "get_index_tickers", self._params(quoteCcy=quote_ccy, product_symbol=product_symbol)
        )

    async def get_mark_price_candles(
        self,
        product_symbol: str,
        after: str | None = None,
        before: str | None = None,
        bar: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """Get mark price candles through ``GET /api/v5/market/mark-price-candles``."""
        return await self._native_public(
            "get_mark_price_candles",
            self._params(
                product_symbol=product_symbol, after=after, before=before, bar=bar, limit=limit
            ),
        )

    async def get_system_status(self, state: str | None = None) -> dict[str, Any]:
        """Get system status through ``GET /api/v5/system/status``."""
        return await self._native_public("get_system_status", self._params(state=state))

    async def get_books_rpi(self, *, inst_id: str, sz: str | None = None) -> dict[str, Any]:
        """
        GET /api/v5/market/books-rpi. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-rpi-order-book
        """
        return await self._native_public(
            "get_books_rpi", self._native_params(instId=inst_id, sz=sz)
        )

    async def get_platform_24_volume(self) -> dict[str, Any]:
        """
        GET /api/v5/market/platform-24-volume. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-24h-total-volume
        """
        return await self._native_public("get_platform_24_volume", self._native_params())

    async def get_call_auction_details(self, *, inst_id: str) -> dict[str, Any]:
        """

        GET /api/v5/market/call-auction-details. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-call-auction-details

        """
        return await self._native_public(
            "get_call_auction_details", self._native_params(instId=inst_id)
        )

    async def get_block_tickers(
        self, *, inst_type: str, inst_family: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/market/block-tickers. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-block-tickers
        """
        return await self._native_public(
            "get_block_tickers", self._native_params(instType=inst_type, instFamily=inst_family)
        )

    async def get_block_ticker(self, *, inst_id: str) -> dict[str, Any]:
        """
        GET /api/v5/market/block-ticker. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-block-ticker
        """
        return await self._native_public("get_block_ticker", self._native_params(instId=inst_id))

    async def get_rfq_public_trades(
        self, *, begin_id: str | None = None, end_id: str | None = None, limit: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v5/rfq/public-trades. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-public-multi-leg-transactions-of-block-trades

        """
        return await self._native_public(
            "get_rfq_public_trades",
            self._native_params(beginId=begin_id, endId=end_id, limit=limit),
        )

    async def get_block_trades(self, *, inst_id: str) -> dict[str, Any]:
        """

        GET /api/v5/public/block-trades. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-public-single-leg-transactions-of-block-trades

        """
        return await self._native_public("get_block_trades", self._native_params(instId=inst_id))

    async def get_estimated_settlement_info(self, *, inst_id: str) -> dict[str, Any]:
        """

        GET /api/v5/public/estimated-settlement-info. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-estimated-future-settlement-price

        """
        return await self._native_public(
            "get_estimated_settlement_info", self._native_params(instId=inst_id)
        )

    async def get_settlement_history(
        self,
        *,
        inst_family: str,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/settlement-history. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-futures-settlement-history
        """
        return await self._native_public(
            "get_settlement_history",
            self._native_params(instFamily=inst_family, after=after, before=before, limit=limit),
        )

    async def get_insurance_fund(
        self,
        *,
        inst_type: str,
        type_: str | None = None,
        inst_family: str | None = None,
        ccy: str | None = None,
        before: str | None = None,
        after: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/insurance-fund. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-security-fund
        """
        return await self._native_public(
            "get_insurance_fund",
            self._native_params(
                instType=inst_type,
                type=type_,
                instFamily=inst_family,
                ccy=ccy,
                before=before,
                after=after,
                limit=limit,
            ),
        )

    async def get_premium_history(
        self,
        *,
        inst_id: str,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/premium-history. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-premium-history
        """
        return await self._native_public(
            "get_premium_history",
            self._native_params(instId=inst_id, after=after, before=before, limit=limit),
        )

    async def get_index_candles(
        self,
        *,
        inst_id: str,
        after: str | None = None,
        before: str | None = None,
        bar: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/market/index-candles. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-candlesticks
        """
        return await self._native_public(
            "get_index_candles",
            self._native_params(instId=inst_id, after=after, before=before, bar=bar, limit=limit),
        )

    async def get_history_index_candles(
        self,
        *,
        inst_id: str,
        after: str | None = None,
        before: str | None = None,
        bar: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/market/history-index-candles. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-candlesticks-history
        """
        return await self._native_public(
            "get_history_index_candles",
            self._native_params(instId=inst_id, after=after, before=before, bar=bar, limit=limit),
        )

    async def get_history_mark_price_candles(
        self,
        *,
        inst_id: str,
        after: str | None = None,
        before: str | None = None,
        bar: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v5/market/history-mark-price-candles. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price-candlesticks-history

        """
        return await self._native_public(
            "get_history_mark_price_candles",
            self._native_params(instId=inst_id, after=after, before=before, bar=bar, limit=limit),
        )

    async def get_exchange_rate(self) -> dict[str, Any]:
        """
        GET /api/v5/market/exchange-rate. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-exchange-rate
        """
        return await self._native_public("get_exchange_rate", self._native_params())

    async def get_index_components(self, *, index: str) -> dict[str, Any]:
        """
        GET /api/v5/market/index-components. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-components
        """
        return await self._native_public("get_index_components", self._native_params(index=index))

    async def get_market_data_history(
        self,
        *,
        module: str,
        inst_type: str,
        date_aggr_type: str,
        begin: str,
        end: str,
        inst_id_list: str | None = None,
        inst_family_list: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/market-data-history. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-historical-market-data
        """
        return await self._native_public(
            "get_market_data_history",
            self._native_params(
                module=module,
                instType=inst_type,
                instIdList=inst_id_list,
                instFamilyList=inst_family_list,
                dateAggrType=date_aggr_type,
                begin=begin,
                end=end,
            ),
        )

    async def get_delta_hedge_currencies(self, *, ccy: str | None = None) -> dict[str, Any]:
        """
        GET /api/v5/public/delta-hedge-currencies. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-delta-hedge-currencies
        """
        return await self._native_public("get_delta_hedge_currencies", self._native_params(ccy=ccy))

    async def get_loan_ratio(
        self,
        *,
        ccy: str,
        begin: str | None = None,
        end: str | None = None,
        period: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v5/rubik/stat/margin/loan-ratio. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-margin-long-short-ratio

        """
        return await self._native_public(
            "get_loan_ratio", self._native_params(ccy=ccy, begin=begin, end=end, period=period)
        )

    async def get_announcements(
        self, *, ann_type: str | None = None, page: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/support/announcements. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#announcement-get-announcements
        """
        return await self._native_public(
            "get_announcements", self._native_params(annType=ann_type, page=page)
        )

    async def get_announcement_types(self) -> dict[str, Any]:
        """
        GET /api/v5/support/announcement-types. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#announcement-get-announcement-types
        """
        return await self._native_public("get_announcement_types", self._native_params())

    async def get_sbe_orderbook(self, inst_id_code: int) -> bytes:
        """Fetch raw SBE snapshot bytes; decode with OKX's versioned SBE XML schema."""
        if self._native_client is None:
            raise RuntimeError("OKX native client is required.")
        return await self._native_client.get_sbe_orderbook_async(inst_id_code)

    async def get_trading_bot_grid_ai_param(
        self,
        *,
        algo_ord_type: str,
        inst_id: str,
        direction: str | None = None,
        duration: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/ai-param. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-ai-parameter-public
        """
        return await self._native_public(
            "get_trading_bot_grid_ai_param",
            self._native_params(
                algoOrdType=algo_ord_type, instId=inst_id, direction=direction, duration=duration
            ),
        )

    async def trading_bot_grid_min_investment(
        self,
        *,
        inst_id: str,
        algo_ord_type: str,
        max_px: str,
        min_px: str,
        grid_num: str,
        run_type: str,
        direction: str | None = None,
        lever: str | None = None,
        base_pos: bool | None = None,
        investment_type: str | None = None,
        trigger_strategy: str | None = None,
        top_up_amt: str | None = None,
        investment_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/min-investment. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-compute-min-investment-public
        """
        return await self._native_public(
            "trading_bot_grid_min_investment",
            self._native_params(
                instId=inst_id,
                algoOrdType=algo_ord_type,
                maxPx=max_px,
                minPx=min_px,
                gridNum=grid_num,
                runType=run_type,
                direction=direction,
                lever=lever,
                basePos=base_pos,
                investmentType=investment_type,
                triggerStrategy=trigger_strategy,
                topUpAmt=top_up_amt,
                investmentData=investment_data,
            ),
        )

    async def get_trading_bot_public_rsi_back_testing(
        self,
        *,
        inst_id: str,
        timeframe: str,
        thold: str,
        time_period: str,
        trigger_cond: str | None = None,
        duration: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/public/rsi-back-testing. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-rsi-back-testing-public
        """
        return await self._native_public(
            "get_trading_bot_public_rsi_back_testing",
            self._native_params(
                instId=inst_id,
                timeframe=timeframe,
                thold=thold,
                timePeriod=time_period,
                triggerCond=trigger_cond,
                duration=duration,
            ),
        )

    async def get_trading_bot_grid_grid_quantity(
        self,
        *,
        inst_id: str,
        run_type: str,
        algo_ord_type: str,
        max_px: str,
        min_px: str,
        lever: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/grid-quantity. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-max-grid-quantity-public
        """
        return await self._native_public(
            "get_trading_bot_grid_grid_quantity",
            self._native_params(
                instId=inst_id,
                runType=run_type,
                algoOrdType=algo_ord_type,
                maxPx=max_px,
                minPx=min_px,
                lever=lever,
            ),
        )

    async def get_copytrading_public_config(
        self, *, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-config. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-copy-trading-configuration
        """
        return await self._native_public(
            "get_copytrading_public_config", self._native_params(instType=inst_type)
        )

    async def get_copytrading_public_lead_traders(
        self,
        *,
        inst_type: str | None = None,
        sort_type: str | None = None,
        state: str | None = None,
        min_lead_days: str | None = None,
        min_assets: str | None = None,
        max_assets: str | None = None,
        min_aum: str | None = None,
        max_aum: str | None = None,
        data_ver: str | None = None,
        page: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-lead-traders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-ranks
        """
        return await self._native_public(
            "get_copytrading_public_lead_traders",
            self._native_params(
                instType=inst_type,
                sortType=sort_type,
                state=state,
                minLeadDays=min_lead_days,
                minAssets=min_assets,
                maxAssets=max_assets,
                minAum=min_aum,
                maxAum=max_aum,
                dataVer=data_ver,
                page=page,
                limit=limit,
            ),
        )

    async def get_copytrading_public_weekly_pnl(
        self, *, unique_code: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-weekly-pnl. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-weekly-pnl
        """
        return await self._native_public(
            "get_copytrading_public_weekly_pnl",
            self._native_params(instType=inst_type, uniqueCode=unique_code),
        )

    async def get_copytrading_public_pnl(
        self, *, unique_code: str, last_days: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-pnl. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-daily-pnl
        """
        return await self._native_public(
            "get_copytrading_public_pnl",
            self._native_params(instType=inst_type, uniqueCode=unique_code, lastDays=last_days),
        )

    async def get_copytrading_public_stats(
        self, *, unique_code: str, last_days: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-stats. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-stats
        """
        return await self._native_public(
            "get_copytrading_public_stats",
            self._native_params(instType=inst_type, uniqueCode=unique_code, lastDays=last_days),
        )

    async def get_copytrading_public_preference_currency(
        self, *, unique_code: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-preference-currency.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-currency-preferences
        """
        return await self._native_public(
            "get_copytrading_public_preference_currency",
            self._native_params(instType=inst_type, uniqueCode=unique_code),
        )

    async def get_copytrading_public_current_subpositions(
        self,
        *,
        unique_code: str,
        inst_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-current-subpositions.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-current-lead-positions
        """
        return await self._native_public(
            "get_copytrading_public_current_subpositions",
            self._native_params(
                instType=inst_type, uniqueCode=unique_code, after=after, before=before, limit=limit
            ),
        )

    async def get_copytrading_public_subpositions_history(
        self,
        *,
        unique_code: str,
        inst_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-subpositions-history.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-trader-lead-position-history
        """
        return await self._native_public(
            "get_copytrading_public_subpositions_history",
            self._native_params(
                instType=inst_type, uniqueCode=unique_code, after=after, before=before, limit=limit
            ),
        )

    async def get_copytrading_public_copy_traders(
        self, *, unique_code: str, inst_type: str | None = None, limit: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/public-copy-traders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-copy-traders
        """
        return await self._native_public(
            "get_copytrading_public_copy_traders",
            self._native_params(instType=inst_type, uniqueCode=unique_code, limit=limit),
        )

    async def get_public_event_contract_series(
        self, *, series_id: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/event-contract/series. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-series
        """
        return await self._native_public(
            "get_public_event_contract_series", self._native_params(seriesId=series_id)
        )

    async def get_public_event_contract_events(
        self,
        *,
        series_id: str,
        event_id: str | None = None,
        state: str | None = None,
        limit: str | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/event-contract/events. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-events
        """
        return await self._native_public(
            "get_public_event_contract_events",
            self._native_params(
                seriesId=series_id,
                eventId=event_id,
                state=state,
                limit=limit,
                before=before,
                after=after,
            ),
        )

    async def get_public_event_contract_markets(
        self,
        *,
        series_id: str,
        event_id: str | None = None,
        inst_id: str | None = None,
        state: str | None = None,
        limit: str | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/public/event-contract/markets. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-markets
        """
        return await self._native_public(
            "get_public_event_contract_markets",
            self._native_params(
                seriesId=series_id,
                eventId=event_id,
                instId=inst_id,
                state=state,
                limit=limit,
                before=before,
                after=after,
            ),
        )

    async def get_public_interest_rate_loan_quota(self) -> dict[str, Any]:
        """
        GET /api/v5/public/interest-rate-loan-quota. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#public-data-rest-api-get-interest-rate-and-loan-quota
        """
        return await self._native_public(
            "get_public_interest_rate_loan_quota", self._native_params()
        )
