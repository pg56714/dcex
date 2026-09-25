use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{PublicParams, normalize_order_side};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub fn get_options_exchange_info(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_exchange_info",
            Vec::new(),
        )
    }

    pub fn get_options_index_price(
        &self,
        underlying: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_index_price",
            vec![("underlying".to_string(), underlying.to_string())],
        )
    }

    pub fn get_options_exercise_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_exercise_history",
            Vec::new(),
        )
    }

    pub fn get_options_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_klines",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("interval".to_string(), interval.to_string()),
            ],
        )
    }

    pub fn get_options_open_interest(
        &self,
        underlying_asset: &str,
        expiration: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_open_interest",
            vec![
                ("underlyingAsset".to_string(), underlying_asset.to_string()),
                ("expiration".to_string(), expiration.to_string()),
            ],
        )
    }

    pub fn get_options_mark_price(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_options_mark_price", Vec::new())
    }

    pub fn get_options_orderbook(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_orderbook",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_options_block_trades(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_block_trades",
            Vec::new(),
        )
    }

    pub fn get_options_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_options_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn ping_options(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "ping_options", Vec::new())
    }

    pub fn get_options_ticker(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_options_ticker", Vec::new())
    }

    pub fn place_options_order(
        &self,
        product_symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_options_order",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("side".to_string(), side.to_string()),
                ("type".to_string(), "LIMIT".to_string()),
                ("quantity".to_string(), quantity.to_string()),
                ("price".to_string(), price.to_string()),
                ("timeInForce".to_string(), "GTC".to_string()),
            ],
        )
    }

    pub fn get_options_account_bill(
        &self,
        currency: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_options_account_bill",
            vec![("currency".to_string(), currency.to_string())],
        )
    }

    pub fn get_options_margin_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_options_margin_account",
            Vec::new(),
        )
    }

    pub fn get_options_account_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_options_account_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn cancel_all_options_orders_by_underlying(
        &self,
        underlying: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_all_options_orders_by_underlying",
            vec![("underlying".to_string(), underlying.to_string())],
        )
    }

    pub fn cancel_all_options_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_all_options_orders",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn place_options_batch_orders(
        &self,
        orders: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_options_batch_orders",
            vec![("orders".to_string(), orders.to_string())],
        )
    }

    pub fn cancel_options_batch_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_options_batch_orders",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_options_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_options_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn cancel_options_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_options_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_options_positions(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_options_positions", Vec::new())
    }

    pub fn get_open_options_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_open_options_orders",
            Vec::new(),
        )
    }

    pub fn get_options_order_history(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_options_order_history",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_options_commission(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_options_commission", Vec::new())
    }

    pub fn get_options_exercise_records(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_options_exercise_records",
            Vec::new(),
        )
    }

    pub fn create_options_listen_key(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "create_options_listen_key",
            Vec::new(),
        )
    }

    pub fn keep_alive_options_listen_key(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "keep_alive_options_listen_key",
            Vec::new(),
        )
    }

    pub fn close_options_listen_key(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "close_options_listen_key",
            Vec::new(),
        )
    }

    pub(super) async fn options_public_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, query) = match method_name {
            "get_options_exchange_info" => {
                params.ensure_allowed(&[])?;
                (OPTIONS_EXCHANGE_INFO, Vec::new())
            }
            "get_options_exercise_history" => {
                params.ensure_allowed(&["underlying", "startTime", "endTime", "limit"])?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("limit", 1, 100)?;
                (OPTIONS_EXERCISE_HISTORY, params.without(&[]))
            }
            "get_options_index_price" => {
                params.ensure_allowed(&["underlying"])?;
                params.required("underlying")?;
                (OPTIONS_INDEX_PRICE, params.without(&[]))
            }
            "get_options_klines" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "interval",
                    "startTime",
                    "endTime",
                    "limit",
                ])?;
                params.required("product_symbol")?;
                params.required("interval")?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("limit", 1, 1500)?;
                (OPTIONS_KLINES, options_symbol_query(params, &[]))
            }
            "get_options_open_interest" => {
                params.ensure_allowed(&["underlyingAsset", "expiration"])?;
                params.required("underlyingAsset")?;
                params.required("expiration")?;
                (OPTIONS_OPEN_INTEREST, params.without(&[]))
            }
            "get_options_mark_price" => {
                params.ensure_allowed(&["product_symbol"])?;
                (OPTIONS_MARK_PRICE, options_symbol_query(params, &[]))
            }
            "get_options_orderbook" => {
                params.ensure_allowed(&["product_symbol", "limit"])?;
                params.required("product_symbol")?;
                params.optional_u64_range("limit", 1, 1000)?;
                (OPTIONS_ORDERBOOK, options_symbol_query(params, &[]))
            }
            "get_options_block_trades" => {
                params.ensure_allowed(&[])?;
                (OPTIONS_BLOCK_TRADES, Vec::new())
            }
            "get_options_trades" => {
                params.ensure_allowed(&["product_symbol", "limit"])?;
                params.required("product_symbol")?;
                params.optional_u64_range("limit", 1, 1000)?;
                (OPTIONS_TRADES, options_symbol_query(params, &[]))
            }
            "ping_options" => {
                params.ensure_allowed(&[])?;
                (OPTIONS_PING, Vec::new())
            }
            "get_options_ticker" => {
                params.ensure_allowed(&["product_symbol"])?;
                (OPTIONS_TICKER, options_symbol_query(params, &[]))
            }
            _ => return Ok(None),
        };
        Ok(Some(
            self.request(HttpMethod::Get, BinanceMarket::Options, path, query, false)
                .await?,
        ))
    }

    pub(super) async fn options_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_options_account_bill" => {
                params.ensure_allowed(&[
                    "currency",
                    "recordId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                params.required("currency")?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("limit", 1, 1000)?;
                self.options_signed_request(HttpMethod::Get, OPTIONS_ACCOUNT_BILL, params, &[])
                    .await
            }
            "get_options_margin_account" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.options_signed_request(HttpMethod::Get, OPTIONS_MARGIN_ACCOUNT, params, &[])
                    .await
            }
            "get_options_account_trades" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "fromId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                params.required("product_symbol")?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("limit", 1, 1000)?;
                self.options_signed_request(
                    HttpMethod::Get,
                    OPTIONS_USER_TRADES,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "cancel_all_options_orders_by_underlying" => {
                params.ensure_allowed(&["underlying", "recvWindow"])?;
                params.required("underlying")?;
                self.options_signed_request(
                    HttpMethod::Delete,
                    OPTIONS_ALL_OPEN_ORDERS_BY_UNDERLYING,
                    params,
                    &[],
                )
                .await
            }
            "cancel_all_options_orders" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                params.required("product_symbol")?;
                self.options_signed_request(
                    HttpMethod::Delete,
                    OPTIONS_ALL_OPEN_ORDERS,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "place_options_batch_orders" => {
                params.ensure_allowed(&["orders", "recvWindow"])?;
                params.required("orders")?;
                self.options_signed_request(HttpMethod::Post, OPTIONS_BATCH_ORDERS, params, &[])
                    .await
            }
            "cancel_options_batch_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderIds",
                    "clientOrderIds",
                    "recvWindow",
                ])?;
                params.required("product_symbol")?;
                require_any(params, &["orderIds", "clientOrderIds"])?;
                self.options_signed_request(
                    HttpMethod::Delete,
                    OPTIONS_BATCH_ORDERS,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "get_options_order" => {
                validate_options_order_lookup(params)?;
                self.options_signed_request(
                    HttpMethod::Get,
                    OPTIONS_ORDER,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "place_options_order" => {
                validate_options_order(params)?;
                self.options_signed_request(
                    HttpMethod::Post,
                    OPTIONS_ORDER,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "cancel_options_order" => {
                validate_options_order_lookup(params)?;
                self.options_signed_request(
                    HttpMethod::Delete,
                    OPTIONS_ORDER,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "get_options_positions" => {
                params.ensure_allowed(&["product_symbol", "recvWindow"])?;
                self.options_signed_request(
                    HttpMethod::Get,
                    OPTIONS_POSITION,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "get_open_options_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "recvWindow",
                ])?;
                params.ensure_time_order("startTime", "endTime")?;
                self.options_signed_request(
                    HttpMethod::Get,
                    OPTIONS_OPEN_ORDERS,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "get_options_order_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                params.required("product_symbol")?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("limit", 1, 1000)?;
                self.options_signed_request(
                    HttpMethod::Get,
                    OPTIONS_HISTORY_ORDERS,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "get_options_commission" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.options_signed_request(HttpMethod::Get, OPTIONS_COMMISSION, params, &[])
                    .await
            }
            "get_options_exercise_records" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("limit", 1, 1000)?;
                self.options_signed_request(
                    HttpMethod::Get,
                    OPTIONS_EXERCISE_RECORD,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "create_options_listen_key" => {
                params.ensure_allowed(&[])?;
                self.api_key_request(
                    HttpMethod::Post,
                    BinanceMarket::Options,
                    OPTIONS_USER_DATA_STREAM,
                    Vec::new(),
                )
                .await
            }
            "keep_alive_options_listen_key" => {
                params.ensure_allowed(&[])?;
                self.api_key_request(
                    HttpMethod::Put,
                    BinanceMarket::Options,
                    OPTIONS_USER_DATA_STREAM,
                    Vec::new(),
                )
                .await
            }
            "close_options_listen_key" => {
                params.ensure_allowed(&[])?;
                self.api_key_request(
                    HttpMethod::Delete,
                    BinanceMarket::Options,
                    OPTIONS_USER_DATA_STREAM,
                    Vec::new(),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    async fn options_signed_request(
        &self,
        method: HttpMethod,
        path: &str,
        params: &PublicParams,
        symbol_aliases: &[&str],
    ) -> Result<ValidatedResponse> {
        let mut query = options_symbol_query(params, symbol_aliases);
        for (key, value) in &mut query {
            if matches!(
                key.as_str(),
                "side" | "type" | "timeInForce" | "newOrderRespType"
            ) {
                *value = value.to_ascii_uppercase();
            }
        }
        self.request(method, BinanceMarket::Options, path, query, true)
            .await
    }
}

fn options_symbol_query(params: &PublicParams, excluded: &[&str]) -> Vec<(String, String)> {
    let mut all_excluded = excluded.to_vec();
    if !all_excluded.contains(&"product_symbol") {
        all_excluded.push("product_symbol");
    }
    let mut query = params.without(&all_excluded);
    if let Some(symbol) = params.get("product_symbol") {
        query.push(("symbol".to_string(), symbol.to_string()));
    }
    query
}

fn validate_options_order(params: &PublicParams) -> Result<()> {
    params.ensure_allowed(&[
        "product_symbol",
        "side",
        "type",
        "quantity",
        "price",
        "timeInForce",
        "reduceOnly",
        "postOnly",
        "newOrderRespType",
        "clientOrderId",
        "selfTradePreventionMode",
        "recvWindow",
    ])?;
    params.required("product_symbol")?;
    normalize_order_side(params.required("side")?)?;
    let order_type = params.required("type")?.to_ascii_uppercase();
    if order_type != "LIMIT" {
        return Err(DcexError::InvalidInput(
            "Binance Options currently supports LIMIT orders only.".to_string(),
        ));
    }
    positive_decimal(params, "quantity")?;
    positive_decimal(params, "price")?;
    params.required("timeInForce")?;
    params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK", "GTX"])?;
    params.optional_one_of("newOrderRespType", &["ACK", "RESULT"])?;
    params.optional_bool("reduceOnly")?;
    params.optional_bool("postOnly")?;
    Ok(())
}

fn validate_options_order_lookup(params: &PublicParams) -> Result<()> {
    params.ensure_allowed(&["product_symbol", "orderId", "clientOrderId", "recvWindow"])?;
    params.required("product_symbol")?;
    require_any(params, &["orderId", "clientOrderId"])
}

fn require_any(params: &PublicParams, keys: &[&str]) -> Result<()> {
    if keys.iter().any(|key| params.get(key).is_some()) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "Binance requires one of: {}",
            keys.join(", ")
        )))
    }
}

fn positive_decimal(params: &PublicParams, key: &str) -> Result<()> {
    let value = params.required(key)?;
    let number = value.parse::<f64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Binance decimal parameter {key}: {error}"))
    })?;
    if !number.is_finite() || number <= 0.0 {
        return Err(DcexError::InvalidInput(format!(
            "Binance parameter {key} must be positive"
        )));
    }
    Ok(())
}
