use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::GateioClient;
use super::endpoints::*;
use super::params::{
    bool_value, insert_optional_string, insert_truthy_bool, json_value_string, normalize_side,
    signed_size, GateioParams,
};

const CONTRACT_ORDER_STRING_KEYS: &[&str] = &["price", "tif", "text", "auto_size", "stp_act"];
const CONTRACT_ORDER_INTEGER_KEYS: &[&str] = &["size", "iceberg"];
const CONTRACT_ORDER_BOOL_KEYS: &[&str] = &["close", "reduce_only"];
const SPOT_ORDER_STRING_KEYS: &[&str] = &[
    "amount",
    "text",
    "account",
    "price",
    "time_in_force",
    "iceberg",
    "stp_act",
    "action_mode",
];

impl GateioClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &GateioParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_futures_all_positions" => {
                let path = fill_settle(FUTURES_POSITIONS, params.settle());
                let query = params.only_renamed(&[
                    ("holding", "holding"),
                    ("limit", "limit"),
                    ("offset", "offset"),
                ]);
                self.private_get(&path, normalize_bool_query(query)).await
            }
            "get_contract_single_positions" => {
                let contract = self.required_contract(params)?;
                let path = match params.market_path()? {
                    "futures" => fill_contract(FUTURES_POSITION, params.settle(), &contract),
                    "delivery" => fill_contract(DELIVERY_POSITION, params.settle(), &contract),
                    _ => unreachable!(),
                };
                self.private_get(&path, Vec::new()).await
            }
            "update_futures_positions_leverage" => {
                let contract = self.required_contract(params)?;
                let path = fill_contract(FUTURES_POSITION_LEVERAGE, params.settle(), &contract);
                let mut query = vec![(
                    "leverage".to_string(),
                    params.required("leverage")?.to_string(),
                )];
                if let Some(value) = params.get("cross_leverage_limit") {
                    query.push(("cross_leverage_limit".to_string(), value.to_string()));
                }
                self.private_post_query(&path, query).await
            }
            "future_dual_mode_switch" => {
                let path = fill_settle(FUTURES_DUAL_MODE, params.settle());
                let dual_mode = params.required("dual_mode")?;
                self.private_post_query(
                    &path,
                    vec![("dual_mode".to_string(), bool_query_value(dual_mode))],
                )
                .await
            }
            "place_contract_order" => self.contract_order_from_params(params, None, None).await,
            "place_contract_market_order" => {
                self.contract_order_from_params(params, None, Some(("price", "0", "tif", "ioc")))
                    .await
            }
            "place_contract_market_buy_order" => {
                self.contract_order_from_params(
                    params,
                    Some(true),
                    Some(("price", "0", "tif", "ioc")),
                )
                .await
            }
            "place_contract_market_sell_order" => {
                self.contract_order_from_params(
                    params,
                    Some(false),
                    Some(("price", "0", "tif", "ioc")),
                )
                .await
            }
            "place_contract_limit_order" => {
                self.contract_order_from_params(params, None, Some(("tif", "gtc", "", "")))
                    .await
            }
            "place_contract_limit_buy_order" => {
                self.contract_order_from_params(params, Some(true), Some(("tif", "gtc", "", "")))
                    .await
            }
            "place_contract_limit_sell_order" => {
                self.contract_order_from_params(params, Some(false), Some(("tif", "gtc", "", "")))
                    .await
            }
            "place_contract_post_only_limit_order" => {
                self.contract_order_from_params(params, None, Some(("tif", "poc", "", "")))
                    .await
            }
            "place_contract_post_only_limit_buy_order" => {
                self.contract_order_from_params(params, Some(true), Some(("tif", "poc", "", "")))
                    .await
            }
            "place_contract_post_only_limit_sell_order" => {
                self.contract_order_from_params(params, Some(false), Some(("tif", "poc", "", "")))
                    .await
            }
            "place_futures_batch_order" => self.place_futures_batch_order_from_params(params).await,
            "get_contract_order_list" => {
                let market = params.market_path()?;
                let path = match market {
                    "futures" => fill_settle(FUTURES_ORDERS, params.settle()),
                    "delivery" => fill_settle(DELIVERY_ORDERS, params.settle()),
                    _ => unreachable!(),
                };
                let mut query = params.only_renamed(&[
                    ("status", "status"),
                    ("limit", "limit"),
                    ("offset", "offset"),
                    ("last_id", "last_id"),
                ]);
                self.push_optional_contract(&mut query, params)?;
                if market == "delivery" {
                    if let Some(value) = params.get("count_total") {
                        query.push(("count_total".to_string(), value.to_string()));
                    }
                }
                self.private_get(&path, query).await
            }
            "cancel_contract_all_order_matched" => {
                let market = params.market_path()?;
                let path = match market {
                    "futures" => fill_settle(FUTURES_ORDERS, params.settle()),
                    "delivery" => fill_settle(DELIVERY_ORDERS, params.settle()),
                    _ => unreachable!(),
                };
                let mut query = Vec::new();
                self.push_required_contract(&mut query, params)?;
                if let Some(side) = params.get("side") {
                    query.push(("side".to_string(), normalize_side(side)?));
                }
                self.private_delete(&path, query).await
            }
            "get_contract_single_order" => {
                let path = self.contract_order_path(params)?;
                self.private_get(&path, Vec::new()).await
            }
            "cancel_contract_single_order" => {
                let path = self.contract_order_path(params)?;
                self.private_delete(&path, Vec::new()).await
            }
            "amend_futures_single_order" => {
                let path = fill_order(FUTURES_ORDER, params.settle(), params.required("order_id")?);
                let body = Value::Object(params.body(
                    &["price", "amend_text", "biz_info", "bbo"],
                    &["size"],
                    &[],
                ));
                self.private_put_json(&path, body).await
            }
            "get_trading_history" => {
                let market = params.market_path()?;
                let path = match market {
                    "futures" => fill_settle(FUTURES_MY_TRADES, params.settle()),
                    "delivery" => fill_settle(DELIVERY_MY_TRADES, params.settle()),
                    _ => unreachable!(),
                };
                let mut query = params.only_renamed(&[
                    ("order", "order"),
                    ("limit", "limit"),
                    ("offset", "offset"),
                    ("late_id", "late_id"),
                ]);
                self.push_required_contract(&mut query, params)?;
                if market == "delivery" {
                    if let Some(value) = params.get("count_total") {
                        query.push(("count_total".to_string(), value.to_string()));
                    }
                }
                self.private_get(&path, query).await
            }
            "get_futures_position_close_history" => {
                let path = fill_settle(FUTURES_POSITION_CLOSE, params.settle());
                let mut query = params.only_renamed(&[
                    ("limit", "limit"),
                    ("offset", "offset"),
                    ("from_timestamp", "from"),
                    ("from", "from"),
                    ("to_timestamp", "to"),
                    ("to", "to"),
                    ("pnl", "pnl"),
                ]);
                self.push_required_contract(&mut query, params)?;
                if let Some(side) = params.get("side") {
                    query.push(("side".to_string(), normalize_side(side)?));
                }
                self.private_get(&path, query).await
            }
            "get_futures_auto_deleveraging_history" => {
                let path = fill_settle(FUTURES_AUTO_DELEVERAGES, params.settle());
                let mut query = params.only_renamed(&[
                    ("limit", "limit"),
                    ("at_timestamp", "at"),
                    ("at", "at"),
                ]);
                self.push_required_contract(&mut query, params)?;
                self.private_get(&path, query).await
            }
            "get_delivery_all_positions" => {
                let path = fill_settle(DELIVERY_POSITIONS, params.settle());
                self.private_get(&path, Vec::new()).await
            }
            "update_delivery_positions_leverage" => {
                let contract = self.required_contract(params)?;
                let path = fill_contract(DELIVERY_POSITION_LEVERAGE, params.settle(), &contract);
                self.private_post_query(
                    &path,
                    vec![(
                        "leverage".to_string(),
                        params.required("leverage")?.to_string(),
                    )],
                )
                .await
            }
            "get_delivery_position_close_history" => {
                let path = fill_settle(DELIVERY_POSITION_CLOSE, params.settle());
                let mut query = params.only(&["limit"]);
                self.push_required_contract(&mut query, params)?;
                self.private_get(&path, query).await
            }
            "place_spot_order" => self.spot_order_from_params(params, None, None, None).await,
            "place_spot_market_order" => {
                self.spot_order_from_params(params, None, Some("market"), Some("ioc"))
                    .await
            }
            "place_spot_market_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("market"), Some("ioc"))
                    .await
            }
            "place_spot_market_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("market"), Some("ioc"))
                    .await
            }
            "place_spot_limit_order" => {
                self.spot_order_from_params(params, None, Some("limit"), None)
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("limit"), None)
                    .await
            }
            "place_spot_limit_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("limit"), None)
                    .await
            }
            "place_spot_post_only_limit_order" => {
                self.spot_order_from_params(params, None, Some("limit"), Some("poc"))
                    .await
            }
            "place_spot_post_only_limit_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("limit"), Some("poc"))
                    .await
            }
            "place_spot_post_only_limit_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("limit"), Some("poc"))
                    .await
            }
            "get_spot_open_orders" => {
                self.private_get(SPOT_OPEN_ORDERS, params.only(&["page", "limit", "account"]))
                    .await
            }
            "get_spot_order_list" => {
                let mut query = params.only_renamed(&[
                    ("status", "status"),
                    ("page", "page"),
                    ("limit", "limit"),
                    ("account", "account"),
                    ("from_timestamp", "from"),
                    ("from", "from"),
                    ("to_timestamp", "to"),
                    ("to", "to"),
                ]);
                self.push_required_currency_pair(&mut query, params)?;
                if let Some(side) = params.get("side") {
                    query.push(("side".to_string(), normalize_side(side)?));
                }
                self.private_get(SPOT_ORDERS, query).await
            }
            "cancel_spot_order" => {
                let mut query = params.only(&["account", "action_mode"]);
                self.push_optional_currency_pair(&mut query, params)?;
                if let Some(side) = params.get("side") {
                    query.push(("side".to_string(), normalize_side(side)?));
                }
                self.private_delete(SPOT_ORDERS, query).await
            }
            "get_spot_single_order" => {
                let path = fill_spot_order(params.required("order_id")?);
                let mut query = params.only(&["account"]);
                self.push_required_currency_pair(&mut query, params)?;
                self.private_get(&path, query).await
            }
            "cancel_spot_single_order" => {
                let path = fill_spot_order(params.required("order_id")?);
                let mut query = params.only(&["account", "action_mode"]);
                self.push_required_currency_pair(&mut query, params)?;
                self.private_delete(&path, query).await
            }
            "amend_spot_single_order" => {
                let path = fill_spot_order(params.required("order_id")?);
                let mut body = params.body(
                    &["account", "amount", "price", "amend_text", "action_mode"],
                    &[],
                    &[],
                );
                self.insert_optional_currency_pair(&mut body, params)?;
                self.private_patch_json(&path, Value::Object(body)).await
            }
            "get_spot_trading_history" => {
                let mut query = params.only_renamed(&[
                    ("limit", "limit"),
                    ("page", "page"),
                    ("order_id", "order_id"),
                    ("account", "account"),
                    ("from_timestamp", "from"),
                    ("from", "from"),
                    ("to_timestamp", "to"),
                    ("to", "to"),
                ]);
                self.push_optional_currency_pair(&mut query, params)?;
                self.private_get(SPOT_MY_TRADES, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn contract_order_from_params(
        &self,
        params: &GateioParams,
        positive_size: Option<bool>,
        defaults: Option<(&str, &str, &str, &str)>,
    ) -> Result<ValidatedResponse> {
        let market = params.market_path()?;
        let path = match market {
            "futures" => fill_settle(FUTURES_ORDERS, params.settle()),
            "delivery" => fill_settle(DELIVERY_ORDERS, params.settle()),
            _ => unreachable!(),
        };
        let mut body = params.body(
            CONTRACT_ORDER_STRING_KEYS,
            CONTRACT_ORDER_INTEGER_KEYS,
            CONTRACT_ORDER_BOOL_KEYS,
        );
        self.insert_required_contract(&mut body, params)?;
        if let Some(positive_size) = positive_size {
            body.insert(
                "size".to_string(),
                serde_json::Value::Number(
                    signed_size(params.required("size")?, positive_size)?.into(),
                ),
            );
        }
        if let Some((first_key, first_value, second_key, second_value)) = defaults {
            if !first_key.is_empty() {
                body.insert(
                    first_key.to_string(),
                    Value::String(first_value.to_string()),
                );
            }
            if !second_key.is_empty() {
                body.insert(
                    second_key.to_string(),
                    Value::String(second_value.to_string()),
                );
            }
        }
        self.private_post_json(&path, Value::Object(body)).await
    }

    async fn place_futures_batch_order_from_params(
        &self,
        params: &GateioParams,
    ) -> Result<ValidatedResponse> {
        let mut orders = params.json_required("orders")?;
        let Value::Array(orders_array) = &mut orders else {
            return Err(DcexError::InvalidInput(
                "orders must be a JSON array.".to_string(),
            ));
        };
        for order in orders_array {
            if let Value::Object(order) = order {
                if let Some(product_symbol) = order.remove("product_symbol") {
                    let symbol = self.exchange_symbol(&json_value_string(&product_symbol))?;
                    order.insert("contract".to_string(), Value::String(symbol));
                } else if let Some(contract) = order.get_mut("contract") {
                    let symbol = self.exchange_symbol(&json_value_string(contract))?;
                    *contract = Value::String(symbol);
                }
            }
        }
        let path = fill_settle(FUTURES_BATCH_ORDERS, params.settle());
        self.private_post_json(&path, orders).await
    }

    async fn spot_order_from_params(
        &self,
        params: &GateioParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
        tif_override: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(SPOT_ORDER_STRING_KEYS, &[], &[]);
        self.insert_required_currency_pair(&mut body, params)?;
        let side = match side_override {
            Some(side) => side.to_string(),
            None => normalize_side(params.required("side")?)?,
        };
        body.insert("side".to_string(), Value::String(side));
        let order_type = type_override
            .or_else(|| params.get("order_type"))
            .or_else(|| params.get("type"));
        insert_optional_string(&mut body, "type", order_type);
        let tif = tif_override.or_else(|| params.get("time_in_force"));
        insert_optional_string(&mut body, "time_in_force", tif);
        insert_truthy_bool(&mut body, "auto_borrow", params.get("auto_borrow"));
        insert_truthy_bool(&mut body, "auto_repay", params.get("auto_repay"));
        self.private_post_json(SPOT_ORDERS, Value::Object(body))
            .await
    }

    fn contract_order_path(&self, params: &GateioParams) -> Result<String> {
        let order_id = params.required("order_id")?;
        match params.market_path()? {
            "futures" => Ok(fill_order(FUTURES_ORDER, params.settle(), order_id)),
            "delivery" => Ok(fill_order(DELIVERY_ORDER, params.settle(), order_id)),
            _ => unreachable!(),
        }
    }

    pub(super) fn push_optional_contract(
        &self,
        query: &mut Vec<(String, String)>,
        params: &GateioParams,
    ) -> Result<()> {
        if let Some(contract) = params.get("contract") {
            query.push(("contract".to_string(), self.exchange_symbol(contract)?));
        } else if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                "contract".to_string(),
                self.exchange_symbol(product_symbol)?,
            ));
        }
        Ok(())
    }

    fn push_required_contract(
        &self,
        query: &mut Vec<(String, String)>,
        params: &GateioParams,
    ) -> Result<()> {
        query.push(("contract".to_string(), self.required_contract(params)?));
        Ok(())
    }

    fn required_contract(&self, params: &GateioParams) -> Result<String> {
        let symbol = params.required_any(&["contract", "product_symbol"])?;
        self.exchange_symbol(symbol)
    }

    pub(super) fn push_optional_currency_pair(
        &self,
        query: &mut Vec<(String, String)>,
        params: &GateioParams,
    ) -> Result<()> {
        if let Some(currency_pair) = params.get("currency_pair") {
            query.push((
                "currency_pair".to_string(),
                self.exchange_symbol(currency_pair)?,
            ));
        } else if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                "currency_pair".to_string(),
                self.exchange_symbol(product_symbol)?,
            ));
        }
        Ok(())
    }

    fn push_required_currency_pair(
        &self,
        query: &mut Vec<(String, String)>,
        params: &GateioParams,
    ) -> Result<()> {
        query.push((
            "currency_pair".to_string(),
            self.required_currency_pair(params)?,
        ));
        Ok(())
    }

    fn insert_required_contract(
        &self,
        body: &mut Map<String, Value>,
        params: &GateioParams,
    ) -> Result<()> {
        body.insert(
            "contract".to_string(),
            Value::String(self.required_contract(params)?),
        );
        Ok(())
    }

    fn insert_required_currency_pair(
        &self,
        body: &mut Map<String, Value>,
        params: &GateioParams,
    ) -> Result<()> {
        body.insert(
            "currency_pair".to_string(),
            Value::String(self.required_currency_pair(params)?),
        );
        Ok(())
    }

    fn insert_optional_currency_pair(
        &self,
        body: &mut Map<String, Value>,
        params: &GateioParams,
    ) -> Result<()> {
        if let Some(currency_pair) = params.get("currency_pair") {
            body.insert(
                "currency_pair".to_string(),
                Value::String(self.exchange_symbol(currency_pair)?),
            );
        } else if let Some(product_symbol) = params.get("product_symbol") {
            body.insert(
                "currency_pair".to_string(),
                Value::String(self.exchange_symbol(product_symbol)?),
            );
        }
        Ok(())
    }

    fn required_currency_pair(&self, params: &GateioParams) -> Result<String> {
        let symbol = params.required_any(&["currency_pair", "product_symbol"])?;
        self.exchange_symbol(symbol)
    }

    pub(super) fn currency_pairs_from_products(&self, value: &str) -> Result<String> {
        if let Ok(Value::Array(values)) = serde_json::from_str::<Value>(value) {
            return values
                .iter()
                .map(json_value_string)
                .map(|symbol| self.exchange_symbol(&symbol))
                .collect::<Result<Vec<_>>>()
                .map(|values| values.join(","));
        }
        value
            .split(',')
            .map(str::trim)
            .filter(|value| !value.is_empty())
            .map(|symbol| self.exchange_symbol(symbol))
            .collect::<Result<Vec<_>>>()
            .map(|values| values.join(","))
    }
}

fn bool_query_value(value: &str) -> String {
    bool_value(value)
        .map(|value| value.to_string())
        .unwrap_or_else(|| value.to_string())
}

fn normalize_bool_query(params: Vec<(String, String)>) -> Vec<(String, String)> {
    params
        .into_iter()
        .map(|(key, value)| {
            if matches!(key.as_str(), "holding" | "dual_mode") {
                (key, bool_query_value(&value))
            } else {
                (key, value)
            }
        })
        .collect()
}
