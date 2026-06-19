"""Benchmark local CPU-bound Python fallback paths against Rust native paths."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import statistics
import subprocess
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dcex import _native
from dcex.lighter import _crypto as crypto
from dcex.lighter import signer_client as signer


CSV_FIELDS = ["operation", "pyo3_speedup", "rust_speedup"]
HASH_VALUES = [
    3451004116618606032,
    11263134342958518251,
    10957204882857370932,
    5369763041201481933,
    7695734348563036858,
    1393419330378128434,
    7387917082382606332,
]


def _scalar_bytes(limbs: list[int]) -> bytes:
    return b"".join(limb.to_bytes(8, "little") for limb in limbs)


PRIVATE_KEY_BYTES = _scalar_bytes(
    [
        12235002942052073545,
        1175977464658719998,
        8536934969147463310,
        6524687619313720391,
        2922072024880609112,
    ]
)
PRIVATE_KEY = crypto.private_key_from_bytes(PRIVATE_KEY_BYTES)
NONCE_BYTES = _scalar_bytes(
    [
        5245666847777449560,
        15178169970799106939,
        4403065012435293749,
        15306540389399388999,
        8935555081913173844,
    ]
)
NONCE = int.from_bytes(NONCE_BYTES, "little")
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
TX_ATTRIBUTES = {1: 9, 2: 10, 4: 1}
TX_PAYLOAD = {
    "AccountIndex": 12,
    "ApiKeyIndex": 3,
    "MarketIndex": 4,
    "ClientOrderIndex": 5,
    "BaseAmount": 6,
    "Price": 7,
    "IsAsk": 1,
    "Type": 0,
    "TimeInForce": 2,
    "ReduceOnly": 0,
    "TriggerPrice": 0,
    "OrderExpiry": 8,
    "ExpiredAt": 1_590_000,
    "Nonce": 11,
}


@contextmanager
def _python_fallback() -> Iterator[None]:
    crypto_native = crypto._NATIVE
    signer_native = signer._NATIVE
    crypto._NATIVE = None
    signer._NATIVE = None
    try:
        yield
    finally:
        crypto._NATIVE = crypto_native
        signer._NATIVE = signer_native


def _measure(
    callback: Callable[[], Any],
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


def _run_rust_benchmark(args: argparse.Namespace) -> dict[str, float]:
    env = os.environ.copy()
    env["DCEX_BENCH_ITERATIONS"] = str(args.iterations)
    env["DCEX_BENCH_WARMUP"] = str(args.warmup)
    env["DCEX_BENCH_INNER_LOOPS"] = str(args.inner_loops)
    env["DCEX_BENCH_OUTPUT"] = "json"

    completed = subprocess.run(
        ["cargo", "run", "-q", "-p", "dcex", "--example", "core_local_benchmark", "--release"],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"Rust core local benchmark failed with exit code {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    for line in reversed(completed.stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            payload = json.loads(line)
            return {
                str(row["operation"]): float(row["rust_median_ms"])
                for row in payload["rows"]
            }
    raise SystemExit(f"Rust core local benchmark did not emit JSON:\n{completed.stdout}")


def _python_hash() -> bytes:
    return crypto.poseidon_hash_bytes(HASH_VALUES)


def _pyo3_hash() -> bytes:
    return bytes(_native.lighter_poseidon_hash_bytes(HASH_VALUES))


def _python_signature() -> bytes:
    return crypto.schnorr_sign(MESSAGE_HASH, PRIVATE_KEY, NONCE)


def _pyo3_signature() -> bytes:
    return bytes(_native.lighter_schnorr_sign(MESSAGE_HASH, PRIVATE_KEY_BYTES, NONCE_BYTES))


def _tx_payload_json() -> bytes:
    return json.dumps(TX_PAYLOAD, separators=(",", ":")).encode()


def _python_transaction_payload() -> tuple[bytes, bytes]:
    message_hash = signer._transaction_hash(TX_VALUES, TX_ATTRIBUTES)
    payload = dict(TX_PAYLOAD)
    payload["Sig"] = base64.b64encode(
        crypto.schnorr_sign(message_hash, PRIVATE_KEY, NONCE)
    ).decode()
    payload["L2TxAttributes"] = TX_ATTRIBUTES
    return json.dumps(payload, separators=(",", ":")).encode(), message_hash


def _pyo3_transaction_payload() -> tuple[bytes, bytes]:
    tx_info, message_hash = _native.lighter_sign_transaction(
        TX_VALUES,
        list(TX_ATTRIBUTES.items()),
        _tx_payload_json(),
        PRIVATE_KEY_BYTES,
        NONCE_BYTES,
    )
    return bytes(tx_info), bytes(message_hash)


def _canonical_transaction_payload(result: tuple[bytes, bytes]) -> tuple[dict[str, Any], bytes]:
    payload, message_hash = result
    return json.loads(payload), message_hash


def _benchmark_pair(
    operation: str,
    python_callback: Callable[[], Any],
    pyo3_callback: Callable[[], Any],
    *,
    iterations: int,
    warmup: int,
    inner_loops: int,
    rust_median_ms: float,
    canonical: Callable[[Any], Any] | None = None,
) -> dict[str, str | float]:
    canonical = canonical or (lambda value: value)
    with _python_fallback():
        python_result = python_callback()
    pyo3_result = pyo3_callback()
    if canonical(python_result) != canonical(pyo3_result):
        raise SystemExit(f"{operation} Python and PyO3 outputs did not match")

    with _python_fallback():
        python_median_ms = _measure(
            python_callback,
            iterations=iterations,
            warmup=warmup,
            inner_loops=inner_loops,
        )
    pyo3_median_ms = _measure(
        pyo3_callback,
        iterations=iterations,
        warmup=warmup,
        inner_loops=inner_loops,
    )
    return {
        "operation": operation,
        "pyo3_speedup": python_median_ms / pyo3_median_ms,
        "rust_speedup": python_median_ms / rust_median_ms,
    }


def _print_markdown(rows: list[dict[str, str | float]]) -> None:
    print("Speedups are measured against the pure Python fallback implementation.")
    print()
    print("| Operation | PyO3 bridge speedup | Rust native speedup |")
    print("| --------- | ------------------- | ------------------- |")
    for row in rows:
        print(
            f"| {row['operation']} | {float(row['pyo3_speedup']):.2f}x | "
            f"{float(row['rust_speedup']):.2f}x |"
        )


def _write_csv(path: Path, rows: list[dict[str, str | float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run local CPU-bound benchmark pairs and print speedup multipliers."""
    parser = argparse.ArgumentParser(
        description="Benchmark local CPU-bound Python fallback paths against Rust native paths.",
    )
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--inner-loops", type=int, default=1)
    parser.add_argument("--csv", type=Path, default=None, help="Optional local CSV output path.")
    args = parser.parse_args()

    if args.iterations <= 0:
        raise SystemExit("--iterations must be positive")
    if args.warmup < 0:
        raise SystemExit("--warmup cannot be negative")
    if args.inner_loops <= 0:
        raise SystemExit("--inner-loops must be positive")

    rust_rows = _run_rust_benchmark(args)
    rows = [
        _benchmark_pair(
            "Cryptographic hash",
            _python_hash,
            _pyo3_hash,
            iterations=args.iterations,
            warmup=args.warmup,
            inner_loops=args.inner_loops,
            rust_median_ms=rust_rows["Cryptographic hash"],
        ),
        _benchmark_pair(
            "Schnorr signature",
            _python_signature,
            _pyo3_signature,
            iterations=args.iterations,
            warmup=args.warmup,
            inner_loops=args.inner_loops,
            rust_median_ms=rust_rows["Schnorr signature"],
        ),
        _benchmark_pair(
            "Transaction payload signing",
            _python_transaction_payload,
            _pyo3_transaction_payload,
            iterations=args.iterations,
            warmup=args.warmup,
            inner_loops=args.inner_loops,
            rust_median_ms=rust_rows["Transaction payload signing"],
            canonical=_canonical_transaction_payload,
        ),
    ]

    _print_markdown(rows)
    if args.csv is not None:
        _write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
