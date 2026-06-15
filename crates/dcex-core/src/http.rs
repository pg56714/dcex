use std::collections::BTreeMap;
use std::future::Future;
use std::sync::{mpsc, Arc, OnceLock};
use std::time::Duration;

use reqwest::header::{HeaderName, HeaderValue};
use reqwest::{Client, Method, Url};
use serde_json::Value;
use tokio::runtime::{Builder, Runtime};

use crate::{DcexError, Result};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HttpMethod {
    Delete,
    Get,
    Patch,
    Post,
    Put,
}

impl HttpMethod {
    fn as_reqwest(self) -> Method {
        match self {
            Self::Delete => Method::DELETE,
            Self::Get => Method::GET,
            Self::Patch => Method::PATCH,
            Self::Post => Method::POST,
            Self::Put => Method::PUT,
        }
    }
}

#[derive(Clone, Debug, Default, PartialEq)]
pub enum RequestBody {
    #[default]
    Empty,
    Form(Vec<(String, String)>),
    Json(Value),
    Raw(Vec<u8>),
}

#[derive(Clone, Debug, PartialEq)]
pub struct HttpRequest {
    pub method: HttpMethod,
    pub base_url: String,
    pub path: String,
    pub query: Vec<(String, String)>,
    pub headers: BTreeMap<String, String>,
    pub body: RequestBody,
}

impl HttpRequest {
    pub fn new(method: HttpMethod, base_url: impl Into<String>, path: impl Into<String>) -> Self {
        Self {
            method,
            base_url: base_url.into(),
            path: path.into(),
            query: Vec::new(),
            headers: BTreeMap::new(),
            body: RequestBody::Empty,
        }
    }

    pub fn query(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.query.push((key.into(), value.into()));
        self
    }

    pub fn header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.insert(key.into(), value.into());
        self
    }

    pub fn form(mut self, values: Vec<(String, String)>) -> Self {
        self.body = RequestBody::Form(values);
        self
    }

    pub fn json(mut self, value: Value) -> Self {
        self.body = RequestBody::Json(value);
        self
    }

    pub fn raw(mut self, value: impl Into<Vec<u8>>) -> Self {
        self.body = RequestBody::Raw(value.into());
        self
    }

    pub fn url(&self) -> Result<Url> {
        let base = self.base_url.trim_end_matches('/');
        let path = self.path.trim_start_matches('/');
        Url::parse(&format!("{base}/{path}"))
            .map_err(|error| DcexError::InvalidInput(format!("invalid request URL: {error}")))
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HttpResponse {
    pub status: u16,
    pub headers: BTreeMap<String, String>,
    pub body: Vec<u8>,
}

impl HttpResponse {
    pub fn text(&self) -> Result<String> {
        String::from_utf8(self.body.clone()).map_err(|error| DcexError::Decode(error.to_string()))
    }

    pub fn json(&self) -> Result<Value> {
        serde_json::from_slice(&self.body).map_err(|error| DcexError::Decode(error.to_string()))
    }

    pub fn ensure_success(&self) -> Result<()> {
        if (200..300).contains(&self.status) {
            return Ok(());
        }
        Err(DcexError::HttpStatus {
            status: self.status,
            message: String::from_utf8_lossy(&self.body).into_owned(),
            headers: self
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        })
    }
}

#[derive(Clone)]
pub struct AsyncHttpClient {
    client: Client,
}

impl AsyncHttpClient {
    pub fn new(timeout: Duration) -> Result<Self> {
        let client = Client::builder()
            .timeout(timeout)
            .build()
            .map_err(|error| DcexError::Transport(error.to_string()))?;
        Ok(Self { client })
    }

    pub async fn execute(&self, request: HttpRequest) -> Result<HttpResponse> {
        let mut builder = self
            .client
            .request(request.method.as_reqwest(), request.url()?);
        if !request.query.is_empty() {
            builder = builder.query(&request.query);
        }
        for (key, value) in request.headers {
            let name = HeaderName::from_bytes(key.as_bytes()).map_err(|error| {
                DcexError::InvalidInput(format!("invalid header name {key:?}: {error}"))
            })?;
            let value = HeaderValue::from_str(&value).map_err(|error| {
                DcexError::InvalidInput(format!("invalid header value for {key:?}: {error}"))
            })?;
            builder = builder.header(name, value);
        }
        builder = match request.body {
            RequestBody::Empty => builder,
            RequestBody::Form(values) => builder.form(&values),
            RequestBody::Json(value) => builder.json(&value),
            RequestBody::Raw(value) => builder.body(value),
        };

        let response = builder
            .send()
            .await
            .map_err(|error| DcexError::Transport(error.to_string()))?;
        let status = response.status().as_u16();
        let headers = response
            .headers()
            .iter()
            .map(|(key, value)| {
                (
                    key.as_str().to_string(),
                    value.to_str().unwrap_or_default().to_string(),
                )
            })
            .collect();
        let body = response
            .bytes()
            .await
            .map_err(|error| DcexError::Transport(error.to_string()))?
            .to_vec();
        Ok(HttpResponse {
            status,
            headers,
            body,
        })
    }
}

#[derive(Clone)]
pub struct BlockingHttpClient {
    inner: AsyncHttpClient,
}

impl BlockingHttpClient {
    pub fn new(timeout: Duration) -> Result<Self> {
        Ok(Self {
            inner: AsyncHttpClient::new(timeout)?,
        })
    }

    pub fn execute(&self, request: HttpRequest) -> Result<HttpResponse> {
        let client = self.inner.clone();
        block_on(async move { client.execute(request).await })
    }
}

pub fn block_on<F, T>(future: F) -> Result<T>
where
    F: Future<Output = Result<T>> + Send + 'static,
    T: Send + 'static,
{
    let (sender, receiver) = mpsc::sync_channel(1);
    shared_runtime().spawn(async move {
        let _ = sender.send(future.await);
    });
    receiver
        .recv()
        .map_err(|error| DcexError::Runtime(error.to_string()))?
}

fn shared_runtime() -> &'static Runtime {
    static RUNTIME: OnceLock<Runtime> = OnceLock::new();
    RUNTIME.get_or_init(|| {
        Builder::new_multi_thread()
            .enable_all()
            .thread_name("dcex-runtime")
            .build()
            .expect("failed to initialize dcex Tokio runtime")
    })
}

pub type SharedAsyncHttpClient = Arc<AsyncHttpClient>;

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::thread;

    fn server() -> (String, thread::JoinHandle<String>) {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let address = listener.local_addr().expect("address");
        let handle = thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("accept");
            let mut buffer = [0u8; 4096];
            let size = stream.read(&mut buffer).expect("read");
            let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
            stream
                .write_all(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
X-Test: yes\r\nContent-Length: 11\r\nConnection: close\r\n\r\n{\"ok\":true}",
                )
                .expect("write");
            request
        });
        (format!("http://{address}"), handle)
    }

    #[tokio::test]
    async fn async_client_sends_query_and_headers() {
        let (base_url, handle) = server();
        let client = AsyncHttpClient::new(Duration::from_secs(2)).expect("client");
        let response = client
            .execute(
                HttpRequest::new(HttpMethod::Get, base_url, "/test")
                    .query("symbol", "BTCUSDT")
                    .header("X-API-Key", "key"),
            )
            .await
            .expect("response");

        assert_eq!(response.status, 200);
        assert_eq!(response.json().expect("json")["ok"], true);
        let raw_request = handle.join().expect("server");
        assert!(raw_request.starts_with("GET /test?symbol=BTCUSDT HTTP/1.1"));
        assert!(raw_request.to_ascii_lowercase().contains("x-api-key: key"));
    }

    #[test]
    fn blocking_client_uses_shared_async_transport() {
        let (base_url, handle) = server();
        let client = BlockingHttpClient::new(Duration::from_secs(2)).expect("client");
        let response = client
            .execute(HttpRequest::new(HttpMethod::Get, base_url, "/health"))
            .expect("response");

        assert_eq!(response.status, 200);
        assert_eq!(
            response.headers.get("x-test").map(String::as_str),
            Some("yes")
        );
        assert!(handle
            .join()
            .expect("server")
            .starts_with("GET /health HTTP/1.1"));
    }
}
