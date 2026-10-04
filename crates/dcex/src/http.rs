use std::collections::BTreeMap;
use std::future::Future;
use std::sync::{Arc, OnceLock, mpsc};
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
        if self.path.is_empty() {
            return Url::parse(base)
                .map_err(|error| DcexError::InvalidInput(format!("invalid request URL: {error}")));
        }
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

    pub fn header_pairs(&self) -> Vec<(String, String)> {
        self.headers
            .iter()
            .map(|(key, value)| (key.clone(), value.clone()))
            .collect()
    }

    /// An exchange error in the one shared format (see [`api_error_message`]).
    pub fn api_error(&self, exchange: &str, code: Option<&str>, message: &str) -> DcexError {
        DcexError::HttpStatus {
            status: self.status,
            message: api_error_message(exchange, self.status, code, message),
            headers: self.header_pairs(),
        }
    }

    /// A non-2xx status becomes an exchange error with the body's code and message.
    pub fn ensure_success(&self, exchange: &str) -> Result<()> {
        if (200..300).contains(&self.status) {
            return Ok(());
        }
        let (code, message) = error_parts(&self.body);
        Err(self.api_error(exchange, code.as_deref(), &message))
    }
}

/// The one error text for every exchange: `{Exchange} API Error: [{code}] {message} (HTTP {status})`.
/// Without an exchange code the HTTP status stands in, so the code is never "Unknown".
pub fn api_error_message(exchange: &str, status: u16, code: Option<&str>, message: &str) -> String {
    let code = code
        .map(str::trim)
        .filter(|code| !code.is_empty() && *code != "null")
        .map_or_else(|| format!("HTTP {status}"), ToString::to_string);
    let message = message.trim();
    let message = if message.is_empty() {
        "no error message"
    } else {
        message
    };
    format!("{exchange} API Error: [{code}] {message} (HTTP {status})")
}

const CODE_KEYS: &[&str] = &["retCode", "code", "error_code", "errorCode", "ret_code"];
const MESSAGE_KEYS: &[&str] = &[
    "retMsg",
    "msg",
    "message",
    "error",
    "errorMessage",
    "error_description",
    "detail",
];

/// The code and message of an error body: a nested `error` object is read first, then
/// the top level; a non-JSON body is the message itself.
pub fn error_parts(body: &[u8]) -> (Option<String>, String) {
    let text = String::from_utf8_lossy(body).trim().to_string();
    let Ok(Value::Object(object)) = serde_json::from_slice::<Value>(body) else {
        return (None, text);
    };
    let nested = object.get("error").and_then(Value::as_object);
    let scopes = nested.into_iter().chain(std::iter::once(&object));
    let (mut code, mut message) = (None, None);
    for scope in scopes {
        code = code.or_else(|| CODE_KEYS.iter().find_map(|key| scalar(scope.get(*key)?)));
        message = message.or_else(|| MESSAGE_KEYS.iter().find_map(|key| scalar(scope.get(*key)?)));
    }
    (code, message.unwrap_or(text))
}

fn scalar(value: &Value) -> Option<String> {
    match value {
        Value::String(text) if !text.trim().is_empty() => Some(text.clone()),
        Value::Number(number) => Some(number.to_string()),
        Value::Array(items) if !items.is_empty() => Some(
            items
                .iter()
                .filter_map(scalar)
                .collect::<Vec<_>>()
                .join(", "),
        ),
        _ => None,
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
        let client = AsyncHttpClient::new(Duration::from_secs(10)).expect("client");
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
        let client = BlockingHttpClient::new(Duration::from_secs(10)).expect("client");
        let response = client
            .execute(HttpRequest::new(HttpMethod::Get, base_url, "/health"))
            .expect("response");

        assert_eq!(response.status, 200);
        assert_eq!(
            response.headers.get("x-test").map(String::as_str),
            Some("yes")
        );
        assert!(
            handle
                .join()
                .expect("server")
                .starts_with("GET /health HTTP/1.1")
        );
    }

    #[test]
    fn exchange_errors_share_one_format() {
        let cases: [(&[u8], &str); 6] = [
            (
                br#"{"status":"ERROR","error":{"code":1137,"message":"Position is missing for reduce-only order"}}"#,
                "Extended API Error: [1137] Position is missing for reduce-only order (HTTP 400)",
            ),
            (
                br#"{"success":false,"error":"reduce only order can only be IOC","error_code":"reduce_only_invalid_tif"}"#,
                "Extended API Error: [reduce_only_invalid_tif] reduce only order can only be IOC (HTTP 400)",
            ),
            (
                br#"{"code":"INVALID_ORDER","message":"Fill or kill order would not complete fill immediately"}"#,
                "Extended API Error: [INVALID_ORDER] Fill or kill order would not complete fill immediately (HTTP 400)",
            ),
            (
                br#"{"code":-5021,"msg":"FOK order rejected"}"#,
                "Extended API Error: [-5021] FOK order rejected (HTTP 400)",
            ),
            (
                b"Bad Gateway",
                "Extended API Error: [HTTP 400] Bad Gateway (HTTP 400)",
            ),
            (b"", "Extended API Error: [HTTP 400] no error message (HTTP 400)"),
        ];
        for (body, expected) in cases {
            let response = HttpResponse {
                status: 400,
                headers: BTreeMap::new(),
                body: body.to_vec(),
            };
            let error = response.ensure_success("Extended").unwrap_err();
            assert_eq!(error.to_string(), expected);
            assert!(matches!(error, DcexError::HttpStatus { status: 400, .. }));
        }
    }

    #[test]
    fn missing_or_null_code_falls_back_to_http_status_never_unknown() {
        for code in [None, Some(""), Some("null")] {
            let text = api_error_message("Bybit", 200, code, "");
            assert_eq!(
                text,
                "Bybit API Error: [HTTP 200] no error message (HTTP 200)"
            );
            assert!(!text.contains("Unknown"));
        }
    }
}
