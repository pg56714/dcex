use serde_json::Value;

use crate::http::{HttpMethod, HttpResponse};
use crate::{DcexError, Result};

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    if !data.is_object() {
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Unexpected response type: {}", data_type_name(&data)),
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    if data
        .as_object()
        .and_then(|object| object.get("code"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string())
        != "0"
    {
        let (code, message) = okx_error_details(&data);
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("OKX API Error: [{code}] {message}"),
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    response.ensure_success()?;
    Ok(data)
}

fn okx_error_details(data: &Value) -> (String, String) {
    let Some(object) = data.as_object() else {
        return ("Unknown".to_string(), "Unknown error".to_string());
    };
    let mut api_code = object
        .get("code")
        .map(json_value_string)
        .unwrap_or_else(|| "Unknown".to_string());
    let mut error_message = object
        .get("msg")
        .map(json_value_string)
        .unwrap_or_else(|| "Unknown error".to_string());
    if let Some(row) = object
        .get("data")
        .and_then(Value::as_array)
        .and_then(|rows| rows.first())
        .and_then(Value::as_object)
    {
        if let Some(code) = row
            .get("sCode")
            .map(json_value_string)
            .filter(|value| !value.is_empty())
        {
            api_code = code;
        }
        if let Some(message) = row
            .get("sMsg")
            .map(json_value_string)
            .filter(|value| !value.is_empty())
        {
            error_message = message;
        }
    }
    (api_code, error_message)
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

fn data_type_name(value: &Value) -> &'static str {
    match value {
        Value::Null => "null",
        Value::Bool(_) => "bool",
        Value::Number(_) => "number",
        Value::String(_) => "string",
        Value::Array(_) => "array",
        Value::Object(_) => "object",
    }
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

pub(super) fn iso_timestamp(timestamp_ms: u64) -> String {
    let seconds = timestamp_ms / 1_000;
    let milliseconds = timestamp_ms % 1_000;
    let days = (seconds / 86_400) as i64;
    let seconds_of_day = seconds % 86_400;
    let hour = seconds_of_day / 3_600;
    let minute = seconds_of_day % 3_600 / 60;
    let second = seconds_of_day % 60;

    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let day_of_era = z - era * 146_097;
    let year_of_era =
        (day_of_era - day_of_era / 1_460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let mut year = year_of_era + era * 400;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let month_prime = (5 * day_of_year + 2) / 153;
    let day = day_of_year - (153 * month_prime + 2) / 5 + 1;
    let month = month_prime + if month_prime < 10 { 3 } else { -9 };
    year += i64::from(month <= 2);

    format!("{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{milliseconds:03}Z")
}
