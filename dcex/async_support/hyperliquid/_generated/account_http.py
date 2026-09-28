"""Generated hyperliquid account HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedAccountHTTP(TradeHTTP):
    """Account API methods."""

    async def get_user_to_multi_sig_signers(self, *, user: str) -> Any:  # noqa: ANN401
        """
        Query userToMultiSigSigners.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/info.py#L626
        """
        return await self._native_public(
            "get_user_to_multi_sig_signers", self._native_params(user=user)
        )

    async def get_extra_agents(self, *, user: str) -> Any:  # noqa: ANN401
        """
        Query extraAgents.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/info.py#L763
        """
        return await self._native_public("get_extra_agents", self._native_params(user=user))
