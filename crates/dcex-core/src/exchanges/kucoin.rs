use std::time::Duration;

use serde_json::Value;

use crate::crypto::hmac_sha256_base64;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const SPOT_BASE_URL: &str = "https://api.kucoin.com";
const FUTURES_BASE_URL: &str = "https://api-futures.kucoin.com";
const SPOT_INSTRUMENT_INFO: &str = "/api/v2/symbols";
const SPOT_TICKER: &str = "/api/v1/market/orderbook/level1";
const SPOT_ALL_TICKERS: &str = "/api/v1/market/allTickers";
const SPOT_ORDERBOOK: &str = "/api/v3/market/orderbook/level2";
const SPOT_PUBLIC_TRADES: &str = "/api/v1/market/histories";
const SPOT_KLINE: &str = "/api/v1/market/candles";
const FUTURES_CONTRACTS: &str = "/api/v1/contracts/active";
const FUTURES_TICKER: &str = "/api/v1/ticker";
const FUTURES_ORDERBOOK: &str = "/api/v1/level2/snapshot";
const FUTURES_PUBLIC_TRADES: &str = "/api/v1/trade/history";
const FUTURES_KLINE: &str = "/api/v1/kline/query";
const FUTURES_OPEN_INTEREST: &str = "/api/ua/v1/market/open-interest";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum KucoinMarket {
    Futures,
    Spot,
}

#[derive(Clone)]
pub struct KucoinClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    encrypted_passphrase: Option<String>,
}

impl KucoinClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            passphrase,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        let encrypted_passphrase = match (&api_secret, &passphrase) {
            (Some(api_secret), Some(passphrase)) => Some(hmac_sha256_base64(
                api_secret.as_bytes(),
                passphrase.as_bytes(),
            )?),
            _ => None,
        };
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            api_key,
            api_secret,
            encrypted_passphrase,
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, market, path, params, body, signed)
            .await?;
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
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?.to_string();
        let request = self.build_request(method, market, path, params, body, signed, &timestamp)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, market, path, params, body, signed)
                .await
        })
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (market, path) = match method_name {
            "get_spot_instrument_info" => (KucoinMarket::Spot, SPOT_INSTRUMENT_INFO.to_string()),
            "get_spot_ticker" => {
                normalize_symbol_query(&mut params, false);
                (KucoinMarket::Spot, SPOT_TICKER.to_string())
            }
            "get_spot_all_tickers" => (KucoinMarket::Spot, SPOT_ALL_TICKERS.to_string()),
            "get_spot_orderbook" => {
                normalize_symbol_query(&mut params, false);
                (KucoinMarket::Spot, SPOT_ORDERBOOK.to_string())
            }
            "get_spot_public_trades" => {
                normalize_symbol_query(&mut params, false);
                (KucoinMarket::Spot, SPOT_PUBLIC_TRADES.to_string())
            }
            "get_spot_kline" => {
                normalize_symbol_query(&mut params, false);
                normalize_spot_timeframe(&mut params)?;
                (KucoinMarket::Spot, SPOT_KLINE.to_string())
            }
            "get_futures_contracts" => (KucoinMarket::Futures, FUTURES_CONTRACTS.to_string()),
            "get_futures_contract" => {
                let symbol = take_symbol(&mut params, true)?;
                (KucoinMarket::Futures, format!("/api/v1/contracts/{symbol}"))
            }
            "get_futures_ticker" => {
                normalize_symbol_query(&mut params, true);
                (KucoinMarket::Futures, FUTURES_TICKER.to_string())
            }
            "get_futures_orderbook" => {
                normalize_symbol_query(&mut params, true);
                let path = take_param(&mut params, "depth")
                    .map(|depth| format!("/api/v1/level2/depth{depth}"))
                    .unwrap_or_else(|| FUTURES_ORDERBOOK.to_string());
                (KucoinMarket::Futures, path)
            }
            "get_futures_public_trades" => {
                normalize_symbol_query(&mut params, true);
                (KucoinMarket::Futures, FUTURES_PUBLIC_TRADES.to_string())
            }
            "get_futures_kline" => {
                normalize_symbol_query(&mut params, true);
                normalize_futures_timeframe(&mut params)?;
                (KucoinMarket::Futures, FUTURES_KLINE.to_string())
            }
            "get_futures_open_interest" => {
                normalize_symbol_query(&mut params, true);
                (KucoinMarket::Spot, FUTURES_OPEN_INTEREST.to_string())
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported KuCoin public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, market, path, params, None, false)
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: &str,
    ) -> Result<HttpRequest> {
        if !matches!(
            method,
            HttpMethod::Get | HttpMethod::Post | HttpMethod::Put | HttpMethod::Delete
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported KuCoin HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = if matches!(method, HttpMethod::Get | HttpMethod::Delete) {
            url::form_urlencoded::Serializer::new(String::new())
                .extend_pairs(params)
                .finish()
        } else {
            String::new()
        };
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let body = if matches!(method, HttpMethod::Post | HttpMethod::Put) {
            body.unwrap_or_default()
        } else {
            Vec::new()
        };
        let base_url = match market {
            KucoinMarket::Futures => &self.futures_base_url,
            KucoinMarket::Spot => &self.spot_base_url,
        };
        let mut request = HttpRequest::new(method, base_url, &request_path)
            .header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Post | HttpMethod::Put) && !body.is_empty() {
            request.body = RequestBody::Raw(body.clone());
        }

        if signed {
            let (api_key, api_secret, encrypted_passphrase) = self.credentials()?;
            let canonical = format!(
                "{timestamp}{}{request_path}{}",
                http_method_name(method),
                String::from_utf8_lossy(&body)
            );
            let signature = hmac_sha256_base64(api_secret.as_bytes(), canonical.as_bytes())?;
            request
                .headers
                .insert("KC-API-KEY".to_string(), api_key.to_string());
            request.headers.insert("KC-API-SIGN".to_string(), signature);
            request
                .headers
                .insert("KC-API-TIMESTAMP".to_string(), timestamp.to_string());
            request.headers.insert(
                "KC-API-PASSPHRASE".to_string(),
                encrypted_passphrase.to_string(),
            );
            request
                .headers
                .insert("KC-API-KEY-VERSION".to_string(), "2".to_string());
        }

        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.encrypted_passphrase) {
            (Some(api_key), Some(api_secret), Some(encrypted_passphrase)) => {
                Ok((api_key, api_secret, encrypted_passphrase))
            }
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key, Secret, and Passphrase.".to_string(),
            )),
        }
    }
}

fn take_param(params: &mut Vec<(String, String)>, key: &str) -> Option<String> {
    params
        .iter()
        .position(|(param_key, _)| param_key == key)
        .map(|index| params.remove(index).1)
}

fn take_symbol(params: &mut Vec<(String, String)>, futures: bool) -> Result<String> {
    take_param(params, "symbol")
        .or_else(|| {
            take_param(params, "product_symbol").map(|value| exchange_symbol(&value, futures))
        })
        .ok_or_else(|| DcexError::InvalidInput("KuCoin symbol is required.".to_string()))
}

fn normalize_symbol_query(params: &mut Vec<(String, String)>, futures: bool) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" {
            *key = "symbol".to_string();
            *value = exchange_symbol(value, futures);
        } else if key == "symbol" {
            *value = exchange_symbol(value, futures);
        }
    }
}

fn exchange_symbol(product_symbol: &str, futures: bool) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) if futures => format!("{base}{quote}"),
        (Some(base), Some(quote), Some(_kind)) => format!("{base}-{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn normalize_spot_timeframe(params: &mut Vec<(String, String)>) -> Result<()> {
    for (key, value) in params.iter_mut() {
        if key == "timeframe" {
            *key = "type".to_string();
            *value = kucoin_spot_timeframe(value)?;
        }
    }
    Ok(())
}

fn normalize_futures_timeframe(params: &mut Vec<(String, String)>) -> Result<()> {
    for (key, value) in params.iter_mut() {
        if key == "timeframe" {
            *key = "granularity".to_string();
            *value = kucoin_futures_granularity(value)?.to_string();
        }
    }
    Ok(())
}

fn kucoin_spot_timeframe(timeframe: &str) -> Result<String> {
    let value = match timeframe {
        "1m" => "1min",
        "3m" => "3min",
        "5m" => "5min",
        "15m" => "15min",
        "30m" => "30min",
        "1h" => "1hour",
        "2h" => "2hour",
        "4h" => "4hour",
        "6h" => "6hour",
        "8h" => "8hour",
        "12h" => "12hour",
        "1d" => "1day",
        "1w" => "1week",
        "1M" => "1month",
        _ => {
            return Err(DcexError::InvalidInput(
                "timeframe not supported".to_string(),
            ))
        }
    };
    Ok(value.to_string())
}

fn kucoin_futures_granularity(timeframe: &str) -> Result<u64> {
    match timeframe {
        "1m" => Ok(60),
        "5m" => Ok(300),
        "15m" => Ok(900),
        "30m" => Ok(1800),
        "1h" => Ok(3600),
        "2h" => Ok(7200),
        "4h" => Ok(14400),
        "8h" => Ok(28800),
        "12h" => Ok(43200),
        "1d" => Ok(86400),
        "1w" => Ok(604800),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    if data
        .as_object()
        .and_then(|object| object.get("code"))
        .and_then(Value::as_str)
        != Some("200000")
    {
        let code = data
            .as_object()
            .and_then(|object| object.get("code"))
            .map(json_value_string)
            .unwrap_or_else(|| "Unknown".to_string());
        let message = data
            .as_object()
            .and_then(|object| object.get("msg"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("KUCOIN API Error: [{code}] {message}"),
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

const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signature_and_passphrase_match_python_vectors() {
        let client = KucoinClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            Some("passphrase".to_string()),
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                KucoinMarket::Spot,
                "/api/v1/accounts",
                vec![
                    ("currency".to_string(), "BTC-USDT".to_string()),
                    ("type".to_string(), "trade".to_string()),
                ],
                None,
                true,
                "1700000000000",
            )
            .expect("request");

        assert_eq!(
            request.headers.get("KC-API-SIGN").map(String::as_str),
            Some("U7HJOAA1P91EHj3Qgp0soO+BbskRIYBAUVt+Lrmrbvk=")
        );
        assert_eq!(
            request.headers.get("KC-API-PASSPHRASE").map(String::as_str),
            Some("BiepdEOmmFVpiE0m2qjSxvqjTlOfQ1XzmhElRgdHLwI=")
        );
    }
}
