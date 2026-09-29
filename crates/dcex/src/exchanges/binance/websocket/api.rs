//! Binance Spot and USD-M WebSocket request/response APIs.
//!
//! Requests return their correlation ID after writing. `recv` preserves complete
//! responses (including errors, partial results and rate limits) and user events.
//! A background reader answers server pings while requests and reads run concurrently.
use std::sync::{
    Arc,
    atomic::{AtomicU64, Ordering},
};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use base64::{Engine, engine::general_purpose::STANDARD};
use ed25519_dalek::{Signer, SigningKey};
use serde_json::{Map, Value, json};
use tokio::sync::{Mutex, mpsc, oneshot};

use crate::crypto::hmac_sha256_hex;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::api_schema::{Auth, schema};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BinanceWebSocketApiMarket {
    Spot,
    Futures,
    CoinFutures,
}

enum ApiSigner {
    Hmac(String),
    Ed25519(SigningKey),
}
enum Command {
    Send(Value, oneshot::Sender<Result<()>>),
    Close(oneshot::Sender<Result<()>>),
}
#[derive(Clone)]
struct Session {
    commands: mpsc::Sender<Command>,
    events: Arc<Mutex<mpsc::Receiver<Result<Vec<u8>>>>>,
}

pub struct BinanceWebSocketApi {
    config: WebSocketConfig,
    market: BinanceWebSocketApiMarket,
    api_key: Option<String>,
    signer: Option<ApiSigner>,
    next_id: AtomicU64,
    session: Mutex<Option<Session>>,
}

impl BinanceWebSocketApi {
    pub(super) fn market_kind(&self) -> BinanceWebSocketApiMarket {
        self.market
    }
    /// `ed25519_seed` accepts a 32-byte seed encoded as 64 hexadecimal characters.
    /// Supply either an HMAC secret or an Ed25519 seed, together with the API key.
    pub fn new(
        market: BinanceWebSocketApiMarket,
        api_key: Option<String>,
        api_secret: Option<String>,
        ed25519_seed: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        let url = match market {
            BinanceWebSocketApiMarket::Spot => "wss://ws-api.binance.com:443/ws-api/v3",
            BinanceWebSocketApiMarket::Futures => "wss://ws-fapi.binance.com/ws-fapi/v1",
            BinanceWebSocketApiMarket::CoinFutures => "wss://ws-dapi.binance.com/ws-dapi/v1",
        };
        Self::with_url(market, api_key, api_secret, ed25519_seed, timeout, url)
    }

    pub fn with_url(
        market: BinanceWebSocketApiMarket,
        api_key: Option<String>,
        api_secret: Option<String>,
        ed25519_seed: Option<String>,
        timeout: Duration,
        url: impl Into<String>,
    ) -> Result<Self> {
        if api_secret.is_some() && ed25519_seed.is_some() {
            return Err(invalid("choose HMAC or Ed25519 credentials"));
        }
        if api_key.as_ref().is_some_and(|v| v.trim().is_empty())
            || api_secret.as_ref().is_some_and(|v| v.is_empty())
        {
            return Err(invalid("credentials must not be empty"));
        }
        if api_key.is_none() && (api_secret.is_some() || ed25519_seed.is_some()) {
            return Err(invalid("api_key is required with signing credentials"));
        }
        let signer = if let Some(seed) = ed25519_seed {
            let bytes = hex::decode(seed)
                .map_err(|_| invalid("ed25519_seed must be 64 hexadecimal characters"))?;
            let seed: [u8; 32] = bytes
                .try_into()
                .map_err(|_| invalid("ed25519_seed must contain exactly 32 bytes"))?;
            Some(ApiSigner::Ed25519(SigningKey::from_bytes(&seed)))
        } else {
            api_secret.map(ApiSigner::Hmac)
        };
        Ok(Self {
            config: WebSocketConfig::new(url, timeout)?,
            market,
            api_key,
            signer,
            next_id: AtomicU64::new(1),
            session: Mutex::new(None),
        })
    }

    pub async fn connect(&self) -> Result<()> {
        let mut session = self.session.lock().await;
        if session.as_ref().is_some_and(|s| !s.commands.is_closed()) {
            return Ok(());
        }
        let mut connection = WebSocketConnection::new(self.config.clone());
        connection.connect().await?;
        let (commands, command_rx) = mpsc::channel(64);
        let (events, event_rx) = mpsc::channel(1024);
        tokio::spawn(run(connection, command_rx, events));
        *session = Some(Session {
            commands,
            events: Arc::new(Mutex::new(event_rx)),
        });
        Ok(())
    }

    pub async fn close(&self) -> Result<()> {
        let Some(session) = self.session.lock().await.take() else {
            return Ok(());
        };
        let (ack, result) = oneshot::channel();
        if session.commands.send(Command::Close(ack)).await.is_err() {
            return Ok(());
        }
        result.await.map_err(|_| disconnected())?
    }

    /// Native Binance symbol names and JSON parameter types are preserved.
    /// Decimal quantities/prices must be strings; integer fields must be numbers.
    /// `timestamp` may be supplied for clock synchronization; otherwise it is added.
    /// Caller-supplied apiKey/signature are rejected to prevent accidental overrides.
    pub async fn request(&self, method: &str, params: Value) -> Result<u64> {
        let payload = self.prepare(method, params)?;
        let id = payload["id"].as_u64().expect("locally generated ID");
        let session = self.current().await?;
        let (ack, result) = oneshot::channel();
        session
            .commands
            .send(Command::Send(payload, ack))
            .await
            .map_err(|_| disconnected())?;
        result.await.map_err(|_| disconnected())??;
        Ok(id)
    }

    pub async fn recv_bytes(&self) -> Result<Vec<u8>> {
        let session = self.current().await?;
        let mut events = session.events.lock().await;
        tokio::time::timeout(self.config.timeout, events.recv())
            .await
            .map_err(|_| DcexError::Transport("Binance WebSocket API receive timed out".into()))?
            .ok_or_else(disconnected)?
    }

    pub async fn recv(&self) -> Result<Value> {
        serde_json::from_slice(&self.recv_bytes().await?)
            .map_err(|e| DcexError::Decode(e.to_string()))
    }

    async fn current(&self) -> Result<Session> {
        self.session.lock().await.clone().ok_or_else(disconnected)
    }

    fn prepare(&self, method: &str, params: Value) -> Result<Value> {
        let (auth, fields) = schema(self.market, method)
            .ok_or_else(|| invalid("unsupported method for this market"))?;
        let mut params = params
            .as_object()
            .cloned()
            .ok_or_else(|| invalid("params must be a JSON object"))?;
        if params.contains_key("apiKey") || params.contains_key("signature") {
            return Err(invalid("apiKey and signature are managed by the client"));
        }
        super::api_validation::validate(self.market, method, &params, fields)?;
        if method == "session.logon" && !matches!(self.signer, Some(ApiSigner::Ed25519(_))) {
            return Err(invalid("session.logon requires Ed25519 credentials"));
        }
        if auth != Auth::Public {
            params.insert(
                "apiKey".into(),
                json!(
                    self.api_key
                        .as_ref()
                        .ok_or_else(|| invalid("api_key is required"))?
                ),
            );
        }
        if auth == Auth::Signed {
            if !params.contains_key("timestamp") {
                let timestamp = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .map_err(|_| invalid("system clock precedes Unix epoch"))?
                    .as_millis();
                params.insert(
                    "timestamp".into(),
                    json!(u64::try_from(timestamp).map_err(|_| invalid("timestamp overflow"))?),
                );
            }
            let payload = signature_payload(&params)?;
            let signature = match self
                .signer
                .as_ref()
                .ok_or_else(|| invalid("signing credentials are required"))?
            {
                ApiSigner::Hmac(secret) => hmac_sha256_hex(secret.as_bytes(), payload.as_bytes())?,
                ApiSigner::Ed25519(key) => STANDARD.encode(key.sign(payload.as_bytes()).to_bytes()),
            };
            params.insert("signature".into(), json!(signature));
        }
        let id = self
            .next_id
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |id| id.checked_add(1))
            .map_err(|_| invalid("request ID range exhausted"))?;
        Ok(json!({"id":id,"method":method,"params":params}))
    }
}

fn signature_payload(params: &Map<String, Value>) -> Result<String> {
    let mut keys: Vec<_> = params.keys().collect();
    keys.sort_unstable();
    keys.into_iter()
        .map(|key| {
            let value = match &params[key] {
                Value::String(value) => value.clone(),
                Value::Number(_) | Value::Bool(_) => params[key].to_string(),
                _ => return Err(invalid("signed parameters must be scalar JSON values")),
            };
            Ok(format!("{key}={value}"))
        })
        .collect::<Result<Vec<_>>>()
        .map(|values| values.join("&"))
}

async fn run(
    mut connection: WebSocketConnection,
    mut commands: mpsc::Receiver<Command>,
    events: mpsc::Sender<Result<Vec<u8>>>,
) {
    loop {
        tokio::select! {
            command = commands.recv() => match command {
                Some(Command::Send(value, ack)) => {
                    let result = connection.send_json(&value).await;
                    let failed = result.is_err();
                    let _ = ack.send(result);
                    if failed { break; }
                },
                Some(Command::Close(ack)) => { let _ = ack.send(connection.close().await); break; },
                None => break,
            },
            event = connection.recv_bytes() => {
                // An idle connection is normal; the actor must keep servicing writes.
                if matches!(&event, Err(DcexError::Transport(message)) if message == "WebSocket receive timed out.") { continue; }
                let failed = event.is_err();
                // Do not silently discard events. Buffer exhaustion disconnects;
                // the consumer drains queued events then receives a transport error.
                if events.try_send(event).is_err() || failed { break; }
            }
        }
    }
    let _ = connection.close().await;
}

use crate::exchanges::binance::params::invalid_ws as invalid;
fn disconnected() -> DcexError {
    DcexError::Transport(
        "Binance WebSocket API disconnected; reconnect and reconcile orders before retrying".into(),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn official_hmac_vector() {
        let client = BinanceWebSocketApi::new(
            BinanceWebSocketApiMarket::Spot,
            Some("vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A".into()),
            Some("NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j".into()),
            None,
            Duration::from_secs(5),
        )
        .unwrap();
        let request = client.prepare("order.place",json!({"symbol":"BTCUSDT","side":"SELL","type":"LIMIT","timeInForce":"GTC","quantity":"0.01000000","price":"52000.00","recvWindow":100,"timestamp":1645423376532_i64})).unwrap();
        assert_eq!(
            request["params"]["signature"],
            "aa1b5712c094bc4e57c05a1a5c1fd8d88dcd628338ea863fec7b88e59fe2db24"
        );
    }
    #[test]
    fn utf8_payload_is_not_url_encoded() {
        assert_eq!(
            signature_payload(
                json!({"symbol":"１２３４５６USDT","timestamp":1})
                    .as_object()
                    .unwrap()
            )
            .unwrap(),
            "symbol=１２３４５６USDT&timestamp=1"
        );
    }
    #[test]
    fn ed25519_logon_signs_exact_sorted_payload() {
        use ed25519_dalek::{Signature, Verifier, VerifyingKey};
        // RFC 8032 test key; verification uses its independently published public key.
        let client = BinanceWebSocketApi::new(
            BinanceWebSocketApiMarket::Spot,
            Some("test-key".into()),
            None,
            Some("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60".into()),
            Duration::from_secs(2),
        )
        .unwrap();
        let payload = client
            .prepare(
                "session.logon",
                json!({"timestamp":1645423376532_i64,"recvWindow":5000}),
            )
            .unwrap();
        let bytes = STANDARD
            .decode(payload["params"]["signature"].as_str().unwrap())
            .unwrap();
        let signature = Signature::from_slice(&bytes).unwrap();
        let public: [u8; 32] =
            hex::decode("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
                .unwrap()
                .try_into()
                .unwrap();
        VerifyingKey::from_bytes(&public)
            .unwrap()
            .verify(
                b"apiKey=test-key&recvWindow=5000&timestamp=1645423376532",
                &signature,
            )
            .unwrap();
        assert_eq!(payload["method"], "session.logon");
    }
}
