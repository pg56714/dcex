"""KuCoin Spot and Futures Market async HTTP client backed by Rust."""

import json
from typing import Any

from dcex._schema_codec import normalize_params

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Async HTTP client for KuCoin public market API operations."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed KuCoin public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("KuCoin native client is required for public market methods.")
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
            if key == "from_":
                key = "from"
            if isinstance(value, list):
                value = json.dumps(value, separators=(",", ":"))
            params.append((key, str(value)))
        return params

    async def get_spot_instrument_info(self, market: str | None = None) -> dict[str, Any]:
        """Retrieve trading instrument information."""
        return await self._native_public(
            "get_spot_instrument_info",
            self._params(market=market),
        )

    async def get_spot_ticker(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve single ticker information for a specific trading pair."""
        return await self._native_public(
            "get_spot_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_all_tickers(self) -> dict[str, Any]:
        """Retrieve ticker information for all trading pairs."""
        return await self._native_public("get_spot_all_tickers", [])

    async def get_spot_orderbook(self, product_symbol: str, depth: int = 20) -> dict[str, Any]:
        """Retrieve the top 20 (default) or 100 orderbook levels for a trading pair."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(product_symbol=product_symbol, depth=depth),
        )

    async def get_spot_public_trades(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve public trade history for a specific trading pair."""
        return await self._native_public(
            "get_spot_public_trades",
            self._params(product_symbol=product_symbol),
        )

    async def get_spot_kline(
        self,
        product_symbol: str,
        timeframe: str,
        startAt: int | None = None,
        endAt: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve candlestick/K-line data for a specific trading pair."""
        return await self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=product_symbol,
                timeframe=timeframe,
                startAt=startAt,
                endAt=endAt,
            ),
        )

    async def get_futures_contracts(self) -> dict[str, Any]:
        """Retrieve active KuCoin futures contracts."""
        return await self._native_public("get_futures_contracts", [])

    async def get_futures_contract(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve one KuCoin futures contract."""
        return await self._native_public(
            "get_futures_contract",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_ticker(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve one KuCoin futures ticker."""
        return await self._native_public(
            "get_futures_ticker",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures orderbook."""
        return await self._native_public(
            "get_futures_orderbook",
            self._params(
                product_symbol=product_symbol,
                depth=depth,
            ),
        )

    async def get_futures_public_trades(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve KuCoin futures public trade history."""
        return await self._native_public(
            "get_futures_public_trades",
            self._params(product_symbol=product_symbol),
        )

    async def get_futures_kline(
        self,
        product_symbol: str,
        timeframe: str,
        from_: int | None = None,
        to: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures candlestick/K-line data."""
        return await self._native_public(
            "get_futures_kline",
            self._params(
                product_symbol=product_symbol,
                timeframe=timeframe,
                from_=from_,
                to=to,
            ),
        )

    async def get_futures_open_interest(
        self,
        product_symbol: str | list[str] | None = None,
        interval: str | None = None,
        startAt: int | None = None,
        endAt: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Get futures open interest history."""
        return await self._native_public(
            "get_futures_open_interest",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startAt=startAt,
                endAt=endAt,
                pageSize=pageSize,
            ),
        )

    async def get_uta_position_tiers(
        self,
        product_symbol: str | None = None,
        tradeType: str = "FUTURES",
        currency: str | None = None,
        marginMode: str = "CROSS",
        data: str = "RISK_LIMIT",
        accountType: str = "UNIFIED",
    ) -> dict[str, Any]:
        """Retrieve KuCoin UTA futures position tiers and risk limits."""
        return await self._native_public(
            "get_uta_position_tiers",
            self._params(
                product_symbol=product_symbol,
                tradeType=tradeType,
                currency=currency,
                marginMode=marginMode,
                data=data,
                accountType=accountType,
            ),
        )

    async def get_futures_current_funding_rate(self, product_symbol: str) -> dict[str, Any]:
        """GET /api/v1/funding-rate/{symbol}/current; public market data."""
        return await self._native_public(
            "get_futures_current_funding_rate", self._native_params(product_symbol=product_symbol)
        )

    async def get_futures_public_funding_history(
        self, product_symbol: str, from_: int, to: int
    ) -> dict[str, Any]:
        """GET /api/v1/contract/funding-rates; public market data."""
        return await self._native_public(
            "get_futures_public_funding_history",
            self._native_params(product_symbol=product_symbol, **{"from": from_, "to": to}),
        )

    async def get_futures_all_tickers(self) -> dict[str, Any]:
        """Call ``GET /api/v1/allTickers``."""
        return await self._native_public("get_futures_all_tickers", self._native_params())

    async def get_futures_mark_price(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v1/mark-price/{symbol}/current``."""
        return await self._native_public(
            "get_futures_mark_price", self._native_params(product_symbol=product_symbol)
        )

    async def get_futures_server_time(self) -> dict[str, Any]:
        """Call ``GET /api/v1/timestamp``."""
        return await self._native_public("get_futures_server_time", self._native_params())

    async def get_futures_service_status(self) -> dict[str, Any]:
        """Call ``GET /api/v1/status``."""
        return await self._native_public("get_futures_service_status", self._native_params())

    async def get_margin_mark_price(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v1/mark-price/{symbol}/current``."""
        return await self._native_public(
            "get_margin_mark_price", self._native_params(product_symbol=product_symbol)
        )

    async def get_margin_mark_prices(self) -> dict[str, Any]:
        """Call ``GET /api/v3/mark-price/all-symbols``."""
        return await self._native_public("get_margin_mark_prices", self._native_params())

    async def get_spot_server_time(self) -> dict[str, Any]:
        """Call ``GET /api/v1/timestamp``."""
        return await self._native_public("get_spot_server_time", self._native_params())

    async def get_spot_service_status(self) -> dict[str, Any]:
        """Call ``GET /api/v1/status``."""
        return await self._native_public("get_spot_service_status", self._native_params())

    async def get_uta_borrowable_currencies(self) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/borrowable-currency``."""
        return await self._native_public("get_uta_borrowable_currencies", self._native_params())

    async def get_uta_collateral_ratios(self) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/collateral-discount-ratio``."""
        return await self._native_public("get_uta_collateral_ratios", self._native_params())

    async def get_uta_current_funding_rates(
        self, *, product_symbol: str | None = None, product_type: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/funding-rate``."""
        return await self._native_public(
            "get_uta_current_funding_rates",
            self._native_params(product_symbol=product_symbol, productType=product_type),
        )

    async def get_uta_funding_rate_history(
        self, product_symbol: str, start_at: str, end_at: str
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/funding-rate-history``."""
        return await self._native_public(
            "get_uta_funding_rate_history",
            self._native_params(product_symbol=product_symbol, startAt=start_at, endAt=end_at),
        )

    async def get_uta_index_prices(
        self,
        product_symbol: str,
        *,
        start_at: str | None = None,
        end_at: str | None = None,
        page_size: str | None = None,
        last_id: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/index-price``."""
        return await self._native_public(
            "get_uta_index_prices",
            self._native_params(
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                pageSize=page_size,
                lastId=last_id,
            ),
        )

    async def get_uta_interest_rate_index(
        self,
        product_symbol: str,
        *,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/interest-rate-index``."""
        return await self._native_public(
            "get_uta_interest_rate_index",
            self._native_params(
                product_symbol=product_symbol,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                pageSize=page_size,
            ),
        )

    async def get_uta_klines(
        self,
        product_symbol: str,
        trade_type: str,
        interval: str,
        *,
        kline_type: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """
        Call ``GET /api/ua/v2/market/kline``. Times are in seconds; futures do not support 6hour
        or 3day intervals.
        """
        return await self._native_public(
            "get_uta_klines",
            self._native_params(
                product_symbol=product_symbol,
                tradeType=trade_type,
                klineType=kline_type,
                interval=interval,
                startAt=start_at,
                endAt=end_at,
            ),
        )

    async def get_uta_service_status(self, trade_type: str) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/server/status``."""
        return await self._native_public(
            "get_uta_service_status", self._native_params(tradeType=trade_type)
        )

    async def get_uta_tickers(
        self, trade_type: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/ticker``."""
        return await self._native_public(
            "get_uta_tickers",
            self._native_params(tradeType=trade_type, product_symbol=product_symbol),
        )

    async def get_uta_trade_statistics(self) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/trade-statistics``."""
        return await self._native_public("get_uta_trade_statistics", self._native_params())

    async def get_uta_public_trades(self, trade_type: str, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/trade``."""
        return await self._native_public(
            "get_uta_public_trades",
            self._native_params(tradeType=trade_type, product_symbol=product_symbol),
        )

    async def get_uta_instruments(
        self, trade_type: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/ua/v2/market/instrument``."""
        return await self._native_public(
            "get_uta_instruments",
            self._native_params(product_symbol=product_symbol, tradeType=trade_type),
        )

    async def get_convert_currencies(self) -> dict[str, Any]:
        """

        GET /api/v1/convert/currencies.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-currencies

        """
        return await self._native_public("get_convert_currencies", self._native_params())

    async def get_convert_symbol(
        self, *, from_currency: str, to_currency: str, order_type: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v1/convert/symbol.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/convert/get-convert-symbol

        """
        return await self._native_public(
            "get_convert_symbol",
            self._native_params(
                fromCurrency=from_currency, toCurrency=to_currency, orderType=order_type
            ),
        )

    async def get_futures_interest_rate_index(
        self,
        *,
        symbol: str,
        start_at: int | None = None,
        end_at: int | None = None,
        reverse: bool | None = None,
        offset: int | None = None,
        forward: bool | None = None,
        max_count: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/interest/query.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/futures-trading/market-data/get-interest-rate-index

        """
        return await self._native_public(
            "get_futures_interest_rate_index",
            self._native_params(
                symbol=symbol,
                startAt=start_at,
                endAt=end_at,
                reverse=reverse,
                offset=offset,
                forward=forward,
                maxCount=max_count,
            ),
        )

    async def get_futures_premium_index(
        self,
        *,
        symbol: str,
        start_at: int | None = None,
        end_at: int | None = None,
        reverse: bool | None = None,
        offset: int | None = None,
        forward: bool | None = None,
        max_count: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/premium/query.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/futures-trading/market-data/get-premium-index

        """
        return await self._native_public(
            "get_futures_premium_index",
            self._native_params(
                symbol=symbol,
                startAt=start_at,
                endAt=end_at,
                reverse=reverse,
                offset=offset,
                forward=forward,
                maxCount=max_count,
            ),
        )

    async def get_margin_config(self) -> dict[str, Any]:
        """

        GET /api/v1/margin/config.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/margin-trading/market-data/get-margin-config

        """
        return await self._native_public("get_margin_config", self._native_params())

    async def get_announcements(
        self,
        *,
        current_page: int | None = None,
        page_size: int | None = None,
        ann_type: str | None = None,
        lang: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v3/announcements.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-announcements

        """
        return await self._native_public(
            "get_announcements",
            self._native_params(
                currentPage=current_page,
                pageSize=page_size,
                annType=ann_type,
                lang=lang,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    async def get_call_auction_info(self, *, symbol: str) -> dict[str, Any]:
        """

        GET /api/v1/market/callauctionData.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-call-auction-info

        """
        return await self._native_public(
            "get_call_auction_info", self._native_params(symbol=symbol)
        )

    async def get_call_auction_part_order_book(self, *, size: int, symbol: str) -> dict[str, Any]:
        """

        GET /api/v1/market/orderbook/callauction/level2_{size}.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-call-auction-part-orderbook

        """
        return await self._native_public(
            "get_call_auction_part_order_book", self._native_params(size=size, symbol=symbol)
        )

    async def get_spot_currency_v3(
        self, *, currency: str, chain: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v3/currencies/{currency}.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-currency

        """
        return await self._native_public(
            "get_spot_currency_v3", self._native_params(currency=currency, chain=chain)
        )

    async def get_fiat_price(
        self, *, base: str | None = None, currencies: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v1/prices.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-fiat-price

        """
        return await self._native_public(
            "get_fiat_price", self._native_params(base=base, currencies=currencies)
        )

    async def get_market_list(self) -> dict[str, Any]:
        """

        GET /api/v1/markets.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-market-list

        """
        return await self._native_public("get_market_list", self._native_params())

    async def get_spot_symbol_v2(self, *, symbol: str) -> dict[str, Any]:
        """

        GET /api/v2/symbols/{symbol}.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-symbol

        """
        return await self._native_public("get_spot_symbol_v2", self._native_params(symbol=symbol))

    async def get_uta_currencies(
        self, *, chain: str | None = None, currency_list: list[str] | None = None
    ) -> dict[str, Any]:
        """

        GET /api/ua/v2/asset/currencies.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/currencies

        """
        return await self._native_public(
            "get_uta_currencies", self._native_params(chain=chain, currencyList=currency_list)
        )

    async def get_uta_currency(self, *, currency: str, chain: str | None = None) -> dict[str, Any]:
        """

        GET /api/ua/v2/market/currency.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/currency

        """
        return await self._native_public(
            "get_uta_currency", self._native_params(chain=chain, currency=currency)
        )

    async def get_uta_fiat_price(
        self, *, base: str, currencies: list[str] | None = None
    ) -> dict[str, Any]:
        """

        GET /api/ua/v2/market/fiat-price.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/fiat-price

        """
        return await self._native_public(
            "get_uta_fiat_price", self._native_params(base=base, currencies=currencies)
        )

    async def get_uta_announcements(
        self,
        *,
        language: str | None = None,
        type_: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/ua/v2/market/announcement.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/get-announcements

        """
        return await self._native_public(
            "get_uta_announcements",
            self._native_params(
                language=language,
                type=type_,
                pageNumber=page_number,
                pageSize=page_size,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    async def get_uta_call_auction_info(self, *, symbol: str) -> dict[str, Any]:
        """

        GET /api/ua/v2/market/call-auction-info.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/get-call-auction-info

        """
        return await self._native_public(
            "get_uta_call_auction_info", self._native_params(symbol=symbol)
        )

    async def get_uta_client_ip_address(self) -> dict[str, Any]:
        """

        GET /api/ua/v2/user/my-ip.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/get-client-ip-address

        """
        return await self._native_public("get_uta_client_ip_address", self._native_params())

    async def get_uta_kyc_regions(self) -> dict[str, Any]:
        """

        GET /api/ua/v2/user/kyc-region.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/v2/rest/ua/get-kyc-region

        """
        return await self._native_public("get_uta_kyc_regions", self._native_params())

    async def get_spot_24h_statistics(self, *, symbol: str) -> dict[str, Any]:
        """

        GET /api/v1/market/stats.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-24hr-stats

        """
        return await self._native_public(
            "get_spot_24h_statistics", self._native_params(symbol=symbol)
        )

    async def get_client_ip_address(self) -> dict[str, Any]:
        """

        GET /api/v1/my-ip.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-client-ip-address

        """
        return await self._native_public("get_client_ip_address", self._native_params())

    async def get_kyc_regions(self) -> dict[str, Any]:
        """

        GET /api/kyc/regions/v4.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-kyc-regions

        """
        return await self._native_public("get_kyc_regions", self._native_params())

    async def get_spot_index_price(
        self,
        *,
        symbol: str,
        start_at: int | None = None,
        end_at: int | None = None,
        reverse: bool | None = None,
        offset: int | None = None,
        forward: bool | None = None,
        max_count: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v1/index/query.

        Use native exchange symbols and decimal strings. Source:
        https://www.kucoin.com/docs-new/rest/futures-trading/market-data/get-spot-index-price

        """
        return await self._native_public(
            "get_spot_index_price",
            self._native_params(
                symbol=symbol,
                startAt=start_at,
                endAt=end_at,
                reverse=reverse,
                offset=offset,
                forward=forward,
                maxCount=max_count,
            ),
        )

    async def get_uta_oes_currency(
        self, *, custodian: str | None = None, currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/ua/v2/oes/currency.

        Use native exchange symbols and decimal strings. Source: https://www.kucoin.com/docs-new/v2/rest/ua/get-oes-settlement-currency
        """
        return await self._native_public(
            "get_uta_oes_currency", self._native_params(custodian=custodian, currency=currency)
        )

    async def get_currencies_v3(self) -> dict[str, Any]:
        """List current currency metadata."""
        return await self._native_public("get_currencies_v3", self._native_params())
