# Endpoint schemas and request adapters

Ordinary REST endpoints use the shared request engine in
`crates/dcex/src/exchanges/schema.rs`. It owns field types, decimal syntax,
required and duplicate fields, recursive JSON constraints, arrays, and form
encoding. Python's `dcex/_schema_codec.py` checks values before conversion to
native string pairs: financial floats are rejected and `Decimal` values are
rendered in fixed notation without rounding.

Exchange adapters retain host selection, symbol conversion, authentication,
conditional business rules, and the documented location and wire type of each
field. Keep hand-written code for cryptographic envelopes, caller-signed
transactions, multi-step operations, and constraints involving several fields.
Such adapters must still use the shared field/number encoder. Do not introduce
another generic JSON validator or decimal-to-float conversion.

## Files

- `schemas/*.json`: committed endpoint and field data. `table_*.json` contains
  immutable transport tables; `routes_*.json` contains routes with conditional
  adapters. Domain catalog files also retain official source and Python-name
  metadata. Wire names take precedence over Python names in the shared loader.
- `generated/*.rs` and Python `_generated/*_http.py`: generated declarations and
  adapters. Edit the source schema or generator, then regenerate.
- `schema_requests.rs` and `schema_requests/`: exchange adapters to the common
  engine. Product-specific adapters can remain in their product module.
- `private.rs`: private method dispatch, consistently across exchanges.
- `withdrawals.rs` / `_withdrawals_http.py`: withdrawals and transfers to another
  user; `transfers.rs` / `_transfers_http.py`: transfers between owned accounts;
  `batch.rs` / `_batch_http.py`: batch operations. Public names stay stable.
- Rust `tests.rs` declares test modules only; route coverage belongs in
  `tests/endpoint_coverage.rs`. Other tests are split by topic.
- Python clients compose `_http_manager.py`, `_market_http.py`, `_trade_http.py`
  and `_account_http.py`, plus product mixins. Arcus spot and perpetual clients
  keep separate public classes while using these same file roles.

## Numbers and wire format

Prices, quantities and amounts use plain decimal strings. Reject Python floats,
scientific strings, invalid negative values and non-numbers before transport. Integers,
booleans and identifiers retain their own types; a signed identifier is not an
amount. Signed margin deltas and OKX's `tpOrdPx`/`slOrdPx=-1` market selectors
retain their existing contracts; ordinary schema amounts remain nonnegative.
Existing documented zero values retain their endpoint-specific checks.
Kraken EditOrder relative prices, signed RFQ/portfolio sizes, and Bitget's empty
TPSL size selector retain their endpoint-specific meanings. Signed JSON numbers
are declared with `x-signed`; callers supply exact strings or `Decimal` values.
An explicit JSON `number` schema can produce a JSON number from an exact plain
string; Rust uses `serde_json` arbitrary precision, never an intermediate `f64`.
Range comparisons remain separate from value serialization.

An array's placement (JSON, repeated query key, or indexed key) is part of its
transport adapter. Binance prediction batch cancellation requires a nonempty
`cancelInfoList`; the common form encoder leaves brackets in keys literal while
escaping values. The signer sends exactly the bytes it signs.

## Regeneration and verification

Run each command from the repository root:

```powershell
uv run --no-sync python -m scripts.build_binance_wrappers
uv run --no-sync python -m scripts.build_bitget_wrappers
uv run --no-sync python -m scripts.build_bybit_wrappers
uv run --no-sync python -m scripts.build_bingx_wrappers
uv run --no-sync python -m scripts.build_hyperliquid_wrappers
uv run --no-sync python -m scripts.build_kucoin_wrappers
uv run --no-sync python -m scripts.build_schema_tables
uv run --no-sync ruff format dcex scripts
uv run --no-sync ruff check dcex scripts --fix
uv run --no-sync ruff format dcex scripts
cargo fmt --all
```

A second run must produce identical files. Run the existing endpoint wire and
signature tests, shared sync/async wrapper tests and schema codec regressions.
When changing evidence paths, regenerate `scripts/build_endpoint_docs.py` and
run its `--check`. Check for loaded `.pyd` modules and verify exclusive access
before rebuilding native. Behaviour fixes and file-only moves use separate
commits; do not edit `CHANGELOG.md` manually.
