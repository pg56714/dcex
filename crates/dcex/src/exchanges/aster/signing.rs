use crate::ethereum::{keccak256, recoverable_sign};
use crate::http::HttpMethod;
use crate::{DcexError, Result};

const DOMAIN_NAME: &str = "AsterSignTransaction";
const DOMAIN_VERSION: &str = "1";
const DOMAIN_CHAIN_ID: u64 = 1666;
const DOMAIN_TYPE: &str =
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";
const MESSAGE_TYPE: &str = "Message(string msg)";

pub fn sign_message(message: &str, private_key: &[u8; 32]) -> Result<String> {
    let digest = eip712_digest(message);
    let mut signature = recoverable_sign(&digest, private_key)?;
    signature[64] += 27;
    Ok(format!("0x{}", hex::encode(signature)))
}

fn eip712_digest(message: &str) -> [u8; 32] {
    let mut domain = Vec::with_capacity(160);
    domain.extend_from_slice(&keccak256(DOMAIN_TYPE.as_bytes()));
    domain.extend_from_slice(&keccak256(DOMAIN_NAME.as_bytes()));
    domain.extend_from_slice(&keccak256(DOMAIN_VERSION.as_bytes()));
    let mut chain_id = [0u8; 32];
    chain_id[24..].copy_from_slice(&DOMAIN_CHAIN_ID.to_be_bytes());
    domain.extend_from_slice(&chain_id);
    domain.extend_from_slice(&[0u8; 32]);
    let domain_separator = keccak256(&domain);

    let mut message_struct = Vec::with_capacity(64);
    message_struct.extend_from_slice(&keccak256(MESSAGE_TYPE.as_bytes()));
    message_struct.extend_from_slice(&keccak256(message.as_bytes()));
    let message_hash = keccak256(&message_struct);

    let mut digest = Vec::with_capacity(66);
    digest.extend_from_slice(b"\x19\x01");
    digest.extend_from_slice(&domain_separator);
    digest.extend_from_slice(&message_hash);
    keccak256(&digest)
}

pub(super) fn parse_private_key(private_key: &str) -> Result<[u8; 32]> {
    let normalized = private_key.strip_prefix("0x").unwrap_or(private_key);
    let bytes = hex::decode(normalized)
        .map_err(|error| DcexError::InvalidInput(format!("invalid Aster private key: {error}")))?;
    bytes.try_into().map_err(|bytes: Vec<u8>| {
        DcexError::InvalidInput(format!(
            "Aster private key must contain 32 bytes, got {}",
            bytes.len()
        ))
    })
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

pub(super) const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}
