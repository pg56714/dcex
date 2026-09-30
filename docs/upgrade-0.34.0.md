# Upgrading to Python 0.34.0 / Rust rust-v0.12.0

This guide covers caller-contract changes from 0.33.0 / rust-v0.11.0 and safety requirements introduced in the same release. Python sync and async surfaces share the rules; await async calls. In examples, `...` and `args` stand for the other required arguments, and examples are not executed automatically. Error columns contain actual messages or stable fragments; full prefixes differ between Python binding, native validation and exchange responses.

`CHANGELOG.md` is CI-generated; this guide is maintained separately. Read the [intermediate-commit deployment restriction](intermediate-commit-deployment.md) before deploying historical commits.

## Explicit consent and operation scope

Irreversible/sensitive operations require the literal boolean `confirm=True`, not the Python string `"true"`. Account-wide operations require a nonempty symbol/order scope or `all_symbols=True`, exclusively. Backpack vault redemption uses `all=True`, exclusive with `vault_token_quantity`. These flags are local consent controls and are removed before exchange serialization.

| Rule | Old call | New call | Error |
|---|---|---|---|
| confirm | `client.delete_api_key(**args)` | `client.delete_api_key(**args, confirm=True)` | `confirm=True is required for this account operation` |
| scope | `client.cancel_spot_all_orders()` | `client.cancel_spot_all_orders(product_symbol="BTC-USDT-SPOT")` or `client.cancel_spot_all_orders(all_symbols=True)` | `provide a nonempty scope or all_symbols=True, exclusively` |
| vault | `client.vault_redeem(vault_id=1)` | `client.vault_redeem(vault_id=1, vault_token_quantity="1")` or `client.vault_redeem(vault_id=1, all=True)` | `provide a nonempty scope or all=True, exclusively` |

The table lists every public REST entry point. For each row, the old form is `client.method(**args)`; the new form adds the listed flag (or an explicit scope). Python errors use the confirm/scope messages above, except the native-specific case listed below.

| Method | New requirement |
|---|---|
| `aster.trigger_futures_asset_exchange` | `confirm=True` |
| `backpack.cancel_open_strategies` | `all_symbols=True` or explicit scope |
| `bingx.cancel_coin_swap_all_orders` | `all_symbols=True` or explicit scope |
| `bingx.close_coin_swap_all_positions` | `all_symbols=True` or explicit scope |
| `bingx.delete_cswap_v1_trade_all_open_orders` | `all_symbols=True` or explicit scope |
| `bingx.reverse_swap_position` | `confirm=True` |
| `bingx.set_swap_asset_mode` | `confirm=True` |
| `bitget.broker_delete_subaccount_apikey` | `confirm=True` |
| `bitget.cancel_futures_plan_orders` | `all_symbols=True` or explicit scope |
| `bitget.cancel_spot_plan_orders` | `all_symbols=True` or explicit scope |
| `bitget.cfd_trade_cancel_all_orders` | `confirm=True` |
| `bitget.cfd_trade_close_all_positions` | `confirm=True` |
| `bitget.classic_broker_apikey_delete_subaccount_api_key` | `confirm=True` |
| `bitget.classic_copytrading_future_copytrade_follower_close_positions` | `all_symbols=True` or explicit scope |
| `bitget.classic_copytrading_future_copytrade_trader_trader_order_close_positions` | `all_symbols=True` or explicit scope |
| `bitget.close_futures_positions` | `all_symbols=True` or explicit scope |
| `bitget.close_uta_positions` | `all_symbols=True` or explicit scope |
| `bitget.copy_trading_follower_close_all` | `confirm=True` |
| `bitget.delete_uta_subaccount` | `confirm=True` |
| `bitget.move_uta_positions` | `confirm=True` |
| `bitget.p2p_order_management_confirm_payment` | `confirm=True` |
| `bitget.p2p_order_management_release_asset` | `confirm=True` |
| `bitget.reverse_futures_position` | `confirm=True` |
| `bitget.set_futures_asset_mode` | `confirm=True` |
| `bitget.set_uta_account_mode` | `confirm=True` |
| `bitget.upgrade_classic_account` | `confirm=True` |
| `bitget.upgrade_to_uta` | `confirm=True` |
| `bybit.delete_api_key` | `confirm=True` |
| `bybit.modify_api_key` | `confirm=True` |
| `hyperliquid.convert_to_multi_sig_user_signed` | `confirm=True` |
| `hyperliquid.perp_deploy_disable_dex` | `confirm=True` |
| `kucoin.cancel_futures_stop_orders` | `all_symbols=True` or explicit scope |
| `kucoin.cancel_margin_oco_orders` | `all_symbols=True` or explicit scope |
| `kucoin.cancel_spot_oco_orders` | `all_symbols=True` or explicit scope |
| `kucoin.cancel_spot_stop_orders` | `all_symbols=True` or explicit scope |
| `kucoin.delete_v1_broker_nd_account_apikey` | `confirm=True` |
| `kucoin.set_uta_account_mode` | `confirm=True` |
| `mexc.cancel_spot_all_orders` | `all_symbols=True` or explicit scope |
| `ondo.delete_api_key` | `confirm=True` |

Rust/native `params` use `("confirm", "true")` or `("all_symbols", "true")`; errors are `<method>: confirm=true is required` or `<method>: provide a symbol, order IDs, or all_symbols=true, exclusively`. KuCoin `delete_v1_broker_nd_account_apikey` rejects with `API key deletion requires confirm=true`. Bybit `modify_api_key(confirm=True)` still needs an actual change, otherwise it reports `at least one API key change is required`.

### WebSocket scope

- Kraken V1: `send_message({"event":"cancelAll"})` → `send_message({"event":"cancelAll"}, all_symbols=True)`; `cancelAllOrdersAfter` requires the same account-wide flag. Rejection: `Only account-wide cancellations require all_symbols=true.`
- OKX: a mass cancellation without an instrument family/spread needs `send_operation(..., all_symbols=True)`. Rejection: `provide an instrument family/spread or all_symbols=true exclusively`. Ordinary order operations must not pass that flag.

## Other call, input and response changes

### Exact decimal inputs

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `client.place_order(..., quantity=0.1)` | `client.place_order(..., quantity="0.1") / Decimal("0.1")` | `requires an exact decimal string or Decimal, not float/bool` |

Declared decimal fields reject floats and bools, including nested orders, TP/SL and batches. Plain strings, finite Decimal and valid integers preserve precision. Rust/native callers supply plain decimal strings.

### Scientific notation and bounds

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `price="1e-7" / quantity="-1" / price="0"` | `price="0.0000001"; positive quantities/prices` | `requires a plain decimal string / must be a positive plain decimal string` |

The explicit input catalog controls sign, positive bounds and sentinels. Quantities and ordinary limit prices cannot use zero unless the endpoint declares it. Integer/boolean metadata declarations are not a general runtime type validator.

### Structured arrays and objects

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `rfq_cancel_batch_rfqs(rfq_ids="a,b")` | `rfq_cancel_batch_rfqs(rfq_ids=["a", "b"]) / rfq_ids='["a","b"]'` | `must be a JSON array / must be a JSON object` |

Arrays accept lists and JSON array strings; CSV is supported only for the 11 declared fields. Object arrays cannot be flattened into CSV. See array-input-formats for all 67 fields, wire aliases and repeated-key exceptions.

### Kraken margin selection

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `set_futures_leverage_preference("PF_XBTUSD")` | `set_futures_leverage_preference("PF_XBTUSD", margin_mode="cross") / margin_mode="isolated", max_leverage="5"` | `missing required parameter: margin_mode / margin_mode must be cross without maxLeverage, or isolated with maxLeverage` |

Choose cross without a leverage cap or isolated with a positive cap. Do not infer the account setting from an omitted argument.

### BingX position side

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `place_swap_market_buy_order("BTC-USDT-SWAP", "1")` | `place_swap_market_buy_order("BTC-USDT-SWAP", "1", position_side="LONG")` | `missing a required argument: 'position_side' / missing required parameter: positionSide` |

The six market/limit/post-only buy/sell helpers require position_side. Supply LONG/SHORT for hedge positions or BOTH when using one-way mode; choose the value for the actual account. Lower-level orders must satisfy their explicit side/close rules too.

### MEXC opening leverage

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `place_contract_market_buy_order("BTC-USDT-SWAP", vol=1)` | `place_contract_market_buy_order("BTC-USDT-SWAP", vol=1, leverage=5)` | `missing required parameter: leverage (required for MEXC Contract opening orders, side 1 or 3)` |

The nine contract market/limit/post-only wrappers no longer default leverage to 50. Opening sides 1/3 require an explicit value; closing sides 2/4 do not gain this requirement.

### KuCoin disconnection protection

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `set_dcp(0); set_dcp(..., product_symbol="BTC-USDT")` | `set_dcp(-1) to disable; set_dcp(30, symbols=["BTC-USDT"]) to arm` | `KuCoin DCP timeout must be -1 or between 5 and 86400 / unexpected keyword argument` |

DCP targets spot /api/v1/hf/orders/dead-cancel-all; get_dcp uses its /query route. symbols is a list or CSV of at most 50 pairs; omitted/empty means all pairs. There is no futures DCP implied by these methods.

### Binance batch return shape

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `for item in client.place_futures_batch_orders(orders): ...` | `result = client.place_futures_batch_orders(orders); inspect result["ok"] and result["errors"]` | `No exception is guaranteed for partial failure; inspect errors even after HTTP 200.` |

Place/amend/cancel for USD-M and COIN-M, plus options place/cancel, return two arrays. Each entry preserves index and response. Preserve the input index for reconciliation; retry only after checking individual exchange errors.

### Binance conditional batches

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `place_futures_batch_orders([{"type":"STOP_MARKET", ...}])` | `place_futures_algo_order(...) / place_coin_futures_algo_order(...)` | `USD-M conditional orders cannot be batched; use place_futures_algo_order` |

Use the market-specific REST algo surface. COIN-M reports its own migration error and /dapi/v1/algoOrder route. LIMIT/MARKET batches reject closePosition, mixed identifier lists, oversized lists and invalid types locally.

### OKX attached order corrections

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `amend_order(..., attachAlgoOrds=[{"newSz":"1"}])` | `amend_order(..., attachAlgoOrds=[{"sz":"1"}])` | `contains unsupported fields: newSz` |

Amend attached size is sz, positive. Algo-order attached items do not accept sz/newSz. Placement ratios are greater than -1 and nonzero; amend new* ratios allow zero to delete, including negative sell ratios. -1 remains only a declared TP/SL market-price sentinel. closeFraction omits algo sz rather than sending sz=0.

### BingX optional attached orders

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `takeProfit="{}" / stopLoss={} / takeProfit="   "` | `omit unused fields or pass None; supply a nonempty JSON object when used` | `must be a nonempty JSON object` |

Single swap, coin-M and batch consistently omit null, empty string and whitespace TP/SL. Empty objects are rejected. Nested decimal fields retain exact values; client order IDs remain quoted strings including leading zeros.

### Documented zero and relative exceptions

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `send qty=0 without closing flags; use absolute triggerQuantity="0"` | `Bybit qty="0" only with reduceOnly=True and closeOnTrigger=True; Backpack triggerQuantity="10%" or a positive absolute value` | `must be a positive plain decimal string / requires a decimal percentage greater than 0% and at most 100%` |

Kraken zero-volume closing orders retain reduce_only=True; convenience placement/edit wrappers need positive volume. Kraken relative prices +5, -5, #5 and percentages remain supported. Signed margin deltas and declared TP/SL deletion zeros remain valid.

### Backpack funding account filter

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `get_funding_payments(subaccountId=1)` | `get_funding_payments() on the intended authenticated client` | `unexpected keyword argument 'subaccountId'` |

This endpoint no longer exposes the unsupported subaccountId parameter; do not assume an unaccepted query field selects a subaccount.

### BingX aggregated order-book depth

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `get_spot_orderbook_v2("BTC-USDT-SPOT", limit=5)` | `get_spot_orderbook_v2("BTC-USDT-SPOT", depth=5)` | `unexpected keyword argument 'limit' / missing a required argument: 'depth'` |

depth is explicit and required for the V2 aggregated book. The separate get_spot_orderbook still has its own limit argument.

### KuCoin market boundaries

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `batch_cancel_uta_orders(trade_type="SPOT", cancel_order_list=[{"symbol":"XBTUSDTM", ...}])` | `use matching trade_type and symbols for SPOT/MARGIN/FUTURES` | `tradeType` |

A symbol from another market is rejected instead of silently selecting a different market. The error names tradeType; its full text depends on the offending symbol.

### Ondo product-table expansion

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `iterate get_product_symbols(exchange="ondo") and trade every row` | `get_product_symbols(exchange="ondo", product_type="swap") for perpetual trading` | `Ondo -SPOT symbols are only valid for get_spot_* endpoints` |

Spot rows are public-data products. Private spot order/balance contracts remain unavailable. The follow-up WS fix accepts SPY-USDC-SPOT as well as SPY-USDC; the originally published 0.34.0 WS helpers require the exchange form SPY-USDC.

### Empty exchange packages and internal imports

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `import dcex.bitmart / bitmex / decibel / gateio; import private domain modules` | `use an implemented exchange Client and its documented public methods` | `ModuleNotFoundError / ImportError` |

Empty exchange packages are removed. Internal underscore modules were reorganized into domain mixins and are not stable import paths; use dcex.<exchange>.client.Client or its async_support equivalent.

### Canonical keyword conflicts

| Old call/assumption | New call/handling | Error or result |
|---|---|---|
| `place_spot_order(..., orderType="limit", order_type="limit")` | `provide only order_type="limit"` | `Provide only order_type; orderType is its legacy alias.` |

Bitget/BingX camelCase aliases generally remain compatible when declared; the snake_case rename alone is not a removal. Supplying both spellings now raises instead of choosing one silently. Native generic calls still use documented wire field names.

## Verification references

- [Array input formats](array-input-formats.md)
- [Schema and decimal contracts](schema-conventions.md)
- [Ondo spot scope](ondo-spot.md)
- [Python operation guards](../dcex/_operation_guards.py)
- [Rust operation guards](../crates/dcex/src/exchanges/operation_guards.rs)
- [Complete explicit input catalog](../dcex/_input_contracts.json)
- [Endpoint coverage and replacements](endpoint-audit.md)
