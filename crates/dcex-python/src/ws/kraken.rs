use std::sync::Arc;

use dcex::ws::kraken::{KrakenPrivateWebSocket, KrakenPublicWebSocket};
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
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            KrakenPublicWebSocket::with_url(base_url, Duration::from_secs_f64(timeout))
        } else {
            KrakenPublicWebSocket::new(Duration::from_secs_f64(timeout))
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

    fn subscribe_ticker<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_ticker(&product_symbol)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_trades<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_trades(&product_symbol)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, depth=10))]
    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        depth: u32,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orderbook(&product_symbol, depth)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, interval=1))]
    fn subscribe_klines<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        interval: u32,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_klines(&product_symbol, interval)
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
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let timeout = Duration::from_secs_f64(timeout);
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

    fn subscribe_balances<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_balances()
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

    #[pyo3(signature = (snap_orders=true, snap_trades=false))]
    fn subscribe_executions<'py>(
        &self,
        py: Python<'py>,
        snap_orders: bool,
        snap_trades: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_executions(snap_orders, snap_trades)
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

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonKrakenPublicWebSocketClient>()?;
    m.add_class::<PythonKrakenPrivateWebSocketClient>()
}
