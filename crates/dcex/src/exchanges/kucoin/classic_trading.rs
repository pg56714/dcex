//! Current classic trading and risk endpoints. See docs/endpoint-audit.md.
use super::client::{KucoinClient, KucoinMarket};
use super::params::{
    KucoinParams, bool_value, generate_client_oid, path_identifier, path_segment,
    require_exactly_one, validate_bool, validate_client_oid, validate_enum,
    validate_positive_number, validate_time_range, validate_u64_range,
};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
use serde_json::{Map, Value};
impl KucoinClient {
    pub(super) async fn classic_trading_request(
        &self,
        name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match name {
            "place_futures_batch_orders" => {
                validate_params(params, &["orders"])?;
                let orders = params.json_required("orders")?;
                let orders = orders
                    .as_array()
                    .filter(|v| !v.is_empty() && v.len() <= 20)
                    .ok_or_else(|| {
                        DcexError::InvalidInput("batch requires 1..=20 orders".into())
                    })?;
                let mut bodies = Vec::new();
                let mut ids = std::collections::HashSet::new();
                for order in orders {
                    let object = order
                        .as_object()
                        .ok_or_else(|| DcexError::InvalidInput("order must be an object".into()))?;
                    let mut pairs = Vec::new();
                    for (k, v) in object {
                        if !matches!(v, Value::String(_) | Value::Number(_) | Value::Bool(_)) {
                            return Err(DcexError::InvalidInput(
                                "batch order fields must be scalar values".into(),
                            ));
                        }
                        pairs.push((
                            k.clone(),
                            v.as_str()
                                .map(str::to_string)
                                .unwrap_or_else(|| v.to_string()),
                        ));
                    }
                    let body = self.build_futures_order_body(
                        &KucoinParams::from_pairs(pairs),
                        None,
                        None,
                        false,
                    )?;
                    if !ids.insert(body["clientOid"].as_str().unwrap_or_default().to_owned()) {
                        return Err(DcexError::InvalidInput(
                            "duplicate clientOid in batch".into(),
                        ));
                    }
                    bodies.push(Value::Object(body));
                }
                self.private_post(
                    KucoinMarket::Futures,
                    "/api/v1/orders/multi",
                    Value::Array(bodies),
                )
                .await?
            }
            "cancel_futures_batch_orders" => {
                validate_params(params, &["orderIdsList", "clientOidsList"])?;
                if params.get("orderIdsList").is_some() == params.get("clientOidsList").is_some() {
                    return Err(DcexError::InvalidInput(
                        "provide exactly one of orderIdsList or clientOidsList".into(),
                    ));
                }
                let mut body = Map::new();
                for k in ["orderIdsList", "clientOidsList"] {
                    if params.get(k).is_none() {
                        continue;
                    }
                    let mut value = params.json_required(k)?;
                    let list = value
                        .as_array_mut()
                        .filter(|v| !v.is_empty() && v.len() <= 10)
                        .ok_or_else(|| {
                            DcexError::InvalidInput("cancel list requires 1..=10 orders".into())
                        })?;
                    for item in list {
                        if k == "orderIdsList" {
                            if item.as_str().is_none_or(|v| v.trim().is_empty()) {
                                return Err(DcexError::InvalidInput(
                                    "order IDs must be nonempty strings".into(),
                                ));
                            }
                        } else {
                            let item = item.as_object_mut().ok_or_else(|| {
                                DcexError::InvalidInput(
                                    "clientOidsList items must be objects".into(),
                                )
                            })?;
                            if item
                                .keys()
                                .any(|k| !matches!(k.as_str(), "symbol" | "clientOid"))
                            {
                                return Err(DcexError::InvalidInput(
                                    "unknown clientOidsList item field".into(),
                                ));
                            }
                            let id = item
                                .get("clientOid")
                                .and_then(Value::as_str)
                                .filter(|v| !v.trim().is_empty())
                                .ok_or_else(|| {
                                    DcexError::InvalidInput("clientOid is required".into())
                                })?;
                            validate_client_oid(
                                &KucoinParams::from_pairs(vec![("clientOid".into(), id.into())]),
                                "clientOid",
                            )?;
                            let symbol =
                                item.get("symbol").and_then(Value::as_str).ok_or_else(|| {
                                    DcexError::InvalidInput("symbol is required".into())
                                })?;
                            let symbol = self.exchange_symbol(symbol, true)?;
                            item.insert("symbol".into(), symbol.into());
                        }
                    }
                    body.insert(k.into(), value);
                }
                let body = serde_json::to_vec(&body)
                    .map_err(|e| DcexError::InvalidInput(e.to_string()))?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Futures,
                    "/api/v1/orders/multi-cancel",
                    Vec::new(),
                    Some(body),
                    true,
                )
                .await?
            }
            "set_futures_batch_margin_mode" => {
                validate_params(params, &["marginMode", "symbols"])?;
                params.required("marginMode")?;
                validate_enum(params, "marginMode", &["ISOLATED", "CROSS"])?;
                let mut symbols = params.json_required("symbols")?;
                let list = symbols
                    .as_array_mut()
                    .filter(|v| !v.is_empty())
                    .ok_or_else(|| {
                        DcexError::InvalidInput("symbols must be a nonempty array".into())
                    })?;
                for symbol in list {
                    *symbol = self
                        .exchange_symbol(
                            symbol.as_str().ok_or_else(|| {
                                DcexError::InvalidInput("symbol must be a string".into())
                            })?,
                            true,
                        )?
                        .into();
                }
                self.private_post(KucoinMarket::Futures,"/api/v2/position/batchChangeMarginMode",serde_json::json!({"marginMode":params.required("marginMode")?,"symbols":symbols})).await?
            }
            "get_spot_stop_order_by_client_oid" => {
                validate_params(params, &["clientOid", "product_symbol", "symbol"])?;
                params.required("clientOid")?;

                let mut query = params.only(&["clientOid"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.private_get(
                    KucoinMarket::Spot,
                    "/api/v1/stop-order/queryOrderByClientOid",
                    query,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/cancel-order-by-clientoid
            "cancel_spot_order_by_client_oid" => {
                validate_params(params, &["symbol", "clientOid", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("clientOid")?;

                let path = "/api/v1/hf/orders/client-order/{clientOid}"
                    .replace("{clientOid}", path_identifier(params, "clientOid")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/cancel-partial-order
            "cancel_spot_partial_order" => {
                validate_params(
                    params,
                    &["symbol", "cancelSize", "orderId", "product_symbol"],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("cancelSize")?;
                validate_positive_number(params, "cancelSize")?;
                params.required("orderId")?;

                let path = "/api/v1/hf/orders/cancel/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let mut query = params.only(&["cancelSize"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-order-by-orderld
            "get_spot_order" => {
                validate_params(params, &["symbol", "orderId", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("orderId")?;

                let path = "/api/v1/hf/orders/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-order-by-clientoid
            "get_spot_order_by_client_oid" => {
                validate_params(params, &["symbol", "clientOid", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("clientOid")?;

                let path = "/api/v1/hf/orders/client-order/{clientOid}"
                    .replace("{clientOid}", path_identifier(params, "clientOid")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-symbols-with-open-order
            "get_spot_active_order_symbols" => {
                validate_params(params, &[])?;

                let path = "/api/v1/hf/orders/active/symbols".to_string();
                let query = params.only(&[]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-open-orders
            "get_spot_active_orders" => {
                validate_params(params, &["symbol", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;

                let path = "/api/v1/hf/orders/active".to_string();
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-closed-orders
            "get_spot_closed_orders" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "side",
                        "type",
                        "lastId",
                        "limit",
                        "startAt",
                        "endAt",
                        "product_symbol",
                    ],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_u64_range(params, "lastId", 0, 9223372036854775807)?;
                validate_u64_range(params, "limit", 1, 100)?;
                validate_u64_range(params, "startAt", 1000000000000, 9999999999999)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;

                let path = "/api/v1/hf/orders/done".to_string();
                let mut query =
                    params.only(&["side", "type", "lastId", "limit", "startAt", "endAt"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/add-stop-order
            "place_spot_stop_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "type",
                        "remark",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "postOnly",
                        "cancelAfter",
                        "funds",
                        "stopPrice",
                        "tradeType",
                        "stop",
                        "product_symbol",
                    ],
                )?;
                params.required("side")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("type")?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_enum(params, "stp", &["DC", "CO", "CN", "CB"])?;
                validate_positive_number(params, "price")?;
                validate_positive_number(params, "size")?;
                validate_enum(params, "timeInForce", &["GTC", "GTT", "IOC", "FOK"])?;
                validate_bool(params, "postOnly")?;
                validate_positive_number(params, "funds")?;
                params.required("stopPrice")?;
                validate_positive_number(params, "stopPrice")?;
                validate_enum(params, "stop", &["loss", "entry"])?;

                validate_classic_order(params, false, false)?;
                let path = "/api/v1/stop-order".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "type",
                        "remark",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "funds",
                        "stopPrice",
                        "tradeType",
                        "stop",
                    ],
                    &["cancelAfter"],
                    &["postOnly"],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, false)?),
                    );
                }
                if !body.contains_key("clientOid") {
                    body.insert("clientOid".into(), generate_client_oid().into());
                }
                self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/cancel-stop-order-by-clientoid
            "cancel_spot_stop_order_by_client_oid" => {
                validate_params(params, &["symbol", "clientOid", "product_symbol"])?;
                params.required("clientOid")?;

                let path = "/api/v1/stop-order/cancelOrderByClientOid".to_string();
                let mut query = params.only(&["clientOid"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/cancel-stop-order-by-orderld
            "cancel_spot_stop_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v1/stop-order/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let query = params.only(&[]);
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/batch-cancel-stop-orders
            "cancel_spot_stop_orders" => {
                validate_params(
                    params,
                    &["symbol", "tradeType", "orderIds", "product_symbol"],
                )?;

                let path = "/api/v1/stop-order/cancel".to_string();
                let mut query = params.only(&["tradeType", "orderIds"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-stop-orders-list
            "get_spot_stop_orders" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "side",
                        "type",
                        "tradeType",
                        "startAt",
                        "endAt",
                        "currentPage",
                        "orderIds",
                        "pageSize",
                        "stop",
                        "product_symbol",
                    ],
                )?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "currentPage", 1, 9223372036854775807)?;
                validate_u64_range(params, "pageSize", 10, 500)?;

                let path = "/api/v1/stop-order".to_string();
                let mut query = params.only(&[
                    "side",
                    "type",
                    "tradeType",
                    "startAt",
                    "endAt",
                    "currentPage",
                    "orderIds",
                    "pageSize",
                    "stop",
                ]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-stop-order-by-orderld
            "get_spot_stop_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v1/stop-order/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let query = params.only(&[]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/add-oco-order
            "place_spot_oco_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "remark",
                        "price",
                        "size",
                        "stopPrice",
                        "limitPrice",
                        "tradeType",
                        "product_symbol",
                    ],
                )?;
                params.required("clientOid")?;
                params.required("side")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("price")?;
                validate_positive_number(params, "price")?;
                params.required("size")?;
                validate_positive_number(params, "size")?;
                params.required("stopPrice")?;
                validate_positive_number(params, "stopPrice")?;
                params.required("limitPrice")?;
                validate_positive_number(params, "limitPrice")?;
                validate_enum(params, "tradeType", &["TRADE"])?;

                validate_classic_order(params, false, true)?;
                let path = "/api/v3/oco/order".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "remark",
                        "price",
                        "size",
                        "stopPrice",
                        "limitPrice",
                        "tradeType",
                    ],
                    &[],
                    &[],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, false)?),
                    );
                }
                self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/cancel-oco-order-by-orderld
            "cancel_spot_oco_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/oco/order/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let query = params.only(&[]);
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/cancel-oco-order-by-clientoid
            "cancel_spot_oco_order_by_client_oid" => {
                validate_params(params, &["clientOid"])?;
                params.required("clientOid")?;

                let path = "/api/v3/oco/client-order/{clientOid}"
                    .replace("{clientOid}", path_identifier(params, "clientOid")?);
                let query = params.only(&[]);
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/batch-cancel-oco-order
            "cancel_spot_oco_orders" => {
                validate_params(params, &["orderIds", "symbol", "product_symbol"])?;

                let path = "/api/v3/oco/orders".to_string();
                let mut query = params.only(&["orderIds"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-oco-order-by-orderld
            "get_spot_oco_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/oco/order/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let query = params.only(&[]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-oco-order-by-clientoid
            "get_spot_oco_order_by_client_oid" => {
                validate_params(params, &["clientOid"])?;
                params.required("clientOid")?;

                let path = "/api/v3/oco/client-order/{clientOid}"
                    .replace("{clientOid}", path_identifier(params, "clientOid")?);
                let query = params.only(&[]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-oco-order-detail-by-orderld
            "get_spot_oco_order_details" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/oco/order/details/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let query = params.only(&[]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/spot-trading/orders/get-oco-order-list
            "get_spot_oco_orders" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "startAt",
                        "endAt",
                        "orderIds",
                        "pageSize",
                        "currentPage",
                        "product_symbol",
                    ],
                )?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "pageSize", 10, 500)?;
                validate_u64_range(params, "currentPage", 0, 9223372036854775807)?;

                let path = "/api/v3/oco/orders".to_string();
                let mut query =
                    params.only(&["startAt", "endAt", "orderIds", "pageSize", "currentPage"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/add-order
            "place_margin_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "type",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "postOnly",
                        "cancelAfter",
                        "funds",
                        "isIsolated",
                        "autoBorrow",
                        "autoRepay",
                        "product_symbol",
                    ],
                )?;
                params.required("clientOid")?;
                params.required("side")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_enum(params, "stp", &["DC", "CO", "CN", "CB"])?;
                validate_positive_number(params, "price")?;
                validate_positive_number(params, "size")?;
                validate_enum(params, "timeInForce", &["GTC", "GTT", "IOC", "FOK"])?;
                validate_bool(params, "postOnly")?;
                validate_positive_number(params, "funds")?;
                validate_bool(params, "isIsolated")?;
                validate_bool(params, "autoBorrow")?;
                validate_bool(params, "autoRepay")?;

                validate_classic_order(params, false, false)?;
                let path = "/api/v3/hf/margin/order".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "type",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "funds",
                    ],
                    &["cancelAfter"],
                    &["postOnly", "isIsolated", "autoBorrow", "autoRepay"],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, false)?),
                    );
                }
                self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/add-order-test
            "test_margin_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "type",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "postOnly",
                        "cancelAfter",
                        "funds",
                        "isIsolated",
                        "autoBorrow",
                        "autoRepay",
                        "product_symbol",
                    ],
                )?;
                params.required("clientOid")?;
                params.required("side")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_enum(params, "stp", &["DC", "CO", "CN", "CB"])?;
                validate_positive_number(params, "price")?;
                validate_positive_number(params, "size")?;
                validate_enum(params, "timeInForce", &["GTC", "GTT", "IOC", "FOK"])?;
                validate_bool(params, "postOnly")?;
                validate_positive_number(params, "funds")?;
                validate_bool(params, "isIsolated")?;
                validate_bool(params, "autoBorrow")?;
                validate_bool(params, "autoRepay")?;

                validate_classic_order(params, false, false)?;
                let path = "/api/v3/hf/margin/order/test".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "type",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "funds",
                    ],
                    &["cancelAfter"],
                    &["postOnly", "isIsolated", "autoBorrow", "autoRepay"],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, false)?),
                    );
                }
                self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-order-by-orderld
            "cancel_margin_order" => {
                validate_params(params, &["symbol", "orderId", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("orderId")?;

                let path = "/api/v3/hf/margin/orders/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-order-by-clientoid
            "cancel_margin_order_by_client_oid" => {
                validate_params(params, &["symbol", "clientOid", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("clientOid")?;

                let path = "/api/v3/hf/margin/orders/client-order/{clientOid}"
                    .replace("{clientOid}", path_identifier(params, "clientOid")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-all-orders-by-symbol
            "cancel_margin_orders_by_symbol" => {
                validate_params(params, &["symbol", "tradeType", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("tradeType")?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;

                let path = "/api/v3/hf/margin/orders".to_string();
                let mut query = params.only(&["tradeType"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-symbols-with-open-order
            "get_margin_active_order_symbols" => {
                validate_params(params, &["tradeType"])?;
                params.required("tradeType")?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;

                let path = "/api/v3/hf/margin/order/active/symbols".to_string();
                let query = params.only(&["tradeType"]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-open-orders
            "get_margin_open_orders" => {
                validate_params(params, &["symbol", "tradeType", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("tradeType")?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;

                let path = "/api/v3/hf/margin/orders/active".to_string();
                let mut query = params.only(&["tradeType"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-closed-orders
            "get_margin_closed_orders" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "tradeType",
                        "side",
                        "type",
                        "lastId",
                        "limit",
                        "startAt",
                        "endAt",
                        "product_symbol",
                    ],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("tradeType")?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_u64_range(params, "lastId", 0, 9223372036854775807)?;
                validate_u64_range(params, "limit", 1, 100)?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;

                let path = "/api/v3/hf/margin/orders/done".to_string();
                let mut query = params.only(&[
                    "tradeType",
                    "side",
                    "type",
                    "lastId",
                    "limit",
                    "startAt",
                    "endAt",
                ]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-trade-history
            "get_margin_trade_history" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "tradeType",
                        "orderId",
                        "side",
                        "type",
                        "lastId",
                        "limit",
                        "startAt",
                        "endAt",
                        "product_symbol",
                    ],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("tradeType")?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_u64_range(params, "lastId", 0, 9223372036854775807)?;
                validate_u64_range(params, "limit", 1, 100)?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;

                let path = "/api/v3/hf/margin/fills".to_string();
                let mut query = params.only(&[
                    "tradeType",
                    "orderId",
                    "side",
                    "type",
                    "lastId",
                    "limit",
                    "startAt",
                    "endAt",
                ]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-order-by-orderld
            "get_margin_order" => {
                validate_params(params, &["symbol", "orderId", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("orderId")?;

                let path = "/api/v3/hf/margin/orders/{orderId}"
                    .replace("{orderId}", path_identifier(params, "orderId")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-order-by-clientoid
            "get_margin_order_by_client_oid" => {
                validate_params(params, &["symbol", "clientOid", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("clientOid")?;

                let path = "/api/v3/hf/margin/orders/client-order/{clientOid}"
                    .replace("{clientOid}", path_identifier(params, "clientOid")?);
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/add-stop-order
            "place_margin_stop_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "type",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "postOnly",
                        "cancelAfter",
                        "funds",
                        "isIsolated",
                        "autoBorrow",
                        "autoRepay",
                        "remark",
                        "stop",
                        "stopPrice",
                        "product_symbol",
                    ],
                )?;
                params.required("clientOid")?;
                params.required("side")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_enum(params, "stp", &["DC", "CO", "CN", "CB"])?;
                validate_positive_number(params, "price")?;
                validate_positive_number(params, "size")?;
                validate_enum(params, "timeInForce", &["GTC", "GTT", "IOC", "FOK"])?;
                validate_bool(params, "postOnly")?;
                validate_positive_number(params, "funds")?;
                params.required("isIsolated")?;
                validate_bool(params, "isIsolated")?;
                params.required("autoBorrow")?;
                validate_bool(params, "autoBorrow")?;
                params.required("autoRepay")?;
                validate_bool(params, "autoRepay")?;
                validate_enum(params, "stop", &["loss", "entry"])?;
                params.required("stopPrice")?;
                validate_positive_number(params, "stopPrice")?;

                validate_classic_order(params, false, false)?;
                let path = "/api/v3/hf/margin/stop-order".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "type",
                        "stp",
                        "price",
                        "size",
                        "timeInForce",
                        "funds",
                        "remark",
                        "stop",
                        "stopPrice",
                    ],
                    &["cancelAfter"],
                    &["postOnly", "isIsolated", "autoBorrow", "autoRepay"],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, false)?),
                    );
                }
                self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-stop-order-by-clientoid
            "cancel_margin_stop_order_by_client_oid" => {
                validate_params(params, &["clientOid"])?;
                params.required("clientOid")?;

                let path = "/api/v3/hf/margin/stop-order/cancel-by-clientOid".to_string();
                let query = params.only(&["clientOid"]);
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/batch-cancel-stop-orders
            "cancel_margin_stop_orders" => {
                validate_params(
                    params,
                    &["symbol", "tradeType", "orderIds", "product_symbol"],
                )?;
                params.required("tradeType")?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_ISOLATED_TRADE", "MARGIN_TRADE"],
                )?;

                let path = "/api/v3/hf/margin/stop-order/cancel".to_string();
                let mut query = params.only(&["tradeType", "orderIds"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-stop-order-list
            "get_margin_stop_orders" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "side",
                        "type",
                        "tradeType",
                        "startAt",
                        "endAt",
                        "currentPage",
                        "orderIds",
                        "pageSize",
                        "stop",
                        "product_symbol",
                    ],
                )?;
                validate_enum(
                    params,
                    "type",
                    &["limit", "market", "limit_stop", "market_stop"],
                )?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_ISOLATED_TRADE", "MARGIN_TRADE"],
                )?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "currentPage", 1, 9223372036854775807)?;
                validate_u64_range(params, "pageSize", 10, 500)?;
                validate_enum(params, "stop", &["stop", "oco"])?;

                let path = "/api/v3/hf/margin/stop-orders".to_string();
                let mut query = params.only(&[
                    "side",
                    "type",
                    "tradeType",
                    "startAt",
                    "endAt",
                    "currentPage",
                    "orderIds",
                    "pageSize",
                    "stop",
                ]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-stop-order-by-orderld
            "get_margin_stop_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/hf/margin/stop-order/orderId".to_string();
                let query = params.only(&["orderId"]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-stop-order-by-clientoid
            "get_margin_stop_order_by_client_oid" => {
                validate_params(params, &["clientOid"])?;
                params.required("clientOid")?;

                let path = "/api/v3/hf/margin/stop-order/clientOid".to_string();
                let query = params.only(&["clientOid"]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/add-oco-order
            "place_margin_oco_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "price",
                        "size",
                        "stopPrice",
                        "limitPrice",
                        "isIsolated",
                        "autoRepay",
                        "autoBorrow",
                        "product_symbol",
                    ],
                )?;
                params.required("clientOid")?;
                params.required("side")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("price")?;
                validate_positive_number(params, "price")?;
                params.required("size")?;
                validate_positive_number(params, "size")?;
                params.required("stopPrice")?;
                validate_positive_number(params, "stopPrice")?;
                params.required("limitPrice")?;
                validate_positive_number(params, "limitPrice")?;
                params.required("isIsolated")?;
                validate_bool(params, "isIsolated")?;
                validate_bool(params, "autoRepay")?;
                validate_bool(params, "autoBorrow")?;

                validate_classic_order(params, false, true)?;
                let path = "/api/v3/hf/margin/oco-order".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "price",
                        "size",
                        "stopPrice",
                        "limitPrice",
                    ],
                    &[],
                    &["isIsolated", "autoRepay", "autoBorrow"],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, false)?),
                    );
                }
                self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-oco-order-by-orderld
            "cancel_margin_oco_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/hf/margin/oco-order/cancel-by-id".to_string();
                let query = params.only(&["orderId"]);
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-oco-order-by-clientoid
            "cancel_margin_oco_order_by_client_oid" => {
                validate_params(params, &["clientOid"])?;
                params.required("clientOid")?;

                let path = "/api/v3/hf/margin/oco-order/cancel-by-clientOid".to_string();
                let query = params.only(&["clientOid"]);
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/batch-cancel-oco-orders
            "cancel_margin_oco_orders" => {
                validate_params(
                    params,
                    &["orderIds", "symbol", "tradeType", "product_symbol"],
                )?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;

                let path = "/api/v3/hf/margin/oco-order/cancel".to_string();
                let mut query = params.only(&["orderIds", "tradeType"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Spot,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-oco-order-by-orderld
            "get_margin_oco_order" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/hf/margin/oco-order/orderId".to_string();
                let query = params.only(&["orderId"]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-oco-order-by-clientoid
            "get_margin_oco_order_by_client_oid" => {
                validate_params(params, &["clientOid"])?;
                params.required("clientOid")?;

                let path = "/api/v3/hf/margin/oco-order/clientOid".to_string();
                let query = params.only(&["clientOid"]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-oco-order-detail-by-orderld
            "get_margin_oco_order_details" => {
                validate_params(params, &["orderId"])?;
                params.required("orderId")?;

                let path = "/api/v3/hf/margin/oco-order/detail/orderId".to_string();
                let query = params.only(&["orderId"]);
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/margin-trading/orders/get-oco-order-list
            "get_margin_oco_orders" => {
                validate_params(
                    params,
                    &[
                        "pageSize",
                        "currentPage",
                        "symbol",
                        "startAt",
                        "endAt",
                        "orderIds",
                        "tradeType",
                        "product_symbol",
                    ],
                )?;
                params.required("pageSize")?;
                validate_u64_range(params, "pageSize", 10, 500)?;
                params.required("currentPage")?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;
                validate_enum(
                    params,
                    "tradeType",
                    &["MARGIN_TRADE", "MARGIN_ISOLATED_TRADE"],
                )?;

                let path = "/api/v3/hf/margin/oco-orders".to_string();
                let mut query = params.only(&[
                    "pageSize",
                    "currentPage",
                    "startAt",
                    "endAt",
                    "orderIds",
                    "tradeType",
                ]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.request(HttpMethod::Get, KucoinMarket::Spot, path, query, None, true)
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/orders/add-take-profit-and-stop-loss-order
            "place_futures_tpsl_order" => {
                validate_params(
                    params,
                    &[
                        "clientOid",
                        "side",
                        "symbol",
                        "leverage",
                        "type",
                        "remark",
                        "stopPriceType",
                        "reduceOnly",
                        "closeOrder",
                        "forceHold",
                        "stp",
                        "marginMode",
                        "price",
                        "size",
                        "timeInForce",
                        "postOnly",
                        "triggerStopUpPrice",
                        "triggerStopDownPrice",
                        "qty",
                        "valueQty",
                        "positionSide",
                        "product_symbol",
                    ],
                )?;
                params.required("clientOid")?;
                validate_enum(params, "side", &["buy", "sell"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_u64_range(params, "leverage", 0, 9223372036854775807)?;
                validate_positive_number(params, "leverage")?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_enum(params, "stopPriceType", &["TP", "MP", "IP"])?;
                validate_bool(params, "reduceOnly")?;
                validate_bool(params, "closeOrder")?;
                validate_bool(params, "forceHold")?;
                validate_enum(params, "stp", &["CN", "CO", "CB"])?;
                validate_enum(params, "marginMode", &["ISOLATED", "CROSS"])?;
                validate_positive_number(params, "price")?;
                validate_u64_range(params, "size", 0, 9223372036854775807)?;
                validate_positive_number(params, "size")?;
                validate_enum(params, "timeInForce", &["GTC", "IOC"])?;
                validate_bool(params, "postOnly")?;
                validate_positive_number(params, "triggerStopUpPrice")?;
                validate_positive_number(params, "triggerStopDownPrice")?;
                validate_positive_number(params, "qty")?;
                validate_positive_number(params, "valueQty")?;
                validate_enum(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;

                validate_classic_order(params, true, false)?;
                let path = "/api/v1/st-orders".to_string();
                let mut body = params.body(
                    &[
                        "clientOid",
                        "side",
                        "type",
                        "remark",
                        "stopPriceType",
                        "stp",
                        "marginMode",
                        "price",
                        "timeInForce",
                        "triggerStopUpPrice",
                        "triggerStopDownPrice",
                        "qty",
                        "valueQty",
                        "positionSide",
                    ],
                    &["leverage", "size"],
                    &["reduceOnly", "closeOrder", "forceHold", "postOnly"],
                )?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, true)?),
                    );
                }
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/orders/cancel-all-stop-orders
            "cancel_futures_stop_orders" => {
                validate_params(params, &["symbol", "product_symbol"])?;

                let path = "/api/v1/stopOrders".to_string();
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Delete,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/orders/get-recent-closed-orders
            "get_futures_recent_closed_orders" => {
                validate_params(params, &["symbol", "product_symbol"])?;

                let path = "/api/v1/recentDoneOrders".to_string();
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/orders/get-stop-order-list
            "get_futures_stop_orders" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "side",
                        "type",
                        "startAt",
                        "endAt",
                        "currentPage",
                        "pageSize",
                        "product_symbol",
                    ],
                )?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "currentPage", 0, 9223372036854775807)?;
                validate_u64_range(params, "pageSize", 0, 1000)?;

                let path = "/api/v1/stopOrders".to_string();
                let mut query = params.only(&[
                    "side",
                    "type",
                    "startAt",
                    "endAt",
                    "currentPage",
                    "pageSize",
                ]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-margin-mode
            "get_futures_margin_mode" => {
                validate_params(params, &["symbol", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;

                let path = "/api/v2/position/getMarginMode".to_string();
                let mut query = params.only(&[]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/switch-margin-mode
            "set_futures_margin_mode" => {
                validate_params(params, &["symbol", "marginMode", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("marginMode")?;
                validate_enum(params, "marginMode", &["ISOLATED", "CROSS"])?;

                let path = "/api/v2/position/changeMarginMode".to_string();
                let mut body = params.body(&["marginMode"], &[], &[])?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, true)?),
                    );
                }
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/switch-position-mode
            "set_futures_position_mode" => {
                validate_params(params, &["positionMode"])?;
                params.required("positionMode")?;
                validate_enum(params, "positionMode", &["0", "1"])?;

                let path = "/api/v2/position/switchPositionMode".to_string();
                let body = params.body(&["positionMode"], &[], &[])?;
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-max-open-size
            "get_futures_max_open_size" => {
                validate_params(params, &["symbol", "price", "leverage", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("price")?;
                validate_positive_number(params, "price")?;
                params.required("leverage")?;
                validate_u64_range(params, "leverage", 0, 9223372036854775807)?;
                validate_positive_number(params, "leverage")?;

                let path = "/api/v2/getMaxOpenSize".to_string();
                let mut query = params.only(&["price", "leverage"]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-positions-history
            "get_futures_position_history" => {
                validate_params(
                    params,
                    &["symbol", "from", "to", "limit", "pageId", "product_symbol"],
                )?;
                validate_u64_range(params, "from", 0, 9223372036854775807)?;
                validate_u64_range(params, "to", 0, 9223372036854775807)?;
                validate_u64_range(params, "limit", 0, 200)?;
                validate_u64_range(params, "pageId", 0, 9223372036854775807)?;

                let path = "/api/v1/history-positions".to_string();
                let mut query = params.only(&["from", "to", "limit", "pageId"]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-max-withdraw-margin
            "get_futures_max_withdraw_margin" => {
                validate_params(params, &["symbol", "positionSide", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_enum(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;

                let path = "/api/v1/margin/maxWithdrawMargin".to_string();
                let mut query = params.only(&["positionSide"]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/add-isolated-margin
            "add_futures_isolated_margin" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "margin",
                        "bizNo",
                        "positionSide",
                        "product_symbol",
                    ],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("margin")?;
                validate_positive_number(params, "margin")?;
                params.required("bizNo")?;
                validate_enum(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;

                let path = "/api/v1/position/margin/deposit-margin".to_string();
                let mut body = params.body(&["bizNo", "positionSide"], &[], &[])?;
                if let Some(v) = params.get("margin") {
                    let v = serde_json::from_str::<Value>(v)
                        .map_err(|_| DcexError::InvalidInput("expected JSON number".into()))?;
                    if !v.is_number() {
                        return Err(DcexError::InvalidInput("expected JSON number".into()));
                    }
                    body.insert("margin".into(), v);
                }
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, true)?),
                    );
                }
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/remove-isolated-margin
            "remove_futures_isolated_margin" => {
                validate_params(
                    params,
                    &["symbol", "withdrawAmount", "positionSide", "product_symbol"],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("withdrawAmount")?;
                validate_positive_number(params, "withdrawAmount")?;
                validate_enum(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;

                let path = "/api/v1/margin/withdrawMargin".to_string();
                let mut body = params.body(&["withdrawAmount", "positionSide"], &[], &[])?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, true)?),
                    );
                }
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-cross-margin-risk-limit
            "get_futures_cross_margin_risk_limit" => {
                validate_params(
                    params,
                    &["symbol", "totalMargin", "leverage", "product_symbol"],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_u64_range(params, "leverage", 0, 9223372036854775807)?;
                validate_positive_number(params, "leverage")?;

                let path = "/api/v2/batchGetCrossOrderLimit".to_string();
                let mut query = params.only(&["totalMargin", "leverage"]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-cross-margin-requirement
            "get_futures_cross_margin_requirement" => {
                validate_params(
                    params,
                    &["symbol", "leverage", "positionValue", "product_symbol"],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_positive_number(params, "leverage")?;
                params.required("positionValue")?;
                validate_positive_number(params, "positionValue")?;

                let path = "/api/v2/getCrossModeMarginRequirement".to_string();
                let mut body = params.body(&["leverage", "positionValue"], &[], &[])?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, true)?),
                    );
                }
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/get-isolated-margin-risk-limit
            "get_futures_isolated_margin_risk_limit" => {
                validate_params(params, &["symbol", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;

                let symbol = self
                    .exchange_symbol(params.required_any(&["symbol", "product_symbol"])?, true)?;
                let path = "/api/v1/contracts/risk-limit/{symbol}"
                    .replace("{symbol}", path_segment(&symbol)?);
                let query = params.only(&[]);
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/positions/modify-isolated-margin-risk-limit
            "set_futures_isolated_margin_risk_limit" => {
                validate_params(params, &["symbol", "level", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("level")?;
                validate_u64_range(params, "level", 0, 9223372036854775807)?;

                let path = "/api/v1/position/risk-limit-level/change".to_string();
                let mut body = params.body(&[], &["level"], &[])?;
                if let Some(v) = params.get_any(&["product_symbol", "symbol"]) {
                    body.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol(v, true)?),
                    );
                }
                self.private_post(KucoinMarket::Futures, path, Value::Object(body))
                    .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/funding-fees/get-current-funding-rate
            "get_futures_current_funding_rate" => {
                validate_params(params, &["symbol", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;

                let symbol = self
                    .exchange_symbol(params.required_any(&["symbol", "product_symbol"])?, true)?;
                let path = "/api/v1/funding-rate/{symbol}/current"
                    .replace("{symbol}", path_segment(&symbol)?);
                let query = params.only(&[]);
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    false,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/funding-fees/get-public-funding-history
            "get_futures_public_funding_history" => {
                validate_params(params, &["symbol", "from", "to", "product_symbol"])?;
                params.required_any(&["symbol", "product_symbol"])?;
                params.required("from")?;
                validate_u64_range(params, "from", 0, 9223372036854775807)?;
                params.required("to")?;
                validate_u64_range(params, "to", 0, 9223372036854775807)?;

                let path = "/api/v1/contract/funding-rates".to_string();
                let mut query = params.only(&["from", "to"]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    false,
                )
                .await?
            }
            // https://www.kucoin.com/docs-new/rest/futures-trading/funding-fees/get-private-funding-history
            "get_futures_funding_history" => {
                validate_params(
                    params,
                    &[
                        "symbol",
                        "startAt",
                        "endAt",
                        "reverse",
                        "offset",
                        "forward",
                        "maxCount",
                        "product_symbol",
                    ],
                )?;
                params.required_any(&["symbol", "product_symbol"])?;
                validate_u64_range(params, "startAt", 0, 9223372036854775807)?;
                validate_u64_range(params, "endAt", 0, 9223372036854775807)?;
                validate_bool(params, "reverse")?;
                validate_u64_range(params, "offset", 0, 9223372036854775807)?;
                validate_bool(params, "forward")?;
                validate_u64_range(params, "maxCount", 0, 1500)?;

                let path = "/api/v1/funding-history".to_string();
                let mut query = params.only(&[
                    "startAt", "endAt", "reverse", "offset", "forward", "maxCount",
                ]);
                self.push_optional_symbol(&mut query, params, true)?;
                self.request(
                    HttpMethod::Get,
                    KucoinMarket::Futures,
                    path,
                    query,
                    None,
                    true,
                )
                .await?
            }
            _ => return Ok(None),
        };
        Ok(Some(response))
    }
}

fn validate_classic_order(params: &KucoinParams, futures: bool, oco: bool) -> Result<()> {
    let is_true = |key| params.get(key).and_then(bool_value) == Some(true);
    let kind = params.get("type").unwrap_or("limit");
    if futures && is_true("closeOrder") {
        if ["side", "size", "qty", "valueQty", "leverage"]
            .iter()
            .any(|k| params.get(k).is_some())
        {
            return Err(DcexError::InvalidInput(
                "closeOrder requires side and quantity fields to be omitted".into(),
            ));
        }
    } else {
        params.required("side")?;
        if futures {
            require_exactly_one(params, &["size", "qty", "valueQty"])?;
        } else if kind == "market" {
            require_exactly_one(params, &["size", "funds"])?;
        } else {
            params.required("size")?;
        }
    }
    if kind == "limit" || oco {
        params.required("price")?;
    } else if params.get("price").is_some()
        || params.get("timeInForce").is_some()
        || is_true("postOnly")
    {
        return Err(DcexError::InvalidInput(
            "market orders cannot include limit order fields".into(),
        ));
    }
    if is_true("postOnly") && matches!(params.get("timeInForce"), Some("IOC" | "FOK")) {
        return Err(DcexError::InvalidInput(
            "postOnly is incompatible with IOC/FOK".into(),
        ));
    }
    if params.get("timeInForce") == Some("GTT") {
        params.required("cancelAfter")?;
    }
    if let Some(v) = params.get("cancelAfter")
        && (params.get("timeInForce") != Some("GTT")
            || !v.parse::<i64>().is_ok_and(|v| v == -1 || v > 0))
    {
        return Err(DcexError::InvalidInput(
            "cancelAfter requires GTT and -1 or a positive integer".into(),
        ));
    }
    // The current official margin Add Order spec explicitly requires funds for
    // autoBorrow buys (including limit buys), and size for sells.
    // https://www.kucoin.com/docs-new/rest/margin-trading/orders/add-order
    if params.get("autoBorrow").and_then(bool_value) == Some(true) {
        params.required(if params.get("side") == Some("buy") {
            "funds"
        } else {
            "size"
        })?;
    }
    if futures {
        if params.get("triggerStopUpPrice").is_none()
            && params.get("triggerStopDownPrice").is_none()
        {
            return Err(DcexError::InvalidInput(
                "at least one TP/SL trigger price is required".into(),
            ));
        }
        params.required("stopPriceType")?;
    }
    Ok(())
}

fn validate_params(params: &KucoinParams, allowed: &[&str]) -> Result<()> {
    params.ensure_allowed(allowed)?;
    for (start, end) in [("startAt", "endAt"), ("from", "to")] {
        if allowed.contains(&start) && allowed.contains(&end) {
            validate_time_range(params, start, end, None)?;
        }
    }
    if allowed.contains(&"clientOid") {
        validate_client_oid(params, "clientOid")?;
    }
    Ok(())
}
