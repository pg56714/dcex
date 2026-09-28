"""Copy explicit input contracts into generated endpoint metadata."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

SOURCE = Path(__file__).resolve().parents[1] / "crates/dcex/src/exchanges/input_contracts.json"


def annotate(exchange: str, endpoints: list[dict[str, Any]]) -> None:
    """Attach declarations by exact exchange, endpoint and wire field names."""
    contracts = json.loads(SOURCE.read_text(encoding="utf-8"))["exchanges"].get(exchange, {})
    for endpoint in endpoints:
        contract = contracts.get(endpoint.get("name"))
        if contract is None:
            continue
        endpoint["input_schema"] = deepcopy(contract)
