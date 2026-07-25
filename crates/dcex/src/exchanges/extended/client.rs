use std::collections::BTreeMap;
use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{BASE_URL, USER_AGENT};
use super::signing::{parse_felt_hex, ExtendedSigningCredentials, StarknetDomain};

#[derive(Clone)]
pub struct ExtendedClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    signing: Option<ExtendedSigningCredentials>,
    signing_domain: StarknetDomain,
    user_agent: String,
    product_table: Option<Arc<ProductTable>>,
}

impl ExtendedClient {
    pub fn new(api_key: Option<String>, timeout: Duration) -> Result<Self> {
        Self::with_base_url(
            api_key,
            timeout,
            BASE_URL.to_string(),
            USER_AGENT.to_string(),
        )
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, timeout)
    }

    pub fn with_base_url(
        api_key: Option<String>,
        timeout: Duration,
        base_url: String,
        user_agent: String,
    ) -> Result<Self> {
        let (api_key, base_url, user_agent) =
            validate_client_config(api_key, base_url, user_agent)?;
        let signing_domain = signing_domain_for_base_url(&base_url);
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            signing: None,
            signing_domain,
            user_agent,
            product_table: None,
        })
    }

    pub fn with_base_url_and_stark(
        api_key: Option<String>,
        stark_private_key: Option<String>,
        stark_public_key: Option<String>,
        vault_number: Option<u64>,
        client_id: Option<String>,
        timeout: Duration,
        base_url: String,
        user_agent: String,
    ) -> Result<Self> {
        let (api_key, base_url, user_agent) =
            validate_client_config(api_key, base_url, user_agent)?;
        let signing_domain = signing_domain_for_base_url(&base_url);
        let signing = match (stark_private_key, stark_public_key, vault_number) {
            (Some(stark_private_key), Some(stark_public_key), Some(vault_number)) => {
                let private_key = parse_felt_hex(&stark_private_key, "stark_private_key")?;
                let public_key = parse_felt_hex(&stark_public_key, "stark_public_key")?;
                if private_key == starknet_crypto::Felt::ZERO
                    || public_key == starknet_crypto::Felt::ZERO
                    || vault_number == 0
                {
                    return Err(DcexError::InvalidInput(
                        "Extended Stark keys and vault_number must be non-zero".to_string(),
                    ));
                }
                Some(ExtendedSigningCredentials::new(
                    stark_private_key,
                    stark_public_key,
                    vault_number,
                    client_id,
                ))
            }
            (None, None, None) => None,
            _ => {
                return Err(DcexError::InvalidInput(
                    "Extended order signing requires stark_private_key, stark_public_key, and vault_number together.".to_string(),
                ))
            }
        };
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            signing,
            signing_domain,
            user_agent,
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
        extra_headers: BTreeMap<String, String>,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, path, params, body, signed, extra_headers)
            .await?;
        response.ensure_success()?;
        let data = match response.json() {
            Ok(data) => data,
            Err(DcexError::Decode(_)) => Value::String(response.text()?),
            Err(error) => return Err(error),
        };
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
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpResponse> {
        let request = self.build_request(method, path, params, body, signed, extra_headers)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, params, body, signed, extra_headers)
                .await
        })
    }

    pub(super) async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, false, BTreeMap::new())
            .await
    }

    pub(super) async fn private_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true, BTreeMap::new())
            .await
    }

    pub(super) async fn private_post_value(
        &self,
        path: &str,
        body: Value,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.private_body_request(HttpMethod::Post, path, body, params)
            .await
    }

    pub(super) async fn private_delete(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Delete,
            path,
            params,
            None,
            true,
            BTreeMap::new(),
        )
        .await
    }

    async fn private_body_request(
        &self,
        method: HttpMethod,
        path: &str,
        body: Value,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let body = serde_json::to_vec(&body)
            .map_err(|error| DcexError::InvalidInput(format!("invalid JSON body: {error}")))?;
        self.request(method, path, params, Some(body), true, BTreeMap::new())
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpRequest> {
        if signed && self.api_key.is_none() {
            return Err(DcexError::InvalidInput(
                "Signed Extended requests require api_key; order bodies must already include the exchange-required settlement signature.".to_string(),
            ));
        }
        let mut request = HttpRequest::new(method, &self.base_url, path.into())
            .header("Accept", "application/json")
            .header("Content-Type", "application/json")
            .header("User-Agent", &self.user_agent);
        request.query = params;
        if let Some(api_key) = self.api_key.as_deref() {
            request
                .headers
                .insert("X-Api-Key".to_string(), api_key.to_string());
        }
        request.headers.extend(extra_headers);
        if let Some(body) = body {
            request.body = RequestBody::Raw(body);
        }
        Ok(request)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if !product_symbol.contains('-') || product_symbol.ends_with("-USD") {
            return Ok(product_symbol.to_string());
        }
        if let Some(table) = &self.product_table {
            return table.get_exchange_symbol("extended", product_symbol);
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn signing_credentials(&self) -> Result<&ExtendedSigningCredentials> {
        self.signing.as_ref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Extended automatic order signing requires stark_private_key, stark_public_key, and vault_number.".to_string(),
            )
        })
    }

    pub(super) const fn signing_domain(&self) -> StarknetDomain {
        self.signing_domain
    }
}

pub(super) fn signing_domain_for_base_url(base_url: &str) -> StarknetDomain {
    if base_url.contains("starknet.sepolia.extended.exchange") {
        StarknetDomain::sepolia()
    } else {
        StarknetDomain::mainnet()
    }
}

fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    match parts.as_slice() {
        [base, _, "SPOT"] => format!("{base}SPOT"),
        [base, quote, ..] => format!("{base}-{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn validate_client_config(
    api_key: Option<String>,
    base_url: String,
    user_agent: String,
) -> Result<(Option<String>, String, String)> {
    let api_key = api_key
        .map(|value| {
            let value = value.trim().to_string();
            if value.is_empty() {
                return Err(DcexError::InvalidInput(
                    "Extended API key must not be empty".to_string(),
                ));
            }
            Ok(value)
        })
        .transpose()?;
    let base_url = base_url.trim().trim_end_matches('/').to_string();
    if base_url.is_empty() || !(base_url.starts_with("https://") || base_url.starts_with("http://"))
    {
        return Err(DcexError::InvalidInput(
            "Extended REST base URL must use http:// or https://".to_string(),
        ));
    }
    let user_agent = user_agent.trim().to_string();
    if user_agent.is_empty() {
        return Err(DcexError::InvalidInput(
            "Extended User-Agent must not be empty".to_string(),
        ));
    }
    Ok((api_key, base_url, user_agent))
}
