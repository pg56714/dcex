# Endpoint coverage and verification

**English** | [繁體中文](endpoint-audit.zh_tw.md)

Reviewed: 2026-09-29. The original report contained 3,180 rows; the reconciled ledger contains 4,846 rows, with official documentation inventories for all 15 exchanges.

All documented endpoints are in scope, including withdrawals, address management, market making, RFQ, broker, referral and partner operations. All 111 originally excluded rows have been addressed; there are no scope exclusions. This does not mean every newly discovered endpoint is implemented.

API withdrawals have no second confirmation; they execute on submit. Trading API keys should not have withdrawal permission. Wallet-authorized operations retain caller-provided signatures; undocumented signing rules are not guessed.

[Interactive coverage table](endpoint-coverage.html) · [Per-row evidence](endpoint-coverage-ledger.json) · [Remaining items](endpoint-recheck.md) · [Method index](endpoint-methods.md)

## Coverage status

Historical, grouped and overlapping rows prevent converting these counts into an endpoint coverage percentage.

| Status | Rows | Definition |
| --- | ---: | --- |
| `implemented` | 3,696 | Exact offline HTTP route and public Rust/Python wrappers |
| `protocol` | 403 | Asynchronous WebSocket protocol support with cited offline evidence; no live certification |
| `superseded` | 686 | Historical or grouped row replaced by explicit current rows |
| `unavailable` | 19 | Retired/unavailable operation, or documentation-only section with no endpoint |
| `unverified` | 11 | Wrapper exists, but part of the official specification is incomplete |
| `blocked` | 30 | Required signing or authorization specification is missing |
| `partial` | 1 | Grouped capability still has a documented gap |
| `pending` | 0 | Documented operation awaiting implementation or dedicated verification |

## Exchanges and Python methods

Method counts include aliases and signing helpers, not endpoints. Additions are relative to `d0bbf8b0`.

| Exchange | Public methods | Added | Implemented rows | Pending rows |
| --- | ---: | ---: | ---: | ---: |
| [binance](official-endpoint-inventory/binance.json) | 758 | 449 | 748 | 0 |
| [bybit](official-endpoint-inventory/bybit.json) | 448 | 278 | 434 | 0 |
| [okx](official-endpoint-inventory/okx.json) | 404 | 228 | 388 | 0 |
| [bitget](official-endpoint-inventory/bitget.json) | 638 | 500 | 610 | 0 |
| [bingx](official-endpoint-inventory/bingx.json) | 210 | 121 | 191 | 0 |
| [kraken](official-endpoint-inventory/kraken.json) | 164 | 98 | 148 | 0 |
| [mexc](official-endpoint-inventory/mexc.json) | 176 | 56 | 157 | 0 |
| [kucoin](official-endpoint-inventory/kucoin.json) | 368 | 252 | 340 | 0 |
| [hyperliquid](official-endpoint-inventory/hyperliquid.json) | 146 | 100 | 118 | 0 |
| [lighter](official-endpoint-inventory/lighter.json) | 136 | 64 | 110 | 0 |
| [backpack](official-endpoint-inventory/backpack.json) | 82 | 18 | 79 | 0 |
| [aster](official-endpoint-inventory/aster.json) | 157 | 69 | 152 | 0 |
| [extended](official-endpoint-inventory/extended.json) | 72 | 31 | 72 | 0 |
| [ondo](official-endpoint-inventory/ondo.json) | 78 | 7 | 72 | 0 |
| [arcus](official-endpoint-inventory/arcus.json) | 90 | 50 | 77 | 0 |

## Verification and limits

<!-- VERIFICATION -->
- Rust passed: `690`
- Rust live ignored: `53`
- Python passed: `23984`
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
