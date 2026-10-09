"""Lossless values governed exclusively by explicit endpoint field schemas."""

import json
import re
from collections.abc import Mapping
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

CATALOG = json.loads(Path(__file__).with_name("_input_contracts.json").read_text(encoding="utf-8"))
_PLAIN = re.compile(r"[0-9]+(?:\.[0-9]+)?\Z", re.ASCII)


def resolve_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve a shared component from the committed catalog."""
    if reference := schema.get("$ref"):
        return CATALOG["definitions"][reference.removeprefix("#/definitions/")]
    return schema


def contextual_schema(schema: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    """Allow zero when one declared group of sibling conditions matches."""
    conditions = schema.get("x-zero-when")
    if not conditions:
        return schema
    groups = conditions if isinstance(conditions, list) else [conditions]
    if conditions and any(
        all(values.get(key) in allowed for key, allowed in group.items()) for group in groups
    ):
        return {**schema, "x-positive": False}
    return schema


def normalize(
    value: Any,  # noqa: ANN401
    key: str = "",
    *,
    signed_fields: frozenset[str] = frozenset(),
    schema: dict[str, Any] | None = None,
) -> Any:  # noqa: ANN401, ARG001
    """Reject lossy declared decimals; never infer a type from a field name."""
    schema = resolve_schema(schema or {})
    if isinstance(value, Enum):
        value = value.value
    if value is None:
        return None
    if isinstance(value, str) and not value.strip() and schema.get("x-empty-as-absent"):
        return value
    if (
        isinstance(value, str)
        and schema.get("x-delimited-string")
        and not value.lstrip().startswith("[")
    ):
        if not all(part.strip() for part in value.split(",")):
            raise ValueError(f"{key} requires nonempty comma-separated identifiers")
        return value.split(",")
    if isinstance(value, str) and schema.get("type") in {"object", "array"}:
        try:
            parsed = json.loads(value.strip(), parse_float=str)
        except json.JSONDecodeError as error:
            raise ValueError(f"{key} must be a JSON {schema['type']}") from error
        normalized = normalize(parsed, key, schema=schema)
        # Array wrappers may serialize again or expand repeated query keys.
        # Decode once at the public boundary to preserve their wire shape.
        return normalized if schema.get("type") == "array" else value
    if schema.get("type") == "object" and not isinstance(value, dict):
        raise ValueError(f"{key} must be a JSON object")
    if schema.get("x-nonempty-object") and value == {}:
        raise ValueError(f"{key} must be a nonempty JSON object")
    if schema.get("format") == "decimal":
        if isinstance(value, float | bool):
            raise ValueError(f"{key} requires an exact decimal string or Decimal, not float/bool")
        if not isinstance(value, str | int | Decimal):
            raise ValueError(f"{key} requires a plain decimal string")
        text = format(value, "f") if isinstance(value, Decimal) else str(value)
        if text in schema.get("x-decimal-sentinels", []):
            return text
        relative = schema.get("x-relative")
        if relative and re.fullmatch(CATALOG["definitions"][relative]["pattern"], text, re.ASCII):
            return text
        digits = text.removesuffix("%") if schema.get("x-percent") else text
        digits = digits.removeprefix("-") if schema.get("x-signed") else digits
        if not _PLAIN.fullmatch(digits):
            raise ValueError(f"{key} requires a plain decimal string")
        if "x-minimum" in schema:
            number, minimum = Decimal(text), Decimal(schema["x-minimum"])
            if (
                number < minimum
                or number == minimum
                and schema.get("x-exclusive-minimum")
                or number == 0
                and schema.get("x-nonzero")
            ):
                raise ValueError(f"{key} requires a decimal within its declared range")
        if schema.get("x-positive") and not any(char in "123456789" for char in digits):
            raise ValueError(f"{key} must be a positive plain decimal string")
        if schema.get("x-percent-range") and text.endswith("%") and not 0 < Decimal(digits) <= 100:
            raise ValueError(
                f"{key} requires a decimal percentage greater than 0% and at most 100%"
            )
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError(f"{key or 'decimal'} must be finite")
        return format(value, "f")
    if isinstance(value, dict):
        if forbidden := set(value).intersection(schema.get("x-forbidden-keys", [])):
            raise ValueError(f"{key} contains unsupported fields: {', '.join(sorted(forbidden))}")
        properties = schema.get("properties", {})
        return {
            name: normalize(
                child, str(name), schema=contextual_schema(properties.get(name, {}), value)
            )
            for name, child in value.items()
        }
    if isinstance(value, list | tuple):
        return [normalize(child, key, schema=schema.get("items", {})) for child in value]
    return value


# Official wire names that Python spells with a trailing underscore: ``from`` is a keyword
# and ``type``/``range`` shadow builtins, so keyword arguments use ``from_``/``type_``/``range_``.
PYTHON_RESERVED_KEYWORDS = {"from_": "from", "type_": "type", "range_": "range"}


def normalize_params(values: dict[str, Any]) -> dict[str, Any]:
    """Restore official names for reserved-word arguments and keep exact values."""
    return normalize(
        {PYTHON_RESERVED_KEYWORDS.get(key, key): value for key, value in values.items()}
    )


def encode_json(value: Any, *, signed_fields: tuple[str, ...] = (), **options: Any) -> str:  # noqa: ANN401
    """Keep the existing call signature; endpoint schemas now own signed opt-ins."""
    return json.dumps(normalize(value, signed_fields=frozenset(signed_fields)), **options)


def wire_keywords(values: Mapping[str, Any], fields: Mapping[str, str]) -> dict[str, Any]:
    """Restore official wire field names when serializing Python parameters."""
    reverse = {python: wire for wire, python in fields.items()}
    return {reverse.get(key, key): value for key, value in values.items()}
