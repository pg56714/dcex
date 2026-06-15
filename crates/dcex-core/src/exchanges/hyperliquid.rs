use std::time::Duration;

use serde_json::{Map, Number, Value};

use crate::ethereum::{keccak256, recoverable_sign};
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const MAINNET_URL: &str = "https://api.hyperliquid.xyz";
const TESTNET_URL: &str = "https://api.hyperliquid-testnet.xyz";
const DOMAIN_TYPE: &str =
    "EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)";
const AGENT_TYPE: &str = "Agent(string source,bytes32 connectionId)";

#[derive(Clone)]
pub struct HyperliquidClient {
    transport: AsyncHttpClient,
    endpoint: String,
    testnet: bool,
    wallet_address: Option<String>,
    private_key: Option<[u8; 32]>,
}

impl HyperliquidClient {
    pub fn new(
        testnet: bool,
        wallet_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_endpoint(
            testnet,
            wallet_address,
            private_key,
            timeout,
            if testnet { TESTNET_URL } else { MAINNET_URL }.to_string(),
        )
    }

    pub fn with_endpoint(
        testnet: bool,
        wallet_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
        endpoint: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            endpoint,
            testnet,
            wallet_address,
            private_key: private_key.map(|key| parse_private_key(&key)).transpose()?,
        })
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, path, query_json, action_msgpack, signed)
            .await?;
        response.ensure_success()?;
        let data = response.json()?;
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
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?;
        let request = self.build_request(
            method,
            path,
            query_json,
            action_msgpack.as_deref(),
            signed,
            timestamp,
        )?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, query_json, action_msgpack, signed)
                .await
        })
    }

    pub async fn public_request(&self, query_json: Vec<u8>) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Post, "/info", query_json, None, false)
            .await
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        query_json: Vec<u8>,
        action_msgpack: Option<&[u8]>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        if !matches!(method, HttpMethod::Get | HttpMethod::Post) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Hyperliquid HTTP method: {}",
                http_method_name(method)
            )));
        }
        let mut query: Value = if query_json.is_empty() {
            Value::Object(Map::new())
        } else {
            serde_json::from_slice(&query_json)
                .map_err(|error| DcexError::Decode(error.to_string()))?
        };
        let query_object = query.as_object_mut().ok_or_else(|| {
            DcexError::InvalidInput("Hyperliquid query must be a JSON object.".to_string())
        })?;

        if signed {
            if self.wallet_address.is_none() || self.private_key.is_none() {
                return Err(DcexError::InvalidInput(
                    "Signed request requires Address and Private Key of wallet.".to_string(),
                ));
            }
            let action_msgpack = action_msgpack.ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Hyperliquid requests require MessagePack action bytes.".to_string(),
                )
            })?;
            let vault_address = query_object
                .get("vaultAddress")
                .and_then(Value::as_str)
                .filter(|value| !value.is_empty());
            let expire_after = query_object.get("expireAfter").and_then(Value::as_u64);
            let signature = hyperliquid_signature(
                action_msgpack,
                timestamp,
                vault_address,
                expire_after,
                self.testnet,
                self.private_key.as_ref().expect("checked private key"),
            )?;
            query_object.insert("nonce".to_string(), Value::Number(Number::from(timestamp)));
            query_object.insert(
                "signature".to_string(),
                serde_json::json!({
                    "r": signature.r,
                    "s": signature.s,
                    "v": signature.v,
                }),
            );
        }

        let path = path.into();
        let mut request = HttpRequest::new(method, &self.endpoint, &path)
            .header("Content-Type", "application/json");
        if method == HttpMethod::Get {
            let query_string = encode_query(query_object);
            if !query_string.is_empty() {
                request.path = format!("{path}?{query_string}");
            }
        } else {
            request.body = RequestBody::Raw(
                serde_json::to_vec(&query).map_err(|error| DcexError::Decode(error.to_string()))?,
            );
        }
        Ok(request)
    }
}

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
        r: hex::encode(&signature[..32]),
        s: hex::encode(&signature[32..64]),
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

fn parse_private_key(private_key: &str) -> Result<[u8; 32]> {
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

fn encode_query(query: &Map<String, Value>) -> String {
    let mut pairs = query
        .iter()
        .filter(|(_, value)| !value.is_null())
        .map(|(key, value)| (key.as_str(), python_value(value)))
        .collect::<Vec<_>>();
    pairs.sort_by(|left, right| left.0.cmp(right.0));
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(pairs)
        .finish()
}

fn python_value(value: &Value) -> String {
    match value {
        Value::Null => "None".to_string(),
        Value::Bool(value) => {
            if *value {
                "True".to_string()
            } else {
                "False".to_string()
            }
        }
        Value::Number(value) => value.to_string(),
        Value::String(value) => value.clone(),
        Value::Array(values) => format!(
            "[{}]",
            values
                .iter()
                .map(python_value_repr)
                .collect::<Vec<_>>()
                .join(", ")
        ),
        Value::Object(values) => format!(
            "{{{}}}",
            values
                .iter()
                .map(|(key, value)| format!("'{key}': {}", python_value_repr(value)))
                .collect::<Vec<_>>()
                .join(", ")
        ),
    }
}

fn python_value_repr(value: &Value) -> String {
    match value {
        Value::String(value) => format!("'{value}'"),
        _ => python_value(value),
    }
}

const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signature_matches_python_vector() {
        let action = hex::decode("82a474797065a56f72646572a16101").expect("msgpack");
        assert_eq!(
            hyperliquid_signature(&action, 1_700_000_000_000, None, None, false, &[0x11; 32],)
                .expect("signature"),
            HyperliquidSignature {
                r: "193f5e88d621ca384beca6146a4c059b8716d5ad3da0404f6cd36f020fc87671".to_string(),
                s: "0c3767a2287482caef8a77be7b5c76eac08d9d8fb3080c53033e394bbb35d047".to_string(),
                v: 27,
            }
        );
    }
}
