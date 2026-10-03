"""Bybit Market HTTP client backed by Rust."""

from typing import Any

from dcex._schema_codec import normalize_params

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """Bybit market data HTTP client."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Bybit public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Bybit native client is required for public market methods.")
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

    def get_instruments_info(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        symbolType: str | None = None,
        status: str | None = None,
        baseCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get instruments information."""
        return self._native_public(
            "get_instruments_info",
            self._params(
                category=category,
                product_symbol=product_symbol,
                symbolType=symbolType,
                status=status,
                baseCoin=baseCoin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_kline(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get kline/candlestick data."""
        return self._native_public(
            "get_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get order book data."""
        return self._native_public(
            "get_orderbook",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    def get_tickers(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        expDate: str | None = None,
    ) -> dict[str, Any]:
        """Get ticker information."""
        return self._native_public(
            "get_tickers",
            self._params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                expDate=expDate,
            ),
        )

    def get_funding_rate_history(
        self,
        product_symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get funding rate history."""
        return self._native_public(
            "get_funding_rate_history",
            self._params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_public_trade_history(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        category: str | None = None,
        baseCoin: str | None = None,
        optionType: str | None = None,
    ) -> dict[str, Any]:
        """Get public trade history."""
        return self._native_public(
            "get_public_trade_history",
            self._params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                optionType=optionType,
                limit=limit,
            ),
        )

    def get_open_interest(
        self,
        product_symbol: str,
        intervalTime: str = "5min",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get open interest history."""
        return self._native_public(
            "get_open_interest",
            self._params(
                product_symbol=product_symbol,
                intervalTime=intervalTime,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_long_short_ratio(
        self,
        product_symbol: str,
        period: str = "5min",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get long/short account ratio history."""
        return self._native_public(
            "get_long_short_ratio",
            self._params(
                product_symbol=product_symbol,
                period=period,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_historical_volatility(
        self,
        category: str = "option",
        baseCoin: str | None = None,
        quoteCoin: str | None = None,
        period: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get historical volatility data."""
        return self._native_public(
            "get_historical_volatility",
            self._params(
                category=category,
                baseCoin=baseCoin,
                quoteCoin=quoteCoin,
                period=period,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_insurance_pool(self, coin: str | None = None) -> dict[str, Any]:
        """Get insurance pool data."""
        return self._native_public("get_insurance_pool", self._params(coin=coin))

    def get_delivery_price(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get delivery price data."""
        return self._native_public(
            "get_delivery_price",
            self._params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_order_price_limit(
        self,
        product_symbol: str,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Get order price limit data."""
        return self._native_public(
            "get_order_price_limit",
            self._params(category=category, product_symbol=product_symbol),
        )

    def get_adl_alert(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """Get ADL alert data."""
        return self._native_public(
            "get_adl_alert",
            self._params(product_symbol=product_symbol),
        )

    def get_risk_limit(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get risk limit information."""
        return self._native_public(
            "get_risk_limit",
            self._params(category=category, product_symbol=product_symbol, cursor=cursor),
        )

    def get_spread_instruments(
        self,
        *,
        symbol: str | None = None,
        base_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Bybit spread combination specifications."""
        return self._native_public(
            "get_spread_instruments",
            self._native_params(symbol=symbol, baseCoin=base_coin, limit=limit, cursor=cursor),
        )

    def get_spread_orderbook(self, symbol: str, *, limit: int | None = None) -> dict[str, Any]:
        """Get the spread combination order book."""
        return self._native_public(
            "get_spread_orderbook", self._native_params(symbol=symbol, limit=limit)
        )

    def get_spread_tickers(self, symbol: str) -> dict[str, Any]:
        """Get the latest spread combination ticker."""
        return self._native_public("get_spread_tickers", self._native_params(symbol=symbol))

    def get_spread_recent_trades(self, symbol: str, *, limit: int | None = None) -> dict[str, Any]:
        """Get recent public spread executions."""
        return self._native_public(
            "get_spread_recent_trades", self._native_params(symbol=symbol, limit=limit)
        )

    def get_mark_price_kline(
        self,
        product_symbol: str,
        interval: str,
        *,
        category: str | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get mark price candles; interval uses values such as ``1m`` or ``1h``."""
        return self._native_public(
            "get_mark_price_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                category=category,
                start=start,
                end=end,
                limit=limit,
            ),
        )

    def get_index_price_kline(
        self,
        product_symbol: str,
        interval: str,
        *,
        category: str | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get index price candles; interval uses values such as ``1m`` or ``1h``."""
        return self._native_public(
            "get_index_price_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                category=category,
                start=start,
                end=end,
                limit=limit,
            ),
        )

    def get_premium_index_price_kline(
        self,
        product_symbol: str,
        interval: str,
        *,
        category: str | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get premium index price candles; interval uses values such as ``1m`` or ``1h``."""
        return self._native_public(
            "get_premium_index_price_kline",
            self._params(
                product_symbol=product_symbol,
                interval=interval,
                category=category,
                start=start,
                end=end,
                limit=limit,
            ),
        )

    def get_full_orderbook(self, category: str, product_symbol: str) -> dict[str, Any]:
        """Get full orderbook; see https://bybit-exchange.github.io/docs/v5/market/full-ob."""
        return self._native_public(
            "get_full_orderbook", self._params(category=category, product_symbol=product_symbol)
        )

    def get_rpi_orderbook(
        self, product_symbol: str, limit: int, category: str | None = None
    ) -> dict[str, Any]:
        """Get rpi orderbook; see https://bybit-exchange.github.io/docs/v5/market/rpi-orderbook."""
        return self._native_public(
            "get_rpi_orderbook",
            self._params(product_symbol=product_symbol, limit=limit, category=category),
        )

    def get_system_status(self, id: str | None = None, state: str | None = None) -> dict[str, Any]:
        """Get system status; see https://bybit-exchange.github.io/docs/v5/system-status."""
        return self._native_public("get_system_status", self._params(id=id, state=state))

    def get_announcements(
        self,
        *,
        locale: str,
        type_: str | None = None,
        tag: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/announcements/index.

        Source:
        https://bybit-exchange.github.io/docs/v5/announcement

        """
        return self._native_public(
            "get_announcements",
            self._native_params(locale=locale, type=type_, tag=tag, page=page, limit=limit),
        )

    def get_fee_group_info(
        self, *, product_type: str, group_id: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/market/fee-group-info.

        Source:
        https://bybit-exchange.github.io/docs/v5/market/fee-group-info

        """
        return self._native_public(
            "get_fee_group_info", self._native_params(productType=product_type, groupId=group_id)
        )

    def get_index_price_components(self, *, index_name: str) -> dict[str, Any]:
        """
        GET /v5/market/index-price-components.

        Source:
        https://bybit-exchange.github.io/docs/v5/market/index-components

        """
        return self._native_public(
            "get_index_price_components", self._native_params(indexName=index_name)
        )

    def get_option_delivery_prices(
        self, *, category: str, base_coin: str, settle_coin: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/market/new-delivery-price.

        Source:
        https://bybit-exchange.github.io/docs/v5/market/new-delivery-price

        """
        return self._native_public(
            "get_option_delivery_prices",
            self._native_params(category=category, baseCoin=base_coin, settleCoin=settle_coin),
        )

    def get_option_base_coins(self, *, underlying_type: str | None = None) -> dict[str, Any]:
        """
        GET /v5/market/option-base-coins.

        Source:
        https://bybit-exchange.github.io/docs/v5/market/option-base-coins

        """
        return self._native_public(
            "get_option_base_coins", self._native_params(underlyingType=underlying_type)
        )

    def get_crypto_loan_collateral_data(
        self, *, vip_level: str | None = None, currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/collateral-data.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/collateral-coin.mdx
        """
        return self._native_public(
            "get_crypto_loan_collateral_data",
            self._native_params(vipLevel=vip_level, currency=currency),
        )

    def get_crypto_loan_loanable_data(
        self, *, vip_level: str | None = None, currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan/loanable-data.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/loan-coin.mdx
        """
        return self._native_public(
            "get_crypto_loan_loanable_data",
            self._native_params(vipLevel=vip_level, currency=currency),
        )

    def get_crypto_loan_common_collateral_data(
        self, *, currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-common/collateral-data.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/collateral-coin.mdx
        """
        return self._native_public(
            "get_crypto_loan_common_collateral_data", self._native_params(currency=currency)
        )

    def get_crypto_loan_fixed_borrow_order_quote(
        self,
        *,
        order_currency: str,
        order_by: str,
        term: str | None = None,
        sort: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/borrow-order-quote.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow-market.mdx
        """
        return self._native_public(
            "get_crypto_loan_fixed_borrow_order_quote",
            self._native_params(
                orderCurrency=order_currency, orderBy=order_by, term=term, sort=sort, limit=limit
            ),
        )

    def get_crypto_loan_fixed_supply_order_quote(
        self,
        *,
        order_currency: str,
        order_by: str,
        term: str | None = None,
        sort: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-fixed/supply-order-quote.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/supply-market.mdx
        """
        return self._native_public(
            "get_crypto_loan_fixed_supply_order_quote",
            self._native_params(
                orderCurrency=order_currency, term=term, orderBy=order_by, sort=sort, limit=limit
            ),
        )

    def get_crypto_loan_common_loanable_data(
        self, *, vip_level: str | None = None, currency: str | None = None
    ) -> dict[str, Any]:
        """
        GET /v5/crypto-loan-common/loanable-data.

        Decimal amounts are strings. Source: https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/loan-coin.mdx
        """
        return self._native_public(
            "get_crypto_loan_common_loanable_data",
            self._native_params(vipLevel=vip_level, currency=currency),
        )

    def get_spot_lever_token_reference(self, *, lt_coin: str) -> dict[str, Any]:
        """
        GET /v5/spot-lever-token/reference.

        Decimal amounts are strings. Source: https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/leverage-token-reference.mdx
        """
        return self._native_public(
            "get_spot_lever_token_reference", self._native_params(ltCoin=lt_coin)
        )

    def get_server_time(self) -> dict[str, Any]:
        """Retrieve the exchange server time."""
        return self._native_public("get_server_time", [])
