# Endpoint coverage and verification

**English** | [繁體中文](endpoint-audit.zh_tw.md)

Reviewed: 2026-09-30. The original report contained 3,180 rows; the reconciled ledger contains 4,860 rows, with official documentation inventories for all 15 exchanges.

All documented endpoints are in scope, including withdrawals, address management, market making, RFQ, broker, referral and partner operations. All 111 originally excluded rows have been addressed; there are no scope exclusions. This does not mean every newly discovered endpoint is implemented.

API withdrawals have no second confirmation; they execute on submit. Trading API keys should not have withdrawal permission. Wallet-authorized operations retain caller-provided signatures; undocumented signing rules are not guessed.

[Interactive coverage table](endpoint-coverage.html) · [Per-row evidence](endpoint-coverage-ledger.json)

## Coverage status

Historical, grouped and overlapping rows prevent converting these counts into an endpoint coverage percentage.

| Status | Rows | Definition |
| --- | ---: | --- |
| `implemented` | 3,700 | Exact offline HTTP route and public Rust/Python wrappers |
| `protocol` | 406 | Asynchronous WebSocket protocol support with cited offline evidence; no live certification |
| `superseded` | 686 | Historical or grouped row replaced by explicit current rows |
| `unavailable` | 19 | Retired/unavailable operation, or documentation-only section with no endpoint |
| `unverified` | 11 | Wrapper exists, but part of the official specification is incomplete |
| `blocked` | 37 | Required signing or authorization specification is missing |
| `partial` | 1 | Grouped capability still has a documented gap |
| `pending` | 0 | Documented operation awaiting implementation or dedicated verification |

## Exchanges and Python methods

Method counts include aliases and signing helpers, not endpoints.

| Exchange | Public methods | Implemented rows | Pending rows |
| --- | ---: | ---: | ---: |
| [binance](official-endpoint-inventory/binance.json) | 753 | 748 | 0 |
| [bybit](official-endpoint-inventory/bybit.json) | 448 | 434 | 0 |
| [okx](official-endpoint-inventory/okx.json) | 404 | 388 | 0 |
| [bitget](official-endpoint-inventory/bitget.json) | 629 | 610 | 0 |
| [bingx](official-endpoint-inventory/bingx.json) | 210 | 191 | 0 |
| [kraken](official-endpoint-inventory/kraken.json) | 164 | 148 | 0 |
| [mexc](official-endpoint-inventory/mexc.json) | 176 | 157 | 0 |
| [kucoin](official-endpoint-inventory/kucoin.json) | 365 | 340 | 0 |
| [hyperliquid](official-endpoint-inventory/hyperliquid.json) | 145 | 118 | 0 |
| [lighter](official-endpoint-inventory/lighter.json) | 133 | 110 | 0 |
| [backpack](official-endpoint-inventory/backpack.json) | 82 | 79 | 0 |
| [aster](official-endpoint-inventory/aster.json) | 156 | 152 | 0 |
| [extended](official-endpoint-inventory/extended.json) | 71 | 72 | 0 |
| [ondo](official-endpoint-inventory/ondo.json) | 81 | 76 | 0 |
| [arcus](official-endpoint-inventory/arcus.json) | 90 | 77 | 0 |

## Verification and limits

<!-- VERIFICATION -->
- Rust passed: `693`
- Rust live ignored: `53`
- Python passed: `24134`
- Python deselected: `944`
- Python skipped: `0`
- Python xfailed: `0`
- Outstanding test failures: `0`
- Native extension rebuilt: `True`
- Native build profile: `release`
- Existing Clippy warnings: `14`
<!-- /VERIFICATION -->

Offline tests verify routes, HTTP methods, parameters, signatures, WebSocket messages and response handling. They do not establish live account eligibility or exchange availability. No live orders, withdrawals or account-administration requests were submitted.

- OKX/Bitget SBE returns raw bytes without a built-in decoder.
- Lighter explorer uses a separate base URL; historical exports never automatically pay a fee.
- The ledger records the exact gaps and resolution requirements for `unverified` and `blocked` rows.
