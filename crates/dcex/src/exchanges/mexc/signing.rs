use serde_json::Value;
use url::form_urlencoded;

use crate::Result;
use crate::http::HttpResponse;

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    response.ensure_success("MEXC")?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        let success = object.get("success").and_then(Value::as_bool);
        let code_is_error =
            code.is_some_and(|code| !matches!(json_value_string(code).as_str(), "0" | "200"));
        if success == Some(false) || code_is_error {
            let message = object
                .get("msg")
                .or_else(|| object.get("message"))
                .and_then(Value::as_str)
                .unwrap_or("");
            return Err(response.api_error(
                "MEXC",
                code.map(json_value_string).as_deref(),
                message,
            ));
        }
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

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}
