//! Additional order lifecycle and risk controls from the Binance REST API.
use super::client::{BinanceClient, BinanceMarket};
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

crate::exchanges::impl_exchange_method_wrappers! {
    @extend; BinanceClient;
    public [];
    private [
        /// Submit raw COIN-M algo fields. The official migration note names the route,
        /// but its standalone parameter/signing examples are not yet published.
        place_coin_futures_algo_order(fields => "fields"),
        /// Cancel a COIN-M algo order using caller-provided exchange fields; not verified live.
        cancel_coin_futures_algo_order(fields => "fields"),
        /// Query a COIN-M algo order using caller-provided exchange fields; not verified live.
        get_coin_futures_algo_order(fields => "fields"),
        create_coin_futures_listen_key(),
        keep_alive_coin_futures_listen_key(),
        close_coin_futures_listen_key(),
        create_pm_listen_key(),
        keep_alive_pm_listen_key(),
        close_pm_listen_key(),
        cancel_replace_spot_order(product_symbol => "product_symbol", side => "side", order_type => "type", cancel_replace_mode => "cancelReplaceMode"),






        get_spot_order_list(),
        get_spot_all_order_lists(),
        get_spot_open_order_lists(),
        cancel_spot_order_list(product_symbol => "product_symbol"),
        amend_spot_order_keep_priority(product_symbol => "product_symbol", new_quantity => "newQty"),
        get_futures_position_mode(),
        set_futures_position_mode(dual_side_position => "dualSidePosition"),
        set_futures_margin_type(product_symbol => "product_symbol", margin_type => "marginType"),
        set_futures_cancel_countdown(product_symbol => "product_symbol", countdown_time => "countdownTime"),
        get_futures_leverage_brackets(),
        amend_futures_order(product_symbol => "product_symbol", side => "side", quantity => "quantity"),
        get_coin_futures_position_mode(),
        set_coin_futures_position_mode(dual_side_position => "dualSidePosition"),
        set_coin_futures_margin_type(product_symbol => "product_symbol", margin_type => "marginType"),
        set_coin_futures_cancel_countdown(product_symbol => "product_symbol", countdown_time => "countdownTime"),
        get_coin_futures_leverage_brackets(),
        amend_coin_futures_order(symbol => "symbol", side => "side", quantity => "quantity"),
        set_coin_futures_leverage(product_symbol => "product_symbol", leverage => "leverage"),
        get_coin_futures_pair_leverage_brackets(),
        get_coin_futures_all_orders(),
        get_coin_futures_account_trades(),
    ];
}

impl BinanceClient {
    pub(super) async fn trading_controls_private_request(
        &self,
        name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        if matches!(
            name,
            "place_coin_futures_algo_order"
                | "cancel_coin_futures_algo_order"
                | "get_coin_futures_algo_order"
        ) {
            params.ensure_allowed(&["fields"])?;
            let fields: serde_json::Map<String, serde_json::Value> =
                serde_json::from_str(params.required("fields")?)
                    .map_err(|e| DcexError::InvalidInput(e.to_string()))?;
            crate::exchanges::schema::validate_numbers(
                &serde_json::Value::Object(fields.clone()),
                "fields",
            )?;
            if fields.is_empty()
                || fields
                    .keys()
                    .any(|key| matches!(key.as_str(), "timestamp" | "signature" | "apiKey"))
            {
                return Err(DcexError::InvalidInput(
                    "provide nonempty algo fields without authentication fields".into(),
                ));
            }
            if let Some(symbol) = fields.get("symbol") {
                self.batch_symbol(None, symbol.as_str(), BinanceMarket::CoinFutures)?;
            }
            let pairs = fields
                .into_iter()
                .map(|(key, value)| {
                    let value = match value {
                        serde_json::Value::String(value) => value,
                        serde_json::Value::Number(value) => value.to_string(),
                        serde_json::Value::Bool(value) => value.to_string(),
                        _ => {
                            return Err(DcexError::InvalidInput(
                                "algo fields must be scalar exchange parameters".into(),
                            ));
                        }
                    };
                    Ok((key, value))
                })
                .collect::<Result<Vec<_>>>()?;
            let verb = match name {
                "place_coin_futures_algo_order" => HttpMethod::Post,
                "cancel_coin_futures_algo_order" => HttpMethod::Delete,
                _ => HttpMethod::Get,
            };
            return self
                .request(
                    verb,
                    BinanceMarket::CoinFutures,
                    "/dapi/v1/algoOrder",
                    pairs,
                    true,
                )
                .await
                .map(Some);
        }
        let normalized;
        let params = if name.contains("coin_futures") && params.get("product_symbol").is_some() {
            if params.get("symbol").is_some() {
                return Err(DcexError::InvalidInput(
                    "use product_symbol or symbol, exclusively".into(),
                ));
            }
            let product = params.required("product_symbol")?;
            let symbol = if product.contains('-') {
                if self.market_for_product_symbol(product)? != BinanceMarket::CoinFutures {
                    return Err(DcexError::InvalidInput(
                        "product_symbol does not match COIN-M".into(),
                    ));
                }
                self.exchange_symbol(product)?
            } else {
                self.batch_symbol(None, Some(product), BinanceMarket::CoinFutures)?
            };
            let mut pairs = params.without(&["product_symbol"]);
            pairs.push(("symbol".into(), symbol));
            normalized = PublicParams(pairs);
            &normalized
        } else {
            params
        };
        let (market, method, path, allowed, required, rule): (
            BinanceMarket,
            HttpMethod,
            &str,
            &[&str],
            &[&str],
            &str,
        ) = match name {
            "cancel_replace_spot_order" => (
                BinanceMarket::Spot,
                HttpMethod::Post,
                "/api/v3/order/cancelReplace",
                &[
                    "product_symbol",
                    "side",
                    "type",
                    "cancelReplaceMode",
                    "timeInForce",
                    "quantity",
                    "quoteOrderQty",
                    "price",
                    "cancelNewClientOrderId",
                    "cancelOrigClientOrderId",
                    "cancelOrderId",
                    "newClientOrderId",
                    "strategyId",
                    "strategyType",
                    "stopPrice",
                    "trailingDelta",
                    "icebergQty",
                    "newOrderRespType",
                    "selfTradePreventionMode",
                    "cancelRestrictions",
                    "orderRateLimitExceededMode",
                    "pegPriceType",
                    "pegOffsetValue",
                    "pegOffsetType",
                    "recvWindow",
                ],
                &["product_symbol", "side", "type", "cancelReplaceMode"],
                "cancel_replace",
            ),
            "create_coin_futures_listen_key" => {
                params.ensure_allowed(&[])?;
                return Ok(Some(
                    self.api_key_request(
                        HttpMethod::Post,
                        BinanceMarket::CoinFutures,
                        "/dapi/v1/listenKey",
                        Vec::new(),
                    )
                    .await?,
                ));
            }
            "keep_alive_coin_futures_listen_key" => {
                params.ensure_allowed(&[])?;
                return Ok(Some(
                    self.api_key_request(
                        HttpMethod::Put,
                        BinanceMarket::CoinFutures,
                        "/dapi/v1/listenKey",
                        Vec::new(),
                    )
                    .await?,
                ));
            }
            "close_coin_futures_listen_key" => {
                params.ensure_allowed(&[])?;
                return Ok(Some(
                    self.api_key_request(
                        HttpMethod::Delete,
                        BinanceMarket::CoinFutures,
                        "/dapi/v1/listenKey",
                        Vec::new(),
                    )
                    .await?,
                ));
            }
            "create_pm_listen_key" => {
                params.ensure_allowed(&[])?;
                return Ok(Some(
                    self.api_key_request(
                        HttpMethod::Post,
                        BinanceMarket::PortfolioMargin,
                        "/papi/v1/listenKey",
                        Vec::new(),
                    )
                    .await?,
                ));
            }
            "keep_alive_pm_listen_key" => {
                params.ensure_allowed(&[])?;
                return Ok(Some(
                    self.api_key_request(
                        HttpMethod::Put,
                        BinanceMarket::PortfolioMargin,
                        "/papi/v1/listenKey",
                        Vec::new(),
                    )
                    .await?,
                ));
            }
            "close_pm_listen_key" => {
                params.ensure_allowed(&[])?;
                return Ok(Some(
                    self.api_key_request(
                        HttpMethod::Delete,
                        BinanceMarket::PortfolioMargin,
                        "/papi/v1/listenKey",
                        Vec::new(),
                    )
                    .await?,
                ));
            }
            "get_spot_order_list" => (
                BinanceMarket::Spot,
                HttpMethod::Get,
                "/api/v3/orderList",
                &["orderListId", "origClientOrderId", "recvWindow"],
                &[],
                "list_lookup",
            ),
            "get_spot_all_order_lists" => (
                BinanceMarket::Spot,
                HttpMethod::Get,
                "/api/v3/allOrderList",
                &["fromId", "startTime", "endTime", "limit", "recvWindow"],
                &[],
                "spot_history",
            ),
            "get_spot_open_order_lists" => (
                BinanceMarket::Spot,
                HttpMethod::Get,
                "/api/v3/openOrderList",
                &["recvWindow"],
                &[],
                "none",
            ),
            "cancel_spot_order_list" => (
                BinanceMarket::Spot,
                HttpMethod::Delete,
                "/api/v3/orderList",
                &[
                    "product_symbol",
                    "orderListId",
                    "listClientOrderId",
                    "newClientOrderId",
                    "recvWindow",
                ],
                &["product_symbol"],
                "cancel_list",
            ),
            "amend_spot_order_keep_priority" => (
                BinanceMarket::Spot,
                HttpMethod::Put,
                "/api/v3/order/amend/keepPriority",
                &[
                    "product_symbol",
                    "newQty",
                    "orderId",
                    "origClientOrderId",
                    "newClientOrderId",
                    "recvWindow",
                ],
                &["product_symbol", "newQty"],
                "amend_spot",
            ),
            "get_futures_position_mode" => (
                BinanceMarket::Futures,
                HttpMethod::Get,
                "/fapi/v1/positionSide/dual",
                &["recvWindow"],
                &[],
                "none",
            ),
            "set_futures_position_mode" => (
                BinanceMarket::Futures,
                HttpMethod::Post,
                "/fapi/v1/positionSide/dual",
                &["dualSidePosition", "recvWindow"],
                &["dualSidePosition"],
                "mode",
            ),
            "set_futures_margin_type" => (
                BinanceMarket::Futures,
                HttpMethod::Post,
                "/fapi/v1/marginType",
                &["product_symbol", "marginType", "recvWindow"],
                &["product_symbol", "marginType"],
                "margin_type",
            ),
            "set_futures_cancel_countdown" => (
                BinanceMarket::Futures,
                HttpMethod::Post,
                "/fapi/v1/countdownCancelAll",
                &["product_symbol", "countdownTime", "recvWindow"],
                &["product_symbol", "countdownTime"],
                "countdown",
            ),
            "get_futures_leverage_brackets" => (
                BinanceMarket::Futures,
                HttpMethod::Get,
                "/fapi/v1/leverageBracket",
                &["product_symbol", "recvWindow"],
                &[],
                "none",
            ),
            "amend_futures_order" => (
                BinanceMarket::Futures,
                HttpMethod::Put,
                "/fapi/v1/order",
                &[
                    "product_symbol",
                    "side",
                    "quantity",
                    "price",
                    "priceMatch",
                    "orderId",
                    "origClientOrderId",
                    "modifyId",
                    "reduceOnly",
                    "recvWindow",
                ],
                &["product_symbol", "side", "quantity"],
                "amend_futures",
            ),
            "get_coin_futures_position_mode" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Get,
                "/dapi/v1/positionSide/dual",
                &["recvWindow"],
                &[],
                "none",
            ),
            "set_coin_futures_position_mode" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Post,
                "/dapi/v1/positionSide/dual",
                &["dualSidePosition", "recvWindow"],
                &["dualSidePosition"],
                "mode",
            ),
            "set_coin_futures_margin_type" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Post,
                "/dapi/v1/marginType",
                &["symbol", "marginType", "recvWindow"],
                &["symbol", "marginType"],
                "margin_type",
            ),
            "set_coin_futures_cancel_countdown" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Post,
                "/dapi/v1/countdownCancelAll",
                &["symbol", "countdownTime", "recvWindow"],
                &["symbol", "countdownTime"],
                "countdown",
            ),
            "get_coin_futures_leverage_brackets" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Get,
                "/dapi/v2/leverageBracket",
                &["symbol", "recvWindow"],
                &[],
                "none",
            ),
            "amend_coin_futures_order" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Put,
                "/dapi/v1/order",
                &[
                    "symbol",
                    "side",
                    "quantity",
                    "price",
                    "priceMatch",
                    "orderId",
                    "origClientOrderId",
                    "modifyId",
                    "recvWindow",
                ],
                &["symbol", "side", "quantity"],
                "amend_futures",
            ),
            "set_coin_futures_leverage" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Post,
                "/dapi/v1/leverage",
                &["symbol", "leverage", "recvWindow"],
                &["symbol", "leverage"],
                "leverage",
            ),
            "get_coin_futures_pair_leverage_brackets" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Get,
                "/dapi/v1/leverageBracket",
                &["pair", "recvWindow"],
                &[],
                "none",
            ),
            "get_coin_futures_all_orders" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Get,
                "/dapi/v1/allOrders",
                &[
                    "symbol",
                    "pair",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ],
                &[],
                "coin_history",
            ),
            "get_coin_futures_account_trades" => (
                BinanceMarket::CoinFutures,
                HttpMethod::Get,
                "/dapi/v1/userTrades",
                &[
                    "symbol",
                    "pair",
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                    "recvWindow",
                ],
                &[],
                "coin_trades",
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(allowed)?;
        for key in required {
            params.required(key)?;
        }
        if matches!(market, BinanceMarket::Spot) {
            if let Some(value) = params.get("recvWindow") {
                let valid = value
                    .parse::<f64>()
                    .is_ok_and(|v| v.is_finite() && v > 0.0 && v <= 60_000.0)
                    && value.chars().all(|c| c.is_ascii_digit() || c == '.')
                    && value
                        .split_once('.')
                        .is_none_or(|(_, fraction)| fraction.len() <= 3);
                if !valid {
                    return Err(DcexError::InvalidInput(
                        "recvWindow must be positive, at most 60000, with at most 3 decimals"
                            .into(),
                    ));
                }
            }
        } else {
            params.optional_u64_range("recvWindow", 1, 60_000)?;
        }
        for key in ["orderId", "orderListId", "fromId", "modifyId"] {
            params.u64(key)?;
        }
        params.ensure_time_order("startTime", "endTime")?;
        params.optional_u64_range("limit", 1, 1000)?;
        match rule {
            "cancel_replace" => validate_cancel_replace(params)?,
            "list_lookup" => require_identifier(params, "orderListId", "origClientOrderId")?,
            "cancel_list" => require_identifier(params, "orderListId", "listClientOrderId")?,
            "amend_spot" => {
                require_identifier(params, "orderId", "origClientOrderId")?;
                positive(params, "newQty")?;
            }
            "amend_futures" => {
                require_identifier(params, "orderId", "origClientOrderId")?;
                params.optional_one_of("side", &["BUY", "SELL"])?;
                positive(params, "quantity")?;
                if params.get("price").is_some() == params.get("priceMatch").is_some() {
                    return Err(DcexError::InvalidInput(
                        "provide price or priceMatch, exclusively".into(),
                    ));
                }
                if params.get("price").is_some() {
                    positive(params, "price")?;
                }
                params.optional_one_of(
                    "priceMatch",
                    &[
                        "OPPONENT",
                        "OPPONENT_5",
                        "OPPONENT_10",
                        "OPPONENT_20",
                        "QUEUE",
                        "QUEUE_5",
                        "QUEUE_10",
                        "QUEUE_20",
                    ],
                )?;
                params.optional_one_of("reduceOnly", &["true", "false"])?;
            }
            "mode" => params.optional_one_of("dualSidePosition", &["true", "false"])?,
            "margin_type" => params.optional_one_of("marginType", &["ISOLATED", "CROSSED"])?,
            "countdown" => {
                params.u64("countdownTime")?;
            }
            "leverage" => params.optional_u64_range("leverage", 1, 125)?,
            "spot_history" | "coin_history" | "coin_trades" => {
                if params.get("fromId").is_some()
                    && (params.get("startTime").is_some() || params.get("endTime").is_some())
                {
                    return Err(DcexError::InvalidInput(
                        "fromId cannot be combined with startTime or endTime".into(),
                    ));
                }
                if rule != "spot_history" {
                    require_identifier(params, "symbol", "pair")?;
                    if params.get("symbol").is_some() && params.get("pair").is_some() {
                        return Err(DcexError::InvalidInput(
                            "symbol and pair cannot be sent together".into(),
                        ));
                    }
                    if (params.get("orderId").is_some() || params.get("fromId").is_some())
                        && params.get("symbol").is_none()
                    {
                        return Err(DcexError::InvalidInput(
                            "orderId and fromId require symbol".into(),
                        ));
                    }
                }
                if let (Some(start), Some(end)) = (params.u64("startTime")?, params.u64("endTime")?)
                {
                    let max = if rule == "spot_history" {
                        86_400_000
                    } else {
                        7 * 86_400_000
                    };
                    if end - start > max {
                        return Err(DcexError::InvalidInput(
                            "query time range exceeds the endpoint limit".into(),
                        ));
                    }
                }
            }
            _ => {}
        }
        let mut query = params.without(&["product_symbol"]);
        if let Some(symbol) = params.get("product_symbol") {
            let actual = self.market_for_product_symbol(symbol)?;
            if actual != market {
                return Err(DcexError::InvalidInput(
                    "product_symbol does not match the endpoint market".into(),
                ));
            }
            query.push(("symbol".into(), self.exchange_symbol(symbol)?));
        }
        if matches!(market, BinanceMarket::CoinFutures)
            && let Some(symbol) = params.get("symbol")
            && !symbol
                .chars()
                .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == '_')
        {
            return Err(DcexError::InvalidInput(
                "COIN-M endpoints require a native symbol such as BTCUSD_PERP".into(),
            ));
        }
        Ok(Some(self.request(method, market, path, query, true).await?))
    }
}

fn require_identifier(params: &PublicParams, first: &str, second: &str) -> Result<()> {
    if params.get(first).is_none() && params.get(second).is_none() {
        return Err(DcexError::InvalidInput(format!(
            "{first} or {second} is required"
        )));
    }
    Ok(())
}
fn positive(params: &PublicParams, key: &str) -> Result<()> {
    if !params
        .required(key)?
        .parse::<f64>()
        .is_ok_and(|v| v.is_finite() && v > 0.0)
    {
        return Err(DcexError::InvalidInput(format!("{key} must be positive")));
    }
    Ok(())
}

fn validate_cancel_replace(params: &PublicParams) -> Result<()> {
    require_identifier(params, "cancelOrderId", "cancelOrigClientOrderId")?;
    params.u64("cancelOrderId")?;
    params.optional_one_of("side", &["BUY", "SELL"])?;
    params.optional_one_of(
        "type",
        &[
            "LIMIT",
            "MARKET",
            "STOP_LOSS",
            "STOP_LOSS_LIMIT",
            "TAKE_PROFIT",
            "TAKE_PROFIT_LIMIT",
            "LIMIT_MAKER",
        ],
    )?;
    params.optional_one_of("cancelReplaceMode", &["STOP_ON_FAILURE", "ALLOW_FAILURE"])?;
    params.optional_one_of("cancelRestrictions", &["ONLY_NEW", "ONLY_PARTIALLY_FILLED"])?;
    params.optional_one_of("orderRateLimitExceededMode", &["DO_NOTHING", "CANCEL_ONLY"])?;
    params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK"])?;
    params.optional_one_of("newOrderRespType", &["ACK", "RESULT", "FULL"])?;
    params.optional_one_of("pegPriceType", &["PRIMARY_PEG", "MARKET_PEG"])?;
    params.optional_one_of("pegOffsetType", &["PRICE_LEVEL"])?;
    params.optional_u64_range("pegOffsetValue", 0, 100)?;
    params.optional_u64_range("strategyType", 1_000_000, u64::MAX)?;
    params.u64("strategyId")?;
    params.u64("trailingDelta")?;
    for k in [
        "quantity",
        "quoteOrderQty",
        "price",
        "stopPrice",
        "icebergQty",
    ] {
        if params.get(k).is_some() {
            positive(params, k)?;
        }
    }
    let kind = params.required("type")?;
    if kind == "MARKET" {
        if params.get("quantity").is_some() == params.get("quoteOrderQty").is_some() {
            return Err(DcexError::InvalidInput(
                "MARKET requires exactly one of quantity and quoteOrderQty".into(),
            ));
        }
    } else {
        params.required("quantity")?;
        if params.get("quoteOrderQty").is_some() {
            return Err(DcexError::InvalidInput(
                "quoteOrderQty requires MARKET".into(),
            ));
        }
    }
    if matches!(
        kind,
        "LIMIT" | "LIMIT_MAKER" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT_LIMIT"
    ) {
        if params.get("pegPriceType").is_none() {
            params.required("price")?;
        }
        if kind != "LIMIT_MAKER" {
            params.required("timeInForce")?;
        }
    } else if params.get("pegPriceType").is_some()
        || params.get("price").is_some()
        || params.get("timeInForce").is_some()
    {
        return Err(DcexError::InvalidInput(
            "limit fields require a limit order type".into(),
        ));
    }
    if matches!(
        kind,
        "STOP_LOSS" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT" | "TAKE_PROFIT_LIMIT"
    ) {
        require_identifier(params, "stopPrice", "trailingDelta")?;
    } else if params.get("stopPrice").is_some() || params.get("trailingDelta").is_some() {
        return Err(DcexError::InvalidInput(
            "trigger fields require a conditional order type".into(),
        ));
    }
    if params.get("icebergQty").is_some() && params.get("timeInForce") != Some("GTC") {
        return Err(DcexError::InvalidInput("icebergQty requires GTC".into()));
    }
    if params.get("pegOffsetValue").is_some() != params.get("pegOffsetType").is_some()
        || ((params.get("pegOffsetValue").is_some() || params.get("pegOffsetType").is_some())
            && params.get("pegPriceType").is_none())
    {
        return Err(DcexError::InvalidInput(
            "peg offsets require pegPriceType and both offset fields".into(),
        ));
    }
    Ok(())
}
