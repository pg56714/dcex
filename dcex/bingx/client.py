"""BingX sync client module."""
# pylint: disable=unused-argument

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(
    TradeHTTP,
    MarketHTTP,
    AccountHTTP,
):
    """BingX sync client for trading operations."""

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the BingX client.

        Args:
            **args: Additional arguments passed to parent classes.
        """
        super().__init__(**args)

    def __enter__(self) -> "Client":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,  # noqa: ANN401
    ) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Release native HTTP resources held by the Rust extension."""
        self._native_client = None
