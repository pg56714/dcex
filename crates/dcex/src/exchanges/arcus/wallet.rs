//! Read-only Robinhood Chain data for self-custodied Arcus Spot wallets.

use std::collections::{BTreeMap, HashSet};

use num_bigint::BigUint;
use serde_json::{Value, json};
use sha3::{Digest, Keccak256};

use super::ArcusSpotClient;
use crate::exchange::ValidatedResponse;
use crate::http::{HttpMethod, HttpRequest};
use crate::{DcexError, Result};

const PERMIT2: &str = "0x000000000022D473030F116dDEE9F6B43aC78BA3";
const MAINNET_SWAP_SHELL: &str = "0x4262efBd176F02824af27010bEa218429c33c7E8";
const TESTNET_SWAP_SHELL: &str = "0x528B30910B3ef5a615cDC3847F273947dc474519";
const SWAP_EXECUTED_SIGNATURE: &str = "SwapExecuted(address,address,address,uint256,uint256,uint256,uint256,uint256,uint256,uint256,address,bytes32,bool,string)";

impl ArcusSpotClient {
    /// Read wallet state over Robinhood Chain JSON-RPC; no Perps credentials are used.
    pub async fn wallet_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let values: BTreeMap<_, _> = params.into_iter().collect();
        let allowed: &[&str] = match method_name {
            "get_native_balance" => &["address"],
            "get_balances" => &["address", "tokens_json", "include_wrapped"],
            "get_token_balance" => &["address", "token"],
            "get_allowance" => &["address", "token", "spender"],
            "get_transaction_receipt" => &["tx_hash"],
            "get_block_number" => &[],
            "get_trade_history" => &[
                "address",
                "from_block",
                "to_block",
                "token_in",
                "token_out",
                "swap_shell",
            ],
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus spot wallet method: {method_name}"
                )));
            }
        };
        if let Some(key) = values.keys().find(|key| !allowed.contains(&key.as_str())) {
            return Err(DcexError::InvalidInput(format!(
                "unknown Arcus spot wallet parameter: {key}"
            )));
        }
        if matches!(
            method_name,
            "get_native_balance"
                | "get_token_balance"
                | "get_allowance"
                | "get_balances"
                | "get_trade_history"
        ) {
            self.wallet_address(&values)?;
        }
        if matches!(method_name, "get_token_balance" | "get_allowance") {
            required_address(&values, "token")?;
        }
        if method_name == "get_transaction_receipt" {
            validate_hash(required(&values, "tx_hash")?)?;
        }
        if method_name == "get_trade_history" {
            decimal_block(required(&values, "from_block")?)?;
        }
        self.verify_rpc_chain().await?;
        let data = match method_name {
            "get_native_balance" => {
                let address = self.wallet_address(&values)?;
                let result = self
                    .rpc_call("eth_getBalance", json!([address, "latest"]))
                    .await?;
                json!({"chainId": self.chain_id, "address": address, "symbol": "ETH", "decimals": 18, "balance": decimal_quantity(&result)?})
            }
            "get_token_balance" => {
                let address = self.wallet_address(&values)?;
                let token = required_address(&values, "token")?;
                let balance = self.token_balance(&address, &token).await?;
                json!({"chainId": self.chain_id, "address": address, "token": token, "balance": balance})
            }
            "get_allowance" => {
                let address = self.wallet_address(&values)?;
                let token = required_address(&values, "token")?;
                let spender = values.get("spender").map(String::as_str).unwrap_or(PERMIT2);
                validate_address(spender)?;
                let data = format!(
                    "0xdd62ed3e{}{}",
                    encode_address(&address),
                    encode_address(spender)
                );
                let result = self.eth_call(&token, &data).await?;
                json!({"chainId": self.chain_id, "address": address, "token": token, "spender": spender, "allowance": decimal_quantity(&result)?})
            }
            "get_balances" => {
                let address = self.wallet_address(&values)?;
                let include_wrapped = match values.get("include_wrapped").map(String::as_str) {
                    None | Some("true") => true,
                    Some("false") => false,
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "Arcus spot include_wrapped must be true or false".into(),
                        ));
                    }
                };
                let tokens = if let Some(raw) = values.get("tokens_json") {
                    let tokens: Value = serde_json::from_str(raw).map_err(|_| {
                        DcexError::InvalidInput("invalid Arcus spot tokens_json".into())
                    })?;
                    tokens.as_array().cloned().ok_or_else(|| {
                        DcexError::InvalidInput("Arcus spot tokens_json must be an array".into())
                    })?
                } else {
                    let response = self.router_request("get_tokens", vec![]).await?;
                    response.data.as_array().cloned().ok_or_else(|| {
                        DcexError::Decode("Arcus spot token list must be an array".into())
                    })?
                };
                let native = self
                    .rpc_call("eth_getBalance", json!([address, "latest"]))
                    .await?;
                let mut balances = vec![
                    json!({"symbol": "ETH", "decimals": 18, "balance": decimal_quantity(&native)?}),
                ];
                let mut entries = Vec::with_capacity(tokens.len() * 2);
                let mut seen = HashSet::new();
                for token in &tokens {
                    let token_address = token
                        .as_str()
                        .or_else(|| token["address"].as_str())
                        .ok_or_else(|| {
                            DcexError::InvalidInput("Arcus spot token address is required".into())
                        })?;
                    validate_address(token_address)?;
                    if seen.insert(token_address.to_ascii_lowercase()) {
                        let mut entry = json!({"token": token_address, "kind": "underlying"});
                        if let Some(symbol) = token["symbol"].as_str() {
                            entry["symbol"] = json!(symbol);
                        }
                        if let Some(decimals) = token["decimals"].as_u64() {
                            entry["decimals"] = json!(decimals);
                        }
                        entries.push(entry);
                    }
                    if include_wrapped {
                        if let Some(wrapped) = token["wrappedTokenAddress"]
                            .as_str()
                            .filter(|wrapped| !wrapped.is_empty())
                        {
                            validate_address(wrapped)?;
                            if seen.insert(wrapped.to_ascii_lowercase()) {
                                let mut entry = json!({
                                    "token": wrapped, "kind": "wrapped", "underlyingToken": token_address,
                                });
                                if let Some(symbol) = token["symbol"].as_str() {
                                    entry["underlyingSymbol"] = json!(symbol);
                                }
                                if let Some(decimals) = token["decimals"].as_u64() {
                                    entry["decimals"] = json!(decimals);
                                }
                                entries.push(entry);
                            }
                        }
                    }
                }
                let addresses = entries
                    .iter()
                    .filter_map(|entry| entry["token"].as_str())
                    .map(str::to_string)
                    .collect::<Vec<_>>();
                let token_balances = self.token_balances(&address, &addresses).await?;
                for (mut entry, balance) in entries.into_iter().zip(token_balances) {
                    entry["balance"] = json!(balance);
                    balances.push(entry);
                }
                json!({"chainId": self.chain_id, "address": address, "balances": balances})
            }
            "get_transaction_receipt" => {
                let hash = required(&values, "tx_hash")?;
                validate_hash(hash)?;
                self.rpc_call("eth_getTransactionReceipt", json!([hash]))
                    .await?
            }
            "get_block_number" => {
                let result = self.rpc_call("eth_blockNumber", json!([])).await?;
                json!({"chainId": self.chain_id, "blockNumber": decimal_quantity(&result)?})
            }
            "get_trade_history" => self.trade_history(&values).await?,
            _ => unreachable!(),
        };
        Ok(ValidatedResponse {
            status: 200,
            headers: BTreeMap::new(),
            data,
        })
    }

    async fn token_balance(&self, address: &str, token: &str) -> Result<String> {
        let data = format!("0x70a08231{}", encode_address(address));
        decimal_token_quantity(&self.eth_call(token, &data).await?)
    }

    async fn token_balances(&self, owner: &str, tokens: &[String]) -> Result<Vec<String>> {
        let mut balances = Vec::with_capacity(tokens.len());
        for chunk in tokens.chunks(25) {
            if chunk.len() == 1 {
                balances.push(self.token_balance(owner, &chunk[0]).await?);
                continue;
            }
            let calls = chunk.iter().enumerate().map(|(index, token)| {
                json!({
                    "jsonrpc": "2.0", "id": index + 1, "method": "eth_call",
                    "params": [{"to": token, "data": format!("0x70a08231{}", encode_address(owner))}, "latest"]
                })
            }).collect::<Vec<_>>();
            match self.rpc_batch(calls).await {
                Ok(results) => {
                    for result in results {
                        balances.push(decimal_token_quantity(&result)?);
                    }
                }
                Err(_) => {
                    // Some third-party RPC providers disable JSON-RPC batching.
                    for token in chunk {
                        balances.push(self.token_balance(owner, token).await?);
                    }
                }
            }
        }
        Ok(balances)
    }

    async fn eth_call(&self, token: &str, data: &str) -> Result<Value> {
        self.rpc_call("eth_call", json!([{"to": token, "data": data}, "latest"]))
            .await
    }

    fn wallet_address(&self, values: &BTreeMap<String, String>) -> Result<String> {
        let address = values
            .get("address")
            .or(self.wallet_address.as_ref())
            .ok_or_else(|| {
                DcexError::InvalidInput("Arcus Spot wallet address is required".into())
            })?;
        validate_address(address)?;
        Ok(address.clone())
    }

    async fn verify_rpc_chain(&self) -> Result<()> {
        let result = self.rpc_call("eth_chainId", json!([])).await?;
        let chain_id: u64 = parse_quantity(&result)?.try_into().map_err(|_| {
            DcexError::Decode("Arcus wallet RPC returned an invalid chain ID".into())
        })?;
        if chain_id != self.chain_id {
            return Err(DcexError::InvalidInput(format!(
                "Arcus wallet RPC chain ID {chain_id} does not match selected network {}",
                self.chain_id
            )));
        }
        Ok(())
    }

    async fn rpc_call(&self, method: &str, params: Value) -> Result<Value> {
        let request = HttpRequest::new(HttpMethod::Post, &self.rpc_url, "")
            .json(json!({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}));
        let response = self.transport.execute(request).await?;
        response.ensure_success()?;
        let body = response.json()?;
        if let Some(error) = body.get("error") {
            return Err(DcexError::Runtime(format!(
                "Arcus wallet RPC {method} failed: {error}"
            )));
        }
        body.get("result").cloned().ok_or_else(|| {
            DcexError::Decode(format!("Arcus wallet RPC {method} returned no result"))
        })
    }

    async fn rpc_batch(&self, calls: Vec<Value>) -> Result<Vec<Value>> {
        let request =
            HttpRequest::new(HttpMethod::Post, &self.rpc_url, "").json(Value::Array(calls.clone()));
        let response = self.transport.execute(request).await?;
        response.ensure_success()?;
        let body = response.json()?;
        let replies = body.as_array().ok_or_else(|| {
            DcexError::Decode("Arcus wallet RPC batch must return an array".into())
        })?;
        if replies.len() != calls.len() {
            return Err(DcexError::Decode(
                "Arcus wallet RPC batch returned the wrong number of results".into(),
            ));
        }
        let mut results = vec![Value::Null; calls.len()];
        let mut seen = vec![false; calls.len()];
        for reply in replies {
            let index = reply["id"]
                .as_u64()
                .and_then(|id| id.checked_sub(1))
                .and_then(|index| usize::try_from(index).ok())
                .filter(|index| *index < calls.len())
                .ok_or_else(|| DcexError::Decode("Arcus wallet RPC batch ID is invalid".into()))?;
            if seen[index] {
                return Err(DcexError::Decode(
                    "Arcus wallet RPC batch ID is duplicated".into(),
                ));
            }
            if let Some(error) = reply.get("error") {
                return Err(DcexError::Runtime(format!(
                    "Arcus wallet RPC eth_call batch failed: {error}"
                )));
            }
            results[index] = reply.get("result").cloned().ok_or_else(|| {
                DcexError::Decode("Arcus wallet RPC batch result is missing".into())
            })?;
            seen[index] = true;
        }
        Ok(results)
    }

    async fn trade_history(&self, values: &BTreeMap<String, String>) -> Result<Value> {
        let address = self.wallet_address(values)?;
        let from = decimal_block(required(values, "from_block")?)?;
        let to = values
            .get("to_block")
            .map(|value| decimal_block(value))
            .transpose()?;
        if to.is_some_and(|end| end < from) {
            return Err(DcexError::InvalidInput(
                "Arcus spot to_block must not precede from_block".into(),
            ));
        }
        let swap_shell = values
            .get("swap_shell")
            .map(String::as_str)
            .unwrap_or_else(|| {
                if self.chain_id == 46630 {
                    TESTNET_SWAP_SHELL
                } else {
                    MAINNET_SWAP_SHELL
                }
            });
        validate_address(swap_shell)?;
        let token_in = values.get("token_in").map(String::as_str);
        let token_out = values.get("token_out").map(String::as_str);
        for token in [token_in, token_out].into_iter().flatten() {
            validate_address(token)?;
        }
        let topic0 = format!(
            "0x{}",
            hex::encode(Keccak256::digest(SWAP_EXECUTED_SIGNATURE.as_bytes()))
        );
        let filter = json!({
            "address": swap_shell,
            "fromBlock": format!("0x{from:x}"),
            "toBlock": to.map_or_else(|| "latest".to_string(), |end| format!("0x{end:x}")),
            "topics": [topic0, topic_address(&address), token_in.map(topic_address), token_out.map(topic_address)],
        });
        let result = self.rpc_call("eth_getLogs", json!([filter])).await?;
        let logs = result.as_array().ok_or_else(|| {
            DcexError::Decode("Arcus wallet RPC eth_getLogs result must be an array".into())
        })?;
        let trades: Result<Vec<_>> = logs.iter().map(decode_swap_log).collect();
        Ok(json!({"chainId": self.chain_id, "address": address, "trades": trades?}))
    }
}

fn required<'a>(values: &'a BTreeMap<String, String>, key: &str) -> Result<&'a str> {
    values
        .get(key)
        .map(String::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| DcexError::InvalidInput(format!("Arcus spot {key} is required")))
}

fn required_address(values: &BTreeMap<String, String>, key: &str) -> Result<String> {
    let address = required(values, key)?;
    validate_address(address)?;
    Ok(address.into())
}

fn validate_address(address: &str) -> Result<()> {
    if address.len() != 42
        || !address.starts_with("0x")
        || !address[2..].bytes().all(|byte| byte.is_ascii_hexdigit())
    {
        return Err(DcexError::InvalidInput(
            "invalid Arcus Spot wallet or token address".into(),
        ));
    }
    Ok(())
}

fn validate_hash(hash: &str) -> Result<()> {
    if hash.len() != 66
        || !hash.starts_with("0x")
        || !hash[2..].bytes().all(|byte| byte.is_ascii_hexdigit())
    {
        return Err(DcexError::InvalidInput(
            "invalid Arcus Spot transaction hash".into(),
        ));
    }
    Ok(())
}

fn encode_address(address: &str) -> String {
    format!("{:0>64}", &address[2..].to_ascii_lowercase())
}

fn topic_address(address: &str) -> String {
    format!("0x{}", encode_address(address))
}

fn parse_quantity(value: &Value) -> Result<BigUint> {
    let hex = value
        .as_str()
        .and_then(|raw| raw.strip_prefix("0x"))
        .ok_or_else(|| {
            DcexError::Decode("Arcus wallet RPC quantity must be 0x-prefixed hex".into())
        })?;
    BigUint::parse_bytes(hex.as_bytes(), 16)
        .ok_or_else(|| DcexError::Decode("invalid Arcus wallet RPC hex quantity".into()))
}

fn decimal_quantity(value: &Value) -> Result<String> {
    Ok(parse_quantity(value)?.to_str_radix(10))
}

fn decimal_token_quantity(value: &Value) -> Result<String> {
    if value.as_str() == Some("0x") {
        // A predicted wrapped token may not have a deployed contract yet.
        return Ok("0".into());
    }
    decimal_quantity(value)
}

fn decimal_block(value: &str) -> Result<u64> {
    value.parse::<u64>().map_err(|_| {
        DcexError::InvalidInput("Arcus spot block number must be a decimal u64".into())
    })
}

fn decode_swap_log(log: &Value) -> Result<Value> {
    let topics = log["topics"]
        .as_array()
        .ok_or_else(|| DcexError::Decode("Arcus SwapExecuted log has no topics".into()))?;
    if topics.len() != 4 {
        return Err(DcexError::Decode(
            "Arcus SwapExecuted log has invalid topics".into(),
        ));
    }
    let data = log["data"]
        .as_str()
        .and_then(|text| text.strip_prefix("0x"))
        .ok_or_else(|| DcexError::Decode("Arcus SwapExecuted log has no data".into()))?;
    if data.len() < 11 * 64 || !data.bytes().all(|byte| byte.is_ascii_hexdigit()) {
        return Err(DcexError::Decode(
            "Arcus SwapExecuted log has invalid data".into(),
        ));
    }
    let address_topic = |index: usize| -> Result<String> {
        let topic = topics[index]
            .as_str()
            .ok_or_else(|| DcexError::Decode("Arcus SwapExecuted topic must be hex".into()))?;
        if topic.len() != 66 || !topic.starts_with("0x") {
            return Err(DcexError::Decode(
                "Arcus SwapExecuted address topic is invalid".into(),
            ));
        }
        Ok(format!("0x{}", &topic[26..]))
    };
    let word = |index: usize| -> Result<String> {
        let part = &data[index * 64..(index + 1) * 64];
        Ok(BigUint::parse_bytes(part.as_bytes(), 16)
            .ok_or_else(|| DcexError::Decode("invalid Arcus SwapExecuted amount".into()))?
            .to_str_radix(10))
    };
    Ok(json!({
        "transactionHash": log["transactionHash"],
        "blockNumber": decimal_quantity(&log["blockNumber"])?,
        "logIndex": decimal_quantity(&log["logIndex"])?,
        "taker": address_topic(1)?,
        "tokenIn": address_topic(2)?,
        "tokenOut": address_topic(3)?,
        "amountIn": word(1)?,
        "amountOut": word(4)?,
        "minAmountOut": word(0)?,
        "quotedAmountIn": word(2)?,
        "quotedAmountOut": word(3)?,
        "routeTag": format!("0x{}", &data[8 * 64..9 * 64]),
        "success": word(9)? == "1",
        "raw": log,
    }))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::thread;
    use std::time::Duration;

    use crate::http::block_on;

    fn rpc_server(results: Vec<Value>) -> (String, thread::JoinHandle<Vec<Value>>) {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let url = format!("http://{}", listener.local_addr().expect("address"));
        let handle = thread::spawn(move || {
            let mut requests = Vec::new();
            for result in results {
                let (mut stream, _) = listener.accept().expect("accept");
                stream
                    .set_read_timeout(Some(Duration::from_secs(3)))
                    .expect("timeout");
                let mut raw = Vec::new();
                let header_end = loop {
                    let mut chunk = [0; 4096];
                    let size = stream.read(&mut chunk).expect("read");
                    assert!(size > 0, "unexpected EOF");
                    raw.extend_from_slice(&chunk[..size]);
                    if let Some(end) = raw.windows(4).position(|part| part == b"\r\n\r\n") {
                        break end + 4;
                    }
                };
                let headers = String::from_utf8_lossy(&raw[..header_end]);
                let length = headers
                    .lines()
                    .find_map(|line| {
                        line.to_ascii_lowercase()
                            .strip_prefix("content-length: ")
                            .and_then(|value| value.trim().parse::<usize>().ok())
                    })
                    .expect("content length");
                while raw.len() < header_end + length {
                    let mut chunk = [0; 4096];
                    let size = stream.read(&mut chunk).expect("body");
                    assert!(size > 0, "unexpected body EOF");
                    raw.extend_from_slice(&chunk[..size]);
                }
                requests.push(
                    serde_json::from_slice::<Value>(&raw[header_end..header_end + length])
                        .expect("JSON-RPC request"),
                );
                let payload = if requests.last().is_some_and(Value::is_array) {
                    result.to_string()
                } else {
                    json!({"jsonrpc": "2.0", "id": 1, "result": result}).to_string()
                };
                write!(stream, "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}", payload.len(), payload).expect("reply");
            }
            requests
        });
        (url, handle)
    }

    #[test]
    fn reads_spot_wallet_balances_and_permit2_allowance() {
        let (rpc_url, server) = rpc_server(vec![
            json!("0x1237"),
            json!("0xde0b6b3a7640000"),
            json!("0x1237"),
            json!("0x64"),
            json!("0x1237"),
            json!("0xff"),
            json!("0x1237"),
            json!("0x0"),
            json!("0x2a"),
            json!("0x1237"),
            json!([]),
        ]);
        let wallet = format!("0x{}", "11".repeat(20));
        let token = format!("0x{}", "22".repeat(20));
        let client = ArcusSpotClient::new(None, false, Duration::from_secs(3))
            .unwrap()
            .with_wallet_address(wallet.clone())
            .unwrap()
            .with_rpc_url(rpc_url)
            .unwrap();
        block_on(async move {
            let native = client.wallet_request("get_native_balance", vec![]).await?;
            assert_eq!(native.data["balance"], "1000000000000000000");
            let balance = client
                .wallet_request("get_token_balance", vec![("token".into(), token.clone())])
                .await?;
            assert_eq!(balance.data["balance"], "100");
            let allowance = client
                .wallet_request("get_allowance", vec![("token".into(), token.clone())])
                .await?;
            assert_eq!(allowance.data["allowance"], "255");
            assert_eq!(allowance.data["spender"], PERMIT2);
            let balances = client
                .wallet_request(
                    "get_balances",
                    vec![(
                        "tokens_json".into(),
                        json!([{"address": token, "symbol": "TEST", "decimals": 6}]).to_string(),
                    )],
                )
                .await?;
            assert_eq!(balances.data["balances"][0]["balance"], "0");
            assert_eq!(balances.data["balances"][1]["balance"], "42");
            assert_eq!(balances.data["balances"][1]["symbol"], "TEST");
            let trades = client
                .wallet_request(
                    "get_trade_history",
                    vec![("from_block".into(), "100".into())],
                )
                .await?;
            assert_eq!(trades.data["trades"], json!([]));
            Ok(())
        })
        .unwrap();
        let requests = server.join().unwrap();
        assert_eq!(requests.len(), 11);
        assert_eq!(requests[1]["method"], "eth_getBalance");
        assert_eq!(requests[3]["method"], "eth_call");
        assert!(
            requests[3]["params"][0]["data"]
                .as_str()
                .unwrap()
                .starts_with("0x70a08231")
        );
        assert!(
            requests[5]["params"][0]["data"]
                .as_str()
                .unwrap()
                .starts_with("0xdd62ed3e")
        );
        assert_eq!(requests[10]["method"], "eth_getLogs");
        assert_eq!(requests[10]["params"][0]["fromBlock"], "0x64");
    }

    #[test]
    fn rejects_rpc_on_wrong_chain_before_reading_balance() {
        let (rpc_url, server) = rpc_server(vec![json!("0xaa36a7")]);
        let client = ArcusSpotClient::new(None, false, Duration::from_secs(3))
            .unwrap()
            .with_wallet_address(format!("0x{}", "11".repeat(20)))
            .unwrap()
            .with_rpc_url(rpc_url)
            .unwrap();
        let error =
            block_on(async move { client.wallet_request("get_native_balance", vec![]).await })
                .expect_err("wrong chain must fail");
        assert!(
            error
                .to_string()
                .contains("does not match selected network")
        );
        assert_eq!(server.join().unwrap().len(), 1);
    }

    #[test]
    fn batch_balance_results_are_matched_by_json_rpc_id() {
        let (rpc_url, server) = rpc_server(vec![
            json!("0x1237"),
            json!("0x0"),
            json!([
                {"jsonrpc": "2.0", "id": 2, "result": "0x14"},
                {"jsonrpc": "2.0", "id": 1, "result": "0xa"},
            ]),
        ]);
        let wallet = format!("0x{}", "11".repeat(20));
        let first = format!("0x{}", "22".repeat(20));
        let second = format!("0x{}", "33".repeat(20));
        let client = ArcusSpotClient::new(None, false, Duration::from_secs(3))
            .unwrap()
            .with_wallet_address(wallet)
            .unwrap()
            .with_rpc_url(rpc_url)
            .unwrap();
        let balances = block_on(async move {
            client
                .wallet_request(
                    "get_balances",
                    vec![(
                        "tokens_json".into(),
                        json!([{"address": first, "wrappedTokenAddress": second, "symbol": "TEST"}]).to_string(),
                    )],
                )
                .await
        })
        .unwrap();
        assert_eq!(balances.data["balances"][1]["balance"], "10");
        assert_eq!(balances.data["balances"][2]["balance"], "20");
        assert_eq!(balances.data["balances"][2]["kind"], "wrapped");
        let requests = server.join().unwrap();
        assert!(requests[2].is_array());
        assert_eq!(requests[2][0]["method"], "eth_call");
    }

    #[test]
    fn decodes_swap_execution_amounts() {
        assert_eq!(decimal_token_quantity(&json!("0x")).unwrap(), "0");
        let address = format!("0x{}", "11".repeat(20));
        let data = [0, 10, 10, 20, 19, 0, 0, 0, 0, 1, 352]
            .map(|word| format!("{word:064x}"))
            .join("");
        let log = json!({
            "transactionHash": format!("0x{}", "aa".repeat(32)),
            "blockNumber": "0x10", "logIndex": "0x0",
            "topics": [format!("0x{}", "00".repeat(32)), topic_address(&address), topic_address(&address), topic_address(&address)],
            "data": format!("0x{data}"),
        });
        let decoded = decode_swap_log(&log).unwrap();
        assert_eq!(decoded["amountIn"], "10");
        assert_eq!(decoded["amountOut"], "19");
        assert_eq!(decoded["success"], true);
        assert_eq!(decoded["blockNumber"], "16");
    }
}
