from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import AssetHTTPTransfersHTTP
from ._withdrawals_http import AssetHTTPWithdrawalsHTTP


class AssetHTTP(AssetHTTPTransfersHTTP, AssetHTTPWithdrawalsHTTP, HTTPManager):
    async def get_currencies(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get currency information.

        Args:
            ccy: List of currency codes to query. If None, returns all currencies.

        Returns:
            Dict containing currency information from OKX API.
        """
        return await self._native_private(
            "get_currencies",
            self._native_params(ccy=ccy),
        )

    async def get_balances(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get account balances.

        Args:
            ccy: List of currency codes to query. If None, returns all balances.

        Returns:
            Dict containing balance information from OKX API.
        """
        return await self._native_private(
            "get_balances",
            self._native_params(ccy=ccy),
        )

    async def get_asset_valuation(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get asset valuation.

        Args:
            ccy: List of currency codes to query. If None, returns valuation for all currencies.

        Returns:
            Dict containing asset valuation information from OKX API.
        """
        return await self._native_private(
            "get_asset_valuation",
            self._native_params(ccy=ccy),
        )

    async def get_bills(
        self,
        ccy: str | None = None,
        type: str | None = None,
        thirdPartyType: str | None = None,
        clientId: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get bills information.

        Args:
            type: Bill type to query (optional).
            clientId: Client ID to query (optional).
            after: Pagination parameter - query bills after this ID (optional).
            before: Pagination parameter - query bills before this ID (optional).
            limit: Number of results to return (optional).

        Returns:
            Dict containing bills information from OKX API.
        """
        return await self._native_private(
            "get_bills",
            self._native_params(
                ccy=ccy,
                type=type,
                thirdPartyType=thirdPartyType,
                clientId=clientId,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_deposit_address(
        self,
        ccy: str,
    ) -> dict[str, Any]:
        """
        Get deposit address for a specific currency.

        Args:
            ccy: Currency code for which to get deposit address.

        Returns:
            Dict containing deposit address information from OKX API.
        """
        return await self._native_private(
            "get_deposit_address",
            self._native_params(ccy=ccy),
        )

    async def get_deposit_history(
        self,
        ccy: str | None = None,
        depId: str | None = None,
        fromWdId: str | None = None,
        txId: str | None = None,
        type: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get deposit history.

        Args:
            ccy: Currency code to query (optional).
            depId: Deposit ID to query (optional).
            fromWdId: From withdrawal ID to query (optional).
            txId: Transaction ID to query (optional).
            type: Deposit type to query (optional).
            state: Deposit state to query (optional).
            after: Pagination parameter - query deposits after this ID (optional).
            before: Pagination parameter - query deposits before this ID (optional).
            limit: Number of results to return (optional).

        Returns:
            Dict containing deposit history information from OKX API.
        """
        return await self._native_private(
            "get_deposit_history",
            self._native_params(
                ccy=ccy,
                depId=depId,
                fromWdId=fromWdId,
                txId=txId,
                type=type,
                state=state,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_exchange_list(self) -> dict[str, Any]:
        """
        Get exchange list.

        Returns:
            Dict containing exchange list information from OKX API.
        """
        return await self._native_private("get_exchange_list", [])

    async def post_monthly_statement(
        self,
        month: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate monthly statement.

        Args:
            month: Month to generate statement for (e.g., "Jan") (optional).

        Returns:
            Dict containing monthly statement generation result from OKX API.
        """
        return await self._native_private(
            "post_monthly_statement",
            self._native_params(month=month),
        )

    async def get_monthly_statement(
        self,
        month: str,
    ) -> dict[str, Any]:
        """
        Get monthly statement.

        Args:
            month: Month to get statement for (e.g., "Jan").

        Returns:
            Dict containing monthly statement information from OKX API.
        """
        return await self._native_private(
            "get_monthly_statement",
            self._native_params(month=month),
        )

    async def get_convert_currencies(self) -> dict[str, Any]:
        """
        Get convertible currencies.

        Returns:
            Dict containing convertible currencies information from OKX API.
        """
        return await self._native_private("get_convert_currencies", [])

    async def get_convert_history(
        self,
        clTReqId: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        Get convert trade history.

        Args:
            clTReqId: Client order ID assigned by the client.
            after: Return records earlier than this timestamp.
            before: Return records newer than this timestamp.
            limit: Number of results to return.
            tag: Order tag.

        Returns:
            Dict containing convert trade history from OKX API.
        """
        return await self._native_private(
            "get_convert_history",
            self._native_params(
                clTReqId=clTReqId, after=after, before=before, limit=limit, tag=tag
            ),
        )
