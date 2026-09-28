"""Compatibility aliases for public parameters renamed to snake_case."""

from collections.abc import Awaitable, Callable, Mapping
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


def wire_keywords(values: Mapping[str, Any], aliases: Mapping[str, str]) -> dict[str, Any]:
    """Restore exchange field names when a wrapper serializes its local parameters."""
    reverse = {new: old for old, new in aliases.items()}
    return {reverse.get(key, key): value for key, value in values.items()}


def legacy_keywords(aliases: Mapping[str, str]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Accept legacy keywords while exposing the canonical typed signature."""

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        def normalize(kwargs: dict[str, Any]) -> dict[str, Any]:
            result = dict(kwargs)
            for old, new in aliases.items():
                if old in result:
                    if new in result:
                        raise TypeError(f"Provide only {new}; {old} is its legacy alias.")
                    result[new] = result.pop(old)
            return result

        if iscoroutinefunction(function):

            @wraps(function)
            async def asynchronous(*args: P.args, **kwargs: P.kwargs) -> Any:  # noqa: ANN401
                return await cast(Awaitable[Any], function(*args, **normalize(kwargs)))

            asynchronous.__dict__["__legacy_keywords__"] = dict(aliases)
            return cast(Callable[P, R], asynchronous)

        @wraps(function)
        def synchronous(*args: P.args, **kwargs: P.kwargs) -> R:
            return function(*args, **normalize(kwargs))

        synchronous.__dict__["__legacy_keywords__"] = dict(aliases)
        return synchronous

    return decorate
