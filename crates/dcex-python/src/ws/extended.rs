use std::sync::Arc;

use dcex::ws::extended::{ExtendedPrivateWebSocket, ExtendedPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "ExtendedPublicWebSocketClient")]
struct PythonExtendedPublicWebSocketClient {
    client: Arc<Mutex<ExtendedPublicWebSocket>>,
}

#[pyclass(name = "ExtendedPrivateWebSocketClient")]
struct PythonExtendedPrivateWebSocketClient {
    client: Arc<Mutex<ExtendedPrivateWebSocket>>,
}

#[pymethods]
impl PythonExtendedPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            ExtendedPublicWebSocket::with_url(base_url, timeout)
        } else {
            ExtendedPublicWebSocket::new(timeout)
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn is_connected(&self) -> PyResult<bool> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Extended WebSocket client is busy; try again later.")
        })?;
        Ok(client.is_connected())
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

    #[pyo3(signature = (market=None, depth=None))]
    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        market: Option<String>,
        depth: Option<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orderbook(market.as_deref(), depth)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (market=None))]
    fn subscribe_trades<'py>(
        &self,
        py: Python<'py>,
        market: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_trades(market.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (market=None))]
    fn subscribe_funding<'py>(
        &self,
        py: Python<'py>,
        market: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_funding(market.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_candles<'py>(
        &self,
        py: Python<'py>,
        market: String,
        candle_type: String,
        interval: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_candles(&market, &candle_type, &interval)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (market=None))]
    fn subscribe_mark_price<'py>(
        &self,
        py: Python<'py>,
        market: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_mark_price(market.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (market=None))]
    fn subscribe_index_price<'py>(
        &self,
        py: Python<'py>,
        market: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_index_price(market.as_deref())
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
impl PythonExtendedPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (api_key, timeout=10.0, base_url=None))]
    fn new(api_key: String, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            ExtendedPrivateWebSocket::with_url(api_key, base_url, timeout)
        } else {
            ExtendedPrivateWebSocket::new(api_key, timeout)
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn is_connected(&self) -> PyResult<bool> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Extended WebSocket client is busy; try again later.")
        })?;
        Ok(client.is_connected())
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
    m.add_class::<PythonExtendedPublicWebSocketClient>()?;
    m.add_class::<PythonExtendedPrivateWebSocketClient>()
}
