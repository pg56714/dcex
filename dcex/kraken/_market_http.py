"""Kraken public market-data HTTP client backed by Rust."""

from json import dumps
from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for Kraken public market-data APIs."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Kraken public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Kraken native client is required for public market methods.")
        response, data = request_native_json(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    def get_server_time(self) -> dict[str, Any]:
        """Retrieve Kraken spot server time."""
        return self._native_public("get_server_time", [])

    def get_spot_system_status(self) -> dict[str, Any]:
        """Retrieve Kraken spot system status."""
        return self._native_public("get_spot_system_status", [])

    def get_spot_assets(
        self,
        asset: str | None = None,
        aclass: str | None = None,
        assetVersion: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot asset metadata."""
        return self._native_public(
            "get_spot_assets",
            self._native_params(asset=asset, aclass=aclass, assetVersion=assetVersion),
        )

    def get_spot_spread(
        self,
        product_symbol: str,
        since: str | None = None,
        assetVersion: int | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve recent Kraken spot bid/ask spreads."""
        return self._native_public(
            "get_spot_spread",
            self._native_params(
                product_symbol=product_symbol,
                since=since,
                assetVersion=assetVersion,
                asset_class=asset_class,
            ),
        )

    def get_spot_asset_pairs(
        self,
        pair: str | None = None,
        info: str = "info",
        assetVersion: int | None = None,
        aclass_base: str | None = None,
        country_code: str | None = None,
        execution_venue: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot tradable asset pairs."""
        return self._native_public(
            "get_spot_asset_pairs",
            self._native_params(
                pair=pair,
                info=info,
                assetVersion=assetVersion,
                aclass_base=aclass_base,
                country_code=country_code,
                execution_venue=execution_venue,
            ),
        )

    def get_spot_ticker(
        self,
        product_symbol: str | None = None,
        pair: str | None = None,
        assetVersion: int | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot ticker data for one pair or all pairs."""
        if product_symbol is not None and pair is not None:
            raise ValueError("Specify either product_symbol or pair, not both.")
        return self._native_public(
            "get_spot_ticker",
            self._native_params(
                product_symbol=product_symbol,
                pair=pair,
                assetVersion=assetVersion,
                asset_class=asset_class,
            ),
        )

    def get_spot_orderbook(
        self,
        product_symbol: str,
        count: int | None = None,
        assetVersion: int | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot orderbook data."""
        return self._native_public(
            "get_spot_orderbook",
            self._native_params(
                product_symbol=product_symbol,
                count=count,
                assetVersion=assetVersion,
                asset_class=asset_class,
            ),
        )

    def get_spot_public_trades(
        self,
        product_symbol: str,
        since: str | None = None,
        count: int | None = None,
        assetVersion: int | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot public trades."""
        return self._native_public(
            "get_spot_public_trades",
            self._native_params(
                product_symbol=product_symbol,
                since=since,
                count=count,
                assetVersion=assetVersion,
                asset_class=asset_class,
            ),
        )

    def get_spot_kline(
        self,
        product_symbol: str,
        interval: int = 1,
        since: int | None = None,
        assetVersion: int | None = None,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot OHLC candles."""
        return self._native_public(
            "get_spot_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                since=since,
                assetVersion=assetVersion,
                asset_class=asset_class,
            ),
        )

    def get_futures_instruments(
        self,
        contractType: str | list[str] | None = None,
        expired: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures instruments."""
        return self._native_public(
            "get_futures_instruments",
            self._native_params(contractType=contractType, expired=expired),
        )

    def get_futures_tickers(
        self,
        product_symbol: str | None = None,
        contractType: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures ticker data for one symbol or all symbols."""
        return self._native_public(
            "get_futures_tickers",
            self._native_params(product_symbol=product_symbol, contractType=contractType),
        )

    def get_futures_orderbook(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures orderbook data."""
        return self._native_public(
            "get_futures_orderbook",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_public_trades(
        self,
        product_symbol: str,
        lastTime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures recent public trade history."""
        return self._native_public(
            "get_futures_public_trades",
            self._native_params(product_symbol=product_symbol, lastTime=lastTime),
        )

    def get_futures_kline(
        self,
        product_symbol: str,
        timeframe: str,
        tick_type: str = "trade",
        from_: int | None = None,
        to: int | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures chart candles."""
        return self._native_public(
            "get_futures_kline",
            self._native_params(
                product_symbol=product_symbol,
                timeframe=timeframe,
                tick_type=tick_type,
                from_=from_,
                to=to,
                count=count,
            ),
        )

    def get_futures_funding_history(self, product_symbol: str) -> dict[str, Any]:
        """Get historical derivatives funding rates."""
        return self._native_public(
            "get_futures_funding_history", self._native_params(product_symbol=product_symbol)
        )

    def get_futures_instrument_status(self, *, product_symbol: str) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/instruments/{symbol}/status.

        Source: https://docs.kraken.com/api-reference/instrument-details/get-instrument-status
        """
        return self._native_public(
            "get_futures_instrument_status", self._native_params(product_symbol=product_symbol)
        )

    def get_futures_instrument_statuses(
        self, *, contract_types: list[str] | None = None
    ) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/instruments/status.

        Source: https://docs.kraken.com/api-reference/instrument-details/get-instrument-status-list
        """
        return self._native_public(
            "get_futures_instrument_statuses",
            self._native_params(
                contractType=dumps(contract_types) if contract_types is not None else None
            ),
        )

    def get_spot_grouped_orderbook(
        self, *, product_symbol: str, depth: int | None = None, grouping: int | None = None
    ) -> dict[str, Any]:
        """
        GET /0/public/GroupedBook.

        Source: https://docs.kraken.com/api-reference/market-data/get-grouped-order-book
        """
        return self._native_public(
            "get_spot_grouped_orderbook",
            self._native_params(product_symbol=product_symbol, depth=depth, grouping=grouping),
        )

    def get_spot_maintenance_schedule(self) -> dict[str, Any]:
        """
        GET /0/public/MaintenanceSchedule.

        Source: https://docs.kraken.com/api-reference/market-data/get-maintenance-schedule
        """
        return self._native_public("get_spot_maintenance_schedule", self._native_params())

    def get_futures_market_analytics(
        self, *, symbol: str, analytics_type: str, since: int, interval: int, to: int | None = None
    ) -> dict[str, Any]:
        """
        GET /api/charts/v1/analytics/{symbol}/{analytics_type}.

        Source: https://docs.kraken.com/api-reference/analytics/market-analytics
        """
        return self._native_public(
            "get_futures_market_analytics",
            self._native_params(
                symbol=symbol, analytics_type=analytics_type, since=since, interval=interval, to=to
            ),
        )

    def get_futures_ticker(self, *, symbol: str) -> dict[str, Any]:
        """
        GET /derivatives/api/v3/tickers/{symbol}.

        Source: https://docs.kraken.com/api-reference/market-data/get-ticker-by-symbol
        """
        return self._native_public("get_futures_ticker", self._native_params(symbol=symbol))

    def get_spot_post_trade_data(
        self,
        *,
        symbol: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """
        GET /0/public/PostTrade.

        Source: https://docs.kraken.com/api-reference/transparency/post-trade-data
        """
        return self._native_public(
            "get_spot_post_trade_data",
            self._native_params(symbol=symbol, from_ts=from_ts, to_ts=to_ts, count=count),
        )

    def get_spot_pre_trade_data(self, *, symbol: str) -> dict[str, Any]:
        """
        GET /0/public/PreTrade.

        Source: https://docs.kraken.com/api-reference/transparency/pre-trade-data
        """
        return self._native_public("get_spot_pre_trade_data", self._native_params(symbol=symbol))
