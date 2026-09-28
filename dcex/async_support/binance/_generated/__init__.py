"""Compose generated domain methods with the handwritten client bases."""

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP
from .alpha_http import GeneratedAlphaHTTP
from .c2c_http import GeneratedC2cHTTP
from .fiat_http import GeneratedFiatHTTP
from .gift_card_http import GeneratedGiftCardHTTP
from .loan_http import GeneratedLoanHTTP
from .mining_http import GeneratedMiningHTTP
from .pay_http import GeneratedPayHTTP
from .prediction_http import GeneratedPredictionHTTP
from .tax_http import GeneratedTaxHTTP
from .vip_loan_http import GeneratedVipLoanHTTP


class GeneratedHTTP(
    GeneratedAlphaHTTP,
    GeneratedC2cHTTP,
    GeneratedFiatHTTP,
    GeneratedGiftCardHTTP,
    GeneratedLoanHTTP,
    GeneratedMiningHTTP,
    GeneratedPayHTTP,
    GeneratedPredictionHTTP,
    GeneratedTaxHTTP,
    GeneratedVipLoanHTTP,
    MarketHTTP,
    TradeHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
