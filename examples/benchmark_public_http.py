"""Benchmark Python wrapper overhead for a Rust-backed public HTTP endpoint."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import dcex

try:
    from dcex import _native
except ImportError as exc:  # pragma: no cover - example guard
    raise SystemExit("Build the native extension first: uv run maturin develop --release") from exc


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


def _print_markdown(rows: list[dict[str, str | int | float]]) -> None:
    print("| Target | Iterations | Median ms | Mean ms | Min ms | Max ms |")
    print("| ------ | ---------- | --------- | ------- | ------ | ------ |")
    for row in rows:
        print(
            "| {target} | {iterations} | {median_ms:.3f} | {mean_ms:.3f} | "
            "{min_ms:.3f} | {max_ms:.3f} |".format(**row)
        )


def _write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["target", "iterations", "median_ms", "mean_ms", "min_ms", "max_ms"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run the benchmark and print a Markdown results table."""
    parser = argparse.ArgumentParser(
        description="Benchmark Binance server-time calls through Python and native PyO3 layers.",
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--csv", type=Path, default=None, help="Optional local CSV output path.")
    args = parser.parse_args()

    if args.iterations <= 0 or args.warmup < 0:
        raise SystemExit("--iterations must be positive and --warmup cannot be negative")

    python_client = dcex.binance(preload_product_table=False)
    native_client = _native.BinanceHttpClient(timeout=10)

    rows = [
        _measure(
            "Python sync wrapper",
            lambda: python_client.get_server_time("spot"),
            iterations=args.iterations,
            warmup=args.warmup,
        ),
        _measure(
            "Rust core via PyO3",
            lambda: json.loads(
                bytes(native_client.public_request("get_server_time", [("market_type", "spot")])[2])
            ),
            iterations=args.iterations,
            warmup=args.warmup,
        ),
    ]

    _print_markdown(rows)
    if args.csv is not None:
        _write_csv(args.csv, rows)

    python_client.close()


if __name__ == "__main__":
    main()
