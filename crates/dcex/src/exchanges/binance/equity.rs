use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{normalize_order_side, PublicParams};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub fn get_equity_exchange_info(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_equity_exchange_info",
            Vec::new(),
        )
    }

    pub fn get_equity_tokenized_assets(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_equity_tokenized_assets",
            Vec::new(),
        )
    }

    pub fn get_equity_quote(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_equity_quote",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn place_equity_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_equity_order",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("side".to_string(), side.to_string()),
                ("orderType".to_string(), order_type.to_string()),
            ],
        )
    }

    pub fn cancel_equity_order(
        &self,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_equity_order",
            vec![("orderId".to_string(), order_id.to_string())],
        )
    }

    pub fn cancel_all_equity_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_all_equity_orders",
            Vec::new(),
        )
    }

    pub fn get_open_equity_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_open_equity_orders", Vec::new())
    }

    pub fn get_equity_order_history(
        &self,
        start_time: u64,
        end_time: u64,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_equity_order_history",
            vec![
                ("startTime".to_string(), start_time.to_string()),
                ("endTime".to_string(), end_time.to_string()),
            ],
        )
    }

    pub fn get_equity_order_detail(
        &self,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_equity_order_detail",
            vec![("orderId".to_string(), order_id.to_string())],
        )
    }

    pub fn get_equity_trade_history(
        &self,
        start_time: u64,
        end_time: u64,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_equity_trade_history",
            vec![
                ("startTime".to_string(), start_time.to_string()),
                ("endTime".to_string(), end_time.to_string()),
            ],
        )
    }

    pub fn mint_equity_token(
        &self,
        underlying_asset: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "mint_equity_token",
            vec![
                ("underlyingAsset".to_string(), underlying_asset.to_string()),
                ("underlyingAssetAmount".to_string(), amount.to_string()),
            ],
        )
    }

    pub fn redeem_equity_token(
        &self,
        tokenized_asset: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "redeem_equity_token",
            vec![
                ("tokenizedAsset".to_string(), tokenized_asset.to_string()),
                ("tokenizedAssetAmount".to_string(), amount.to_string()),
            ],
        )
    }

    pub fn get_equity_convert_status(
        &self,
        issuer_request_id: &str,
        convert_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_equity_convert_status",
            vec![
                ("issuerRequestId".to_string(), issuer_request_id.to_string()),
                ("convertType".to_string(), convert_type.to_string()),
            ],
        )
    }

    pub fn get_equity_convert_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_equity_convert_history",
            Vec::new(),
        )
    }

    pub fn sign_equity_disclaimer(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "sign_equity_disclaimer", Vec::new())
    }

    pub fn create_or_renew_equity_listen_key(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "create_or_renew_equity_listen_key",
            Vec::new(),
        )
    }

    pub(super) async fn equity_public_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_equity_exchange_info" => {
                params.ensure_allowed(&["product_symbol"])?;
                let mut query = Vec::new();
                if let Some(product_symbol) = params.get("product_symbol") {
                    query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
                }
                self.api_key_request(
                    HttpMethod::Get,
                    BinanceMarket::Equity,
                    EQUITY_EXCHANGE_INFO,
                    query,
                )
                .await
            }
            "get_equity_tokenized_assets" => {
                params.ensure_allowed(&[])?;
                self.api_key_request(
                    HttpMethod::Get,
                    BinanceMarket::Equity,
                    EQUITY_TOKENIZED_ASSETS,
                    Vec::new(),
                )
                .await
            }
            "get_equity_quote" => {
                params.ensure_allowed(&["product_symbol"])?;
                let query = vec![(
                    "symbol".to_string(),
                    self.exchange_symbol(params.required("product_symbol")?)?,
                )];
                self.api_key_request(HttpMethod::Get, BinanceMarket::Equity, EQUITY_QUOTE, query)
                    .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    pub(super) async fn equity_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "place_equity_order" => self.send_equity_order(params).await,
            "cancel_equity_order" => {
                params.ensure_allowed(&["orderId", "recvWindow"])?;
                params.required("orderId")?;
                self.equity_signed_request(HttpMethod::Post, EQUITY_ORDER_CANCEL, params, &[])
                    .await
            }
            "cancel_all_equity_orders" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.equity_signed_request(HttpMethod::Post, EQUITY_ORDER_CANCEL_ALL, params, &[])
                    .await
            }
            "get_open_equity_orders" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.equity_signed_request(HttpMethod::Get, EQUITY_OPEN_ORDERS, params, &[])
                    .await
            }
            "get_equity_order_history" => {
                validate_equity_order_history(params)?;
                self.equity_signed_request(
                    HttpMethod::Get,
                    EQUITY_ORDER_HISTORY,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "get_equity_order_detail" => {
                params.ensure_allowed(&["orderId", "recvWindow"])?;
                params.required("orderId")?;
                self.equity_signed_request(HttpMethod::Get, EQUITY_ORDER_DETAIL, params, &[])
                    .await
            }
            "get_equity_trade_history" => {
                validate_equity_trade_history(params)?;
                self.equity_signed_request(
                    HttpMethod::Get,
                    EQUITY_TRADE_HISTORY,
                    params,
                    &["product_symbol"],
                )
                .await
            }
            "mint_equity_token" => {
                params.ensure_allowed(&[
                    "underlyingAsset",
                    "underlyingAssetAmount",
                    "clientOrderId",
                    "recvWindow",
                ])?;
                params.required("underlyingAsset")?;
                validate_positive_decimal(params, "underlyingAssetAmount")?;
                self.equity_signed_request(HttpMethod::Post, EQUITY_TOKENIZED_MINT, params, &[])
                    .await
            }
            "redeem_equity_token" => {
                params.ensure_allowed(&[
                    "tokenizedAsset",
                    "tokenizedAssetAmount",
                    "clientOrderId",
                    "recvWindow",
                ])?;
                params.required("tokenizedAsset")?;
                validate_positive_decimal(params, "tokenizedAssetAmount")?;
                self.equity_signed_request(HttpMethod::Post, EQUITY_TOKENIZED_REDEEM, params, &[])
                    .await
            }
            "get_equity_convert_status" => {
                params.ensure_allowed(&["issuerRequestId", "convertType", "recvWindow"])?;
                params.required("issuerRequestId")?;
                validate_uppercase_value(params, "convertType", &["MINT", "REDEEM"])?;
                self.equity_signed_request(
                    HttpMethod::Get,
                    EQUITY_TOKENIZED_CONVERT_STATUS,
                    params,
                    &[],
                )
                .await
            }
            "get_equity_convert_history" => {
                params.ensure_allowed(&["startTime", "endTime", "lastId", "size", "recvWindow"])?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("size", 1, 100)?;
                self.equity_signed_request(HttpMethod::Get, EQUITY_TOKENIZED_HISTORY, params, &[])
                    .await
            }
            "sign_equity_disclaimer" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.equity_signed_request(HttpMethod::Post, EQUITY_DISCLAIMER, params, &[])
                    .await
            }
            "create_or_renew_equity_listen_key" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.timed_api_key_request(
                    HttpMethod::Post,
                    BinanceMarket::Equity,
                    EQUITY_LISTEN_KEY,
                    params.without(&[]),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    pub(super) async fn send_place_equity_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
        extra_params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("product_symbol".to_string(), product_symbol.to_string()),
            ("side".to_string(), side.to_string()),
            ("orderType".to_string(), order_type.to_string()),
        ];
        params.extend(extra_params);
        self.send_equity_order(&PublicParams(params)).await
    }

    async fn send_equity_order(&self, params: &PublicParams) -> Result<ValidatedResponse> {
        validate_equity_order(params)?;
        let mut query = params.without(&["product_symbol", "side", "orderType"]);
        query.push((
            "symbol".to_string(),
            self.exchange_symbol(params.required("product_symbol")?)?,
        ));
        query.push((
            "side".to_string(),
            normalize_order_side(params.required("side")?)?,
        ));
        query.push((
            "orderType".to_string(),
            params.required("orderType")?.to_ascii_uppercase(),
        ));
        self.request(
            HttpMethod::Post,
            BinanceMarket::Equity,
            EQUITY_ORDER_PLACE,
            query,
            true,
        )
        .await
    }

    async fn equity_signed_request(
        &self,
        method: HttpMethod,
        path: &str,
        params: &PublicParams,
        symbol_aliases: &[&str],
    ) -> Result<ValidatedResponse> {
        let mut query = params.without(symbol_aliases);
        for (key, value) in &mut query {
            if matches!(key.as_str(), "side" | "orderType" | "convertType") {
                *value = value.to_ascii_uppercase();
            }
        }
        if symbol_aliases.contains(&"product_symbol") {
            if let Some(product_symbol) = params.get("product_symbol") {
                query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
            }
        }
        self.request(method, BinanceMarket::Equity, path, query, true)
            .await
    }
}

fn validate_equity_order(params: &PublicParams) -> Result<()> {
    params.ensure_allowed(&[
        "product_symbol",
        "side",
        "orderType",
        "quoteAsset",
        "price",
        "quantity",
        "notional",
        "timeInForce",
        "tradingSession",
        "walletType",
        "clientOrderId",
        "tokenize",
        "recvWindow",
    ])?;
    params.required("product_symbol")?;
    let side = normalize_order_side(params.required("side")?)?;
    let order_type = params.required("orderType")?.to_ascii_uppercase();
    if !matches!(order_type.as_str(), "MARKET" | "LIMIT") {
        return Err(DcexError::InvalidInput(format!(
            "invalid Binance Equity orderType: {order_type}; expected MARKET or LIMIT"
        )));
    }
    params.optional_one_of("timeInForce", &["DAY", "GTC"])?;
    params.optional_one_of("tradingSession", &["RTH", "EXTENDED", "24H"])?;
    params.optional_one_of("walletType", &["CARD", "MAIN"])?;
    params.optional_bool("tokenize")?;

    if order_type == "LIMIT" {
        validate_positive_decimal(params, "price")?;
        validate_positive_decimal(params, "quantity")?;
        params.required("tradingSession")?;
        if params.get("notional").is_some() {
            return Err(DcexError::InvalidInput(
                "Binance Equity LIMIT orders do not accept notional.".to_string(),
            ));
        }
        if let Some(price) = params.get("price") {
            if price
                .split_once('.')
                .is_some_and(|(_, decimals)| decimals.len() > 2)
            {
                return Err(DcexError::InvalidInput(
                    "Binance Equity LIMIT price supports at most two decimal places.".to_string(),
                ));
            }
        }
    } else {
        for forbidden in ["price", "tradingSession", "timeInForce"] {
            if params.get(forbidden).is_some() {
                return Err(DcexError::InvalidInput(format!(
                    "Binance Equity MARKET orders do not accept {forbidden}."
                )));
            }
        }
        if side == "BUY" {
            if params.get("notional").is_none() || params.get("quantity").is_some() {
                return Err(DcexError::InvalidInput(
                    "Binance Equity BUY MARKET orders require notional and do not accept quantity."
                        .to_string(),
                ));
            }
            validate_positive_decimal(params, "notional")?;
        } else {
            if params.get("quantity").is_none() || params.get("notional").is_some() {
                return Err(DcexError::InvalidInput(
                    "Binance Equity SELL MARKET orders require quantity and do not accept notional."
                        .to_string(),
                ));
            }
            validate_positive_decimal(params, "quantity")?;
        }
    }
    Ok(())
}

fn validate_equity_order_history(params: &PublicParams) -> Result<()> {
    params.ensure_allowed(&[
        "product_symbol",
        "orderType",
        "side",
        "orderStatus",
        "startTime",
        "endTime",
        "current",
        "size",
        "recvWindow",
    ])?;
    params.required("startTime")?;
    params.required("endTime")?;
    params.ensure_time_order("startTime", "endTime")?;
    params.optional_u64_range("size", 1, 100)?;
    if let Some(order_type) = params.get("orderType") {
        let upper = order_type.to_ascii_uppercase();
        if !matches!(upper.as_str(), "MARKET" | "LIMIT") {
            return Err(DcexError::InvalidInput(format!(
                "invalid Binance Equity orderType: {order_type}"
            )));
        }
    }
    if let Some(side) = params.get("side") {
        normalize_order_side(side)?;
    }
    Ok(())
}

fn validate_equity_trade_history(params: &PublicParams) -> Result<()> {
    params.ensure_allowed(&[
        "product_symbol",
        "side",
        "orderId",
        "startTime",
        "endTime",
        "current",
        "size",
        "recvWindow",
    ])?;
    params.required("startTime")?;
    params.required("endTime")?;
    params.ensure_time_order("startTime", "endTime")?;
    params.optional_u64_range("size", 1, 100)?;
    if let Some(side) = params.get("side") {
        normalize_order_side(side)?;
    }
    Ok(())
}

fn validate_positive_decimal(params: &PublicParams, key: &str) -> Result<()> {
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

fn validate_uppercase_value(params: &PublicParams, key: &str, allowed: &[&str]) -> Result<()> {
    let value = params.required(key)?;
    if !allowed.contains(&value.to_ascii_uppercase().as_str()) {
        return Err(DcexError::InvalidInput(format!(
            "invalid Binance Equity {key}: {value}; expected one of {}",
            allowed.join(", ")
        )));
    }
    Ok(())
}
