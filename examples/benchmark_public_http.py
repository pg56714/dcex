"""Benchmark Binance public HTTP latency across Python, PyO3, and Rust."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CSV_FIELDS = [
    "target",
    "iterations",
    "median_ms",
    "mean_ms",
    "min_ms",
    "max_ms",
    "median_vs_main",
]

MAIN_PYTHON_BENCHMARK = r"""
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
            "main native Python",
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
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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


def _extract_git_ref(ref: str, destination: Path) -> None:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "archive", "--format=tar", ref],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode(errors="replace")
        raise SystemExit(f"Unable to archive git ref {ref!r}:\n{stderr}")

    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        archive.extractall(destination, filter="data")


def _benchmark_main_python(args: argparse.Namespace) -> dict[str, str | int | float]:
    with tempfile.TemporaryDirectory(prefix="dcex-main-bench-") as temp_name:
        checkout = Path(temp_name)
        _extract_git_ref(args.main_ref, checkout)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(checkout)

        row = _run_json_command(
            [
                sys.executable,
                "-c",
                MAIN_PYTHON_BENCHMARK,
                "--iterations",
                str(args.iterations),
                "--warmup",
                str(args.warmup),
                "--timeout",
                str(args.timeout),
            ],
            cwd=checkout,
            env=env,
            context=f"main native Python benchmark from {args.main_ref}",
        )
    return _normalise_row(row, "main native Python")


def _benchmark_pyo3_python(args: argparse.Namespace) -> dict[str, str | int | float]:
    sys.path.insert(0, str(ROOT))

    try:
        import dcex
        from dcex import _native as _unused_native  # noqa: F401
    except ImportError as exc:  # pragma: no cover - example guard
        raise SystemExit("Build the native extension first: uv run maturin develop --release") from exc

    client = dcex.binance(
        preload_product_table=False,
        timeout=args.timeout,
        use_native=True,
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
    baseline = next(row for row in rows if row["target"] == "main native Python")
    baseline_median = float(baseline["median_ms"])

    for row in rows:
        median_ms = float(row["median_ms"])
        row["median_vs_main"] = baseline_median / median_ms if median_ms > 0 else "n/a"


def _format_speedup(value: str | int | float) -> str:
    if isinstance(value, int | float):
        return f"{value:.2f}x"
    return value


def _print_markdown(rows: list[dict[str, str | int | float]]) -> None:
    print("| Target | Iterations | Median ms | Mean ms | Min ms | Max ms | Median vs main |")
    print("| ------ | ---------- | --------- | ------- | ------ | ------ | -------------- |")
    for row in rows:
        print(
            f"| {row['target']} | {row['iterations']} | "
            f"{float(row['median_ms']):.3f} | {float(row['mean_ms']):.3f} | "
            f"{float(row['min_ms']):.3f} | {float(row['max_ms']):.3f} | "
            f"{_format_speedup(row['median_vs_main'])} |"
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
            "Benchmark Binance server-time calls across main Python, "
            "the current PyO3-backed Python wrapper, and native Rust."
        ),
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--main-ref", default="main", help="Local git ref for the Python baseline.")
    parser.add_argument("--csv", type=Path, default=None, help="Optional local CSV output path.")
    args = parser.parse_args()

    if args.iterations <= 0:
        raise SystemExit("--iterations must be positive")
    if args.warmup < 0:
        raise SystemExit("--warmup cannot be negative")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")

    rows = [
        _benchmark_main_python(args),
        _benchmark_pyo3_python(args),
        _benchmark_rust_native(args),
    ]
    _add_speedups(rows)

    _print_markdown(rows)
    if args.csv is not None:
        _write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
