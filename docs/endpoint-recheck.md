# Endpoint recheck: remaining work

**English** | [繁體中文](endpoint-recheck.zh_tw.md)

Reviewed: 2026-09-27. **Coverage is not complete.** The previous 10,993 Python and 639 Rust passing tests verify implemented behavior, not every row of the supplied report. This recheck changes documentation only.

Inputs: the supplied 3,180-row HTML report, current source, official documentation and previously retrieved official documentation caches. Screening the original 1,551 missing and 92 Rust-only rows found 1,027 route-text matches, 423 unmatched literals and 193 semantic/combined/WS/transaction-type rows. These are search categories, not coverage percentages or counts of missing endpoints. A matching route string does not establish the verb, parameter schema or Python exposure.

**The 25 specific interfaces below have no wrapper; they are not the total remaining count.** KuCoin stop-order cancellation still needs parameter clarification; the seven Arcus entries rely on the previously retrieved official documentation. Further unwrapped families and unknowns follow.

## Specific unwrapped interfaces

| Exchange | Route | Status / official source |
| --- | --- | --- |
| Binance | `GET /sapi/v1/capital/withdraw/history` | Read-only reconciliation. [Docs](https://developers.binance.com/docs/wallet/capital/withdraw-history) |
| Binance | `GET /sapi/v1/capital/deposit/subAddress` | Subaccount deposit address/history. [Docs](https://github.com/binance/binance-connector-java/blob/master/clients/sub-account/example_rest.md) |
| Binance | `GET /sapi/v1/capital/deposit/subHisrec` | Subaccount deposit address/history. [Docs](https://github.com/binance/binance-connector-java/blob/master/clients/sub-account/example_rest.md) |
| Binance | `GET /sapi/v1/sub-account/futures/move-position` | Position move/history; account eligibility applies (move: VIP 7–9, master account). [Docs](https://binance.github.io/binance-connector-js/classes/_binance_sub-account.SubAccountRestAPI.AssetManagementApi.html) |
| Binance | `POST /sapi/v1/sub-account/futures/move-position` | Position move/history; account eligibility applies (move: VIP 7–9, master account). [Docs](https://binance.github.io/binance-connector-js/classes/_binance_sub-account.SubAccountRestAPI.AssetManagementApi.html) |
| Bybit | `GET /v5/asset/withdraw/query-record` | Read-only withdrawal history. [Docs](https://bybit-exchange.github.io/docs/v5/asset/withdraw/withdraw-record) |
| OKX | `GET /api/v5/asset/withdrawal-history` | Read-only withdrawal history; official documentation cache checked. [Docs](https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-history) |
| OKX | `GET /api/v5/public/interest-rate-loan-quota` | Public interest rates/loan quotas; official documentation cache checked. [Docs](https://www.okx.com/docs-v5/en/#public-data-rest-api-get-interest-rate-and-loan-quota) |
| Bitget | `GET /api/v2/spot/wallet/withdrawal-records` | Classic read-only withdrawal history. [Docs](https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-withdrawal-records) |
| Bitget | `GET /api/v3/account/withdrawal-records` | UTA read-only withdrawal history. [Docs](https://www.bitget.com/zh-CN/api-doc/uta/account/withdrawal/Get-Withdrawal-Records) |
| BingX | `GET /openApi/api/v3/capital/withdraw/history` | Read-only withdrawal history; official reference cache checked. [Docs](https://github.com/BingX-API/api-ai-skills) |
| BingX | `GET /openApi/wallets/v1/capital/innerTransfer/records` | Read-only main/subaccount P2P transfer history. Transfer submission outside the account family remains excluded. [Docs](https://github.com/BingX-API/api-ai-skills) |
| BingX | `GET /openApi/wallets/v1/capital/subAccount/innerTransfer/records` | Read-only main/subaccount P2P transfer history. Transfer submission outside the account family remains excluded. [Docs](https://github.com/BingX-API/api-ai-skills) |
| KuCoin | `GET /api/v1/withdrawals` | Classic read-only withdrawal history. [Docs](https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-history) |
| KuCoin | `GET /api/v1/withdrawals/{withdrawalId}` | Read-only withdrawal detail. [Docs](https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-by-id) |
| KuCoin | `GET /api/ua/v2/asset/withdrawal/history` | UTA read-only withdrawal history. [Docs](https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-history) |
| KuCoin | `DELETE /api/v3/hf/margin/stop-order/cancel-by-id` | Route confirmed; current official page incorrectly lists no request parameters. Required parameter schema is unknown and must be resolved before implementation. [Docs](https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-stop-order-by-orderld) |
| Kraken | `GET /funding/v1/withdrawals` | New Funding (Beta) read-only replacement; no /funding/ routes exist in the current implementation. Other Funding read APIs also need migration review. [Docs](https://docs.kraken.com/api-reference/funding-beta/list-funding-withdrawals) |
| Arcus | `GET /v1/api-meta/markets` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-market-metadata) |
| Arcus | `GET /v1/api-meta/overview` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-market-overview) |
| Arcus | `GET /v1/api-meta/spot/overview` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-spot-market-overview) |
| Arcus | `GET /v1/api-meta/candles` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-spot-candles) |
| Arcus | `GET /v1/api-meta/userPreferences` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/userpreferences/get-user-preferences) |
| Arcus | `PATCH /v1/api-meta/userPreferences` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/userpreferences/upsert-user-preferences) |
| Arcus | `DELETE /v1/api-meta/userPreferences` | Documented in the previously retrieved official llms-full; live documentation could not be fetched in this recheck. No wrapper in Rust or Python. [Docs](https://docs.arcus.xyz/api-reference/userpreferences/delete-a-user-preference) |

## Further unwrapped families

These remain unfinished. Low priority is not proof of completion or user-approved exclusion.

| Exchange | Unwrapped / requiring individual reconciliation |
| --- | --- |
| Binance | Some subaccount API key/IP management, virtual subaccounts, futures/options enablement, Travel Rule deposit questionnaires/history and managed-account queries. Separate ordinary eligibility from partner-only access. |
| Bybit | New fixed/flexible crypto-loan and collateral management; verify legacy crypto-loan deprecations. Some read-only withdrawal address/information APIs. |
| OKX | Grid, DCA, Signal Bot, Recurring Buy, Copy Trading and some fiat/lending queries. SBE returns snapshot bytes without a built-in decoder. |
| Bitget | 14 UTA grid endpoints, some reality equity fundamentals, lending and read-only withdrawal limits/addresses. |
| MEXC | The report's five STP strategy/group and three subaccount API key operations have no wrappers; current official routes/eligibility were not confirmed in this recheck. |
| KuCoin | OES currencies/custody limits, read-only withdrawal quotas and VIP/OTC loan queries. |
| Hyperliquid | Some lending, vault, staking, deployment and account-abstraction queries/actions; eligibility and purpose require individual review. |
| Lighter | historicalTrades export and advanced types 43/44/45 need current schemas/eligibility checks; pool, staking and leasing products remain unwrapped. |
| Backpack | Vault/prediction and withdrawal-delay controls remain unwrapped; RFQ maker quotes are excluded under MM scope. |
| Extended | Some public vault data and rewards; affiliate/referral operations are separate partner scope. |
| Aster | Spot batches and alternate ticker lack complete documentation; classify wallet migration before treating it as an internal transfer. |
| Kraken | Funding (Beta) query migration remains incomplete; distinguish legacy EditOrder from the recommended AmendOrder. |

The [Bitget changelog](https://www.bitget.com/docs/uta/changelog/2026-08) lists 14 grid APIs. The [OKX Grid documentation](https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-place-grid-algo-order) describes the unwrapped strategy family.

## Unknown schemas, disabled APIs and explicit exclusions

- Aster's official Spot documentation mentions `POST/DELETE /api/v3/batchOrders` and `GET /api/v3/ticker/opt/24hr` without full definitions. Their request schemas are unknown; do not invent them. [Official Spot V3 documentation](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-spot-api-v3.md).
- MEXC `POST /api/v1/private/account/change_risk_level` is officially disabled and returns 8817. Classify it as disabled, not an implementation backlog item. [Official contract documentation](https://mexcdevelop.github.io/apidocs/contract_v1_en/#switch-the-risk-level).
- Kraken `POST /0/private/WithdrawStatus` is deprecated; the official guidance points to Funding (Beta). [Official documentation](https://docs.kraken.com/api-reference/funding/get-status-of-recent-withdrawals). The existing Futures fee-schedule deprecation note still applies.
- Current schemas remain unknown for Lighter historicalTrades export and the previously unconfirmed Binance COIN-M algo / legacy BingX spot-time entries.
- External withdrawal submission, transfers outside the account family and MM/partner-only operations remain explicitly excluded. Read-only withdrawal/transfer history must not be swept into that exclusion.

## False positives resolved

- Arcus get_trade/get_fill use dynamic IDs and have sync/async Python methods; settleLoanResults is supported.
- Arcus get_commission_rates still has only Rust named dispatch and Python generic access; its documented purpose is referral commissions, not ordinary trading fees.
- KuCoin synchronous cancellation uses dynamic order/client IDs and is implemented.
- Kraken history and Extended funding/interest combined rows cannot be checked as a single literal path.
- BingX subaccount API key queries are exposed through get_api_key_info(uid, apiKey) at /openApi/account/v1/apiKey/query, rather than the report's older path.

No additional ordinary Ondo endpoint gap was identified in this recheck. This is not a guarantee of full official API coverage. The exact remaining total is unknown until combined rows, product scope and incomplete official schemas are individually reconciled.
