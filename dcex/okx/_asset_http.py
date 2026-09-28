from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import AssetHTTPTransfersHTTP
from ._withdrawals_http import AssetHTTPWithdrawalsHTTP


class AssetHTTP(AssetHTTPTransfersHTTP, AssetHTTPWithdrawalsHTTP, HTTPManager):
    def get_currencies(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get currency information.

        Args:
            ccy: List of currency codes to query. If None, returns all currencies.

        Returns:
            Dictionary containing currency information.
        """
        return self._native_private(
            "get_currencies",
            self._native_params(ccy=ccy),
        )

    def get_balances(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get account balances.

        Args:
            ccy: List of currency codes to query. If None, returns all currencies.

        Returns:
            Dictionary containing balance information.
        """
        return self._native_private(
            "get_balances",
            self._native_params(ccy=ccy),
        )

    def get_asset_valuation(
        self,
        ccy: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get asset valuation.

        Args:
            ccy: List of currency codes to query. If None, returns all currencies.

        Returns:
            Dictionary containing asset valuation information.
        """
        return self._native_private(
            "get_asset_valuation",
            self._native_params(ccy=ccy),
        )

    def get_bills(
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
            type: Bill type
            clientId: Client ID
            after: Pagination parameter - timestamp after this value
            before: Pagination parameter - timestamp before this value
            limit: Number of results to return

        Returns:
            Dictionary containing bills information.
        """
        return self._native_private(
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

    def get_deposit_address(
        self,
        ccy: str,
    ) -> dict[str, Any]:
        """
        Get deposit address for a currency.

        Args:
            ccy: Currency code

        Returns:
            Dictionary containing deposit address information.
        """
        return self._native_private(
            "get_deposit_address",
            self._native_params(ccy=ccy),
        )

    def get_deposit_history(
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
            ccy: Currency code
            depId: Deposit ID
            fromWdId: From withdrawal ID
            txId: Transaction ID
            type: Deposit type
            state: Deposit state
            after: Pagination parameter - timestamp after this value
            before: Pagination parameter - timestamp before this value
            limit: Number of results to return

        Returns:
            Dictionary containing deposit history.
        """
        return self._native_private(
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

    def get_exchange_list(self) -> dict[str, Any]:
        """
        Get exchange list.

        Returns:
            Dictionary containing exchange list.
        """
        return self._native_private("get_exchange_list", [])

    def post_monthly_statement(
        self,
        month: str | None = None,
    ) -> dict[str, Any]:
        """
        Request monthly statement.

        Args:
            month: Month (e.g., "Jan")

        Returns:
            Dictionary containing monthly statement request result.
        """
        return self._native_private(
            "post_monthly_statement",
            self._native_params(month=month),
        )

    def get_monthly_statement(
        self,
        month: str,
    ) -> dict[str, Any]:
        """
        Get monthly statement.

        Args:
            month: Month (e.g., "Jan")

        Returns:
            Dictionary containing monthly statement.
        """
        return self._native_private(
            "get_monthly_statement",
            self._native_params(month=month),
        )

    def get_convert_currencies(self) -> dict[str, Any]:
        """
        Get convert currencies.

        Returns:
            Dictionary containing convert currencies information.
        """
        return self._native_private("get_convert_currencies", [])

    def get_convert_history(
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
            clTReqId: Client order ID assigned by the client
            after: Return records earlier than this timestamp
            before: Return records newer than this timestamp
            limit: Number of results to return
            tag: Order tag

        Returns:
            Dictionary containing convert trade history.
        """
        return self._native_private(
            "get_convert_history",
            self._native_params(
                clTReqId=clTReqId, after=after, before=before, limit=limit, tag=tag
            ),
        )
