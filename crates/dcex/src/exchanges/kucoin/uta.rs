pub(in crate::exchanges::kucoin) use serde_json::Value;

pub(in crate::exchanges::kucoin) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::kucoin) use crate::{DcexError, Result};

pub(in crate::exchanges::kucoin) use super::client::{KucoinClient, KucoinMarket};
pub(in crate::exchanges::kucoin) use super::endpoints::*;
pub(in crate::exchanges::kucoin) use super::params::{
    KucoinParams, generate_client_oid, require_exactly_one, validate_enum, validate_positive_number,
};

pub(in crate::exchanges::kucoin) const UTA_ORDER_FIELDS: &[&str] = &[
    "tradeType",
    "side",
    "orderType",
    "size",
    "sizeUnit",
    "price",
    "clientOid",
    "timeInForce",
    "marginMode",
    "positionSide",
    "leverage",
    "tags",
    "triggerDirection",
    "triggerPriceType",
    "triggerPrice",
    "tpTriggerPrice",
    "tpTriggerPriceType",
    "slTriggerPrice",
    "slTriggerPriceType",
    "stp",
];
pub(in crate::exchanges::kucoin) const UTA_ORDER_INTEGER_FIELDS: &[&str] = &["cancelAfter"];
pub(in crate::exchanges::kucoin) const UTA_ORDER_BOOL_FIELDS: &[&str] =
    &["postOnly", "reduceOnly", "closeOrder"];
pub(in crate::exchanges::kucoin) const UTA_AMEND_FIELDS: &[&str] = &[
    "orderId",
    "clientOid",
    "newPrice",
    "newSize",
    "sizeUnit",
    "tpTriggerPrice",
    "tpTriggerPriceType",
    "slTriggerPrice",
    "slTriggerPriceType",
];
pub(in crate::exchanges::kucoin) const UTA_AMEND_CHANGE_FIELDS: &[&str] =
    &["newPrice", "newSize", "tpTriggerPrice", "slTriggerPrice"];
pub(in crate::exchanges::kucoin) const UTA_LIST_FIELDS: &[&str] = &[
    "tradeType",
    "side",
    "orderFilter",
    "startAt",
    "endAt",
    "lastId",
    "pageNumber",
    "pageSize",
    "fillType",
    "orderId",
];

impl KucoinClient {
    pub(super) async fn uta_private_request(
        &self,
        method_name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "batch_cancel_uta_orders" => {
                self.dispatch_batch_cancel_uta_orders(method_name, params)
                    .await
            }
            "cancel_uta_orders_by_symbol" => {
                params.ensure_allowed(&[
                    "tradeType",
                    "symbol",
                    "product_symbol",
                    "marginMode",
                    "orderFilter",
                ])?;
                validate_trade_type(params)?;
                params.required("orderFilter")?;
                validate_enum(params, "orderFilter", &["NORMAL", "ADVANCED"])?;
                validate_enum(params, "marginMode", &["CROSS", "ISOLATED"])?;
                let mut body =
                    params.body(&["tradeType", "marginMode", "orderFilter"], &[], &[])?;
                self.uta_insert_symbol(&mut body, params)?;
                self.private_post(KucoinMarket::Spot, UTA_V2_CANCEL_ALL, Value::Object(body))
                    .await
            }
            "get_uta_margin_mode" => {
                // Official UTA v2 margin-mode endpoints apply to futures only.
                // https://www.kucoin.com/docs-new/v2/rest/ua/get-margin-mode
                if params
                    .get("product_symbol")
                    .or_else(|| params.get("symbol"))
                    .is_some_and(is_spot_symbol)
                {
                    return Err(DcexError::InvalidInput(
                        "UTA margin mode supports futures only".into(),
                    ));
                }

                params.ensure_allowed(&["symbol", "product_symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Spot, UTA_V2_MARGIN_MODE, query)
                    .await
            }
            "set_uta_margin_mode" => {
                // Official UTA v2 margin-mode endpoints apply to futures only.
                // https://www.kucoin.com/docs-new/v2/rest/ua/get-margin-mode
                if params
                    .get("product_symbol")
                    .or_else(|| params.get("symbol"))
                    .is_some_and(is_spot_symbol)
                {
                    return Err(DcexError::InvalidInput(
                        "UTA margin mode supports futures only".into(),
                    ));
                }

                params.ensure_allowed(&["symbol", "product_symbol", "marginMode"])?;
                params.required("marginMode")?;
                validate_enum(params, "marginMode", &["CROSS", "ISOLATED"])?;
                let mut body = params.body(&["marginMode"], &[], &[])?;
                self.uta_insert_symbol_with_mode(&mut body, params, true)?;
                self.private_post(KucoinMarket::Spot, UTA_V2_MARGIN_MODE, Value::Object(body))
                    .await
            }
            "modify_uta_position_margin" => {
                params.ensure_allowed(&[
                    "symbol",
                    "product_symbol",
                    "type",
                    "amount",
                    "tradeType",
                ])?;
                params.required("type")?;
                validate_enum(params, "type", &["DEPOSIT", "WITHDRAW"])?;
                validate_enum(params, "tradeType", &["FUTURES"])?;
                params.required("amount")?;
                validate_positive_number(params, "amount")?;
                let amount = params.json_required("amount")?;
                if !amount.is_number() {
                    return Err(DcexError::InvalidInput(
                        "KuCoin margin amount must be a JSON number".into(),
                    ));
                }
                let mut body = params.body(&["type"], &[], &[])?;
                self.uta_insert_symbol_with_mode(&mut body, params, true)?;
                body.insert("tradeType".into(), Value::String("FUTURES".into()));
                body.insert("amount".into(), amount);
                self.private_post(
                    KucoinMarket::Spot,
                    UTA_V2_MODIFY_MARGIN,
                    Value::Object(body),
                )
                .await
            }
            "get_uta_max_order_quantity" => {
                params.ensure_allowed(&["tradeType", "symbol", "product_symbol", "price"])?;
                validate_trade_type(params)?;
                validate_positive_number(params, "price")?;
                let mut query = params.only(&["tradeType", "price"]);
                self.push_required_symbol(&mut query, params, uta_is_futures(params))?;
                self.private_get(KucoinMarket::Spot, UTA_V2_MAX_ORDER_QUANTITY, query)
                    .await
            }
            "get_uta_leverage" => {
                params.ensure_allowed(&[
                    "tradeType",
                    "symbol",
                    "product_symbol",
                    "currency",
                    "marginMode",
                ])?;
                params.required("tradeType")?;
                validate_enum(params, "tradeType", &["FUTURES", "MARGIN"])?;
                validate_trade_type(params)?;
                validate_enum(params, "marginMode", &["CROSS", "ISOLATED"])?;
                let mut query = params.only(&["tradeType", "currency", "marginMode"]);
                self.push_optional_symbol(&mut query, params, uta_is_futures(params))?;
                self.private_get(KucoinMarket::Spot, UTA_V2_LEVERAGE, query)
                    .await
            }
            "modify_uta_futures_leverage" => {
                params.ensure_allowed(&["symbol", "product_symbol", "leverage"])?;
                params.required("leverage")?;
                validate_positive_number(params, "leverage")?;
                let mut body = params.body(&["leverage"], &[], &[])?;
                self.uta_insert_symbol_with_mode(&mut body, params, true)?;
                self.private_post(
                    KucoinMarket::Spot,
                    UTA_V2_MODIFY_LEVERAGE,
                    Value::Object(body),
                )
                .await
            }
            "modify_uta_cross_margin_leverage" => {
                params.ensure_allowed(&["currency", "leverage"])?;
                params.required("leverage")?;
                validate_positive_number(params, "leverage")?;
                let body = params.body(&["currency", "leverage"], &[], &[])?;
                self.private_post(
                    KucoinMarket::Spot,
                    UTA_V2_MODIFY_MARGIN_LEVERAGE,
                    Value::Object(body),
                )
                .await
            }
            "get_uta_position_history" | "get_uta_funding_history" => {
                params.ensure_allowed(&[
                    "symbol",
                    "product_symbol",
                    "startAt",
                    "endAt",
                    "lastId",
                    "pageSize",
                ])?;
                params.body(&[], &["startAt", "endAt", "lastId", "pageSize"], &[])?;
                let mut query = params.only(&["startAt", "endAt", "lastId", "pageSize"]);
                self.push_optional_symbol(&mut query, params, true)?;
                let path = if method_name == "get_uta_position_history" {
                    UTA_V2_POSITION_HISTORY
                } else {
                    UTA_V2_FUNDING_HISTORY
                };
                self.private_get(KucoinMarket::Spot, path, query).await
            }
            "place_uta_order" => {
                let mut allowed = UTA_ORDER_FIELDS.to_vec();
                allowed.extend_from_slice(UTA_ORDER_INTEGER_FIELDS);
                allowed.extend_from_slice(UTA_ORDER_BOOL_FIELDS);
                allowed.extend_from_slice(&["product_symbol", "symbol"]);
                params.ensure_allowed(&allowed)?;
                validate_trade_type(params)?;
                validate_enum(params, "side", &["BUY", "SELL"])?;
                validate_enum(params, "orderType", &["LIMIT", "MARKET"])?;
                params.required("side")?;
                let order_type = params.required("orderType")?;
                params.required("size")?;
                params.required("sizeUnit")?;
                validate_enum(params, "sizeUnit", &["BASECCY", "QUOTECCY", "UNIT"])?;
                validate_enum(params, "stp", &["DC", "CO", "CN", "CB"])?;
                validate_positive_number(params, "size")?;
                validate_positive_number(params, "price")?;
                if order_type == "LIMIT" {
                    params.required("price")?;
                }
                let mut body = params.body(
                    UTA_ORDER_FIELDS,
                    UTA_ORDER_INTEGER_FIELDS,
                    UTA_ORDER_BOOL_FIELDS,
                )?;
                self.uta_insert_symbol(&mut body, params)?;
                if !body.contains_key("clientOid") {
                    body.insert("clientOid".into(), Value::String(generate_client_oid()));
                }
                self.private_post(KucoinMarket::Spot, UTA_V2_PLACE_ORDER, Value::Object(body))
                    .await
            }
            "cancel_uta_order" => {
                params.ensure_allowed(&[
                    "tradeType",
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "clientOid",
                ])?;
                validate_trade_type(params)?;
                require_exactly_one(params, &["orderId", "clientOid"])?;
                let mut body = params.body(&["tradeType", "orderId", "clientOid"], &[], &[])?;
                self.uta_insert_symbol(&mut body, params)?;
                self.private_post(KucoinMarket::Spot, UTA_V2_CANCEL_ORDER, Value::Object(body))
                    .await
            }
            "amend_uta_order" => {
                let mut allowed = UTA_AMEND_FIELDS.to_vec();
                allowed.extend_from_slice(&["product_symbol", "symbol", "cxlOnFail"]);
                params.ensure_allowed(&allowed)?;
                require_exactly_one(params, &["orderId", "clientOid"])?;
                if !UTA_AMEND_CHANGE_FIELDS
                    .iter()
                    .any(|key| params.get(key).is_some())
                {
                    return Err(DcexError::InvalidInput(
                        "KuCoin UTA amend requires a new price, size, or TP/SL trigger price"
                            .into(),
                    ));
                }
                for key in UTA_AMEND_CHANGE_FIELDS {
                    validate_positive_number(params, key)?;
                }
                validate_enum(params, "sizeUnit", &["BASECCY", "UNIT"])?;
                validate_enum(params, "tpTriggerPriceType", &["TP", "IP", "MP"])?;
                validate_enum(params, "slTriggerPriceType", &["TP", "IP", "MP"])?;
                let symbol = params.required_any(&["product_symbol", "symbol"])?;
                if is_spot_symbol(symbol) {
                    return Err(DcexError::InvalidInput(format!(
                        "KuCoin UTA amend supports futures only, got spot symbol {symbol}"
                    )));
                }
                let mut body = params.body(UTA_AMEND_FIELDS, &[], &["cxlOnFail"])?;
                self.uta_insert_symbol_with_mode(&mut body, params, true)?;
                self.private_post(KucoinMarket::Spot, UTA_V2_AMEND_ORDER, Value::Object(body))
                    .await
            }
            "get_uta_order_detail" => {
                params.ensure_allowed(&[
                    "tradeType",
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "clientOid",
                ])?;
                validate_trade_type(params)?;
                require_exactly_one(params, &["orderId", "clientOid"])?;
                let mut query = params.only(&["tradeType", "orderId", "clientOid"]);
                self.push_required_symbol(&mut query, params, uta_is_futures(params))?;
                self.private_get(KucoinMarket::Spot, UTA_V2_ORDER_DETAIL, query)
                    .await
            }
            "get_uta_open_orders" | "get_uta_order_history" | "get_uta_trade_history" => {
                let mut allowed = UTA_LIST_FIELDS.to_vec();
                allowed.extend_from_slice(&["product_symbol", "symbol"]);
                params.ensure_allowed(&allowed)?;
                validate_trade_type(params)?;
                let mut query = params.only(UTA_LIST_FIELDS);
                self.push_optional_symbol(&mut query, params, uta_is_futures(params))?;
                let path = match method_name {
                    "get_uta_open_orders" => UTA_V2_OPEN_ORDERS,
                    "get_uta_order_history" => UTA_V2_ORDER_HISTORY,
                    _ => UTA_V2_EXECUTIONS,
                };
                self.private_get(KucoinMarket::Spot, path, query).await
            }
            "get_uta_positions" => {
                params.ensure_allowed(&["product_symbol", "symbol", "pageNumber", "pageSize"])?;
                let mut query = params.only(&["pageNumber", "pageSize"]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Spot, UTA_V2_POSITIONS, query)
                    .await
            }
            "get_uta_account_balance" => {
                params.ensure_allowed(&[])?;
                self.private_get(KucoinMarket::Spot, UTA_V2_BALANCE, Vec::new())
                    .await
            }
            "get_uta_account_overview" => {
                params.ensure_allowed(&[])?;
                self.private_get(KucoinMarket::Spot, UTA_V2_OVERVIEW, Vec::new())
                    .await
            }
            _ => return Ok(None),
        };
        result.map(Some)
    }

    pub(in crate::exchanges::kucoin) fn uta_insert_symbol(
        &self,
        body: &mut serde_json::Map<String, Value>,
        params: &KucoinParams,
    ) -> Result<()> {
        self.uta_insert_symbol_with_mode(body, params, uta_is_futures(params))
    }

    pub(in crate::exchanges::kucoin) fn uta_insert_symbol_with_mode(
        &self,
        body: &mut serde_json::Map<String, Value>,
        params: &KucoinParams,
        futures: bool,
    ) -> Result<()> {
        let symbol = params.required_any(&["product_symbol", "symbol"])?;
        body.insert(
            "symbol".into(),
            Value::String(self.exchange_symbol(symbol, futures)?),
        );
        Ok(())
    }
}

pub(in crate::exchanges::kucoin) fn validate_trade_type(params: &KucoinParams) -> Result<()> {
    params.required("tradeType")?;
    validate_enum(params, "tradeType", &["SPOT", "MARGIN", "FUTURES"])?;
    if let Some(symbol) = params
        .get("product_symbol")
        .or_else(|| params.get("symbol"))
        && is_spot_symbol(symbol) == uta_is_futures(params)
    {
        return Err(DcexError::InvalidInput(
            "symbol does not match tradeType".into(),
        ));
    }
    Ok(())
}

/// Canonical spot product symbols end in `-SPOT`; raw KuCoin spot pairs are
/// `BASE-QUOTE`, while raw futures contracts (e.g. `XBTUSDTM`) have no dash.
pub(in crate::exchanges::kucoin) fn is_spot_symbol(symbol: &str) -> bool {
    let parts: Vec<&str> = symbol.split('-').collect();
    parts.len() == 2 || parts.get(2) == Some(&"SPOT")
}

pub(in crate::exchanges::kucoin) fn uta_is_futures(params: &KucoinParams) -> bool {
    params.get("tradeType") == Some("FUTURES")
}
