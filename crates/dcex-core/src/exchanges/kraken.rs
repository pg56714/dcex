use std::time::{Duration, SystemTime, UNIX_EPOCH};

use base64::Engine;
use serde_json::Value;

use crate::crypto::{hmac_sha512_base64, sha256};
use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const SPOT_BASE_URL: &str = "https://api.kraken.com";
const FUTURES_BASE_URL: &str = "https://futures.kraken.com";
const SPOT_SERVER_TIME: &str = "/0/public/Time";
const SPOT_ASSET_PAIRS: &str = "/0/public/AssetPairs";
const SPOT_TICKER: &str = "/0/public/Ticker";
const SPOT_ORDERBOOK: &str = "/0/public/Depth";
const SPOT_PUBLIC_TRADES: &str = "/0/public/Trades";
const SPOT_OHLC: &str = "/0/public/OHLC";
const FUTURES_INSTRUMENTS: &str = "/derivatives/api/v3/instruments";
const FUTURES_TICKERS: &str = "/derivatives/api/v3/tickers";
const FUTURES_ORDERBOOK: &str = "/derivatives/api/v3/orderbook";
const FUTURES_PUBLIC_TRADES: &str = "/derivatives/api/v3/history";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum KrakenAuth {
    Futures,
    Spot,
}

#[derive(Clone)]
pub struct KrakenClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    spot_api_key: Option<String>,
    spot_api_secret: Option<String>,
    futures_api_key: Option<String>,
    futures_api_secret: Option<String>,
}

impl KrakenClient {
    pub fn new(
        spot_api_key: Option<String>,
        spot_api_secret: Option<String>,
        futures_api_key: Option<String>,
        futures_api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            spot_api_key,
            spot_api_secret,
            futures_api_key,
            futures_api_secret,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    #[allow(clippy::too_many_arguments)]
    pub fn with_base_urls(
        spot_api_key: Option<String>,
        spot_api_secret: Option<String>,
        futures_api_key: Option<String>,
        futures_api_secret: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            spot_api_key,
            spot_api_secret,
            futures_api_key,
            futures_api_secret,
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        auth: KrakenAuth,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        json_body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, auth, path, params, json_body, signed)
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
        auth: KrakenAuth,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        json_body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let nonce = unix_timestamp_ns()?.to_string();
        let request = self.build_request(method, auth, path, params, json_body, signed, &nonce)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        auth: KrakenAuth,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        json_body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, auth, path, params, json_body, signed)
                .await
        })
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (auth, path) = match method_name {
            "get_server_time" => (KrakenAuth::Spot, SPOT_SERVER_TIME.to_string()),
            "get_spot_asset_pairs" => (KrakenAuth::Spot, SPOT_ASSET_PAIRS.to_string()),
            "get_spot_ticker" => {
                normalize_symbol_query(&mut params, "pair", "");
                (KrakenAuth::Spot, SPOT_TICKER.to_string())
            }
            "get_spot_orderbook" => {
                normalize_symbol_query(&mut params, "pair", "");
                (KrakenAuth::Spot, SPOT_ORDERBOOK.to_string())
            }
            "get_spot_public_trades" => {
                normalize_symbol_query(&mut params, "pair", "");
                (KrakenAuth::Spot, SPOT_PUBLIC_TRADES.to_string())
            }
            "get_spot_kline" => {
                normalize_symbol_query(&mut params, "pair", "");
                (KrakenAuth::Spot, SPOT_OHLC.to_string())
            }
            "get_futures_instruments" => (KrakenAuth::Futures, FUTURES_INSTRUMENTS.to_string()),
            "get_futures_tickers" => {
                normalize_symbol_query(&mut params, "symbol", "PF_");
                (KrakenAuth::Futures, FUTURES_TICKERS.to_string())
            }
            "get_futures_orderbook" => {
                normalize_symbol_query(&mut params, "symbol", "PF_");
                (KrakenAuth::Futures, FUTURES_ORDERBOOK.to_string())
            }
            "get_futures_public_trades" => {
                normalize_symbol_query(&mut params, "symbol", "PF_");
                (KrakenAuth::Futures, FUTURES_PUBLIC_TRADES.to_string())
            }
            "get_futures_kline" => {
                let tick_type =
                    take_param(&mut params, "tick_type").unwrap_or_else(|| "trade".to_string());
                let symbol = take_symbol(&mut params, "PF_")?;
                let resolution = take_param(&mut params, "timeframe")
                    .ok_or_else(|| DcexError::InvalidInput("timeframe is required.".to_string()))?;
                (
                    KrakenAuth::Futures,
                    format!("/api/charts/v1/{tick_type}/{symbol}/{resolution}"),
                )
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Kraken public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, auth, path, params, None, false)
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        auth: KrakenAuth,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        json_body: Option<Vec<u8>>,
        signed: bool,
        nonce: &str,
    ) -> Result<HttpRequest> {
        if !matches!(
            method,
            HttpMethod::Get | HttpMethod::Post | HttpMethod::Put | HttpMethod::Delete
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Kraken HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let encoded_query = encode_params(&params);
        let base_url = match auth {
            KrakenAuth::Futures => &self.futures_base_url,
            KrakenAuth::Spot => &self.spot_base_url,
        };
        let mut request =
            HttpRequest::new(method, base_url, &path).header("Accept", "application/json");

        if !signed {
            if !encoded_query.is_empty() {
                request.path = format!("{path}?{encoded_query}");
            }
            if matches!(method, HttpMethod::Post | HttpMethod::Put) {
                if let Some(json_body) = json_body {
                    request
                        .headers
                        .insert("Content-Type".to_string(), "application/json".to_string());
                    request.body = RequestBody::Raw(json_body);
                }
            }
            return Ok(request);
        }

        request.headers.insert(
            "Content-Type".to_string(),
            "application/x-www-form-urlencoded".to_string(),
        );
        match auth {
            KrakenAuth::Spot => {
                if method != HttpMethod::Post {
                    return Err(DcexError::InvalidInput(
                        "Signed Kraken spot requests must use POST.".to_string(),
                    ));
                }
                let (api_key, api_secret) = self.spot_credentials()?;
                let mut payload = vec![("nonce".to_string(), nonce.to_string())];
                payload.extend(params);
                let encoded_payload = encode_params(&payload);
                let signature = spot_signature(&path, nonce, &encoded_payload, api_secret)?;
                request
                    .headers
                    .insert("API-Key".to_string(), api_key.to_string());
                request.headers.insert("API-Sign".to_string(), signature);
                request.body = RequestBody::Raw(encoded_payload.into_bytes());
            }
            KrakenAuth::Futures => {
                let (api_key, api_secret) = self.futures_credentials()?;
                let signature = futures_signature(&path, &encoded_query, nonce, api_secret)?;
                request
                    .headers
                    .insert("APIKey".to_string(), api_key.to_string());
                request.headers.insert("Authent".to_string(), signature);
                request
                    .headers
                    .insert("Nonce".to_string(), nonce.to_string());
                if matches!(method, HttpMethod::Get | HttpMethod::Delete) {
                    if !encoded_query.is_empty() {
                        request.path = format!("{path}?{encoded_query}");
                    }
                } else if !encoded_query.is_empty() {
                    request.body = RequestBody::Raw(encoded_query.into_bytes());
                }
            }
        }
        Ok(request)
    }

    fn spot_credentials(&self) -> Result<(&str, &str)> {
        match (&self.spot_api_key, &self.spot_api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed Kraken spot requests require spot_api_key and spot_api_secret.".to_string(),
            )),
        }
    }

    fn futures_credentials(&self) -> Result<(&str, &str)> {
        match (&self.futures_api_key, &self.futures_api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed Kraken futures requests require futures_api_key and futures_api_secret."
                    .to_string(),
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

fn take_symbol(params: &mut Vec<(String, String)>, futures_prefix: &str) -> Result<String> {
    take_param(params, "symbol")
        .or_else(|| {
            take_param(params, "product_symbol")
                .map(|value| exchange_symbol(&value, futures_prefix))
        })
        .ok_or_else(|| DcexError::InvalidInput("Kraken symbol is required.".to_string()))
}

fn normalize_symbol_query(
    params: &mut Vec<(String, String)>,
    target_key: &str,
    futures_prefix: &str,
) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" {
            *key = target_key.to_string();
            *value = exchange_symbol(value, futures_prefix);
        } else if key == target_key {
            *value = exchange_symbol(value, futures_prefix);
        }
    }
}

fn exchange_symbol(product_symbol: &str, futures_prefix: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => {
            let base = kraken_asset(base);
            let quote = kraken_asset(quote);
            format!("{futures_prefix}{base}{quote}")
        }
        _ => product_symbol.to_string(),
    }
}

fn kraken_asset(asset: &str) -> &str {
    match asset {
        "BTC" => "XBT",
        other => other,
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    response.ensure_success()?;
    let data = response.json()?;
    if let Some(message) = kraken_error_message(&data) {
        return Err(DcexError::HttpStatus {
            status: response.status,
            message,
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    Ok(data)
}

fn kraken_error_message(data: &Value) -> Option<String> {
    let object = data.as_object()?;
    match object.get("error") {
        Some(Value::Array(errors)) if !errors.is_empty() => {
            return Some(
                errors
                    .iter()
                    .map(json_value_string)
                    .collect::<Vec<_>>()
                    .join(", "),
            );
        }
        Some(Value::String(error)) if !error.is_empty() => return Some(error.clone()),
        _ => {}
    }
    if object.get("result").and_then(Value::as_str) == Some("error") {
        let message = object
            .get("errors")
            .or_else(|| object.get("error"))
            .map(json_value_string)
            .unwrap_or_else(|| "Kraken API error".to_string());
        return Some(message);
    }
    None
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        Value::Array(values) => values
            .iter()
            .map(json_value_string)
            .collect::<Vec<_>>()
            .join(", "),
        _ => value.to_string(),
    }
}

fn encode_params(params: &[(String, String)]) -> String {
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(
            params
                .iter()
                .map(|(key, value)| (key.as_str(), value.as_str())),
        )
        .finish()
}

fn decode_secret(api_secret: &str) -> Result<Vec<u8>> {
    base64::engine::general_purpose::STANDARD
        .decode(api_secret)
        .map_err(|error| DcexError::InvalidInput(format!("invalid Kraken API secret: {error}")))
}

fn spot_signature(
    path: &str,
    nonce: &str,
    encoded_payload: &str,
    api_secret: &str,
) -> Result<String> {
    let digest = sha256(format!("{nonce}{encoded_payload}").as_bytes());
    let mut message = Vec::with_capacity(path.len() + digest.len());
    message.extend_from_slice(path.as_bytes());
    message.extend_from_slice(&digest);
    hmac_sha512_base64(&decode_secret(api_secret)?, &message)
}

fn futures_signature(path: &str, post_data: &str, nonce: &str, api_secret: &str) -> Result<String> {
    let auth_path = path.strip_prefix("/derivatives").unwrap_or(path);
    let digest = sha256(format!("{post_data}{nonce}{auth_path}").as_bytes());
    hmac_sha512_base64(&decode_secret(api_secret)?, &digest)
}

fn unix_timestamp_ns() -> Result<u128> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_nanos())
        .map_err(|error| DcexError::Runtime(error.to_string()))
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

    const SECRET: &str = "c2VjcmV0";
    const NONCE: &str = "1700000000000000000";

    #[test]
    fn spot_signature_matches_python_vector() {
        assert_eq!(
            spot_signature(
                "/0/private/Balance",
                NONCE,
                "nonce=1700000000000000000&asset=BTC+USD",
                SECRET,
            )
            .expect("signature"),
            "WEQePGAjbQaKqtYh0z8ylm5D/0D60D6FAQXlHzu7dDclIHTnRqYoAijaRpRtwLIoj4hnPnEPFO2nXwS+c+BhPQ=="
        );
    }

    #[test]
    fn futures_signature_matches_python_vector() {
        assert_eq!(
            futures_signature(
                "/derivatives/api/v3/sendorder",
                "symbol=PI_XBTUSD&side=buy",
                NONCE,
                SECRET,
            )
            .expect("signature"),
            "W2YL8mj+KExVX/X6fTAPvwlPPo6EP14ISry2Bv5BfJsBu4tDy6PUc1nVNu3OKXcJXrliaG19axFphls37F14zQ=="
        );
    }
}
