"""Render generated artifacts in memory before checking or explicitly writing."""

import argparse
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

OUTPUTS: dict[Path, str] = {}
ROOT = Path(__file__).resolve().parents[1]


def emit(path: Path, content: str) -> None:
    """Collect output without touching the filesystem."""
    OUTPUTS[path] = content


def formatted(path: Path, content: str) -> str:
    """Use formatter stdin/stdout so check mode creates no temporary files."""
    commands = []
    if path.suffix == ".rs":
        commands = [["rustfmt", "--edition", "2024", "--emit", "stdout"]]
    elif path.suffix == ".py":
        commands = [
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--no-cache",
                "--stdin-filename",
                str(path),
                "-",
            ],
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--fix",
                "--no-cache",
                "--stdin-filename",
                str(path),
                "-",
            ],
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--no-cache",
                "--stdin-filename",
                str(path),
                "-",
            ],
        ]
    for command in commands:
        result = subprocess.run(  # noqa: S603
            command,
            input=content,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            cwd=ROOT,
        )  # noqa: S603
        if result.returncode:
            raise RuntimeError(result.stderr)
        content = result.stdout
    return content


def run(render: Callable[[], None]) -> int:
    """Require a mode and compare every rendered artifact before any write."""
    parser = argparse.ArgumentParser(description=render.__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--write", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    OUTPUTS.clear()
    render()
    outputs = {path: formatted(path, content) for path, content in OUTPUTS.items()}
    stale = [
        path
        for path, content in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]
    for path in stale:
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(outputs[path], encoding="utf-8", newline="\n")
        else:
            print(f"Generated artifact is stale: {path.relative_to(ROOT)}")
    return int(bool(stale) and not args.write)
