"""Shared decimal serialization for synchronous and asynchronous Binance batches."""

from decimal import Decimal
from json import dumps
from typing import Any

_DECIMAL_FIELDS = frozenset({"quantity", "price", "stopPrice", "activationPrice", "callbackRate"})


def encode_batch_orders(orders: list[dict[str, Any]]) -> str:
    """Encode decimal strings or Decimal amounts without rounding or mutating inputs."""
    normalized = []
    for order in orders:
        item = dict(order)
        for field in _DECIMAL_FIELDS & item.keys():
            value = item[field]
            if isinstance(value, Decimal):
                if not value.is_finite() or value <= 0:
                    raise ValueError(f"{field} must be a positive decimal amount")
                item[field] = format(value, "f")
            elif not isinstance(value, str):
                # Match the Rust request validator's ValueError contract.
                raise ValueError(  # noqa: TRY004
                    f"{field} must be a decimal string or Decimal; floats are rejected"
                )
        normalized.append(item)
    return dumps(normalized)
