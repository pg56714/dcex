use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{AsterClient, AsterMarket};
use super::endpoints::*;
use super::params::AsterParams;

const FUTURES_ORDER_KEYS: &[&str] = &[
    "positionSide",
    "type",
    "timeInForce",
    "quantity",
    "reduceOnly",
    "price",
    "newClientOrderId",
    "stopPrice",
    "closePosition",
    "activationPrice",
    "callbackRate",
    "workingType",
    "priceProtect",
    "newOrderRespType",
    "pegPriceType",
    "pegOffset",
    "stpMode",
];

const BATCH_ORDER_KEYS: &[&str] = &[
    "symbol",
    "product_symbol",
    "side",
    "positionSide",
    "type",
    "timeInForce",
    "quantity",
    "reduceOnly",
    "price",
    "newClientOrderId",
    "stopPrice",
    "activationPrice",
    "callbackRate",
    "workingType",
    "priceProtect",
    "newOrderRespType",
];

const STRATEGY_SUB_ORDER_KEYS: &[&str] = &[
    "strategySubId",
    "securityType",
    "symbol",
    "product_symbol",
    "side",
    "positionSide",
    "type",
    "quantity",
    "price",
    "stopPrice",
    "timeInForce",
    "workingType",
    "reduceOnly",
    "closePosition",
    "priceProtect",
    "clientOrderId",
    "activationPrice",
    "callbackRate",
    "firstDrivenId",
    "firstDrivenOn",
    "firstTrigger",
    "secondDrivenId",
    "secondDrivenOn",
    "secondTrigger",
];

impl AsterClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = AsterParams::from_pairs(params);
        validate_private_params(method_name, &params)?;
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Aster private method: {method_name}"
        )))
    }

    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &AsterParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "place_spot_order" => {
                let mut query = params.only(&[
                    "type",
                    "timeInForce",
                    "quantity",
                    "quoteOrderQty",
                    "price",
                    "newClientOrderId",
                    "stopPrice",
                ]);
                self.push_required_symbol(&mut query, params)?;
                self.push_required_side(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Spot, SPOT_ORDER, query)
                    .await
            }
            "cancel_spot_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Delete, AsterMarket::Spot, SPOT_ORDER, query)
                    .await
            }
            "get_spot_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_ORDER, query)
                    .await
            }
            "get_spot_open_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_OPEN_ORDER, query)
                    .await
            }
            "get_spot_open_orders" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "cancel_all_spot_open_orders" => {
                let mut query = params.only(&["orderIdList", "origClientOrderIdList"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Spot,
                    SPOT_ALL_OPEN_ORDERS,
                    query,
                )
                .await
            }
            "get_spot_all_orders" => {
                let mut query = params.only(&["orderId", "startTime", "endTime", "limit"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_ALL_ORDERS, query)
                    .await
            }
            "get_spot_user_trades" => {
                let mut query =
                    params.only(&["orderId", "startTime", "endTime", "fromId", "limit"]);
                self.push_optional_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_USER_TRADES, query)
                    .await
            }
            "place_futures_order" => {
                let mut query = params.only(FUTURES_ORDER_KEYS);
                self.push_required_symbol(&mut query, params)?;
                self.push_required_side(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Futures, FUTURES_ORDER, query)
                    .await
            }
            "modify_futures_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId", "quantity", "price"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Put, AsterMarket::Futures, FUTURES_ORDER, query)
                    .await
            }
            "place_futures_chase_order" => {
                let mut query = params.only(&[
                    "positionSide",
                    "quantityUnit",
                    "quantity",
                    "reduceOnly",
                    "chaseOffset",
                    "chaseOffsetType",
                    "maxChaseOffset",
                    "maxChaseOffsetType",
                    "timeInForce",
                    "clientStrategyId",
                ]);
                self.push_required_symbol(&mut query, params)?;
                self.push_required_side(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Futures, FUTURES_CHASE, query)
                    .await
            }
            "place_futures_batch_orders" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_BATCH_ORDERS,
                    vec![(
                        "batchOrders".to_string(),
                        self.resolve_batch_orders(params)?,
                    )],
                )
                .await
            }
            "get_futures_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Futures, FUTURES_ORDER, query)
                    .await
            }
            "cancel_futures_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_ORDER,
                    query,
                )
                .await
            }
            "cancel_all_futures_open_orders" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_ALL_OPEN_ORDERS,
                    query,
                )
                .await
            }
            "cancel_futures_batch_orders" => {
                let mut query = params.only(&["orderIdList", "origClientOrderIdList"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_BATCH_ORDERS,
                    query,
                )
                .await
            }
            "set_futures_countdown_cancel_all" => {
                let mut query = params.only(&["countdownTime"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_COUNTDOWN_CANCEL_ALL,
                    query,
                )
                .await
            }
            "get_futures_open_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_OPEN_ORDER,
                    query,
                )
                .await
            }
            "get_futures_open_orders" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_OPEN_ORDERS,
                    query,
                )
                .await
            }
            "get_futures_all_orders" => {
                let mut query = params.only(&["orderId", "startTime", "endTime", "limit"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_ALL_ORDERS,
                    query,
                )
                .await
            }
            "set_futures_leverage" => {
                let mut query = params.only(&["leverage"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_LEVERAGE,
                    query,
                )
                .await
            }
            "set_futures_margin_type" => {
                let mut query = params.only(&["marginType"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_MARGIN_TYPE,
                    query,
                )
                .await
            }
            "place_futures_strategy_order" => {
                self.strategy_order(
                    HttpMethod::Post,
                    FUTURES_PLACE_STRATEGY_ORDER,
                    params,
                    false,
                )
                .await
            }
            "update_futures_strategy_order" => {
                self.strategy_order(
                    HttpMethod::Post,
                    FUTURES_UPDATE_STRATEGY_ORDER,
                    params,
                    true,
                )
                .await
            }
            "get_futures_strategy_open_order" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_STRATEGY_OPEN_ORDER,
                    params.only(&["strategyId", "clientStrategyId", "strategyType"]),
                )
                .await
            }
            "get_futures_strategy_history_order" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_STRATEGY_HISTORY_ORDER,
                    params.only(&[
                        "strategyId",
                        "clientStrategyId",
                        "strategyType",
                        "startTime",
                        "endTime",
                        "limit",
                    ]),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    fn push_required_side(
        &self,
        query: &mut Vec<(String, String)>,
        params: &AsterParams,
    ) -> Result<()> {
        query.push((
            "side".to_string(),
            params.required("side")?.to_ascii_uppercase(),
        ));
        Ok(())
    }

    pub(super) fn resolve_batch_orders(&self, params: &AsterParams) -> Result<String> {
        let mut value = params.json_required("batchOrders")?;
        let Value::Array(orders) = &mut value else {
            return Err(DcexError::InvalidInput(format!(
                "Aster batchOrders must be a JSON array."
            )));
        };
        if orders.is_empty() || orders.len() > 5 {
            return Err(DcexError::InvalidInput(
                "Aster batchOrders must contain between 1 and 5 orders.".to_string(),
            ));
        }
        for order in orders {
            self.resolve_order_object(order)?;
            let Value::Object(order) = order else {
                unreachable!("resolve_order_object validated object")
            };
            let order = AsterParams::from_json_object(order)?;
            order.ensure_allowed(BATCH_ORDER_KEYS, &[])?;
            validate_symbol_alias(&order, true)?;
            validate_futures_order(&order, true)?;
        }
        Ok(value.to_string())
    }

    fn resolve_order_object(&self, value: &mut Value) -> Result<()> {
        let Value::Object(order) = value else {
            return Err(DcexError::InvalidInput(
                "Aster order payload must be a JSON object.".to_string(),
            ));
        };
        if let Some(product_symbol) = order
            .remove("product_symbol")
            .and_then(|value| value.as_str().map(str::to_string))
        {
            order.insert(
                "symbol".to_string(),
                Value::String(self.exchange_symbol(&product_symbol)?),
            );
        } else if let Some(symbol) = order
            .get("symbol")
            .and_then(Value::as_str)
            .filter(|symbol| symbol.contains('-'))
            .map(str::to_string)
        {
            order.insert(
                "symbol".to_string(),
                Value::String(self.exchange_symbol(&symbol)?),
            );
        }
        if let Some(side) = order
            .get("side")
            .and_then(Value::as_str)
            .map(str::to_ascii_uppercase)
        {
            order.insert("side".to_string(), Value::String(side));
        }
        Ok(())
    }

    async fn strategy_order(
        &self,
        method: HttpMethod,
        path: &str,
        params: &AsterParams,
        update: bool,
    ) -> Result<ValidatedResponse> {
        let mut query = if update {
            params.only(&["strategyId", "strategyType"])
        } else {
            params.only(&["clientStrategyId", "strategyType", "builder", "feeRate"])
        };
        query.push((
            "subOrderList".to_string(),
            self.resolve_strategy_orders(params, update)?,
        ));
        self.signed(method, AsterMarket::Futures, path, query).await
    }

    fn resolve_strategy_orders(&self, params: &AsterParams, update: bool) -> Result<String> {
        let mut value = params.json_required("subOrderList")?;
        let Value::Array(orders) = &mut value else {
            return Err(DcexError::InvalidInput(
                "Aster subOrderList must be a JSON array.".to_string(),
            ));
        };
        let strategy_type = params.required("strategyType")?;
        let maximum = if strategy_type == "OTOCO" { 3 } else { 2 };
        if orders.is_empty()
            || (!update && orders.len() != maximum)
            || (update && orders.len() > maximum)
        {
            let requirement = if update {
                format!("between 1 and {maximum}")
            } else {
                format!("exactly {maximum}")
            };
            return Err(DcexError::InvalidInput(format!(
                "Aster {strategy_type} subOrderList must contain {requirement} orders."
            )));
        }
        for (index, order) in orders.iter_mut().enumerate() {
            self.resolve_order_object(order)?;
            let Value::Object(order) = order else {
                unreachable!("resolve_order_object validated object")
            };
            let order = AsterParams::from_json_object(order)?;
            order.ensure_allowed(STRATEGY_SUB_ORDER_KEYS, &[])?;
            validate_symbol_alias(&order, true)?;
            validate_strategy_sub_order(&order, update, index + 1)?;
        }
        Ok(value.to_string())
    }
}

fn ensure_order_lookup(params: &AsterParams) -> Result<()> {
    if params.get("orderId").is_none() && params.get("origClientOrderId").is_none() {
        return Err(DcexError::InvalidInput(
            "Specify orderId or origClientOrderId.".to_string(),
        ));
    }
    Ok(())
}

fn validate_private_params(method_name: &str, params: &AsterParams) -> Result<()> {
    match method_name {
        "get_spot_account"
        | "get_futures_position_mode"
        | "get_futures_stp_mode"
        | "get_futures_multi_assets_mode"
        | "get_futures_balance"
        | "get_futures_account"
        | "create_spot_listen_key"
        | "create_futures_listen_key"
        | "keep_alive_futures_listen_key"
        | "close_futures_listen_key" => params.ensure_allowed(&[], &[]),
        "get_spot_transaction_history" => {
            params.ensure_allowed(&["asset", "type", "startTime", "endTime", "limit"], &[])?;
            params.optional_one_of(
                "type",
                &[
                    "TRADE_TARGET",
                    "TRADE_SOURCE",
                    "TRANSFER_SPOT_TO_FUTURE",
                    "TRANSFER_FUTURE_TO_SPOT",
                    "TRANSFER_SPOT_TO_SPOT",
                    "AIRDROP",
                    "DIVIDEND",
                    "TRANSFER_REFUND",
                    "INTERNAL_TRANSFER",
                    "TRANSFER",
                    "SWAP",
                    "COMMISSION_REBATE",
                    "CASH_BACK",
                    "STAKING_WITHDRAW",
                    "STAKING_CLAIM",
                    "STAKING_DELEGATE",
                ],
            )?;
            params.optional_u64_range("limit", 1, 1000)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "transfer_spot_futures" => {
            params.ensure_allowed(
                &["amount", "asset", "clientTranId", "kindType", "market"],
                &[],
            )?;
            params.required_positive_decimal("amount")?;
            params.required("asset")?;
            params.required("clientTranId")?;
            params.required_one_of("kindType", &["FUTURE_SPOT", "SPOT_FUTURE"])?;
            params.optional_one_of("market", &["spot", "futures"])
        }
        "set_futures_position_mode" => {
            params.ensure_allowed(&["dualSidePosition"], &[])?;
            params.required("dualSidePosition")?;
            params.optional_bool("dualSidePosition")
        }
        "set_futures_stp_mode" => {
            params.ensure_allowed(&["stpMode"], &[])?;
            params.required_one_of("stpMode", &["EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"])
        }
        "set_futures_multi_assets_mode" => {
            params.ensure_allowed(&["multiAssetsMargin"], &[])?;
            params.required("multiAssetsMargin")?;
            params.optional_bool("multiAssetsMargin")
        }
        "modify_futures_position_margin" => {
            params.ensure_allowed(
                &["product_symbol", "symbol", "positionSide", "amount", "type"],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            params.optional_one_of("positionSide", &["BOTH", "LONG", "SHORT"])?;
            params.required_positive_decimal("amount")?;
            params.required_one_of("type", &["1", "2"])
        }
        "get_futures_position_margin_history" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "type",
                    "startTime",
                    "endTime",
                    "limit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            params.optional_one_of("type", &["1", "2"])?;
            params.optional_u64_range("limit", 1, u64::MAX)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "get_futures_position_risk"
        | "get_futures_leverage_bracket"
        | "get_futures_adl_quantile"
        | "get_futures_mmp" => {
            params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
            validate_symbol_alias(params, false)
        }
        "get_futures_user_trades" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            validate_trade_history(params)
        }
        "get_futures_income" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "incomeType",
                    "startTime",
                    "endTime",
                    "limit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, false)?;
            params.optional_one_of(
                "incomeType",
                &[
                    "TRANSFER",
                    "WELCOME_BONUS",
                    "REALIZED_PNL",
                    "FUNDING_FEE",
                    "COMMISSION",
                    "INSURANCE_CLEAR",
                    "MARKET_MERCHANT_RETURN_REWARD",
                ],
            )?;
            params.optional_u64_range("limit", 1, 1000)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "get_futures_force_orders" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "autoCloseType",
                    "startTime",
                    "endTime",
                    "limit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, false)?;
            params.optional_one_of("autoCloseType", &["LIQUIDATION", "ADL"])?;
            params.optional_u64_range("limit", 1, 100)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "get_spot_commission_rate" | "get_futures_commission_rate" => {
            params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
            validate_symbol_alias(params, true)
        }
        "update_futures_mmp" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "windowTimeInMilliseconds",
                    "frozenTimeInMilliseconds",
                    "qtyLimit",
                    "valueLimit",
                    "deltaLimit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            params.required_u64_range("windowTimeInMilliseconds", 1, u64::MAX)?;
            params.required_u64_range("frozenTimeInMilliseconds", 1, u64::MAX)?;
            for key in ["qtyLimit", "valueLimit", "deltaLimit"] {
                params.optional_u64_range(key, 1, u64::MAX)?;
            }
            Ok(())
        }
        "delete_futures_mmp" | "reset_futures_mmp" => {
            params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
            validate_symbol_alias(params, true)
        }
        "keep_alive_spot_listen_key" | "close_spot_listen_key" => {
            params.ensure_allowed(&["listenKey"], &[])?;
            params.required("listenKey")?;
            Ok(())
        }
        "place_spot_order" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "side",
                    "type",
                    "timeInForce",
                    "quantity",
                    "quoteOrderQty",
                    "price",
                    "newClientOrderId",
                    "stopPrice",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            validate_spot_order(params)
        }
        "cancel_spot_order"
        | "get_spot_order"
        | "get_spot_open_order"
        | "get_futures_order"
        | "cancel_futures_order"
        | "get_futures_open_order" => {
            params.ensure_allowed(
                &["product_symbol", "symbol", "orderId", "origClientOrderId"],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            ensure_order_lookup(params)?;
            params.u64("orderId")?;
            Ok(())
        }
        "get_spot_open_orders" | "get_futures_open_orders" => {
            params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
            validate_symbol_alias(params, false)
        }
        "cancel_all_spot_open_orders" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "orderIdList",
                    "origClientOrderIdList",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            validate_optional_id_list(params, "orderIdList", false, None)?;
            validate_optional_id_list(params, "origClientOrderIdList", true, None)
        }
        "get_spot_all_orders" | "get_futures_all_orders" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            params.u64("orderId")?;
            params.optional_u64_range("limit", 1, 1000)?;
            params.ensure_max_time_span("startTime", "endTime", 7 * 24 * 60 * 60 * 1000)
        }
        "get_spot_user_trades" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                ],
                &[],
            )?;
            validate_symbol_alias(params, false)?;
            if params.get("orderId").is_some() {
                params.required_any(&["product_symbol", "symbol"])?;
            }
            params.u64("orderId")?;
            validate_trade_history(params)
        }
        "place_futures_order" => {
            let mut allowed = vec!["product_symbol", "symbol", "side"];
            allowed.extend_from_slice(FUTURES_ORDER_KEYS);
            params.ensure_allowed(&allowed, &[])?;
            validate_symbol_alias(params, true)?;
            validate_futures_order(params, false)
        }
        "modify_futures_order" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "origClientOrderId",
                    "quantity",
                    "price",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            ensure_order_lookup(params)?;
            params.u64("orderId")?;
            params.required_positive_decimal("quantity")?;
            params.required_positive_decimal("price")
        }
        "place_futures_chase_order" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "side",
                    "positionSide",
                    "quantityUnit",
                    "quantity",
                    "reduceOnly",
                    "chaseOffset",
                    "chaseOffsetType",
                    "maxChaseOffset",
                    "maxChaseOffsetType",
                    "timeInForce",
                    "clientStrategyId",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            params.required_one_of("side", &["BUY", "SELL"])?;
            params.optional_one_of("positionSide", &["BOTH", "LONG", "SHORT"])?;
            params.required_one_of("quantityUnit", &["BASE", "QUOTE"])?;
            params.required_positive_decimal("quantity")?;
            params.optional_bool("reduceOnly")?;
            params.optional_non_negative_decimal("chaseOffset")?;
            params.optional_one_of("chaseOffsetType", &["ABSOLUTE"])?;
            if params.get("maxChaseOffset").is_some() {
                params.required_positive_decimal("maxChaseOffset")?;
            }
            params.optional_one_of("maxChaseOffsetType", &["ABSOLUTE", "PERCENTAGE"])?;
            params.optional_one_of("timeInForce", &["GTX"])?;
            validate_client_id(params, "clientStrategyId", 28)
        }
        "place_futures_batch_orders" => {
            params.ensure_allowed(&["batchOrders"], &[])?;
            params.required("batchOrders")?;
            Ok(())
        }
        "cancel_all_futures_open_orders" => {
            params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
            validate_symbol_alias(params, true)
        }
        "cancel_futures_batch_orders" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "symbol",
                    "orderIdList",
                    "origClientOrderIdList",
                ],
                &[],
            )?;
            validate_symbol_alias(params, true)?;
            params.ensure_exactly_one(&["orderIdList", "origClientOrderIdList"])?;
            validate_optional_id_list(params, "orderIdList", false, Some(10))?;
            validate_optional_id_list(params, "origClientOrderIdList", true, Some(10))
        }
        "set_futures_countdown_cancel_all" => {
            params.ensure_allowed(&["product_symbol", "symbol", "countdownTime"], &[])?;
            validate_symbol_alias(params, true)?;
            params.required_u64_range("countdownTime", 0, u64::MAX)
        }
        "set_futures_leverage" => {
            params.ensure_allowed(&["product_symbol", "symbol", "leverage"], &[])?;
            validate_symbol_alias(params, true)?;
            params.required_u64_range("leverage", 1, 125)
        }
        "set_futures_margin_type" => {
            params.ensure_allowed(&["product_symbol", "symbol", "marginType"], &[])?;
            validate_symbol_alias(params, true)?;
            params.required_one_of("marginType", &["ISOLATED", "CROSSED"])
        }
        "place_futures_strategy_order" => {
            params.ensure_allowed(
                &[
                    "clientStrategyId",
                    "strategyType",
                    "subOrderList",
                    "builder",
                    "feeRate",
                ],
                &[],
            )?;
            params.required_one_of("strategyType", &["OTO", "OCO", "OTOCO"])?;
            params.required("subOrderList")?;
            validate_client_id(params, "clientStrategyId", 36)?;
            params.optional_decimal("feeRate")?;
            Ok(())
        }
        "update_futures_strategy_order" => {
            params.ensure_allowed(&["strategyId", "strategyType", "subOrderList"], &[])?;
            params.required_u64_range("strategyId", 0, u64::MAX)?;
            params.required_one_of("strategyType", &["OTO", "OCO", "OTOCO"])?;
            params.required("subOrderList")?;
            Ok(())
        }
        "get_futures_strategy_open_order" | "get_futures_strategy_history_order" => {
            let mut allowed = vec!["strategyId", "clientStrategyId", "strategyType"];
            if method_name.ends_with("history_order") {
                allowed.extend_from_slice(&["startTime", "endTime", "limit"]);
            }
            params.ensure_allowed(&allowed, &[])?;
            params.ensure_exactly_one(&["strategyId", "clientStrategyId"])?;
            params.u64("strategyId")?;
            params.required_one_of("strategyType", &["OTO", "OCO", "OTOCO"])?;
            if method_name.ends_with("history_order") {
                params.optional_u64_range("limit", 1, 1000)?;
                params.ensure_max_time_span("startTime", "endTime", 90 * 24 * 60 * 60 * 1000)?;
            }
            Ok(())
        }
        _ => Ok(()),
    }
}

fn validate_symbol_alias(params: &AsterParams, required: bool) -> Result<()> {
    params.ensure_at_most_one(&["product_symbol", "symbol"])?;
    if required {
        params.required_any(&["product_symbol", "symbol"])?;
    }
    Ok(())
}

fn validate_trade_history(params: &AsterParams) -> Result<()> {
    params.u64("fromId")?;
    params.optional_u64_range("limit", 1, 1000)?;
    params.ensure_absent_with("fromId", &["startTime", "endTime"])?;
    params.ensure_max_time_span("startTime", "endTime", 7 * 24 * 60 * 60 * 1000)
}

fn validate_spot_order(params: &AsterParams) -> Result<()> {
    params.required_one_of("side", &["BUY", "SELL"])?;
    let order_type = params.required("type")?;
    params.required_one_of(
        "type",
        &[
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
        ],
    )?;
    params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK", "GTX"])?;
    for key in ["quantity", "quoteOrderQty", "price", "stopPrice"] {
        if params.get(key).is_some() {
            params.required_positive_decimal(key)?;
        }
    }
    validate_client_id(params, "newClientOrderId", 36)?;
    match order_type {
        "LIMIT" => {
            params.required("timeInForce")?;
            params.required("quantity")?;
            params.required("price")?;
        }
        "MARKET" => params.ensure_exactly_one(&["quantity", "quoteOrderQty"])?,
        "STOP" | "TAKE_PROFIT" => {
            params.required("quantity")?;
            params.required("price")?;
            params.required("stopPrice")?;
        }
        "STOP_MARKET" | "TAKE_PROFIT_MARKET" => {
            params.required("quantity")?;
            params.required("stopPrice")?;
        }
        _ => unreachable!("validated spot order type"),
    }
    if order_type != "MARKET" && params.get("quoteOrderQty").is_some() {
        return Err(DcexError::InvalidInput(
            "Aster quoteOrderQty is only supported for MARKET orders".to_string(),
        ));
    }
    Ok(())
}

fn validate_futures_order(params: &AsterParams, batch: bool) -> Result<()> {
    params.required_one_of("side", &["BUY", "SELL"])?;
    params.optional_one_of("positionSide", &["BOTH", "LONG", "SHORT"])?;
    let order_type = params.required("type")?;
    params.required_one_of(
        "type",
        &[
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
            "TRAILING_STOP_MARKET",
        ],
    )?;
    params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK", "GTX", "HIDDEN"])?;
    params.optional_one_of("workingType", &["MARK_PRICE", "CONTRACT_PRICE"])?;
    params.optional_one_of("newOrderRespType", &["ACK", "RESULT"])?;
    params.optional_one_of("pegPriceType", &["COUNTERPARTY_1", "QUEUE_1"])?;
    params.optional_one_of("stpMode", &["EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"])?;
    for key in ["reduceOnly", "closePosition", "priceProtect"] {
        params.optional_bool(key)?;
    }
    for key in ["quantity", "price", "stopPrice", "activationPrice"] {
        if params.get(key).is_some() {
            params.required_positive_decimal(key)?;
        }
    }
    params.optional_decimal("pegOffset")?;
    params.optional_decimal_range("callbackRate", 0.1, if batch { 4.0 } else { 5.0 })?;
    validate_client_id(params, "newClientOrderId", 36)?;

    if batch {
        params.required("quantity")?;
    }
    match order_type {
        "LIMIT" => {
            params.required("timeInForce")?;
            params.required("quantity")?;
            params.required("price")?;
        }
        "MARKET" => {
            params.required("quantity")?;
        }
        "STOP" | "TAKE_PROFIT" => {
            params.required("quantity")?;
            params.required("price")?;
            params.required("stopPrice")?;
        }
        "STOP_MARKET" | "TAKE_PROFIT_MARKET" => {
            params.required("stopPrice")?;
            let closes_position = params
                .get("closePosition")
                .is_some_and(|value| value.eq_ignore_ascii_case("true"));
            if !closes_position {
                params.required("quantity")?;
            }
        }
        "TRAILING_STOP_MARKET" => {
            params.required("callbackRate")?;
        }
        _ => unreachable!("validated futures order type"),
    }
    if params
        .get("closePosition")
        .is_some_and(|value| value.eq_ignore_ascii_case("true"))
    {
        params.ensure_absent_with("closePosition", &["quantity", "reduceOnly"])?;
        if !matches!(order_type, "STOP_MARKET" | "TAKE_PROFIT_MARKET") {
            return Err(DcexError::InvalidInput(
                "Aster closePosition is only supported for STOP_MARKET or TAKE_PROFIT_MARKET"
                    .to_string(),
            ));
        }
    }
    Ok(())
}

fn validate_strategy_sub_order(
    params: &AsterParams,
    update: bool,
    expected_index: usize,
) -> Result<()> {
    params.required_u64_range("strategySubId", 1, u64::MAX)?;
    if !update
        && params.u64("strategySubId")? != Some(u64::try_from(expected_index).unwrap_or(u64::MAX))
    {
        return Err(DcexError::InvalidInput(
            "Aster strategySubId values must start at 1 and match their array positions"
                .to_string(),
        ));
    }
    params.required_one_of("securityType", &["USDT_FUTURES", "COIN_FUTURES", "OPTIONS"])?;
    params.required_one_of("side", &["BUY", "SELL"])?;
    params.optional_one_of("positionSide", &["BOTH", "LONG", "SHORT"])?;
    params.required_one_of(
        "type",
        &[
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
            "TRAILING_STOP_MARKET",
        ],
    )?;
    params.optional_one_of("timeInForce", &["GTC", "GTX", "HIDDEN"])?;
    params.optional_one_of("workingType", &["CONTRACT_PRICE", "MARK_PRICE"])?;
    for key in ["reduceOnly", "closePosition", "priceProtect"] {
        params.optional_bool(key)?;
    }
    for key in [
        "quantity",
        "price",
        "stopPrice",
        "activationPrice",
        "callbackRate",
    ] {
        params.optional_decimal(key)?;
    }
    params.optional_one_of(
        "firstDrivenOn",
        &[
            "NEW",
            "PARTIALLY_FILLED_OR_FILLED",
            "FILLED",
            "CANCELED",
            "REPLACED",
            "STOPPED",
            "REJECTED",
            "EXPIRED",
        ],
    )?;
    params.optional_one_of(
        "secondDrivenOn",
        &[
            "NEW",
            "PARTIALLY_FILLED_OR_FILLED",
            "FILLED",
            "CANCELED",
            "REPLACED",
            "STOPPED",
            "REJECTED",
            "EXPIRED",
        ],
    )?;
    params.optional_one_of("firstTrigger", &["PLACE_ORDER", "CANCEL_ORDER"])?;
    params.optional_one_of("secondTrigger", &["PLACE_ORDER", "CANCEL_ORDER"])?;
    params.u64("firstDrivenId")?;
    params.u64("secondDrivenId")?;
    if update {
        return Ok(());
    }
    let order_type = params.required("type")?;
    let closes_position = params
        .get("closePosition")
        .is_some_and(|value| value.eq_ignore_ascii_case("true"));
    if !closes_position {
        params.required("quantity")?;
    }
    if matches!(order_type, "LIMIT" | "STOP" | "TAKE_PROFIT") {
        params.required("price")?;
    }
    if matches!(
        order_type,
        "STOP" | "STOP_MARKET" | "TAKE_PROFIT" | "TAKE_PROFIT_MARKET"
    ) {
        params.required("stopPrice")?;
    }
    if order_type == "LIMIT" {
        params.required("timeInForce")?;
    }
    Ok(())
}

fn validate_client_id(params: &AsterParams, key: &str, max_length: usize) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if value.len() > max_length
        || !value.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | ':' | '/' | '_' | '-')
        })
    {
        return Err(DcexError::InvalidInput(format!(
            "invalid Aster {key}; expected 1-{max_length} characters matching [A-Za-z0-9._:/-]"
        )));
    }
    Ok(())
}

fn validate_optional_id_list(
    params: &AsterParams,
    key: &str,
    strings: bool,
    maximum: Option<usize>,
) -> Result<()> {
    let Some(raw) = params.get(key) else {
        return Ok(());
    };
    let value: Value = serde_json::from_str(raw).map_err(|error| {
        DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
    })?;
    let Value::Array(items) = value else {
        return Err(DcexError::InvalidInput(format!(
            "Aster {key} must be a JSON array"
        )));
    };
    if items.is_empty() || maximum.is_some_and(|maximum| items.len() > maximum) {
        return Err(DcexError::InvalidInput(format!(
            "Aster {key} must contain between 1 and {} values",
            maximum.unwrap_or(usize::MAX)
        )));
    }
    let valid = if strings {
        items
            .iter()
            .all(|item| item.as_str().is_some_and(|value| !value.trim().is_empty()))
    } else {
        items.iter().all(|item| item.as_u64().is_some())
    };
    if !valid {
        return Err(DcexError::InvalidInput(format!(
            "Aster {key} contains an invalid value"
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_bbo_peg_fields() {
        let params = AsterParams::from_pairs(vec![
            ("pegPriceType".to_string(), "QUEUE_1".to_string()),
            ("pegOffset".to_string(), "-0.5".to_string()),
        ]);
        let query = params.only(FUTURES_ORDER_KEYS);
        assert!(query.contains(&("pegPriceType".to_string(), "QUEUE_1".to_string())));
        assert!(query.contains(&("pegOffset".to_string(), "-0.5".to_string())));
    }

    #[test]
    fn validates_current_chase_order_fields() {
        let valid = AsterParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("side".to_string(), "BUY".to_string()),
            ("quantityUnit".to_string(), "BASE".to_string()),
            ("quantity".to_string(), "0.001".to_string()),
        ]);
        validate_private_params("place_futures_chase_order", &valid).expect("valid chase order");

        let invalid = AsterParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("side".to_string(), "BUY".to_string()),
            ("quantityUnit".to_string(), "BASE".to_string()),
            ("quantity".to_string(), "0.001".to_string()),
            ("priceLimit".to_string(), "100".to_string()),
        ]);
        assert!(validate_private_params("place_futures_chase_order", &invalid).is_err());
    }

    #[test]
    fn current_mmp_query_accepts_an_omitted_symbol() {
        let params = AsterParams::from_pairs(Vec::new());
        validate_private_params("get_futures_mmp", &params).expect("optional symbol");
    }

    #[test]
    fn strategy_lookup_requires_exactly_one_identifier() {
        let both = AsterParams::from_pairs(vec![
            ("strategyId".to_string(), "1".to_string()),
            ("clientStrategyId".to_string(), "client-1".to_string()),
            ("strategyType".to_string(), "OTO".to_string()),
        ]);
        assert!(validate_private_params("get_futures_strategy_open_order", &both).is_err());
    }
}
