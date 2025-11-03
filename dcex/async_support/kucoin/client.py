"""KuCoin async client module."""
# pylint: disable=unused-argument

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(
    MarketHTTP,
    AccountHTTP,
    TradeHTTP,
):
    """KuCoin async client for trading operations."""

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the KuCoin client.

        Args:
            **args: Additional arguments passed to parent classes.
        """
        super().__init__(**args)

    async def __aenter__(self) -> "Client":
        """Async context manager entry."""
        await self.async_init()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,  # noqa: ANN401
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client and clean up resources."""
        if hasattr(self, "session") and self.session is not None:
            if not self.session.is_closed:
                # Close the session gracefully
                await self.session.aclose()
            self.session = None
