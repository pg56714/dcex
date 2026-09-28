"""Validate explicitly declared endpoint inputs before serialization."""

import inspect
from functools import wraps
from typing import Any

from ._input_codec import CATALOG, normalize


def endpoint_schema(exchange: str, method: str, *, websocket: bool = False) -> dict[str, Any]:
    """Return a declared contract; unspecified values have no numeric inference."""
    return CATALOG["websocket" if websocket else "exchanges"].get(exchange, {}).get(method, {})


def normalize_endpoint(exchange: str, method: str, values: Any, *, websocket: bool = False) -> Any:  # noqa: ANN401
    """Normalize values using only the selected endpoint's declarations."""
    return normalize(values, schema=endpoint_schema(exchange, method, websocket=websocket))


def bind_endpoint_validation(cls: type) -> None:
    """Install signature-preserving validation on methods declared by a mixin."""
    parts = cls.__module__.split(".")
    index = 2 if len(parts) > 1 and parts[1] == "async_support" else 1
    if len(parts) <= index:
        return
    exchange = parts[index]
    schemas = CATALOG["exchanges"].get(exchange, {})
    wrapped: dict[Any, tuple[dict[str, Any], Any]] = {}
    for name, function in list(vars(cls).items()):
        if inspect.isfunction(function) and name in schemas:
            if getattr(function, "__dcex_input_schema__", None) == schemas[name]:
                continue
            previous = wrapped.get(function)
            if previous is not None and previous[0] == schemas[name]:
                setattr(cls, name, previous[1])
            else:
                validated = _validated(function, schemas[name])
                validated.__dcex_input_schema__ = schemas[name]
                wrapped[function] = (schemas[name], validated)
                setattr(cls, name, validated)


def _validated(function: Any, schema: dict[str, Any]) -> Any:  # noqa: ANN401
    signature = inspect.signature(function)
    positional = [
        parameter.name
        for parameter in signature.parameters.values()
        if parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
    ]
    aliases = getattr(function, "__legacy_keywords__", {})
    properties = schema.get("properties", {})

    def arguments(
        args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> tuple[tuple[Any, ...], dict[str, Any]]:
        normalized_args = tuple(
            normalize(value, key=positional[index], schema=properties.get(positional[index], {}))
            if index < len(positional) and positional[index] != "self"
            else value
            for index, value in enumerate(args)
        )
        normalized_kwargs = {
            key: normalize(
                value, key=key, schema=properties.get(key, properties.get(aliases.get(key), {}))
            )
            for key, value in kwargs.items()
        }
        return normalized_args, normalized_kwargs

    if inspect.iscoroutinefunction(function):

        @wraps(function)
        async def asynchronous(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            args, kwargs = arguments(args, kwargs)
            return await function(*args, **kwargs)

        return asynchronous

    @wraps(function)
    def synchronous(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        args, kwargs = arguments(args, kwargs)
        return function(*args, **kwargs)

    return synchronous
