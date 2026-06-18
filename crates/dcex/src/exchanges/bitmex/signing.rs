use serde_json::Value;
use url::form_urlencoded;

use crate::http::{HttpMethod, HttpResponse};
use crate::Result;

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
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

pub(super) fn encode_params(params: &[(String, String)]) -> String {
    let mut serializer = form_urlencoded::Serializer::new(String::new());
    serializer.extend_pairs(
        params
            .iter()
            .map(|(key, value)| (key.as_str(), value.as_str())),
    );
    serializer.finish()
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
