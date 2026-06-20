# dcex Examples

These examples are intentionally small and read-only. They are for learning
basic client usage, not for exhaustively validating exchange endpoints.

- `sync/` contains synchronous Python examples.
- `async/` contains asynchronous Python examples.
- `crates/dcex/examples/` contains direct Rust examples for the `dcex` crate.
- `*_public.py` files do not require API keys.
- `*_private_readonly.py` files require credentials but avoid order placement, cancellations, external withdrawals, transfers, leverage changes, and account-mode changes.
- Generated-report endpoint checks belong in `tests` and should be run with the `generated` marker.
- `benchmark_core_local.py` measures local CPU-bound Lighter operations against a PyPI `dcex==0.21.2` native Python baseline, the current PyO3-backed Python wrapper, and Rust native. It prints Markdown by default and writes CSV only when `--csv` is provided.
- `benchmark_public_http.py` measures live public Binance server-time calls against a PyPI `dcex==0.21.2` native Python baseline, the current PyO3-backed Python wrapper, and Rust native. It prints Markdown by default and writes CSV only when `--csv` is provided.
- Rust benchmark examples are available through `cargo run -p dcex --example core_local_benchmark --release` and `cargo run -p dcex --example public_http_benchmark --release`.

Use the pytest live suites for endpoint validation.
