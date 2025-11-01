from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket
from .enums import BinanceProductType


class MarketHTTP(HTTPManager):
    """HTTP client for Binance market data API endpoints."""

    async def get_spot_exchange_info(
        self,
        product_symbol: str | None = None,
        product_symbols: list | None = None,
        symbolStatus: str | None = None,
    ) -> dict:
        """
        Get spot exchange information.

        Args:
            product_symbol: Single trading pair symbol (e.g., 'BTCUSDT')
            product_symbols: List of trading pair symbols
            symbolStatus: Symbol status filter (TRADING, HALT, BREAK)

        Returns:
            dict: Exchange information including symbols, filters, and trading rules
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if product_symbols is not None:
            formatted_symbols = [
                self.ptm.get_exchange_symbol(Common.BINANCE, symbol) for symbol in product_symbols
            ]
            payload["symbols"] = str(formatted_symbols).replace("'", '"')
        if symbolStatus is not None:
            payload["symbolStatus"] = symbolStatus

        res = await self._request(
            method="GET",
            path=SpotMarket.EXCHANGE_INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """
        Get spot order book data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            limit: Number of orders to return (5, 10, 20, 50, 100, 500, 1000, 5000)

        Returns:
            dict: Order book data including bids and asks
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)
        res = await self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """
        Get recent spot trades.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            limit: Number of trades to return (max 1000)

        Returns:
            dict: Recent trade data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=SpotMarket.TRADES,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_price(
        self,
        product_symbol: str | None = None,
        product_symbols: list | None = None,
    ) -> dict:
        """
        Get spot price information.

        Args:
            product_symbol: Single trading pair symbol (e.g., 'BTCUSDT')
            product_symbols: List of trading pair symbols

        Returns:
            dict: Price information
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if product_symbols is not None:
            formatted_symbols = [
                self.ptm.get_exchange_symbol(Common.BINANCE, symbol) for symbol in product_symbols
            ]
            payload["symbols"] = str(formatted_symbols).replace("'", '"')

        res = await self._request(
            method="GET",
            path=SpotMarket.PRICE,
            query=payload,
            signed=False,
        )
        return res

    async def get_klines(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get kline/candlestick data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Time interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            start_time: Start time in milliseconds
            limit: Number of klines to return (max 1000)

        Returns:
            dict: Kline data including OHLCV
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol),
            "interval": interval,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=SpotMarket.KLINES
            if self.ptm.get_exchange_type(Common.BINANCE, product_symbol=product_symbol)
            == BinanceProductType.SPOT
            else FuturesMarket.KLINES,
            query=payload,
            signed=False,
        )
        return res

    async def get_futures_exchange_info(
        self,
    ) -> dict:
        """
        Get futures exchange information.

        Returns:
            dict: Futures exchange information including symbols and trading rules
        """
        res = await self._request(
            method="GET",
            path=FuturesMarket.EXCHANGE_INFO,
            query={},
            signed=False,
        )
        return res

    async def get_futures_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get futures ticker information.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Futures ticker data including price and volume
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)

        res = await self._request(
            method="GET",
            path=FuturesMarket.BOOK_TICKER,
            query=payload,
            signed=False,
        )
        return res

    async def get_futures_premium_index(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get futures premium index.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Premium index data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)

        res = await self._request(
            method="GET",
            path=FuturesMarket.PREMIUM_INDEX,
            query=payload,
            signed=False,
        )
        return res

    async def get_futures_funding_rate(
        self,
        product_symbol: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get futures funding rate history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            startTime: Start time in milliseconds
            endTime: End time in milliseconds
            limit: Number of records to return (max 1000)

        Returns:
            dict: Funding rate history data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=FuturesMarket.FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res
