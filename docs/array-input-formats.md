# Array input formats

Checked against the linked official API pages on 2026-09-30. Each row has sync and async localhost wire coverage for a Python list and its string representation. CSV is accepted only where declared; other arrays accept JSON array strings. Object lists must not be flattened into CSV.

The fixture records all 67 newly declared fields, including wire-name aliases. `json` means a JSON array string accepted by the Python boundary; the endpoint adapter retains the official JSON body or encoded query/form representation. `repeated` accepts a JSON array string and emits repeated query/form keys. `csv` accepts comma-separated input and delegates endpoint-specific serialization.

Binance dust conversion emits one `asset=BTC,ETH` parameter. Backpack market types and Binance prediction token IDs use repeated keys. Bitget UTA uses a top-level JSON array (the linked legacy example shows the array omitted by the newer catalogue rendering). BingX swap batch IDs use JSON arrays: numeric system IDs and quoted string client IDs, including leading zeros. Lighter accepts CSV input and emits repeated `type` query keys.

| Exchange | Method / field | String input | Official source |
|---|---|---|---|
| arcus | `batch_cancel_orders.cancels` | json | [API](https://docs.arcus.xyz/api-reference/exchange/batch-cancel-orders) |
| aster | `cancel_futures_batch_orders.orderIdList` | json | [API](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#cancel-multiple-orders-trade) |
| aster | `cancel_futures_batch_orders.origClientOrderIdList` | json | [API](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#cancel-multiple-orders-trade) |
| aster | `guarded_cancel_futures_batch_orders.orderIdList` | json | [API](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#cancel-multiple-orders-guarded-trade) |
| aster | `guarded_cancel_futures_batch_orders.origClientOrderIdList` | json | [API](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-futures-api-v3.md#cancel-multiple-orders-guarded-trade) |
| aster | `cancel_all_spot_open_orders.orderIdList` | json | [API](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-prediction-api-tesetnet.md#L1409) |
| aster | `cancel_all_spot_open_orders.origClientOrderIdList` | json | [API](https://github.com/asterdex/api-docs/blob/eeddec8d97cd1250351f62b976973ae2a0d583c5/V3%28Recommended%29/EN/aster-finance-prediction-api-tesetnet.md#L1409) |
| backpack | `get_order_history.marketType` | repeated | [API](https://docs.backpack.exchange/#tag/Order/operation/get_order_history) |
| binance | `cancel_options_batch_orders.orderIds` | json | [API](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/trade#cancel-multiple-option-orders) |
| binance | `cancel_options_batch_orders.clientOrderIds` | json | [API](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/rest-api/trade#cancel-multiple-option-orders) |
| binance | `cancel_futures_batch_orders.order_ids` | json | [API](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#cancel-multiple-orders) |
| binance | `cancel_futures_batch_orders.client_order_ids` | json | [API](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#cancel-multiple-orders) |
| binance | `cancel_coin_futures_batch_orders.order_ids` | json | [API](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#cancel-multiple-orders) |
| binance | `cancel_coin_futures_batch_orders.client_order_ids` | json | [API](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/trade#cancel-multiple-orders) |
| binance | `wallet_dust_transfer.asset` | csv | [API](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/asset#dust-transfer) |
| binance | `prediction_batch_redeem.token_ids` | json | [API](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/redeem#batch-redeem) |
| binance | `prediction_batch_cancel_orders.cancel_info_list` | json | [API](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#batch-cancel-orders) |
| bingx | `post_wealth_v1_product_dual_currency_order.select_accounts` | json | [API](https://bingx-api.github.io/docs-v3/#/en/Wealth/Dual-Currency/Dual-Currency%20Place%20Order) |
| bingx | `cancel_spot_batch_orders.order_ids` | csv | [API](https://bingx-api.github.io/docs-v3/#/en/Spot/Trades%20Endpoints/Cancel%20multiple%20orders) |
| bingx | `cancel_spot_batch_orders.client_order_ids` | csv | [API](https://bingx-api.github.io/docs-v3/#/en/Spot/Trades%20Endpoints/Cancel%20multiple%20orders) |
| bingx | `cancel_swap_batch_order.order_id_list` | json | [API](https://bingx-api.github.io/docs-v3/#/en/Swap/Trades%20Endpoints/Cancel%20multiple%20orders) |
| bingx | `cancel_swap_batch_order.client_order_id_list` | json | [API](https://bingx-api.github.io/docs-v3/#/en/Swap/Trades%20Endpoints/Cancel%20multiple%20orders) |
| bitget | `cancel_spot_batch_orders.order_list` | json | [API](https://www.bitget.com/docs/catalog/classic-spot-trade/classic-spot-trade#batch-cancel-orders) |
| bitget | `cancel_uta_batch_orders.order_list` | json | [API](https://www.bitget.com/legacy-docs/uta/trade/Cancel-Batch) |
| bitget | `cancel_futures_batch_orders.order_id_list` | json | [API](https://www.bitget.com/docs/catalog/classic-contract-trade/classic-contract-trade#batch-cancel) |
| bitget | `cancel_futures_batch_orders.orderIdList` | json | [API](https://www.bitget.com/docs/catalog/classic-contract-trade/classic-contract-trade#batch-cancel) |
| bitget | `cancel_cross_margin_batch_orders.orders` | json | [API](https://www.bitget.com/docs/catalog/classic-margin-cross-trade/classic-margin-cross-trade#cross-batch-cancel-orders) |
| bitget | `cancel_cross_margin_batch_orders.orderIdList` | json | [API](https://www.bitget.com/docs/catalog/classic-margin-cross-trade/classic-margin-cross-trade#cross-batch-cancel-orders) |
| bitget | `cancel_isolated_margin_batch_orders.orders` | json | [API](https://www.bitget.com/api-doc/margin/isolated/trade/Isolated-Batch-Cancel-Orders) |
| bitget | `cancel_isolated_margin_batch_orders.orderIdList` | json | [API](https://www.bitget.com/api-doc/margin/isolated/trade/Isolated-Batch-Cancel-Orders) |
| bitget | `cancel_futures_plan_orders.order_id_list` | json | [API](https://www.bitget.com/docs/catalog/classic-contract-plan/classic-contract-plan#cancel-trigger-order) |
| bitget | `cancel_spot_plan_orders.symbol_list` | json | [API](https://www.bitget.com/docs/catalog/classic-spot-plan/classic-spot-plan#cancel-plan-orders-in-batch) |
| bitget | `classic_copytrading_spot_copytrade_follower_order_close_tracking.tracking_no_list` | json | [API](https://www.bitget.com/api-doc/classic/copytrading/spot-copytrade/follower/Order-Close-Tracking) |
| bitget | `classic_copytrading_spot_copytrade_follower_stop_order.tracking_no_list` | json | [API](https://www.bitget.com/api-doc/classic/copytrading/spot-copytrade/follower/Stop-Order) |
| bitget | `classic_copytrading_spot_copytrade_trader_order_close_tracking.tracking_no_list` | json | [API](https://www.bitget.com/docs/catalog/classic-copytrading-spot-trader/classic-copytrading-spot-copytrade-trader#sell-and-sell-in-batch) |
| bybit | `batch_set_collateral_coins.request` | json | [API](https://bybit-exchange.github.io/docs/v5/account/batch-set-collateral) |
| bybit | `get_transferable_amount.coins` | csv | [API](https://bybit-exchange.github.io/docs/v5/account/unified-trans-amnt) |
| bybit | `get_alpha_lp_order_list.order_status` | json | [API](https://bybit-exchange.github.io/docs/v5/alpha/lp/order-list) |
| bybit | `request_alpha_prediction_order_book.token_ids` | json | [API](https://bybit-exchange.github.io/docs/v5/alpha/prediction/order-book) |
| bybit | `get_alpha_trade_order_list.order_status` | json | [API](https://bybit-exchange.github.io/docs/v5/alpha/trade/order-list) |
| hyperliquid | `cancel_batch_orders.cancels` | json | [API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-orders) |
| hyperliquid | `cancel_batch_orders_by_cloid.cancels` | json | [API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#cancel-orders-by-cloid) |
| kraken | `cancel_spot_batch_orders.orders` | json | [API](https://docs.kraken.com/api-reference/trading/cancel-order-batch) |
| kraken | `cancel_spot_batch_orders.cl_ord_ids` | json | [API](https://docs.kraken.com/api-reference/trading/cancel-order-batch) |
| kraken | `get_futures_order_status.orderIds` | csv | [API](https://docs.kraken.com/api-reference/order-management/get-specific-orders-status) |
| kraken | `get_futures_order_status.cliOrdIds` | csv | [API](https://docs.kraken.com/api-reference/order-management/get-specific-orders-status) |
| kucoin | `batch_cancel_uta_orders.cancel_order_list` | json | [API](https://www.kucoin.com/docs-new/v2/rest/ua/batch-cancel-order-by-id) |
| kucoin | `cancel_futures_batch_orders.order_ids` | json | [API](https://www.kucoin.com/docs-new/3470241e0) |
| kucoin | `cancel_futures_batch_orders.client_orders` | json | [API](https://www.kucoin.com/docs-new/3470241e0) |
| kucoin | `set_futures_batch_margin_mode.symbols` | json | [API](https://www.kucoin.com/docs-new/rest/futures-trading/positions/batch-switch-margin-mode) |
| lighter | `get_transfer_history.type_` | csv | [API](https://apidocs.lighter.xyz/reference/transfer_history) |
| mexc | `cancel_contract_batch_orders_by_external_id.orders` | json | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/batch-cancel-by-external-order-id) |
| mexc | `get_contract_batch_orders_by_external_id.orders` | json | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/batch-query-orders-by-external-order-id) |
| mexc | `cancel_contract_orders.orders` | json | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/cancel-orders) |
| mexc | `get_contract_orders.order_ids` | csv | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/batch-query-orders-by-order-id) |
| mexc | `cancel_contract_plan_orders.orders` | json | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/cancel-planned-orders) |
| mexc | `get_contract_trailing_orders.states` | csv | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/query-trailing-orders) |
| mexc | `cancel_contract_tpsl_orders.orders` | json | [API](https://www.mexc.com/api-docs/futures/account-and-trading-endpoints/cancel-tpsl-planned-orders) |
| okx | `trading_bot_recurring_order_algo.source` | json | [API](https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-place-recurring-buy-order) |
| okx | `rfq_cancel_batch_rfqs.rfq_ids` | json | [API](https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs) |
| okx | `rfq_cancel_batch_rfqs.cl_rfq_ids` | json | [API](https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs) |
| okx | `rfq_cancel_batch_rfqs.rfqIds` | json | [API](https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs) |
| okx | `rfq_cancel_batch_rfqs.clRfqIds` | json | [API](https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs) |
| okx | `cancel_rfq_batch_quotes.quote_ids` | json | [API](https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-quotes) |
| okx | `cancel_rfq_batch_quotes.cl_quote_ids` | json | [API](https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-quotes) |
| okx | `get_max_withdrawal.ccy` | csv | [API](https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-maximum-withdrawals) |
| ondo | `batch_cancel_orders.orderIDs` | csv | [API](https://docs.ondoperps.xyz/api-reference/orders/batch-cancel-orders) |
