use std::sync::{Arc, Mutex};
use std::time::Duration;

use crate::exchange::{unix_timestamp_ms, ExchangeHttpClient, ValidatedResponse};
use crate::http::{block_on, HttpMethod, HttpRequest, HttpResponse};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::*;
use super::params::{
    exchange_symbol_fallback, is_canonical_product_symbol, market_for_product_symbol_fallback,
};
use super::signing::{extract_server_time_ms, BinanceResponseValidator, BinanceSigner};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BinanceMarket {
    Equity,
    Futures,
    Spot,
}

impl BinanceMarket {
    pub const fn base_url(self) -> &'static str {
        match self {
            Self::Equity => SPOT_BASE_URL,
            Self::Futures => FUTURES_BASE_URL,
            Self::Spot => SPOT_BASE_URL,
        }
    }

    pub fn from_path(path: &str) -> Result<Self> {
        if path.starts_with("/sapi/v1/equity/") {
            return Ok(Self::Equity);
        }
        if path.starts_with("/fapi/") || path.starts_with("/futures/") {
            return Ok(Self::Futures);
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
    futures_base_url: String,
    spot_base_url: String,
    api_key: Option<String>,
    timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
    product_table: Option<Arc<ProductTable>>,
}

impl BinanceClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
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
        let timestamp_offset_ms = Arc::new(Mutex::new(None));
        let mut inner =
            ExchangeHttpClient::new(timeout)?.with_validator(Arc::new(BinanceResponseValidator));
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
            futures_base_url,
            spot_base_url,
            api_key: api_key_header,
            timestamp_offset_ms,
            product_table: None,
        })
    }

    pub fn with_product_table(mut self, product_table: ProductTable) -> Self {
        self.product_table = Some(Arc::new(product_table));
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
            BinanceMarket::Equity => SPOT_SERVER_TIME,
            BinanceMarket::Futures => FUTURES_SERVER_TIME,
            BinanceMarket::Spot => SPOT_SERVER_TIME,
        };
        let request = self.build_request(HttpMethod::Get, market, path, Vec::new());
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
            BinanceMarket::Equity => &self.spot_base_url,
            BinanceMarket::Futures => &self.futures_base_url,
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

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                return table.get_exchange_symbol("binance", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn market_for_product_symbol(&self, product_symbol: &str) -> Result<BinanceMarket> {
        if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                let product_type = table.get_product_type("binance", Some(product_symbol), None)?;
                return Ok(match product_type.as_str() {
                    "equity" | "stock" => BinanceMarket::Equity,
                    "spot" => BinanceMarket::Spot,
                    _ => BinanceMarket::Futures,
                });
            }
        }
        Ok(market_for_product_symbol_fallback(product_symbol))
    }
}
