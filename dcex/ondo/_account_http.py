"""Authenticated Ondo account methods."""

# ruff: noqa: ANN401

from typing import Any

from ._http_manager import HTTPManager
from ._withdrawals_http import AccountHTTPWithdrawalsHTTP


class AccountHTTP(AccountHTTPWithdrawalsHTTP, HTTPManager):
    def get_account(self) -> Any:
        return self._native_private("get_account")

    def get_balance(self) -> Any:
        return self._native_private("get_balance")

    def get_positions(self) -> Any:
        return self._native_private("get_positions")

    def get_deposits(self) -> Any:
        return self._native_private("get_deposits")

    def get_klines(
        self,
        market: str,
        resolution: str,
        from_time: int,
        to_time: int,
    ) -> Any:
        return self._native_private(
            "get_klines",
            market=market,
            resolution=resolution,
            from_time=from_time,
            to_time=to_time,
        )

    def get_leverage(self, market: str | None = None) -> Any:
        return self._native_private("get_leverage", market=market)

    def set_leverage(self, market: str, leverage: str) -> Any:
        return self._native_private("set_leverage", market=market, leverage=leverage)

    def get_portfolio_summary(self) -> Any:
        return self._native_private("get_portfolio_summary")

    def get_max_order_size(self, market: str, buffer: str | None = None) -> Any:
        return self._native_private("get_max_order_size", market=market, buffer=buffer)

    def get_open_order_counts(self) -> Any:
        return self._native_private("get_open_order_counts")

    def get_deposit(self, depositID: str) -> Any:
        return self._native_private("get_deposit", depositID=depositID)

    def get_deposit_addresses(
        self,
        coins: list[str],
        network: str | None = None,
        depositDestination: dict[str, object] | None = None,
    ) -> Any:
        return self._native_private(
            "get_deposit_addresses",
            coins=coins,
            network=network,
            depositDestination=depositDestination,
        )

    def export_deposits_csv(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:
        return self._native_private(
            "export_deposits_csv",
            start_time=start_time,
            end_time=end_time,
        )

    def get_address_book(self) -> Any:
        return self._native_private("get_address_book")

    def get_address_book_challenge(
        self,
        walletAddress: str,
        chainId: str,
        withdrawalAddress: str,
    ) -> Any:
        return self._native_private(
            "get_address_book_challenge",
            walletAddress=walletAddress,
            chainId=chainId,
            withdrawalAddress=withdrawalAddress,
        )

    def complete_address_book_challenge(
        self,
        id: str,
        signature: str,
        addressLabel: str | None = None,
    ) -> Any:
        return self._native_private(
            "complete_address_book_challenge",
            id=id,
            signature=signature,
            addressLabel=addressLabel,
        )

    def sandbox_deposit(
        self,
        amount: str,
        symbol: str,
        deposit_destination: dict[str, object],
        chain_id: str,
    ) -> Any:
        return self._native_private(
            "sandbox_deposit",
            amount=amount,
            symbol=symbol,
            deposit_destination=deposit_destination,
            chain_id=chain_id,
        )

    def provision_deposit_address(
        self,
        network: str,
        symbol: str,
        deposit_destination: dict[str, object],
    ) -> Any:
        return self._native_private(
            "provision_deposit_address",
            network=network,
            symbol=symbol,
            deposit_destination=deposit_destination,
        )

    def edit_address_book_entry(
        self,
        withdrawalAddress: str,
        addressLabel: str | None = None,
    ) -> Any:
        return self._native_private(
            "edit_address_book_entry",
            withdrawalAddress=withdrawalAddress,
            addressLabel=addressLabel,
        )

    def remove_address_book_entry(self, withdrawalAddress: str) -> Any:
        return self._native_private(
            "remove_address_book_entry",
            withdrawalAddress=withdrawalAddress,
        )

    def get_candles(
        self,
        market: str,
        resolution: str,
        from_time: int,
        to_time: int,
    ) -> Any:
        return self._native_private(
            "get_candles",
            market=market,
            resolution=resolution,
            from_time=from_time,
            to_time=to_time,
        )

    def get_funding_fee_payments(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "get_funding_fee_payments",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    def get_order_summaries(self) -> Any:
        return self._native_private("get_order_summaries")

    def get_liquidation_history(
        self,
        market: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> Any:
        return self._native_private(
            "get_liquidation_history",
            market=market,
            limit=limit,
            cursor=cursor,
            startTime=startTime,
            endTime=endTime,
        )

    def get_portfolio_summary_graph(self, range_: str | None = None) -> Any:
        return self._native_private("get_portfolio_summary_graph", range_=range_)
