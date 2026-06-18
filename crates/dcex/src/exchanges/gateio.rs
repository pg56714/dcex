use std::time::Duration;

use crate::crypto::{hmac_sha512_hex, sha512_hex};
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://api.gateio.ws";
const API_PREFIX: &str = "/api/v4";

#[derive(Clone)]
pub struct GateioClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
}

impl GateioClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(api_key, api_secret, timeout, BASE_URL.to_string())
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
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
        response.ensure_success()?;
        let data = response.json()?;
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
        let timestamp = unix_timestamp_ms()? / 1000;
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
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let path = match method_name {
            "get_all_futures_contracts" => {
                let settle = take_settle(&mut params);
                format!("{API_PREFIX}/futures/{settle}/contracts")
            }
            "get_a_single_futures_contract" => {
                let settle = take_settle(&mut params);
                let contract = take_contract(&mut params)?;
                format!("{API_PREFIX}/futures/{settle}/contracts/{contract}")
            }
            "get_contract_order_book" => {
                let settle = take_settle(&mut params);
                let market_path = take_market_path(&mut params, "futures")?;
                normalize_contract_query(&mut params);
                format!("{API_PREFIX}/{market_path}/{settle}/order_book")
            }
            "get_contract_kline" => {
                let settle = take_settle(&mut params);
                let market_path = take_market_path(&mut params, "futures")?;
                normalize_contract_query(&mut params);
                format!("{API_PREFIX}/{market_path}/{settle}/candlesticks")
            }
            "get_contract_list_tickers" => {
                let settle = take_settle(&mut params);
                let market_path = take_market_path(&mut params, "futures")?;
                normalize_contract_query(&mut params);
                format!("{API_PREFIX}/{market_path}/{settle}/tickers")
            }
            "get_futures_funding_rate_history" => {
                let settle = take_settle(&mut params);
                normalize_contract_query(&mut params);
                format!("{API_PREFIX}/futures/{settle}/funding_rate")
            }
            "get_futures_contract_stats" => {
                let settle = take_settle(&mut params);
                normalize_contract_query(&mut params);
                format!("{API_PREFIX}/futures/{settle}/contract_stats")
            }
            "get_all_delivery_contracts" => {
                let settle = take_settle(&mut params);
                format!("{API_PREFIX}/delivery/{settle}/contracts")
            }
            "get_spot_all_currency_pairs" => {
                format!("{API_PREFIX}/spot/currency_pairs")
            }
            "get_spot_order_book" => {
                normalize_currency_pair_query(&mut params);
                format!("{API_PREFIX}/spot/order_book")
            }
            "get_spot_kline" => {
                normalize_currency_pair_query(&mut params);
                format!("{API_PREFIX}/spot/candlesticks")
            }
            "get_spot_list_tickers" => {
                normalize_currency_pair_query(&mut params);
                format!("{API_PREFIX}/spot/tickers")
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Gate.io public method: {method_name}"
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
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        let query = params
            .iter()
            .map(|(key, value)| format!("{key}={value}"))
            .collect::<Vec<_>>()
            .join("&");
        let request_path = if query.is_empty() {
            path.clone()
        } else {
            format!("{path}?{query}")
        };
        let mut request = HttpRequest::new(method, &self.base_url, request_path)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
        if matches!(
            method,
            HttpMethod::Post | HttpMethod::Put | HttpMethod::Patch
        ) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret) = self.credentials()?;
            let body = body.as_deref().unwrap_or_default();
            let canonical = format!(
                "{}\n{path}\n{query}\n{}\n{timestamp}",
                http_method_name(method),
                sha512_hex(body)
            );
            let signature = hmac_sha512_hex(api_secret.as_bytes(), canonical.as_bytes())?;
            request
                .headers
                .insert("KEY".to_string(), api_key.to_string());
            request
                .headers
                .insert("Timestamp".to_string(), timestamp.to_string());
            request.headers.insert("SIGN".to_string(), signature);
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

fn take_param(params: &mut Vec<(String, String)>, key: &str) -> Option<String> {
    params
        .iter()
        .position(|(param_key, _)| param_key == key)
        .map(|index| params.remove(index).1)
}

fn take_settle(params: &mut Vec<(String, String)>) -> String {
    take_param(params, "settle")
        .or_else(|| take_param(params, "ccy"))
        .unwrap_or_else(|| "usdt".to_string())
}

fn take_market_path(params: &mut Vec<(String, String)>, default: &str) -> Result<String> {
    let market_path = take_param(params, "path").unwrap_or_else(|| default.to_string());
    match market_path.as_str() {
        "futures" | "delivery" => Ok(market_path),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io market path: {market_path}"
        ))),
    }
}

fn take_contract(params: &mut Vec<(String, String)>) -> Result<String> {
    take_param(params, "contract")
        .or_else(|| take_param(params, "product_symbol").map(|value| exchange_symbol(&value)))
        .ok_or_else(|| DcexError::InvalidInput("Gate.io contract is required.".to_string()))
}

fn normalize_contract_query(params: &mut Vec<(String, String)>) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" {
            *key = "contract".to_string();
            *value = exchange_symbol(value);
        } else if key == "contract" {
            *value = exchange_symbol(value);
        }
    }
}

fn normalize_currency_pair_query(params: &mut Vec<(String, String)>) {
    for (key, value) in params.iter_mut() {
        if key == "product_symbol" || key == "symbol" {
            *key = "currency_pair".to_string();
            *value = exchange_symbol(value);
        } else if key == "currency_pair" {
            *value = exchange_symbol(value);
        }
    }
}

fn exchange_symbol(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}_{quote}"),
        _ => product_symbol.to_string(),
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
    fn signature_matches_python_vector() {
        let client = GateioClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Post,
                "/api/v4/spot/orders",
                vec![("a".to_string(), "1".to_string())],
                Some(br#"{"b":"2"}"#.to_vec()),
                true,
                1_700_000_000,
            )
            .expect("request");
        assert_eq!(
            request.headers.get("SIGN").map(String::as_str),
            Some(
                "3a314366c1367344b6abbad3a7f0b0519a5f1f606acde4c269a8cada67d7ddbd\
33504564f284bd0f8f7be971075a6ef0f8a47f95f310cad579fdb483f0330b7a"
            )
        );
    }
}
