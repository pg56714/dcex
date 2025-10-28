from typing import Any

from ._http_manager import HTTPManager
from .endpoints.asset import Asset


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
        payload = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload = {
                "ccy": ccyName,
            }

        res = await self._request(
            method="GET",
            path=Asset.CURRENCY_INFO,
            query=payload,
        )
        return res

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
        payload = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload = {
                "ccy": ccyName,
            }

        res = await self._request(
            method="GET",
            path=Asset.GET_BALANCES,
            query=payload,
        )
        return res

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
        payload = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload = {
                "ccy": ccyName,
            }

        res = await self._request(
            method="GET",
            path=Asset.ASSET_VALUATION,
            query=payload,
        )
        return res

    async def funds_transfer(
        self,
        ccy: str,
        amt: str,
        from_account: str,
        to_account: str,
        type: str | None = None,
        subAcct: str | None = None,
        loanTrans: str | None = None,
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
        account_map = {
            "FUND": "6",
            "TRADING": "18",
        }

        payload = {
            "ccy": ccy,
            "amt": amt,
            "from": account_map.get(from_account),
            "to": account_map.get(to_account),
        }

        if type is not None:
            payload["type"] = type
        if subAcct is not None:
            payload["subAcct"] = subAcct
        if loanTrans is not None:
            payload["loanTrans"] = loanTrans

        res = await self._request(
            method="POST",
            path=Asset.FUNDS_TRANSFER,
            query=payload,
        )
        return res

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
        payload = {}
        if transId is not None:
            payload["transId"] = transId
        if clientId is not None:
            payload["clientId"] = clientId
        if type is not None:
            payload["type"] = type

        res = await self._request(
            method="GET",
            path=Asset.TRANSFER_STATE,
            query=payload,
        )
        return res

    async def get_bills(
        self,
        type: str | None = None,
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
        payload = {}
        if type is not None:
            payload["type"] = type
        if clientId is not None:
            payload["clientId"] = clientId
        if after is not None:
            payload["after"] = after
        if before is not None:
            payload["before"] = before
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Asset.BILLS_INFO,
            query=payload,
        )
        return res

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
        payload = {
            "ccy": ccy,
        }

        res = await self._request(
            method="GET",
            path=Asset.DEPOSIT_ADDRESS,
            query=payload,
        )
        return res

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
        payload = {}
        if ccy is not None:
            payload["ccy"] = ccy
        if depId is not None:
            payload["depId"] = depId
        if fromWdId is not None:
            payload["fromWdId"] = fromWdId
        if txId is not None:
            payload["txId"] = txId
        if type is not None:
            payload["type"] = type
        if state is not None:
            payload["state"] = state
        if after is not None:
            payload["after"] = after
        if before is not None:
            payload["before"] = before
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Asset.DEPOSIT_HISTORY,
            query=payload,
        )
        return res

    async def withdrawal(
        self,
        ccy: str,
        amt: str,
        dest: str,
        toAddr: str,
        chain: str | None = None,
        areaCode: str | None = None,
        rcvrInfo: str | None = None,
    ) -> dict[str, Any]:
        """
        Withdraw cryptocurrency.

        Args:
            ccy: Currency code to withdraw.
            amt: Amount to withdraw.
            dest: Destination type.
            toAddr: Destination address.
            chain: Blockchain network (optional).
            areaCode: Area code for phone verification (optional).
            rcvrInfo: Receiver information (optional).

        Returns:
            Dict containing withdrawal result from OKX API.
        """
        payload = {
            "ccy": ccy,
            "amt": amt,
            "dest": dest,
            "toAddr": toAddr,
        }
        if chain is not None:
            payload["chain"] = chain
        if areaCode is not None:
            payload["areaCode"] = areaCode
        if rcvrInfo is not None:
            payload["rcvrInfo"] = rcvrInfo

        res = await self._request(
            method="POST",
            path=Asset.WITHDRAWAL_COIN,
            query=payload,
        )
        return res

    async def cancel_withdrawal(
        self,
        wdId: str,
    ) -> dict[str, Any]:
        """
        Cancel a withdrawal request.

        Args:
            wdId: Withdrawal ID to cancel.

        Returns:
            Dict containing cancellation result from OKX API.
        """
        payload = {
            "wdId": wdId,
        }

        res = await self._request(
            method="POST",
            path=Asset.CANCEL_WITHDRAWAL,
            query=payload,
        )
        return res

    async def get_withdrawal_history(
        self,
        ccy: str | None = None,
        wdId: str | None = None,
        clientId: str | None = None,
        txId: str | None = None,
        type: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get withdrawal history.

        Args:
            ccy: Currency code to query (optional).
            wdId: Withdrawal ID to query (optional).
            clientId: Client ID to query (optional).
            txId: Transaction ID to query (optional).
            type: Withdrawal type to query (optional).
            state: Withdrawal state to query (optional).
            after: Pagination parameter - query withdrawals after this ID (optional).
            before: Pagination parameter - query withdrawals before this ID (optional).
            limit: Number of results to return (optional).

        Returns:
            Dict containing withdrawal history information from OKX API.
        """
        payload = {}
        if ccy is not None:
            payload["ccy"] = ccy
        if wdId is not None:
            payload["wdId"] = wdId
        if clientId is not None:
            payload["clientId"] = clientId
        if txId is not None:
            payload["txId"] = txId
        if type is not None:
            payload["type"] = type
        if state is not None:
            payload["state"] = state
        if after is not None:
            payload["after"] = after
        if before is not None:
            payload["before"] = before
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Asset.WITHDRAWAL_HISTORY,
            query=payload,
        )
        return res

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
        payload = {}
        if wdId is not None:
            payload["wdId"] = wdId
        if txId is not None:
            payload["txId"] = txId
        if ccy is not None:
            payload["ccy"] = ccy
        if to is not None:
            payload["to"] = to
        if chain is not None:
            payload["chain"] = chain

        res = await self._request(
            method="GET",
            path=Asset.GET_DEPOSIT_WITHDRAW_STATUS,
            query=payload,
        )
        return res

    async def get_exchange_list(self) -> dict[str, Any]:
        """
        Get exchange list.

        Returns:
            Dict containing exchange list information from OKX API.
        """
        res = await self._request(
            method="GET",
            path=Asset.EXCHANGE_LIST,
            query={},
        )
        return res

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
        payload = {}
        if month is not None:
            payload["month"] = month

        res = await self._request(
            method="POST",
            path=Asset.MONTHLY_STATEMENT,
            query=payload,
        )
        return res

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
        payload = {
            "month": month,
        }

        res = await self._request(
            method="GET",
            path=Asset.MONTHLY_STATEMENT,
            query=payload,
        )
        return res

    async def get_convert_currencies(self) -> dict[str, Any]:
        """
        Get convertible currencies.

        Returns:
            Dict containing convertible currencies information from OKX API.
        """
        res = await self._request(
            method="GET",
            path=Asset.GET_CURRENCIES,
            query={},
        )
        return res
