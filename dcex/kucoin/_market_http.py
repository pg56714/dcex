"""KuCoin Spot Market HTTP client."""

from typing import Any

from ..utils.common import Common
from ..utils.timeframe_utils import kucoin_convert_timeframe
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket


def _kucoin_futures_granularity(timeframe: str) -> int:
    """Convert standard timeframe strings to KuCoin futures granularity seconds."""
    mapping = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "30m": 1800,
        "1h": 3600,
        "2h": 7200,
        "4h": 14400,
        "8h": 28800,
        "12h": 43200,
        "1d": 86400,
        "1w": 604800,
    }
    try:
        return mapping[timeframe]
    except KeyError as exc:
        raise ValueError("timeframe not supported") from exc


class MarketHTTP(HTTPManager):
    """
    HTTP client for KuCoin Spot Market API operations.

    This class provides methods for retrieving market data including
    instrument information, tickers, orderbook data, trade history,
    and candlestick/K-line data.
    """

    def get_spot_instrument_info(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve trading instrument information.

        Returns:
            List of available trading instruments from KuCoin API.
        """
        payload: dict[str, Any] = {}
        res = self._request(
            method="GET",
            path=SpotMarket.INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_ticker(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve single ticker information for a specific trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., "BTC-USDT-SPOT").

        Returns:
            Ticker information for the specified trading pair.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.TICKER,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_all_tickers(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve ticker information for all trading pairs.

        Returns:
            Ticker information for all available trading pairs.
        """
        payload: dict[str, Any] = {}
        res = self._request(
            method="GET",
            path=SpotMarket.ALL_TICKERS,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_orderbook(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve orderbook data for a specific trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., "BTC-USDT-SPOT").

        Returns:
            Orderbook data for the specified trading pair.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK,
            query=payload,
        )
        return res

    def get_spot_public_trades(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Retrieve public trade history for a specific trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., "BTC-USDT-SPOT").

        Returns:
            Public trade history for the specified trading pair.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }

        res = self._request(
            method="GET",
            path=SpotMarket.PUBLIC_TRADES,
            query=payload,
            signed=False,
        )
        return res

    def get_spot_kline(
        self,
        product_symbol: str,
        timeframe: str,
        startAt: int | None = None,
        endAt: int | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve candlestick/K-line data for a specific trading pair.

        Args:
            product_symbol: Trading pair symbol (e.g., "BTC-USDT-SPOT").
            timeframe: Timeframe type (e.g., "1m", "5m", "1h", "1d").
            startAt: Optional start time in milliseconds.
            endAt: Optional end time in milliseconds.

        Returns:
            Candlestick/K-line data for the specified trading pair and timeframe.
        """
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
            "type": kucoin_convert_timeframe(timeframe),
        }

        if startAt is not None:
            payload["startAt"] = startAt
        if endAt is not None:
            payload["endAt"] = endAt

        res = self._request(
            method="GET",
            path=SpotMarket.KLINE,
            query=payload,
            signed=False,
        )
        return res

    def get_futures_contracts(self) -> dict[str, Any]:
        """Retrieve active KuCoin futures contracts."""
        res = self._request(
            method="GET",
            path=FuturesMarket.CONTRACTS,
            signed=False,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_contract(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve one KuCoin futures contract."""
        exchange_symbol = self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol)
        res = self._request(
            method="GET",
            path=FuturesMarket.CONTRACT.format(symbol=exchange_symbol),
            signed=False,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_ticker(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve one KuCoin futures ticker."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }
        res = self._request(
            method="GET",
            path=FuturesMarket.TICKER,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_orderbook(
        self,
        product_symbol: str,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures orderbook."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }
        path = (
            FuturesMarket.PART_ORDERBOOK.format(size=depth)
            if depth is not None
            else FuturesMarket.ORDERBOOK
        )
        res = self._request(
            method="GET",
            path=path,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_public_trades(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures public trade history."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
        }
        res = self._request(
            method="GET",
            path=FuturesMarket.PUBLIC_TRADES,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_kline(
        self,
        product_symbol: str,
        timeframe: str,
        from_: int | None = None,
        to: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures candlestick/K-line data."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
            "granularity": _kucoin_futures_granularity(timeframe),
        }
        if from_ is not None:
            payload["from"] = from_
        if to is not None:
            payload["to"] = to

        res = self._request(
            method="GET",
            path=FuturesMarket.KLINE,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )
        return res

    def get_futures_open_interest(
        self,
        product_symbol: str,
        interval: str = "5min",
        startAt: int | None = None,
        endAt: int | None = None,
        pageSize: int | None = None,
    ) -> dict[str, Any]:
        """Get futures open interest history."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KUCOIN, product_symbol),
            "interval": interval,
        }
        if startAt is not None:
            payload["startAt"] = startAt
        if endAt is not None:
            payload["endAt"] = endAt
        if pageSize is not None:
            payload["pageSize"] = pageSize

        res = self._request(
            method="GET",
            path=FuturesMarket.OPEN_INTEREST,
            query=payload,
            signed=False,
        )
        return res
