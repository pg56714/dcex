from typing import Any, cast

from ..._native_http import NativeResponse
from ._http_manager import HTTPManager
from .enums import BinanceProductType


class AccountHTTP(HTTPManager):
    """HTTP client for Binance account-related API endpoints."""

    async def _native_private(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> Any:  # noqa: ANN401
        """Call a Rust-backed Binance private method and decode its JSON body."""
        if self._native_client is None:
            raise RuntimeError("Binance native client is required for private account methods.")
        status, headers, body = await self._native_client.private_request_async(method_name, params)
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
            if isinstance(value, bool):
                value = str(value).lower()
            params.append((key, str(value)))
        return params

    @staticmethod
    def _ensure_futures_listen_key(market_type: str) -> None:
        if str(market_type) == BinanceProductType.SPOT.value:
            raise NotImplementedError(
                "Binance Spot user data streams are subscribed through the WebSocket API."
            )

    async def get_account_balance(
        self,
        market_type: str,
    ) -> dict:
        """
        Get account balance.

        Args:
            market_type: Market type ("spot" or "swap")

        Returns:
            dict: Account balance information
        """
        return await self._native_private(
            "get_account_balance",
            self._params(market_type=str(market_type)),
        )

    async def get_income_history(
        self,
        product_symbol: str | None = None,
        incomeType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get futures income history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTCUSDT')
            incomeType: Income type (TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, etc.)
            startTime: Start time in milliseconds
            endTime: End time in milliseconds
            page: Page number for pagination
            limit: Number of records per page

        Returns:
            dict: Income history data
        """
        return await self._native_private(
            "get_income_history",
            self._params(
                product_symbol=product_symbol,
                incomeType=incomeType,
                startTime=startTime,
                endTime=endTime,
                page=page,
                limit=limit,
            ),
        )

    async def get_futures_account_info(self) -> dict:
        """
        Get futures account information, including balances and positions.

        Returns:
            dict: Futures account information.
        """
        return await self._native_private("get_futures_account_info", [])

    async def get_wallet_balance(
        self,
        quoteAsset: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get the estimated balance of every activated Binance wallet."""
        return cast(
            list[dict[str, Any]],
            await self._native_private(
                "get_wallet_balance",
                self._params(quoteAsset=quoteAsset),
            ),
        )

    async def get_funding_wallet(
        self,
        asset: str | None = None,
        needBtcValuation: bool | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get assets held in the Binance Funding Wallet."""
        return cast(
            list[dict[str, Any]],
            await self._native_private(
                "get_funding_wallet",
                self._params(asset=asset, needBtcValuation=needBtcValuation),
            ),
        )

    async def create_universal_transfer(
        self,
        type_: str,
        asset: str,
        amount: str,
        fromSymbol: str | None = None,
        toSymbol: str | None = None,
    ) -> dict:
        """Transfer an asset between Binance account wallets."""
        return await self._native_private(
            "create_universal_transfer",
            self._params(
                type=type_,
                asset=asset,
                amount=amount,
                fromSymbol=fromSymbol,
                toSymbol=toSymbol,
            ),
        )

    async def get_universal_transfer_history(
        self,
        type_: str,
        startTime: int | None = None,
        endTime: int | None = None,
        current: int | None = None,
        size: int | None = None,
        fromSymbol: str | None = None,
        toSymbol: str | None = None,
    ) -> dict:
        """Get Binance universal transfer records."""
        return await self._native_private(
            "get_universal_transfer_history",
            self._params(
                type=type_,
                startTime=startTime,
                endTime=endTime,
                current=current,
                size=size,
                fromSymbol=fromSymbol,
                toSymbol=toSymbol,
            ),
        )

    async def get_listen_key(self, market_type: str = BinanceProductType.SWAP) -> str:
        """
        Start a futures user data stream and return its listen key.

        Args:
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            str: User data stream listen key.
        """
        self._ensure_futures_listen_key(market_type)
        res = await self._native_private("create_futures_listen_key", [])
        return res["listenKey"]

    async def keep_alive_listen_key(
        self,
        listen_key: str,
        market_type: str = BinanceProductType.SWAP,
    ) -> dict:
        """
        Keep a futures user data stream alive.

        Args:
            listen_key: User data stream listen key.
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            dict: Binance response.
        """
        self._ensure_futures_listen_key(market_type)
        return await self._native_private(
            "keep_alive_futures_listen_key",
            self._params(listenKey=listen_key),
        )

    async def close_listen_key(
        self,
        listen_key: str,
        market_type: str = BinanceProductType.SWAP,
    ) -> dict:
        """
        Close a futures user data stream.

        Args:
            listen_key: User data stream listen key.
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            dict: Binance response.
        """
        self._ensure_futures_listen_key(market_type)
        return await self._native_private(
            "close_futures_listen_key",
            self._params(listenKey=listen_key),
        )
