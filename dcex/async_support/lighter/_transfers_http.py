"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    async def get_transfer_history(
        self,
        account_index: int | None = None,
        cursor: str | None = None,
        type_: str | list[str] | tuple[str, ...] | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter transfer history."""
        return await self._native_private("get_transfer_history", self._native_params(**locals()))

    async def get_transfer_fee_info(
        self,
        account_index: int | None = None,
        to_account_index: int | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Lighter transfer fee information."""
        return await self._native_private("get_transfer_fee_info", self._native_params(**locals()))
