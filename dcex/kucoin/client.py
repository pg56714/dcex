"""KuCoin sync client module."""
# pylint: disable=unused-argument

from typing import Any

from ._account_http import AccountHTTP
from ._earn_http import EarnHTTP
from ._generated import GeneratedHTTP
from ._margin_http import MarginHTTP
from ._market_http import MarketHTTP


class Client(
    MarketHTTP,
    AccountHTTP,
    EarnHTTP,
    MarginHTTP,
    GeneratedHTTP,
):
    """KuCoin sync client for trading operations."""

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
