use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};
use tokio::sync::Mutex;

use super::endpoints::{BASE_URL, TIME_ENDPOINT};
use super::params::{canonical_category_fallback, exchange_symbol_fallback};
use super::signing::{encode_params, extract_server_time_ms, validate_response};
use crate::crypto::hmac_sha256_hex;
use crate::exchange::{ValidatedResponse, unix_timestamp_ms};
use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody, block_on};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

#[derive(Clone)]
pub struct BybitClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    recv_window: u64,
    sync_server_time: bool,
    timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
    product_table: Option<Arc<ProductTable>>,
}

impl BybitClient {
    pub(crate) const INPUT_EXCHANGE: &'static str = "bybit";

    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            api_key,
            api_secret,
            recv_window,
            sync_server_time,
            timeout,
            BASE_URL.to_string(),
        )
    }

    pub fn public(recv_window: u64, sync_server_time: bool, timeout: Duration) -> Result<Self> {
        Self::new(None, None, recv_window, sync_server_time, timeout)
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
            recv_window,
            sync_server_time,
            timestamp_offset_ms: Arc::new(Mutex::new(None)),
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
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self.request_raw(method, path, params, body, signed).await?;
        let data = validate_response(&response)?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = self.timestamp(signed).await?;
        let request = self.build_request(method, path, params, body, signed, timestamp)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request_raw(method, path, params, body, signed).await })
    }
}

impl BybitClient {
    pub(super) async fn get_request(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true)
            .await
    }

    pub(super) async fn post_request(
        &self,
        path: &str,
        mut body: Map<String, Value>,
    ) -> Result<ValidatedResponse> {
        if self.product_table.is_some() {
            let category = body
                .get("category")
                .and_then(Value::as_str)
                .map(str::to_string);
            if let Some(items) = body.get_mut("request").and_then(Value::as_array_mut) {
                for item in items {
                    if let Some(symbol) = item.get("symbol").and_then(Value::as_str) {
                        let native = self.symbol_category(symbol, category.as_deref())?.0;
                        item["symbol"] = Value::String(native);
                    }
                }
            }
        }
        let body = serde_json::to_vec(&Value::Object(body))
            .map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(HttpMethod::Post, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) fn loaded_strategy_symbol(
        &self,
        symbol: &str,
        requested: Option<&str>,
    ) -> Result<Option<(String, String)>> {
        fn category(row: &crate::product_table::MarketInfo) -> Option<&'static str> {
            match (
                row.exchange_type.as_str(),
                row.product_type.as_str(),
                row.quote_currency.as_str(),
            ) {
                ("spot", "spot", _) => Some("UTA_SPOT"),
                ("inverse", "swap", _) => Some("UTA_INVERSE"),
                ("inverse", "futures", _) => Some("UTA_INVERSE_FUTURE"),
                ("linear", "swap", "USDT") => Some("UTA_USDT"),
                ("linear", "swap", "USDC") => Some("UTA_USDC"),
                ("linear", "futures", "USDT") => Some("UTA_USDT_FUTURE"),
                _ => None,
            }
        }
        let Some(table) = &self.product_table else {
            return Ok(None);
        };
        let row = table.resolve_symbol_in("bybit", symbol, |row| {
            category(row).is_some_and(|value| requested.is_none_or(|requested| requested == value))
        })?;
        Ok(Some((
            row.exchange_symbol.clone(),
            category(row).expect("filtered category").into(),
        )))
    }

    /// Resolve a product symbol and its category. `category` is the caller's explicit
    /// category: it narrows native symbols and must agree with a unified symbol's market.
    pub(super) fn symbol_category(
        &self,
        symbol: &str,
        category: Option<&str>,
    ) -> Result<(String, String)> {
        self.resolve_symbol_category(symbol, category, true)
    }

    fn resolve_symbol_category(
        &self,
        symbol: &str,
        category: Option<&str>,
        explicit: bool,
    ) -> Result<(String, String)> {
        let check = |derived: &str| match category {
            Some(category) if explicit && category != derived => {
                Err(DcexError::InvalidInput(format!(
                    "Bybit product_symbol {symbol} is a {derived} market but category={category} was given; omit category or pass the matching one."
                )))
            }
            _ => Ok(()),
        };
        if let Some(table) = &self.product_table {
            let canonical = table
                .rows()
                .iter()
                .any(|row| row.exchange == "bybit" && row.product_symbol == symbol);
            // Canonical symbols determine the category; native symbols are narrowed only by
            // the category and otherwise must be unique across all Bybit markets.
            let row = if canonical {
                let row = table.resolve_symbol("bybit", symbol, None, None)?;
                check(&row.exchange_type)?;
                row
            } else {
                table
                    .resolve_symbol("bybit", symbol, None, category)
                    .map_err(|error| {
                        let ambiguous = category.is_none()
                            && table
                                .rows()
                                .iter()
                                .filter(|row| {
                                    row.exchange == "bybit" && row.exchange_symbol == symbol
                                })
                                .count()
                                > 1;
                        if ambiguous {
                            DcexError::InvalidInput(format!(
                                "{error}; pass category= or the unified product symbol (e.g. BTC-USDT-SPOT / BTC-USDT-SWAP)"
                            ))
                        } else {
                            error
                        }
                    })?
            };
            return Ok((row.exchange_symbol.clone(), row.exchange_type.clone()));
        }
        let native = exchange_symbol_fallback(symbol)?;
        let category = match canonical_category_fallback(symbol) {
            Some(derived) => {
                check(derived)?;
                derived
            }
            None => category.unwrap_or("linear"),
        };
        Ok((native, category.to_string()))
    }

    /// Resolve a symbol for an endpoint that only serves `allowed` categories and was called
    /// without an explicit category. Native symbols are narrowed to those categories; unified
    /// symbols keep their own category, which must be one of them.
    pub(super) fn symbol_category_within(
        &self,
        symbol: &str,
        allowed: &[&str],
    ) -> Result<(String, String)> {
        let resolved = match &self.product_table {
            Some(table) => {
                let row = table.resolve_symbol_in("bybit", symbol, |row| {
                    allowed.contains(&row.exchange_type.as_str())
                })?;
                (row.exchange_symbol.clone(), row.exchange_type.clone())
            }
            None => self.symbol_category(symbol, None)?,
        };
        if !allowed.contains(&resolved.1.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "Bybit product_symbol {symbol} is a {} market; this endpoint supports category {} only",
                resolved.1,
                allowed.join("/")
            )));
        }
        Ok(resolved)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        Ok(self.symbol_category(product_symbol, None)?.0)
    }

    /// Category of a product symbol; `default_category` only applies to native symbols.
    pub(super) fn category_for_product_symbol(
        &self,
        product_symbol: &str,
        default_category: &str,
    ) -> Result<String> {
        Ok(self
            .resolve_symbol_category(product_symbol, Some(default_category), false)?
            .1)
    }

    pub(super) fn push_symbol_category(
        &self,
        params: &mut Vec<(String, String)>,
        product_symbol: &str,
        category: Option<&str>,
        include_category: bool,
    ) -> Result<()> {
        let (symbol, category) = self.symbol_category(product_symbol, category)?;
        params.push(("symbol".into(), symbol));
        if include_category {
            params.retain(|(key, _)| key != "category");
            params.push(("category".into(), category));
        }
        Ok(())
    }

    pub(super) fn insert_symbol_category(
        &self,
        body: &mut Map<String, Value>,
        product_symbol: &str,
        category: Option<&str>,
    ) -> Result<()> {
        let (symbol, category) = self.symbol_category(product_symbol, category)?;
        body.insert("category".into(), Value::String(category));
        body.insert("symbol".into(), Value::String(symbol));
        Ok(())
    }

    async fn timestamp(&self, signed: bool) -> Result<u64> {
        if !signed || !self.sync_server_time {
            return unix_timestamp_ms();
        }
        let mut offset = self.timestamp_offset_ms.lock().await;
        if offset.is_none() {
            let local_start = unix_timestamp_ms()?;
            let response = self
                .transport
                .execute(HttpRequest::new(
                    HttpMethod::Get,
                    &self.base_url,
                    TIME_ENDPOINT,
                ))
                .await;
            let local_end = unix_timestamp_ms()?;
            let calculated = response
                .ok()
                .and_then(|response| response.json().ok())
                .and_then(|data| extract_server_time_ms(&data))
                .map(|server_time| server_time as i64 - ((local_start + local_end) / 2) as i64)
                .unwrap_or(0);
            *offset = Some(calculated);
        }
        let local = unix_timestamp_ms()? as i64;
        let adjusted = local + offset.unwrap_or(0);
        u64::try_from(adjusted).map_err(|error| DcexError::Runtime(error.to_string()))
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let payload = if matches!(method, HttpMethod::Get) {
            encode_params(&params)
        } else {
            String::from_utf8_lossy(body.as_deref().unwrap_or_default()).into_owned()
        };
        let mut request = HttpRequest::new(method, &self.base_url, path)
            .header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Get) {
            request.query = params;
        } else {
            request.body = body.map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret) = self.credentials()?;
            let signature_payload = format!("{timestamp}{api_key}{}{payload}", self.recv_window);
            let signature = hmac_sha256_hex(api_secret.as_bytes(), signature_payload.as_bytes())?;
            request
                .headers
                .insert("X-BAPI-API-KEY".to_string(), api_key.to_string());
            request.headers.insert("X-BAPI-SIGN".to_string(), signature);
            request
                .headers
                .insert("X-BAPI-SIGN-TYPE".to_string(), "2".to_string());
            request
                .headers
                .insert("X-BAPI-TIMESTAMP".to_string(), timestamp.to_string());
            request.headers.insert(
                "X-BAPI-RECV-WINDOW".to_string(),
                self.recv_window.to_string(),
            );
        }
        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str)> {
        match (&self.api_key, &self.api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret.".to_string(),
            )),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::super::signing::extract_server_time_ms;
    use super::*;

    #[test]
    fn auth_matches_python_vector() {
        let client = BybitClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            5_000,
            false,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/v5/order/realtime",
                vec![
                    ("symbol".to_string(), "BTCUSDT".to_string()),
                    ("category".to_string(), "linear".to_string()),
                ],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BAPI-SIGN").map(String::as_str),
            Some("ef8980e55f6ba1d32ab182ddbdad9c8182df87123b035c969965698c9dcd8713")
        );
    }

    #[test]
    fn auth_signs_encoded_get_query_payload() {
        let client = BybitClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            5_000,
            false,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/v5/account/withdrawal",
                vec![("coinName".to_string(), "BTC,ETH".to_string())],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BAPI-SIGN").map(String::as_str),
            Some("debcb4f8de9897ee9b0f8ff0c4f6c4ee2e98b96ee3e418617f23da70801fe587")
        );
    }

    #[test]
    fn extracts_supported_server_time_shapes() {
        assert_eq!(
            extract_server_time_ms(&serde_json::json!({"time": "1700000000000"})),
            Some(1_700_000_000_000)
        );
        assert_eq!(
            extract_server_time_ms(
                &serde_json::json!({"result": {"timeNano": "1700000000000000000"}})
            ),
            Some(1_700_000_000_000)
        );
    }

    #[test]
    fn symbol_category_replaces_default_query_category() {
        let client = BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client");
        let mut params = vec![("category".to_string(), "linear".to_string())];

        client
            .push_symbol_category(&mut params, "BTC-USD-SWAP", None, true)
            .expect("symbol category");

        assert_eq!(
            params
                .iter()
                .filter(|(key, _)| key == "category")
                .collect::<Vec<_>>(),
            vec![&("category".to_string(), "inverse".to_string())]
        );
        assert!(params.contains(&("symbol".to_string(), "BTCUSD".to_string())));
    }

    #[test]
    fn raw_symbol_preserves_explicit_category() {
        let client = BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client");
        let mut params = vec![("category".to_string(), "spot".to_string())];

        client
            .push_symbol_category(&mut params, "BTCUSDT", Some("spot"), true)
            .expect("symbol category");

        assert!(params.contains(&("category".to_string(), "spot".to_string())));
        assert_eq!(
            params.iter().filter(|(key, _)| key == "category").count(),
            1
        );
    }

    #[test]
    fn unified_symbol_rejects_conflicting_explicit_category() {
        let row =
            |product: &str, kind: &str, exchange_type: &str| crate::product_table::MarketInfo {
                exchange: "bybit".into(),
                exchange_symbol: "BTCUSDT".into(),
                product_symbol: product.into(),
                product_type: kind.into(),
                exchange_type: exchange_type.into(),
                ..Default::default()
            };
        let fallback = BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client");
        let table = fallback
            .clone()
            .with_product_table(crate::product_table::ProductTable::new(vec![
                row("BTC-USDT-SPOT", "spot", "spot"),
                row("BTC-USDT-SWAP", "swap", "linear"),
            ]));
        for client in [&fallback, &table] {
            for (symbol, category) in [("BTC-USDT-SPOT", "linear"), ("BTC-USDT-SWAP", "spot")] {
                let error = client
                    .symbol_category(symbol, Some(category))
                    .expect_err("conflicting category");
                assert!(error.to_string().contains("category="), "{error}");
            }
            assert_eq!(
                client
                    .symbol_category("BTC-USDT-SWAP", Some("linear"))
                    .expect("match"),
                ("BTCUSDT".to_string(), "linear".to_string())
            );
            // Method defaults never filter a unified symbol.
            assert_eq!(
                client
                    .category_for_product_symbol("BTC-USDT-SWAP", "spot")
                    .expect("default"),
                "linear"
            );
        }
        assert_eq!(
            table
                .symbol_category("BTCUSDT", Some("spot"))
                .expect("native"),
            ("BTCUSDT".to_string(), "spot".to_string())
        );
    }
}
