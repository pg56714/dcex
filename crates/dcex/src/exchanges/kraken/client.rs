use std::sync::Arc;
use std::time::Duration;

use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};
use super::params::{exchange_symbol_fallback, is_canonical_product_symbol, KrakenParams};
use super::signing::{
    encode_params, futures_signature, http_method_name, spot_signature, unix_timestamp_ns,
    validate_response,
};

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
    product_table: Option<Arc<ProductTable>>,
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

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, None, timeout)
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

    pub(super) async fn private_get(
        &self,
        auth: KrakenAuth,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, auth, path, params, None, true)
            .await
    }

    pub(super) async fn private_post(
        &self,
        auth: KrakenAuth,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Post, auth, path, params, None, true)
            .await
    }

    pub(super) fn build_request(
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

    pub(super) fn spot_credentials(&self) -> Result<(&str, &str)> {
        match (&self.spot_api_key, &self.spot_api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed Kraken spot requests require spot_api_key and spot_api_secret.".to_string(),
            )),
        }
    }

    pub(super) fn futures_credentials(&self) -> Result<(&str, &str)> {
        match (&self.futures_api_key, &self.futures_api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed Kraken futures requests require futures_api_key and futures_api_secret."
                    .to_string(),
            )),
        }
    }

    pub(super) fn exchange_symbol(
        &self,
        product_symbol: &str,
        futures_prefix: &str,
    ) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("kraken", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol, futures_prefix))
    }

    pub(super) fn push_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &KrakenParams,
        key: &str,
        futures_prefix: &str,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                key.to_string(),
                self.exchange_symbol(product_symbol, futures_prefix)?,
            ));
        }
        Ok(())
    }

    pub(super) fn push_required_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &KrakenParams,
        key: &str,
        futures_prefix: &str,
    ) -> Result<()> {
        query.push((
            key.to_string(),
            self.exchange_symbol(params.required("product_symbol")?, futures_prefix)?,
        ));
        Ok(())
    }
}
