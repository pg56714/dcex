use hmac::{Hmac, Mac};
use sha2::Sha256;

use crate::http::HttpMethod;
use crate::{DcexError, Result};

type HmacSha256 = Hmac<Sha256>;

pub(super) fn adjusted_timestamp_ms(offset_ms: i64) -> Result<String> {
    let local_ms = i64::try_from(crate::exchange::unix_timestamp_ms()?)
        .map_err(|error| DcexError::Runtime(format!("invalid Ondo local timestamp: {error}")))?;
    let adjusted = local_ms
        .checked_add(offset_ms)
        .and_then(|value| u64::try_from(value).ok())
        .ok_or_else(|| DcexError::Runtime("invalid adjusted Ondo timestamp".to_string()))?;
    Ok(adjusted.to_string())
}

pub(super) fn server_clock_offset_ms(message: &str, local_ms: u64) -> Option<i64> {
    if !message.contains("timestamp too far") {
        return None;
    }
    let server_time = message.split_once("current time unixMilli ")?.1;
    let digits = server_time
        .chars()
        .take_while(|character| character.is_ascii_digit())
        .collect::<String>();
    let server_ms = digits.parse::<i64>().ok()?;
    let local_ms = i64::try_from(local_ms).ok()?;
    server_ms.checked_sub(local_ms)?.checked_sub(1_000)
}

pub(super) fn method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}

pub(super) fn rest_signature(
    api_secret: &str,
    timestamp: &str,
    method: HttpMethod,
    request_path: &str,
    body: &[u8],
) -> Result<String> {
    let body = std::str::from_utf8(body)
        .map_err(|error| DcexError::InvalidInput(format!("Ondo body must be UTF-8: {error}")))?;
    let message = format!("{timestamp}{}{request_path}{body}", method_name(method));
    hmac_hex(api_secret, message.as_bytes())
}

pub(super) fn websocket_signature(api_secret: &str, timestamp: &str) -> Result<String> {
    hmac_hex(
        api_secret,
        format!("{timestamp}ondo_perps_ws_login").as_bytes(),
    )
}

fn hmac_hex(api_secret: &str, message: &[u8]) -> Result<String> {
    let mut mac = HmacSha256::new_from_slice(api_secret.as_bytes())
        .map_err(|error| DcexError::InvalidInput(format!("invalid Ondo API secret: {error}")))?;
    mac.update(message);
    Ok(hex::encode(mac.finalize().into_bytes()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rest_signature_matches_hmac_sha256_vector() {
        assert_eq!(
            rest_signature(
                "ondoApiSecret_SECRET",
                "1741170600000",
                HttpMethod::Get,
                "/v1/perps/orders?market=AAPL-USD.P&limit=1000",
                b"",
            )
            .expect("signature"),
            "8a4117a0af84fd0340763cda02debb7c72bf8f8fc9a7fb6cc3750cf572728c3a"
        );
    }

    #[test]
    fn websocket_signature_uses_documented_suffix() {
        assert_eq!(
            websocket_signature("secret", "1700000000000").expect("signature"),
            "6986f27f7d9c2558026ad52bf49e21fc9820a0e7aba43786fe0c8958871212fc"
        );
    }

    #[test]
    fn server_clock_offset_uses_reported_milliseconds_with_past_margin() {
        assert_eq!(
            server_clock_offset_ms(
                "timestamp too far in the future. current time unixMilli 1789810892725, timestamp 1789810894652",
                1789810894652,
            ),
            Some(-2927),
        );
        assert_eq!(server_clock_offset_ms("timestamp too far", 1000), None);
        assert_eq!(
            server_clock_offset_ms("unrelated error current time unixMilli 2000", 3000),
            None,
        );
    }
}
