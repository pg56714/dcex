from ...utils.common import Common
from ...utils.timeframe_utils import bybit_convert_timeframe
from ._http_manager import HTTPManager
from .endpoints.market import SpotMarket


class MarketHTTP(HTTPManager):
    """HTTP client for Ascendex market data API endpoints."""

    async def get_spot_instrument_info(self) -> dict:
        """
        Get spot trading instrument information.

        Returns:
            dict: Instrument information including symbols, status, and specifications
        """
        payload = {}
        res = await self._request(
            method="GET",
            path=SpotMarket.INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get spot ticker information.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT'). If None, returns all tickers.

        Returns:
            dict: Ticker information including price, volume, and 24h change
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol)

        res = await self._request(
            method="GET",
            path=SpotMarket.TICKER,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        to_timestamp: int | None = None,
        from_timestamp: int | None = None,
        n: int | None = None,
    ) -> dict:
        """
        Get spot kline/candlestick data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Time interval (e.g., '1m', '5m', '1h', '1d')
            to_timestamp: End time in milliseconds (optional)
            from_timestamp: Start time in milliseconds (optional)
            n: Number of klines to retrieve (optional)

        Returns:
            dict: Kline data including OHLCV (Open, High, Low, Close, Volume)
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
            "interval": bybit_convert_timeframe(interval),
        }
        if to_timestamp is not None:
            payload["to"] = str(to_timestamp)
        if from_timestamp is not None:
            payload["from"] = str(from_timestamp)
        if n is not None:
            payload["n"] = str(n)

        res = await self._request(
            method="GET",
            path=SpotMarket.KLINE,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_orderbook(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Get spot order book data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            dict: Order book data including bids and asks
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_public_trade(
        self,
        product_symbol: str,
        n: int | None = None,
    ) -> dict:
        """
        Get spot public trade history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            n: Number of trades to retrieve (optional)

        Returns:
            dict: Recent public trade data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.ASCENDEX, product_symbol),
        }
        if n is not None:
            payload["n"] = str(n)

        res = await self._request(
            method="GET",
            path=SpotMarket.PUBLIC_TRADE,
            query=payload,
            signed=False,
        )
        return res
