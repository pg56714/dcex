use std::sync::Arc;

use dcex::ws::bingx::{BingxPrivateWebSocket, BingxPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "BingxPublicWebSocketClient")]
struct PythonBingxPublicWebSocketClient {
    client: Arc<Mutex<BingxPublicWebSocket>>,
}

#[pyclass(name = "BingxPrivateWebSocketClient")]
struct PythonBingxPrivateWebSocketClient {
    client: Arc<Mutex<BingxPrivateWebSocket>>,
}

#[pymethods]
impl PythonBingxPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None, market="spot"))]
    fn new(timeout: f64, base_url: Option<String>, market: &str) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let market = market.to_ascii_lowercase();
        if !matches!(market.as_str(), "spot" | "swap") {
            return Err(PyValueError::new_err(
                "BingX public WebSocket market must be 'spot' or 'swap'",
            ));
        }
        let client = if let Some(base_url) = base_url {
            if market == "swap" {
                BingxPublicWebSocket::with_swap_url(base_url, timeout)
            } else {
                BingxPublicWebSocket::with_spot_url(base_url, timeout)
            }
        } else {
            match market.as_str() {
                "spot" => BingxPublicWebSocket::new(timeout),
                "swap" => BingxPublicWebSocket::new_swap(timeout),
                _ => unreachable!("market was validated above"),
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

    fn subscribe<'py>(&self, py: Python<'py>, data_type: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&data_type)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(&self, py: Python<'py>, data_type: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&data_type)
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

    #[pyo3(signature = (product_symbol, depth=5, speed=None))]
    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        depth: u32,
        speed: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let speed = speed.unwrap_or_else(|| "500ms".to_string());
            client
                .lock()
                .await
                .subscribe_orderbook(&product_symbol, depth, &speed)
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
                .recv_bytes()
                .await
                .map_err(to_py_runtime_error)?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}

#[pymethods]
impl PythonBingxPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (
        api_key,
        api_secret,
        timeout=10.0,
        http_base_url=None,
        ws_base_url=None,
        market="spot"
    ))]
    fn new(
        api_key: String,
        api_secret: String,
        timeout: f64,
        http_base_url: Option<String>,
        ws_base_url: Option<String>,
        market: &str,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let market = market.to_ascii_lowercase();
        if !matches!(market.as_str(), "spot" | "swap") {
            return Err(PyValueError::new_err(
                "BingX private WebSocket market must be 'spot' or 'swap'",
            ));
        }
        let client = match (http_base_url, ws_base_url) {
            (None, None) if market == "spot" => {
                BingxPrivateWebSocket::new(api_key, api_secret, timeout)
            }
            (None, None) => BingxPrivateWebSocket::new_swap(api_key, api_secret, timeout),
            (http_base_url, ws_base_url) => {
                let http_base_url =
                    http_base_url.unwrap_or_else(|| "https://open-api.bingx.com".to_string());
                let ws_base_url = ws_base_url.unwrap_or_else(|| {
                    if market == "swap" {
                        "wss://open-api-swap.bingx.com/swap-market".to_string()
                    } else {
                        "wss://open-api-ws.bingx.com/market".to_string()
                    }
                });
                if market == "swap" {
                    BingxPrivateWebSocket::with_swap_urls(
                        api_key,
                        api_secret,
                        timeout,
                        http_base_url,
                        ws_base_url,
                    )
                } else {
                    BingxPrivateWebSocket::with_spot_urls(
                        api_key,
                        api_secret,
                        timeout,
                        http_base_url,
                        ws_base_url,
                    )
                }
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

    fn connect_with_listen_key<'py>(
        &self,
        py: Python<'py>,
        listen_key: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .connect_with_listen_key(listen_key)
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

    fn subscribe<'py>(&self, py: Python<'py>, data_type: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&data_type)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(&self, py: Python<'py>, data_type: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&data_type)
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
            PyRuntimeError::new_err("BingX WebSocket client is busy; try again later.")
        })?;
        Ok(client.listen_key().map(ToString::to_string))
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
    m.add_class::<PythonBingxPublicWebSocketClient>()?;
    m.add_class::<PythonBingxPrivateWebSocketClient>()
}
