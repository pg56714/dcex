"""KuCoin Spot Market HTTP client."""

from typing import Any

from ...utils.common import Common
from ...utils.timeframe_utils import kucoin_convert_timeframe
from ._http_manager import HTTPManager
from .endpoints.market import SpotMarket


class MarketHTTP(HTTPManager):
    """
    HTTP client for KuCoin Spot Market API operations.

    This class provides methods for retrieving market data including
    instrument information, tickers, orderbook data, trade history,
    and candlestick/K-line data.
    """

    async def get_spot_instrument_info(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve trading instrument information.

        Returns:
            List of available trading instruments from KuCoin API.
        """
        payload: dict[str, Any] = {}
        res = await self._request(
            method="GET",
            path=SpotMarket.INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_ticker(
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

        res = await self._request(
            method="GET",
            path=SpotMarket.TICKER,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_all_tickers(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve ticker information for all trading pairs.

        Returns:
            Ticker information for all available trading pairs.
        """
        payload: dict[str, Any] = {}
        res = await self._request(
            method="GET",
            path=SpotMarket.ALL_TICKERS,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_orderbook(
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

        res = await self._request(
            method="GET",
            path=SpotMarket.ORDERBOOK,
            query=payload,
        )
        return res

    async def get_spot_public_trades(
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

        res = await self._request(
            method="GET",
            path=SpotMarket.PUBLIC_TRADES,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_kline(
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

        res = await self._request(
            method="GET",
            path=SpotMarket.KLINE,
            query=payload,
            signed=False,
        )
        return res
