use std::time::Duration;

use serde_json::Value;

use crate::crypto::hmac_sha256_base64;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://openapi.okx.com";
const PUBLIC_INSTRUMENTS: &str = "/api/v5/public/instruments";
const PUBLIC_FUNDING_RATE: &str = "/api/v5/public/funding-rate";
const PUBLIC_FUNDING_RATE_HISTORY: &str = "/api/v5/public/funding-rate-history";
const PUBLIC_OPEN_INTEREST: &str = "/api/v5/public/open-interest";
const PUBLIC_POSITION_TIERS: &str = "/api/v5/public/position-tiers";
const PUBLIC_TRADING_DATA_SUPPORT_COIN: &str = "/api/v5/rubik/stat/trading-data/support-coin";
const PUBLIC_TAKER_VOLUME: &str = "/api/v5/rubik/stat/taker-volume";
const PUBLIC_CONTRACT_TAKER_VOLUME: &str = "/api/v5/rubik/stat/taker-volume-contract";
const PUBLIC_LONG_SHORT_RATIO: &str = "/api/v5/rubik/stat/contracts/long-short-account-ratio";
const PUBLIC_CONTRACT_LONG_SHORT_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract";
const PUBLIC_TOP_TRADER_LONG_SHORT_ACCOUNT_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader";
const PUBLIC_TOP_TRADER_LONG_SHORT_POSITION_RATIO: &str =
    "/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader";
const PUBLIC_CONTRACTS_OPEN_INTEREST_VOLUME: &str =
    "/api/v5/rubik/stat/contracts/open-interest-volume";
const PUBLIC_CONTRACT_OPEN_INTEREST_HISTORY: &str =
    "/api/v5/rubik/stat/contracts/open-interest-history";
const MARKET_CANDLES: &str = "/api/v5/market/candles";
const MARKET_ORDERBOOK: &str = "/api/v5/market/books";
const MARKET_TICKERS: &str = "/api/v5/market/tickers";
const MARKET_PUBLIC_TRADES: &str = "/api/v5/market/trades";

#[derive(Clone)]
pub struct OkxClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    passphrase: Option<String>,
    flag: String,
}

impl OkxClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        flag: String,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            api_key,
            api_secret,
            passphrase,
            flag,
            timeout,
            BASE_URL.to_string(),
        )
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        flag: String,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
            passphrase,
            flag,
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
        let timestamp = iso_timestamp(unix_timestamp_ms()?);
        let request = self.build_request(method, path, params, body, signed, &timestamp)?;
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
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let path = match method_name {
            "get_candles_ticks" => {
                normalize_inst_id_query(&mut params);
                MARKET_CANDLES
            }
            "get_orderbook" => {
                normalize_inst_id_query(&mut params);
                MARKET_ORDERBOOK
            }
            "get_tickers" => MARKET_TICKERS,
            "get_public_trades" => {
                normalize_inst_id_query(&mut params);
                MARKET_PUBLIC_TRADES
            }
            "get_public_instruments" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_INSTRUMENTS
            }
            "get_funding_rate" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_FUNDING_RATE
            }
            "get_funding_rate_history" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_FUNDING_RATE_HISTORY
            }
            "get_open_interest" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_OPEN_INTEREST
            }
            "get_position_tiers" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_POSITION_TIERS
            }
            "get_trading_data_support_coin" => PUBLIC_TRADING_DATA_SUPPORT_COIN,
            "get_taker_volume" => PUBLIC_TAKER_VOLUME,
            "get_contract_taker_volume" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_CONTRACT_TAKER_VOLUME
            }
            "get_long_short_ratio" => PUBLIC_LONG_SHORT_RATIO,
            "get_contract_long_short_ratio" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_CONTRACT_LONG_SHORT_RATIO
            }
            "get_top_trader_long_short_account_ratio" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_TOP_TRADER_LONG_SHORT_ACCOUNT_RATIO
            }
            "get_top_trader_long_short_position_ratio" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_TOP_TRADER_LONG_SHORT_POSITION_RATIO
            }
            "get_contracts_open_interest_and_volume" => PUBLIC_CONTRACTS_OPEN_INTEREST_VOLUME,
            "get_contract_open_interest_history" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_CONTRACT_OPEN_INTEREST_HISTORY
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported OKX public method: {method_name}"
                )));
            }
        };
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
        timestamp: &str,
    ) -> Result<HttpRequest> {
        if !matches!(method, HttpMethod::Get | HttpMethod::Post) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported OKX HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = if method == HttpMethod::Get {
            params
                .iter()
                .filter(|(_, value)| !value.is_empty())
                .map(|(key, value)| format!("{key}={value}"))
                .collect::<Vec<_>>()
                .join("&")
        } else {
            String::new()
        };
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let body = if method == HttpMethod::Post {
            body.unwrap_or_default()
        } else {
            Vec::new()
        };

        let mut request = HttpRequest::new(method, &self.base_url, &request_path)
            .header("Content-Type", "application/json")
            .header("x-simulated-trading", &self.flag);

        if method == HttpMethod::Post {
            request.body = RequestBody::Raw(body.clone());
        }

        if signed {
            let (api_key, api_secret, passphrase) = self.credentials()?;
            let canonical = format!(
                "{timestamp}{}{request_path}{}",
                http_method_name(method),
                String::from_utf8_lossy(&body)
            );
            let signature = hmac_sha256_base64(api_secret.as_bytes(), canonical.as_bytes())?;
            request
                .headers
                .insert("OK-ACCESS-KEY".to_string(), api_key.to_string());
            request
                .headers
                .insert("OK-ACCESS-SIGN".to_string(), signature);
            request
                .headers
                .insert("OK-ACCESS-TIMESTAMP".to_string(), timestamp.to_string());
            request
                .headers
                .insert("OK-ACCESS-PASSPHRASE".to_string(), passphrase.to_string());
        }

        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.passphrase) {
            (Some(api_key), Some(api_secret), Some(passphrase)) => {
                Ok((api_key, api_secret, passphrase))
            }
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret and Passphrase.".to_string(),
            )),
        }
    }
}

fn normalize_inst_id_query(params: &mut Vec<(String, String)>) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" {
            *key = "instId".to_string();
            *value = exchange_symbol(value);
        } else if key == "instId" {
            *value = exchange_symbol(value);
        }
    }
}

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(kind)) if kind == "SPOT" => format!("{base}-{quote}"),
        (Some(base), Some(quote), Some(kind)) => format!("{base}-{quote}-{kind}"),
        _ => product_symbol.to_string(),
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    if !data.is_object() {
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Unexpected response type: {}", data_type_name(&data)),
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    if data
        .as_object()
        .and_then(|object| object.get("code"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string())
        != "0"
    {
        let (code, message) = okx_error_details(&data);
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("OKX API Error: [{code}] {message}"),
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

fn okx_error_details(data: &Value) -> (String, String) {
    let Some(object) = data.as_object() else {
        return ("Unknown".to_string(), "Unknown error".to_string());
    };
    let mut api_code = object
        .get("code")
        .map(json_value_string)
        .unwrap_or_else(|| "Unknown".to_string());
    let mut error_message = object
        .get("msg")
        .map(json_value_string)
        .unwrap_or_else(|| "Unknown error".to_string());
    if let Some(row) = object
        .get("data")
        .and_then(Value::as_array)
        .and_then(|rows| rows.first())
        .and_then(Value::as_object)
    {
        if let Some(code) = row
            .get("sCode")
            .map(json_value_string)
            .filter(|value| !value.is_empty())
        {
            api_code = code;
        }
        if let Some(message) = row
            .get("sMsg")
            .map(json_value_string)
            .filter(|value| !value.is_empty())
        {
            error_message = message;
        }
    }
    (api_code, error_message)
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

fn data_type_name(value: &Value) -> &'static str {
    match value {
        Value::Null => "null",
        Value::Bool(_) => "bool",
        Value::Number(_) => "number",
        Value::String(_) => "string",
        Value::Array(_) => "array",
        Value::Object(_) => "object",
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

fn iso_timestamp(timestamp_ms: u64) -> String {
    let seconds = timestamp_ms / 1_000;
    let milliseconds = timestamp_ms % 1_000;
    let days = (seconds / 86_400) as i64;
    let seconds_of_day = seconds % 86_400;
    let hour = seconds_of_day / 3_600;
    let minute = seconds_of_day % 3_600 / 60;
    let second = seconds_of_day % 60;

    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let day_of_era = z - era * 146_097;
    let year_of_era =
        (day_of_era - day_of_era / 1_460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let mut year = year_of_era + era * 400;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let month_prime = (5 * day_of_year + 2) / 153;
    let day = day_of_year - (153 * month_prime + 2) / 5 + 1;
    let month = month_prime + if month_prime < 10 { 3 } else { -9 };
    year += i64::from(month <= 2);

    format!("{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{milliseconds:03}Z")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn timestamp_matches_python_format() {
        assert_eq!(iso_timestamp(1_700_000_000_000), "2023-11-14T22:13:20.000Z");
    }

    #[test]
    fn signature_matches_python_vector() {
        let client = OkxClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            Some("passphrase".to_string()),
            "0".to_string(),
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/api/v5/account/balance",
                Vec::new(),
                None,
                true,
                "1700000000",
            )
            .expect("request");

        assert_eq!(
            request.headers.get("OK-ACCESS-SIGN").map(String::as_str),
            Some("Ls74ct2P5Xi0SXq7smDS5O2D8cy4VmItOq3VDxnTQYE=")
        );
    }
}
