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
    #[new]
    #[pyo3(signature = (testnet=false, timeout=10.0))]
    fn new(testnet: bool, timeout: f64) -> PyResult<Self> {
        Ok(Self {
            client: Arc::new(Mutex::new(
                ArcusWebSocket::new(testnet, websocket_timeout(timeout)?)
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
