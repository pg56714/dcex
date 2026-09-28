//! Schema-driven request validation, encoding and dispatch.
use super::{client::BingxClient, params::*};
use crate::{
    DcexError, Result,
    exchange::{ValidatedResponse, unix_timestamp_ms},
};
use serde_json::Value;

#[path = "generated/schema_tables.rs"]
mod endpoints;

pub(super) struct Endpoint {
    pub path: &'static str,
    pub verb: &'static str,
    pub public: bool,
    pub fields: &'static [&'static str],
    pub required: &'static [&'static str],
    pub integers: &'static [&'static str],
}

impl BingxClient {
    pub(super) async fn table_request(
        &self,
        name: &str,
        params: &BingxParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(e) = endpoints::endpoint(name) else {
            return Ok(None);
        };
        if e.public != public {
            return Ok(None);
        }
        params.ensure_allowed(e.fields)?;
        let supplied = params.only(e.fields);
        crate::exchanges::schema::validate_pairs(&supplied)?;
        if supplied
            .iter()
            .map(|(k, _)| k)
            .collect::<std::collections::BTreeSet<_>>()
            .len()
            != supplied.len()
        {
            return Err(invalid("duplicate parameter"));
        }
        for key in e.required {
            params.required(key)?;
        }
        for key in e.fields {
            if params.get(key).is_some() {
                params.required(key)?;
            }
        }
        for key in e.integers {
            validate_u64_range(params, key, 0, u64::MAX)?;
        }
        validate_u64_range(params, "recvWindow", 1, 5000)?;
        validate_time_range(params, "startTime", "endTime", None)?;
        validate_u64_range(params, "pageIndex", 1, u64::MAX)?;
        validate_u64_range(params, "pageSize", 1, 1000)?;
        let limit = if name == "get_coin_swap_kline" {
            1440
        } else if name == "get_spot_historical_kline" {
            500
        } else if name == "get_coin_swap_force_orders" {
            100
        } else {
            1000
        };
        validate_u64_range(params, "limit", 1, limit)?;
        if name == "get_swap_historical_trades" {
            validate_u64_range(params, "limit", 1, 100)?;
        }
        if name == "get_spot_historical_trades" {
            validate_u64_range(params, "limit", 1, 500)?;
        }
        if name == "reverse_swap_position" {
            validate_enum(params, "type_", &["Reverse", "TriggerReverse"])?;
            if params.get("type_") == Some("TriggerReverse") {
                params.required("triggerPrice")?;
                params.required("workingType")?;
            }
        }
        validate_enum(params, "adjustType", &["0", "1"])?;
        validate_enum(params, "transferable", &["true", "false"])?;
        validate_enum(params, "freeze", &["true", "false"])?;
        if name == "create_sub_account_deposit_address" {
            validate_enum(params, "walletType", &["1", "2", "3", "15"])?;
        }
        if name == "get_sub_account_deposit_history" {
            validate_enum(params, "status", &["0", "1", "6"])?;
        }
        if name == "create_sub_account" {
            let value = params.required("subAccountString")?;
            if value.len() <= 6
                || !value.as_bytes()[0].is_ascii_alphabetic()
                || !value.bytes().any(|b| b.is_ascii_digit())
            {
                return Err(invalid(
                    "subAccountString must start with a letter, contain a digit, and exceed six characters",
                ));
            }
        }
        if name == "get_coin_swap_orderbook" {
            validate_enum(
                params,
                "limit",
                &["5", "10", "20", "50", "100", "500", "1000"],
            )?;
        }
        validate_enum(
            params,
            "interval",
            &[
                "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d",
                "1w", "1M",
            ],
        )?;
        validate_enum(
            params,
            "side",
            if name == "set_coin_swap_leverage" {
                &["LONG", "SHORT", "BOTH"]
            } else {
                &["BUY", "SELL"]
            },
        )?;
        validate_enum(params, "positionSide", &["LONG", "SHORT", "BOTH"])?;
        validate_enum(params, "marginType", &["ISOLATED", "CROSSED"])?;
        validate_enum(params, "autoCloseType", &["LIQUIDATION", "ADL"])?;
        validate_enum(params, "workingType", &["MARK_PRICE", "CONTRACT_PRICE"])?;
        validate_enum(params, "timeInForce", &["GTC", "IOC", "FOK", "PostOnly"])?;
        if name == "get_deposit_history" {
            validate_enum(params, "status", &["0", "1", "2", "6"])?;
        }
        for key in [
            "quantity",
            "price",
            "stopPrice",
            "limitPrice",
            "triggerPrice",
            "orderPrice",
            "amount",
        ] {
            validate_positive_number(params, key)?;
        }
        validate_u64_range(params, "leverage", 1, u64::MAX)?;
        validate_client_id(params, "clientOrderId", false)?;
        if [
            "get_coin_swap_order",
            "cancel_coin_swap_order",
            "cancel_spot_oco",
        ]
        .contains(&name)
        {
            require_one_identifier(params, &["orderId", "clientOrderId"])?;
        }
        if name == "get_spot_oco" {
            require_one_identifier(params, &["orderListId", "clientOrderId"])?;
        }
        if name == "adjust_coin_swap_position_margin" {
            validate_enum(params, "type_", &["1", "2"])?;
            validate_enum(params, "positionSide", &["LONG", "SHORT"])?;
        }
        if name == "place_coin_swap_order" {
            let kind = params.required("type_")?;
            validate_enum(
                params,
                "type_",
                &[
                    "MARKET",
                    "LIMIT",
                    "STOP_MARKET",
                    "STOP",
                    "TAKE_PROFIT_MARKET",
                    "TAKE_PROFIT",
                ],
            )?;
            params.required("quantity")?;
            if ["LIMIT", "STOP", "TAKE_PROFIT"].contains(&kind) {
                params.required("price")?;
            }
            if !["LIMIT", "MARKET"].contains(&kind) {
                params.required("stopPrice")?;
            }
            for key in ["takeProfit", "stopLoss"] {
                if let Some(text) = params.get(key) {
                    if !["LIMIT", "MARKET"].contains(&kind) {
                        return Err(invalid("attached TP/SL requires LIMIT or MARKET"));
                    }
                    let obj: Value =
                        serde_json::from_str(text).map_err(|_| invalid("invalid TP/SL JSON"))?;
                    let obj = obj
                        .as_object()
                        .ok_or_else(|| invalid("TP/SL must be an object"))?;
                    if obj.keys().any(|k| {
                        !["type", "stopPrice", "price", "workingType"].contains(&k.as_str())
                    }) {
                        return Err(invalid("unsupported TP/SL field"));
                    }
                    let kind = obj
                        .get("type")
                        .and_then(Value::as_str)
                        .ok_or_else(|| invalid("TP/SL type is required"))?;
                    let types = if key == "takeProfit" {
                        &["TAKE_PROFIT", "TAKE_PROFIT_MARKET"]
                    } else {
                        &["STOP", "STOP_MARKET"]
                    };
                    if !types.contains(&kind) {
                        return Err(invalid("invalid TP/SL type"));
                    }
                    for k in ["stopPrice", "price"] {
                        if (k == "stopPrice"
                            || ["STOP", "TAKE_PROFIT"].contains(&kind)
                            || obj.contains_key(k))
                            && !obj
                                .get(k)
                                .and_then(Value::as_f64)
                                .is_some_and(|v| v.is_finite() && v > 0.0)
                        {
                            return Err(invalid("TP/SL prices must be positive JSON numbers"));
                        }
                    }
                    if obj.get("workingType").is_some_and(|v| {
                        !matches!(v.as_str(), Some("MARK_PRICE" | "CONTRACT_PRICE"))
                    }) {
                        return Err(invalid("invalid TP/SL workingType"));
                    }
                }
            }
        }
        if name == "place_spot_oco" {
            if params
                .get("listClientOrderId")
                .is_some_and(|v| !v.bytes().all(|b| b.is_ascii_digit()))
            {
                return Err(invalid("listClientOrderId requires decimal digits"));
            }
            let limit = params
                .required("limitPrice")?
                .parse::<f64>()
                .map_err(|_| invalid("invalid limitPrice"))?;
            let trigger = params
                .required("triggerPrice")?
                .parse::<f64>()
                .map_err(|_| invalid("invalid triggerPrice"))?;
            if (params.get("side") == Some("SELL") && limit <= trigger)
                || (params.get("side") == Some("BUY") && limit >= trigger)
            {
                return Err(invalid("OCO limit and trigger prices are reversed"));
            }
        }
        let mut query = params.only(e.fields);
        query.retain(|(k, _)| k != "product_symbol");
        if let Some(product) = params.get("product_symbol") {
            let symbol = self.exchange_symbol(product)?;
            if e.path.contains("/cswap/") && !symbol.ends_with("-USD") {
                return Err(invalid("Coin-M requires a BASE-USD symbol"));
            }
            query.push(("symbol".into(), symbol));
        }
        if matches!(
            name,
            "create_sub_account"
                | "set_sub_account_frozen"
                | "create_sub_account_api_key"
                | "modify_sub_account_api_key"
                | "delete_sub_account_api_key"
        ) {
            let mut body = serde_json::Map::new();
            for (key, value) in query {
                let parsed = if e.integers.contains(&key.as_str()) {
                    Value::from(
                        value
                            .parse::<u64>()
                            .map_err(|_| invalid("invalid JSON integer"))?,
                    )
                } else if key == "freeze" {
                    Value::Bool(
                        value
                            .parse::<bool>()
                            .map_err(|_| invalid("invalid freeze flag"))?,
                    )
                } else if key == "permissions" {
                    let values: Vec<u64> = serde_json::from_str(&value)
                        .map_err(|_| invalid("permissions must be an integer array"))?;
                    if values.is_empty()
                        || values.iter().any(|v| !matches!(v, 1 | 2 | 3 | 4 | 5 | 7))
                    {
                        return Err(invalid("unsupported API permission code"));
                    }
                    serde_json::to_value(values).map_err(|_| invalid("invalid permission array"))?
                } else if key == "ipAddresses" {
                    let values: Vec<String> = serde_json::from_str(&value)
                        .map_err(|_| invalid("ipAddresses must be a string array"))?;
                    if values
                        .iter()
                        .any(|v| v.parse::<std::net::IpAddr>().is_err())
                    {
                        return Err(invalid("invalid IP address"));
                    }
                    serde_json::to_value(values).map_err(|_| invalid("invalid IP array"))?
                } else {
                    Value::String(value)
                };
                body.insert(key, parsed);
            }
            return Ok(Some(
                self.request(
                    crate::http::HttpMethod::Post,
                    e.path,
                    vec![],
                    true,
                    vec![],
                    Some(Value::Object(body)),
                )
                .await?,
            ));
        }
        Ok(Some(if public {
            if name != "get_swap_server_time" {
                query.push(("timestamp".into(), unix_timestamp_ms()?.to_string()));
            }
            self.public_get(e.path, query).await?
        } else {
            match e.verb {
                "POST" => self.private_post(e.path, query).await?,
                "DELETE" => self.private_delete(e.path, query).await?,
                _ => self.private_get(e.path, query).await?,
            }
        }))
    }
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("BingX: {message}"))
}

mod request_tables;
