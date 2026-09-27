# Endpoint coverage and verification

**English** | [繁體中文](endpoint-audit.zh_tw.md)

Reviewed: 2026-09-27. Inputs are the supplied endpoint coverage report and the official API documentation inspected during this audit. Scope covers ordinary market data, trading, accounts, internal transfers and risk controls. External withdrawal submission and market-maker/partner-only workflows are excluded.

## Verification status

**Offline validation passed.** `cargo test --workspace --all-features`: 639 passed (636 core tests and 3 interface/safety tests); 53 live tests intentionally ignored. After rebuilding and installing the native extension from this source, `pytest tests/unit` passed all 10,993 tests with no failures or skips. Ruff lint/format, Rust format and Pyright passed (0 type errors). No orders or account administration operations were sent to live exchanges. Offline tests check routes, verbs, types, signatures and response handling; they do not establish account eligibility or current server availability.

**Coverage correction: implementation is not complete.** The recheck found missing read-only account queries, Arcus api-meta, KuCoin margin stop cancellation and additional families. Passing tests do not establish completion of every report row. See [remaining work](endpoint-recheck.md).

## Exchanges

Counts below are public REST/signing convenience methods, including aliases and separate operations, not percentages of official endpoint coverage. Rust exposes the corresponding named dispatch and typed request builders; binary downloads and offline signing have dedicated methods. See the [new-method index](endpoint-methods.md).

| Exchange / official docs | Python sync | Python async | New methods | Areas added or expanded |
| --- | ---: | ---: | ---: | --- |
| [Binance](https://developers.binance.com/) | 566 | 566 | 257 | Spot order lists and cancel/replace; USD-M/COIN-M and PM risk; SAPI account, transfers, conversion; TWAP/VP; WS trading |
| [Bybit](https://bybit-exchange.github.io/docs/v5/intro) | 249 | 249 | 79 | Account risk, collateral, position moves, batch trading, historical data and PRO rate limits |
| [OKX](https://www.okx.com/docs-v5/en/) | 266 | 266 | 90 | Algo orders, spreads, margin/portfolio simulation, position moves, conversion, subaccounts and RFQ taker operations |
| [Bitget](https://www.bitget.com/api-doc/common/intro) | 352 | 352 | 214 | Classic and UTA account/risk, batch operations, plans, internal transfers, quotas, subaccount administration and WS trading |
| [Kraken](https://docs.kraken.com/api-reference/) | 117 | 117 | 51 | Spot batch orders and exports; Futures risk, history, analytics and subaccounts; Spot WS trading and Futures streams |
| [MEXC](https://www.mexc.com/api-docs/) | 141 | 141 | 21 | Spot and contract market/account controls, conversion and contract WS subscriptions |
| [BingX](https://bingx-api.github.io/docs/) | 165 | 165 | 76 | USD-M and COIN-M controls; spot OCO/cancel-replace; report bytes; COIN-M WS |
| [KuCoin](https://www.kucoin.com/docs-new) | 295 | 295 | 179 | Classic spot/margin/futures and UTA trading/risk, batch orders, conversion and subaccounts |
| [Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api) | 65 | 65 | 19 | Market/account information, trading controls and caller-signed WS actions |
| [Lighter](https://github.com/elliottech/lighter-python) | 89 | 89 | 18 | Grouped orders, account/asset modes, subaccounts, key rotation, read-only tokens, deposits and signed WS submissions |
| [Backpack](https://docs.backpack.exchange/) | 70 | 70 | 6 | Strategy-order lifecycle and self-trade prevention |
| [Aster](https://github.com/asterdex/api-docs) | 102 | 102 | 14 | V3 account/market queries, guarded cancellation, internal transfers, asset exchange and caller-signed wallet administration |
| [Extended](https://api.docs.extended.exchange/) | 59 | 59 | 18 | Portfolio funding, interest/drawdown analytics and RFQ orderbook stream |
| [Ondo](https://docs.ondoperps.xyz/api-reference) | 74 | 74 | 5 | Perpetual market/account/trade endpoints, SIWE login and JWT invalidation |
| [Arcus](https://docs.arcus.xyz/api-reference) | 46 | 46 | 22 | Perps queries, TP/SL grouping, signed WS request construction and wallet-authorized API keys |

## Limitations and unwrapped areas

| Item | Status and reason |
| --- | --- |
| External withdrawal submission, transfers outside an account family, broker/affiliate and MM-only operations | Excluded by scope; read-only withdrawal history is separate and remains partially unwrapped. |
| Kraken legacy Futures fee schedules | Officially deprecated: values no longer reflect actual fees from 2026-06-22. Use Spot GetTradeVolume. |
| Kraken portfolio simulation | Wrapped, but officially limited to pre-production. Configure the appropriate base URL. |
| Kraken assignment programs / off-book RFQ administration | Not wrapped; not counted as supported ordinary order endpoints. |
| OKX SBE binary orderbook | REST snapshot bytes are wrapped with get_sbe_orderbook; decode template 1006 with the official versioned XML schema. No built-in SBE decoder. |
| Lighter historicalTrades export | Current official request schema is unknown. It was absent from the inspected current SDK; no guessed route or fields were added. |
| Binance COIN-M algo, legacy BingX spot/time and obsolete report paths | Items not confirmed in current official documentation were not guessed. Documented market and trading paths are supported separately. |
| Earn/staking/public pools, lending investment products, referral/leasing, prediction markets and explorer data | Not completed in this expansion. Classify each operation against the agreed exclusions; these product families were not collectively excluded by the user. See the remaining-work report. |

This does not claim coverage of every exchange business or protocol. Combined report rows, dynamic paths and aliases need individual interpretation; literal path counts are not a coverage percentage.

## Operational details

- Arcus API key creation/revocation, Aster wallet administration and Lighter key rotation preserve caller wallet authorization. Trading API keys cannot replace wallet signatures.
- Lighter `change_api_key_signed` requires an explicit nonce and the official `Register Lighter Account` wallet signature. Recreate the client with the new key after confirmed rotation.
- Binance PM/PM Pro, Bybit PRO quotas and Kraken institutional subaccounts remain subject to exchange account eligibility.
- Bitget position moves affect pending orders on both accounts. API key administration and JWT invalidation alter account access.
- Kraken exports return ZIP bytes; BingX income exports return Excel bytes. Do not decode them as JSON.
- KuCoin convert accepts decimal strings and preserves them as JSON numbers. Do not convert inputs to floats first. Futures batch cancellation preserves its DELETE JSON body and includes those exact bytes in the signature.

## Test locations

Rust: `crates/dcex/src/exchanges/*/tests*`. Python: `tests/unit/test_*_endpoint_coverage.py`, `test_*risk*`, `test_ws_*` and binary export tests. Signing tests use local dummy credentials and local HTTP/WS peers.

## Specific official references

- [Kraken Futures fee schedules](https://docs.kraken.com/api-reference/fee-schedules/get-fee-schedules)
- [Kraken portfolio simulation](https://docs.kraken.com/api-reference/account-information/calculate-portfolio-margin-pnl-and-greeks)
- [Lighter transaction definitions](https://github.com/elliottech/lighter-go/tree/main/types/txtypes)
- [Arcus API key onboarding](https://docs.arcus.xyz/api-reference/onboarding/create-api-key)
