"""BingX account HTTP client."""

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import FundAccount, SpotAccount, SwapAccount, TransferAccount


class AccountHTTP(HTTPManager):
    """HTTP client for BingX account-related API endpoints."""

    def get_account_balance(self) -> dict:
        """
        Get account balance information.

        Returns:
            dict: Account balance data
        """
        payload = {}
        res = self._request(
            method="GET",
            path=SwapAccount.ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    def get_swap_account_balance(self) -> dict:
        """Get swap account balance information."""
        return self.get_account_balance()

    def get_spot_account_balance(
        self,
        recvWindow: int | None = None,
    ) -> dict:
        """Get spot account balance information."""
        payload = {}
        if recvWindow is not None:
            payload["recvWindow"] = recvWindow

        res = self._request(
            method="GET",
            path=SpotAccount.ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    def get_fund_account_balance(
        self,
        asset: str | None = None,
        recvWindow: int | None = None,
    ) -> dict:
        """Get fund account balance information."""
        payload = {}
        if asset is not None:
            payload["asset"] = asset
        if recvWindow is not None:
            payload["recvWindow"] = recvWindow

        res = self._request(
            method="GET",
            path=FundAccount.ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    def get_all_account_balance(
        self,
        accountType: str | None = None,
        recvWindow: int | None = None,
    ) -> dict:
        """Get BingX asset overview across account types."""
        payload = {}
        if accountType is not None:
            payload["accountType"] = accountType
        if recvWindow is not None:
            payload["recvWindow"] = recvWindow

        res = self._request(
            method="GET",
            path=FundAccount.ALL_ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    def get_account_uid(
        self,
        recvWindow: int | None = None,
    ) -> dict:
        """Get BingX account UID."""
        payload = {}
        if recvWindow is not None:
            payload["recvWindow"] = recvWindow

        res = self._request(
            method="GET",
            path=FundAccount.ACCOUNT_UID,
            query=payload,
        )
        return res

    def get_api_key_info(
        self,
        uid: int | str,
        apiKey: str | None = None,
        recvWindow: int | None = None,
    ) -> dict:
        """Get BingX API key information for an account UID."""
        payload = {"uid": str(uid)}
        if apiKey is not None:
            payload["apiKey"] = apiKey
        if recvWindow is not None:
            payload["recvWindow"] = str(recvWindow)

        res = self._request(
            method="GET",
            path=FundAccount.API_KEY_INFO,
            query=payload,
        )
        return res

    def get_transferable_coins(
        self,
        fromAccount: str,
        toAccount: str,
        recvWindow: int | None = None,
    ) -> dict:
        """Get transferable coins between BingX account types."""
        payload = {
            "fromAccount": fromAccount,
            "toAccount": toAccount,
        }
        if recvWindow is not None:
            payload["recvWindow"] = str(recvWindow)

        res = self._request(
            method="GET",
            path=TransferAccount.TRANSFERABLE_COINS,
            query=payload,
        )
        return res

    def asset_transfer(
        self,
        fromAccount: str,
        toAccount: str,
        asset: str,
        amount: str,
        recvWindow: int | None = None,
    ) -> dict:
        """Transfer assets between BingX account types."""
        payload = {
            "fromAccount": fromAccount,
            "toAccount": toAccount,
            "asset": asset,
            "amount": amount,
        }
        if recvWindow is not None:
            payload["recvWindow"] = str(recvWindow)

        res = self._request(
            method="POST",
            path=TransferAccount.ASSET_TRANSFER,
            query=payload,
        )
        return res

    def get_asset_transfer_records(
        self,
        fromAccount: str | None = None,
        toAccount: str | None = None,
        tranId: int | str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageIndex: int | None = None,
        pageSize: int | None = None,
        recvWindow: int | None = None,
    ) -> dict:
        """Get BingX asset transfer records."""
        payload = {}
        if fromAccount is not None:
            payload["fromAccount"] = fromAccount
        if toAccount is not None:
            payload["toAccount"] = toAccount
        if tranId is not None:
            payload["tranId"] = str(tranId)
        if startTime is not None:
            payload["startTime"] = str(startTime)
        if endTime is not None:
            payload["endTime"] = str(endTime)
        if pageIndex is not None:
            payload["pageIndex"] = str(pageIndex)
        if pageSize is not None:
            payload["pageSize"] = str(pageSize)
        if recvWindow is not None:
            payload["recvWindow"] = str(recvWindow)

        res = self._request(
            method="GET",
            path=TransferAccount.TRANSFER_RECORDS,
            query=payload,
        )
        return res

    def get_open_positions(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get open positions.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Open positions data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = self._request(
            method="GET",
            path=SwapAccount.OPEN_POSITIONS,
            query=payload,
        )
        return res

    def get_fund_flow(
        self,
        product_symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get fund flow history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            income_type: Income type (TRANSFER_IN, TRANSFER_OUT, TRADE_FEE, etc.)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of records per page

        Returns:
            dict: Fund flow history data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = product_symbol
        if income_type is not None:
            payload["incomeType"] = income_type
        if start_time is not None:
            payload["startTime"] = start_time
        if end_time is not None:
            payload["endTime"] = end_time
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="GET",
            path=SwapAccount.FUND_FLOW,
            query=payload,
        )
        return res

    def get_listen_key(self) -> str:
        """
        Get WebSocket listen key.

        Returns:
            str: WebSocket listen key
        """

        if not self.api_key:
            raise ValueError("API key is required")

        url = self.base_url + SwapAccount.LISTEN_KEY
        headers = {"X-BX-APIKEY": self.api_key}

        res = self.session.post(url, headers=headers)
        data = res.json()
        return data.get("listenKey")

    def keep_alive_listen_key(self, listen_key: str) -> dict:
        """
        Keep alive WebSocket listen key.

        Args:
            listen_key: WebSocket listen key to keep alive

        Returns:
            dict: API response
        """
        payload = {
            "listenKey": listen_key,
        }

        res = self._request(
            method="PUT",
            path=SwapAccount.LISTEN_KEY,
            query=payload,
        )
        return res
