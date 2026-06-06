from typing import Any, cast

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import FuturesAccount, SpotAccount, WalletAsset
from .enums import BinanceProductType


class AccountHTTP(HTTPManager):
    """HTTP client for Binance account-related API endpoints."""

    def _listen_key_path(self, market_type: str) -> FuturesAccount:
        if str(market_type) == BinanceProductType.SPOT.value:
            raise NotImplementedError(
                "Binance Spot user data streams are subscribed through the WebSocket API."
            )
        return FuturesAccount.USER_DATA_STREAM

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
        res = await self._request(
            method="GET",
            path=SpotAccount.ACCOUNT_BALANCE
            if market_type == BinanceProductType.SPOT
            else FuturesAccount.ACCOUNT_BALANCE,
            query={},
        )
        return res

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
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINANCE, product_symbol)
        if incomeType is not None:
            payload["incomeType"] = incomeType
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if page is not None:
            payload["page"] = page
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=FuturesAccount.INCOME_HISTORY,
            query=payload,
        )
        return res

    async def get_futures_account_info(self) -> dict:
        """
        Get futures account information, including balances and positions.

        Returns:
            dict: Futures account information.
        """
        res = await self._request(
            method="GET",
            path=FuturesAccount.ACCOUNT_INFO,
            query={},
        )
        return res

    async def get_wallet_balance(
        self,
        quoteAsset: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get the estimated balance of every activated Binance wallet."""
        payload = {}
        if quoteAsset is not None:
            payload["quoteAsset"] = quoteAsset
        return cast(
            list[dict[str, Any]],
            await self._request(
                method="GET",
                path=WalletAsset.WALLET_BALANCE,
                query=payload,
            ),
        )

    async def get_funding_wallet(
        self,
        asset: str | None = None,
        needBtcValuation: bool | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get assets held in the Binance Funding Wallet."""
        payload = {}
        if asset is not None:
            payload["asset"] = asset
        if needBtcValuation is not None:
            payload["needBtcValuation"] = (
                str(needBtcValuation).lower()
                if isinstance(needBtcValuation, bool)
                else needBtcValuation
            )
        return cast(
            list[dict[str, Any]],
            await self._request(
                method="POST",
                path=WalletAsset.FUNDING_WALLET,
                query=payload,
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
        payload = {
            "type": type_,
            "asset": asset,
            "amount": amount,
        }
        if fromSymbol is not None:
            payload["fromSymbol"] = fromSymbol
        if toSymbol is not None:
            payload["toSymbol"] = toSymbol
        return await self._request(
            method="POST",
            path=WalletAsset.UNIVERSAL_TRANSFER,
            query=payload,
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
        payload: dict[str, Any] = {"type": type_}
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if current is not None:
            payload["current"] = current
        if size is not None:
            payload["size"] = size
        if fromSymbol is not None:
            payload["fromSymbol"] = fromSymbol
        if toSymbol is not None:
            payload["toSymbol"] = toSymbol
        return await self._request(
            method="GET",
            path=WalletAsset.UNIVERSAL_TRANSFER,
            query=payload,
        )

    async def get_listen_key(self, market_type: str = BinanceProductType.SWAP) -> str:
        """
        Start a futures user data stream and return its listen key.

        Args:
            market_type: Market type. Only "swap" is supported by this REST endpoint.

        Returns:
            str: User data stream listen key.
        """
        path = self._listen_key_path(market_type)
        res = await self._request(method="POST", path=path, query={}, signed=False)
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
        path = self._listen_key_path(market_type)
        return await self._request(
            method="PUT",
            path=path,
            query={"listenKey": listen_key},
            signed=False,
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
        path = self._listen_key_path(market_type)
        return await self._request(
            method="DELETE",
            path=path,
            query={"listenKey": listen_key},
            signed=False,
        )
