"""BitMEX async private position HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class PositionHTTP(HTTPManager):
    """Async HTTP client for BitMEX position APIs."""

    async def get_positions(
        self,
        filter: dict[str, Any] | str | None = None,
        columns: list[str] | str | None = None,
        count: int | None = None,
        target_account_id: int | None = None,
        target_account_ids: list[str | int] | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get current BitMEX positions."""
        params = self._native_params(
            filter=filter,
            columns=columns,
            count=count,
            targetAccountId=target_account_id,
        )
        self._append_target_account_ids(params, target_account_ids)
        return await self._native_private("get_positions", params)

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
        target_account_ids: list[str | int] | str | None = None,
    ) -> list[dict[str, Any]]:
        """Get BitMEX margining mode."""
        params = self._native_params(targetAccountId=target_account_id)
        self._append_target_account_ids(params, target_account_ids)
        return await self._native_private("get_margining_mode", params)

    async def get_margin(
        self,
        currency: str = "XBt",
        target_account_id: int | None = None,
        target_account_ids: list[str | int] | str | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Get BitMEX margin information."""
        params = self._native_params(currency=currency, targetAccountId=target_account_id)
        self._append_target_account_ids(params, target_account_ids)
        return await self._native_private("get_margin", params)

    @staticmethod
    def _append_target_account_ids(
        params: list[tuple[str, str]],
        target_account_ids: list[str | int] | str | None,
    ) -> None:
        if isinstance(target_account_ids, list):
            params.extend(
                ("targetAccountIds[]", str(account_id)) for account_id in target_account_ids
            )
        elif isinstance(target_account_ids, str):
            params.append(("targetAccountIds", target_account_ids))
