use std::sync::Arc;

use dcex::ws::ondo::{OndoPrivateWebSocket, OndoPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "OndoPublicWebSocketClient")]
struct PythonOndoPublicWebSocketClient {
    client: Arc<Mutex<OndoPublicWebSocket>>,
}

#[pymethods]
impl PythonOndoPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = match base_url {
            Some(url) => OndoPublicWebSocket::with_url(url, timeout),
            None => OndoPublicWebSocket::new(timeout),
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn is_connected(&self) -> PyResult<bool> {
        Ok(self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Ondo WebSocket is busy."))?
            .is_connected())
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

    #[pyo3(signature = (channel, markets=None))]
    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        markets: Option<Vec<String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&channel, markets.unwrap_or_default())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (channel, markets=None))]
    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        markets: Option<Vec<String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&channel, markets.unwrap_or_default())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_klines<'py>(
        &self,
        py: Python<'py>,
        market: String,
        resolution: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_klines(market, &resolution)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .recv_bytes()
                .await
                .map_err(to_py_runtime_error)
        })
    }
}

#[pyclass(name = "OndoPrivateWebSocketClient")]
struct PythonOndoPrivateWebSocketClient {
    client: Arc<Mutex<OndoPrivateWebSocket>>,
}

#[pymethods]
impl PythonOndoPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (api_key_id=None, api_secret=None, timeout=10.0, base_url=None))]
    fn new(
        api_key_id: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = match base_url {
            Some(url) => OndoPrivateWebSocket::with_url(api_key_id, api_secret, url, timeout),
            None => OndoPrivateWebSocket::new(api_key_id, api_secret, timeout),
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn is_connected(&self) -> PyResult<bool> {
        Ok(self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Ondo WebSocket is busy."))?
            .is_connected())
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

    #[pyo3(signature = (channel, markets=None))]
    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        markets: Option<Vec<String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&channel, markets.unwrap_or_default())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .recv_bytes()
                .await
                .map_err(to_py_runtime_error)
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonOndoPublicWebSocketClient>()?;
    m.add_class::<PythonOndoPrivateWebSocketClient>()
}
