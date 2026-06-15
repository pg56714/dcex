# dcex Examples

These examples are intentionally small and read-only. They are for learning basic client usage, not for exhaustively validating exchange endpoints.

- `sync/` contains synchronous examples.
- `async/` contains asynchronous examples.
- `*_public.py` files do not require API keys.
- `*_private_readonly.py` files require credentials but avoid order placement, cancellations, external withdrawals, transfers, leverage changes, and account-mode changes.
- Generated-report endpoint checks belong in `tests` and should be run with the `generated` marker.
- `benchmark_public_http.py` measures live public Binance server-time calls through the Python wrapper and the native PyO3 layer. It prints Markdown by default and writes CSV only when `--csv` is provided.

Use the pytest live suites for endpoint validation.
