from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.positions import Positions


class PositionHTTP(HTTPManager):
    """
    BitMEX Position HTTP client for position management operations.

    This class provides methods for managing trading positions including
    getting positions, switching modes, setting leverage, and managing margin.
    """

    def get_positions(
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
            filter: Filter criteria for positions
            columns: Specific columns to return
            count: Maximum number of results to return
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or "*" for all accounts

        Returns:
            Dict containing position data

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

        res = self._request(
            method="GET",
            path=Positions.GET_POSITIONS,
            query=payload,
        )
        return res

    def switch_mode(
        self,
        product_symbol: str,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """
        Switch between isolated margin and cross margin modes.

        Args:
            product_symbol: Trading symbol to switch mode for
            enabled: True for isolated margin, False for cross margin

        Returns:
            Dict containing the result of the mode switch

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {
            "symbol": self.ptm.get_exchange_symbol(Common.BITMEX, product_symbol),
            "enabled": enabled,
        }

        res = self._request(
            method="POST",
            path=Positions.SWITCH_MODE,
            query=payload,
        )
        return res

    def set_leverage(
        self,
        product_symbol: str,
        leverage: float,
        cross_margin: bool = True,
        target_account_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Set leverage for a trading position.

        Args:
            product_symbol: Trading symbol to set leverage for
            leverage: Leverage multiplier (e.g., 10.0 for 10x)
            cross_margin: True for cross margin, False for isolated margin
            target_account_id: Specific account ID to set leverage for

        Returns:
            Dict containing the result of the leverage setting

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

        res = self._request(
            method="POST",
            path=Positions.LEVERAGE,
            query=payload,
        )
        return res

    def set_margining_mode(
        self,
        multi_asset: bool = False,
        target_account_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Set the margining mode for the account.

        Args:
            multi_asset: True for multi-asset margining, False for single-asset
            target_account_id: Specific account ID to set margining mode for

        Returns:
            Dict containing the result of the margining mode setting

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if multi_asset:
            payload["marginingMode"] = "MultiAsset"
        # For single-asset margining, leave the field empty (don't include it)

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        res = self._request(
            method="POST",
            path=Positions.MARGINING_MODE,
            query=payload,
        )
        return res

    def get_margining_mode(
        self,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Get the current margining mode for the account.

        Args:
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or "*" for all accounts

        Returns:
            Dict containing margining mode information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {}

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        if target_account_ids is not None:
            payload["targetAccountIds"] = target_account_ids

        res = self._request(
            method="GET",
            path=Positions.MARGINING_MODE,
            query=payload,
        )
        return res

    def get_margin(
        self,
        currency: str = "all",
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Get margin information for the account.

        Args:
            currency: Currency to filter by (default: "all")
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or "*" for all accounts

        Returns:
            Dict containing margin information

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

        res = self._request(
            method="GET",
            path=Positions.GET_MARGIN,
            query=payload,
        )
        return res
