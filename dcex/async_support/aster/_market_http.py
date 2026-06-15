"""Aster V3 public market-data async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import NativeResponse
from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import SpotMarket


class MarketHTTP(HTTPManager):
    """HTTP client for Aster V3 public market APIs."""

    async def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Aster public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Aster native client is required for public market methods.")
        status, headers, body = await self._native_client.public_request_async(method_name, params)
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
            if isinstance(value, list):
                params.extend((key, str(item)) for item in value)
            else:
                params.append((key, str(value)))
        return params

    def _symbol(self, product_symbol: str) -> str:
        if "-" not in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.ASTER, product_symbol)

    async def ping_spot(self) -> dict[str, Any] | list[Any]:
        """Test Aster spot API connectivity."""
        return await self._native_public("ping_spot", [])

    async def ping_futures(self) -> dict[str, Any] | list[Any]:
        """Test Aster futures API connectivity."""
        return await self._native_public("ping_futures", [])

    async def get_spot_server_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot server time."""
        return await self._native_public("get_spot_server_time", [])

    async def get_futures_server_time(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures server time."""
        return await self._native_public("get_futures_server_time", [])

    async def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot trading specifications."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_spot_exchange_info",
            self._params(product_symbol=symbol, symbols=symbols),
        )

    async def get_futures_exchange_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures trading specifications."""
        return await self._native_public("get_futures_exchange_info", [])

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot order-book depth."""
        return await self._native_public(
            "get_spot_orderbook",
            self._params(product_symbol=self._symbol(product_symbol), limit=limit),
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures order-book depth."""
        return await self._native_public(
            "get_futures_orderbook",
            self._params(product_symbol=self._symbol(product_symbol), limit=limit),
        )

    async def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent Aster spot trades."""
        return await self._native_public(
            "get_spot_recent_trades",
            self._params(product_symbol=self._symbol(product_symbol), limit=limit),
        )

    async def get_futures_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve recent Aster futures trades."""
        return await self._native_public(
            "get_futures_recent_trades",
            self._params(product_symbol=self._symbol(product_symbol), limit=limit),
        )

    async def get_spot_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        fromId: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve historical Aster spot trades."""
        return await self._native_public(
            "get_spot_historical_trades",
            self._params(product_symbol=self._symbol(product_symbol), limit=limit, fromId=fromId),
        )

    async def get_futures_historical_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        fromId: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve historical Aster futures trades."""
        return await self._native_public(
            "get_futures_historical_trades",
            self._params(product_symbol=self._symbol(product_symbol), limit=limit, fromId=fromId),
        )

    async def get_spot_agg_trades(
        self,
        product_symbol: str,
        fromId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve aggregate Aster spot trades."""
        return await self._native_public(
            "get_spot_agg_trades",
            self._params(
                product_symbol=self._symbol(product_symbol),
                fromId=fromId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_agg_trades(
        self,
        product_symbol: str,
        fromId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve aggregate Aster futures trades."""
        return await self._native_public(
            "get_futures_agg_trades",
            self._params(
                product_symbol=self._symbol(product_symbol),
                fromId=fromId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot candlesticks."""
        return await self._native_public(
            "get_spot_klines",
            self._params(
                product_symbol=self._symbol(product_symbol),
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures candlesticks."""
        return await self._native_public(
            "get_futures_klines",
            self._params(
                product_symbol=self._symbol(product_symbol),
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_index_price_klines(
        self,
        pair: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures index-price candlesticks."""
        return await self._native_public(
            "get_futures_index_price_klines",
            self._params(
                pair=pair,
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_mark_price_klines(
        self,
        product_symbol: str,
        interval: str,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures mark-price candlesticks."""
        return await self._native_public(
            "get_futures_mark_price_klines",
            self._params(
                product_symbol=self._symbol(product_symbol),
                interval=interval,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot 24-hour ticker data."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_spot_ticker_24hr",
            self._params(product_symbol=symbol),
        )

    async def get_futures_ticker_24hr(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures 24-hour ticker data."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_futures_ticker_24hr",
            self._params(product_symbol=symbol),
        )

    async def get_spot_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve latest Aster spot prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_spot_ticker_price",
            self._params(product_symbol=symbol),
        )

    async def get_futures_ticker_price(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve latest Aster futures prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_futures_ticker_price",
            self._params(product_symbol=symbol),
        )

    async def get_spot_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot best bid and ask prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_spot_book_ticker",
            self._params(product_symbol=symbol),
        )

    async def get_futures_book_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures best bid and ask prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_futures_book_ticker",
            self._params(product_symbol=symbol),
        )

    async def get_spot_commission_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve signed Aster spot commission rates."""
        return await self._request(
            "GET",
            SpotMarket.COMMISSION_RATE,
            {"symbol": self._symbol(product_symbol)},
        )

    async def get_spot_withdraw_fee(
        self,
        chainId: str,
        asset: str,
    ) -> dict[str, Any] | list[Any]:
        """Estimate the public Aster withdrawal fee without creating a withdrawal."""
        return await self._native_public(
            "get_spot_withdraw_fee",
            self._params(chainId=chainId, asset=asset),
        )

    async def get_futures_premium_index(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures mark and index prices."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_futures_premium_index",
            self._params(product_symbol=symbol),
        )

    async def get_futures_funding_rate(
        self,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures funding-rate history."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_futures_funding_rate",
            self._params(
                product_symbol=symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_funding_info(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures funding-rate configuration."""
        symbol = self._symbol(product_symbol) if product_symbol else None
        return await self._native_public(
            "get_futures_funding_info",
            self._params(product_symbol=symbol),
        )

    async def get_futures_index_references(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures index reference components."""
        return await self._native_public(
            "get_futures_index_references",
            self._params(product_symbol=self._symbol(product_symbol)),
        )
