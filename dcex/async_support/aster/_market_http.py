"""Aster V3 public market-data async HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ...utils.common import Common
from ._http_manager import HTTPManager


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
            if isinstance(value, list):
                params.extend((key, str(item)) for item in value)
            else:
                params.append((key, str(value)))
        return params

    def _symbol(self, product_symbol: str) -> str:
        if "-" not in product_symbol:
            return product_symbol
        ptm = getattr(self, "ptm", None)
        if ptm is None:
            return product_symbol
        return ptm.get_exchange_symbol(Common.ASTER, product_symbol)

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

    async def get_spot_exchange_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot trading specifications."""
        return await self._native_public("get_spot_exchange_info", [])

    async def get_futures_exchange_info(self) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures trading specifications."""
        return await self._native_public("get_futures_exchange_info", [])

    async def get_futures_remaining_openable_notional(
        self, product_symbol: str, leverage: int
    ) -> dict[str, Any] | list[Any]:
        """Get the symbol-wide remaining openable notional at a leverage tier."""
        return await self._native_public(
            "get_futures_remaining_openable_notional",
            self._params(product_symbol=self._symbol(product_symbol), leverage=leverage),
        )

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
        """
        Retrieve Aster futures index-price candlesticks.

        The official Aster V3 docs flag this path as unverified against the
        current server and mention an undocumented ``/fapi/v3/marketKlines``
        alternative; confirm availability before relying on it.
        """
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
        """
        Retrieve Aster futures mark-price candlesticks.

        The official Aster V3 docs flag this path as unverified against the
        current server and mention an undocumented ``/fapi/v3/marketKlines``
        alternative; confirm availability before relying on it.
        """
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
        return await self._native_private(
            "get_spot_commission_rate",
            self._native_params(product_symbol=product_symbol),
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

    async def get_asset_logos(self) -> dict[str, Any] | list[Any]:
        """GET /fapi/v3/common/asset/all-asset-logo."""
        return await self._native_public("get_asset_logos", self._native_params())

    async def get_prediction_ping(self) -> dict[str, Any] | list[Any]:
        """GET /api/v3/ping on the prediction host. Use native prediction symbols."""
        return await self._native_public("get_prediction_ping", self._native_params())

    async def get_prediction_time(self) -> dict[str, Any] | list[Any]:
        """GET /api/v3/time on the prediction host. Use native prediction symbols."""
        return await self._native_public("get_prediction_time", self._native_params())

    async def get_prediction_exchange_info(self) -> dict[str, Any] | list[Any]:
        """
        GET /api/v3/prediction/exchangeInfo on the prediction host. Use native prediction
        symbols.
        """
        return await self._native_public("get_prediction_exchange_info", self._native_params())

    async def get_prediction_depth(
        self, *, symbol: str, limit: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/depth on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_depth", self._native_params(symbol=symbol, limit=limit)
        )

    async def get_prediction_trades(
        self, *, symbol: str, limit: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/trades on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_trades", self._native_params(symbol=symbol, limit=limit)
        )

    async def get_prediction_historical_trades(
        self, *, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/historicalTrades on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_historical_trades",
            self._native_params(symbol=symbol, limit=limit, fromId=from_id),
        )

    async def get_prediction_agg_trades(
        self,
        *,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/aggTrades on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_agg_trades",
            self._native_params(
                symbol=symbol, fromId=from_id, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    async def get_prediction_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/klines on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_klines",
            self._native_params(
                symbol=symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_prediction_ticker_24hr(
        self, *, symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/ticker/24hr on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_ticker_24hr", self._native_params(symbol=symbol)
        )

    async def get_prediction_ticker_price(
        self, *, symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/ticker/price on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_ticker_price", self._native_params(symbol=symbol)
        )

    async def get_prediction_ticker_book_ticker(
        self, *, symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/ticker/bookTicker on the prediction host. Use native prediction symbols."""
        return await self._native_public(
            "get_prediction_ticker_book_ticker", self._native_params(symbol=symbol)
        )
