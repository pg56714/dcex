# dcex Examples

These examples are intentionally small and read-only. They are for learning basic client usage, not for exhaustively validating exchange endpoints.

- `sync/` contains synchronous examples.
- `async/` contains asynchronous examples.
- `*_public.py` files do not require API keys.
- `*_private_readonly.py` files require credentials but avoid order placement, cancellations, withdrawals, transfers, leverage changes, and account-mode changes.
- Generated-report endpoint checks belong in `tests` and should be run with the `generated` marker.

Use the pytest live suites for endpoint validation.
