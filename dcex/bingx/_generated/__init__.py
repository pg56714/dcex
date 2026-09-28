"""Compose generated domain methods with the handwritten client bases."""

from .._market_http import MarketHTTP
from .affiliate_http import GeneratedAffiliateHTTP
from .announcements_http import GeneratedAnnouncementsHTTP
from .coin_futures_http import GeneratedCoinFuturesHTTP
from .copy_trading_http import GeneratedCopyTradingHTTP
from .deposits_http import GeneratedDepositsHTTP
from .earn_http import GeneratedEarnHTTP
from .market_http import GeneratedMarketHTTP


class GeneratedHTTP(
    GeneratedAffiliateHTTP,
    GeneratedAnnouncementsHTTP,
    GeneratedCoinFuturesHTTP,
    GeneratedCopyTradingHTTP,
    GeneratedDepositsHTTP,
    GeneratedEarnHTTP,
    GeneratedMarketHTTP,
    MarketHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
