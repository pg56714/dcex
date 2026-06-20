# dcex Examples

These examples are intentionally small and read-only. They are for learning
basic client usage, not for exhaustively validating exchange endpoints.

- `sync/` contains synchronous Python examples.
- `async/` contains asynchronous Python examples.
- `crates/dcex/examples/` contains direct Rust examples for the `dcex` crate.
- `*_public.py` files do not require API keys.
- `*_private_readonly.py` files require credentials but avoid order placement, cancellations, external withdrawals, transfers, leverage changes, and account-mode changes.
- Generated-report endpoint checks belong in `tests` and should be run with the `generated` marker.

Use the pytest live suites for endpoint validation.
