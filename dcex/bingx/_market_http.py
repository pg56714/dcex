"""BingX market HTTP client backed by Rust."""

from typing import Any

from .._native_http import request_native_json
from ._http_manager import HTTPManager


class MarketHTTP(HTTPManager):
    """HTTP client for BingX market-related API endpoints."""

    def _native_public(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed BingX public method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("BingX native client is required for public market methods.")
        response, data = request_native_json(
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
            params.append((key, str(value)))
        return params

    def get_swap_instrument_info(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get swap instrument information."""
        return self._native_public(
            "get_swap_instrument_info",
            self._native_params(product_symbol=product_symbol),
        )

    def get_spot_instrument_info(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get spot instrument information."""
        return self._native_public(
            "get_spot_instrument_info",
            self._native_params(product_symbol=product_symbol),
        )

    def get_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get order book data."""
        return self._native_public(
            "get_orderbook",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_spot_orderbook(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get spot order book data."""
        return self._native_public(
            "get_spot_orderbook",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_spot_orderbook_v2(
        self,
        product_symbol: str,
        depth: int,
        type_: str = "step0",
    ) -> dict:
        """Get spot v2 aggregated order book data; BingX requires ``depth``."""
        return self._native_public(
            "get_spot_orderbook_v2",
            self._native_params(
                product_symbol=product_symbol,
                depth=depth,
                type_=type_,
            ),
        )

    def get_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get public trade data."""
        return self._native_public(
            "get_public_trades",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_spot_public_trades(
        self,
        product_symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Get spot public trade data."""
        return self._native_public(
            "get_spot_public_trades",
            self._native_params(product_symbol=product_symbol, limit=limit),
        )

    def get_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get kline/candlestick data."""
        return self._native_public(
            "get_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    def get_spot_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get spot kline/candlestick data."""
        return self._native_public(
            "get_spot_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    def get_spot_kline_v2(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get spot v2 kline/candlestick data."""
        return self._native_public(
            "get_spot_kline_v2",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    def get_open_interest(self, product_symbol: str) -> dict:
        """Get swap open interest."""
        return self._native_public(
            "get_open_interest",
            self._native_params(product_symbol=product_symbol),
        )

    def get_mark_price_kline(
        self,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Get swap mark price kline data."""
        return self._native_public(
            "get_mark_price_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    def get_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get 24hr ticker price change statistics."""
        return self._native_public(
            "get_ticker",
            self._native_params(product_symbol=product_symbol),
        )

    def get_swap_premium_index(self, product_symbol: str | None = None) -> dict[str, Any]:
        """Get perpetual mark/index prices and premium."""
        return self._native_public(
            "get_swap_premium_index", self._native_params(product_symbol=product_symbol)
        )

    def get_swap_funding_rate(
        self,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get perpetual funding rates."""
        return self._native_public(
            "get_swap_funding_rate",
            self._native_params(
                product_symbol=product_symbol,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    def get_swap_book_ticker(self, product_symbol: str) -> dict[str, Any]:
        """Get the perpetual best bid and ask."""
        return self._native_public(
            "get_swap_book_ticker", self._native_params(product_symbol=product_symbol)
        )

    def get_swap_trading_rules(self, product_symbol: str) -> dict[str, Any]:
        """Get perpetual minimums and price protection rules."""
        return self._native_public(
            "get_swap_trading_rules", self._native_params(product_symbol=product_symbol)
        )

    def get_spot_ticker(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """Get spot 24hr ticker statistics."""
        return self._native_public(
            "get_spot_ticker",
            self._native_params(product_symbol=product_symbol),
        )

    def get_spot_book_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot best bid/ask ticker."""
        return self._native_public(
            "get_spot_book_ticker",
            self._native_params(product_symbol=product_symbol),
        )

    def get_spot_price_ticker(
        self,
        product_symbol: str,
    ) -> dict:
        """Get spot latest price ticker."""
        return self._native_public(
            "get_spot_price_ticker",
            self._native_params(product_symbol=product_symbol),
        )

    def get_coin_swap_contracts(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/market/contracts.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-market/api-reference.md

        """
        return self._native_public(
            "get_coin_swap_contracts",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_coin_swap_orderbook(
        self, *, product_symbol: str, limit: int | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/market/depth.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-market/api-reference.md

        """
        return self._native_public(
            "get_coin_swap_orderbook",
            self._native_params(product_symbol=product_symbol, limit=limit, recvWindow=recv_window),
        )

    def get_coin_swap_kline(
        self,
        *,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/market/klines.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-market/api-reference.md

        """
        return self._native_public(
            "get_coin_swap_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_coin_swap_premium_index(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/market/premiumIndex.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-market/api-reference.md

        """
        return self._native_public(
            "get_coin_swap_premium_index",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_coin_swap_open_interest(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/market/openInterest.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-market/api-reference.md

        """
        return self._native_public(
            "get_coin_swap_open_interest",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_coin_swap_ticker(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """

        GET /openApi/cswap/v1/market/ticker.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/cswap-market/api-reference.md

        """
        return self._native_public(
            "get_coin_swap_ticker",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_spot_historical_kline(
        self,
        *,
        product_symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """

        GET /openApi/market/his/v1/kline.

        Source:
        https://github.com/BingX-API/api-ai-skills/blob/main/skills/spot-market/api-reference.md

        """
        return self._native_public(
            "get_spot_historical_kline",
            self._native_params(
                product_symbol=product_symbol,
                interval=interval,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                recvWindow=recv_window,
            ),
        )

    def get_swap_server_time(self) -> dict[str, Any]:
        """Get USD-M server time without authentication or a client timestamp."""
        return self._native_public("get_swap_server_time", [])

    def get_swap_price_ticker(
        self, *, product_symbol: str | None = None, recv_window: int | None = None
    ) -> dict[str, Any]:
        """Get the USD-M last price for one or all symbols."""
        return self._native_public(
            "get_swap_price_ticker",
            self._native_params(product_symbol=product_symbol, recvWindow=recv_window),
        )

    def get_spot_historical_trades(
        self,
        *,
        product_symbol: str,
        limit: int | None = None,
        from_id: str | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/market/his/v1/trade. Timestamps use milliseconds."""
        return self._native_public(
            "get_spot_historical_trades",
            self._native_params(
                product_symbol=product_symbol, limit=limit, fromId=from_id, recvWindow=recv_window
            ),
        )

    def get_swap_historical_trades(
        self,
        *,
        product_symbol: str,
        from_id: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """GET /openApi/swap/v1/market/historicalTrades. Timestamps use milliseconds."""
        return self._native_public(
            "get_swap_historical_trades",
            self._native_params(
                product_symbol=product_symbol, fromId=from_id, limit=limit, recvWindow=recv_window
            ),
        )

    def get_spot_server_time(self) -> Any:  # noqa: ANN401
        """
        Get the spot server time; the server returns its native timestamp unit.
        """
        return self._native_public("get_spot_server_time", [])
