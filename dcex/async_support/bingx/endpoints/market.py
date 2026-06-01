"""BingX swap market endpoints."""

from enum import Enum


class SwapMarket(str, Enum):
    """BingX swap market API endpoints."""

    INSTRUMENT_INFO = "/openApi/swap/v2/quote/contracts"
    ORDERBOOK = "/openApi/swap/v2/quote/depth"
    PUBLIC_TRADE = "/openApi/swap/v2/quote/trades"
    KLINE = "/openApi/swap/v3/quote/klines"
    TICKER = "/openApi/swap/v2/quote/ticker"
    OPEN_INTEREST = "/openApi/swap/v2/quote/openInterest"
    MARK_PRICE_KLINE = "/openApi/swap/v1/market/markPriceKlines"

    def __str__(self) -> str:
        return self.value
