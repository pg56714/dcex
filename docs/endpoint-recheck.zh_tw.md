# 端點複查：待處理項目

[English](endpoint-recheck.md) | **繁體中文**

核對日期：2026-09-28。原始報表有 3,180 列；目前清冊共 4,846 列，另保存 15 家交易所的官方文件清冊。

所有官方端點均納入範圍，包含提款、地址管理、做市商、RFQ、經紀商、推薦與合作夥伴操作。原先 111 個 excluded 列已處理，沒有保留範圍排除；這不代表所有新發現端點均已實作。

API 提款沒有第二次確認，送出即執行。建議交易用 API 金鑰不要開啟提款權限。需要錢包授權的操作保留呼叫端提供的簽章；不臆測未公開的簽章規格。

[清冊與逐列原因](endpoint-coverage-ledger.json) · [可篩選的待處理列表](endpoint-coverage.html)

## 規格與可用性缺口

| 列 | 交易所 | 操作 | 狀態 | 官方文件 |
| ---: | --- | --- | --- | --- |
| 8 | binance | Margin user data (margin-stream.binance.com, /sapi/v1/margin/listen-key) | `partial` | [Docs](https://developers.binance.com/en/docs/products/margin-trading/listen-token-data-stream) |
| 1367 | okx | POST /api/v5/finance/stable-rewards/quote | `unavailable` | [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1368 | okx | POST /api/v5/finance/stable-rewards/trade | `unavailable` | [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1369 | okx | GET /api/v5/finance/stable-rewards/subscribe-redeem-history | `unavailable` | [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1986 | bingx | - | `unavailable` | [Docs](https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/swap-ws-account/api-reference.md#L3) |
| 2065 | kraken | GET /derivatives/api/v3/feeschedules | `unavailable` | [Docs](https://docs.kraken.com/api-reference/fee-schedules/get-fee-schedules) |
| 2066 | kraken | GET /derivatives/api/v3/feeschedules/volumes | `unavailable` | [Docs](https://docs.kraken.com/api-reference/fee-schedules/get-fee-schedule-volumes) |
| 2218 | mexc | POST /api/v1/private/account/change_risk_level | `unavailable` | [Docs](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/change-risk-level) |
| 2472 | kucoin | DELETE /api/v3/hf/margin/stop-order/cancel-by-id | `unverified` | [Docs](https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-stop-order-by-orderld) |
| 2651 | hyperliquid | sendToEvmWithData | `unverified` | [Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#send-to-evm-with-data) |
| 2846 | backpack | GET /wapi/v1/capital/withdrawals/delay | `blocked` | [Docs](https://docs.backpack.exchange/#tag/Withdrawal-Delays/operation/get_withdrawal_delay) |
| 2847 | backpack | POST /wapi/v1/capital/withdrawals/delay | `blocked` | [Docs](https://docs.backpack.exchange/#tag/Withdrawal-Delays/operation/create_withdrawal_delay) |
| 2848 | backpack | PATCH /wapi/v1/capital/withdrawals/delay | `blocked` | [Docs](https://docs.backpack.exchange/#tag/Withdrawal-Delays/operation/update_withdrawal_delay) |
| 2876 | aster | GET /api/v3/ticker/opt/24hr | `unverified` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-spot-api-v3.md#24h-price-change) |
| 2886 | aster | POST /api/v3/batchOrders | `unverified` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-spot-api-v3.md#cancel-all-open-orders-trade) |
| 2887 | aster | DELETE /api/v3/batchOrders | `unverified` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-spot-api-v3.md#cancel-all-open-orders-trade) |
| 2910 | aster | GET /fapi/v3/marketKlines | `unverified` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#mark-price-klinecandlestick-data) |
| 2969 | aster | POST /fapi/v3/asset/migrateUser | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#migrate-user-assets-withdraw) |
| 3162 | arcus | POST /v1/settleLoan | `unavailable` | [Docs](https://docs.arcus.xyz/api-reference/exchange/sell-spot-collateral-to-settle-the-accounts-loan) |
| 3240 | bybit | POST /v5/grid/close-grid | `unverified` | [Docs](https://bybit-exchange.github.io/docs/v5/bot/spot-grid/close) |
| 3321 | bybit | GET /v5/compliance/appeal/list | `unverified` | [Docs](https://bybit-exchange.github.io/docs/v5/tm-onchain/appeal-list) |
| 3374 | kucoin | POST /api/v2/broker/withdrawal | `unverified` | [Docs](https://www.kucoin.com/docs-new/rest/broker/exchange-broker/apply-for-fast-withdrawal) |
| 3555 | kraken | GET /funding/v1/deposits | `unverified` | [Docs](https://docs.kraken.com/api-reference/funding-beta/list-funding-deposits) |
| 3585 | lighter | POST /api/v1/sendTx | `blocked` | [Docs](https://apidocs.lighter.xyz/reference/sendtx) |
| 3586 | lighter | POST /api/v1/sendTx | `blocked` | [Docs](https://apidocs.lighter.xyz/reference/sendtx) |
| 3587 | lighter | POST /api/v1/sendTx | `blocked` | [Docs](https://apidocs.lighter.xyz/reference/sendtx) |
| 3588 | binance | POST /sapi/v1/userListenToken | `blocked` | [Docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/user-data-stream) |
| 3715 | aster | GET /aster-chain/v3/account/status | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#get-account-status-user_data) |
| 3716 | aster | POST /aster-chain/v3/account/modify-status | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#modify-account-status-trade) |
| 3717 | aster | POST /aster-chain/v3/transfer | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#transfer-to-address-withdraw) |
| 3718 | aster | GET /aster-chain/v3/staking/stakeAccountStatus | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#get-staking-account-status-user_data) |
| 3719 | aster | GET /aster-chain/v3/staking/myStaking | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#get-my-staking-user_data) |
| 3720 | aster | GET /aster-chain/v3/staking/claimableRewards | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#get-claimable-rewards-user_data) |
| 3721 | aster | POST /aster-chain/v3/staking/create | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#create-staking-trade) |
| 3722 | aster | POST /aster-chain/v3/staking/deposit | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#deposit-stake-trade) |
| 3723 | aster | POST /aster-chain/v3/staking/updateLockPeriod | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#update-lock-period-trade) |
| 3724 | aster | POST /aster-chain/v3/staking/claimRewards | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#claim-rewards-trade) |
| 3726 | aster | GET /aster-chain/v3/spot/user-deposit-address | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#get-user-deposit-address-user_data) |
| 3727 | aster | POST /aster-chain/v3/perp/user-withdraw | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#user-withdraw-withdraw) |
| 3728 | aster | POST /aster-chain/v3/perp/user-solana-withdraw | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#user-solana-withdraw-withdraw) |
| 3729 | aster | GET /aster-chain/v3/perp/user-withdraw-info | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#get-withdraw-info-user_data) |
| 3730 | aster | GET /aster-chain/v3/perp/deposit-withdraw-history | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#depositwithdraw-history-user_data) |
| 3731 | aster | POST /aster-chain/v3/perp/wallet/transfer | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#wallet-transfer-trade) |
| 3732 | aster | POST /aster-chain/v3/spot/user-withdraw | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#user-withdraw-withdraw) |
| 3733 | aster | POST /aster-chain/v3/spot/user-solana-withdraw | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#user-solana-withdraw-withdraw) |
| 3734 | aster | POST /aster-chain/v3/spot/wallet/transfer | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-chain.md#wallet-transfer-trade) |
| 3739 | aster | POST /v1/private/campaign/portfolio/summary/pro | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/bapi/aster-bapi-en.md#3-pro-summary) |
| 3740 | aster | POST /v1/private/campaign/portfolio/overview/v2/line/chart | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/bapi/aster-bapi-en.md#4-portfolio-line-chart) |
| 3741 | aster | POST /v1/private/campaign/portfolio/overview/line/calendar | `blocked` | [Docs](https://github.com/asterdex/api-docs/blob/master/bapi/aster-bapi-en.md#5-portfolio-line-calendar) |
| 4073 | bitget | GET /api/v3/trade/demo-placeholder | `unavailable` | [Docs](https://www.bitget.com/docs/catalog/stock-plus/fills#stock-fills-placeholder) |
| 4196 | aster | WS 40xx - Filters and other Issues (channel=40xx - Filters and other Issues) | `unavailable` | [Docs](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-futures-api-testnet.md#L4946) |
| 4218 | aster | WS 40xx - Filters and other Issues (channel=40xx - Filters and other Issues) | `unavailable` | [Docs](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#L6518) |
| 4231 | aster | WS How to correctly maintain a local copy of an order book (channel=How to correctly maintain a local copy of an order book) | `unavailable` | [Docs](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-prediction-api-tesetnet.md#L2427) |
| 4245 | aster | WS How to correctly maintain a local copy of an order book (channel=How to correctly maintain a local copy of an order book) | `unavailable` | [Docs](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-prediction-api.md#L2427) |
| 4258 | aster | WS How to correctly maintain a local copy of an order book (channel=How to correctly maintain a local copy of an order book) | `unavailable` | [Docs](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-spot-api-testnet.md#L2056) |
| 4271 | aster | WS How to correctly maintain a local copy of an order book (channel=How to correctly maintain a local copy of an order book) | `unavailable` | [Docs](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-spot-api-v3.md#L2058) |
| 4378 | binance | WS /session.logon (channel=session_logon) | `unavailable` | [Docs](https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/ws-api/auth#session-logon) |
| 4711 | mexc | WS /ws (channel=enum-definitions) | `unavailable` | [Docs](https://www.mexc.com/api-docs/futures/websocket-api/enum-definitions) |
| 4712 | mexc | WS /ws (channel=incremental-order-book-maintenance-mechanism) | `unavailable` | [Docs](https://www.mexc.com/api-docs/futures/websocket-api/incremental-order-book-maintenance-mechanism) |
| 4718 | mexc | WS /ws (channel=how-to-properly-maintain-a-local-copy-of-the-order-book) | `unavailable` | [Docs](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams/how-to-properly-maintain-a-local-copy-of-the-order-book) |
| 4736 | mexc | WS /ws (channel=deduction-info) | `unverified` | [Docs](https://www.mexc.com/api-docs/futures/websocket-api/deduction-info) |

## 新增清冊的待處理列

目前所有清冊列均有明確處理狀態；未公開規格或仍待確認者保留在上表。一般 WebSocket 支援不會自動算成每個官方主題均驗證完成。

| 交易所 | REST／操作待處理 | WebSocket 待處理 |
| --- | ---: | ---: |
| binance | 0 | 0 |
| bybit | 0 | 0 |
| okx | 0 | 0 |
| bitget | 0 | 0 |
| bingx | 0 | 0 |
| kraken | 0 | 0 |
| mexc | 0 | 0 |
| kucoin | 0 | 0 |
| hyperliquid | 0 | 0 |
| lighter | 0 | 0 |
| backpack | 0 | 0 |
| aster | 0 | 0 |
| extended | 0 | 0 |
| ondo | 0 | 0 |
| arcus | 0 | 0 |
