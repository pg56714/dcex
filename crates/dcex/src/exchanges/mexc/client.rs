use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{BASE_URL, CONTRACT_BASE_URL};
use super::params::{
    exchange_symbol_fallback, insert_optional_string, is_canonical_product_symbol, MexcParams,
};
use super::signing::{encode_params, validate_response};

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
    product_table: Option<Arc<ProductTable>>,
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
            CONTRACT_BASE_URL.to_string(),
        )
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, timeout)
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

    pub(super) async fn spot_private(
        &self,
        method: HttpMethod,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(method, MexcApi::Spot, path, params, None, true)
            .await
    }

    pub(super) async fn contract_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, MexcApi::Contract, path, params, None, true)
            .await
    }

    pub(super) async fn contract_post_json(
        &self,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(
            HttpMethod::Post,
            MexcApi::Contract,
            path,
            Vec::new(),
            Some(body),
            true,
        )
        .await
    }

    #[allow(clippy::too_many_arguments)]
    pub(super) fn build_request(
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

    pub(super) fn credentials(&self) -> Result<(&str, &str)> {
        match (&self.api_key, &self.api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed MEXC requests require api_key and api_secret.".to_string(),
            )),
        }
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str, separator: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("mexc", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol, separator))
    }

    pub(super) fn take_symbol(
        &self,
        params: &mut Vec<(String, String)>,
        separator: &str,
    ) -> Result<String> {
        if let Some(symbol) = take_param(params, "symbol") {
            return self.exchange_symbol(&symbol, separator);
        }
        if let Some(product_symbol) = take_param(params, "product_symbol") {
            return self.exchange_symbol(&product_symbol, separator);
        }
        Err(DcexError::InvalidInput(
            "MEXC symbol is required.".to_string(),
        ))
    }

    pub(super) fn normalize_symbol_params(
        &self,
        params: &mut [(String, String)],
        separator: &str,
    ) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if key == "product_symbol" {
                *key = "symbol".to_string();
                *value = self.exchange_symbol(value, separator)?;
            } else if key == "symbol" {
                *value = self.exchange_symbol(value, separator)?;
            }
        }
        Ok(())
    }

    pub(super) fn push_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &MexcParams,
        separator: &str,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol(symbol, separator)?,
            ));
        } else if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, separator)?,
            ));
        }
        Ok(())
    }

    pub(super) fn push_required_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &MexcParams,
        separator: &str,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol(symbol, separator)?,
            ));
            return Ok(());
        }
        query.push((
            "symbol".to_string(),
            self.exchange_symbol(params.required("product_symbol")?, separator)?,
        ));
        Ok(())
    }

    pub(super) fn insert_product_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &MexcParams,
        separator: &str,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            let symbol = self.exchange_symbol(symbol, separator)?;
            insert_optional_string(body, "symbol", Some(&symbol));
        } else if let Some(product_symbol) = params.get("product_symbol") {
            let symbol = self.exchange_symbol(product_symbol, separator)?;
            insert_optional_string(body, "symbol", Some(&symbol));
        }
        Ok(())
    }

    pub(super) fn insert_required_product_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &MexcParams,
        separator: &str,
    ) -> Result<()> {
        let symbol = if let Some(symbol) = params.get("symbol") {
            self.exchange_symbol(symbol, separator)?
        } else {
            self.exchange_symbol(params.required("product_symbol")?, separator)?
        };
        body.insert("symbol".to_string(), Value::String(symbol));
        Ok(())
    }
}

pub(super) fn take_param(params: &mut Vec<(String, String)>, key: &str) -> Option<String> {
    params
        .iter()
        .position(|(param_key, _)| param_key == key)
        .map(|index| params.remove(index).1)
}
