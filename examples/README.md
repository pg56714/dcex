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
- WebSocket examples currently cover public streams for Backpack, Binance, BingX, Bybit, OKX, Bitget, BitMart, BitMEX, Gate.io, Hyperliquid, Kraken, KuCoin, Lighter, and MEXC, plus private user-data streams for Backpack, Binance, BingX, Bybit, OKX, Bitget, BitMart, BitMEX, Gate.io, Hyperliquid, Kraken, KuCoin, Lighter, and MEXC.
- Generated-report endpoint checks belong in `tests` and should be run with the `generated` marker.

Use the pytest live suites for endpoint validation.
