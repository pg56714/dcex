"""MEXC public market-data HTTP client backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for MEXC public market-data APIs."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed MEXC public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("MEXC native client is required for public market methods.")
        response, data = request_native_json(
            self._native_client,
            "public_request",
            method_name,
            params,
        )
        self._store_response_headers(response)
        return data

    def ping(self) -> dict[str, Any] | list[Any]:
        """Test MEXC Spot API connectivity."""
        return self._native_public("ping", [])

    def get_spot_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot server time."""
        return self._native_public("get_spot_time", [])

    def get_spot_default_symbols(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot API default symbols."""
        return self._native_public("get_spot_default_symbols", [])

    def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        symbols: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot exchange information."""
        return self._native_public(
            "get_spot_exchange_info",
            self._native_params(
                product_symbol=product_symbol,
                symbols=symbols,
            ),
        )

    def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot orderbook depth."""
        return self._native_public(
            "get_spot_orderbook",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot recent trades."""
        return self._native_public(
            "get_spot_recent_trades",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_spot_agg_trades(
        self,
        product_symbol: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot aggregate trades."""
        return self._native_public(
            "get_spot_agg_trades",
            self._native_params(
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_spot_klines(
        self,
        product_symbol: str,
        interval: str = "1m",
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot candles."""
        return self._native_public(
            "get_spot_klines",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_spot_avg_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot current average price."""
        return self._native_public(
            "get_spot_avg_price",
            self._native_params(product_symbol=product_symbol),
        )

    def get_spot_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot 24h ticker."""
        return self._native_public(
            "get_spot_ticker_24hr",
            self._native_params(product_symbol=product_symbol),
        )

    def get_spot_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot price ticker."""
        return self._native_public(
            "get_spot_ticker_price",
            self._native_params(product_symbol=product_symbol),
        )

    def get_spot_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Spot best bid/ask ticker."""
        return self._native_public(
            "get_spot_book_ticker",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract server time."""
        return self._native_public("get_contract_time", [])

    def get_contract_details(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract metadata."""
        return self._native_public(
            "get_contract_details",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract ticker."""
        return self._native_public(
            "get_contract_ticker",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_depth(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract orderbook depth."""
        return self._native_public(
            "get_contract_depth",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_contract_depth_commits(
        self,
        product_symbol: str,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent MEXC Contract depth snapshots."""
        return self._native_public(
            "get_contract_depth_commits",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_contract_index_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract index price."""
        return self._native_public(
            "get_contract_index_price",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_fair_price(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract fair price."""
        return self._native_public(
            "get_contract_fair_price",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_funding_rate(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract current funding rate."""
        return self._native_public(
            "get_contract_funding_rate",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_kline(
        self,
        product_symbol: str,
        interval: str = "Min1",
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract candles."""
        return self._native_public(
            "get_contract_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start=start,
                end=end,
            ),
        )

    def get_contract_index_price_kline(
        self,
        product_symbol: str,
        interval: str = "Min1",
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract index-price candles."""
        return self._native_public(
            "get_contract_index_price_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start=start,
                end=end,
            ),
        )

    def get_contract_fair_price_kline(
        self,
        product_symbol: str,
        interval: str = "Min1",
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract fair-price candles."""
        return self._native_public(
            "get_contract_fair_price_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start=start,
                end=end,
            ),
        )

    def get_contract_deals(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract recent deals."""
        return self._native_public(
            "get_contract_deals",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_contract_risk_reverse(self, product_symbol: str) -> dict[str, Any] | list[Any]:
        """Retrieve a MEXC Contract risk fund balance."""
        return self._native_public(
            "get_contract_risk_reverse",
            self._native_params(product_symbol=product_symbol),
        )

    def get_contract_risk_reverse_history(
        self,
        product_symbol: str,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract risk fund balance history."""
        return self._native_public(
            "get_contract_risk_reverse_history",
            self._native_params(
                product_symbol=product_symbol,
                page_num=page_num,
                page_size=page_size,
            ),
        )

    def get_contract_funding_rate_history(
        self,
        product_symbol: str,
        page_num: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve MEXC Contract historical funding rates."""
        return self._native_public(
            "get_contract_funding_rate_history",
            self._native_params(
                product_symbol=product_symbol,
                page_num=page_num,
                page_size=page_size,
            ),
        )
