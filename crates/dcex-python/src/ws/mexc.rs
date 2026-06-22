use std::sync::Arc;

use dcex::ws::mexc::{MexcPrivateWebSocket, MexcPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "MexcPublicWebSocketClient")]
struct PythonMexcPublicWebSocketClient {
    client: Arc<Mutex<MexcPublicWebSocket>>,
}

#[pyclass(name = "MexcPrivateWebSocketClient")]
struct PythonMexcPrivateWebSocketClient {
    client: Arc<Mutex<MexcPrivateWebSocket>>,
}

#[pymethods]
impl PythonMexcPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            MexcPublicWebSocket::with_url(base_url, Duration::from_secs_f64(timeout))
        } else {
            MexcPublicWebSocket::new(Duration::from_secs_f64(timeout))
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

    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        channels: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(channels)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        channels: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(channels)
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

    #[pyo3(signature = (product_symbol, speed=None))]
    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        speed: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let speed = speed.unwrap_or_else(|| "100ms".to_string());
            client
                .lock()
                .await
                .subscribe_orderbook(&product_symbol, &speed)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol, levels=5))]
    fn subscribe_partial_orderbook<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        levels: u32,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_partial_orderbook(&product_symbol, levels)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_book_ticker<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_book_ticker(&product_symbol)
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

#[pymethods]
impl PythonMexcPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (api_key, api_secret=None, timeout=10.0, spot_http_base_url=None, ws_base_url=None))]
    fn new(
        api_key: String,
        api_secret: Option<String>,
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
        let client = match (api_secret, spot_http_base_url, ws_base_url) {
            (None, None, None) => MexcPrivateWebSocket::new(api_key, timeout),
            (Some(api_secret), None, None) => {
                MexcPrivateWebSocket::with_secret(api_key, api_secret, timeout)
            }
            (api_secret, spot_http_base_url, ws_base_url) => {
                MexcPrivateWebSocket::with_urls_and_secret(
                    api_key,
                    api_secret,
                    timeout,
                    spot_http_base_url.unwrap_or_else(|| "https://api.mexc.com".to_string()),
                    ws_base_url.unwrap_or_else(|| "wss://wbs-api.mexc.com/ws".to_string()),
                )
            }
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

    fn keep_alive<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .keep_alive()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn close_listen_key<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .close_listen_key()
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

    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        channels: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(channels)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        channels: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(channels)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_deals<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_deals()
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

    fn listen_key(&self) -> PyResult<Option<String>> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("MEXC WebSocket client is busy; try again later.")
        })?;
        Ok(client.listen_key().map(ToString::to_string))
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
    m.add_class::<PythonMexcPublicWebSocketClient>()?;
    m.add_class::<PythonMexcPrivateWebSocketClient>()
}
