from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.positions import Positions


class PositionHTTP(HTTPManager):
    """
    HTTP client for BitMEX position management API endpoints.

    This class provides methods to manage trading positions on BitMEX,
    including position queries, margin mode switching, leverage settings,
    and margin information retrieval.
    """

    async def get_positions(
        self,
        filter: str | None = None,
        columns: str | None = None,
        count: int | None = None,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Get current trading positions.

        Args:
            filter: Filter criteria as a string
            columns: Comma-separated list of columns to return
            count: Maximum number of results to return
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or string for filtering

        Returns:
            dict: Position data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if filter is not None:
            payload["filter"] = filter

        if columns is not None:
            payload["columns"] = columns

        if count is not None:
            payload["count"] = count

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        if target_account_ids is not None:
            payload["targetAccountIds"] = target_account_ids

        res = await self._request(
            method="GET",
            path=Positions.GET_POSITIONS,
            query=payload,
        )
        return res

    async def switch_mode(
        self,
        product_symbol: str,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """
        Switch between isolated and cross margin modes.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            enabled: True for isolated margin, False for cross margin

        Returns:
            dict: Mode switch response

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol),
            "enabled": enabled,
        }

        res = await self._request(
            method="POST",
            path=Positions.SWITCH_MODE,
            query=payload,
        )
        return res

    async def set_leverage(
        self,
        product_symbol: str,
        leverage: float,
        cross_margin: bool = True,
        target_account_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Set leverage for a trading position.

        Args:
            product_symbol: Trading symbol (e.g., 'BTCUSD')
            leverage: Leverage multiplier (e.g., 2.0 for 2x leverage)
            cross_margin: True for cross margin, False for isolated margin
            target_account_id: Specific account ID to target

        Returns:
            dict: Leverage setting response

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol),
            "leverage": leverage,
            "crossMargin": cross_margin,
        }

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        res = await self._request(
            method="POST",
            path=Positions.LEVERAGE,
            query=payload,
        )
        return res

    async def set_margining_mode(
        self,
        multi_asset: bool = False,
        target_account_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Set margining mode for the account.

        Args:
            multi_asset: True for multi-asset margining, False for single-asset
            target_account_id: Specific account ID to target

        Returns:
            dict: Margining mode setting response

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if multi_asset:
            payload["marginingMode"] = "MultiAsset"
        # For single-asset margining, leave the field empty (don't include it)

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        res = await self._request(
            method="POST",
            path=Positions.MARGINING_MODE,
            query=payload,
        )
        return res

    async def get_margining_mode(
        self,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Get current margining mode for the account.

        Args:
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or string for filtering

        Returns:
            dict: Margining mode information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        if target_account_ids is not None:
            payload["targetAccountIds"] = target_account_ids

        res = await self._request(
            method="GET",
            path=Positions.MARGINING_MODE,
            query=payload,
        )
        return res

    async def get_margin(
        self,
        currency: str = "all",
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Get margin information for the account.

        Args:
            currency: Currency symbol to filter by (default: "all")
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or string for filtering

        Returns:
            dict: Margin information data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {
            "currency": currency,
        }

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        if target_account_ids is not None:
            payload["targetAccountIds"] = target_account_ids

        res = await self._request(
            method="GET",
            path=Positions.GET_MARGIN,
            query=payload,
        )
        return res
