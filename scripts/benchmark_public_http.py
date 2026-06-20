"""Benchmark Binance public HTTP latency across published Python and Rust artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUST_PUBLIC_EXAMPLE = ROOT / "crates" / "dcex" / "examples" / "public_http_benchmark.rs"
DEFAULT_PYTHON_BASELINE_VERSION = "0.21.2"
DEFAULT_PYO3_VERSION = "0.22.0"
DEFAULT_RUST_CRATE_VERSION = "0.1.0"
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
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    client = dcex.binance(preload_product_table=False, timeout=args.timeout)
    try:
        row = measure(
            args.label,
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

RUST_PUBLIC_CARGO_TOML = """
[package]
name = "dcex-public-http-release-benchmark"
version = "0.0.0"
# Match the published dcex crate workspace edition.
edition = "2021"
publish = false

[dependencies]
dcex = "={version}"
serde_json = "1"
tokio = {{ version = "1", features = ["macros", "rt-multi-thread"] }}
"""


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


def _install_pypi_package(version: str, target: Path) -> None:
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
        raise SystemExit("uv is required to install the PyPI benchmark package.") from exc

    if completed.returncode != 0:
        raise SystemExit(
            f"Unable to install PyPI dcex=={version}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def _benchmark_pypi_python(
    args: argparse.Namespace,
    *,
    version: str,
    target: str,
) -> dict[str, str | int | float]:
    with tempfile.TemporaryDirectory(prefix=f"dcex-pypi-{version}-http-bench-") as temp_name:
        temp_root = Path(temp_name)
        site_packages = temp_root / "site"
        _install_pypi_package(version, site_packages)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(site_packages)

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
                "--label",
                target,
            ],
            cwd=temp_root,
            env=env,
            context=f"PyPI dcex=={version} HTTP benchmark",
        )
    return _normalise_row(row, target)


def _benchmark_rust_native(args: argparse.Namespace) -> dict[str, str | int | float]:
    with tempfile.TemporaryDirectory(prefix="dcex-crate-http-bench-") as temp_name:
        project = Path(temp_name)
        src = project / "src"
        src.mkdir()
        (project / "Cargo.toml").write_text(
            RUST_PUBLIC_CARGO_TOML.format(version=args.rust_crate_version),
            encoding="utf-8",
        )
        (src / "main.rs").write_text(
            RUST_PUBLIC_EXAMPLE.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["DCEX_BENCH_ITERATIONS"] = str(args.iterations)
        env["DCEX_BENCH_WARMUP"] = str(args.warmup)
        env["DCEX_BENCH_OUTPUT"] = "json"
        env["DCEX_BENCH_TARGET"] = f"dcex crate {args.rust_crate_version} Rust native"
        env["DCEX_BENCH_CRATE_VERSION"] = args.rust_crate_version

        row = _run_json_command(
            ["cargo", "run", "-q", "--release"],
            cwd=project,
            env=env,
            context=f"crates.io dcex=={args.rust_crate_version} HTTP benchmark",
        )
    return _normalise_row(row, f"dcex crate {args.rust_crate_version} Rust native")


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


def _print_markdown(rows: list[dict[str, str | int | float]], args: argparse.Namespace) -> None:
    print(
        "Baseline: PyPI "
        f"`dcex=={args.python_baseline_version}` native Python implementation = 1.00x."
    )
    print(
        f"Rust-backed Python: PyPI `dcex=={args.pyo3_version}`; "
        f"Rust native: crates.io `dcex=={args.rust_crate_version}`."
    )
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
            "Benchmark Binance server-time calls across published Python and Rust artifacts."
        ),
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument(
        "--python-baseline-version",
        "--baseline-version",
        default=DEFAULT_PYTHON_BASELINE_VERSION,
        help="PyPI dcex version for the native Python baseline.",
    )
    parser.add_argument(
        "--pyo3-version",
        default=DEFAULT_PYO3_VERSION,
        help="PyPI dcex version for the Rust-backed Python package.",
    )
    parser.add_argument(
        "--rust-crate-version",
        default=DEFAULT_RUST_CRATE_VERSION,
        help="crates.io dcex version for the Rust native benchmark.",
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
        _benchmark_pypi_python(
            args,
            version=args.python_baseline_version,
            target=f"dcex {args.python_baseline_version} native Python",
        ),
        _benchmark_pypi_python(
            args,
            version=args.pyo3_version,
            target=f"dcex {args.pyo3_version} Rust-backed Python",
        ),
        _benchmark_rust_native(args),
    ]
    _add_speedups(rows)

    _print_markdown(rows, args)
    if args.csv is not None:
        _write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
