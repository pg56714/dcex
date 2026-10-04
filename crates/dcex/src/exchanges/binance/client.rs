use serde_json::Value;
use std::sync::{Arc, Mutex};
use std::time::Duration;

use crate::exchange::{ExchangeHttpClient, ValidatedResponse, unix_timestamp_ms};
use crate::http::{HttpMethod, HttpRequest, HttpResponse, block_on};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::*;
use super::params::{exchange_symbol_fallback, market_for_product_symbol_fallback};
use super::signing::{BinanceResponseValidator, BinanceSigner, extract_server_time_ms};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BinanceMarket {
    CoinFutures,
    Equity,
    Futures,
    Options,
    PortfolioMargin,
    Spot,
}

impl BinanceMarket {
    pub(super) fn table_exchange(self) -> &'static str {
        if self == Self::CoinFutures {
            "binance_coinm"
        } else {
            "binance"
        }
    }

    pub(super) fn accepts(self, row: &crate::product_table::MarketInfo) -> bool {
        match self {
            Self::Spot => row.product_type == "spot",
            Self::Equity => matches!(row.product_type.as_str(), "equity" | "stock"),
            Self::Options => matches!(row.product_type.as_str(), "option" | "options"),
            Self::Futures | Self::CoinFutures => {
                matches!(row.product_type.as_str(), "swap" | "futures")
            }
            Self::PortfolioMargin => false,
        }
    }

    pub const fn base_url(self) -> &'static str {
        match self {
            Self::CoinFutures => COIN_FUTURES_BASE_URL,
            Self::Equity => SPOT_BASE_URL,
            Self::Futures => FUTURES_BASE_URL,
            Self::Options => OPTIONS_BASE_URL,
            Self::PortfolioMargin => PORTFOLIO_MARGIN_BASE_URL,
            Self::Spot => SPOT_BASE_URL,
        }
    }

    pub fn from_path(path: &str) -> Result<Self> {
        if path.starts_with("/papi/") {
            return Ok(Self::PortfolioMargin);
        }
        if path.starts_with("/dapi/") {
            return Ok(Self::CoinFutures);
        }
        if path.starts_with("/sapi/v1/equity/") {
            return Ok(Self::Equity);
        }
        if path.starts_with("/fapi/") || path.starts_with("/futures/") {
            return Ok(Self::Futures);
        }
        if path.starts_with("/eapi/") {
            return Ok(Self::Options);
        }
        if path.starts_with("/api/") || path.starts_with("/sapi/") {
            return Ok(Self::Spot);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Binance API path: {path}"
        )))
    }
}

#[derive(Clone)]
pub struct BinanceClient {
    inner: ExchangeHttpClient,
    coin_futures_base_url: String,
    futures_base_url: String,
    options_base_url: String,
    portfolio_margin_base_url: String,
    spot_base_url: String,
    alpha_base_url: String,
    api_key: Option<String>,
    timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
    pub(super) product_table: Option<Arc<ProductTable>>,
}

impl BinanceClient {
    pub(super) fn has_product_table(&self) -> bool {
        self.product_table.is_some()
    }
    pub(crate) const INPUT_EXCHANGE: &'static str = "binance";

    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_all_base_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
            OPTIONS_BASE_URL.to_string(),
        )
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, timeout)
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        Self::with_all_base_urls(
            api_key,
            api_secret,
            timeout,
            spot_base_url,
            futures_base_url,
            OPTIONS_BASE_URL.to_string(),
        )
    }

    pub fn with_all_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
        options_base_url: String,
    ) -> Result<Self> {
        let timestamp_offset_ms = Arc::new(Mutex::new(None));
        let mut inner = ExchangeHttpClient::new(timeout, Arc::new(BinanceResponseValidator))?;
        let api_key_header = api_key.clone();
        if let (Some(api_key), Some(api_secret)) = (api_key, api_secret) {
            inner = inner.with_signer(Arc::new(BinanceSigner {
                api_key,
                api_secret,
                timestamp_offset_ms: timestamp_offset_ms.clone(),
            }));
        }
        Ok(Self {
            inner,
            coin_futures_base_url: COIN_FUTURES_BASE_URL.to_string(),
            futures_base_url,
            options_base_url,
            portfolio_margin_base_url: PORTFOLIO_MARGIN_BASE_URL.to_string(),
            spot_base_url,
            alpha_base_url: "https://www.binance.com".into(),
            api_key: api_key_header,
            timestamp_offset_ms,
            product_table: None,
        })
    }

    pub fn with_product_table(mut self, product_table: ProductTable) -> Self {
        self.product_table = Some(Arc::new(product_table));
        self
    }

    pub fn with_alpha_base_url(mut self, base_url: impl Into<String>) -> Self {
        self.alpha_base_url = base_url.into();
        self
    }

    pub(super) async fn inventory_transport(
        &self,
        method: HttpMethod,
        path: &str,
        query: Vec<(String, String)>,
        body: Option<Value>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        if signed {
            self.sync_server_time(BinanceMarket::Spot).await?;
        }
        let mut request = self.build_request(method, BinanceMarket::Spot, path, query.clone());
        if path.starts_with("/bapi/") {
            request.base_url = self.alpha_base_url.clone();
        }
        if let Some(body) = body {
            request = request.json(body);
            request.query = query;
        }
        let response = self.inner.execute_raw(request, signed).await?;
        response.ensure_success("Binance")?;
        let data = response.json()?;
        let failed = data.get("success") == Some(&Value::Bool(false))
            || data.get("code").is_some_and(|code| {
                !matches!(
                    super::signing::json_value_string(code).as_str(),
                    "0" | "000000" | "200"
                )
            });
        if failed {
            let (code, message) = crate::http::error_parts(&response.body);
            return Err(DcexError::ExchangeResponse {
                status: response.status,
                message: crate::http::api_error_message(
                    "Binance",
                    response.status,
                    code.as_deref(),
                    &message,
                ),
                headers: response.headers.into_iter().collect(),
                data,
            });
        }
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    pub fn with_portfolio_margin_base_url(mut self, base_url: impl Into<String>) -> Self {
        self.portfolio_margin_base_url = base_url.into();
        self
    }

    pub fn with_coin_futures_base_url(mut self, base_url: impl Into<String>) -> Self {
        self.coin_futures_base_url = base_url.into();
        self
    }

    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.product_table = Some(Arc::new(product_table));
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        if signed {
            self.sync_server_time(market).await?;
        }
        let request = self.build_request(method, market, path, params);
        self.inner.execute(request, signed).await
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        if signed {
            self.sync_server_time(market).await?;
        }
        let request = self.build_request(method, market, path, params);
        self.inner.execute_raw(request, signed).await
    }

    pub async fn request_raw_auto(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let path = path.into();
        let market = BinanceMarket::from_path(&path)?;
        self.request_raw(method, market, path, params, signed).await
    }

    async fn sync_server_time(&self, market: BinanceMarket) -> Result<()> {
        {
            let offset = self.timestamp_offset_ms.lock().map_err(|error| {
                DcexError::Runtime(format!("Binance timestamp offset lock poisoned: {error}"))
            })?;
            if offset.is_some() {
                return Ok(());
            }
        }

        let local_start = unix_timestamp_ms()?;
        let path = match market {
            BinanceMarket::CoinFutures => COIN_FUTURES_SERVER_TIME,
            BinanceMarket::Equity => SPOT_SERVER_TIME,
            BinanceMarket::Futures => FUTURES_SERVER_TIME,
            BinanceMarket::Options => OPTIONS_SERVER_TIME,
            BinanceMarket::PortfolioMargin => SPOT_SERVER_TIME,
            BinanceMarket::Spot => SPOT_SERVER_TIME,
        };
        let time_market = if market == BinanceMarket::PortfolioMargin {
            BinanceMarket::Spot
        } else {
            market
        };
        let request = self.build_request(HttpMethod::Get, time_market, path, Vec::new());
        let response = self.inner.execute(request, false).await?;
        let local_end = unix_timestamp_ms()?;
        let server_time = extract_server_time_ms(&response.data).ok_or_else(|| {
            DcexError::Decode(format!(
                "Binance server time response did not include serverTime: {response:?}"
            ))
        })?;
        let midpoint = ((local_start + local_end) / 2) as i64;
        let mut offset = self.timestamp_offset_ms.lock().map_err(|error| {
            DcexError::Runtime(format!("Binance timestamp offset lock poisoned: {error}"))
        })?;
        *offset = Some(server_time as i64 - midpoint);
        Ok(())
    }

    fn build_request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> HttpRequest {
        let base_url = match market {
            BinanceMarket::CoinFutures => &self.coin_futures_base_url,
            BinanceMarket::Equity => &self.spot_base_url,
            BinanceMarket::Futures => &self.futures_base_url,
            BinanceMarket::Options => &self.options_base_url,
            BinanceMarket::PortfolioMargin => &self.portfolio_margin_base_url,
            BinanceMarket::Spot => &self.spot_base_url,
        };
        match method {
            HttpMethod::Get | HttpMethod::Delete => {
                let mut request = HttpRequest::new(method, base_url, path);
                request.query = params;
                request
            }
            HttpMethod::Post | HttpMethod::Put | HttpMethod::Patch => {
                HttpRequest::new(method, base_url, path).form(params)
            }
        }
    }

    pub(super) async fn api_key_request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let api_key = self.api_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("Binance API key is required for this request.".to_string())
        })?;
        let mut request = self.build_request(method, market, path, params);
        request
            .headers
            .insert("X-MBX-APIKEY".to_string(), api_key.to_string());
        self.inner.execute(request, false).await
    }

    pub(super) async fn timed_api_key_request(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.sync_server_time(market).await?;
        let local_timestamp = unix_timestamp_ms()? as i64;
        let offset = {
            let offset = self.timestamp_offset_ms.lock().map_err(|error| {
                DcexError::Runtime(format!("Binance timestamp offset lock poisoned: {error}"))
            })?;
            offset.unwrap_or_default()
        };
        let timestamp = (local_timestamp + offset).max(0);
        if !params.iter().any(|(key, _)| key == "timestamp") {
            params.push(("timestamp".to_string(), timestamp.to_string()));
        }
        if !params.iter().any(|(key, _)| key == "recvWindow") {
            params.push(("recvWindow".to_string(), "5000".to_string()));
        }
        self.api_key_request(method, market, path, params).await
    }

    pub fn request_blocking(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request(method, market, path, params, signed).await })
    }

    pub fn get_server_time_blocking(
        &self,
        market_type: impl Into<String>,
    ) -> Result<ValidatedResponse> {
        let client = self.clone();
        let market_type = market_type.into();
        block_on(async move { client.get_server_time(&market_type).await })
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: BinanceMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
        })
    }

    pub fn request_raw_auto_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request_raw_auto(method, path, params, signed).await })
    }

    pub(super) fn loaded_symbol_for(
        &self,
        symbol: &str,
        market: BinanceMarket,
    ) -> Result<Option<String>> {
        self.product_table
            .as_ref()
            .map(|table| {
                table
                    .resolve_symbol_in(market.table_exchange(), symbol, |row| market.accepts(row))
                    .map(|row| row.exchange_symbol.clone())
            })
            .transpose()
    }

    pub(super) fn normalize_loaded_symbols(
        &self,
        params: Vec<(String, String)>,
        market: BinanceMarket,
    ) -> Result<Vec<(String, String)>> {
        params
            .into_iter()
            .map(|(key, value)| {
                let value = if key == "symbol" {
                    self.loaded_symbol_for(&value, market)?.unwrap_or(value)
                } else {
                    value
                };
                Ok((key, value))
            })
            .collect()
    }

    pub(super) fn exchange_symbol_for(
        &self,
        symbol: &str,
        market: BinanceMarket,
    ) -> Result<String> {
        if let Some(table) = &self.product_table {
            return Ok(table
                .resolve_symbol_in(market.table_exchange(), symbol, |row| market.accepts(row))?
                .exchange_symbol
                .clone());
        }
        exchange_symbol_fallback(symbol)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        self.exchange_symbol_for(
            product_symbol,
            self.market_for_product_symbol(product_symbol)?,
        )
    }

    pub(super) fn market_for_product_symbol(&self, product_symbol: &str) -> Result<BinanceMarket> {
        if let Some(table) = &self.product_table {
            // Without an explicit market, a symbol must be unique across every Binance market.
            let row = table
                .resolve_symbol_across(&["binance", "binance_coinm"], product_symbol, |_| true)
                .map_err(|error| match error {
                    DcexError::InvalidInput(message) => DcexError::InvalidInput(format!(
                        "{message}; pass the unified product symbol (e.g. BTC-USDT-SWAP or BTC-USDT-SPOT) to select the market"
                    )),
                    error => error,
                })?;
            if row.exchange == "binance_coinm" {
                return Ok(BinanceMarket::CoinFutures);
            }
            return Ok(match row.product_type.as_str() {
                "equity" | "stock" => BinanceMarket::Equity,
                "option" | "options" => BinanceMarket::Options,
                "spot" => BinanceMarket::Spot,
                _ => BinanceMarket::Futures,
            });
        }
        Ok(market_for_product_symbol_fallback(product_symbol))
    }

    /// Market for the generic order and kline helpers, which cover Spot, USD-M, Options and
    /// Equity; COIN-M products must use the dedicated coin-futures methods.
    pub(super) fn generic_market(&self, product_symbol: &str) -> Result<BinanceMarket> {
        match self.market_for_product_symbol(product_symbol)? {
            BinanceMarket::CoinFutures => Err(DcexError::InvalidInput(format!(
                "Binance COIN-M product {product_symbol:?} requires the coin-futures methods (get_coin_futures_order, cancel_coin_futures_order, get_coin_futures_open_orders, cancel_all_coin_futures_orders)"
            ))),
            market => Ok(market),
        }
    }
}
