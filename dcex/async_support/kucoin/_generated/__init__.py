"""Compose generated domain methods with the handwritten client bases."""

from .._trade_http import TradeHTTP
from .account_http import GeneratedAccountHTTP
from .affiliate_http import GeneratedAffiliateHTTP
from .broker_http import GeneratedBrokerHTTP
from .copy_trading_http import GeneratedCopyTradingHTTP
from .transfers_http import GeneratedTransfersHTTP
from .withdrawals_http import GeneratedWithdrawalsHTTP


class GeneratedHTTP(
    GeneratedAccountHTTP,
    GeneratedAffiliateHTTP,
    GeneratedBrokerHTTP,
    GeneratedCopyTradingHTTP,
    GeneratedTransfersHTTP,
    GeneratedWithdrawalsHTTP,
    TradeHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
