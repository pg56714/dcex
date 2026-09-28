"""Fund movement and batch endpoint mixins."""

import json
from typing import Any

from ..base.http_manager import BaseHTTPManager


class ClientWithdrawalsHTTP(BaseHTTPManager):
    """Withdrawals methods moved from Client."""

    private_request: Any

    _call: Any
    public_request: Any
    private_request: Any
    address: str | None
    account_index: int | None

    def create_withdrawal_signed(
        self,
        *,
        ethereum_address: str,
        amount: str,
        nonce: str,
        signature: dict[str, str],
        account_index: int | None = None,
        spot_asset_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /v1/withdraw.

        API withdrawals have no second confirmation; they execute on submit. Amount is an integer
        quantum string. Supply a wallet EIP-712 signature; no API key headers are sent.
        Source: https://docs.arcus.xyz/api-reference/exchange/submit-withdrawal
        """
        return self.private_request(
            "create_withdrawal_signed",
            **{
                "ethereumAddress": ethereum_address,
                "accountIndex": account_index,
                "spotAssetId": spot_asset_id,
                "amount": amount,
                "nonce": nonce,
                "signature": json.dumps(signature, separators=(",", ":"), allow_nan=False),
            },
        )

    def create_withdrawal(
        self, *, ethereum_address: str, amount: str, nonce: str, account_index: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        POST /v1/withdraw.

        API withdrawals have no second confirmation; they execute on submit. Amount is an integer
        quantum string. USDG only; the API key must carry operator-provisioned withdraw permission.
        Source: https://docs.arcus.xyz/api-reference/exchange/submit-withdrawal
        """
        return self.private_request(
            "create_withdrawal",
            **{
                "ethereumAddress": ethereum_address,
                "accountIndex": account_index,
                "amount": amount,
                "nonce": nonce,
            },
        )
