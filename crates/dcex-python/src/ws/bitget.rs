use std::sync::Arc;

use dcex::ws::bitget::{BitgetPrivateWebSocket, BitgetPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "BitgetPublicWebSocketClient")]
struct PythonBitgetPublicWebSocketClient {
    client: Arc<Mutex<BitgetPublicWebSocket>>,
}

#[pyclass(name = "BitgetPrivateWebSocketClient")]
struct PythonBitgetPrivateWebSocketClient {
    client: Arc<Mutex<BitgetPrivateWebSocket>>,
}

#[pymethods]
impl PythonBitgetPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (inst_type, timeout=10.0, base_url=None))]
    fn new(inst_type: String, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            BitgetPublicWebSocket::with_url(inst_type, base_url, Duration::from_secs_f64(timeout))
        } else {
            BitgetPublicWebSocket::new(inst_type, Duration::from_secs_f64(timeout))
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        let mut client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Bitget WebSocket client is busy; try again later.")
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
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_channel(&channel, &product_symbol)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe_channel(&channel, &product_symbol)
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

    #[pyo3(signature = (product_symbol, depth=5))]
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
impl PythonBitgetPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (api_key, api_secret, passphrase, timeout=10.0, base_url=None))]
    fn new(
        api_key: String,
        api_secret: String,
        passphrase: String,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            BitgetPrivateWebSocket::with_url(
                api_key,
                api_secret,
                passphrase,
                base_url,
                Duration::from_secs_f64(timeout),
            )
        } else {
            BitgetPrivateWebSocket::new(
                api_key,
                api_secret,
                passphrase,
                Duration::from_secs_f64(timeout),
            )
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

    fn login<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .login()
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

    #[pyo3(signature = (inst_type, channel, inst_id=None, coin=None))]
    fn subscribe_channel<'py>(
        &self,
        py: Python<'py>,
        inst_type: String,
        channel: String,
        inst_id: Option<String>,
        coin: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_channel(&inst_type, &channel, inst_id.as_deref(), coin.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type, channel, inst_id=None, coin=None))]
    fn unsubscribe_channel<'py>(
        &self,
        py: Python<'py>,
        inst_type: String,
        channel: String,
        inst_id: Option<String>,
        coin: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe_channel(&inst_type, &channel, inst_id.as_deref(), coin.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type=None, inst_id=None))]
    fn subscribe_orders<'py>(
        &self,
        py: Python<'py>,
        inst_type: Option<String>,
        inst_id: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let inst_type = default_private_inst_type(inst_type);
            client
                .lock()
                .await
                .subscribe_orders(&inst_type, inst_id.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type=None, inst_id=None))]
    fn subscribe_fills<'py>(
        &self,
        py: Python<'py>,
        inst_type: Option<String>,
        inst_id: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let inst_type = default_private_inst_type(inst_type);
            client
                .lock()
                .await
                .subscribe_fills(&inst_type, inst_id.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type=None, inst_id=None))]
    fn subscribe_positions<'py>(
        &self,
        py: Python<'py>,
        inst_type: Option<String>,
        inst_id: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let inst_type = default_private_inst_type(inst_type);
            client
                .lock()
                .await
                .subscribe_positions(&inst_type, inst_id.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type=None, coin=None))]
    fn subscribe_account<'py>(
        &self,
        py: Python<'py>,
        inst_type: Option<String>,
        coin: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let inst_type = default_private_inst_type(inst_type);
            client
                .lock()
                .await
                .subscribe_account(&inst_type, coin.as_deref())
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type=None))]
    fn subscribe_equity<'py>(
        &self,
        py: Python<'py>,
        inst_type: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let inst_type = default_private_inst_type(inst_type);
            client
                .lock()
                .await
                .subscribe_equity(&inst_type)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn is_logged_in(&self) -> PyResult<bool> {
        let client = self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Bitget WebSocket client is busy."))?;
        Ok(client.is_logged_in())
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
    m.add_class::<PythonBitgetPublicWebSocketClient>()?;
    m.add_class::<PythonBitgetPrivateWebSocketClient>()
}

fn default_private_inst_type(inst_type: Option<String>) -> String {
    inst_type.unwrap_or_else(|| "USDT-FUTURES".to_string())
}
