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


class SpotMarket(str, Enum):
    """BingX spot market API endpoints."""

    SYMBOLS = "/openApi/spot/v1/common/symbols"
    ORDERBOOK = "/openApi/spot/v1/market/depth"
    ORDERBOOK_V2 = "/openApi/spot/v2/market/depth"
    PUBLIC_TRADE = "/openApi/spot/v1/market/trades"
    KLINE = "/openApi/spot/v1/market/kline"
    KLINE_V2 = "/openApi/spot/v2/market/kline"
    TICKER = "/openApi/spot/v1/ticker/24hr"
    BOOK_TICKER = "/openApi/spot/v1/ticker/bookTicker"
    PRICE_TICKER = "/openApi/spot/v2/ticker/price"

    def __str__(self) -> str:
        return self.value
