"""Compose generated domain methods with the handwritten client bases."""

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP
from .alpha_http import GeneratedAlphaHTTP
from .batch_http import GeneratedBatchHTTP
from .c2c_http import GeneratedC2cHTTP
from .fiat_http import GeneratedFiatHTTP
from .gift_card_http import GeneratedGiftCardHTTP
from .loan_http import GeneratedLoanHTTP
from .mining_http import GeneratedMiningHTTP
from .pay_http import GeneratedPayHTTP
from .prediction_http import GeneratedPredictionHTTP
from .tax_http import GeneratedTaxHTTP
from .transfers_http import GeneratedTransfersHTTP
from .vip_loan_http import GeneratedVipLoanHTTP
from .withdrawals_http import GeneratedWithdrawalsHTTP


class GeneratedHTTP(
    GeneratedAlphaHTTP,
    GeneratedBatchHTTP,
    GeneratedC2cHTTP,
    GeneratedFiatHTTP,
    GeneratedGiftCardHTTP,
    GeneratedLoanHTTP,
    GeneratedMiningHTTP,
    GeneratedPayHTTP,
    GeneratedPredictionHTTP,
    GeneratedTaxHTTP,
    GeneratedTransfersHTTP,
    GeneratedVipLoanHTTP,
    GeneratedWithdrawalsHTTP,
    MarketHTTP,
    TradeHTTP,
):
    """Business-specific generated methods with compatible base precedence."""
