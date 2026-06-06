"""Kraken public market-data HTTP client."""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import FuturesMarket, SpotMarket


class MarketHTTP(HTTPManager):
    """HTTP client for Kraken public market-data APIs."""

    def get_server_time(self) -> dict[str, Any]:
        """Retrieve Kraken spot server time."""
        return self._request("GET", SpotMarket.SERVER_TIME, signed=False)

    def get_spot_asset_pairs(
        self,
        pair: str | None = None,
        info: str = "info",
    ) -> dict[str, Any]:
        """Retrieve Kraken spot tradable asset pairs."""
        payload: dict[str, Any] = {"pair": pair, "info": info}
        return self._request("GET", SpotMarket.ASSET_PAIRS, query=payload, signed=False)

    def get_spot_ticker(
        self,
        product_symbol: str | None = None,
        pair: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot ticker data for one pair or all pairs."""
        if product_symbol is not None and pair is not None:
            raise ValueError("Specify either product_symbol or pair, not both.")
        resolved_pair = (
            self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol)
            if product_symbol is not None
            else pair
        )
        payload: dict[str, Any] = {"pair": resolved_pair}
        return self._request("GET", SpotMarket.TICKER, query=payload, signed=False)

    def get_spot_orderbook(
        self,
        product_symbol: str,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot orderbook data."""
        payload: dict[str, Any] = {
            "pair": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
            "count": count,
        }
        return self._request("GET", SpotMarket.ORDERBOOK, query=payload, signed=False)

    def get_spot_public_trades(
        self,
        product_symbol: str,
        since: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot public trades."""
        payload: dict[str, Any] = {
            "pair": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
            "since": since,
        }
        return self._request("GET", SpotMarket.PUBLIC_TRADES, query=payload, signed=False)

    def get_spot_kline(
        self,
        product_symbol: str,
        interval: int = 1,
        since: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot OHLC candles."""
        payload: dict[str, Any] = {
            "pair": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
            "interval": interval,
            "since": since,
        }
        return self._request("GET", SpotMarket.OHLC, query=payload, signed=False)

    def get_futures_instruments(
        self,
        contractType: str | list[str] | None = None,
        expired: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures instruments."""
        payload: dict[str, Any] = {"contractType": contractType, "expired": expired}
        return self._request(
            "GET",
            FuturesMarket.INSTRUMENTS,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )

    def get_futures_tickers(
        self,
        product_symbol: str | None = None,
        contractType: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures ticker data for one symbol or all symbols."""
        symbol = (
            self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol)
            if product_symbol is not None
            else None
        )
        payload: dict[str, Any] = {"symbol": symbol, "contractType": contractType}
        return self._request(
            "GET",
            FuturesMarket.TICKERS,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )

    def get_futures_orderbook(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures orderbook data."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
        }
        return self._request(
            "GET",
            FuturesMarket.ORDERBOOK,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )

    def get_futures_public_trades(
        self,
        product_symbol: str,
        lastTime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures recent public trade history."""
        payload: dict[str, Any] = {
            "symbol": self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol),
            "lastTime": lastTime,
        }
        return self._request(
            "GET",
            FuturesMarket.PUBLIC_TRADES,
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )

    def get_futures_kline(
        self,
        product_symbol: str,
        timeframe: str,
        tick_type: str = "trade",
        from_: int | None = None,
        to: int | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures chart candles."""
        exchange_symbol = self.ptm.get_exchange_symbol(Common.KRAKEN, product_symbol)
        payload: dict[str, Any] = {"from": from_, "to": to, "count": count}
        return self._request(
            "GET",
            FuturesMarket.CANDLES.format(
                tick_type=tick_type,
                symbol=exchange_symbol,
                resolution=timeframe,
            ),
            query=payload,
            signed=False,
            base_url=self.futures_base_url,
        )
