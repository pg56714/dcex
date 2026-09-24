"""Binance Convert API methods backed by Rust."""

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP


class ConvertHTTP(AccountHTTP, MarketHTTP):
    """Typed Convert endpoints; accepting quotes and placing orders change account state."""

    async def get_convert_pairs(
        self, fromAsset: str | None = None, toAsset: str | None = None
    ) -> list[dict[str, Any]]:
        """Call the Binance Convert public endpoint."""
        return await self._native_public(
            "get_convert_pairs", self._params(fromAsset=fromAsset, toAsset=toAsset)
        )

    async def get_convert_asset_info(self) -> list[dict[str, Any]]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private("get_convert_asset_info", self._params())

    async def get_convert_quote(
        self,
        fromAsset: str,
        toAsset: str,
        fromAmount: str | None = None,
        toAmount: str | None = None,
        walletType: str | None = None,
        validTime: str | None = None,
    ) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private(
            "get_convert_quote",
            self._params(
                fromAsset=fromAsset,
                toAsset=toAsset,
                fromAmount=fromAmount,
                toAmount=toAmount,
                walletType=walletType,
                validTime=validTime,
            ),
        )

    async def accept_convert_quote(self, quoteId: str) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private("accept_convert_quote", self._params(quoteId=quoteId))

    async def get_convert_order_status(
        self, orderId: str | None = None, quoteId: str | None = None
    ) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private(
            "get_convert_order_status", self._params(orderId=orderId, quoteId=quoteId)
        )

    async def get_convert_trade_history(
        self, startTime: int, endTime: int, limit: int | None = None
    ) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private(
            "get_convert_trade_history",
            self._params(startTime=startTime, endTime=endTime, limit=limit),
        )

    async def place_convert_limit_order(
        self,
        baseAsset: str,
        quoteAsset: str,
        limitPrice: str,
        side: str,
        expiredType: str,
        baseAmount: str | None = None,
        quoteAmount: str | None = None,
        walletType: str | None = None,
    ) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private(
            "place_convert_limit_order",
            self._params(
                baseAsset=baseAsset,
                quoteAsset=quoteAsset,
                limitPrice=limitPrice,
                side=side,
                expiredType=expiredType,
                baseAmount=baseAmount,
                quoteAmount=quoteAmount,
                walletType=walletType,
            ),
        )

    async def cancel_convert_limit_order(self, orderId: int) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private(
            "cancel_convert_limit_order", self._params(orderId=orderId)
        )

    async def get_open_convert_limit_orders(self) -> dict[str, Any]:
        """Call the Binance Convert private endpoint."""
        return await self._native_private("get_open_convert_limit_orders", self._params())
