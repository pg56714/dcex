use crate::ethereum::{keccak256, recoverable_sign};
use crate::http::HttpMethod;
use crate::{DcexError, Result};

const DOMAIN_TYPE: &str =
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";
const AGENT_TYPE: &str = "Agent(string source,bytes32 connectionId)";

#[derive(Debug, PartialEq, Eq)]
pub struct HyperliquidSignature {
    pub r: String,
    pub s: String,
    pub v: u8,
}

pub fn hyperliquid_signature(
    action_msgpack: &[u8],
    timestamp: u64,
    vault_address: Option<&str>,
    expire_after: Option<u64>,
    testnet: bool,
    private_key: &[u8; 32],
) -> Result<HyperliquidSignature> {
    let mut connection = Vec::with_capacity(action_msgpack.len() + 38);
    connection.extend_from_slice(action_msgpack);
    connection.extend_from_slice(&timestamp.to_be_bytes());
    if let Some(vault_address) = vault_address {
        connection.push(1);
        connection.extend_from_slice(&parse_address(vault_address)?);
    } else {
        connection.push(0);
    }
    if let Some(expire_after) = expire_after {
        connection.push(0);
        connection.extend_from_slice(&expire_after.to_be_bytes());
    }
    let connection_id = keccak256(&connection);
    let digest = agent_eip712_digest(if testnet { "b" } else { "a" }, &connection_id);
    let signature = recoverable_sign(&digest, private_key)?;
    Ok(HyperliquidSignature {
        r: format!("0x{}", hex::encode(&signature[..32])),
        s: format!("0x{}", hex::encode(&signature[32..64])),
        v: signature[64] + 27,
    })
}

fn agent_eip712_digest(source: &str, connection_id: &[u8; 32]) -> [u8; 32] {
    let mut domain = Vec::with_capacity(160);
    domain.extend_from_slice(&keccak256(DOMAIN_TYPE.as_bytes()));
    domain.extend_from_slice(&keccak256(b"Exchange"));
    domain.extend_from_slice(&keccak256(b"1"));
    let mut chain_id = [0u8; 32];
    chain_id[24..].copy_from_slice(&1337u64.to_be_bytes());
    domain.extend_from_slice(&chain_id);
    domain.extend_from_slice(&[0u8; 32]);
    let domain_separator = keccak256(&domain);

    let mut agent = Vec::with_capacity(96);
    agent.extend_from_slice(&keccak256(AGENT_TYPE.as_bytes()));
    agent.extend_from_slice(&keccak256(source.as_bytes()));
    agent.extend_from_slice(connection_id);
    let agent_hash = keccak256(&agent);

    let mut digest = Vec::with_capacity(66);
    digest.extend_from_slice(b"\x19\x01");
    digest.extend_from_slice(&domain_separator);
    digest.extend_from_slice(&agent_hash);
    keccak256(&digest)
}

pub(super) fn parse_private_key(private_key: &str) -> Result<[u8; 32]> {
    let normalized = private_key.strip_prefix("0x").unwrap_or(private_key);
    let bytes = hex::decode(normalized).map_err(|error| {
        DcexError::InvalidInput(format!("invalid Hyperliquid private key: {error}"))
    })?;
    bytes.try_into().map_err(|bytes: Vec<u8>| {
        DcexError::InvalidInput(format!(
            "Hyperliquid private key must contain 32 bytes, got {}",
            bytes.len()
        ))
    })
}

fn parse_address(address: &str) -> Result<[u8; 20]> {
    let normalized = address.strip_prefix("0x").unwrap_or(address);
    let bytes = hex::decode(normalized).map_err(|error| {
        DcexError::InvalidInput(format!("invalid Hyperliquid vault address: {error}"))
    })?;
    bytes.try_into().map_err(|bytes: Vec<u8>| {
        DcexError::InvalidInput(format!(
            "Hyperliquid vault address must contain 20 bytes, got {}",
            bytes.len()
        ))
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
