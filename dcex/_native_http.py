"""Helpers shared by Python managers using the Rust HTTP core."""

import json
from dataclasses import dataclass
from importlib import import_module
from types import ModuleType
from typing import Any


def load_native() -> ModuleType:
    """Load the required PyO3 module."""
    try:
        return import_module("dcex._native")
    except ImportError as exc:
        raise RuntimeError("The dcex native extension is required.") from exc


@dataclass(frozen=True)
class NativeResponse:
    """Adapt a Rust response tuple to the Python response interface."""

    status_code: int
    headers: dict[str, str]
    content: bytes

    @property
    def ok(self) -> bool:
        """Return whether the HTTP status is below 400."""
        return self.status_code < 400

    @property
    def text(self) -> str:
        """Decode the response body for existing error messages."""
        return self.content.decode(errors="replace")

    def json(self) -> Any:  # noqa: ANN401
        """Decode the response body as JSON."""
        return json.loads(self.content)
