pub(in crate::exchanges::okx) use serde_json::{Map, Value};

pub(in crate::exchanges::okx) use crate::common::OrderSide;
pub(in crate::exchanges::okx) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::okx) use crate::{DcexError, Result};

pub(in crate::exchanges::okx) use super::client::OkxClient;
pub(in crate::exchanges::okx) use super::endpoints::*;
pub(in crate::exchanges::okx) use super::params::{
    OkxParams, insert_optional_bool, insert_optional_string, push_optional, require_one,
};

impl OkxClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_easy_convert_currencies" => {
                params.ensure_allowed(&["source"])?;
                if let Some(source) = params.get("source")
                    && !matches!(source, "1" | "2")
                {
                    return Err(DcexError::InvalidInput(
                        "OKX easy convert source must be 1 or 2".to_string(),
                    ));
                }
                self.get_request(TRADE_EASY_CONVERT_CURRENCIES, params.only(&["source"]))
                    .await
            }
            "get_easy_convert_history" => {
                params.ensure_allowed(&["limit", "after", "before"])?;
                if let Some(limit) = params.get("limit")
                    && !(1..=100).contains(&limit.parse::<u16>().map_err(|_| {
                        DcexError::InvalidInput(
                            "OKX easy convert limit must be an integer".to_string(),
                        )
                    })?)
                {
                    return Err(DcexError::InvalidInput(
                        "OKX easy convert limit must be between 1 and 100".to_string(),
                    ));
                }
                self.get_request(
                    TRADE_EASY_CONVERT_HISTORY,
                    params.only(&["after", "before", "limit"]),
                )
                .await
            }
            "place_easy_convert" => {
                params.ensure_allowed(&["fromCcy", "toCcy", "source"])?;
                let currencies = params.json_required("fromCcy")?;
                if !currencies.as_array().is_some_and(|items| {
                    (1..=5).contains(&items.len())
                        && items.iter().all(|item| {
                            item.as_str()
                                .is_some_and(|currency| !currency.trim().is_empty())
                        })
                }) {
                    return Err(DcexError::InvalidInput(
                        "OKX easy convert fromCcy must contain 1 to 5 currency strings".to_string(),
                    ));
                }
                let to_ccy = params.required("toCcy")?;
                if currencies
                    .as_array()
                    .is_some_and(|items| items.iter().any(|item| item.as_str() == Some(to_ccy)))
                {
                    return Err(DcexError::InvalidInput(
                        "OKX easy convert toCcy must differ from fromCcy".to_string(),
                    ));
                }
                if let Some(source) = params.get("source")
                    && !matches!(source, "1" | "2")
                {
                    return Err(DcexError::InvalidInput(
                        "OKX easy convert source must be 1 or 2".to_string(),
                    ));
                }
                let mut body = params.required_body(&["toCcy"])?;
                body.insert("fromCcy".to_string(), currencies);
                insert_optional_string(&mut body, "source", params.get("source"));
                self.post_request(TRADE_EASY_CONVERT, Value::Object(body))
                    .await
            }
            "place_order" => self.place_order_from_params(params).await,
            "pre_check_order" => self.pre_check_order_from_params(params).await,
            "set_cancel_all_after" => {
                params.ensure_allowed(&["timeOut", "tag"])?;
                let mut body = Map::new();
                body.insert(
                    "timeOut".to_string(),
                    Value::String(params.required("timeOut")?.to_string()),
                );
                insert_optional_string(&mut body, "tag", params.get("tag"));
                self.post_request(TRADE_CANCEL_ALL_AFTER, Value::Object(body))
                    .await
            }
            "place_batch_orders" => self.dispatch_place_batch_orders(method_name, params).await,
            "place_market_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("ordType", "market")],
                )?)
                .await
            }
            "place_market_buy_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "buy"), ("ordType", "market")],
                )?)
                .await
            }
            "place_market_sell_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "sell"), ("ordType", "market")],
                )?)
                .await
            }
            "place_limit_order" => {
                self.place_order_from_params(&forced_order_params(params, &[("ordType", "limit")])?)
                    .await
            }
            "place_limit_buy_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "buy"), ("ordType", "limit")],
                )?)
                .await
            }
            "place_limit_sell_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "sell"), ("ordType", "limit")],
                )?)
                .await
            }
            "place_post_only_limit_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("ordType", "post_only")],
                )?)
                .await
            }
            "place_post_only_limit_buy_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "buy"), ("ordType", "post_only")],
                )?)
                .await
            }
            "place_post_only_limit_sell_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "sell"), ("ordType", "post_only")],
                )?)
                .await
            }
            "cancel_order" => {
                params.ensure_allowed(&["ordId", "clOrdId", "product_symbol"])?;
                self.cancel_order_from_params(params).await
            }
            "cancel_batch_orders" => self.dispatch_cancel_batch_orders(method_name, params).await,
            "cancel_all_orders" => {
                params.ensure_allowed(&["product_symbol", "after", "before", "limit"])?;
                self.cancel_all_orders_from_params(params).await
            }
            "amend_order" => self.amend_order_from_params(params).await,
            "amend_multiple_orders" => {
                params.ensure_allowed(&["orders"])?;
                self.post_request(TRADE_AMEND_BATCH_ORDERS, params.json_required("orders")?)
                    .await
            }
            "close_positions" => {
                params.ensure_allowed(&[
                    "mgnMode",
                    "posSide",
                    "autoCxl",
                    "ccy",
                    "tag",
                    "clOrdId",
                    "product_symbol",
                ])?;
                let mut body = params.required_body(&["mgnMode"])?;
                self.insert_required_inst_id(&mut body, params)?;
                insert_optional_string(&mut body, "posSide", params.get("posSide"));
                insert_optional_bool(&mut body, "autoCxl", params.get("autoCxl"))?;
                insert_optional_string(&mut body, "ccy", params.get("ccy"));
                insert_optional_string(&mut body, "tag", params.get("tag"));
                insert_optional_string(&mut body, "clOrdId", params.get("clOrdId"));
                self.post_request(TRADE_CLOSE_POSITION, Value::Object(body))
                    .await
            }
            "get_order" => {
                params.ensure_allowed(&["ordId", "clOrdId", "product_symbol"])?;
                self.get_order_lookup(TRADE_ORDER, params).await
            }
            "get_order_list" => {
                params.ensure_allowed(&[
                    "instType",
                    "instFamily",
                    "ordType",
                    "state",
                    "after",
                    "before",
                    "limit",
                ])?;
                self.get_order_list_from_params(params).await
            }
            "get_orders_history" => {
                params.ensure_allowed(&[
                    "instType",
                    "instFamily",
                    "ordType",
                    "state",
                    "category",
                    "after",
                    "before",
                    "begin",
                    "end",
                    "limit",
                ])?;
                self.get_order_history_request(TRADE_ORDERS_HISTORY, params, true)
                    .await
            }
            "get_orders_history_archive" => {
                params.ensure_allowed(&[
                    "instType",
                    "instFamily",
                    "ordType",
                    "state",
                    "category",
                    "after",
                    "before",
                    "begin",
                    "end",
                    "limit",
                ])?;
                self.get_order_history_request(TRADE_ORDERS_HISTORY_ARCHIVE, params, true)
                    .await
            }
            "get_fills" => {
                params.ensure_allowed(&[
                    "instType",
                    "instFamily",
                    "ordId",
                    "subType",
                    "after",
                    "before",
                    "begin",
                    "end",
                    "limit",
                ])?;
                self.get_fills_request(TRADE_FILLS, params, false).await
            }
            "get_fills_history" => {
                params.ensure_allowed(&[
                    "instType",
                    "instFamily",
                    "ordId",
                    "subType",
                    "after",
                    "before",
                    "begin",
                    "end",
                    "limit",
                ])?;
                self.get_fills_request(TRADE_FILLS_HISTORY, params, true)
                    .await
            }
            "get_account_rate_limit" => {
                params.ensure_allowed(&[])?;
                self.get_request(TRADE_ACCOUNT_RATE_LIMIT, Vec::new()).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

/// Documented `POST /api/v5/trade/order` fields:
/// <https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order>.
const PLACE_ORDER_KEYS: &[&str] = &[
    "product_symbol",
    "tdMode",
    "side",
    "ordType",
    "sz",
    "ccy",
    "clOrdId",
    "tag",
    "posSide",
    "px",
    "outcome",
    "pxUsd",
    "pxVol",
    "reduceOnly",
    "tgtCcy",
    "banAmend",
    "pxAmendType",
    "tradeQuoteCcy",
    "slippagePct",
    "stpMode",
    "rpiTakerAccess",
    "isElpTakerAccess",
    "rpiPxRound",
    "attachAlgoOrds",
];
/// Documented `POST /api/v5/trade/order-precheck` fields:
/// <https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-order-precheck>.
const PRE_CHECK_ORDER_KEYS: &[&str] = &[
    "product_symbol",
    "tdMode",
    "side",
    "ordType",
    "sz",
    "posSide",
    "px",
    "outcome",
    "reduceOnly",
    "tgtCcy",
    "attachAlgoOrds",
];

/// Rejects undocumented keys and enum values before any request instead of dropping them.
pub(in crate::exchanges::okx) fn validate_order_params(
    params: &OkxParams,
    pre_check: bool,
) -> Result<()> {
    let (allowed, label) = if pre_check {
        (PRE_CHECK_ORDER_KEYS, "order precheck")
    } else {
        (PLACE_ORDER_KEYS, "order")
    };
    ensure_okx_keys(params, allowed, label)?;
    validate_order_enums(params, pre_check)
}

fn ensure_okx_keys(params: &OkxParams, allowed: &[&str], label: &str) -> Result<()> {
    for (key, _) in params.pairs() {
        if !allowed.contains(&key.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported OKX {label} parameter: {key}"
            )));
        }
    }
    Ok(())
}

/// Documented `POST /api/v5/trade/batch-orders` element fields (`isElpTakerAccess` is the
/// documented alias of `rpiTakerAccess`).
const BATCH_ORDER_KEYS: &[&str] = &[
    "instId",
    "tdMode",
    "ccy",
    "clOrdId",
    "tag",
    "side",
    "posSide",
    "ordType",
    "sz",
    "px",
    "speedBump",
    "outcome",
    "pxUsd",
    "pxVol",
    "reduceOnly",
    "tgtCcy",
    "banAmend",
    "pxAmendType",
    "tradeQuoteCcy",
    "slippagePct",
    "stpMode",
    "rpiTakerAccess",
    "isElpTakerAccess",
    "rpiPxRound",
    "attachAlgoOrds",
];

/// Documented `POST /api/v5/trade/amend-order` fields (`instId` comes from `product_symbol`).
const AMEND_ORDER_KEYS: &[&str] = &[
    "product_symbol",
    "cxlOnFail",
    "ordId",
    "clOrdId",
    "reqId",
    "newSz",
    "newPx",
    "speedBump",
    "newPxUsd",
    "newPxVol",
    "pxAmendType",
    "attachAlgoOrds",
    "rpiTakerAccess",
    "rpiPxRound",
];

const ORDER_BOOL_KEYS: &[&str] = &[
    "reduceOnly",
    "banAmend",
    "rpiTakerAccess",
    "isElpTakerAccess",
    "rpiPxRound",
    "cxlOnFail",
];

fn validate_okx_bools(params: &OkxParams) -> Result<()> {
    for key in ORDER_BOOL_KEYS {
        if let Some(value) = params.get(key)
            && !matches!(value, "true" | "false")
        {
            return Err(DcexError::InvalidInput(format!(
                "OKX {key} must be true or false, got {value}"
            )));
        }
    }
    Ok(())
}

/// Converts one JSON batch element into string pairs for the shared validators.
fn json_order_params(order: &Value) -> Result<OkxParams> {
    let order = order.as_object().ok_or_else(|| {
        DcexError::InvalidInput("each OKX batch order must be a JSON object".to_string())
    })?;
    Ok(OkxParams::from_pairs(
        order
            .iter()
            .map(|(key, value)| {
                let value = match value {
                    Value::String(text) => text.clone(),
                    other => other.to_string(),
                };
                (key.clone(), value)
            })
            .collect(),
    ))
}

/// Validates every batch element like a single order; any failure rejects the whole batch.
pub(in crate::exchanges::okx) fn validate_batch_orders(orders: &Value) -> Result<()> {
    let items = orders
        .as_array()
        .ok_or_else(|| DcexError::InvalidInput("OKX orders must be a JSON array".to_string()))?;
    for order in items {
        let params = json_order_params(order)?;
        ensure_okx_keys(&params, BATCH_ORDER_KEYS, "batch order")?;
        validate_order_enums(&params, false)?;
        validate_okx_bools(&params)?;
    }
    validate_batch_order_slippage(orders)
}

fn validate_order_enums(params: &OkxParams, pre_check: bool) -> Result<()> {
    let mut order_types = vec![
        "market",
        "limit",
        "post_only",
        "fok",
        "ioc",
        "optimal_limit_ioc",
        "rpi",
        "elp",
    ];
    if !pre_check {
        order_types.extend(["mmp", "mmp_and_post_only"]);
    }
    for (key, allowed) in [
        ("ordType", order_types.as_slice()),
        (
            "tdMode",
            &["cross", "isolated", "cash", "spot_isolated"][..],
        ),
        (
            "stpMode",
            &["cancel_maker", "cancel_taker", "cancel_both"][..],
        ),
    ] {
        if let Some(value) = params.get(key)
            && !allowed.contains(&value)
        {
            return Err(DcexError::InvalidInput(format!(
                "invalid OKX {key}: {value}; expected one of {}",
                allowed.join(", ")
            )));
        }
    }
    Ok(())
}

/// Applies a convenience method's fixed fields, rejecting a conflicting caller value
/// instead of silently replacing it.
fn forced_order_params(params: &OkxParams, forced: &[(&str, &str)]) -> Result<OkxParams> {
    let keys: Vec<&str> = forced.iter().map(|(key, _)| *key).collect();
    for (key, value) in forced {
        if let Some(existing) = params.get(key)
            && !existing.eq_ignore_ascii_case(value)
        {
            return Err(DcexError::InvalidInput(format!(
                "this OKX order method sets {key}={value}; got conflicting {key}={existing}"
            )));
        }
    }
    let mut pairs = params.without(&keys);
    pairs.extend(
        forced
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string())),
    );
    Ok(OkxParams::from_pairs(pairs))
}

impl OkxClient {
    pub(in crate::exchanges::okx) async fn place_order_from_params(
        &self,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        self.order_validation_request(params, TRADE_ORDER, false)
            .await
    }

    pub(in crate::exchanges::okx) async fn pre_check_order_from_params(
        &self,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        self.order_validation_request(params, TRADE_ORDER_PRECHECK, true)
            .await
    }

    pub(in crate::exchanges::okx) async fn order_validation_request(
        &self,
        params: &OkxParams,
        endpoint: &str,
        pre_check: bool,
    ) -> Result<ValidatedResponse> {
        let body = self.order_body_from_params(params, pre_check)?;
        self.post_request(endpoint, Value::Object(body)).await
    }

    pub(in crate::exchanges::okx) fn order_body_from_params(
        &self,
        params: &OkxParams,
        pre_check: bool,
    ) -> Result<Map<String, Value>> {
        validate_order_params(params, pre_check)?;
        let mut body = params.required_body(&["tdMode", "ordType", "sz"])?;
        self.insert_required_inst_id(&mut body, params)?;
        body.insert(
            "side".to_string(),
            Value::String(
                OrderSide::parse(params.required("side")?)?
                    .to_exchange("okx")?
                    .to_string(),
            ),
        );
        let string_keys: &[&str] = if pre_check {
            &["posSide", "px", "outcome", "tgtCcy"]
        } else {
            &[
                "ccy",
                "clOrdId",
                "posSide",
                "px",
                "outcome",
                "pxUsd",
                "pxVol",
                "tgtCcy",
                "pxAmendType",
                "tradeQuoteCcy",
                "slippagePct",
                "stpMode",
                "tag",
            ]
        };
        for key in string_keys {
            insert_optional_string(&mut body, key, params.get(key));
        }
        insert_optional_bool(&mut body, "reduceOnly", params.get("reduceOnly"))?;
        if !pre_check {
            insert_optional_bool(&mut body, "banAmend", params.get("banAmend"))?;
            insert_optional_bool(
                &mut body,
                "isElpTakerAccess",
                params.get("isElpTakerAccess"),
            )?;
            insert_optional_bool(&mut body, "rpiTakerAccess", params.get("rpiTakerAccess"))?;
            insert_optional_bool(&mut body, "rpiPxRound", params.get("rpiPxRound"))?;
        }
        if let Some(value) = params.json_optional("attachAlgoOrds")? {
            body.insert("attachAlgoOrds".to_string(), value);
        }
        validate_slippage_pct(&body)?;
        Ok(body)
    }

    pub(in crate::exchanges::okx) async fn cancel_order_from_params(
        &self,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        require_one(params, &["ordId", "clOrdId"])?;
        let mut body = Map::new();
        self.insert_required_inst_id(&mut body, params)?;
        insert_optional_string(&mut body, "ordId", params.get("ordId"));
        insert_optional_string(&mut body, "clOrdId", params.get("clOrdId"));
        self.post_request(TRADE_CANCEL_ORDER, Value::Object(body))
            .await
    }

    pub(in crate::exchanges::okx) async fn cancel_all_orders_from_params(
        &self,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        const PAGE_SIZE: usize = 100;
        const CANCEL_BATCH_SIZE: usize = 20;

        let selected_inst_id = params
            .get("product_symbol")
            .map(|symbol| self.exchange_symbol(symbol))
            .transpose()?;
        let mut base_pairs = params.without(&["after", "before", "limit"]);
        base_pairs.push(("limit".to_string(), PAGE_SIZE.to_string()));
        let mut cursor: Option<String> = None;
        let mut cancel_rows = Vec::new();

        let mut response = loop {
            let mut page_pairs = base_pairs.clone();
            if let Some(cursor) = cursor.as_deref() {
                page_pairs.push(("after".to_string(), cursor.to_string()));
            }
            let response = self
                .get_order_list_from_params(&OkxParams::from_pairs(page_pairs))
                .await?;
            let rows = response
                .data
                .get("data")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            let next_cursor = rows
                .last()
                .and_then(Value::as_object)
                .and_then(|order| order.get("ordId"))
                .and_then(Value::as_str)
                .map(str::to_string);

            cancel_rows.extend(
                rows.iter()
                    .filter_map(Value::as_object)
                    .filter(|order| {
                        selected_inst_id.as_ref().is_none_or(|inst_id| {
                            order.get("instId").and_then(Value::as_str) == Some(inst_id.as_str())
                        })
                    })
                    .map(|order| {
                        let mut row = Map::new();
                        for key in ["instId", "ordId", "clOrdId"] {
                            if let Some(value) = order.get(key).and_then(Value::as_str) {
                                row.insert(key.to_string(), Value::String(value.to_string()));
                            }
                        }
                        Value::Object(row)
                    }),
            );

            if rows.len() < PAGE_SIZE || next_cursor.is_none() || next_cursor == cursor {
                break response;
            }
            cursor = next_cursor;
        };

        if cancel_rows.is_empty() {
            return Ok(response);
        }

        let mut cancellation_results = Vec::new();
        for chunk in cancel_rows.chunks(CANCEL_BATCH_SIZE) {
            let batch_response = self
                .post_request(TRADE_CANCEL_BATCH_ORDERS, Value::Array(chunk.to_vec()))
                .await?;
            if let Some(rows) = batch_response.data.get("data").and_then(Value::as_array) {
                cancellation_results.extend(rows.iter().cloned());
            }
            response.status = batch_response.status;
            response.headers = batch_response.headers;
        }
        response.data = serde_json::json!({
            "code": "0",
            "msg": "",
            "data": cancellation_results,
        });
        Ok(response)
    }

    pub(in crate::exchanges::okx) async fn amend_order_from_params(
        &self,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        ensure_okx_keys(params, AMEND_ORDER_KEYS, "amend order")?;
        validate_okx_bools(params)?;
        require_one(params, &["ordId", "clOrdId"])?;
        require_one(
            params,
            &[
                "newSz",
                "newPx",
                "speedBump",
                "newPxUsd",
                "newPxVol",
                "attachAlgoOrds",
                "rpiTakerAccess",
                "rpiPxRound",
            ],
        )?;
        let mut body = Map::new();
        self.insert_required_inst_id(&mut body, params)?;
        for key in [
            "ordId",
            "clOrdId",
            "newSz",
            "newPx",
            "speedBump",
            "newPxUsd",
            "newPxVol",
            "pxAmendType",
            "reqId",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        insert_optional_bool(&mut body, "cxlOnFail", params.get("cxlOnFail"))?;
        insert_optional_bool(&mut body, "rpiTakerAccess", params.get("rpiTakerAccess"))?;
        insert_optional_bool(&mut body, "rpiPxRound", params.get("rpiPxRound"))?;
        if let Some(value) = params.json_optional("attachAlgoOrds")? {
            body.insert("attachAlgoOrds".to_string(), value);
        }
        self.post_request(TRADE_AMEND_ORDER, Value::Object(body))
            .await
    }

    pub(in crate::exchanges::okx) async fn get_order_lookup(
        &self,
        path: &str,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        require_one(params, &["ordId", "clOrdId"])?;
        let mut query = Vec::new();
        self.push_required_inst_id(&mut query, params)?;
        push_optional(&mut query, "ordId", params.get("ordId"));
        push_optional(&mut query, "clOrdId", params.get("clOrdId"));
        self.get_request(path, query).await
    }

    pub(in crate::exchanges::okx) async fn get_order_list_from_params(
        &self,
        params: &OkxParams,
    ) -> Result<ValidatedResponse> {
        let mut query = params.only(&[
            "instType",
            "instFamily",
            "ordType",
            "state",
            "after",
            "before",
            "limit",
        ]);
        self.push_inst_id(&mut query, params, "product_symbol")?;
        self.get_request(TRADE_ORDERS_PENDING, query).await
    }

    pub(in crate::exchanges::okx) async fn get_order_history_request(
        &self,
        path: &str,
        params: &OkxParams,
        require_inst_type: bool,
    ) -> Result<ValidatedResponse> {
        let mut query = if require_inst_type {
            params.required_only(&["instType"])?
        } else {
            Vec::new()
        };
        for key in [
            "instFamily",
            "ordType",
            "state",
            "category",
            "after",
            "before",
            "begin",
            "end",
            "limit",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.push_inst_id(&mut query, params, "product_symbol")?;
        self.get_request(path, query).await
    }

    pub(in crate::exchanges::okx) async fn get_fills_request(
        &self,
        path: &str,
        params: &OkxParams,
        require_inst_type: bool,
    ) -> Result<ValidatedResponse> {
        let mut query = if require_inst_type {
            params.required_only(&["instType"])?
        } else {
            Vec::new()
        };
        for key in [
            "instType",
            "instFamily",
            "ordId",
            "subType",
            "after",
            "before",
            "begin",
            "end",
            "limit",
        ] {
            if !require_inst_type || key != "instType" {
                push_optional(&mut query, key, params.get(key));
            }
        }
        self.push_inst_id(&mut query, params, "product_symbol")?;
        self.get_request(path, query).await
    }
}

pub(in crate::exchanges::okx) fn validate_batch_order_slippage(orders: &Value) -> Result<()> {
    let orders = orders
        .as_array()
        .ok_or_else(|| DcexError::InvalidInput("OKX orders must be a JSON array".to_string()))?;
    for order in orders {
        let order = order.as_object().ok_or_else(|| {
            DcexError::InvalidInput("each OKX batch order must be a JSON object".to_string())
        })?;
        validate_slippage_pct(order)?;
    }
    Ok(())
}

pub(in crate::exchanges::okx) fn validate_slippage_pct(order: &Map<String, Value>) -> Result<()> {
    let Some(value) = order.get("slippagePct") else {
        return Ok(());
    };
    let value = value
        .as_str()
        .ok_or_else(|| DcexError::InvalidInput("OKX slippagePct must be a string".to_string()))?;
    if value.is_empty() {
        return Ok(());
    }
    let mut parts = value.split('.');
    let whole = parts.next().unwrap_or_default();
    let fractional = parts.next();
    if whole.is_empty()
        || !whole.chars().all(|character| character.is_ascii_digit())
        || fractional.is_some_and(|digits| {
            digits.is_empty()
                || digits.len() > 4
                || !digits.chars().all(|character| character.is_ascii_digit())
        })
        || parts.next().is_some()
    {
        return Err(DcexError::InvalidInput(
            "OKX slippagePct must be a decimal with at most four fractional digits".to_string(),
        ));
    }
    let parsed = value
        .parse::<f64>()
        .map_err(|error| DcexError::InvalidInput(format!("invalid OKX slippagePct: {error}")))?;
    if !parsed.is_finite() || !(0.0..=0.05).contains(&parsed) {
        return Err(DcexError::InvalidInput(
            "OKX slippagePct must be between 0 and 0.05 inclusive".to_string(),
        ));
    }
    let inst_id = order
        .get("instId")
        .and_then(Value::as_str)
        .unwrap_or_default();
    if inst_id.split('-').count() != 2
        || order.get("ordType").and_then(Value::as_str) != Some("market")
    {
        return Err(DcexError::InvalidInput(
            "OKX slippagePct is only supported for spot and spot-margin market orders".to_string(),
        ));
    }
    let expected_tgt_ccy = match order.get("side").and_then(Value::as_str) {
        Some("buy") => "base_ccy",
        Some("sell") => "quote_ccy",
        _ => {
            return Err(DcexError::InvalidInput(
                "OKX slippagePct requires side buy or sell".to_string(),
            ));
        }
    };
    if order.get("tgtCcy").and_then(Value::as_str) != Some(expected_tgt_ccy) {
        return Err(DcexError::InvalidInput(format!(
            "OKX slippagePct requires tgtCcy={expected_tgt_ccy} for this side"
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use serde_json::json;

    use super::*;

    pub(in crate::exchanges::okx) fn client() -> OkxClient {
        OkxClient::public(Duration::from_secs(1)).expect("client")
    }

    #[test]
    pub(in crate::exchanges::okx) fn place_order_body_preserves_boolean_and_array_json_types() {
        let params = OkxParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("tdMode".to_string(), "cross".to_string()),
            ("side".to_string(), "buy".to_string()),
            ("ordType".to_string(), "limit".to_string()),
            ("sz".to_string(), "1".to_string()),
            ("reduceOnly".to_string(), "true".to_string()),
            ("banAmend".to_string(), "false".to_string()),
            ("isElpTakerAccess".to_string(), "true".to_string()),
            ("rpiTakerAccess".to_string(), "true".to_string()),
            ("rpiPxRound".to_string(), "true".to_string()),
            (
                "attachAlgoOrds".to_string(),
                r#"[{"tpTriggerPx":"110","tpOrdPx":"109"}]"#.to_string(),
            ),
        ]);

        let body = client()
            .order_body_from_params(&params, false)
            .expect("body");
        assert_eq!(body["reduceOnly"], Value::Bool(true));
        assert_eq!(body["banAmend"], Value::Bool(false));
        assert_eq!(body["isElpTakerAccess"], Value::Bool(true));
        assert_eq!(body["rpiTakerAccess"], Value::Bool(true));
        assert_eq!(body["rpiPxRound"], Value::Bool(true));
        assert_eq!(
            body["attachAlgoOrds"],
            json!([{"tpTriggerPx": "110", "tpOrdPx": "109"}])
        );
    }

    #[test]
    pub(in crate::exchanges::okx) fn easy_convert_rejects_more_than_five_currencies_before_network()
    {
        let params = OkxParams::from_pairs(vec![
            ("fromCcy".into(), r#"["A","B","C","D","E","F"]"#.into()),
            ("toCcy".into(), "USDT".into()),
        ]);
        let error = crate::http::block_on(async move {
            client()
                .trade_private_request("place_easy_convert", &params)
                .await
        })
        .expect_err("too many currencies");
        assert!(error.to_string().contains("1 to 5"));
    }

    #[test]
    pub(in crate::exchanges::okx) fn precheck_body_drops_place_only_fields() {
        let params = OkxParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("tdMode".to_string(), "cross".to_string()),
            ("side".to_string(), "buy".to_string()),
            ("ordType".to_string(), "limit".to_string()),
            ("sz".to_string(), "1".to_string()),
            ("px".to_string(), "100".to_string()),
            ("outcome".to_string(), "yes".to_string()),
        ]);

        let body = client()
            .order_body_from_params(&params, true)
            .expect("body");
        assert_eq!(body["outcome"], "yes");

        for (key, value) in [("clOrdId", "x"), ("stpMode", "cancel_maker")] {
            let mut pairs = vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("tdMode".to_string(), "cross".to_string()),
                ("side".to_string(), "buy".to_string()),
                ("ordType".to_string(), "limit".to_string()),
                ("sz".to_string(), "1".to_string()),
            ];
            pairs.push((key.to_string(), value.to_string()));
            let error = client()
                .order_body_from_params(&OkxParams::from_pairs(pairs), true)
                .expect_err("place-only field must be rejected by precheck");
            assert!(error.to_string().contains(key), "{error}");
        }
    }

    #[test]
    pub(in crate::exchanges::okx) fn place_order_rejects_undocumented_keys_and_enums() {
        let base = || {
            vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("tdMode".to_string(), "cross".to_string()),
                ("side".to_string(), "buy".to_string()),
                ("ordType".to_string(), "limit".to_string()),
                ("sz".to_string(), "1".to_string()),
                ("px".to_string(), "100".to_string()),
            ]
        };
        let mut valid = base();
        valid.push(("clOrdId".to_string(), "abc1".to_string()));
        valid.push(("stpMode".to_string(), "cancel_both".to_string()));
        let body = client()
            .order_body_from_params(&OkxParams::from_pairs(valid), false)
            .expect("documented fields");
        assert_eq!(body["clOrdId"], "abc1");
        assert_eq!(body["stpMode"], "cancel_both");
        for ord_type in [
            "market",
            "post_only",
            "fok",
            "ioc",
            "optimal_limit_ioc",
            "mmp",
            "mmp_and_post_only",
            "rpi",
        ] {
            let mut pairs = base();
            pairs[3].1 = ord_type.to_string();
            client()
                .order_body_from_params(&OkxParams::from_pairs(pairs), false)
                .expect("documented ordType");
        }
        for (key, value) in [
            ("speedBump", "1"),
            ("timeInForce", "GTC"),
            ("ordType", "LIMIT"),
            ("ordType", "gtd"),
            ("tdMode", "margin"),
            ("stpMode", "none"),
            ("reduceOnly", "yes"),
        ] {
            let mut pairs: Vec<_> = base().into_iter().filter(|(k, _)| k != key).collect();
            pairs.push((key.to_string(), value.to_string()));
            assert!(
                client()
                    .order_body_from_params(&OkxParams::from_pairs(pairs), false)
                    .is_err(),
                "{key}={value} must be rejected"
            );
        }
    }

    #[test]
    pub(in crate::exchanges::okx) fn batch_orders_are_validated_per_element() {
        let valid = json!([
            {"instId": "BTC-USDT", "tdMode": "cash", "side": "buy", "ordType": "post_only",
             "sz": "1", "px": "100", "clOrdId": "a1", "stpMode": "cancel_maker",
             "reduceOnly": false, "speedBump": "1",
             "attachAlgoOrds": [{"tpTriggerPx": "110", "tpOrdPx": "-1"}]}
        ]);
        validate_batch_orders(&valid).expect("documented batch element");
        for bad in [
            json!([{"instId": "BTC-USDT", "ordType": "limit", "timeInForce": "GTC"}]),
            json!([{"instId": "BTC-USDT", "ordType": "gtc"}]),
            json!([{"instId": "BTC-USDT", "tdMode": "margin"}]),
            json!([{"instId": "BTC-USDT", "reduceOnly": "yes"}]),
            json!([{"instId": "BTC-USDT", "ordType": "limit"}, {"product_symbol": "x"}]),
            json!(["not-an-object"]),
        ] {
            assert!(validate_batch_orders(&bad).is_err(), "{bad}");
        }
    }

    #[tokio::test]
    pub(in crate::exchanges::okx) async fn amend_rejects_undocumented_keys_before_network() {
        for (key, value) in [("newOrdType", "limit"), ("cxlOnFail", "yes")] {
            let params = OkxParams::from_pairs(vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("ordId".to_string(), "1".to_string()),
                ("newSz".to_string(), "2".to_string()),
                (key.to_string(), value.to_string()),
            ]);
            let error = client()
                .amend_order_from_params(&params)
                .await
                .expect_err("must fail before network");
            assert!(error.to_string().contains(key), "{error}");
        }
    }

    #[test]
    pub(in crate::exchanges::okx) fn convenience_order_rejects_conflicting_ord_type() {
        let params = OkxParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("ordType".to_string(), "ioc".to_string()),
        ]);
        let error = forced_order_params(&params, &[("ordType", "post_only")])
            .err()
            .expect("conflict");
        assert!(error.to_string().contains("conflicting"));
    }
}
