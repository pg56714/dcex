"""Extended async client module."""

from typing import Any, Self

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(MarketHTTP, AccountHTTP, TradeHTTP):
    """Extended async client."""

    def __init__(self, **args: Any) -> None:  # noqa: ANN401
        super().__init__(**args)

    async def __aenter__(self) -> Self:
        await self.async_init()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,  # noqa: ANN401
    ) -> None:
        await self.close()
