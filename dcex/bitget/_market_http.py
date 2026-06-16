"""Bitget public market-data HTTP client backed by Rust."""

from typing import Any

from .._native_http import NativeResponse
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
        status, headers, body = self._native_client.public_request(method_name, params)
        response = NativeResponse(status, dict(headers), bytes(body))
        self._store_response_headers(response)
        return response.json()

    @staticmethod
    def _params(**kwargs: object) -> list[tuple[str, str]]:
        """Convert optional Python arguments into native string pairs."""
        params: list[tuple[str, str]] = []
        for key, value in kwargs.items():
            if value is None:
                continue
            params.append((key, str(value)))
        return params

    def get_spot_coins(self, coin: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot coin metadata."""
        return self._native_public("get_spot_coins", self._params(coin=coin))

    def get_spot_symbols(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot symbol metadata."""
        return self._native_public(
            "get_spot_symbols",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
            ),
        )

    def get_spot_tickers(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot ticker data."""
        return self._native_public(
            "get_spot_tickers",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
            ),
        )

    def get_spot_orderbook(
        self,
        product_symbol: str,
        type_: str = "step0",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot orderbook depth."""
        return self._native_public(
            "get_spot_orderbook",
            self._params(
                product_symbol=product_symbol,
                type=type_,
                limit=limit,
            ),
        )

    def get_spot_kline(
        self,
        product_symbol: str,
        granularity: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot candles."""
        return self._native_public(
            "get_spot_kline",
            self._params(
                product_symbol=product_symbol,
                granularity=granularity,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_spot_history_kline(
        self,
        product_symbol: str,
        granularity: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot candles."""
        return self._native_public(
            "get_spot_history_kline",
            self._params(
                product_symbol=product_symbol,
                granularity=granularity,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget recent spot trades."""
        return self._native_public(
            "get_spot_recent_trades",
            self._params(product_symbol=product_symbol, limit=limit),
        )

    def get_spot_market_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot market trades."""
        return self._native_public(
            "get_spot_market_trades",
            self._params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_futures_contracts(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures contract metadata."""
        return self._native_public(
            "get_futures_contracts",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
                productType=productType,
            ),
        )

    def get_futures_ticker(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures ticker for one symbol."""
        return self._native_public(
            "get_futures_ticker",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
            ),
        )

    def get_futures_tickers(self, productType: str = "USDT-FUTURES") -> dict[str, Any]:
        """Retrieve Bitget futures tickers."""
        return self._native_public(
            "get_futures_tickers",
            self._params(productType=productType),
        )

    def get_futures_orderbook(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        precision: str = "scale0",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures orderbook depth."""
        return self._native_public(
            "get_futures_orderbook",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                precision=precision,
                limit=limit,
            ),
        )

    def get_futures_kline(
        self,
        product_symbol: str,
        granularity: str,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures candles."""
        return self._native_public(
            "get_futures_kline",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                granularity=granularity,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_futures_history_kline(
        self,
        product_symbol: str,
        granularity: str,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical futures candles."""
        return self._native_public(
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

    def get_futures_recent_trades(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget recent futures trades."""
        return self._native_public(
            "get_futures_recent_trades",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                limit=limit,
            ),
        )

    def get_futures_current_funding_rate(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget current futures funding rate."""
        return self._native_public(
            "get_futures_current_funding_rate",
            self._params(
                product_symbol=product_symbol if product_symbol is not None else None,
                productType=productType,
            ),
        )

    def get_futures_history_funding_rate(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        pageSize: int | None = None,
        pageNo: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical futures funding rates."""
        return self._native_public(
            "get_futures_history_funding_rate",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
                pageSize=pageSize,
                pageNo=pageNo,
            ),
        )

    def get_futures_open_interest(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures open interest."""
        return self._native_public(
            "get_futures_open_interest",
            self._params(
                product_symbol=product_symbol,
                productType=productType,
            ),
        )
