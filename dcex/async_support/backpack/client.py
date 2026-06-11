"""Backpack async client module."""

from typing import Any, Self

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(MarketHTTP, AccountHTTP, TradeHTTP):
    """Backpack async client."""

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """Initialize the Backpack client."""
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
