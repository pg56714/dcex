use std::collections::BTreeMap;
use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{API_KEYS, BASE_URL};
use super::params::insert_optional_pair;
use super::signing::{
    chain_id, create_auth_token, encode_params, http_method_name, json_value_string,
    normalize_private_key, private_key_for, public_key_hex,
};
use super::trade::LighterSignedTransaction;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LighterContentType {
    Form,
    Json,
}

#[derive(Clone)]
pub struct LighterClient {
    pub(super) transport: AsyncHttpClient,
    pub(super) base_url: String,
    pub(super) chain_id: u64,
    pub(super) account_index: Option<u64>,
    pub(super) api_key_index: Option<u64>,
    pub(super) api_private_keys: BTreeMap<u64, [u8; 40]>,
    pub(super) product_table: Option<Arc<ProductTable>>,
}

impl LighterClient {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_base_url(timeout, BASE_URL.to_string())
    }

    pub fn with_base_url(timeout: Duration, base_url: String) -> Result<Self> {
        Self::with_base_url_and_credentials(timeout, base_url, None, None, None)
    }

    pub fn with_base_url_and_credentials(
        timeout: Duration,
        base_url: String,
        account_index: Option<u64>,
        api_key_index: Option<u64>,
        api_private_key: Option<String>,
    ) -> Result<Self> {
        let mut api_private_keys = BTreeMap::new();
        if let Some(private_key) = api_private_key {
            let index = api_key_index.unwrap_or(255);
            api_private_keys.insert(index, normalize_private_key(&private_key)?);
        }
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            chain_id: chain_id(&base_url),
            base_url,
            account_index,
            api_key_index,
            api_private_keys,
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

    #[allow(clippy::too_many_arguments)]
    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, path, params, body, signed, headers, content_type)
            .await?;
        let data = validate_response(&response)?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    #[allow(clippy::too_many_arguments)]
    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<HttpResponse> {
        let request =
            self.build_request(method, path, params, body, signed, headers, content_type)?;
        self.transport.execute(request).await
    }

    #[allow(clippy::too_many_arguments)]
    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, params, body, signed, headers, content_type)
                .await
        })
    }

    pub(super) async fn path_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        query: Vec<(String, String)>,
        body: Vec<(String, String)>,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<ValidatedResponse> {
        self.request(method, path, query, body, false, headers, content_type)
            .await
    }

    pub(super) async fn get_path(
        &self,
        path: impl Into<String>,
        query: Vec<(String, String)>,
        headers: BTreeMap<String, String>,
    ) -> Result<ValidatedResponse> {
        self.path_request(
            HttpMethod::Get,
            path,
            query,
            Vec::new(),
            headers,
            LighterContentType::Json,
        )
        .await
    }

    pub(super) async fn post_form(
        &self,
        path: impl Into<String>,
        body: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.path_request(
            HttpMethod::Post,
            path,
            Vec::new(),
            body,
            BTreeMap::new(),
            LighterContentType::Form,
        )
        .await
    }

    pub(super) fn private_account_index(&self, account_index: Option<u64>) -> Result<u64> {
        account_index.or(self.account_index).ok_or_else(|| {
            DcexError::InvalidInput("Lighter private requests require account_index.".to_string())
        })
    }

    pub(super) fn private_api_key_index(&self, api_key_index: Option<u64>) -> Result<u64> {
        api_key_index.or(self.api_key_index).ok_or_else(|| {
            DcexError::InvalidInput("Lighter private requests require api_key_index.".to_string())
        })
    }

    pub(super) fn private_key(&self, api_key_index: u64) -> Result<&[u8; 40]> {
        if self.api_private_keys.is_empty() {
            return Err(DcexError::InvalidInput(
                "Lighter private requests require api_private_key.".to_string(),
            ));
        }
        private_key_for(&self.api_private_keys, api_key_index)
    }

    pub fn create_auth_token(
        &self,
        deadline: Option<u64>,
        api_key_index: Option<u64>,
    ) -> Result<String> {
        let account_index = self.private_account_index(None)?;
        let api_key_index = self.private_api_key_index(api_key_index)?;
        let private_key = self.private_key(api_key_index)?;
        create_auth_token(account_index, api_key_index, private_key, deadline)
    }

    pub async fn check_client(&self) -> Result<Option<String>> {
        let account_index = self.private_account_index(None)?;
        let response = self
            .get_path(
                API_KEYS,
                vec![("account_index".to_string(), account_index.to_string())],
                BTreeMap::new(),
            )
            .await?;
        self.check_client_data(&response.data)
    }

    pub fn check_client_blocking(&self) -> Result<Option<String>> {
        let client = self.clone();
        block_on(async move { client.check_client().await })
    }

    pub(super) fn check_client_data(&self, data: &Value) -> Result<Option<String>> {
        let Some(api_keys) = data.get("api_keys").and_then(Value::as_array) else {
            return Ok(Some(format!("failed to get API keys: {data:?}")));
        };
        let mut remote_keys = BTreeMap::new();
        for item in api_keys {
            let Some(index) = item.get("api_key_index").and_then(Value::as_u64) else {
                continue;
            };
            let Some(public_key) = item.get("public_key").and_then(Value::as_str) else {
                continue;
            };
            remote_keys.insert(
                index,
                public_key.trim_start_matches("0x").to_ascii_lowercase(),
            );
        }
        for (api_key_index, private_key) in &self.api_private_keys {
            let own_key = public_key_hex(private_key)?;
            if remote_keys.get(api_key_index) != Some(&own_key) {
                return Ok(Some(format!(
                    "private key does not match the one on Lighter on api key {api_key_index}"
                )));
            }
        }
        Ok(None)
    }

    pub(super) async fn submit_signed_tx(
        &self,
        tx: LighterSignedTransaction,
        price_protection: Option<bool>,
    ) -> Result<ValidatedResponse> {
        let mut body = vec![
            ("tx_type".to_string(), tx.tx_type.to_string()),
            ("tx_info".to_string(), tx.tx_info),
        ];
        insert_optional_pair(&mut body, "price_protection", price_protection);
        self.post_form(super::endpoints::SEND_TX, body).await
    }

    pub(super) fn market_id(&self, product_symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            return table.get_exchange_symbol("lighter", product_symbol);
        }
        if product_symbol.contains('-') {
            return Err(DcexError::InvalidInput(
                "Lighter product_symbol requires a product table.".to_string(),
            ));
        }
        Ok(product_symbol.to_string())
    }

    #[allow(clippy::too_many_arguments)]
    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<HttpRequest> {
        if signed {
            return Err(DcexError::InvalidInput(
                "Signed raw Lighter requests are not implemented; use private_request methods."
                    .to_string(),
            ));
        }
        if !matches!(method, HttpMethod::Get | HttpMethod::Post) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Lighter HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = encode_params(&params);
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let content_type = match content_type {
            LighterContentType::Form => "application/x-www-form-urlencoded",
            LighterContentType::Json => "application/json",
        };
        let mut request = HttpRequest::new(method, &self.base_url, request_path)
            .header("Content-Type", content_type);
        request.headers.extend(headers);
        if method == HttpMethod::Post && !body.is_empty() {
            request.body = RequestBody::Raw(encode_params(&body).into_bytes());
        }
        Ok(request)
    }
}

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    response.ensure_success()?;
    let data = response.json()?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        if code.is_some_and(|code| !matches!(json_value_string(code).as_str(), "0" | "200")) {
            let message = object
                .get("message")
                .or_else(|| object.get("msg"))
                .map(json_value_string)
                .unwrap_or_else(|| "Unknown error".to_string());
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!(
                    "Lighter API Error: [{}] {message}",
                    code.map(json_value_string)
                        .unwrap_or_else(|| "Unknown".to_string())
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
