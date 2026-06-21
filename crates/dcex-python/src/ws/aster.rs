use std::sync::Arc;

use dcex::ws::aster::{AsterPrivateWebSocket, AsterPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "AsterPublicWebSocketClient")]
struct PythonAsterPublicWebSocketClient {
    client: Arc<Mutex<AsterPublicWebSocket>>,
}

#[pyclass(name = "AsterPrivateWebSocketClient")]
struct PythonAsterPrivateWebSocketClient {
    client: Arc<Mutex<AsterPrivateWebSocket>>,
}

#[pymethods]
impl PythonAsterPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (market="futures", timeout=10.0, base_url=None))]
    fn new(market: &str, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let market = aster_market(market)?;
        let client = if let Some(base_url) = base_url {
            AsterPublicWebSocket::with_url(market, base_url, Duration::from_secs_f64(timeout))
        } else {
            AsterPublicWebSocket::new(market, Duration::from_secs_f64(timeout))
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        let mut client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Aster WebSocket client is busy; try again later.")
        })?;
        client.set_product_table(table.table.clone());
        Ok(())
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

    fn subscribe<'py>(&self, py: Python<'py>, streams: Vec<String>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(streams)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        streams: Vec<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(streams)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn list_subscriptions<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .list_subscriptions()
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

    fn subscribe_agg_trades<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_agg_trades(&product_symbol)
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

    #[pyo3(signature = (product_symbol, fast=false))]
    fn subscribe_mark_price<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        fast: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_mark_price(&product_symbol, fast)
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
impl PythonAsterPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (
        signer_address,
        private_key,
        user_address=None,
        market="futures",
        timeout=10.0,
        spot_http_base_url=None,
        futures_http_base_url=None,
        ws_base_url=None
    ))]
    fn new(
        signer_address: String,
        private_key: String,
        user_address: Option<String>,
        market: &str,
        timeout: f64,
        spot_http_base_url: Option<String>,
        futures_http_base_url: Option<String>,
        ws_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let market = aster_market(market)?;
        let timeout = Duration::from_secs_f64(timeout);
        let client = match (spot_http_base_url, futures_http_base_url, ws_base_url) {
            (None, None, None) => AsterPrivateWebSocket::new(
                user_address,
                signer_address,
                private_key,
                market,
                timeout,
            ),
            (spot_http_base_url, futures_http_base_url, ws_base_url) => {
                AsterPrivateWebSocket::with_urls(
                    user_address,
                    signer_address,
                    private_key,
                    market,
                    timeout,
                    spot_http_base_url.unwrap_or_else(|| "https://sapi.asterdex.com".to_string()),
                    futures_http_base_url
                        .unwrap_or_else(|| "https://fapi.asterdex.com".to_string()),
                    ws_base_url.unwrap_or_else(|| match market {
                        AsterMarket::Futures => "wss://fstream.asterdex.com".to_string(),
                        AsterMarket::Spot => "wss://sstream.asterdex.com".to_string(),
                    }),
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

    fn listen_key(&self) -> PyResult<Option<String>> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Aster WebSocket client is busy; try again later.")
        })?;
        Ok(client.listen_key().map(ToString::to_string))
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
    m.add_class::<PythonAsterPublicWebSocketClient>()?;
    m.add_class::<PythonAsterPrivateWebSocketClient>()
}
