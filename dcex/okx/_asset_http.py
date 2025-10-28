from typing import Any

from ._http_manager import HTTPManager
from .endpoints.asset import Asset


class AssetHTTP(HTTPManager):
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
        payload: dict[str, Any] = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload["ccy"] = ccyName

        res = self._request(
            method="GET",
            path=Asset.CURRENCY_INFO,
            query=payload,
        )
        return res

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
        payload: dict[str, Any] = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload["ccy"] = ccyName

        res = self._request(
            method="GET",
            path=Asset.GET_BALANCES,
            query=payload,
        )
        return res

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
        payload: dict[str, Any] = {}
        if ccy is not None:
            ccyName = ",".join(ccy)
            payload["ccy"] = ccyName

        res = self._request(
            method="GET",
            path=Asset.ASSET_VALUATION,
            query=payload,
        )
        return res

    def funds_transfer(
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
            ccy: Currency code
            amt: Transfer amount
            from_account: Source account ("FUND" or "TRADING")
            to_account: Destination account ("FUND" or "TRADING")
            type: Transfer type
            subAcct: Sub-account name
            loanTrans: Loan transfer flag

        Returns:
            Dictionary containing transfer result.
        """
        account_map = {
            "FUND": "6",
            "TRADING": "18",
        }

        payload: dict[str, Any] = {
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

        res = self._request(
            method="POST",
            path=Asset.FUNDS_TRANSFER,
            query=payload,
        )
        return res

    def get_transfer_state(
        self,
        transId: str | None = None,
        clientId: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get transfer state information.

        Args:
            transId: Transfer ID
            clientId: Client ID
            type: Transfer type

        Returns:
            Dictionary containing transfer state information.
        """
        payload: dict[str, Any] = {}
        if transId is not None:
            payload["transId"] = transId
        if clientId is not None:
            payload["clientId"] = clientId
        if type is not None:
            payload["type"] = type

        res = self._request(
            method="GET",
            path=Asset.TRANSFER_STATE,
            query=payload,
        )
        return res

    def get_bills(
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
            type: Bill type
            clientId: Client ID
            after: Pagination parameter - timestamp after this value
            before: Pagination parameter - timestamp before this value
            limit: Number of results to return

        Returns:
            Dictionary containing bills information.
        """
        payload: dict[str, Any] = {}
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

        res = self._request(
            method="GET",
            path=Asset.BILLS_INFO,
            query=payload,
        )
        return res

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
        payload: dict[str, Any] = {
            "ccy": ccy,
        }

        res = self._request(
            method="GET",
            path=Asset.DEPOSIT_ADDRESS,
            query=payload,
        )
        return res

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
        payload: dict[str, Any] = {}
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

        res = self._request(
            method="GET",
            path=Asset.DEPOSIT_HISTORY,
            query=payload,
        )
        return res

    def withdrawal(
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
            ccy: Currency code
            amt: Withdrawal amount
            dest: Destination (3: internal transfer, 4: external transfer)
            toAddr: Destination address
            chain: Blockchain network
            areaCode: Area code for phone number
            rcvrInfo: Receiver information

        Returns:
            Dictionary containing withdrawal result.
        """
        payload: dict[str, Any] = {
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

        res = self._request(
            method="POST",
            path=Asset.WITHDRAWAL_COIN,
            query=payload,
        )
        return res

    def cancel_withdrawal(
        self,
        wdId: str,
    ) -> dict[str, Any]:
        """
        Cancel a withdrawal.

        Args:
            wdId: Withdrawal ID

        Returns:
            Dictionary containing withdrawal cancellation result.
        """
        payload: dict[str, Any] = {
            "wdId": wdId,
        }

        res = self._request(
            method="POST",
            path=Asset.CANCEL_WITHDRAWAL,
            query=payload,
        )
        return res

    def get_withdrawal_history(
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
            ccy: Currency code
            wdId: Withdrawal ID
            clientId: Client ID
            txId: Transaction ID
            type: Withdrawal type
            state: Withdrawal state
            after: Pagination parameter - timestamp after this value
            before: Pagination parameter - timestamp before this value
            limit: Number of results to return

        Returns:
            Dictionary containing withdrawal history.
        """
        payload: dict[str, Any] = {}
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

        res = self._request(
            method="GET",
            path=Asset.WITHDRAWAL_HISTORY,
            query=payload,
        )
        return res

    def get_deposit_withdraw_status(
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
            wdId: Withdrawal ID
            txId: Transaction ID
            ccy: Currency code
            to: Destination address
            chain: Blockchain network

        Returns:
            Dictionary containing deposit and withdrawal status.
        """
        payload: dict[str, Any] = {}
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

        res = self._request(
            method="GET",
            path=Asset.GET_DEPOSIT_WITHDRAW_STATUS,
            query=payload,
        )
        return res

    def get_exchange_list(self) -> dict[str, Any]:
        """
        Get exchange list.

        Returns:
            Dictionary containing exchange list.
        """
        res = self._request(
            method="GET",
            path=Asset.EXCHANGE_LIST,
            query={},
        )
        return res

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
        payload: dict[str, Any] = {}
        if month is not None:
            payload["month"] = month

        res = self._request(
            method="POST",
            path=Asset.MONTHLY_STATEMENT,
            query=payload,
        )
        return res

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
        payload: dict[str, Any] = {
            "month": month,
        }

        res = self._request(
            method="GET",
            path=Asset.MONTHLY_STATEMENT,
            query=payload,
        )
        return res

    def get_convert_currencies(self) -> dict[str, Any]:
        """
        Get convert currencies.

        Returns:
            Dictionary containing convert currencies information.
        """
        payload: dict[str, Any] = {}
        res = self._request(
            method="GET",
            path=Asset.GET_CURRENCIES,
            query=payload,
        )
        return res
