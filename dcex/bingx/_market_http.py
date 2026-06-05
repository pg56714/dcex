"""BingX market HTTP client."""

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import SpotMarket, SwapMarket


class MarketHTTP(HTTPManager):
    """HTTP client for BingX market-related API endpoints."""

    def get_swap_instrument_info(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get swap instrument information.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Instrument information data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = self._request(
            method="GET",
            path=SwapMarket.INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_instrument_info(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get spot instrument information."""
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = self._request(
            method="GET",
            path=SpotMarket.SYMBOLS,
            query=payload,
            signed=False,
        )
        return res

    def get_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """
        Get order book data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            limit: Order book depth (5, 10, 20, 50, 100, 500, 1000)

        Returns:
            dict: Order book data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SwapMarket.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get spot order book data."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_orderbook_v2(
        self,
        product_symbol: str,
        limit: int | None = None,
        type_: str = "step0",
    ) -> dict:
        """Get spot v2 order book data."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "type": type_,
        }
        if limit is not None:
            payload["depth"] = str(limit)

        res = self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK_V2,
            query=payload,
            signed=False,
        )
        return res

    def get_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """
        Get public trade data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            limit: Number of trades to return

        Returns:
            dict: Public trade data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SwapMarket.PUBLIC_TRADE,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_public_trades(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot public trade data."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.PUBLIC_TRADE,
            query=payload,
            signed=False,
        )
        return res

    def get_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get kline/candlestick data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of klines to return

        Returns:
            dict: Kline data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "interval": interval,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SwapMarket.KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get spot kline/candlestick data."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "interval": interval,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SpotMarket.KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_kline_v2(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get spot v2 kline/candlestick data."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "interval": interval,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SpotMarket.KLINE_V2,
            query=payload,
            signed=False,
        )
        return res

    def get_open_interest(self, product_symbol: str) -> dict:
        """
        Get swap open interest.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Open interest data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SwapMarket.OPEN_INTEREST,
            query=payload,
            signed=False,
        )
        return res

    def get_mark_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get swap mark price kline data.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            interval: Kline interval
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of klines to return

        Returns:
            dict: Mark price kline data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "interval": interval,
        }
        if start_time is not None:
            payload["startTime"] = str(start_time)
        if end_time is not None:
            payload["endTime"] = str(end_time)
        if limit is not None:
            payload["limit"] = str(limit)

        res = self._request(
            method="GET",
            path=SwapMarket.MARK_PRICE_KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get 24hr ticker price change statistics.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Ticker data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = self._request(
            method="GET",
            path=SwapMarket.TICKER,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot 24hr ticker statistics."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.TICKER,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_book_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot best bid/ask ticker."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.BOOK_TICKER,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_price_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot latest price ticker."""
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.PRICE_TICKER,
            query=payload,
            signed=False,
        )
        return res
