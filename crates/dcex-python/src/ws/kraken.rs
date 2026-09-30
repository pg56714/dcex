use std::sync::Arc;

use dcex::ws::kraken::{KrakenFuturesWebSocket, KrakenPrivateWebSocket, KrakenPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "KrakenPublicWebSocketClient")]
struct PythonKrakenPublicWebSocketClient {
    client: Arc<Mutex<KrakenPublicWebSocket>>,
}

#[pyclass(name = "KrakenPrivateWebSocketClient")]
struct PythonKrakenPrivateWebSocketClient {
    client: Arc<Mutex<KrakenPrivateWebSocket>>,
}

#[pymethods]
impl PythonKrakenPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            KrakenPublicWebSocket::with_url(base_url, timeout)
        } else {
            KrakenPublicWebSocket::new(timeout)
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn connect<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .connect()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn close<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .close()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn ping<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .ping()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        product_symbols: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_channel(&channel, product_symbols)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        product_symbols: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe_channel(&channel, product_symbols)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, event_trigger=None, snapshot=true))]
    fn subscribe_ticker<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        event_trigger: Option<String>,
        snapshot: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let event_trigger = event_trigger.as_deref().unwrap_or("trades");
            client
                .lock()
                .await
                .subscribe_ticker_with_options(&product_symbol, event_trigger, snapshot)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, snapshot=false))]
    fn subscribe_trades<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        snapshot: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_trades_with_options(&product_symbol, snapshot)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, depth=10, snapshot=true))]
    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        depth: u32,
        snapshot: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orderbook_with_options(&product_symbol, depth, snapshot)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, interval=1, snapshot=true))]
    fn subscribe_klines<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        interval: u32,
        snapshot: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_klines_with_options(&product_symbol, interval, snapshot)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let body = client
                .lock()
                .await
                .recv_bytes()
                .await
                .map_err(to_py_runtime_error)?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}

#[pymethods]
impl PythonKrakenPrivateWebSocketClient {
    #[pyo3(signature = (product_symbols, depth=10, snapshot=true))]
    fn subscribe_level3<'py>(
        &self,
        py: Python<'py>,
        product_symbols: Vec<String>,
        depth: u32,
        snapshot: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_level3(product_symbols, depth, snapshot)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    #[pyo3(signature = (product_symbols, depth=10))]
    fn unsubscribe_level3<'py>(
        &self,
        py: Python<'py>,
        product_symbols: Vec<String>,
        depth: u32,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe_level3(product_symbols, depth)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    #[new]
    #[pyo3(signature = (
        api_key,
        api_secret,
        timeout=10.0,
        spot_http_base_url=None,
        ws_base_url=None
    ))]
    fn new(
        api_key: String,
        api_secret: String,
        timeout: f64,
        spot_http_base_url: Option<String>,
        ws_base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = match (spot_http_base_url, ws_base_url) {
            (None, None) => KrakenPrivateWebSocket::new(api_key, api_secret, timeout),
            (spot_http_base_url, ws_base_url) => KrakenPrivateWebSocket::with_urls(
                api_key,
                api_secret,
                timeout,
                spot_http_base_url.unwrap_or_else(|| "https://api.kraken.com".to_string()),
                ws_base_url.unwrap_or_else(|| "wss://ws-auth.kraken.com/v2".to_string()),
            ),
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn connect<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .connect()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn fetch_token<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .fetch_token()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn trade_request<'py>(
        &self,
        py: Python<'py>,
        method: String,
        params: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let params: serde_json::Value = serde_json::from_str(&params)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .trade_request(&method, params)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn close<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .close()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn ping<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .ping()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (snapshot=true, rebased=true, users=None))]
    fn subscribe_balances<'py>(
        &self,
        py: Python<'py>,
        snapshot: bool,
        rebased: bool,
        users: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_balances(snapshot, rebased, users)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe_balances<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe_balances()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (
        snap_orders=true,
        snap_trades=false,
        order_status=true,
        rebased=true,
        ratecounter=false,
        users=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn subscribe_executions<'py>(
        &self,
        py: Python<'py>,
        snap_orders: bool,
        snap_trades: bool,
        order_status: bool,
        rebased: bool,
        ratecounter: bool,
        users: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_executions(
                    snap_orders,
                    snap_trades,
                    order_status,
                    rebased,
                    ratecounter,
                    users,
                )
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe_executions<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe_executions()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn token(&self) -> PyResult<Option<String>> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Kraken WebSocket client is busy; try again later.")
        })?;
        Ok(client.token().map(ToString::to_string))
    }

    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let body = client
                .lock()
                .await
                .recv_bytes()
                .await
                .map_err(to_py_runtime_error)?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}

#[pyclass(name = "KrakenFuturesWebSocketClient")]
struct PythonKrakenFuturesWebSocketClient {
    client: Arc<Mutex<KrakenFuturesWebSocket>>,
}

#[pymethods]
impl PythonKrakenFuturesWebSocketClient {
    #[new]
    #[pyo3(signature=(timeout=10.0, base_url=None, api_key=None, api_secret=None))]
    fn new(
        timeout: f64,
        base_url: Option<String>,
        api_key: Option<String>,
        api_secret: Option<String>,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(url) = base_url {
            KrakenFuturesWebSocket::with_url(url, timeout)
        } else {
            KrakenFuturesWebSocket::new(timeout)
        }
        .map_err(to_py_runtime_error)?;
        let client = match (api_key, api_secret) {
            (None, None) => client,
            (Some(key), Some(secret)) => client
                .with_credentials(key, secret)
                .map_err(to_py_runtime_error)?,
            _ => {
                return Err(pyo3::exceptions::PyValueError::new_err(
                    "provide both api_key and api_secret",
                ));
            }
        };
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }
    fn connect<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .connect()
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn close<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .close()
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn ping<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .ping()
                .await
                .map_err(to_py_runtime_error)
        })
    }
    #[pyo3(signature=(feed,product_ids=None))]
    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        feed: String,
        product_ids: Option<Vec<String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&feed, product_ids)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    #[pyo3(signature=(feed,product_ids=None))]
    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        feed: String,
        product_ids: Option<Vec<String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&feed, product_ids)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let body = client
                .lock()
                .await
                .recv()
                .await
                .map_err(to_py_runtime_error)?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonKrakenV1WebSocketClient>()?;
    m.add_class::<PythonKrakenFuturesWebSocketClient>()?;
    m.add_class::<PythonKrakenPublicWebSocketClient>()?;
    m.add_class::<PythonKrakenPrivateWebSocketClient>()
}

#[pyclass(name = "KrakenV1WebSocketClient")]
struct PythonKrakenV1WebSocketClient {
    client: Arc<Mutex<dcex::ws::kraken::KrakenV1WebSocket>>,
}
#[pymethods]
impl PythonKrakenV1WebSocketClient {
    #[new]
    #[pyo3(signature = (token=None, timeout=10.0, base_url=None))]
    fn new(token: Option<String>, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let client =
            dcex::ws::kraken::KrakenV1WebSocket::new(token, base_url, websocket_timeout(timeout)?)
                .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }
    fn is_connected(&self) -> PyResult<bool> {
        Ok(self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Kraken V1 WS is busy."))?
            .is_connected())
    }
    fn url(&self) -> PyResult<String> {
        Ok(self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Kraken V1 WS is busy."))?
            .url()
            .into())
    }
    fn connect<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .connect()
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn close<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .close()
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let bytes = client
                .lock()
                .await
                .recv_bytes()
                .await
                .map_err(to_py_runtime_error)?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &bytes).unbind()))
        })
    }
    #[pyo3(signature = (message, all_symbols=false))]
    fn send_message<'py>(
        &self,
        py: Python<'py>,
        message: String,
        all_symbols: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let message = serde_json::from_str(&message)
            .map_err(|e| PyValueError::new_err(format!("Invalid JSON: {e}")))?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .send_message(message, all_symbols)
                .await
                .map_err(to_py_runtime_error)
        })
    }
}
