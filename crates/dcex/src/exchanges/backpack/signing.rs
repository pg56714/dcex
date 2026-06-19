use base64::Engine;
use ed25519_dalek::{Signer, SigningKey};

use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::SignaturePayload;

pub(super) fn decode_signing_key(api_secret: &str) -> Result<SigningKey> {
    let seed = base64::engine::general_purpose::STANDARD
        .decode(api_secret)
        .map_err(|error| {
            DcexError::InvalidInput(format!("invalid Backpack API secret: {error}"))
        })?;
    let seed: [u8; 32] = seed.try_into().map_err(|seed: Vec<u8>| {
        DcexError::InvalidInput(format!(
            "Backpack API secret must decode to 32 bytes, got {}",
            seed.len()
        ))
    })?;
    Ok(SigningKey::from_bytes(&seed))
}

pub(super) fn encode_params(params: &[(String, String)]) -> String {
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(
            params
                .iter()
                .map(|(key, value)| (key.as_str(), value.as_str())),
        )
        .finish()
}

pub(super) fn signature_message(
    instruction: &str,
    payload: &[Vec<(String, String)>],
    timestamp: &str,
    window: u64,
) -> String {
    let chunks = if payload.is_empty() {
        vec![format!("instruction={instruction}")]
    } else {
        payload
            .iter()
            .map(|item| {
                let mut sorted = item.clone();
                sorted.sort_by(|left, right| left.0.cmp(&right.0));
                let query = encode_params(&sorted);
                if query.is_empty() {
                    format!("instruction={instruction}")
                } else {
                    format!("instruction={instruction}&{query}")
                }
            })
            .collect()
    };
    format!("{}&timestamp={timestamp}&window={window}", chunks.join("&"))
}

pub(super) fn signature_header(
    signing_key: &SigningKey,
    instruction: &str,
    payload: &SignaturePayload,
    timestamp: &str,
    window: u64,
) -> String {
    let message = signature_message(instruction, payload, timestamp, window);
    let signature = signing_key.sign(message.as_bytes());
    base64::engine::general_purpose::STANDARD.encode(signature.to_bytes())
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
