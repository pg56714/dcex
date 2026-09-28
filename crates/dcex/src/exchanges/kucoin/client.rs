use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::{ValidatedResponse, unix_timestamp_ms};
use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody, block_on};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};
use super::params::{KucoinParams, exchange_symbol_fallback, is_canonical_product_symbol};
use super::signing::{
    encrypted_passphrase, http_method_name, request_signature, validate_response,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum KucoinMarket {
    Futures,
    Spot,
    Broker,
}

#[derive(Clone)]
struct BrokerAuth {
    partner: String,
    key: String,
    name: String,
}

#[derive(Clone)]
pub struct KucoinClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    broker_base_url: String,
    broker_auth: Option<BrokerAuth>,
    api_key: Option<String>,
    api_secret: Option<String>,
    encrypted_passphrase: Option<String>,
    product_table: Option<Arc<ProductTable>>,
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

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, timeout)
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        let encrypted_passphrase =
            encrypted_passphrase(api_secret.as_deref(), passphrase.as_deref())?;
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            broker_base_url: "https://api-broker.kucoin.com".into(),
            broker_auth: None,
            api_key,
            api_secret,
            encrypted_passphrase,
            product_table: None,
        })
    }

    /// Configure the broker host and optional partner attribution credentials.
    pub fn configure_broker(
        &mut self,
        base_url: String,
        partner: Option<String>,
        key: Option<String>,
        name: Option<String>,
    ) -> Result<()> {
        if base_url.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "broker base URL must not be empty".into(),
            ));
        }
        let auth = match (partner, key, name) {
            (None, None, None) => None,
            (Some(partner), Some(key), Some(name))
                if !partner.is_empty() && !key.is_empty() && !name.is_empty() =>
            {
                Some(BrokerAuth { partner, key, name })
            }
            _ => {
                return Err(DcexError::InvalidInput(
                    "broker partner, key and name must be provided together".into(),
                ));
            }
        };
        self.broker_base_url = base_url;
        self.broker_auth = auth;
        Ok(())
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

    pub(super) async fn private_get(
        &self,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, market, path, params, None, true)
            .await
    }

    pub(super) async fn private_post(
        &self,
        market: KucoinMarket,
        path: impl Into<String>,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body = serde_json::to_vec(&body).map_err(|error| {
            DcexError::InvalidInput(format!("invalid KuCoin JSON body: {error}"))
        })?;
        self.request(HttpMethod::Post, market, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) async fn private_delete(
        &self,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Delete, market, path, params, None, true)
            .await
    }

    #[allow(clippy::too_many_arguments)]
    pub(super) fn build_request(
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
                .extend_pairs(
                    params
                        .iter()
                        .map(|(key, value)| (key.as_str(), value.as_str())),
                )
                .finish()
        } else {
            String::new()
        };
        // KuCoin requires the transmitted URL to be percent-encoded, but the
        // signature prehash must contain the original, unencoded query values.
        let signing_query = if matches!(method, HttpMethod::Get | HttpMethod::Delete) {
            params
                .iter()
                .map(|(key, value)| format!("{key}={value}"))
                .collect::<Vec<_>>()
                .join("&")
        } else {
            String::new()
        };
        let request_path = if query.is_empty() {
            path.clone()
        } else {
            format!("{path}?{query}")
        };
        let signing_path = if signing_query.is_empty() {
            path
        } else {
            format!("{path}?{signing_query}")
        };
        let body = if matches!(
            method,
            HttpMethod::Post | HttpMethod::Put | HttpMethod::Delete
        ) {
            body.unwrap_or_default()
        } else {
            Vec::new()
        };
        let base_url = match market {
            KucoinMarket::Futures => &self.futures_base_url,
            KucoinMarket::Spot => &self.spot_base_url,
            KucoinMarket::Broker => &self.broker_base_url,
        };
        let mut request = HttpRequest::new(method, base_url, &request_path)
            .header("Content-Type", "application/json");
        if !body.is_empty() {
            request.body = RequestBody::Raw(body.clone());
        }

        if signed {
            let (api_key, api_secret, encrypted_passphrase) = self.credentials()?;
            let signature = request_signature(api_secret, timestamp, method, &signing_path, &body)?;
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
            if let Some(auth) = &self.broker_auth {
                let preimage = format!("{timestamp}{}{api_key}", auth.partner);
                let signature =
                    crate::crypto::hmac_sha256_base64(auth.key.as_bytes(), preimage.as_bytes())?;
                request
                    .headers
                    .insert("KC-API-PARTNER".into(), auth.partner.clone());
                request
                    .headers
                    .insert("KC-API-PARTNER-SIGN".into(), signature);
                request
                    .headers
                    .insert("KC-BROKER-NAME".into(), auth.name.clone());
                request
                    .headers
                    .insert("KC-API-PARTNER-VERIFY".into(), "true".into());
            }
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

    pub(super) fn exchange_symbol(&self, product_symbol: &str, futures: bool) -> Result<String> {
        if is_canonical_product_symbol(product_symbol)
            && let Some(table) = &self.product_table
        {
            return table.get_exchange_symbol("kucoin", product_symbol);
        }
        Ok(exchange_symbol_fallback(product_symbol, futures))
    }

    pub(super) fn push_required_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &KucoinParams,
        futures: bool,
    ) -> Result<()> {
        let product_symbol = params.required_any(&["product_symbol", "symbol"])?;
        query.push((
            "symbol".to_string(),
            self.exchange_symbol(product_symbol, futures)?,
        ));
        Ok(())
    }

    pub(super) fn push_optional_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &KucoinParams,
        futures: bool,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get_any(&["product_symbol", "symbol"]) {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, futures)?,
            ));
        }
        Ok(())
    }
}
