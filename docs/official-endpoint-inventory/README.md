# Official endpoint inventories

The exchange JSON files preserve the documented HTTP routes, actions and WebSocket
sections used to reconcile [the endpoint ledger](../endpoint-coverage-ledger.json).
`sources/` contains the request schemas and message examples needed by generators
and offline wire tests. Each record retains its official source URL.

A documentation heading is not necessarily an endpoint. The ledger records
duplicates, documentation-only sections, incomplete specifications and unavailable
operations explicitly. Offline tests establish the transmitted message shape;
they do not establish live account eligibility or server availability.

Run generators from the repository root, for example:

```sh
python -m scripts.build_binance_wrappers
python -m scripts.build_bingx_wrappers
python -m scripts.build_bitget_wrappers
python -m scripts.build_hyperliquid_wrappers
python -m scripts.build_kucoin_wrappers
ruff check --fix dcex
ruff format dcex
cargo fmt --all
python -m scripts.build_endpoint_markdown --write
python -m scripts.build_endpoint_markdown --check
python scripts/build_endpoint_docs.py --write
```

The wrapper generators use committed schemas and require no network access.
`collect_bitget_schemas` and `collect_kucoin_schemas` refresh public documentation
schemas. `extract_okx_ws_schemas` accepts a downloaded official HTML snapshot.
Review schema changes and run the associated wire tests before updating ledger
claims. Regenerating wrappers alone does not verify an endpoint.

Independent signing vectors live in `tests/fixtures/signing/`. The Hyperliquid
vector generator documents its isolated official-SDK environment and records the
SDK version in its output; that SDK is not a runtime dependency of dcex.
