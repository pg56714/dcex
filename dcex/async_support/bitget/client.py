"""Bitget async client module."""
# pylint: disable=unused-argument

from typing import Any, Self

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(MarketHTTP, AccountHTTP, TradeHTTP):
    """Bitget async client."""

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """Initialize the Bitget client."""
        super().__init__(**args)

    async def __aenter__(self) -> Self:
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
        if self.session is not None and hasattr(self.session, "aclose"):
            await self.session.aclose()
        self.session = None
