use std::sync::Arc;

use dcex::ws::kucoin::{KucoinPrivateWebSocket, KucoinPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "KucoinPublicWebSocketClient")]
struct PythonKucoinPublicWebSocketClient {
    client: Arc<Mutex<KucoinPublicWebSocket>>,
}

#[pyclass(name = "KucoinPrivateWebSocketClient")]
struct PythonKucoinPrivateWebSocketClient {
    client: Arc<Mutex<KucoinPrivateWebSocket>>,
}

#[pymethods]
impl PythonKucoinPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, spot_http_base_url=None, futures_http_base_url=None))]
    fn new(
        timeout: f64,
        spot_http_base_url: Option<String>,
        futures_http_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let timeout = Duration::from_secs_f64(timeout);
        let client = match (spot_http_base_url, futures_http_base_url) {
            (None, None) => KucoinPublicWebSocket::new(timeout),
            (spot_http_base_url, futures_http_base_url) => KucoinPublicWebSocket::with_base_urls(
                timeout,
                spot_http_base_url.unwrap_or_else(|| "https://api.kucoin.com".to_string()),
                futures_http_base_url
                    .unwrap_or_else(|| "https://api-futures.kucoin.com".to_string()),
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

    fn subscribe<'py>(&self, py: Python<'py>, topic: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&topic)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(&self, py: Python<'py>, topic: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&topic)
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

    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orderbook(&product_symbol)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_klines<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        interval: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_klines(&product_symbol, &interval)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let event = client
                .lock()
                .await
                .recv()
                .await
                .map_err(to_py_runtime_error)?;
            let body = serde_json::to_vec(&event)
                .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}

#[pymethods]
impl PythonKucoinPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (
        api_key,
        api_secret,
        passphrase,
        timeout=10.0,
        spot_http_base_url=None,
        futures_http_base_url=None
    ))]
    fn new(
        api_key: String,
        api_secret: String,
        passphrase: String,
        timeout: f64,
        spot_http_base_url: Option<String>,
        futures_http_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let timeout = Duration::from_secs_f64(timeout);
        let client = match (spot_http_base_url, futures_http_base_url) {
            (None, None) => KucoinPrivateWebSocket::new(api_key, api_secret, passphrase, timeout),
            (spot_http_base_url, futures_http_base_url) => KucoinPrivateWebSocket::with_base_urls(
                api_key,
                api_secret,
                passphrase,
                timeout,
                spot_http_base_url.unwrap_or_else(|| "https://api.kucoin.com".to_string()),
                futures_http_base_url
                    .unwrap_or_else(|| "https://api-futures.kucoin.com".to_string()),
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

    fn subscribe<'py>(&self, py: Python<'py>, topic: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&topic)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(&self, py: Python<'py>, topic: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&topic)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_orders<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orders()
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

    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let event = client
                .lock()
                .await
                .recv()
                .await
                .map_err(to_py_runtime_error)?;
            let body = serde_json::to_vec(&event)
                .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonKucoinPublicWebSocketClient>()?;
    m.add_class::<PythonKucoinPrivateWebSocketClient>()
}
