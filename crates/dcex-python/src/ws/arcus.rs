use std::sync::Arc;

use dcex::ws::arcus::ArcusWebSocket;
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "ArcusWebSocketClient")]
struct PythonArcusWebSocketClient {
    client: Arc<Mutex<ArcusWebSocket>>,
}

#[pymethods]
impl PythonArcusWebSocketClient {
    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        self.client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("WebSocket client is busy"))?
            .set_product_table(table.table.clone());
        Ok(())
    }

    #[new]
    #[pyo3(signature = (testnet=false, timeout=10.0, base_url=None))]
    fn new(testnet: bool, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        Ok(Self {
            client: Arc::new(Mutex::new(
                if let Some(url) = base_url {
                    ArcusWebSocket::with_url(url, websocket_timeout(timeout)?)
                } else {
                    ArcusWebSocket::new(testnet, websocket_timeout(timeout)?)
                }
                .map_err(to_py_runtime_error)?,
            )),
        })
    }

    fn is_connected(&self) -> PyResult<bool> {
        Ok(self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Arcus WebSocket is busy."))?
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

    fn get_request<'py>(
        &self,
        py: Python<'py>,
        id: u64,
        method: String,
        payload: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let payload: serde_json::Value = serde_json::from_str(&payload)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .get_request(id, &method, payload)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn post_request<'py>(&self, py: Python<'py>, frame: String) -> PyResult<Bound<'py, PyAny>> {
        let frame: serde_json::Value = serde_json::from_str(&frame)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .post_request(frame)
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

    #[pyo3(signature = (channel, id=None))]
    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        id: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&channel, id.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (channel, id=None))]
    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        id: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&channel, id.as_deref())
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

pub(super) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonArcusWebSocketClient>()
}
