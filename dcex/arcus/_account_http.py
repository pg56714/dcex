# ruff: noqa: ANN401
"""Arcus HTTP implementation mixins."""

import json
from collections.abc import Sequence
from typing import Any

from ._http_manager import HTTPManager, SpotHTTPManager
from ._request_params import _params


class AccountHTTP(HTTPManager):
    """Arcus perpetual account methods."""

    def get_account(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get a wallet account snapshot."""
        return self.public_request(
            "get_account", address=address or self.address, accountIndex=self.account_index
        )

    def get_positions(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get open positions for an address."""
        return self.public_request(
            "get_positions", address=address or self.address, accountIndex=self.account_index
        )

    def get_open_orders(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get open orders for an address."""
        return self.public_request(
            "get_open_orders", address=address or self.address, accountIndex=self.account_index
        )

    def get_order_status(self, order_id: str, address: str | None = None) -> Any:  # noqa: ANN401
        """Get the current status of one order."""
        return self.public_request(
            "get_order_status",
            order_id=order_id,
            address=address or self.address,
            accountIndex=self.account_index,
        )

    def get_fills(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get account fills."""
        return self.public_request(
            "get_fills", address=address or self.address, accountIndex=self.account_index
        )

    def get_leverages(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get effective leverage and margin mode across markets."""
        return self.public_request(
            "get_leverages", address=address or self.address, accountIndex=self.account_index
        )

    def adjust_isolated_margin(self, product_symbol: str, amount: str) -> Any:  # noqa: ANN401
        """Move signed dollar amount between cross collateral and an isolated leg."""
        return self.private_request(
            "adjust_isolated_margin", product_symbol=product_symbol, amount=amount
        )

    def set_leverage(
        self, product_symbol: str, leverage: int, *, isolated: bool | None = None
    ) -> Any:  # noqa: ANN401
        """Request a leverage or margin-mode change for one market."""
        return self.private_request(
            "set_leverage", product_symbol=product_symbol, leverage=leverage, isolated=isolated
        )

    def get_account_stats(
        self,
        *,
        address: str | None = None,
        include: str | Sequence[str] | None = None,
        windows: str | Sequence[str] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/account/stats; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-account-stats.md
        """
        return self.public_request(
            "get_account_stats",
            **{
                "address": address or self.address,
                "include": include
                if isinstance(include, str) or include is None
                else ",".join(include),
                "windows": windows
                if isinstance(windows, str) or windows is None
                else ",".join(windows),
            },
        )

    def get_compliance(self, *, address: str | None = None) -> Any:  # noqa: ANN401
        """
        GET /v1/compliance; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-compliance-status.md
        """
        return self.public_request("get_compliance", **{"address": address or self.address})

    def get_rate_limit(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/rateLimit; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-current-rate-limit-usage.md
        """
        return self.public_request(
            "get_rate_limit",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_fill(
        self, *, trade_id: str, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/fill/{tradeId}; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-fill-by-id.md
        """
        return self.public_request(
            "get_fill",
            **{
                "trade_id": trade_id,
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_order_history(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        market: str | None = None,
        side: str | None = None,
        status: str | Sequence[str] | None = None,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/orders; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-order-history.md
        """
        return self.public_request(
            "get_order_history",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "market": market,
                "side": side,
                "status": status if isinstance(status, str) or status is None else ",".join(status),
                "limit": limit,
                "from": start_time,
                "to": end_time,
            },
        )

    def get_portfolio_history(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/portfolio; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-portfolio-history.md
        """
        return self.public_request(
            "get_portfolio_history",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_spot_fills(
        self,
        *,
        address: str | None = None,
        account_index: int | None = None,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/spotFills; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-spot-fills.md
        """
        return self.public_request(
            "get_spot_fills",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
                "limit": limit,
                "from": start_time,
                "to": end_time,
            },
        )

    def get_spot_positions(
        self, *, address: str | None = None, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        GET /v1/spotPositions; time bounds use epoch microseconds.

        Source: https://docs.arcus.xyz/api-reference/public/get-spot-positions.md
        """
        return self.public_request(
            "get_spot_positions",
            **{
                "address": address or self.address,
                "accountIndex": self.account_index if account_index is None else account_index,
            },
        )

    def get_api_keys(self, *, address: str | None = None, account_index: int | None = None) -> Any:  # noqa: ANN401
        """List API keys; omitting account_index lists every subaccount scope."""
        return self.public_request(
            "get_api_keys", address=address or self.address, accountIndex=account_index
        )

    def create_api_key_signed(self, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """
        Submit a caller wallet-authorized API key creation body unchanged.

        Sign the EIP-712 payload specified by the Arcus onboarding documentation.
        The trading API key cannot authorize this wallet operation.
        """
        return self.private_request(
            "create_api_key_signed", body=json.dumps(body, separators=(",", ":"), allow_nan=False)
        )

    def revoke_api_key_signed(self, body: dict[str, Any]) -> Any:  # noqa: ANN401
        """Revoke an API key with a caller wallet-authorized signed body."""
        return self.private_request(
            "revoke_api_key_signed", body=json.dumps(body, separators=(",", ":"), allow_nan=False)
        )

    def get_user_preferences(self, *, address: str | None = None) -> Any:  # noqa: ANN401
        """Public preferences for the selected wallet."""
        return self.public_request("get_user_preferences", address=address or self.address)

    def upsert_user_preferences(self, preferences: dict[str, Any]) -> Any:  # noqa: ANN401
        """Patch preferences with the native Ed25519 signing key; no address in the body."""
        return self.private_request(
            "upsert_user_preferences",
            preferences=json.dumps(preferences, separators=(",", ":"), allow_nan=False),
        )

    def delete_user_preference_signed(self, *, key: str, timestamp: int, signature: str) -> Any:  # noqa: ANN401
        """Delete a preference using caller signing headers; timestamp is nanoseconds."""
        return self.private_request(
            "delete_user_preference_signed", key=key, timestamp=timestamp, signature=signature
        )


class SpotAccountHTTP(SpotHTTPManager):
    """Arcus spot account methods."""

    def get_native_balance(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Read the Robinhood Chain ETH balance in wei, without a Perps API key."""
        return self._call("public_request", "get_native_balance", _params(address=address))

    def get_token_balance(self, token: str, address: str | None = None) -> Any:  # noqa: ANN401
        """Read an ERC-20 balance in atomic units."""
        return self._call(
            "public_request", "get_token_balance", _params(token=token, address=address)
        )

    def get_balances(
        self,
        address: str | None = None,
        *,
        tokens: list[str | dict[str, Any]] | None = None,
        include_wrapped: bool = True,
    ) -> Any:  # noqa: ANN401
        """Read ETH, listed tokens, and their wrapped representations by default."""
        return self._call(
            "public_request",
            "get_balances",
            _params(
                address=address,
                tokens_json=None if tokens is None else json.dumps(tokens),
                include_wrapped=None if include_wrapped else False,
            ),
        )

    def get_allowance(
        self, token: str, address: str | None = None, *, spender: str | None = None
    ) -> Any:  # noqa: ANN401
        """Read token allowance; the default spender is canonical Permit2."""
        return self._call(
            "public_request",
            "get_allowance",
            _params(token=token, address=address, spender=spender),
        )

    def get_trade_history(
        self,
        from_block: int,
        to_block: int | None = None,
        *,
        address: str | None = None,
        token_in: str | None = None,
        token_out: str | None = None,
        swap_shell: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Read SwapShell fills for a bounded block range; page large histories."""
        return self._call(
            "public_request",
            "get_trade_history",
            _params(
                from_block=from_block,
                to_block=to_block,
                address=address,
                token_in=token_in,
                token_out=token_out,
                swap_shell=swap_shell,
            ),
        )
