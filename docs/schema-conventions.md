# Endpoint schemas and request adapters

Ordinary REST endpoints use the shared request engine in
`crates/dcex/src/exchanges/schema.rs`. It owns field types, decimal syntax,
required and duplicate fields, recursive JSON constraints, arrays, and form
encoding. `input_contracts.json` is the explicit input-schema source shared by
Rust `input_contracts.rs` and Python `_input_codec.py` / `_input_validation.py`.
The `_schema_codec.py` module retains compatible imports. Python validates
declared endpoint inputs before conversion to native string pairs.

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

The common Rust core is `mod.rs`, `client.rs`, `market.rs`, `trade.rs`,
`params.rs`, `signing.rs`, `private.rs`, `tests.rs`, and
`tests/endpoint_coverage.rs`. Every Python sync/async package has `client.py`
and the four HTTP modules above. All private dispatch entry points, including
Arcus spot, belong in `private.rs`; product handlers remain in their domain
modules. Account/product files are needed only when that exchange has a separate
implementation. `tests/unit/test_exchange_structure.py` checks this contract
for every exchange registered in the native module.

## Numbers and wire format

Numeric validation depends on an explicit `format: decimal` declaration for an
exchange, endpoint and field, including nested properties/items and Python
aliases. No field-name heuristic grants numeric semantics or exceptions.
Hand-written adapters must declare their fields in the same input catalog.
The per-endpoint `input_schema` metadata is regenerated from that catalog;
wire schemas retain their existing types and structural constraints.

Declared decimals reject Python float/bool, scientific strings and non-numbers.
Callers use exact strings or `Decimal`; integer values retain their existing
endpoint rules. Negatives are rejected unless the exact field has `x-signed`.
`x-positive` excludes zero; other zero restrictions remain in endpoint checks.
Kraken's declared REST place/edit/amend and V1 addOrder/editOrder price fields
use `x-relative: kraken_relative_price`, with the shared grammar
`[+\-#][0-9]+(\.[0-9]+)?%?`. Other exchanges do not inherit this exception.
Explicit `x-decimal-sentinels` cover documented OKX market-price selectors and
Bitget/Bybit empty no-change or unused investment selectors. Hyperliquid's
builder fee rate explicitly permits the percent suffix through `x-percent`.
Signed margin deltas, spread prices and RFQ/portfolio sizes opt in per field.
Identifiers, tokens, booleans and undeclared values do not acquire financial
validation from their names; their ordinary endpoint type checks still apply.
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
uv run --no-sync python -m scripts.build_input_contracts --write
uv run --no-sync python -m scripts.build_binance_wrappers --write
uv run --no-sync python -m scripts.build_bitget_wrappers --write
uv run --no-sync python -m scripts.build_bybit_wrappers --write
uv run --no-sync python -m scripts.build_bingx_wrappers --write
uv run --no-sync python -m scripts.build_hyperliquid_wrappers --write
uv run --no-sync python -m scripts.build_kucoin_wrappers --write
uv run --no-sync python -m scripts.build_schema_tables --write
uv run --no-sync ruff format dcex scripts
uv run --no-sync ruff check dcex scripts --fix
uv run --no-sync ruff format dcex scripts
cargo fmt --all
uv run --no-sync python -m scripts.build_input_contracts --check
```

A second run must produce identical files. Run the existing endpoint wire and
signature tests, shared sync/async wrapper tests and schema codec regressions.
Decimal tests traverse every declared REST/WS field and verify the installed
Python endpoint wrappers. Add declarations and wire regressions for new fields.
When changing evidence paths, regenerate `scripts/build_endpoint_docs.py` and
run its `--check`. Check for loaded `.pyd` modules and verify exclusive access
before rebuilding native. Behaviour fixes and file-only moves use separate
commits; do not edit `CHANGELOG.md` manually.

### Explicit boundaries and evidence granularity

An undeclared field receives **no numeric validation**. The completeness guard
independently inventories public signatures, wire aliases, variadic operations and
list/dict parameters; non-financial exceptions are individually documented in
`tests/fixtures/input_contract_exemptions.json`. Adding a numeric parameter without
a declaration fails the guard. `format: decimal` permits zero by default;
`x-positive: true` requires a value strictly greater than zero. Order quantities
and transfer amounts without a zero control meaning opt into positive checks;
zero-valued cancellation controls and documented sentinels retain their semantics.

Kraken V1 `amendOrder` also permits relative limit/trigger prices. Conditional
`close[price]`/`close[price2]` (Python `close_price`/`close_price2`) inherit the
corresponding price rules, as specified by the [Kraken V1 addOrder documentation](https://docs-legacy.kraken.com/api/docs/websocket-v1/addorder/).
[Kraken futures offsets](https://docs.kraken.com/api-reference/order-management/send-order)
allow positive and negative decimal values, with their unit specified separately.
This is verified for `place_futures_order`. Batch offset support is unknown:
the [official Kraken Go SDK batch instruction](https://github.com/krakenfx/api-go/blob/main/pkg/derivatives/entities.go)
does not declare offset fields, unlike its single-order request. The catalog permits
signed offsets, but the existing native batch field allowlist still rejects them;
this change does not assert batch transport support.
[OKX simulation idxVol](https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder)
is a signed decimal in the -0.99 to 1 range.
The [official Backpack Rust client](https://github.com/backpack-exchange/bpx-api-client/blob/master/types/src/order.rs)
serializes `TriggerQuantity::Percent` with a percent suffix. The `triggerQuantity`
declaration permits exact values such as `50%` through `x-percent`; `x-percent-range`
requires percentages greater than 0 and at most 100, compared without binary floats.
[Aster futures pegOffset](https://asterdex.github.io/aster-api-website/futures-v3/account%26trades/)
is explicitly signed: BUY offsets can be negative. Its declaration preserves this existing behavior.

The completeness guard compares captured payload names from all 15 exchange
endpoint-coverage suites with nested declarations; renaming a declaration while leaving the actual wire field unchanged
fails the test. Numeric-name exemptions require a bool/int annotation and a
field-qualified explanation. Currency and mode selectors have explicit nondecimal
declarations. KuCoin deposited margin is positive; Bybit added margin is a signed delta.

Bybit order quantity is positive except when both `reduceOnly` and `closeOnTrigger`
are true, using the declared `x-zero-when` sibling conditions. This preserves the
[documented perpetual/futures zero-quantity close](https://bybit-exchange.github.io/docs/v5/order/create-order).
Kraken spot volume permits zero only with `reduce_only` or `ordertype=settle-position`;
a list of `x-zero-when` condition groups expresses OR, while each group uses AND. Positive rules also
cover the audited Bitget/MEXC/Kraken order sizes, transfer amounts and OKX/Bybit leverage.

[BingX's published request guidance](https://github.com/BingX-API/api-ai-skills/blob/main/skills/swap-trade/SKILL.md)
requires attached TP/SL to be JSON strings with numeric prices. Batch dictionaries
and JSON strings are normalized to that representation without binary floating-point
rounding. Market TP/SL may omit `price`; when present it must be positive, as must
`stopPrice`. Explicit zero prices remain invalid (checked 2026-09-29).

Rust ledger evidence without `::symbol` is deliberately **file-level evidence**:
it proves the cited source file exists, not that a particular function covers a
route. Symbol-qualified references are validated when present; dedicated wire
coverage tests remain the route-level evidence. Superseded reasons must contain
at least four distinct words and cannot be padded single-token placeholders.

All 11 `scripts/build_*.py` generators require explicit `--write` or `--check`. Check mode renders in memory, formats Rust through rustfmt stdin/stdout and Python through Ruff stdin/stdout, and exits nonzero on drift without writing. `python -B -m scripts.build_schema_tables --check` compares formatted Rust tables; CI checks every generator. Signature vectors use the isolated command `uv run --no-sync --with hyperliquid-python-sdk==0.24.0 python -B -m scripts.build_hyperliquid_action_vectors --check`.

The [OKX amend-order documentation](https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-order)
uses nested `attachAlgoOrds[].sz` for split take-profit quantities; `newSz` belongs
to the main order. All three amend declarations preserve that distinction.
Batch TP/SL requires an object; BingX null and empty optional attached values are
left unencoded rather than serialized as the string `null`.

Fund catalog entry points route withdrawal/transfer names through their domain
owners before using shared transport implementations. Ownership tests verify the
router, owner and schema loader instead of relying on schema exceptions. Awaiting
nonce lookup or signing alone never establishes transport ownership. Nondispatch
allowances are bound to exact source bodies, so adding a sender invalidates them.
Financial name fragments (including price, amount, size, qty, fee, margin, collateral
and share) cannot be exempted even with integer annotations. All 454 former input
exemptions now have explicit control or structured declarations. Any future reasons
are compared after stripping method/field tokens and `For ...,` prefixes; more than
four repetitions fail, including nondispatch allowances.

OKX attached TP ratios use signed exact decimals greater than -1; placement excludes
zero, while amended TP/SL ratios allow zero to delete the attached order. SL ratios
are positive except for amendment deletion. These bounds preserve the documented
values without guessing the side of an existing order during amendments. Callback,
activation and split-size fields retain positive rules. Nested amendment `newSz` is
rejected; the algo-order attached schema rejects `sz`, which its official request
table does not list. Absolute placement prices and Kraken convenience volumes are
positive; documented Kraken relative-price controls remain supported.

BingX trims optional attached strings before checking their shape; blank values are
absent and empty objects are rejected. Fund literals outside owners are pinned by
source hashes, and shared schema transports allow only audited routers and owner
callers. Owner domain checks execute in release builds. Generator checks also reject
orphaned files in their owned generated directories without writing or deleting them.

The shared input-contract validators enforce declared decimal rules and structured JSON constraints. Integer and boolean entries in this catalog describe the endpoint inputs; they do not add runtime type enforcement. Endpoint wire adapters retain their own integer/boolean validation. For OKX algo orders, the official specification requires either `sz` or `closeFraction`; it does not document a zero-size exception. An explicitly supplied `sz` must therefore be positive; a full close can omit it and use `closeFraction=1`.

Rust diagnostics use the `log` facade: callers must install a Rust logger to observe warnings, including skipped malformed Ondo spot product rows. The Python extension does not bridge Rust `log` records into Python `logging`; configuring the Python `dcex` logger alone will not expose these warnings.
