use std::time::Duration;

use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://api.mexc.com";
const SPOT_PING: &str = "/api/v3/ping";
const SPOT_TIME: &str = "/api/v3/time";
const SPOT_DEFAULT_SYMBOLS: &str = "/api/v3/defaultSymbols";
const SPOT_EXCHANGE_INFO: &str = "/api/v3/exchangeInfo";
const SPOT_ORDERBOOK: &str = "/api/v3/depth";
const SPOT_RECENT_TRADES: &str = "/api/v3/trades";
const SPOT_AGG_TRADES: &str = "/api/v3/aggTrades";
const SPOT_KLINES: &str = "/api/v3/klines";
const SPOT_AVG_PRICE: &str = "/api/v3/avgPrice";
const SPOT_TICKER_24HR: &str = "/api/v3/ticker/24hr";
const SPOT_TICKER_PRICE: &str = "/api/v3/ticker/price";
const SPOT_BOOK_TICKER: &str = "/api/v3/ticker/bookTicker";
const CONTRACT_PING: &str = "/api/v1/contract/ping";
const CONTRACT_DETAIL: &str = "/api/v1/contract/detail";
const CONTRACT_TICKER: &str = "/api/v1/contract/ticker";
const CONTRACT_RISK_REVERSE: &str = "/api/v1/contract/risk_reverse";
const CONTRACT_RISK_REVERSE_HISTORY: &str = "/api/v1/contract/risk_reverse/history";
const CONTRACT_FUNDING_RATE_HISTORY: &str = "/api/v1/contract/funding_rate/history";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MexcApi {
    Contract,
    Spot,
}

#[derive(Clone)]
pub struct MexcClient {
    transport: AsyncHttpClient,
    base_url: String,
    contract_base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
}

impl MexcClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            timeout,
            BASE_URL.to_string(),
            BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        base_url: String,
        contract_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            contract_base_url,
            api_key,
            api_secret,
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        api: MexcApi,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, api, path, params, body, signed)
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
        api: MexcApi,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp_ms = unix_timestamp_ms()?;
        let request = self.build_request(method, api, path, params, body, signed, timestamp_ms)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        api: MexcApi,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, api, path, params, body, signed)
                .await
        })
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (api, path) = match method_name {
            "ping" => (MexcApi::Spot, SPOT_PING.to_string()),
            "get_spot_time" => (MexcApi::Spot, SPOT_TIME.to_string()),
            "get_spot_default_symbols" => (MexcApi::Spot, SPOT_DEFAULT_SYMBOLS.to_string()),
            "get_spot_exchange_info" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_EXCHANGE_INFO.to_string())
            }
            "get_spot_orderbook" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_ORDERBOOK.to_string())
            }
            "get_spot_recent_trades" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_RECENT_TRADES.to_string())
            }
            "get_spot_agg_trades" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_AGG_TRADES.to_string())
            }
            "get_spot_klines" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_KLINES.to_string())
            }
            "get_spot_avg_price" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_AVG_PRICE.to_string())
            }
            "get_spot_ticker_24hr" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_TICKER_24HR.to_string())
            }
            "get_spot_ticker_price" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_TICKER_PRICE.to_string())
            }
            "get_spot_book_ticker" => {
                normalize_symbol_query(&mut params, "");
                (MexcApi::Spot, SPOT_BOOK_TICKER.to_string())
            }
            "get_contract_time" => (MexcApi::Contract, CONTRACT_PING.to_string()),
            "get_contract_details" => {
                normalize_symbol_query(&mut params, "_");
                (MexcApi::Contract, CONTRACT_DETAIL.to_string())
            }
            "get_contract_ticker" => {
                normalize_symbol_query(&mut params, "_");
                (MexcApi::Contract, CONTRACT_TICKER.to_string())
            }
            "get_contract_depth" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/depth/{symbol}"),
                )
            }
            "get_contract_depth_commits" => {
                let symbol = take_symbol(&mut params, "_")?;
                let limit = take_param(&mut params, "limit").unwrap_or_else(|| "20".to_string());
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/depth_commits/{symbol}/{limit}"),
                )
            }
            "get_contract_index_price" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/index_price/{symbol}"),
                )
            }
            "get_contract_fair_price" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/fair_price/{symbol}"),
                )
            }
            "get_contract_funding_rate" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/funding_rate/{symbol}"),
                )
            }
            "get_contract_kline" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/kline/{symbol}"),
                )
            }
            "get_contract_index_price_kline" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/kline/index_price/{symbol}"),
                )
            }
            "get_contract_fair_price_kline" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/kline/fair_price/{symbol}"),
                )
            }
            "get_contract_deals" => {
                let symbol = take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/deals/{symbol}"),
                )
            }
            "get_contract_risk_reverse" => (MexcApi::Contract, CONTRACT_RISK_REVERSE.to_string()),
            "get_contract_risk_reverse_history" => {
                normalize_symbol_query(&mut params, "_");
                (MexcApi::Contract, CONTRACT_RISK_REVERSE_HISTORY.to_string())
            }
            "get_contract_funding_rate_history" => {
                normalize_symbol_query(&mut params, "_");
                (MexcApi::Contract, CONTRACT_FUNDING_RATE_HISTORY.to_string())
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, api, path, params, None, false)
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        api: MexcApi,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp_ms: u64,
    ) -> Result<HttpRequest> {
        let base_url = match api {
            MexcApi::Contract => &self.contract_base_url,
            MexcApi::Spot => &self.base_url,
        };
        let mut request =
            HttpRequest::new(method, base_url, path).header("Content-Type", "application/json");
        match api {
            MexcApi::Spot => {
                if signed {
                    let (api_key, api_secret) = self.credentials()?;
                    if !params.iter().any(|(key, _)| key == "timestamp") {
                        params.push(("timestamp".to_string(), timestamp_ms.to_string()));
                    }
                    let signature =
                        hmac_sha256_hex(api_secret.as_bytes(), encode_params(&params).as_bytes())?;
                    params.push(("signature".to_string(), signature));
                    request
                        .headers
                        .insert("X-MEXC-APIKEY".to_string(), api_key.to_string());
                }
                request.query = params;
            }
            MexcApi::Contract => {
                if signed {
                    let (api_key, api_secret) = self.credentials()?;
                    let request_time = timestamp_ms.to_string();
                    let request_param = if matches!(method, HttpMethod::Get | HttpMethod::Delete) {
                        params.sort_by(|left, right| left.0.cmp(&right.0));
                        encode_params(&params)
                    } else {
                        String::from_utf8(body.clone().unwrap_or_default())
                            .map_err(|error| DcexError::InvalidInput(error.to_string()))?
                    };
                    let payload = format!("{api_key}{request_time}{request_param}");
                    let signature = hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())?;
                    request
                        .headers
                        .insert("ApiKey".to_string(), api_key.to_string());
                    request
                        .headers
                        .insert("Request-Time".to_string(), request_time);
                    request.headers.insert("Signature".to_string(), signature);
                }
                if matches!(method, HttpMethod::Get | HttpMethod::Delete) || !signed {
                    request.query = params;
                }
                if !matches!(method, HttpMethod::Get | HttpMethod::Delete) {
                    request.body = body.map(RequestBody::Raw).unwrap_or_default();
                }
            }
        }
        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str)> {
        match (&self.api_key, &self.api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed MEXC requests require api_key and api_secret.".to_string(),
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

fn take_symbol(params: &mut Vec<(String, String)>, separator: &str) -> Result<String> {
    take_param(params, "symbol")
        .or_else(|| {
            take_param(params, "product_symbol").map(|value| exchange_symbol(&value, separator))
        })
        .ok_or_else(|| DcexError::InvalidInput("MEXC symbol is required.".to_string()))
}

fn normalize_symbol_query(params: &mut Vec<(String, String)>, separator: &str) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" {
            *key = "symbol".to_string();
            *value = exchange_symbol(value, separator);
        } else if key == "symbol" {
            *value = exchange_symbol(value, separator);
        }
    }
}

fn exchange_symbol(product_symbol: &str, separator: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{separator}{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    response.ensure_success()?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        let success = object.get("success").and_then(Value::as_bool);
        let code_is_error =
            code.is_some_and(|code| !matches!(json_value_string(code).as_str(), "0" | "200"));
        if success == Some(false) || code_is_error {
            let message = object
                .get("msg")
                .or_else(|| object.get("message"))
                .and_then(Value::as_str)
                .unwrap_or("Unknown error");
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!(
                    "MEXC API Error: [{}] {message}",
                    code.map(json_value_string)
                        .unwrap_or_else(|| "null".to_string())
                ),
                headers: response
                    .headers
                    .iter()
                    .map(|(key, value)| (key.clone(), value.clone()))
                    .collect(),
            });
        }
    }
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

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn client() -> MexcClient {
        MexcClient::new(
            Some("api-key".to_string()),
            Some("secret".to_string()),
            Duration::from_secs(1),
        )
        .expect("client")
    }

    #[test]
    fn spot_signature_matches_python_protocol() {
        let request = client()
            .build_request(
                HttpMethod::Get,
                MexcApi::Spot,
                "/api/v3/order",
                vec![("symbol".to_string(), "BTCUSDT".to_string())],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.query,
            vec![
                ("symbol".to_string(), "BTCUSDT".to_string()),
                ("timestamp".to_string(), "1700000000000".to_string()),
                (
                    "signature".to_string(),
                    "6244d11c958f45ac56733152cb3cb1831d23a2b3709b3a88b8b42a072aceb410".to_string(),
                ),
            ]
        );
    }

    #[test]
    fn contract_signature_uses_exact_json_body() {
        let request = client()
            .build_request(
                HttpMethod::Post,
                MexcApi::Contract,
                "/api/v1/private/order/cancel",
                Vec::new(),
                Some(br#"[{"orderId":"1"},{"orderId":"2"}]"#.to_vec()),
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("Signature").map(String::as_str),
            Some("5767f5e6ba9a1f7bf0e35db1de5ecf52d00218b3f2bc2939b4d5ed5758bb0944")
        );
        assert_eq!(
            request.body,
            RequestBody::Raw(br#"[{"orderId":"1"},{"orderId":"2"}]"#.to_vec())
        );
    }
}
