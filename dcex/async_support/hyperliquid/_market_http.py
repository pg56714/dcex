"""Market-related HTTP API client for Hyperliquid exchange."""

from typing import Any

import msgspec

from ..._native_http import NativeResponse
from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoint.market import Market
from .endpoint.path import Path


class MarketHTTP(HTTPManager):
    """HTTP client for market-related operations on Hyperliquid exchange."""

    async def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        native_client = self._native_client
        if (
            method.upper() == "POST"
            and str(path) == str(Path.INFO)
            and not signed
            and native_client is not None
            and self._uses_native_transport()
        ):
            status, headers, body = await native_client.public_request_async(
                msgspec.json.encode(query or {})
            )
            response = NativeResponse(status, dict(headers), bytes(body))
            self._store_response_headers(response)
            return response.json()
        return await super()._request(method, path, query, signed)

    async def get_meta(
        self,
        dex: str | None = None,
    ) -> dict[str, Any]:
        """
        Get market metadata.

        Args:
            dex: DEX identifier (optional)

        Returns:
            Dict containing market metadata
        """
        payload: dict[str, Any] = {
            "type": Market.META,
        }

        if dex is not None:
            payload["dex"] = dex

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_meta(self) -> dict[str, Any]:
        """
        Get spot market metadata.

        Returns:
            Dict containing spot market metadata
        """
        payload = {
            "type": Market.SPOTMETA,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_meta_and_asset_ctxs(self) -> dict[str, Any]:
        """
        Get market metadata and asset contexts.

        Returns:
            Dict containing market metadata and asset contexts
        """
        payload = {
            "type": Market.METAANDASSETCTXS,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_spot_meta_and_asset_ctxs(self) -> dict[str, Any]:
        """
        Get spot market metadata and asset contexts.

        Returns:
            Dict containing spot market metadata and asset contexts
        """
        payload = {
            "type": Market.SPOTMETAANDASSETCTXS,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_l2book(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get L2 order book for a product.

        Args:
            product_symbol: Product symbol (e.g. BTC-USDC-SWAP)

        Returns:
            Dict containing L2 order book data
        """
        payload = {
            "type": Market.L2BOOK,
            "coin": msgspec.json.decode(
                (await self._get_ptm()).get_exchange_symbol(
                    Common.HYPERLIQUID,
                    product_symbol,
                )
            )[0],
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_candle_snapshot(
        self,
        product_symbol: str,
        interval: str,
        startTime: int,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get candlestick data for a product.

        Args:
            product_symbol: Product symbol (e.g. BTC-USDC-SWAP)
            interval: Time interval (e.g. 1m, 5m, 15m, 1h, 4h, 1d)
            startTime: Start timestamp in milliseconds
            endTime: End timestamp in milliseconds (optional)

        Returns:
            Dict containing candlestick data
        """
        payload = {
            "type": Market.CANDLESNAPSHOT,
            "req": {
                "coin": msgspec.json.decode(
                    (await self._get_ptm()).get_exchange_symbol(
                        Common.HYPERLIQUID,
                        product_symbol,
                    )
                )[0],
                "interval": interval,
                "startTime": startTime,
            },
        }

        if endTime is not None:
            payload["req"]["endTime"] = endTime

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_funding_rate_history(
        self,
        product_symbol: str,
        startTime: int,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate history for a product.

        Args:
            product_symbol: Product symbol (e.g. BTC-USDC-SWAP)
            startTime: Start timestamp in milliseconds
            endTime: End timestamp in milliseconds (optional)

        Returns:
            Dict containing funding rate history
        """
        payload = {
            "type": Market.FUNDINGHISTORY,
            "coin": msgspec.json.decode(
                (await self._get_ptm()).get_exchange_symbol(
                    Common.HYPERLIQUID,
                    product_symbol,
                )
            )[0],
            "startTime": startTime,
        }

        if endTime is not None:
            payload["endTime"] = endTime

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res
