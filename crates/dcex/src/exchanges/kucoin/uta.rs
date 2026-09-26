use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{
    KucoinParams, generate_client_oid, require_exactly_one, validate_enum, validate_positive_number,
};

const UTA_ORDER_FIELDS: &[&str] = &[
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
const UTA_ORDER_INTEGER_FIELDS: &[&str] = &["cancelAfter"];
const UTA_ORDER_BOOL_FIELDS: &[&str] = &["postOnly", "reduceOnly", "closeOrder"];
const UTA_AMEND_FIELDS: &[&str] = &[
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
const UTA_AMEND_CHANGE_FIELDS: &[&str] =
    &["newPrice", "newSize", "tpTriggerPrice", "slTriggerPrice"];
const UTA_LIST_FIELDS: &[&str] = &[
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

    fn uta_insert_symbol(
        &self,
        body: &mut serde_json::Map<String, Value>,
        params: &KucoinParams,
    ) -> Result<()> {
        self.uta_insert_symbol_with_mode(body, params, uta_is_futures(params))
    }

    fn uta_insert_symbol_with_mode(
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

fn validate_trade_type(params: &KucoinParams) -> Result<()> {
    params.required("tradeType")?;
    validate_enum(params, "tradeType", &["SPOT", "MARGIN", "FUTURES"])
}

/// Canonical spot product symbols end in `-SPOT`; raw KuCoin spot pairs are
/// `BASE-QUOTE`, while raw futures contracts (e.g. `XBTUSDTM`) have no dash.
fn is_spot_symbol(symbol: &str) -> bool {
    let parts: Vec<&str> = symbol.split('-').collect();
    parts.len() == 2 || parts.get(2) == Some(&"SPOT")
}

fn uta_is_futures(params: &KucoinParams) -> bool {
    params.get("tradeType") == Some("FUTURES")
}
