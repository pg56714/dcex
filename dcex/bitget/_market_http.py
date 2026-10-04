"""Bitget public market-data HTTP client backed by Rust."""

from typing import Any

from dcex._schema_codec import normalize_params

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for Bitget public market-data APIs."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Bitget public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bitget native client is required for public market methods.")
        response, data = request_native_json(
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

    def get_spot_coins(self, coin: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot coin metadata."""
        return self._native_public("get_spot_coins", self._native_params(coin=coin))

    def get_spot_market_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        id_less_than: str | None = None,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot market trades."""
        return self._native_public(
            "get_spot_market_trades",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    def get_uta_instruments(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA instrument metadata, including Reality flags."""
        return self._native_public(
            "get_uta_instruments",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
            ),
        )

    def get_uta_tickers(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA tickers."""
        return self._native_public(
            "get_uta_tickers",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
            ),
        )

    def get_uta_orderbook(
        self,
        category: str,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA orderbook depth."""
        return self._native_public(
            "get_uta_orderbook",
            self._native_params(category=category, product_symbol=product_symbol, limit=limit),
        )

    def get_uta_public_fills(
        self,
        category: str,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve recent public Bitget UTA fills."""
        return self._native_public(
            "get_uta_public_fills",
            self._native_params(category=category, product_symbol=product_symbol, limit=limit),
        )

    def get_uta_kline(
        self,
        category: str,
        product_symbol: str,
        interval: str,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        type_: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA candles."""
        return self._native_public(
            "get_uta_kline",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                type=type_,
                limit=limit,
            ),
        )

    def get_uta_history_kline(
        self,
        category: str,
        product_symbol: str,
        interval: str,
        start_time: int | str | None = None,
        end_time: int | str | None = None,
        type_: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve historical Bitget UTA candles."""
        return self._native_public(
            "get_uta_history_kline",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                type=type_,
                limit=limit,
            ),
        )

    def get_reality_stock_info(
        self,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget Reality underlying-stock and trading-session metadata."""
        return self._native_public(
            "get_reality_stock_info",
            self._native_params(product_symbol=product_symbol, symbol=symbol),
        )

    def get_reality_market_states(self) -> dict[str, Any]:
        """Retrieve Bitget Reality US-market session hours."""
        return self._native_public("get_reality_market_states", [])

    def get_reality_market_calendar(self) -> dict[str, Any]:
        """Retrieve Bitget Reality US-market closure calendar."""
        return self._native_public("get_reality_market_calendar", [])

    def get_uta_liquidations(
        self,
        category: str,
        product_symbol: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA historical liquidation records."""
        return self._native_public(
            "get_uta_liquidations",
            self._native_params(
                product_symbol=product_symbol,
                category=category,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_futures_symbol_price(self, product_symbol: str, product_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/symbol-price``."""
        return self._native_public(
            "get_futures_symbol_price",
            self._native_params(product_symbol=product_symbol, productType=product_type),
        )

    def get_uta_open_interest(
        self, category: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/open-interest``."""
        return self._native_public(
            "get_uta_open_interest",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    def get_uta_current_funding_rate(
        self, *, category: str | None = None, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/current-fund-rate``."""
        return self._native_public(
            "get_uta_current_funding_rate",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    def get_futures_trade_history(
        self,
        product_symbol: str,
        product_type: str,
        *,
        limit: int | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/fills-history``."""
        return self._native_public(
            "get_futures_trade_history",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                limit=limit,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    def get_futures_index_candle_history(
        self,
        product_symbol: str,
        product_type: str,
        granularity: str,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/history-index-candles``."""
        return self._native_public(
            "get_futures_index_candle_history",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                granularity=granularity,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_futures_mark_candle_history(
        self,
        product_symbol: str,
        product_type: str,
        granularity: str,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/history-mark-candles``."""
        return self._native_public(
            "get_futures_mark_candle_history",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                granularity=granularity,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    def get_futures_next_funding_time(
        self, product_symbol: str, product_type: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/funding-time``."""
        return self._native_public(
            "get_futures_next_funding_time",
            self._native_params(product_symbol=product_symbol, productType=product_type),
        )

    def get_futures_interest_exchange_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/exchange-rate``."""
        return self._native_public("get_futures_interest_exchange_rates", self._native_params())

    def get_futures_interest_rate_history(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/union-interest-rate-history``."""
        return self._native_public(
            "get_futures_interest_rate_history", self._native_params(coin=coin)
        )

    def get_futures_vip_fee_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/vip-fee-rate``."""
        return self._native_public("get_futures_vip_fee_rates", self._native_params())

    def get_uta_funding_rate_history(
        self,
        category: str,
        product_symbol: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/history-fund-rate``."""
        return self._native_public(
            "get_uta_funding_rate_history",
            self._native_params(
                category=category, product_symbol=product_symbol, cursor=cursor, limit=limit
            ),
        )

    def get_uta_index_components(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/index-components``."""
        return self._native_public(
            "get_uta_index_components", self._native_params(product_symbol=product_symbol)
        )

    def get_uta_margin_loan_rates(self, coin: str, *, level: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-loans``."""
        return self._native_public(
            "get_uta_margin_loan_rates", self._native_params(coin=coin, level=level)
        )

    def get_uta_position_tiers(
        self, category: str, *, product_symbol: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/position-tier``."""
        return self._native_public(
            "get_uta_position_tiers",
            self._native_params(category=category, product_symbol=product_symbol, coin=coin),
        )

    def get_uta_open_interest_limit(
        self, category: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/oi-limit``."""
        return self._native_public(
            "get_uta_open_interest_limit",
            self._native_params(product_symbol=product_symbol, category=category),
        )

    def get_uta_discount_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/discount-rate``."""
        return self._native_public("get_uta_discount_rates", self._native_params())

    def get_uta_rpi_orderbook(
        self, category: str, product_symbol: str, *, limit: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/rpi-orderbook``."""
        return self._native_public(
            "get_uta_rpi_orderbook",
            self._native_params(category=category, product_symbol=product_symbol, limit=limit),
        )

    def get_uta_rpi_symbols(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/rpi-symbols``."""
        return self._native_public("get_uta_rpi_symbols", self._native_params())

    def get_server_time(self) -> dict[str, Any]:
        """Call ``GET /api/v2/public/time``."""
        return self._native_public("get_server_time", self._native_params())

    def get_uta_cash_dividend_records(
        self,
        product_symbol: str,
        type_: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/cash-dividend-records``."""
        return self._native_public(
            "get_uta_cash_dividend_records",
            self._native_params(
                product_symbol=product_symbol, type=type_, cursor=cursor, limit=limit
            ),
        )

    def get_uta_risk_reserve(
        self, category: str, product_symbol: str, *, margin_coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/risk-reserve``."""
        return self._native_public(
            "get_uta_risk_reserve",
            self._native_params(
                category=category, product_symbol=product_symbol, marginCoin=margin_coin
            ),
        )

    def get_uta_all_risk_reserves(self, category: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/risk-reserve-all``."""
        return self._native_public(
            "get_uta_all_risk_reserves", self._native_params(category=category)
        )

    def get_uta_hourly_risk_reserve(
        self, category: str, product_symbol: str, *, margin_coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/risk-reserve-hour``."""
        return self._native_public(
            "get_uta_hourly_risk_reserve",
            self._native_params(
                category=category, product_symbol=product_symbol, marginCoin=margin_coin
            ),
        )

    def get_uta_split_records(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/split-records``."""
        return self._native_public("get_uta_split_records", self._native_params())

    def get_uta_futures_long_short_ratio(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-account-long-short``."""
        return self._native_public(
            "get_uta_futures_long_short_ratio",
            self._native_params(product_symbol=product_symbol, period=period),
        )

    def get_uta_spot_whale_flow(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/spot-whale-flow``."""
        return self._native_public(
            "get_uta_spot_whale_flow", self._native_params(product_symbol=product_symbol)
        )

    def get_classic_margin_currencies(self) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/currencies``."""
        return self._native_public("get_classic_margin_currencies", self._native_params())

    def get_classic_auction(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/market/auction``."""
        return self._native_public(
            "get_classic_auction", self._native_params(product_symbol=product_symbol)
        )

    def get_classic_vip_fee_rate(self) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/market/vip-fee-rate``."""
        return self._native_public("get_classic_vip_fee_rate", self._native_params())

    def get_uta_proof_of_reserves(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/proof-of-reserves``."""
        return self._native_public("get_uta_proof_of_reserves", self._native_params())

    def get_uta_score_weights(self, *, category: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/market/score-weights``."""
        return self._native_public("get_uta_score_weights", self._native_params(category=category))

    def get_uta_fee_group(self, category: str, *, group: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/market/fee-group``."""
        return self._native_public(
            "get_uta_fee_group", self._native_params(category=category, group=group)
        )

    def get_uta_spot_fund_flow(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/spot-fund-flow``."""
        return self._native_public(
            "get_uta_spot_fund_flow",
            self._native_params(product_symbol=product_symbol, period=period),
        )

    def get_uta_spot_net_flow(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/spot-net-flow``."""
        return self._native_public(
            "get_uta_spot_net_flow", self._native_params(product_symbol=product_symbol)
        )

    def get_uta_margin_long_short(
        self, product_symbol: str, *, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-long-short``."""
        return self._native_public(
            "get_uta_margin_long_short",
            self._native_params(product_symbol=product_symbol, period=period, coin=coin),
        )

    def get_uta_margin_loan_growth(
        self, product_symbol: str, *, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-loan-growth``."""
        return self._native_public(
            "get_uta_margin_loan_growth",
            self._native_params(product_symbol=product_symbol, period=period, coin=coin),
        )

    def get_uta_margin_isolated_borrow(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-isolated-borrow``."""
        return self._native_public(
            "get_uta_margin_isolated_borrow",
            self._native_params(product_symbol=product_symbol, period=period),
        )

    def get_uta_futures_active_buy_sell(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-active-buy-sell``."""
        return self._native_public(
            "get_uta_futures_active_buy_sell",
            self._native_params(product_symbol=product_symbol, period=period),
        )

    def get_uta_futures_long_short(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-long-short``."""
        return self._native_public(
            "get_uta_futures_long_short",
            self._native_params(product_symbol=product_symbol, period=period),
        )

    def get_uta_futures_position_long_short(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-position-long-short``."""
        return self._native_public(
            "get_uta_futures_position_long_short",
            self._native_params(product_symbol=product_symbol, period=period),
        )

    def get_classic_earn_loan_public_coin_infos(self, *, coin: str | None = None) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/public/coinInfos. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-currency-list
        """
        return self._native_public(
            "get_classic_earn_loan_public_coin_infos", self._native_params(coin=coin)
        )

    def get_classic_earn_loan_public_hour_interest(
        self, *, loan_coin: str, pledge_coin: str, daily: str, pledge_amount: str
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/public/hour-interest. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-est-interest-and-borrowable
        """
        return self._native_public(
            "get_classic_earn_loan_public_hour_interest",
            self._native_params(
                loanCoin=loan_coin, pledgeCoin=pledge_coin, daily=daily, pledgeAmount=pledge_amount
            ),
        )

    def get_reality_company_overview(self, *, code: str) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/company-overview. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-company-overview
        """
        return self._native_public("get_reality_company_overview", self._native_params(code=code))

    def get_reality_valuation_indicators(self, *, code: str) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/valuation-indicators. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-valuation-indicators
        """
        return self._native_public(
            "get_reality_valuation_indicators", self._native_params(code=code)
        )

    def get_reality_earnings_forecast(self, *, code: str) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/earnings-forecast. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-earnings-forecast
        """
        return self._native_public("get_reality_earnings_forecast", self._native_params(code=code))

    def get_reality_suspension_resumption_info(self, *, code: str) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/suspension-resumption-info. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-suspension-resumption-info
        """
        return self._native_public(
            "get_reality_suspension_resumption_info", self._native_params(code=code)
        )

    def get_reality_dividends(
        self, *, code: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/dividends. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-dividends
        """
        return self._native_public(
            "get_reality_dividends", self._native_params(code=code, limit=limit, cursor=cursor)
        )

    def get_reality_share_capital_change(self, *, code: str) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/share-capital-change. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-share-capital-change
        """
        return self._native_public(
            "get_reality_share_capital_change", self._native_params(code=code)
        )

    def get_reality_inner_trades(
        self, *, code: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/inner-trades. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-inner-trades
        """
        return self._native_public(
            "get_reality_inner_trades", self._native_params(code=code, limit=limit, cursor=cursor)
        )

    def get_reality_executive_shareholdings(
        self, *, code: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/executive-shareholdings. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-executive-shareholdings
        """
        return self._native_public(
            "get_reality_executive_shareholdings",
            self._native_params(code=code, limit=limit, cursor=cursor),
        )

    def get_reality_sharehold_detail(
        self, *, code: str, limit: str | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v3/reality/market/sharehold-detail. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/reality/basic-info#get-sharehold-detail
        """
        return self._native_public(
            "get_reality_sharehold_detail",
            self._native_params(code=code, limit=limit, cursor=cursor),
        )
