use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;
use tokio::sync::Mutex;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://api.bybit.com";
const TIME_ENDPOINT: &str = "/v5/market/time";
const INSTRUMENTS_INFO: &str = "/v5/market/instruments-info";
const KLINE: &str = "/v5/market/kline";
const ORDERBOOK: &str = "/v5/market/orderbook";
const TICKERS: &str = "/v5/market/tickers";
const FUNDING_RATE_HISTORY: &str = "/v5/market/funding/history";
const PUBLIC_TRADE_HISTORY: &str = "/v5/market/recent-trade";
const OPEN_INTEREST: &str = "/v5/market/open-interest";
const HISTORICAL_VOLATILITY: &str = "/v5/market/historical-volatility";
const INSURANCE_POOL: &str = "/v5/market/insurance";
const RISK_LIMIT: &str = "/v5/market/risk-limit";
const DELIVERY_PRICE: &str = "/v5/market/delivery-price";
const LONG_SHORT_RATIO: &str = "/v5/market/account-ratio";
const ORDER_PRICE_LIMIT: &str = "/v5/market/price-limit";
const ADL_ALERT: &str = "/v5/market/adlAlert";

#[derive(Clone)]
pub struct BybitClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    recv_window: u64,
    sync_server_time: bool,
    timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
}

impl BybitClient {
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
        })
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

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (path, params) = match method_name {
            "get_instruments_info" => (INSTRUMENTS_INFO, normalize_symbol_params(params)?),
            "get_kline" => (KLINE, normalize_kline_params(params)?),
            "get_orderbook" => (ORDERBOOK, normalize_symbol_params(params)?),
            "get_tickers" => (TICKERS, normalize_symbol_params(params)?),
            "get_funding_rate_history" => (FUNDING_RATE_HISTORY, normalize_symbol_params(params)?),
            "get_public_trade_history" => (PUBLIC_TRADE_HISTORY, normalize_symbol_params(params)?),
            "get_open_interest" => (OPEN_INTEREST, normalize_symbol_params(params)?),
            "get_long_short_ratio" => (LONG_SHORT_RATIO, normalize_symbol_params(params)?),
            "get_historical_volatility" => (HISTORICAL_VOLATILITY, params),
            "get_insurance_pool" => (INSURANCE_POOL, params),
            "get_delivery_price" => (DELIVERY_PRICE, normalize_symbol_params(params)?),
            "get_order_price_limit" => (ORDER_PRICE_LIMIT, normalize_symbol_params(params)?),
            "get_adl_alert" => (ADL_ALERT, normalize_symbol_params(params)?),
            "get_risk_limit" => (RISK_LIMIT, normalize_symbol_params(params)?),
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bybit public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, path, params, None, false)
            .await
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
            params
                .iter()
                .map(|(key, value)| format!("{key}={value}"))
                .collect::<Vec<_>>()
                .join("&")
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

fn normalize_symbol_params(params: Vec<(String, String)>) -> Result<Vec<(String, String)>> {
    Ok(params
        .into_iter()
        .map(|(key, value)| {
            if key == "product_symbol" {
                ("symbol".to_string(), exchange_symbol(&value))
            } else if key == "symbol" {
                (key, exchange_symbol(&value))
            } else {
                (key, value)
            }
        })
        .collect())
}

fn normalize_kline_params(params: Vec<(String, String)>) -> Result<Vec<(String, String)>> {
    params
        .into_iter()
        .map(|(key, value)| {
            if key == "product_symbol" {
                Ok(("symbol".to_string(), exchange_symbol(&value)))
            } else if key == "symbol" {
                Ok((key, exchange_symbol(&value)))
            } else if key == "interval" {
                Ok((key, bybit_timeframe(&value)?.to_string()))
            } else if key == "startTime" {
                Ok(("start".to_string(), value))
            } else {
                Ok((key, value))
            }
        })
        .collect()
}

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn bybit_timeframe(timeframe: &str) -> Result<&'static str> {
    match timeframe {
        "1m" => Ok("1"),
        "3m" => Ok("3"),
        "5m" => Ok("5"),
        "15m" => Ok("15"),
        "30m" => Ok("30"),
        "1h" => Ok("60"),
        "2h" => Ok("120"),
        "4h" => Ok("240"),
        "6h" => Ok("360"),
        "12h" => Ok("720"),
        "1d" => Ok("D"),
        "1w" => Ok("W"),
        "1M" => Ok("M"),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
    }
}

fn extract_server_time_ms(data: &Value) -> Option<u64> {
    if let Some(value) = data.get("time").and_then(json_u64) {
        return Some(value);
    }
    let result = data.get("result")?.as_object()?;
    if let Some(value) = result.get("timeNano").and_then(json_u64) {
        return Some(value / 1_000_000);
    }
    result
        .get("timeSecond")
        .and_then(json_u64)
        .map(|value| value * 1_000)
}

fn json_u64(value: &Value) -> Option<u64> {
    value
        .as_u64()
        .or_else(|| value.as_str().and_then(|value| value.parse().ok()))
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("retCode"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string());
    if code != "0" {
        let message = data
            .as_object()
            .and_then(|object| object.get("retMsg"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Bybit API Error: [{code}] {message}"),
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    response.ensure_success()?;
    Ok(data)
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

#[cfg(test)]
mod tests {
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
}
