use std::time::Duration;

use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://www.bitmex.com";
const INSTRUMENT_INFO: &str = "/api/v1/instrument";
const ACTIVE_INSTRUMENTS: &str = "/api/v1/instrument/active";
const ORDERBOOK: &str = "/api/v1/orderBook/L2";
const TRADE: &str = "/api/v1/trade";
const TICKER: &str = "/api/v1/quote/bucketed";
const KLINE: &str = "/api/v1/trade/bucketed";
const FUNDING: &str = "/api/v1/funding";
const LIQUIDATION: &str = "/api/v1/liquidation";

#[derive(Clone)]
pub struct BitmexClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
}

impl BitmexClient {
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
        let expires = unix_timestamp_ms()? / 1000 + 5;
        let request = self.build_request(method, path, params, body, signed, expires)?;
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

    pub async fn get_instrument_info(
        &self,
        product_symbol: Option<&str>,
        filter: Option<&str>,
        count: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional_symbol(&mut params, "symbol", product_symbol);
        push_optional(&mut params, "filter", filter);
        push_optional(&mut params, "count", count);
        let path = if params.is_empty() {
            ACTIVE_INSTRUMENTS
        } else {
            INSTRUMENT_INFO
        };
        self.public_get(path, params).await
    }

    pub async fn get_orderbook(
        &self,
        product_symbol: &str,
        depth: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), exchange_symbol(product_symbol))];
        push_optional(&mut params, "depth", depth);
        self.public_get(ORDERBOOK, params).await
    }

    pub async fn get_trades(&self, params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.public_get(TRADE, normalize_symbol_params(params))
            .await
    }

    pub async fn get_ticker(&self, params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.public_get(TICKER, normalize_symbol_params(params))
            .await
    }

    pub async fn get_kline(&self, params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.public_get(KLINE, normalize_symbol_params(params))
            .await
    }

    pub async fn get_funding(&self, params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.public_get(FUNDING, normalize_symbol_params(params))
            .await
    }

    pub async fn get_liquidations(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.public_get(LIQUIDATION, normalize_symbol_params(params))
            .await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let public_params = PublicParams(params);
        match method_name {
            "get_instrument_info" => {
                self.get_instrument_info(
                    public_params.get("product_symbol"),
                    public_params.get("filter"),
                    public_params.get("count"),
                )
                .await
            }
            "get_orderbook" => {
                self.get_orderbook(
                    public_params.required("product_symbol")?,
                    public_params.get("depth"),
                )
                .await
            }
            "get_trades" => self.get_trades(public_params.into_inner()).await,
            "get_ticker" => self.get_ticker(public_params.into_inner()).await,
            "get_kline" => self.get_kline(public_params.into_inner()).await,
            "get_funding" => self.get_funding(public_params.into_inner()).await,
            "get_liquidations" => self.get_liquidations(public_params.into_inner()).await,
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BitMEX public method: {method_name}"
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
        expires: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        let mut request = HttpRequest::new(method, &self.base_url, &path)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
        let full_path = if matches!(method, HttpMethod::Get) && !params.is_empty() {
            request.query = params;
            format!("{path}?{}", encode_params(&request.query))
        } else {
            path
        };
        if !matches!(method, HttpMethod::Get) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            if let (Some(api_key), Some(api_secret)) = (&self.api_key, &self.api_secret) {
                let body = String::from_utf8_lossy(body.as_deref().unwrap_or_default());
                let payload = format!("{}{full_path}{expires}{body}", http_method_name(method));
                let signature = hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())?;
                request
                    .headers
                    .insert("api-key".to_string(), api_key.clone());
                request
                    .headers
                    .insert("api-signature".to_string(), signature);
                request
                    .headers
                    .insert("api-expires".to_string(), expires.to_string());
            }
        }
        Ok(request)
    }
}

struct PublicParams(Vec<(String, String)>);

impl PublicParams {
    fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    fn into_inner(self) -> Vec<(String, String)> {
        self.0
    }
}

fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

fn push_optional_symbol(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), exchange_symbol(value)));
    }
}

fn normalize_symbol_params(params: Vec<(String, String)>) -> Vec<(String, String)> {
    params
        .into_iter()
        .map(|(key, value)| {
            if key == "symbol" || key == "product_symbol" {
                ("symbol".to_string(), exchange_symbol(&value))
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
    if response.status / 100 != 2 {
        let message = data
            .as_object()
            .and_then(|object| object.get("error"))
            .and_then(Value::as_object)
            .and_then(|error| error.get("message"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(crate::DcexError::HttpStatus {
            status: response.status,
            message: format!("BITMEX API Error: {message}"),
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
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
    fn signature_includes_encoded_query_path() {
        let client = BitmexClient::new(
            Some("api-key".to_string()),
            Some("test_api_secret_0000".to_string()),
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/api/v1/order",
                vec![("symbol".to_string(), "XBT USD".to_string())],
                None,
                true,
                1_700_000_005,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("api-signature").map(String::as_str),
            Some("905e6a49c2961c68bc44ba85b3357543b65aaac1e032d40531df86ecae67feeb")
        );
    }
}
