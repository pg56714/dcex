use std::collections::BTreeMap;
use std::future::Future;
use std::time::Duration;

use dcex::common::{self, OrderSide};
use dcex::exchange::ValidatedResponse;
use dcex::exchanges::arcus::{ArcusClient, ArcusSpotClient};
use dcex::exchanges::aster::{AsterClient, AsterMarket};
use dcex::exchanges::backpack::{BackpackClient, SignaturePayload};
use dcex::exchanges::binance::BinanceClient;
use dcex::exchanges::bingx::BingxClient;
use dcex::exchanges::bitget::BitgetClient;
use dcex::exchanges::bybit::BybitClient;
use dcex::exchanges::extended::ExtendedClient;
use dcex::exchanges::hyperliquid::HyperliquidClient;
use dcex::exchanges::kraken::{KrakenAuth, KrakenClient};
use dcex::exchanges::lighter::{
    LighterClient, LighterContentType, LighterCredentials, LighterNetwork,
};
use dcex::exchanges::mexc::{MexcApi, MexcClient};
use dcex::exchanges::okx::OkxClient;
use dcex::exchanges::ondo::OndoClient;
use dcex::http::{HttpMethod, HttpResponse, block_on};
use dcex::lighter;
use dcex::product_table::{MarketInfo, ProductFilter, ProductTable};
use pyo3::IntoPyObjectExt;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};
use serde_json::Value;

fn to_py_value_error(error: dcex::DcexError) -> PyErr {
    PyValueError::new_err(error.to_string())
}

fn to_py_runtime_error(error: dcex::DcexError) -> PyErr {
    match error {
        dcex::DcexError::InvalidInput(_) => to_py_value_error(error),
        dcex::DcexError::ExchangeResponse {
            status,
            ref data,
            ref headers,
            ..
        } => {
            let exception = PyRuntimeError::new_err(error.to_string());
            Python::attach(|py| {
                let value = exception.value(py);
                if let Ok(data) = json_value_to_py(py, data) {
                    let _ = value.setattr("response_data", data);
                }
                let _ = value.setattr("status_code", status);
                let _ = value.setattr("resp_headers", headers.clone());
            });
            exception
        }
        dcex::DcexError::HttpStatus {
            status,
            ref headers,
            ..
        } => {
            let exception = PyRuntimeError::new_err(error.to_string());
            Python::attach(|py| {
                let value = exception.value(py);
                let _ = value.setattr("status_code", status);
                let _ = value.setattr("resp_headers", headers.clone());
            });
            exception
        }
        _ => PyRuntimeError::new_err(error.to_string()),
    }
}

fn positive_duration_from_secs(timeout: f64, label: &str) -> PyResult<Duration> {
    if timeout <= 0.0 {
        return Err(PyValueError::new_err(format!(
            "{label} timeout must be a positive finite number."
        )));
    }
    Duration::try_from_secs_f64(timeout).map_err(|_| {
        PyValueError::new_err(format!("{label} timeout must be a positive finite number."))
    })
}

fn http_timeout(timeout: f64) -> PyResult<Duration> {
    positive_duration_from_secs(timeout, "HTTP")
}

fn websocket_timeout(timeout: f64) -> PyResult<Duration> {
    positive_duration_from_secs(timeout, "WebSocket")
}

fn http_method(method: &str) -> PyResult<HttpMethod> {
    match method.to_ascii_uppercase().as_str() {
        "DELETE" => Ok(HttpMethod::Delete),
        "GET" => Ok(HttpMethod::Get),
        "PATCH" => Ok(HttpMethod::Patch),
        "POST" => Ok(HttpMethod::Post),
        "PUT" => Ok(HttpMethod::Put),
        _ => Err(PyValueError::new_err(format!(
            "unsupported HTTP method: {method}"
        ))),
    }
}

type PythonJsonResponse = (u16, BTreeMap<String, String>, Py<PyAny>);

fn python_json_http_response(response: HttpResponse) -> PyResult<PythonJsonResponse> {
    let HttpResponse {
        status,
        headers,
        body,
    } = response;
    let body = if body.is_empty() {
        Python::attach(|py| py.None())
    } else {
        let data: Value = serde_json::from_slice(&body)
            .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
        Python::attach(|py| json_value_to_py(py, &data))?
    };
    Ok((status, headers, body))
}

fn python_validated_json_response(response: ValidatedResponse) -> PyResult<PythonJsonResponse> {
    let body = Python::attach(|py| json_value_to_py(py, &response.data))?;
    Ok((response.status, response.headers, body))
}

fn json_value_to_py(py: Python<'_>, value: &Value) -> PyResult<Py<PyAny>> {
    match value {
        Value::Null => Ok(py.None()),
        Value::Bool(value) => value.into_py_any(py),
        Value::Number(value) => json_number_to_py(py, value),
        Value::String(value) => value.into_py_any(py),
        Value::Array(values) => {
            let list = PyList::empty(py);
            for value in values {
                list.append(json_value_to_py(py, value)?)?;
            }
            Ok(list.into_any().unbind())
        }
        Value::Object(values) => {
            let dict = PyDict::new(py);
            for (key, value) in values {
                dict.set_item(key, json_value_to_py(py, value)?)?;
            }
            Ok(dict.into_any().unbind())
        }
    }
}

fn json_number_to_py(py: Python<'_>, value: &serde_json::Number) -> PyResult<Py<PyAny>> {
    if let Some(value) = value.as_i64() {
        return value.into_py_any(py);
    }
    if let Some(value) = value.as_u64() {
        return value.into_py_any(py);
    }
    if let Some(value) = value.as_f64() {
        return value.into_py_any(py);
    }
    value.to_string().into_py_any(py)
}

pub(crate) use product_table::PythonProductTable;

type PythonRequestParams = Vec<(String, String)>;

fn python_validated_json_request<F, Fut>(
    py: Python<'_>,
    method_name: String,
    params: Option<PythonRequestParams>,
    request: F,
) -> PyResult<PythonJsonResponse>
where
    F: FnOnce(String, PythonRequestParams) -> Fut + Send,
    Fut: Future<Output = dcex::Result<ValidatedResponse>> + Send + 'static,
{
    let params = params.unwrap_or_default();
    py.detach(|| block_on(request(method_name, params)))
        .map_err(to_py_runtime_error)
        .and_then(python_validated_json_response)
}

fn python_json_http_request<F>(py: Python<'_>, request: F) -> PyResult<PythonJsonResponse>
where
    F: FnOnce() -> dcex::Result<HttpResponse> + Send,
{
    py.detach(request)
        .map_err(to_py_runtime_error)
        .and_then(python_json_http_response)
}

/// Async calls run on the runtime the blocking calls already use, so a process that mixes
/// both keeps one worker pool. Bound on first use rather than at import: a runtime built
/// before `fork()` has no worker threads in the child.
fn future_into_py<'py, F, T>(py: Python<'py>, future: F) -> PyResult<Bound<'py, PyAny>>
where
    F: Future<Output = PyResult<T>> + Send + 'static,
    T: for<'a> IntoPyObject<'a> + Send + 'static,
{
    static SHARED_RUNTIME: std::sync::Once = std::sync::Once::new();
    SHARED_RUNTIME.call_once(|| {
        // Err means the bridge already has a runtime; it keeps that one.
        let _ = pyo3_async_runtimes::tokio::init_with_runtime(dcex::http::shared_runtime());
    });
    pyo3_async_runtimes::tokio::future_into_py(py, future)
}

type ReceiveFuture<'a> = std::pin::Pin<Box<dyn Future<Output = dcex::Result<Vec<u8>>> + Send + 'a>>;

/// A WebSocket client shared by the Python-facing calls.
///
/// A receive holds the client while it waits for the next message, which on a quiet
/// stream lasts the whole receive timeout. Every other call announces itself first, so a
/// waiting receive lets go of the client, queues behind that call and then resumes: a
/// ping or subscription is sent at once instead of after the next message.
pub(crate) struct WsCell<T> {
    client: tokio::sync::Mutex<T>,
    /// Calls that want the client and do not hold it yet.
    waiting: std::sync::atomic::AtomicUsize,
    interrupt: tokio::sync::Notify,
    /// The client's receive timeout, enforced here across interruptions.
    timeout: Duration,
}

impl<T> WsCell<T> {
    pub(crate) fn new(client: T, timeout: Duration) -> Self {
        Self {
            client: tokio::sync::Mutex::new(client),
            waiting: std::sync::atomic::AtomicUsize::new(0),
            interrupt: tokio::sync::Notify::new(),
            timeout,
        }
    }

    /// Take the client for any call but a receive, interrupting a waiting receive.
    pub(crate) async fn lock(&self) -> tokio::sync::MutexGuard<'_, T> {
        struct Waiting<'a>(&'a std::sync::atomic::AtomicUsize);
        impl Drop for Waiting<'_> {
            fn drop(&mut self) {
                self.0.fetch_sub(1, std::sync::atomic::Ordering::AcqRel);
            }
        }
        self.waiting
            .fetch_add(1, std::sync::atomic::Ordering::AcqRel);
        // Dropped once the client is held, or if the caller gives up waiting for it.
        let _waiting = Waiting(&self.waiting);
        self.interrupt.notify_one();
        self.client.lock().await
    }

    pub(crate) fn try_lock(
        &self,
    ) -> Result<tokio::sync::MutexGuard<'_, T>, tokio::sync::TryLockError> {
        self.client.try_lock()
    }

    /// Wait for the next message, stepping aside whenever another call needs the client.
    /// `receive` restarts after each interruption, so it must lose nothing when dropped
    /// while waiting; a message that is already there always wins over an interruption.
    pub(crate) async fn receive(
        &self,
        mut receive: impl for<'a> FnMut(&'a mut T) -> ReceiveFuture<'a>,
    ) -> dcex::Result<Vec<u8>> {
        // The client's own timeout restarts with every interruption. This deadline keeps
        // the call to one timeout however often it steps aside, so frequent pings cannot
        // hide a connection that has gone silent.
        let deadline = tokio::time::Instant::now() + self.timeout;
        let mut interrupted = false;
        loop {
            let mut client = self.client.lock().await;
            // A call that announced itself but is not queued on the mutex yet goes first.
            if self.waiting.load(std::sync::atomic::Ordering::Acquire) > 0 {
                drop(client);
                tokio::task::yield_now().await;
                continue;
            }
            tokio::select! {
                biased;
                received = receive(&mut client) => return received,
                () = self.interrupt.notified() => interrupted = true,
                // Until the first interruption the client's own timeout is the same one.
                () = tokio::time::sleep_until(deadline), if interrupted => {
                    return Err(dcex::DcexError::Transport(
                        "WebSocket receive timed out.".to_string(),
                    ));
                }
            }
        }
    }
}

fn python_validated_json_request_async<'py, F, Fut>(
    py: Python<'py>,
    method_name: String,
    params: Option<PythonRequestParams>,
    request: F,
) -> PyResult<Bound<'py, PyAny>>
where
    F: FnOnce(String, PythonRequestParams) -> Fut + Send + 'static,
    Fut: Future<Output = dcex::Result<ValidatedResponse>> + Send + 'static,
{
    let params = params.unwrap_or_default();
    future_into_py(py, async move {
        request(method_name, params)
            .await
            .map_err(to_py_runtime_error)
            .and_then(python_validated_json_response)
    })
}

fn python_json_http_request_async<'py, Fut>(
    py: Python<'py>,
    request: Fut,
) -> PyResult<Bound<'py, PyAny>>
where
    Fut: Future<Output = dcex::Result<HttpResponse>> + Send + 'static,
{
    future_into_py(py, async move {
        request
            .await
            .map_err(to_py_runtime_error)
            .and_then(python_json_http_response)
    })
}

fn parse_json_body(body: Option<Vec<u8>>) -> PyResult<Option<serde_json::Value>> {
    body.map(|body| {
        serde_json::from_slice(&body).map_err(|error| PyValueError::new_err(error.to_string()))
    })
    .transpose()
}

fn mexc_api(api: &str) -> PyResult<MexcApi> {
    match api.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(MexcApi::Contract),
        "spot" => Ok(MexcApi::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported MEXC API: {api}"
        ))),
    }
}

fn kraken_auth(auth: &str) -> PyResult<KrakenAuth> {
    match auth.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(KrakenAuth::Futures),
        "spot" | "wallet" => Ok(KrakenAuth::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Kraken auth type: {auth}"
        ))),
    }
}

fn lighter_content_type(content_type: &str) -> PyResult<LighterContentType> {
    match content_type.to_ascii_lowercase().as_str() {
        "form" => Ok(LighterContentType::Form),
        "json" => Ok(LighterContentType::Json),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Lighter content type: {content_type}"
        ))),
    }
}

fn lighter_network(network: &str) -> PyResult<LighterNetwork> {
    network.parse().map_err(to_py_value_error)
}

fn aster_market(market: &str) -> PyResult<AsterMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(AsterMarket::Futures),
        "spot" | "wallet" => Ok(AsterMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Aster market: {market}"
        ))),
    }
}

mod function_bindings;
mod product_table;

#[path = "clients/arcus.rs"]
mod arcus_client;
#[path = "ws/arcus.rs"]
mod arcus_ws;
#[path = "clients/aster.rs"]
mod aster_client;
#[path = "ws/aster.rs"]
mod aster_ws;
#[path = "clients/backpack.rs"]
mod backpack_client;
#[path = "ws/backpack.rs"]
mod backpack_ws;
#[path = "clients/binance.rs"]
mod binance_client;
#[path = "ws/binance.rs"]
mod binance_ws;
#[path = "clients/bingx.rs"]
mod bingx_client;
#[path = "ws/bingx.rs"]
mod bingx_ws;
#[path = "clients/bitget.rs"]
mod bitget_client;
#[path = "ws/bitget.rs"]
mod bitget_ws;
#[path = "clients/bybit.rs"]
mod bybit_client;
#[path = "ws/bybit.rs"]
mod bybit_ws;
#[path = "clients/extended.rs"]
mod extended_client;
#[path = "ws/extended.rs"]
mod extended_ws;
#[path = "clients/hyperliquid.rs"]
mod hyperliquid_client;
#[path = "ws/hyperliquid.rs"]
mod hyperliquid_ws;
#[path = "clients/kraken.rs"]
mod kraken_client;
#[path = "ws/kraken.rs"]
mod kraken_ws;
#[path = "clients/lighter.rs"]
mod lighter_client;
#[path = "ws/lighter.rs"]
mod lighter_ws;
#[path = "clients/mexc.rs"]
mod mexc_client;
#[path = "ws/mexc.rs"]
mod mexc_ws;
#[path = "clients/okx.rs"]
mod okx_client;
#[path = "ws/okx.rs"]
mod okx_ws;
#[path = "clients/ondo.rs"]
mod ondo_client;
#[path = "ws/ondo.rs"]
mod ondo_ws;

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    arcus_client::register(m)?;
    arcus_ws::register(m)?;
    aster_client::register(m)?;
    aster_ws::register(m)?;
    backpack_client::register(m)?;
    backpack_ws::register(m)?;
    binance_client::register(m)?;
    bingx_client::register(m)?;
    bingx_ws::register(m)?;
    bitget_client::register(m)?;
    bitget_ws::register(m)?;
    bybit_client::register(m)?;
    bybit_ws::register(m)?;
    extended_client::register(m)?;
    extended_ws::register(m)?;
    hyperliquid_client::register(m)?;
    hyperliquid_ws::register(m)?;
    kraken_client::register(m)?;
    kraken_ws::register(m)?;
    lighter_client::register(m)?;
    lighter_ws::register(m)?;
    mexc_client::register(m)?;
    mexc_ws::register(m)?;
    okx_client::register(m)?;
    ondo_client::register(m)?;
    ondo_ws::register(m)?;
    binance_ws::register(m)?;
    okx_ws::register(m)?;
    product_table::register(m)?;
    function_bindings::register(m)?;
    Ok(())
}
