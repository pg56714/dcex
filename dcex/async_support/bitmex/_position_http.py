"""BitMEX async private position HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class PositionHTTP(HTTPManager):
    """Async HTTP client for BitMEX position APIs."""

    async def get_positions(
        self,
        filter: str | None = None,
        columns: str | None = None,
        count: int | None = None,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """Get current BitMEX positions."""
        return await self._native_private(
            "get_positions",
            self._native_params(
                filter=filter,
                columns=columns,
                count=count,
                targetAccountId=target_account_id,
                targetAccountIds=target_account_ids,
            ),
        )

    async def switch_mode(
        self,
        product_symbol: str,
        enabled: bool = True,
    ) -> dict[str, Any]:
        """Switch isolated margin mode."""
        return await self._native_private(
            "switch_mode",
            self._native_params(product_symbol=product_symbol, enabled=enabled),
        )

    async def set_leverage(
        self,
        product_symbol: str,
        leverage: float,
        target_account_id: int | None = None,
    ) -> dict[str, Any]:
        """Set BitMEX leverage."""
        return await self._native_private(
            "set_leverage",
            self._native_params(
                product_symbol=product_symbol,
                leverage=leverage,
                targetAccountId=target_account_id,
            ),
        )

    async def set_margining_mode(
        self,
        multi_asset: bool = False,
        target_account_id: int | None = None,
    ) -> dict[str, Any]:
        """Set BitMEX margining mode."""
        return await self._native_private(
            "set_margining_mode",
            self._native_params(multi_asset=multi_asset, targetAccountId=target_account_id),
        )

    async def get_margining_mode(
        self,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """Get BitMEX margining mode."""
        return await self._native_private(
            "get_margining_mode",
            self._native_params(
                targetAccountId=target_account_id,
                targetAccountIds=target_account_ids,
            ),
        )

    async def get_margin(
        self,
        currency: str = "all",
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """Get BitMEX margin information."""
        return await self._native_private(
            "get_margin",
            self._native_params(
                currency=currency,
                targetAccountId=target_account_id,
                targetAccountIds=target_account_ids,
            ),
        )
