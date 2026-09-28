"""Lossless values at the Python/native schema boundary."""

import json
import re
from decimal import Decimal
from enum import Enum
from typing import Any

# Wire names, normalized only for Python snake_case aliases. This deliberately
# excludes signed deltas, percentages, prices expressed as offsets, and IDs.
_DECIMALS = frozenset(
    "price quantity qty amount size volume vol notional funds sz px amt "
    "submittedquantity submittedprice limitprice stopprice triggerprice "
    "activationprice callbackrate newqty newquantity origqty quoteorderqty "
    "baseqty quoteqty orderqty orderprice orderamount minprice maxprice "
    "lowerprice upperprice investment totalinvestment reservedmargin "
    "takeprofit stoploss tpprice slprice tptriggerpx sltriggerpx "
    "tpordpx slordpx execqty execprice baseamount quoteamount "
    "newprice entryprice bidprice askprice openprice openamount trailingamount monitorprice "
    "takeprofitprice stoplossprice investmentamount tokenizedassetamount "
    "underlyingassetamount price2".split()
)
_PLAIN = re.compile(r"[0-9]+(?:\.[0-9]+)?\Z", re.ASCII)


def normalize(value: Any, key: str = "", *, signed_fields: frozenset[str] = frozenset()) -> Any:  # noqa: ANN401
    """Preserve exact decimals and reject lossy financial values before str()."""
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, float) and key.replace("_", "").lower() in _DECIMALS:
        raise ValueError(
            f"{key or 'number'} requires an exact decimal string or Decimal, not float"
        )
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"{key or 'decimal'} must be finite")
        value = format(value, "f")
    if isinstance(value, dict):
        return {k: normalize(v, str(k), signed_fields=signed_fields) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [normalize(item, key, signed_fields=signed_fields) for item in value]
    if isinstance(value, str) and value.startswith(("{", "[")):
        # Already encoded JSON is checked against the native field schema;
        # parsing it through Python floats would lose its declared wire types.
        return value
    if key.replace("_", "").lower() in _DECIMALS and value is not None:
        if isinstance(value, bool):
            raise ValueError(f"{key} requires a plain decimal string or Decimal, not float/bool")
        text = str(value)
        normalized_key = key.replace("_", "").lower()
        if normalized_key == "size" and text == "":
            return value  # Documented Bitget TPSL no-change selector.
        if normalized_key in {"price", "price2"} and re.fullmatch(
            r"(?:\+[0-9]+(?:\.[0-9]+)?%?|-[0-9]+(?:\.[0-9]+)?%)", text
        ):
            return value  # Native Kraken relative-price adapter checks context.
        # Margin adjustments use a signed amount. The endpoint's native schema
        # distinguishes that delta from withdrawals and other positive amounts.
        if (normalized_key == "amount" or normalized_key in signed_fields) and text.startswith("-"):
            text = text[1:]
        # OKX defines -1 as the market-price selector for these two fields.
        if normalized_key in {"tpordpx", "slordpx"} and text == "-1":
            return value
        if not isinstance(value, str | int) or not _PLAIN.fullmatch(text):
            if normalized_key == "quantity" and text.startswith("-"):
                raise ValueError("quantity must be positive plain decimal string")
            raise ValueError(f"{key} requires a nonnegative plain decimal string")
    return value


def normalize_params(values: dict[str, Any]) -> dict[str, Any]:
    """Normalize named inputs without changing their order or None handling."""
    return {key: normalize(value, key) for key, value in values.items()}


def encode_json(value: Any, *, signed_fields: tuple[str, ...] = (), **options: Any) -> str:  # noqa: ANN401
    """Encode structured native parameters without losing decimal precision."""
    return json.dumps(normalize(value, signed_fields=frozenset(signed_fields)), **options)
