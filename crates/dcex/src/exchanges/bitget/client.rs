use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};

use crate::exchange::{ValidatedResponse, unix_timestamp_ms};
use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody, block_on};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::BASE_URL;
use super::params::{BitgetParams, exchange_symbol_fallback};
use super::signing::{encode_params, sign, validate_response};

#[derive(Clone)]
pub struct BitgetClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    passphrase: Option<String>,
    product_table: Option<Arc<ProductTable>>,
}

impl BitgetClient {
    pub(crate) const INPUT_EXCHANGE: &'static str = "bitget";

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

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, timeout)
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

    pub(super) async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }

    pub(super) async fn get_private(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true)
            .await
    }

    pub(super) async fn post_private(&self, path: &str, body: Value) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(HttpMethod::Post, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) fn build_request(
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
            let body = body.as_deref().unwrap_or_default();
            let signature = sign(timestamp, method, &path, &query_string, body, api_secret)?;
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

    pub(super) fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.passphrase) {
            (Some(api_key), Some(api_secret), Some(passphrase)) => {
                Ok((api_key, api_secret, passphrase))
            }
            _ => Err(DcexError::InvalidInput(
                "Signed Bitget requests require api_key, api_secret, and passphrase.".to_string(),
            )),
        }
    }

    pub(super) fn exchange_symbol_category(
        &self,
        product_symbol: &str,
        category: Option<&str>,
    ) -> Result<String> {
        if let Some(table) = &self.product_table {
            return Ok(table
                .resolve_symbol_in("bitget", product_symbol, |row| {
                    category.is_none_or(|category| row.exchange_type.eq_ignore_ascii_case(category))
                })?
                .exchange_symbol
                .clone());
        }
        exchange_symbol_fallback(product_symbol)
    }

    pub(super) fn normalize_batch_symbols(&self, mut body: Value) -> Result<Value> {
        if self.product_table.is_none() {
            return Ok(body);
        }
        fn visit(client: &BitgetClient, value: &mut Value, inherited: Option<&str>) -> Result<()> {
            if let Some(items) = value.as_array_mut() {
                for item in items {
                    visit(client, item, inherited)?;
                }
            } else if let Some(object) = value.as_object_mut() {
                let category = object
                    .get("category")
                    .and_then(Value::as_str)
                    .or(inherited)
                    .map(str::to_string);
                if let Some(symbol) = object.get("symbol").and_then(Value::as_str) {
                    let native = client.exchange_symbol_category(symbol, category.as_deref())?;
                    object.insert("symbol".into(), Value::String(native));
                }
                if let Some(items) = object.get_mut("orderList") {
                    visit(client, items, category.as_deref())?;
                }
            }
            Ok(())
        }
        visit(self, &mut body, None)?;
        Ok(body)
    }

    pub(super) fn normalize_symbol_params(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<Vec<(String, String)>> {
        let category = params
            .iter()
            .find(|(key, _)| key == "category" || key == "productType")
            .map(|(_, value)| value.clone());
        params
            .into_iter()
            .map(|(key, value)| {
                if key == "product_symbol" {
                    Ok((
                        "symbol".to_string(),
                        self.exchange_symbol_category(&value, category.as_deref())?,
                    ))
                } else if key == "symbol" {
                    Ok((
                        key,
                        self.exchange_symbol_category(&value, category.as_deref())?,
                    ))
                } else {
                    Ok((key, value))
                }
            })
            .collect()
    }

    pub(super) fn push_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BitgetParams,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol_category(
                    product_symbol,
                    params.get("category").or(params.get("productType")),
                )?,
            ));
        }
        Ok(())
    }

    pub(super) fn push_required_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BitgetParams,
    ) -> Result<()> {
        query.push((
            "symbol".to_string(),
            self.exchange_symbol_category(
                params.required("product_symbol")?,
                params.get("category").or(params.get("productType")),
            )?,
        ));
        Ok(())
    }

    pub(super) fn push_uta_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BitgetParams,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol_category(
                    symbol,
                    params.get("category").or(params.get("productType")),
                )?,
            ));
        } else {
            self.push_product_symbol(query, params)?;
        }
        Ok(())
    }

    pub(super) fn insert_product_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitgetParams,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get("product_symbol") {
            body.insert(
                "symbol".to_string(),
                Value::String(self.exchange_symbol_category(
                    product_symbol,
                    params.get("category").or(params.get("productType")),
                )?),
            );
        }
        Ok(())
    }

    pub(super) fn insert_required_product_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitgetParams,
    ) -> Result<()> {
        body.insert(
            "symbol".to_string(),
            Value::String(self.exchange_symbol_category(
                params.required("product_symbol")?,
                params.get("category").or(params.get("productType")),
            )?),
        );
        Ok(())
    }

    pub(super) fn insert_uta_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitgetParams,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            body.insert(
                "symbol".into(),
                Value::String(self.exchange_symbol_category(
                    symbol,
                    params.get("category").or(params.get("productType")),
                )?),
            );
        } else {
            self.insert_product_symbol(body, params)?;
        }
        Ok(())
    }
}
