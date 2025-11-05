"""Account-related HTTP API client for Hyperliquid exchange."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoint.account import Account
from .endpoint.path import Path


class AccountHTTP(HTTPManager):
    """HTTP client for account-related operations on Hyperliquid exchange."""

    async def clearinghouse_state(
        self,
        user: str,
        dex: str | None = None,
    ) -> dict[str, Any]:
        """
        Get clearinghouse state for a user.

        Args:
            user: Wallet address
            dex: DEX identifier (optional)

        Returns:
            Dict containing clearinghouse state information
        """
        payload = {
            "type": Account.CLEARINGHOUSESTATE,
            "user": user,
        }

        if dex is not None:
            payload["dex"] = dex

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def open_orders(
        self,
        user: str,
        dex: str | None = None,
    ) -> dict[str, Any]:
        """
        Get open orders for a user.

        Args:
            user: Wallet address
            dex: DEX identifier (optional)

        Returns:
            Dict containing open orders information
        """
        payload = {
            "type": Account.OPENORDERS,
            "user": user,
        }

        if dex is not None:
            payload["dex"] = dex

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def user_fills(
        self,
        user: str,
        aggregateByTime: bool = False,
    ) -> dict[str, Any]:
        """
        Get user fills/trades.

        Args:
            user: Wallet address
            aggregateByTime: Whether to aggregate fills by time

        Returns:
            Dict containing user fills information
        """
        payload = {
            "type": Account.USERFILLS,
            "user": user,
        }

        if aggregateByTime:
            payload["aggregateByTime"] = True

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def user_rate_limit(
        self,
        user: str,
    ) -> dict[str, Any]:
        """
        Get user rate limit information.

        Args:
            user: Wallet address

        Returns:
            Dict containing rate limit information
        """
        payload = {
            "type": Account.USERRATELIMIT,
            "user": user,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def order_status(
        self,
        user: str,
        oid: int | str,
    ) -> dict[str, Any]:
        """
        Get status of a specific order.

        Args:
            user: Wallet address
            oid: Order ID

        Returns:
            Dict containing order status information
        """
        # Accept either numeric order id (oid) or 16-byte hex client order id (cloid)
        # Convert decimal-string oids to int to satisfy API requirement
        normalized_oid: int | str
        if isinstance(oid, str):
            if oid.startswith("0x") or oid.startswith("0X"):
                normalized_oid = oid
            elif oid.isdigit():
                normalized_oid = int(oid)
            else:
                raise ValueError(
                    "oid must be an integer order id or a 0x-prefixed 16-byte hex cloid"
                )
        else:
            normalized_oid = oid

        payload = {
            "type": Account.ORDERSTATUS,
            "user": user,
            "oid": normalized_oid,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def historical_orders(
        self,
        user: str,
    ) -> dict[str, Any]:
        """
        Get historical orders for a user.

        Args:
            user: Wallet address

        Returns:
            Dict containing historical orders information
        """
        payload = {
            "type": Account.HISTORICALORDERS,
            "user": user,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def subaccounts(
        self,
        user: str,
    ) -> dict[str, Any]:
        """
        Get subaccounts for a user.

        Args:
            user: Wallet address

        Returns:
            Dict containing subaccounts information
        """
        payload = {
            "type": Account.SUBACCOUNTS,
            "user": user,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        # API may return JSON null for no subaccounts; normalize to empty list for callers
        if res is None:
            return []  # type: ignore[return-value]
        return res

    async def user_role(
        self,
        user: str,
    ) -> dict[str, Any]:
        """
        Get user role information.

        Args:
            user: Wallet address

        Returns:
            Dict containing user role information
        """
        payload = {
            "type": Account.USERROLE,
            "user": user,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res

    async def portfolio(
        self,
        user: str,
    ) -> dict[str, Any]:
        """
        Get portfolio information for a user.

        Args:
            user: Wallet address

        Returns:
            Dict containing portfolio information
        """
        payload = {
            "type": Account.PORTFOLIO,
            "user": user,
        }

        res = await self._request(
            method="POST",
            path=Path.INFO,
            query=payload,
            signed=False,
        )
        return res
