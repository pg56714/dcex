"""Benchmark Binance public HTTP latency across Python, PyO3, and Rust."""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_VERSION = "0.21.2"
CSV_FIELDS = [
    "target",
    "iterations",
    "median_ms",
    "mean_ms",
    "min_ms",
    "max_ms",
    "median_vs_baseline",
]

PYPI_PYTHON_BENCHMARK = r"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from collections.abc import Callable
from typing import Any

import dcex


def measure(
    label: str,
    callback: Callable[[], Any],
    *,
    iterations: int,
    warmup: int,
) -> dict[str, str | int | float]:
    for _ in range(warmup):
        callback()

    elapsed_ms: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        callback()
        elapsed_ms.append((time.perf_counter_ns() - start) / 1_000_000)

    return {
        "target": label,
        "iterations": iterations,
        "median_ms": statistics.median(elapsed_ms),
        "mean_ms": statistics.fmean(elapsed_ms),
        "min_ms": min(elapsed_ms),
        "max_ms": max(elapsed_ms),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup", type=int, required=True)
    parser.add_argument("--timeout", type=int, required=True)
    args = parser.parse_args()

    client = dcex.binance(preload_product_table=False, timeout=args.timeout)
    try:
        row = measure(
            "native Python baseline",
            lambda: client.get_server_time("spot"),
            iterations=args.iterations,
            warmup=args.warmup,
        )
    finally:
        client.close()

    print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()
"""


def _measure(
    label: str,
    callback: Callable[[], Any],
    *,
    iterations: int,
    warmup: int,
) -> dict[str, str | int | float]:
    for _ in range(warmup):
        callback()

    elapsed_ms: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        callback()
        elapsed_ms.append((time.perf_counter_ns() - start) / 1_000_000)

    return {
        "target": label,
        "iterations": iterations,
        "median_ms": statistics.median(elapsed_ms),
        "mean_ms": statistics.fmean(elapsed_ms),
        "min_ms": min(elapsed_ms),
        "max_ms": max(elapsed_ms),
    }


def _normalise_row(row: dict[str, Any], target: str) -> dict[str, str | int | float]:
    try:
        return {
            "target": target,
            "iterations": int(row["iterations"]),
            "median_ms": float(row["median_ms"]),
            "mean_ms": float(row["mean_ms"]),
            "min_ms": float(row["min_ms"]),
            "max_ms": float(row["max_ms"]),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit(f"Invalid benchmark row for {target}: {row}") from exc


def _run_json_command(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None,
    context: str,
) -> dict[str, Any]:
    completed = subprocess.run(  # noqa: S603
        command,
        cwd=cwd,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"{context} failed with exit code {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)

    raise SystemExit(f"{context} did not emit a JSON benchmark row:\n{completed.stdout}")


def _install_pypi_baseline(version: str, target: Path) -> None:
    try:
        completed = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "uv",
                "pip",
                "install",
                "--python",
                sys.executable,
                "--target",
                str(target),
                "--no-sources",
                f"dcex=={version}",
            ],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:  # pragma: no cover - local tooling guard
        raise SystemExit("uv is required to install the PyPI benchmark baseline.") from exc

    if completed.returncode != 0:
        raise SystemExit(
            f"Unable to install PyPI baseline dcex=={version}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def _benchmark_pypi_python(args: argparse.Namespace) -> dict[str, str | int | float]:
    with tempfile.TemporaryDirectory(prefix="dcex-pypi-bench-") as temp_name:
        temp_root = Path(temp_name)
        baseline_site = temp_root / "site"
        _install_pypi_baseline(args.baseline_version, baseline_site)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(baseline_site)

        row = _run_json_command(
            [
                sys.executable,
                "-c",
                PYPI_PYTHON_BENCHMARK,
                "--iterations",
                str(args.iterations),
                "--warmup",
                str(args.warmup),
                "--timeout",
                str(args.timeout),
            ],
            cwd=temp_root,
            env=env,
            context=f"PyPI dcex=={args.baseline_version} native Python benchmark",
        )
    return _normalise_row(row, f"dcex {args.baseline_version} native Python")


def _benchmark_pyo3_python(args: argparse.Namespace) -> dict[str, str | int | float]:
    sys.path.insert(0, str(ROOT))

    try:
        import dcex
        from dcex import _native as _unused_native  # noqa: F401
    except ImportError as exc:  # pragma: no cover - example guard
        raise SystemExit(
            "Build the native extension first: uv run maturin develop --release"
        ) from exc

    client = dcex.binance(
        preload_product_table=False,
        timeout=args.timeout,
    )
    try:
        return _measure(
            "PyO3 Python wrapper",
            lambda: client.get_server_time("spot"),
            iterations=args.iterations,
            warmup=args.warmup,
        )
    finally:
        client.close()


def _benchmark_rust_native(args: argparse.Namespace) -> dict[str, str | int | float]:
    env = os.environ.copy()
    env["DCEX_BENCH_ITERATIONS"] = str(args.iterations)
    env["DCEX_BENCH_WARMUP"] = str(args.warmup)
    env["DCEX_BENCH_OUTPUT"] = "json"

    row = _run_json_command(
        ["cargo", "run", "-q", "-p", "dcex", "--example", "public_http_benchmark", "--release"],
        cwd=ROOT,
        env=env,
        context="Rust native benchmark",
    )
    return _normalise_row(row, "Rust native")


def _add_speedups(rows: list[dict[str, str | int | float]]) -> None:
    baseline = rows[0]
    baseline_median = float(baseline["median_ms"])

    for row in rows:
        median_ms = float(row["median_ms"])
        row["median_vs_baseline"] = baseline_median / median_ms if median_ms > 0 else "n/a"


def _format_speedup(value: str | int | float) -> str:
    if isinstance(value, int | float):
        return f"{value:.2f}x"
    return value


def _print_markdown(rows: list[dict[str, str | int | float]], baseline_version: str) -> None:
    print(f"Baseline: PyPI `dcex=={baseline_version}` native Python implementation = 1.00x.")
    print()
    print("| Target | Iterations | Median ms | Mean ms | Min ms | Max ms | Median vs baseline |")
    print("| ------ | ---------- | --------- | ------- | ------ | ------ | ------------------ |")
    for row in rows:
        print(
            f"| {row['target']} | {row['iterations']} | "
            f"{float(row['median_ms']):.3f} | {float(row['mean_ms']):.3f} | "
            f"{float(row['min_ms']):.3f} | {float(row['max_ms']):.3f} | "
            f"{_format_speedup(row['median_vs_baseline'])} |"
        )


def _write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run the benchmark and print a Markdown results table."""
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark Binance server-time calls across PyPI Python, "
            "the current PyO3-backed Python wrapper, and native Rust."
        ),
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument(
        "--baseline-version",
        default=DEFAULT_BASELINE_VERSION,
        help="PyPI dcex version for the native Python baseline.",
    )
    parser.add_argument("--csv", type=Path, default=None, help="Optional local CSV output path.")
    args = parser.parse_args()

    if args.iterations <= 0:
        raise SystemExit("--iterations must be positive")
    if args.warmup < 0:
        raise SystemExit("--warmup cannot be negative")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")

    rows = [
        _benchmark_pypi_python(args),
        _benchmark_pyo3_python(args),
        _benchmark_rust_native(args),
    ]
    _add_speedups(rows)

    _print_markdown(rows, args.baseline_version)
    if args.csv is not None:
        _write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
