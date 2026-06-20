"""Benchmark local Lighter core across PyPI Python, PyO3, and native Rust."""

from __future__ import annotations

import argparse
import csv
import importlib
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
sys.path.insert(0, str(ROOT))

_native = importlib.import_module("dcex._native")

DEFAULT_BASELINE_VERSION = "0.21.2"

CSV_FIELDS = [
    "operation",
    "python_median_ms",
    "pyo3_median_ms",
    "rust_median_ms",
    "rust_backed_python_speedup",
    "rust_native_speedup",
]
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

# This embedded script intentionally imports the historical PyPI baseline.
# It is not a runtime dependency of the current package.
PYPI_PYTHON_CORE_BENCHMARK = r"""
from __future__ import annotations

import argparse
import base64
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
) -> float:
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
    args = parser.parse_args()

    rows = [
        {
            "operation": "Cryptographic hash",
            "python_median_ms": _measure(
                _python_hash,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
            ),
        },
        {
            "operation": "Schnorr signature",
            "python_median_ms": _measure(
                _python_signature,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
            ),
        },
        {
            "operation": "Transaction payload signing",
            "python_median_ms": _measure(
                _python_transaction_payload,
                iterations=args.iterations,
                warmup=args.warmup,
                inner_loops=args.inner_loops,
            ),
        },
    ]
    print(json.dumps({"rows": rows}, sort_keys=True))


if __name__ == "__main__":
    main()
"""


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
) -> float:
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


def _run_pypi_python_benchmark(args: argparse.Namespace) -> dict[str, float]:
    with tempfile.TemporaryDirectory(prefix="dcex-pypi-core-bench-") as temp_name:
        temp_root = Path(temp_name)
        baseline_site = temp_root / "site"
        _install_pypi_baseline(args.baseline_version, baseline_site)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(baseline_site)

        payload = _run_json_command(
            [
                sys.executable,
                "-c",
                PYPI_PYTHON_CORE_BENCHMARK,
                "--iterations",
                str(args.iterations),
                "--warmup",
                str(args.warmup),
                "--inner-loops",
                str(args.inner_loops),
            ],
            cwd=temp_root,
            env=env,
            context=f"PyPI dcex=={args.baseline_version} native Python core benchmark",
        )
    return {
        str(row["operation"]): float(row["python_median_ms"])
        for row in payload["rows"]
    }


def _run_rust_benchmark(args: argparse.Namespace) -> dict[str, float]:
    env = os.environ.copy()
    env["DCEX_BENCH_ITERATIONS"] = str(args.iterations)
    env["DCEX_BENCH_WARMUP"] = str(args.warmup)
    env["DCEX_BENCH_INNER_LOOPS"] = str(args.inner_loops)
    env["DCEX_BENCH_OUTPUT"] = "json"

    payload = _run_json_command(
        [
            "cargo",
            "run",
            "-q",
            "-p",
            "dcex",
            "--example",
            "core_local_benchmark",
            "--release",
        ],
        cwd=ROOT,
        env=env,
        context="Rust core local benchmark",
    )
    return {
        str(row["operation"]): float(row["rust_median_ms"])
        for row in payload["rows"]
    }


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


def _benchmark_operation(
    operation: str,
    callback: Callable[[], object],
    *,
    iterations: int,
    warmup: int,
    inner_loops: int,
    python_median_ms: float,
    rust_median_ms: float,
) -> dict[str, str | float]:
    pyo3_median_ms = _measure(
        callback,
        iterations=iterations,
        warmup=warmup,
        inner_loops=inner_loops,
    )
    return {
        "operation": operation,
        "python_median_ms": python_median_ms,
        "pyo3_median_ms": pyo3_median_ms,
        "rust_median_ms": rust_median_ms,
        "rust_backed_python_speedup": python_median_ms / pyo3_median_ms,
        "rust_native_speedup": python_median_ms / rust_median_ms,
    }


def _print_markdown(rows: list[dict[str, str | float]], baseline_version: str) -> None:
    print(f"Baseline: PyPI `dcex=={baseline_version}` native Python implementation = 1.00x.")
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
            "Benchmark local Lighter CPU-bound operations across PyPI Python, "
            "the current PyO3-backed Python wrapper, and native Rust."
        ),
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--inner-loops", type=int, default=1)
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
    if args.inner_loops <= 0:
        raise SystemExit("--inner-loops must be positive")

    python_rows = _run_pypi_python_benchmark(args)
    rust_rows = _run_rust_benchmark(args)
    rows = [
        _benchmark_operation(
            "Cryptographic hash",
            _pyo3_hash,
            iterations=args.iterations,
            warmup=args.warmup,
            inner_loops=args.inner_loops,
            python_median_ms=python_rows["Cryptographic hash"],
            rust_median_ms=rust_rows["Cryptographic hash"],
        ),
        _benchmark_operation(
            "Schnorr signature",
            _pyo3_signature,
            iterations=args.iterations,
            warmup=args.warmup,
            inner_loops=args.inner_loops,
            python_median_ms=python_rows["Schnorr signature"],
            rust_median_ms=rust_rows["Schnorr signature"],
        ),
        _benchmark_operation(
            "Transaction payload signing",
            _pyo3_transaction_payload,
            iterations=args.iterations,
            warmup=args.warmup,
            inner_loops=args.inner_loops,
            python_median_ms=python_rows["Transaction payload signing"],
            rust_median_ms=rust_rows["Transaction payload signing"],
        ),
    ]

    _print_markdown(rows, args.baseline_version)
    if args.csv is not None:
        _write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
