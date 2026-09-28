"""Fund movement and batch endpoint mixins."""

import json
from collections.abc import Mapping
from typing import Any

from ...base.http_manager import BaseHTTPManager


class ClientTransfersHTTP(BaseHTTPManager):
    """Transfers methods moved from Client."""

    private_request: Any
    public_request: Any

    _call: Any
    public_request: Any
    private_request: Any
    address: str | None
    account_index: int | None

    async def get_transfer_updates(self, address: str | None = None) -> Any:  # noqa: ANN401
        """Get deposits and internal-transfer updates for an address."""
        return await self.public_request(
            "get_transfer_updates", address=address or self.address, accountIndex=self.account_index
        )

    async def submit_internal_transfer(self, signed_transfer: Mapping[str, Any]) -> Any:  # noqa: ANN401
        """Submit a same-wallet EIP-712-signed collateral transfer, not a withdrawal."""
        return await self.private_request(
            "submit_internal_transfer",
            signed_transfer_json=json.dumps(dict(signed_transfer), separators=(",", ":")),
        )
