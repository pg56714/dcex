"""Kraken private account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import FuturesAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """HTTP client for Kraken private account operations."""

    def get_spot_account_balance(
        self,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot account balances."""
        payload: dict[str, Any] = {"rebase_multiplier": rebase_multiplier}
        return self._request("POST", SpotAccount.BALANCE, query=payload, signed=True)

    def get_spot_trade_balance(
        self,
        asset: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trade balance."""
        payload: dict[str, Any] = {"asset": asset}
        return self._request("POST", SpotAccount.TRADE_BALANCE, query=payload, signed=True)

    def get_spot_open_positions(
        self,
        txid: str | None = None,
        docalcs: bool | None = None,
        consolidation: str | None = None,
        rebase_multiplier: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot margin open positions."""
        payload: dict[str, Any] = {
            "txid": txid,
            "docalcs": docalcs,
            "consolidation": consolidation,
            "rebase_multiplier": rebase_multiplier,
        }
        return self._request("POST", SpotAccount.OPEN_POSITIONS, query=payload, signed=True)

    def get_spot_ledgers(
        self,
        asset: str | None = None,
        aclass: str | None = None,
        type_: str | None = None,
        start: int | str | None = None,
        end: int | str | None = None,
        ofs: int | None = None,
        without_count: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot ledger entries."""
        payload: dict[str, Any] = {
            "asset": asset,
            "aclass": aclass,
            "type": type_,
            "start": start,
            "end": end,
            "ofs": ofs,
            "without_count": without_count,
        }
        return self._request("POST", SpotAccount.LEDGERS, query=payload, signed=True)

    def get_spot_trade_volume(
        self,
        pair: str | None = None,
        fee_info: bool | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken spot trade volume and optional fee info."""
        payload: dict[str, Any] = {"pair": pair, "fee-info": fee_info}
        return self._request("POST", SpotAccount.TRADE_VOLUME, query=payload, signed=True)

    def wallet_transfer_to_futures(
        self,
        asset: str,
        amount: str,
        from_: str = "Spot Wallet",
        to: str = "Futures Wallet",
    ) -> dict[str, Any]:
        """Transfer funds from Kraken spot wallet to Futures wallet."""
        payload: dict[str, Any] = {
            "asset": asset,
            "from": from_,
            "to": to,
            "amount": amount,
        }
        return self._request("POST", SpotAccount.WALLET_TRANSFER, query=payload, signed=True)

    def get_futures_accounts(self) -> dict[str, Any]:
        """Retrieve Kraken Futures wallets/accounts."""
        return self._request(
            "GET",
            FuturesAccount.ACCOUNTS,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    def get_futures_open_positions(self) -> dict[str, Any]:
        """Retrieve Kraken Futures open positions."""
        return self._request(
            "GET",
            FuturesAccount.OPEN_POSITIONS,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    def get_futures_fills(
        self,
        lastFillTime: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Kraken Futures account fills."""
        payload: dict[str, Any] = {"lastFillTime": lastFillTime}
        return self._request(
            "GET",
            FuturesAccount.FILLS,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    def futures_wallet_transfer(
        self,
        amount: str,
        fromAccount: str,
        toAccount: str,
        unit: str,
    ) -> dict[str, Any]:
        """Transfer funds between Kraken Futures cash and margin accounts."""
        payload: dict[str, Any] = {
            "amount": amount,
            "fromAccount": fromAccount,
            "toAccount": toAccount,
            "unit": unit.lower(),
        }
        return self._request(
            "POST",
            FuturesAccount.TRANSFER,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )

    def withdraw_futures_to_spot_wallet(
        self,
        amount: str,
        currency: str,
        sourceWallet: str | None = None,
    ) -> dict[str, Any]:
        """Withdraw funds from Kraken Futures to the Spot wallet."""
        payload: dict[str, Any] = {
            "amount": amount,
            "currency": currency.lower(),
            "sourceWallet": sourceWallet,
        }
        return self._request(
            "POST",
            FuturesAccount.WITHDRAWAL,
            query=payload,
            signed=True,
            base_url=self.futures_base_url,
            auth_type="futures",
        )
