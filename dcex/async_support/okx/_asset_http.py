from typing import Any

from ._http_manager import HTTPManager


class AssetHTTP(HTTPManager):
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

    async def funds_transfer(
        self,
        ccy: str,
        amt: str,
        from_account: str,
        to_account: str,
        type: str | None = None,
        subAcct: str | None = None,
        loanTrans: bool | str | None = None,
        omitPosRisk: bool | str | None = None,
        clientId: str | None = None,
    ) -> dict[str, Any]:
        """
        Transfer funds between accounts.

        Args:
            ccy: Currency code for the transfer.
            amt: Amount to transfer.
            from_account: Source account type ("FUND" or "TRADING").
            to_account: Destination account type ("FUND" or "TRADING").
            type: Transfer type (optional).
            subAcct: Sub-account name (optional).
            loanTrans: Loan transfer flag (optional).

        Returns:
            Dict containing transfer result from OKX API.
        """
        return await self._native_private(
            "funds_transfer",
            self._native_params(
                ccy=ccy,
                amt=amt,
                from_account=from_account,
                to_account=to_account,
                type=type,
                subAcct=subAcct,
                loanTrans=loanTrans,
                omitPosRisk=omitPosRisk,
                clientId=clientId,
            ),
        )

    async def get_transfer_state(
        self,
        transId: str | None = None,
        clientId: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get transfer state information.

        Args:
            transId: Transfer ID to query (optional).
            clientId: Client ID to query (optional).
            type: Transfer type to query (optional).

        Returns:
            Dict containing transfer state information from OKX API.
        """
        return await self._native_private(
            "get_transfer_state",
            self._native_params(transId=transId, clientId=clientId, type=type),
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

    async def get_deposit_withdraw_status(
        self,
        wdId: str | None = None,
        txId: str | None = None,
        ccy: str | None = None,
        to: str | None = None,
        chain: str | None = None,
    ) -> dict[str, Any]:
        """
        Get deposit and withdrawal status.

        Args:
            wdId: Withdrawal ID to query (optional).
            txId: Transaction ID to query (optional).
            ccy: Currency code to query (optional).
            to: Destination address to query (optional).
            chain: Blockchain network to query (optional).

        Returns:
            Dict containing deposit and withdrawal status information from OKX API.
        """
        if (wdId is None) == (txId is None):
            raise ValueError("Exactly one of wdId or txId is required.")
        if txId is not None:
            missing = [
                name
                for name, value in (("ccy", ccy), ("to", to), ("chain", chain))
                if value is None
            ]
            if missing:
                raise ValueError(
                    f"{', '.join(missing)} required when querying deposit status by txId."
                )
        return await self._native_private(
            "get_deposit_withdraw_status",
            self._native_params(wdId=wdId, txId=txId, ccy=ccy, to=to, chain=chain),
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
