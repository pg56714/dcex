"""Benchmark local Lighter core across published Python and Rust artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUST_CORE_EXAMPLE = ROOT / "crates" / "dcex" / "examples" / "core_local_benchmark.rs"
DEFAULT_PYTHON_BASELINE_VERSION = "0.21.2"
DEFAULT_PYO3_VERSION = "0.26.3"
DEFAULT_RUST_CRATE_VERSION = "0.4.4"

CSV_FIELDS = [
    "operation",
    "python_median_ms",
    "pyo3_median_ms",
    "rust_median_ms",
    "rust_backed_python_speedup",
    "rust_native_speedup",
]

# This embedded script intentionally imports the historical PyPI baseline.
# It is not a runtime dependency of the current package.
PYPI_PYTHON_CORE_BENCHMARK = r"""
from __future__ import annotations

import argparse
import base64
import gc
import json
import statistics
import time
from collections.abc import Callable

from dcex.lighter import _crypto
from dcex.lighter.signer_client import _transaction_hash

HASH_VALUES = [
    3451004116618606032,
    11263134342958518251,
    10957204882857370932,
    5369763041201481933,
    7695734348563036858,
    1393419330378128434,
    7387917082382606332,
]
PRIVATE_KEY_LIMBS = [
    12235002942052073545,
    1175977464658719998,
    8536934969147463310,
    6524687619313720391,
    2922072024880609112,
]
NONCE_LIMBS = [
    5245666847777449560,
    15178169970799106939,
    4403065012435293749,
    15306540389399388999,
    8935555081913173844,
]
MESSAGE_HASH = b"".join(
    limb.to_bytes(8, "little")
    for limb in [
        8398652514106806347,
        11069112711939986896,
        9732488227085561369,
        18076754337204438535,
        17155407358725346236,
    ]
)
TX_VALUES = [
    304,
    14,
    11,
    1_590_000,
    12,
    3,
    4,
    5,
    6,
    7,
    1,
    0,
    2,
    0,
    0,
    8,
]
TX_ATTRIBUTES = [(1, 9), (2, 10), (4, 1)]
TX_PAYLOAD_JSON = (
    b'{"AccountIndex":12,"ApiKeyIndex":3,"MarketIndex":4,"ClientOrderIndex":5,'
    b'"BaseAmount":6,"Price":7,"IsAsk":1,"Type":0,"TimeInForce":2,'
    b'"ReduceOnly":0,"TriggerPrice":0,"OrderExpiry":8,"ExpiredAt":1590000,"Nonce":11}'
)


def _scalar_bytes(limbs: list[int]) -> bytes:
    return b"".join(limb.to_bytes(8, "little") for limb in limbs)


PRIVATE_KEY = _crypto.private_key_from_bytes(_scalar_bytes(PRIVATE_KEY_LIMBS))
NONCE = int.from_bytes(_scalar_bytes(NONCE_LIMBS), "little") % _crypto._SCALAR_ORDER


def _measure(
    callback: Callable[[], object],
    *,
    iterations: int,
    warmup: int,
    inner_loops: int,
    target_batch_ms: float,
    max_inner_loops: int,
) -> float:
    gc.collect()
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        if inner_loops == 0:
            inner_loops = _calibrate_inner_loops(
                callback,
                target_batch_ms=target_batch_ms,
                max_inner_loops=max_inner_loops,
            )

        for _ in range(warmup):
            for _ in range(inner_loops):
                callback()

        elapsed_ms: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            for _ in range(inner_loops):
                callback()
            elapsed_ms.append((time.perf_counter_ns() - start) / inner_loops / 1_000_000)
        return statistics.median(elapsed_ms)
    finally:
        if gc_was_enabled:
            gc.enable()


def _calibrate_inner_loops(
    callback: Callable[[], object],
    *,
    target_batch_ms: float,
    max_inner_loops: int,
) -> int:
    inner_loops = 1
    while True:
        start = time.perf_counter_ns()
        for _ in range(inner_loops):
            callback()
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        if elapsed_ms >= target_batch_ms or inner_loops >= max_inner_loops:
            return inner_loops

        scale = max(2, int((target_batch_ms / max(elapsed_ms, 1e-9)) + 0.999999))
        inner_loops = min(max_inner_loops, inner_loops * scale)


def _python_hash() -> bytes:
    return _crypto.poseidon_hash_bytes(HASH_VALUES)


def _python_signature() -> bytes:
    return _crypto.schnorr_sign(MESSAGE_HASH, PRIVATE_KEY, NONCE)


def _python_transaction_payload() -> bytes:
    message_hash = _transaction_hash(TX_VALUES, dict(TX_ATTRIBUTES))
    payload = json.loads(TX_PAYLOAD_JSON)
    payload["Sig"] = base64.b64encode(
        _crypto.schnorr_sign(message_hash, PRIVATE_KEY, NONCE)
    ).decode()
    payload["L2TxAttributes"] = dict(TX_ATTRIBUTES) or None
    return json.dumps(payload, separators=(",", ":")).encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup", type=int, required=True)
    parser.add_argument("--inner-loops", type=int, required=True)
    parser.add_argument("--target-batch-ms", type=float, required=True)
    parser.add_argument("--max-inner-loops", type=int, required=True)
    args = parser.parse_args()

    rows = [
        {
            "operation": "Cryptographic hash",
            "python_median_ms": _measure(
                _python_hash,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
                target_batch_ms=args.target_batch_ms,
                max_inner_loops=args.max_inner_loops,
            ),
        },
        {
            "operation": "Schnorr signature",
            "python_median_ms": _measure(
                _python_signature,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
                target_batch_ms=args.target_batch_ms,
                max_inner_loops=args.max_inner_loops,
            ),
        },
        {
            "operation": "Transaction payload signing",
            "python_median_ms": _measure(
                _python_transaction_payload,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
                target_batch_ms=args.target_batch_ms,
                max_inner_loops=args.max_inner_loops,
            ),
        },
    ]
    print(json.dumps({"rows": rows}, sort_keys=True))


if __name__ == "__main__":
    main()
"""

RUST_CORE_CARGO_TOML = """
[package]
name = "dcex-core-release-benchmark"
version = "0.0.0"
# Match the published dcex crate workspace edition.
edition = "2021"
publish = false

[dependencies]
dcex = "={version}"
serde_json = "1"
"""

PYPI_PYO3_CORE_BENCHMARK = r"""
from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
from collections.abc import Callable

from dcex import _native

HASH_VALUES = [
    3451004116618606032,
    11263134342958518251,
    10957204882857370932,
    5369763041201481933,
    7695734348563036858,
    1393419330378128434,
    7387917082382606332,
]
PRIVATE_KEY_LIMBS = [
    12235002942052073545,
    1175977464658719998,
    8536934969147463310,
    6524687619313720391,
    2922072024880609112,
]
NONCE_LIMBS = [
    5245666847777449560,
    15178169970799106939,
    4403065012435293749,
    15306540389399388999,
    8935555081913173844,
]
MESSAGE_HASH = b"".join(
    limb.to_bytes(8, "little")
    for limb in [
        8398652514106806347,
        11069112711939986896,
        9732488227085561369,
        18076754337204438535,
        17155407358725346236,
    ]
)
TX_VALUES = [
    304,
    14,
    11,
    1_590_000,
    12,
    3,
    4,
    5,
    6,
    7,
    1,
    0,
    2,
    0,
    0,
    8,
]
TX_ATTRIBUTES = [(1, 9), (2, 10), (4, 1)]
TX_PAYLOAD_JSON = (
    b'{"AccountIndex":12,"ApiKeyIndex":3,"MarketIndex":4,"ClientOrderIndex":5,'
    b'"BaseAmount":6,"Price":7,"IsAsk":1,"Type":0,"TimeInForce":2,'
    b'"ReduceOnly":0,"TriggerPrice":0,"OrderExpiry":8,"ExpiredAt":1590000,"Nonce":11}'
)


def _scalar_bytes(limbs: list[int]) -> bytes:
    return b"".join(limb.to_bytes(8, "little") for limb in limbs)


PRIVATE_KEY_BYTES = _scalar_bytes(PRIVATE_KEY_LIMBS)
NONCE_BYTES = _scalar_bytes(NONCE_LIMBS)


def _measure(
    callback: Callable[[], object],
    *,
    iterations: int,
    warmup: int,
    inner_loops: int,
    target_batch_ms: float,
    max_inner_loops: int,
) -> float:
    gc.collect()
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        if inner_loops == 0:
            inner_loops = _calibrate_inner_loops(
                callback,
                target_batch_ms=target_batch_ms,
                max_inner_loops=max_inner_loops,
            )

        for _ in range(warmup):
            for _ in range(inner_loops):
                callback()

        elapsed_ms: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter_ns()
            for _ in range(inner_loops):
                callback()
            elapsed_ms.append((time.perf_counter_ns() - start) / inner_loops / 1_000_000)
        return statistics.median(elapsed_ms)
    finally:
        if gc_was_enabled:
            gc.enable()


def _calibrate_inner_loops(
    callback: Callable[[], object],
    *,
    target_batch_ms: float,
    max_inner_loops: int,
) -> int:
    inner_loops = 1
    while True:
        start = time.perf_counter_ns()
        for _ in range(inner_loops):
            callback()
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
        if elapsed_ms >= target_batch_ms or inner_loops >= max_inner_loops:
            return inner_loops

        scale = max(2, int((target_batch_ms / max(elapsed_ms, 1e-9)) + 0.999999))
        inner_loops = min(max_inner_loops, inner_loops * scale)


def _pyo3_hash() -> bytes:
    return bytes(_native.lighter_poseidon_hash_bytes(HASH_VALUES))


def _pyo3_signature() -> bytes:
    return bytes(_native.lighter_schnorr_sign(MESSAGE_HASH, PRIVATE_KEY_BYTES, NONCE_BYTES))


def _pyo3_transaction_payload() -> bytes:
    tx_info, _message_hash = _native.lighter_sign_transaction(
        TX_VALUES,
        TX_ATTRIBUTES,
        TX_PAYLOAD_JSON,
        PRIVATE_KEY_BYTES,
        NONCE_BYTES,
    )
    return bytes(tx_info)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument("--warmup", type=int, required=True)
    parser.add_argument("--inner-loops", type=int, required=True)
    parser.add_argument("--target-batch-ms", type=float, required=True)
    parser.add_argument("--max-inner-loops", type=int, required=True)
    args = parser.parse_args()

    rows = [
        {
            "operation": "Cryptographic hash",
            "pyo3_median_ms": _measure(
                _pyo3_hash,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
                target_batch_ms=args.target_batch_ms,
                max_inner_loops=args.max_inner_loops,
            ),
        },
        {
            "operation": "Schnorr signature",
            "pyo3_median_ms": _measure(
                _pyo3_signature,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
                target_batch_ms=args.target_batch_ms,
                max_inner_loops=args.max_inner_loops,
            ),
        },
        {
            "operation": "Transaction payload signing",
            "pyo3_median_ms": _measure(
                _pyo3_transaction_payload,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
                target_batch_ms=args.target_batch_ms,
                max_inner_loops=args.max_inner_loops,
            ),
        },
    ]
    print(json.dumps({"rows": rows}, sort_keys=True))


if __name__ == "__main__":
    main()
"""


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

    raise SystemExit(f"{context} did not emit JSON:\n{completed.stdout}")


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


def _median_metric_by_operation(
    payloads: list[dict[str, Any]],
    metric: str,
) -> dict[str, float]:
    values_by_operation: dict[str, list[float]] = {}
    for payload in payloads:
        for row in payload["rows"]:
            values_by_operation.setdefault(str(row["operation"]), []).append(float(row[metric]))
    return {
        operation: statistics.median(values) for operation, values in values_by_operation.items()
    }


def _run_pypi_core_benchmark(
    *,
    version: str,
    script: str,
    metric: str,
    args: argparse.Namespace,
) -> dict[str, float]:
    with tempfile.TemporaryDirectory(prefix=f"dcex-pypi-{version}-core-bench-") as temp_name:
        temp_root = Path(temp_name)
        site_packages = temp_root / "site"
        _install_pypi_package(version, site_packages)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(site_packages)

        payloads = [
            _run_json_command(
                [
                    sys.executable,
                    "-c",
                    script,
                    "--iterations",
                    str(args.iterations),
                    "--warmup",
                    str(args.warmup),
                    "--inner-loops",
                    str(args.inner_loops),
                    "--target-batch-ms",
                    str(args.target_batch_ms),
                    "--max-inner-loops",
                    str(args.max_inner_loops),
                ],
                cwd=temp_root,
                env=env,
                context=(
                    f"PyPI dcex=={version} core benchmark run {run_index + 1}/{args.process_runs}"
                ),
            )
            for run_index in range(args.process_runs)
        ]
    return _median_metric_by_operation(payloads, metric)


def _run_rust_benchmark(args: argparse.Namespace) -> dict[str, float]:
    with tempfile.TemporaryDirectory(prefix="dcex-crate-core-bench-") as temp_name:
        project = Path(temp_name)
        src = project / "src"
        src.mkdir()
        (project / "Cargo.toml").write_text(
            RUST_CORE_CARGO_TOML.format(version=args.rust_crate_version),
            encoding="utf-8",
        )
        (src / "main.rs").write_text(
            RUST_CORE_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8"
        )

        env = os.environ.copy()
        env["DCEX_BENCH_ITERATIONS"] = str(args.iterations)
        env["DCEX_BENCH_WARMUP"] = str(args.warmup)
        env["DCEX_BENCH_INNER_LOOPS"] = str(args.inner_loops)
        env["DCEX_BENCH_TARGET_BATCH_MS"] = str(args.target_batch_ms)
        env["DCEX_BENCH_MAX_INNER_LOOPS"] = str(args.max_inner_loops)
        env["DCEX_BENCH_OUTPUT"] = "json"
        env["DCEX_BENCH_TARGET"] = f"dcex crate {args.rust_crate_version} Rust native"
        env["DCEX_BENCH_CRATE_VERSION"] = args.rust_crate_version

        payloads = [
            _run_json_command(
                ["cargo", "run", "-q", "--release"],
                cwd=project,
                env=env,
                context=(
                    f"crates.io dcex=={args.rust_crate_version} core benchmark "
                    f"run {run_index + 1}/{args.process_runs}"
                ),
            )
            for run_index in range(args.process_runs)
        ]
    return _median_metric_by_operation(payloads, "rust_median_ms")


def _benchmark_operation(
    operation: str,
    *,
    python_median_ms: float,
    pyo3_median_ms: float,
    rust_median_ms: float,
) -> dict[str, str | float]:
    return {
        "operation": operation,
        "python_median_ms": python_median_ms,
        "pyo3_median_ms": pyo3_median_ms,
        "rust_median_ms": rust_median_ms,
        "rust_backed_python_speedup": python_median_ms / pyo3_median_ms,
        "rust_native_speedup": python_median_ms / rust_median_ms,
    }


def _print_markdown(rows: list[dict[str, str | float]], args: argparse.Namespace) -> None:
    print(
        "Baseline: PyPI "
        f"`dcex=={args.python_baseline_version}` native Python implementation = 1.00x."
    )
    print(
        f"Rust-backed Python: PyPI `dcex=={args.pyo3_version}`; "
        f"Rust native: crates.io `dcex=={args.rust_crate_version}`."
    )
    print()
    print("| Operation | Rust-backed Python | Rust native |")
    print("| --------- | ------------------ | ----------- |")
    for row in rows:
        print(
            f"| {row['operation']} | "
            f"{float(row['rust_backed_python_speedup']):.2f}x | "
            f"{float(row['rust_native_speedup']):.2f}x |"
        )


def _write_csv(path: Path, rows: list[dict[str, str | float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run local CPU-bound benchmark pairs and print speedup multipliers."""
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark local Lighter CPU-bound operations across published "
            "Python and Rust artifacts."
        ),
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument(
        "--inner-loops",
        type=int,
        default=0,
        help="Fixed loops per timed sample. Use 0 to auto-calibrate per operation.",
    )
    parser.add_argument(
        "--target-batch-ms",
        type=float,
        default=100.0,
        help="Target elapsed milliseconds for each auto-calibrated timed sample.",
    )
    parser.add_argument(
        "--max-inner-loops",
        type=int,
        default=1_000_000,
        help="Upper bound for auto-calibrated loops per timed sample.",
    )
    parser.add_argument(
        "--process-runs",
        type=int,
        default=3,
        help="Benchmark process runs per artifact; operation medians are aggregated with median.",
    )
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
    if args.inner_loops < 0:
        raise SystemExit("--inner-loops cannot be negative")
    if args.target_batch_ms <= 0:
        raise SystemExit("--target-batch-ms must be positive")
    if args.max_inner_loops <= 0:
        raise SystemExit("--max-inner-loops must be positive")
    if args.process_runs <= 0:
        raise SystemExit("--process-runs must be positive")

    python_rows = _run_pypi_core_benchmark(
        version=args.python_baseline_version,
        script=PYPI_PYTHON_CORE_BENCHMARK,
        metric="python_median_ms",
        args=args,
    )
    pyo3_rows = _run_pypi_core_benchmark(
        version=args.pyo3_version,
        script=PYPI_PYO3_CORE_BENCHMARK,
        metric="pyo3_median_ms",
        args=args,
    )
    rust_rows = _run_rust_benchmark(args)
    rows = [
        _benchmark_operation(
            "Cryptographic hash",
            python_median_ms=python_rows["Cryptographic hash"],
            pyo3_median_ms=pyo3_rows["Cryptographic hash"],
            rust_median_ms=rust_rows["Cryptographic hash"],
        ),
        _benchmark_operation(
            "Schnorr signature",
            python_median_ms=python_rows["Schnorr signature"],
            pyo3_median_ms=pyo3_rows["Schnorr signature"],
            rust_median_ms=rust_rows["Schnorr signature"],
        ),
        _benchmark_operation(
            "Transaction payload signing",
            python_median_ms=python_rows["Transaction payload signing"],
            pyo3_median_ms=pyo3_rows["Transaction payload signing"],
            rust_median_ms=rust_rows["Transaction payload signing"],
        ),
    ]

    _print_markdown(rows, args)
    if args.csv is not None:
        _write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
