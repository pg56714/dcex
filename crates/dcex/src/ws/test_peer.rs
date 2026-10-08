//! A local WebSocket peer for unit tests: records every text frame a client sends and
//! pushes scripted frames back, across reconnects. Never reaches a real exchange.

use std::time::Duration;

use futures_util::{SinkExt, StreamExt};
use serde_json::Value;
use tokio::net::TcpListener;
use tokio::sync::mpsc;
use tokio_tungstenite::accept_hdr_async;
use tokio_tungstenite::tungstenite::Message;
use tokio_tungstenite::tungstenite::handshake::server::{Request, Response};

pub(crate) struct TestPeer {
    pub url: String,
    received: mpsc::UnboundedReceiver<String>,
    outgoing: mpsc::UnboundedSender<Message>,
    /// One entry per accepted connection: the request path and lower-cased headers.
    connections: mpsc::UnboundedReceiver<Handshake>,
    pongs: mpsc::UnboundedReceiver<Vec<u8>>,
}

#[derive(Debug, Clone)]
pub(crate) struct Handshake {
    pub path: String,
    pub headers: Vec<(String, String)>,
}

impl Handshake {
    pub(crate) fn header(&self, name: &str) -> Option<&str> {
        let name = name.to_ascii_lowercase();
        self.headers
            .iter()
            .find(|(key, _)| *key == name)
            .map(|(_, value)| value.as_str())
    }
}

impl TestPeer {
    pub(crate) async fn start() -> Self {
        let listener = TcpListener::bind("127.0.0.1:0").await.expect("bind");
        let url = format!("ws://{}", listener.local_addr().expect("address"));
        let (received_tx, received) = mpsc::unbounded_channel();
        let (outgoing, mut outgoing_rx) = mpsc::unbounded_channel::<Message>();
        let (connected_tx, connections) = mpsc::unbounded_channel();
        let (pong_tx, pongs) = mpsc::unbounded_channel();
        tokio::spawn(async move {
            while let Ok((stream, _)) = listener.accept().await {
                let mut handshake = None;
                let callback = |request: &Request, response: Response| {
                    handshake = Some(Handshake {
                        path: request.uri().to_string(),
                        headers: request
                            .headers()
                            .iter()
                            .map(|(key, value)| {
                                (
                                    key.as_str().to_ascii_lowercase(),
                                    value.to_str().unwrap_or_default().to_string(),
                                )
                            })
                            .collect(),
                    });
                    Ok(response)
                };
                let Ok(socket) = accept_hdr_async(stream, callback).await else {
                    continue;
                };
                if let Some(handshake) = handshake {
                    let _ = connected_tx.send(handshake);
                }
                let (mut sink, mut source) = socket.split();
                loop {
                    tokio::select! {
                        frame = source.next() => match frame {
                            Some(Ok(Message::Text(text))) => {
                                let _ = received_tx.send(text.to_string());
                            }
                            Some(Ok(Message::Ping(data))) => {
                                let _ = sink.send(Message::Pong(data)).await;
                            }
                            Some(Ok(Message::Pong(data))) => {
                                let _ = pong_tx.send(data.to_vec());
                            }
                            Some(Ok(Message::Close(_))) | None | Some(Err(_)) => break,
                            Some(Ok(_)) => {}
                        },
                        message = outgoing_rx.recv() => match message {
                            Some(Message::Close(frame)) => {
                                let _ = sink.send(Message::Close(frame)).await;
                                break;
                            }
                            Some(message) => {
                                if sink.send(message).await.is_err() {
                                    break;
                                }
                            }
                            None => return,
                        },
                    }
                }
            }
        });
        Self {
            url,
            received,
            outgoing,
            connections,
            pongs,
        }
    }

    /// The next text frame the client sent, parsed as JSON when possible.
    pub(crate) async fn next_text(&mut self) -> String {
        tokio::time::timeout(Duration::from_secs(5), self.received.recv())
            .await
            .expect("client frame within 5s")
            .expect("peer running")
    }

    pub(crate) async fn next_json(&mut self) -> Value {
        let text = self.next_text().await;
        serde_json::from_str(&text).unwrap_or_else(|_| panic!("JSON frame, got {text}"))
    }

    /// True when no further client frame arrives within `wait`.
    pub(crate) async fn quiet(&mut self, wait: Duration) -> bool {
        tokio::time::timeout(wait, self.received.recv())
            .await
            .is_err()
    }

    /// Wait until the client has opened `count` connections in total.
    pub(crate) async fn wait_connections(&mut self, count: usize) {
        for _ in 0..count {
            self.next_handshake().await;
        }
    }

    /// The path and headers of the next accepted connection.
    pub(crate) async fn next_handshake(&mut self) -> Handshake {
        tokio::time::timeout(Duration::from_secs(5), self.connections.recv())
            .await
            .expect("connection within 5s")
            .expect("peer running")
    }

    pub(crate) fn push(&self, text: impl Into<String>) {
        let _ = self.outgoing.send(Message::Text(text.into().into()));
    }

    /// Send any frame, such as binary data or a server ping.
    pub(crate) fn push_message(&self, message: Message) {
        let _ = self.outgoing.send(message);
    }

    /// The payload of the next pong the client sent.
    pub(crate) async fn next_pong(&mut self) -> Vec<u8> {
        tokio::time::timeout(Duration::from_secs(5), self.pongs.recv())
            .await
            .expect("client pong within 5s")
            .expect("peer running")
    }

    pub(crate) fn push_json(&self, value: &Value) {
        self.push(value.to_string());
    }

    /// Close the current connection from the server side (to exercise reconnects).
    pub(crate) fn close_connection(&self) {
        let _ = self.outgoing.send(Message::Close(None));
    }
}
