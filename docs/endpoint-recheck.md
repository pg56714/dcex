# Endpoint recheck: remaining items

**English** | [繁體中文](endpoint-recheck.zh_tw.md)

Reviewed: 2026-09-27. All **3,180 source rows are classified**, but **implementation is not complete**: **10 blocked rows and 2 partial rows** remain. Some rows group multiple operations, so this is not a count of 12 missing endpoints. Another 9 rows are unavailable/retired/undocumented and 111 are outside scope.

[Searchable full table](endpoint-coverage.html) · [Per-row JSON and evidence](endpoint-coverage-ledger.json) · [Coverage and verification](endpoint-audit.md)

## Specifications still needed

| Source row | Exchange | Endpoint / operation | Status and reason |
| ---: | --- | --- | --- |
| 8 | binance | Margin user data (margin-stream.binance.com, /sapi/v1/margin/listen-key) | **partial** — Cross-margin risk listen-key lifecycle is supported. Trade/account events can use SpotApiClient.subscribe_user_data_listen_token with a caller-provided token. REST POST /sapi/v1/userListenToken is not wrapped: the current official page omits an explicit authentication/signature specification and the official SDK has no matching implementation. [Docs](https://developers.binance.com/en/docs/products/margin-trading/listen-token-data-stream) |
| 1906 | bingx | GET /openApi/spot/v1/server/time | **blocked** — Legacy /openApi/spot/v1/server/time is absent from the current official reference; its availability/replacement is not confirmed. Current documented server-time wrapper remains available. [Docs](https://github.com/BingX-API/api-ai-skills) |
| 2037 | kraken | GET/POST/PUT/DELETE /funding/v1/* , /funding/v2/deposit/addresses (15 endpoints) | **blocked** — Funding (Beta): 11 ordinary query/deposit interfaces need the authoritative API-Nonce/GET signing preimage. Existing legacy signer is not reused speculatively. Four address-management/withdrawal writes are excluded. [Docs](https://docs.kraken.com/api-reference/) |
| 2472 | kucoin | DELETE /api/v3/hf/margin/stop-order/cancel-by-id | **blocked** — Official stop-order cancel-by-id page does not provide a reliable request schema; parameters are not invented. [Docs](https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-stop-order-by-orderld) |
| 2767 | lighter | L2CreateStakingPool (33) / L2StakeAssets (35) / L2UnstakeAssets (36) | **partial** — StakeAssets (35) and UnstakeAssets (36) are implemented with independent official Go Poseidon vectors. CreateStakingPool (33) lacks a confirmed public signer/schema. [Docs](https://apidocs.lighter.xyz/) |
| 2769 | lighter | L2StrategyTransfer (43) / L2UpdateMarketConfig (44) / L2ApproveIntegrator (45) | **blocked** — Types 43/44 lack confirmed public signing layouts/eligibility; type 45 is partner-only and excluded. No guessed signatures are emitted. [Docs](https://apidocs.lighter.xyz/) |
| 2846 | backpack | GET /wapi/v1/capital/withdrawals/delay | **blocked** — Read-only withdrawal delay is in scope, but official OpenAPI omits the required signing instruction/auth contract; endpoint returns 401 without auth. [Docs](https://docs.backpack.exchange/#tag/Withdrawal-Delays) |
| 2876 | aster | GET /api/v3/ticker/opt/24hr | **blocked** — Official Aster Spot v3 documentation mentions this route without a complete request schema. [Docs](https://github.com/asterdex/api-docs) |
| 2886 | aster | POST /api/v3/batchOrders | **blocked** — Official Aster Spot v3 documentation mentions this route without a complete request schema. [Docs](https://github.com/asterdex/api-docs) |
| 2887 | aster | DELETE /api/v3/batchOrders | **blocked** — Official Aster Spot v3 documentation mentions this route without a complete request schema. [Docs](https://github.com/asterdex/api-docs) |
| 2910 | aster | GET /fapi/v3/marketKlines | **blocked** — Aster marketKlines is mentioned as an alternative, but its request schema is not confirmed; existing documented kline methods remain available. [Docs](https://github.com/asterdex/api-docs) |
| 2969 | aster | POST /fapi/v3/asset/migrateUser | **blocked** — Wallet migration requires source-wallet signature; ownership/account-family eligibility is not established by the available docs. Not implemented or counted as an ordinary internal transfer. [Docs](https://github.com/asterdex/api-docs) |

## Retired, unavailable or undocumented interfaces

| Source row | Exchange | Endpoint / operation | Reason |
| ---: | --- | --- | --- |
| 1367 | okx | POST /api/v5/finance/stable-rewards/quote | Official Stable Rewards documentation announces decommissioning of quote/trade/subscribe-redeem-history. [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1368 | okx | POST /api/v5/finance/stable-rewards/trade | Official Stable Rewards documentation announces decommissioning of quote/trade/subscribe-redeem-history. [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1369 | okx | GET /api/v5/finance/stable-rewards/subscribe-redeem-history | Official Stable Rewards documentation announces decommissioning of quote/trade/subscribe-redeem-history. [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1986 | bingx | - | The source report lists no BingX WS order-entry endpoint (dash); no official protocol is claimed. [Docs](https://github.com/BingX-API/api-ai-skills) |
| 2065 | kraken | GET /derivatives/api/v3/feeschedules | Futures fee schedules were deprecated on 2026-06-22; use applicable current fee/volume APIs. [Docs](https://docs.kraken.com/api-reference/) |
| 2066 | kraken | GET /derivatives/api/v3/feeschedules/volumes | Futures fee schedules were deprecated on 2026-06-22; use applicable current fee/volume APIs. [Docs](https://docs.kraken.com/api-reference/) |
| 2218 | mexc | POST /api/v1/private/account/change_risk_level | Officially disabled; error code 8817. Do not advertise as supported. [Docs](https://www.mexc.com/api-docs/spot-v3/introduction) |
| 2221 | mexc | POST /api/v1/private/order/submit_batch | Official contract documentation labels submit_batch as under maintenance; availability is unconfirmed and no wrapper is advertised. [Docs](https://www.mexc.com/api-docs/spot-v3/introduction) |
| 3162 | arcus | POST /v1/settleLoan | Official Arcus settle-loan documentation says spot lending is not enabled (zero supply cap). settleLoanResults stream support does not imply a REST wrapper. [Docs](https://docs.arcus.xyz/api-reference) |

## Scope and completion criteria

External withdrawals/control, transfers outside the account family, and market-maker/partner-only operations remain excluded. Read-only withdrawal history and ordinary lending, investment and pools are not blanket exclusions. Every exclusion has a row-level reason.

Blocked items require authoritative parameters, signing rules or eligibility before implementation. Unknown specifications are not guessed. WebSocket `protocol` means generic subscription/transport support; it does not claim a typed helper or dedicated test for every topic.
