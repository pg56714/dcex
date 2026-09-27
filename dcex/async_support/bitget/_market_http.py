"""Bitget public market-data async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for Bitget public market-data APIs."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Bitget public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bitget native client is required for public market methods.")
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
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            params.append((key, str(value)))
        return params

    async def get_spot_coins(self, coin: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot coin metadata."""
        return await self._native_public("get_spot_coins", self._params(coin=coin))

    async def get_spot_symbols(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot symbol metadata."""
        return await self._native_public(
            "get_spot_symbols",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
            ),
        )

    async def get_spot_tickers(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot ticker data."""
        return await self._native_public(
            "get_spot_tickers",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
            ),
        )

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        type_: str = "step0",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot orderbook depth."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(
                product_symbol=product_symbol,
                type=type_,
                limit=limit,
            ),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        granularity: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot candles."""
        return await self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=product_symbol,
                granularity=granularity,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_history_kline(
        self,
        product_symbol: str,
        granularity: str,
        endTime: int | str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot candles."""
        return await self._native_public(
            "get_spot_history_kline",
            self._params(
                product_symbol=product_symbol,
                granularity=granularity,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget recent spot trades."""
        return await self._native_public(
            "get_spot_recent_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    async def get_spot_market_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot market trades."""
        return await self._native_public(
            "get_spot_market_trades",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_futures_contracts(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures contract metadata."""
        return await self._native_public(
            "get_futures_contracts",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
                productType=productType,
            ),
        )

    async def get_futures_ticker(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures ticker for one symbol."""
        return await self._native_public(
            "get_futures_ticker",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
            ),
        )

    async def get_futures_tickers(self, productType: str = "USDT-FUTURES") -> dict[str, Any]:
        """Retrieve Bitget futures tickers."""
        return await self._native_public(
            "get_futures_tickers",
            self._params(productType=productType),
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        precision: str = "scale0",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures orderbook depth."""
        return await self._native_public(
            "get_futures_orderbook",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                precision=precision,
                limit=limit,
            ),
        )

    async def get_futures_kline(
        self,
        product_symbol: str,
        granularity: str,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        kLineType: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures candles."""
        return await self._native_public(
            "get_futures_kline",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                granularity=granularity,
                startTime=startTime,
                endTime=endTime,
                kLineType=kLineType,
                limit=limit,
            ),
        )

    async def get_futures_history_kline(
        self,
        product_symbol: str,
        granularity: str,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical futures candles."""
        return await self._native_public(
            "get_futures_history_kline",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                granularity=granularity,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_recent_trades(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget recent futures trades."""
        return await self._native_public(
            "get_futures_recent_trades",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                limit=limit,
            ),
        )

    async def get_futures_current_funding_rate(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget current futures funding rate."""
        return await self._native_public(
            "get_futures_current_funding_rate",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
                productType=productType,
            ),
        )

    async def get_futures_history_funding_rate(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        pageSize: int | None = None,
        pageNo: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical futures funding rates."""
        return await self._native_public(
            "get_futures_history_funding_rate",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                pageSize=pageSize,
                pageNo=pageNo,
            ),
        )

    async def get_futures_open_interest(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures open interest."""
        return await self._native_public(
            "get_futures_open_interest",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
            ),
        )

    async def get_uta_instruments(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA instrument metadata, including Reality flags."""
        return await self._native_public(
            "get_uta_instruments",
            self._params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
            ),
        )

    async def get_uta_tickers(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA tickers."""
        return await self._native_public(
            "get_uta_tickers",
            self._params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
            ),
        )

    async def get_uta_orderbook(
        self,
        category: str,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA orderbook depth."""
        return await self._native_public(
            "get_uta_orderbook",
            self._params(category=category, product_symbol=product_symbol, limit=limit),
        )

    async def get_uta_public_fills(
        self,
        category: str,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve recent public Bitget UTA fills."""
        return await self._native_public(
            "get_uta_public_fills",
            self._params(category=category, product_symbol=product_symbol, limit=limit),
        )

    async def get_uta_kline(
        self,
        category: str,
        product_symbol: str,
        interval: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        type_: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA candles."""
        return await self._native_public(
            "get_uta_kline",
            self._params(
                category=category,
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                type=type_,
                limit=limit,
            ),
        )

    async def get_uta_history_kline(
        self,
        category: str,
        product_symbol: str,
        interval: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        type_: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve historical Bitget UTA candles."""
        return await self._native_public(
            "get_uta_history_kline",
            self._params(
                category=category,
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                type=type_,
                limit=limit,
            ),
        )

    async def get_reality_stock_info(
        self,
        product_symbol: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget Reality underlying-stock and trading-session metadata."""
        return await self._native_public(
            "get_reality_stock_info",
            self._params(product_symbol=product_symbol, symbol=symbol),
        )

    async def get_reality_market_states(self) -> dict[str, Any]:
        """Retrieve Bitget Reality US-market session hours."""
        return await self._native_public("get_reality_market_states", [])

    async def get_reality_market_calendar(self) -> dict[str, Any]:
        """Retrieve Bitget Reality US-market closure calendar."""
        return await self._native_public("get_reality_market_calendar", [])

    async def get_uta_liquidations(
        self,
        category: str,
        product_symbol: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA historical liquidation records."""
        return await self._native_public(
            "get_uta_liquidations",
            self._params(
                product_symbol=product_symbol,
                category=category,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_futures_symbol_price(
        self, product_symbol: str, product_type: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/symbol-price``."""
        return await self._native_public(
            "get_futures_symbol_price",
            self._params(product_symbol=product_symbol, productType=product_type),
        )

    async def get_uta_open_interest(
        self, category: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/open-interest``."""
        return await self._native_public(
            "get_uta_open_interest", self._params(category=category, product_symbol=product_symbol)
        )

    async def get_uta_current_funding_rate(
        self, *, category: str | None = None, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/current-fund-rate``."""
        return await self._native_public(
            "get_uta_current_funding_rate",
            self._params(category=category, product_symbol=product_symbol),
        )

    async def get_futures_trade_history(
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
        return await self._native_public(
            "get_futures_trade_history",
            self._params(
                product_symbol=product_symbol,
                productType=product_type,
                limit=limit,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    async def get_futures_index_candle_history(
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
        return await self._native_public(
            "get_futures_index_candle_history",
            self._params(
                product_symbol=product_symbol,
                productType=product_type,
                granularity=granularity,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_mark_candle_history(
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
        return await self._native_public(
            "get_futures_mark_candle_history",
            self._params(
                product_symbol=product_symbol,
                productType=product_type,
                granularity=granularity,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_next_funding_time(
        self, product_symbol: str, product_type: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/funding-time``."""
        return await self._native_public(
            "get_futures_next_funding_time",
            self._params(product_symbol=product_symbol, productType=product_type),
        )

    async def get_futures_open_interest_limit(
        self, product_type: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/oi-limit``."""
        return await self._native_public(
            "get_futures_open_interest_limit",
            self._params(productType=product_type, product_symbol=product_symbol),
        )

    async def get_futures_position_tiers(
        self, product_type: str, product_symbol: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/query-position-lever``."""
        return await self._native_public(
            "get_futures_position_tiers",
            self._params(productType=product_type, product_symbol=product_symbol),
        )

    async def get_futures_discount_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/discount-rate``."""
        return await self._native_public("get_futures_discount_rates", self._params())

    async def get_futures_interest_exchange_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/exchange-rate``."""
        return await self._native_public("get_futures_interest_exchange_rates", self._params())

    async def get_futures_interest_rate_history(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/union-interest-rate-history``."""
        return await self._native_public(
            "get_futures_interest_rate_history", self._params(coin=coin)
        )

    async def get_futures_vip_fee_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/market/vip-fee-rate``."""
        return await self._native_public("get_futures_vip_fee_rates", self._params())

    async def get_uta_funding_rate_history(
        self,
        category: str,
        product_symbol: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/history-fund-rate``."""
        return await self._native_public(
            "get_uta_funding_rate_history",
            self._params(
                category=category, product_symbol=product_symbol, cursor=cursor, limit=limit
            ),
        )

    async def get_uta_index_components(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/index-components``."""
        return await self._native_public(
            "get_uta_index_components", self._params(product_symbol=product_symbol)
        )

    async def get_uta_margin_loan_rates(
        self, coin: str, *, level: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-loans``."""
        return await self._native_public(
            "get_uta_margin_loan_rates", self._params(coin=coin, level=level)
        )

    async def get_uta_position_tiers(
        self, category: str, *, product_symbol: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/position-tier``."""
        return await self._native_public(
            "get_uta_position_tiers",
            self._params(category=category, product_symbol=product_symbol, coin=coin),
        )

    async def get_uta_open_interest_limit(
        self, category: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/oi-limit``."""
        return await self._native_public(
            "get_uta_open_interest_limit",
            self._params(product_symbol=product_symbol, category=category),
        )

    async def get_uta_discount_rates(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/discount-rate``."""
        return await self._native_public("get_uta_discount_rates", self._params())

    async def get_uta_rpi_orderbook(
        self, category: str, product_symbol: str, *, limit: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/rpi-orderbook``."""
        return await self._native_public(
            "get_uta_rpi_orderbook",
            self._params(category=category, product_symbol=product_symbol, limit=limit),
        )

    async def get_uta_rpi_symbols(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/rpi-symbols``."""
        return await self._native_public("get_uta_rpi_symbols", self._params())

    async def get_server_time(self) -> dict[str, Any]:
        """Call ``GET /api/v2/public/time``."""
        return await self._native_public("get_server_time", self._params())

    async def get_uta_cash_dividend_records(
        self,
        product_symbol: str,
        type_: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/cash-dividend-records``."""
        return await self._native_public(
            "get_uta_cash_dividend_records",
            self._params(product_symbol=product_symbol, type=type_, cursor=cursor, limit=limit),
        )

    async def get_uta_risk_reserve(
        self, category: str, product_symbol: str, *, margin_coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/risk-reserve``."""
        return await self._native_public(
            "get_uta_risk_reserve",
            self._params(category=category, product_symbol=product_symbol, marginCoin=margin_coin),
        )

    async def get_uta_all_risk_reserves(self, category: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/risk-reserve-all``."""
        return await self._native_public(
            "get_uta_all_risk_reserves", self._params(category=category)
        )

    async def get_uta_hourly_risk_reserve(
        self, category: str, product_symbol: str, *, margin_coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/risk-reserve-hour``."""
        return await self._native_public(
            "get_uta_hourly_risk_reserve",
            self._params(category=category, product_symbol=product_symbol, marginCoin=margin_coin),
        )

    async def get_uta_split_records(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/split-records``."""
        return await self._native_public("get_uta_split_records", self._params())

    async def get_uta_futures_long_short_ratio(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-account-long-short``."""
        return await self._native_public(
            "get_uta_futures_long_short_ratio",
            self._params(product_symbol=product_symbol, period=period),
        )

    async def get_uta_spot_whale_flow(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/spot-whale-flow``."""
        return await self._native_public(
            "get_uta_spot_whale_flow", self._params(product_symbol=product_symbol)
        )

    async def get_classic_interest_rate_record(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/interest-rate-record``."""
        return await self._native_public(
            "get_classic_interest_rate_record", self._params(coin=coin)
        )

    async def get_classic_margin_currencies(self) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/currencies``."""
        return await self._native_public("get_classic_margin_currencies", self._params())

    async def get_classic_convert_currencies(self) -> dict[str, Any]:
        """Call ``GET /api/v2/convert/currencies``."""
        return await self._native_public("get_classic_convert_currencies", self._params())

    async def get_classic_merge_depth(
        self, product_symbol: str, *, precision: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/market/merge-depth``."""
        return await self._native_public(
            "get_classic_merge_depth",
            self._params(product_symbol=product_symbol, precision=precision, limit=limit),
        )

    async def get_classic_auction(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/market/auction``."""
        return await self._native_public(
            "get_classic_auction", self._params(product_symbol=product_symbol)
        )

    async def get_classic_vip_fee_rate(self) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/market/vip-fee-rate``."""
        return await self._native_public("get_classic_vip_fee_rate", self._params())

    async def get_uta_proof_of_reserves(self) -> dict[str, Any]:
        """Call ``GET /api/v3/market/proof-of-reserves``."""
        return await self._native_public("get_uta_proof_of_reserves", self._params())

    async def get_uta_score_weights(self, *, category: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/market/score-weights``."""
        return await self._native_public("get_uta_score_weights", self._params(category=category))

    async def get_uta_fee_group(self, category: str, *, group: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/market/fee-group``."""
        return await self._native_public(
            "get_uta_fee_group", self._params(category=category, group=group)
        )

    async def get_uta_spot_fund_flow(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/spot-fund-flow``."""
        return await self._native_public(
            "get_uta_spot_fund_flow", self._params(product_symbol=product_symbol, period=period)
        )

    async def get_uta_spot_net_flow(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v3/market/spot-net-flow``."""
        return await self._native_public(
            "get_uta_spot_net_flow", self._params(product_symbol=product_symbol)
        )

    async def get_uta_margin_long_short(
        self, product_symbol: str, *, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-long-short``."""
        return await self._native_public(
            "get_uta_margin_long_short",
            self._params(product_symbol=product_symbol, period=period, coin=coin),
        )

    async def get_uta_margin_loan_growth(
        self, product_symbol: str, *, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-loan-growth``."""
        return await self._native_public(
            "get_uta_margin_loan_growth",
            self._params(product_symbol=product_symbol, period=period, coin=coin),
        )

    async def get_uta_margin_isolated_borrow(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/margin-isolated-borrow``."""
        return await self._native_public(
            "get_uta_margin_isolated_borrow",
            self._params(product_symbol=product_symbol, period=period),
        )

    async def get_uta_futures_active_buy_sell(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-active-buy-sell``."""
        return await self._native_public(
            "get_uta_futures_active_buy_sell",
            self._params(product_symbol=product_symbol, period=period),
        )

    async def get_uta_futures_long_short(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-long-short``."""
        return await self._native_public(
            "get_uta_futures_long_short", self._params(product_symbol=product_symbol, period=period)
        )

    async def get_uta_futures_position_long_short(
        self, product_symbol: str, *, period: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/market/futures-position-long-short``."""
        return await self._native_public(
            "get_uta_futures_position_long_short",
            self._params(product_symbol=product_symbol, period=period),
        )
