"""Independent request expectations asserted by the offline wire suites."""
import json
from pathlib import Path

EXPECTED_VERBS = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures/endpoint_wire_verbs.json").read_text(encoding="utf-8")
)
