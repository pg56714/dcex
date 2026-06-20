"""BingX account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for BingX account-related API endpoints backed by Rust."""

    async def get_account_balance(self) -> dict[str, Any]:
        return await self._native_private("get_account_balance", [])

    async def get_swap_account_balance(self) -> dict[str, Any]:
        return await self._native_private("get_swap_account_balance", [])

    async def get_spot_account_balance(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_spot_account_balance",
            self._native_params(recvWindow=recvWindow),
        )

    async def get_fund_account_balance(
        self,
        asset: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_fund_account_balance",
            self._native_params(asset=asset, recvWindow=recvWindow),
        )

    async def get_all_account_balance(
        self,
        accountType: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_all_account_balance",
            self._native_params(accountType=accountType, recvWindow=recvWindow),
        )

    async def get_account_uid(
        self,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_account_uid",
            self._native_params(recvWindow=recvWindow),
        )

    async def get_api_key_info(
        self,
        uid: int | str,
        apiKey: str | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_api_key_info",
            self._native_params(uid=uid, apiKey=apiKey, recvWindow=recvWindow),
        )

    async def get_transferable_coins(
        self,
        fromAccount: str,
        toAccount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_transferable_coins",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                recvWindow=recvWindow,
            ),
        )

    async def asset_transfer(
        self,
        fromAccount: str,
        toAccount: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "asset_transfer",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                asset=asset,
                amount=amount,
                recvWindow=recvWindow,
            ),
        )

    async def get_asset_transfer_records(
        self,
        fromAccount: str | None = None,
        toAccount: str | None = None,
        tranId: int | str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageIndex: int | None = None,
        pageSize: int | None = None,
        recvWindow: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_asset_transfer_records",
            self._native_params(
                fromAccount=fromAccount,
                toAccount=toAccount,
                tranId=tranId,
                startTime=startTime,
                endTime=endTime,
                pageIndex=pageIndex,
                pageSize=pageSize,
                recvWindow=recvWindow,
            ),
        )

    async def get_open_positions(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_fund_flow(
        self,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_fund_flow",
            self._native_params(
                product_symbol=product_symbol,
                income_type=income_type,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
            ),
        )

    async def get_listen_key(self) -> str:
        if not self.api_key:
            raise ValueError("API key is required")
        self._uses_native_transport()
        return (await self._native_private("get_listen_key", []))["listenKey"]

    async def keep_alive_listen_key(self, listen_key: str) -> dict[str, Any]:
        return await self._native_private(
            "keep_alive_listen_key",
            self._native_params(listen_key=listen_key),
        )
