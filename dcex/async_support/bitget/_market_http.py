"""Bitget public market-data async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """Async HTTP client for Bitget public market-data APIs."""

    async def get_spot_coins(self, coin: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot coin metadata."""
        return await self._request("GET", SpotMarket.COINS, {"coin": coin}, signed=False)

    async def get_spot_symbols(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot symbol metadata."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request("GET", SpotMarket.SYMBOLS, {"symbol": symbol}, signed=False)

    async def get_spot_tickers(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Retrieve Bitget spot ticker data."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request("GET", SpotMarket.TICKERS, {"symbol": symbol}, signed=False)

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        type_: str = "step0",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot orderbook depth."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "type": type_,
            "limit": limit,
        }
        return await self._request("GET", SpotMarket.ORDERBOOK, payload, signed=False)

    async def get_spot_kline(
        self,
        product_symbol: str,
        granularity: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot candles."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "granularity": granularity,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
        }
        return await self._request("GET", SpotMarket.CANDLES, payload, signed=False)

    async def get_spot_history_kline(
        self,
        product_symbol: str,
        granularity: str,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot candles."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "granularity": granularity,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
        }
        return await self._request("GET", SpotMarket.HISTORY_CANDLES, payload, signed=False)

    async def get_spot_recent_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget recent spot trades."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "limit": limit,
        }
        return await self._request("GET", SpotMarket.RECENT_TRADES, payload, signed=False)

    async def get_spot_market_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical spot market trades."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "limit": limit,
            "idLessThan": idLessThan,
            "startTime": startTime,
            "endTime": endTime,
        }
        return await self._request("GET", SpotMarket.MARKET_TRADES, payload, signed=False)

    async def get_futures_contracts(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures contract metadata."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "GET",
            FuturesMarket.CONTRACTS,
            {"symbol": symbol, "productType": productType},
            signed=False,
        )

    async def get_futures_ticker(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures ticker for one symbol."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
        }
        return await self._request("GET", FuturesMarket.TICKER, payload, signed=False)

    async def get_futures_tickers(self, productType: str = "USDT-FUTURES") -> dict[str, Any]:
        """Retrieve Bitget futures tickers."""
        return await self._request(
            "GET",
            FuturesMarket.TICKERS,
            {"productType": productType},
            signed=False,
        )

    async def get_futures_orderbook(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        precision: str = "scale0",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures orderbook depth."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "precision": precision,
            "limit": limit,
        }
        return await self._request("GET", FuturesMarket.ORDERBOOK, payload, signed=False)

    async def get_futures_kline(
        self,
        product_symbol: str,
        granularity: str,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures candles."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "granularity": granularity,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
        }
        return await self._request("GET", FuturesMarket.CANDLES, payload, signed=False)

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
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "granularity": granularity,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
        }
        return await self._request("GET", FuturesMarket.HISTORY_CANDLES, payload, signed=False)

    async def get_futures_recent_trades(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget recent futures trades."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "limit": limit,
        }
        return await self._request("GET", FuturesMarket.RECENT_TRADES, payload, signed=False)

    async def get_futures_current_funding_rate(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget current futures funding rate."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.BITGET, product_symbol)
            if product_symbol is not None
            else None
        )
        return await self._request(
            "GET",
            FuturesMarket.CURRENT_FUNDING_RATE,
            {"symbol": symbol, "productType": productType},
            signed=False,
        )

    async def get_futures_history_funding_rate(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        pageSize: int | None = None,
        pageNo: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget historical futures funding rates."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
            "pageSize": pageSize,
            "pageNo": pageNo,
        }
        return await self._request("GET", FuturesMarket.HISTORY_FUNDING_RATE, payload, signed=False)

    async def get_futures_open_interest(
        self,
        product_symbol: str,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve Bitget futures open interest."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITGET, product_symbol),
            "productType": productType,
        }
        return await self._request("GET", FuturesMarket.OPEN_INTEREST, payload, signed=False)
