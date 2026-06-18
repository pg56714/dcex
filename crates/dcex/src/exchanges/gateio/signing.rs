use serde_json::Value;

use crate::crypto::{hmac_sha512_hex, sha512_hex};
use crate::exchange::ValidatedResponse;
use crate::http::{HttpMethod, HttpResponse};
use crate::Result;

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    response.ensure_success()?;
    response.json()
}

pub(super) fn gateio_signature(
    method: HttpMethod,
    path: &str,
    query: &str,
    body: &[u8],
    timestamp: u64,
    api_secret: &str,
) -> Result<String> {
    let canonical = format!(
        "{}\n{path}\n{query}\n{}\n{timestamp}",
        http_method_name(method),
        sha512_hex(body)
    );
    hmac_sha512_hex(api_secret.as_bytes(), canonical.as_bytes())
}

pub(super) fn validated(response: HttpResponse) -> Result<ValidatedResponse> {
    let data = validate_response(&response)?;
    Ok(ValidatedResponse {
        status: response.status,
        headers: response.headers,
        data,
    })
}

pub(super) const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}
