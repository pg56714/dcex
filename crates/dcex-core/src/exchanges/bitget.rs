use std::time::Duration;

use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_base64;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://api.bitget.com";
const SPOT_COINS: &str = "/api/v2/spot/public/coins";
const SPOT_SYMBOLS: &str = "/api/v2/spot/public/symbols";
const SPOT_TICKERS: &str = "/api/v2/spot/market/tickers";
const SPOT_ORDERBOOK: &str = "/api/v2/spot/market/orderbook";
const SPOT_CANDLES: &str = "/api/v2/spot/market/candles";
const SPOT_HISTORY_CANDLES: &str = "/api/v2/spot/market/history-candles";
const SPOT_RECENT_TRADES: &str = "/api/v2/spot/market/fills";
const SPOT_MARKET_TRADES: &str = "/api/v2/spot/market/fills-history";
const FUTURES_CONTRACTS: &str = "/api/v2/mix/market/contracts";
const FUTURES_TICKER: &str = "/api/v2/mix/market/ticker";
const FUTURES_TICKERS: &str = "/api/v2/mix/market/tickers";
const FUTURES_ORDERBOOK: &str = "/api/v2/mix/market/merge-depth";
const FUTURES_CANDLES: &str = "/api/v2/mix/market/candles";
const FUTURES_HISTORY_CANDLES: &str = "/api/v2/mix/market/history-candles";
const FUTURES_RECENT_TRADES: &str = "/api/v2/mix/market/fills";
const FUTURES_CURRENT_FUNDING_RATE: &str = "/api/v2/mix/market/current-fund-rate";
const FUTURES_HISTORY_FUNDING_RATE: &str = "/api/v2/mix/market/history-fund-rate";
const FUTURES_OPEN_INTEREST: &str = "/api/v2/mix/market/open-interest";

#[derive(Clone)]
pub struct BitgetClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    passphrase: Option<String>,
}

impl BitgetClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            api_key,
            api_secret,
            passphrase,
            timeout,
            BASE_URL.to_string(),
        )
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
            passphrase,
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
        let timestamp = unix_timestamp_ms()?;
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
        let params = PublicParams(params);
        match method_name {
            "get_spot_coins" => self.public_get(SPOT_COINS, params.into_inner()).await,
            "get_spot_symbols" => {
                self.public_get(SPOT_SYMBOLS, normalize_symbol_params(params.into_inner()))
                    .await
            }
            "get_spot_tickers" => {
                self.public_get(SPOT_TICKERS, normalize_symbol_params(params.into_inner()))
                    .await
            }
            "get_spot_orderbook" => {
                self.public_get(SPOT_ORDERBOOK, normalize_symbol_params(params.into_inner()))
                    .await
            }
            "get_spot_kline" => {
                self.public_get(SPOT_CANDLES, normalize_symbol_params(params.into_inner()))
                    .await
            }
            "get_spot_history_kline" => {
                self.public_get(
                    SPOT_HISTORY_CANDLES,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_spot_recent_trades" => {
                self.public_get(
                    SPOT_RECENT_TRADES,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_spot_market_trades" => {
                self.public_get(
                    SPOT_MARKET_TRADES,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_contracts" => {
                self.public_get(
                    FUTURES_CONTRACTS,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_ticker" => {
                self.public_get(FUTURES_TICKER, normalize_symbol_params(params.into_inner()))
                    .await
            }
            "get_futures_tickers" => self.public_get(FUTURES_TICKERS, params.into_inner()).await,
            "get_futures_orderbook" => {
                self.public_get(
                    FUTURES_ORDERBOOK,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_kline" => {
                self.public_get(
                    FUTURES_CANDLES,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_history_kline" => {
                self.public_get(
                    FUTURES_HISTORY_CANDLES,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_recent_trades" => {
                self.public_get(
                    FUTURES_RECENT_TRADES,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_current_funding_rate" => {
                self.public_get(
                    FUTURES_CURRENT_FUNDING_RATE,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_history_funding_rate" => {
                self.public_get(
                    FUTURES_HISTORY_FUNDING_RATE,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            "get_futures_open_interest" => {
                self.public_get(
                    FUTURES_OPEN_INTEREST,
                    normalize_symbol_params(params.into_inner()),
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Bitget public method: {method_name}"
            ))),
        }
    }

    async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        let query_string = if matches!(method, HttpMethod::Get) {
            encode_params(&params)
        } else {
            String::new()
        };
        let mut request = HttpRequest::new(method, &self.base_url, &path)
            .header("Content-Type", "application/json")
            .header("locale", "en-US");
        if matches!(method, HttpMethod::Get) {
            request.query = params;
        } else if !matches!(method, HttpMethod::Delete) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret, passphrase) = self.credentials()?;
            let request_path = if query_string.is_empty() {
                path
            } else {
                format!("{path}?{query_string}")
            };
            let body = String::from_utf8_lossy(body.as_deref().unwrap_or_default());
            let payload = format!(
                "{timestamp}{}{request_path}{body}",
                http_method_name(method)
            );
            let signature = hmac_sha256_base64(api_secret.as_bytes(), payload.as_bytes())?;
            request
                .headers
                .insert("ACCESS-KEY".to_string(), api_key.to_string());
            request.headers.insert("ACCESS-SIGN".to_string(), signature);
            request
                .headers
                .insert("ACCESS-TIMESTAMP".to_string(), timestamp.to_string());
            request
                .headers
                .insert("ACCESS-PASSPHRASE".to_string(), passphrase.to_string());
        }
        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.passphrase) {
            (Some(api_key), Some(api_secret), Some(passphrase)) => {
                Ok((api_key, api_secret, passphrase))
            }
            _ => Err(DcexError::InvalidInput(
                "Signed Bitget requests require api_key, api_secret, and passphrase.".to_string(),
            )),
        }
    }
}

struct PublicParams(Vec<(String, String)>);

impl PublicParams {
    fn into_inner(self) -> Vec<(String, String)> {
        self.0
    }
}

fn normalize_symbol_params(params: Vec<(String, String)>) -> Vec<(String, String)> {
    params
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
        .collect()
}

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("code"))
        .map(json_value_string)
        .unwrap_or_default();
    if code != "00000" {
        let message = data
            .as_object()
            .and_then(|object| object.get("msg").or_else(|| object.get("message")))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Bitget API Error: [{code}] {message}"),
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

fn encode_params(params: &[(String, String)]) -> String {
    let mut serializer = form_urlencoded::Serializer::new(String::new());
    serializer.extend_pairs(
        params
            .iter()
            .map(|(key, value)| (key.as_str(), value.as_str())),
    );
    serializer.finish()
}

const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
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
    fn signed_batch_uses_exact_body() {
        let client = BitgetClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            Some("test-passphrase".to_string()),
            Duration::from_secs(1),
        )
        .expect("client");
        let body = br#"[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]"#.to_vec();
        let request = client
            .build_request(
                HttpMethod::Post,
                "/api/v3/trade/place-batch",
                Vec::new(),
                Some(body.clone()),
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("ACCESS-SIGN").map(String::as_str),
            Some("R/bWef7Dwp6wughM4S1AulQN6C10+sQmcP55rWFxRoc=")
        );
        assert_eq!(request.body, RequestBody::Raw(body));
    }
}
