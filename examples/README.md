# dcex Examples

These examples are intentionally small and read-only. They are for learning
basic client usage, not for exhaustively validating exchange endpoints.

- `sync/` contains synchronous Python examples.
- `async/` contains asynchronous Python examples.
- `crates/dcex/examples/` contains direct Rust examples for the `dcex` crate.
- `*_public.py` files do not require API keys.
- `*_ws_public.py` files do not require API keys and read a small number of public stream events.
- `*_private_readonly.py` files require credentials but avoid order placement, cancellations, external withdrawals, transfers, leverage changes, and account-mode changes.
- `*_ws_private_readonly.py` files require credentials or a user address and only open user-data streams; they do not place or cancel orders.
- Generated-report endpoint checks belong in `tests` and should be run with the `generated` marker.

Simple examples:

```sh
uv run python examples/sync/binance_public.py
uv run python examples/async/binance_ws_public.py
cargo run -p dcex --example binance_ws_public
```

Use the pytest live suites for endpoint validation.

## Lighter

Lighter examples use explicit network profiles. The private HTTP and WebSocket
examples demonstrate Mainnet and Robinhood running concurrently with separate
`LIGHTER_MAINNET_*` and `LIGHTER_ROBINHOOD_*` credentials:

```sh
uv run python examples/sync/lighter_private_readonly.py
uv run python examples/async/lighter_private_readonly.py
uv run python examples/async/lighter_ws_private_readonly.py
cargo run -p dcex --example lighter_ws_private_readonly
```

Public clients can pass `Network.ROBINHOOD` or
`LighterNetwork::Robinhood`; omitting the network preserves the Mainnet
default.
