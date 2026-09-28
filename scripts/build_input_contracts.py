"""Package the shared, explicitly declared native input contracts for Python."""

import argparse
import json
from pathlib import Path

from scripts.decimal_declarations import annotate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "crates/dcex/src/exchanges/input_contracts.json"
OUTPUT = ROOT / "dcex/_input_contracts.json"


def render() -> str:
    """Serialize committed declarations without inferring any field types."""
    return (
        json.dumps(json.loads(SOURCE.read_text(encoding="utf-8")), ensure_ascii=False, indent=2)
        + "\n"
    )


def main() -> int:
    """Write explicitly, or check packaged data without modifying it."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--write", action="store_true", help="Package the canonical native declarations"
    )
    mode.add_argument("--check", action="store_true", help="Check Python data without writing")
    args = parser.parse_args()
    content = render()
    if args.write:
        OUTPUT.write_text(content, encoding="utf-8")
    elif not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
        print("Input contracts are stale; run python -m scripts.build_input_contracts --write")
        return 1
    for path in sorted(SOURCE.parent.glob("*/schemas/*.json")):
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            continue
        annotate(path.parent.parent.name, records)
        rendered = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
        if path.read_text(encoding="utf-8") == rendered:
            continue
        if not args.write:
            print(f"Input declarations are stale in {path.relative_to(ROOT)}")
            return 1
        path.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
