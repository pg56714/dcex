"""Compose generated domain methods with the handwritten client bases."""

from .._trade_http import TradeHTTP
from .account_http import GeneratedAccountHTTP
from .affiliate_http import GeneratedAffiliateHTTP
from .broker_http import GeneratedBrokerHTTP
from .copy_trading_http import GeneratedCopyTradingHTTP


class GeneratedHTTP(
    GeneratedAccountHTTP,
    GeneratedAffiliateHTTP,
    GeneratedBrokerHTTP,
    GeneratedCopyTradingHTTP,
    TradeHTTP,
):
    """Business-specific generated methods with compatible base precedence."""

    place_copy_futures_stop_order = vars(GeneratedCopyTradingHTTP)[
        "post_v1_copy_trade_futures_st_orders"
    ]
