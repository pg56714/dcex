use std::sync::Arc;

use dcex::ws::okx::OkxPrivateWebSocket;
use dcex::ws::okx::OkxPublicWebSocket;
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "OkxPublicWebSocketClient")]
struct PythonOkxPublicWebSocketClient {
    client: Arc<Mutex<OkxPublicWebSocket>>,
}

#[pyclass(name = "OkxPrivateWebSocketClient")]
struct PythonOkxPrivateWebSocketClient {
    client: Arc<Mutex<OkxPrivateWebSocket>>,
}

#[pymethods]
impl PythonOkxPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            OkxPublicWebSocket::with_url(base_url, timeout)
        } else {
            OkxPublicWebSocket::new(timeout)
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        let mut client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("OKX WebSocket client is busy; try again later.")
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

    #[pyo3(signature = (channel, product_symbol=None))]
    fn subscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        product_symbol: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(product_symbol) = product_symbol {
                client
                    .subscribe_channel_for_symbol(&channel, &product_symbol)
                    .await
            } else {
                client.subscribe_channel(&channel).await
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (channel, product_symbol=None))]
    fn unsubscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        product_symbol: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(product_symbol) = product_symbol {
                client
                    .unsubscribe_channel_for_symbol(&channel, &product_symbol)
                    .await
            } else {
                client.unsubscribe_channel(&channel).await
            }
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

    fn subscribe_orderbook5<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orderbook5(&product_symbol)
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
impl PythonOkxPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (api_key, api_secret, passphrase, timeout=10.0, base_url=None))]
    fn new(
        api_key: String,
        api_secret: String,
        passphrase: String,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            OkxPrivateWebSocket::with_url(api_key, api_secret, passphrase, base_url, timeout)
        } else {
            OkxPrivateWebSocket::new(api_key, api_secret, passphrase, timeout)
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

    #[pyo3(signature = (channel, inst_type=None, inst_id=None, ccy=None))]
    fn subscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        inst_type: Option<String>,
        inst_id: Option<String>,
        ccy: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let arg = okx_private_arg(channel, inst_type, inst_id, ccy)?;
            client
                .lock()
                .await
                .subscribe(vec![arg])
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (channel, inst_type=None, inst_id=None, ccy=None))]
    fn unsubscribe_channel<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        inst_type: Option<String>,
        inst_id: Option<String>,
        ccy: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let arg = okx_private_arg(channel, inst_type, inst_id, ccy)?;
            client
                .lock()
                .await
                .unsubscribe(vec![arg])
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
            let mut client = client.lock().await;
            match (inst_type, inst_id) {
                (None, None) => client.subscribe_orders().await,
                (Some(inst_type), None) => client.subscribe_orders_for_type(&inst_type).await,
                (Some(inst_type), Some(inst_id)) => {
                    client
                        .subscribe_orders_for_instrument(&inst_type, &inst_id)
                        .await
                }
                (None, Some(inst_id)) => {
                    client
                        .subscribe(vec![
                            dcex::ws::okx::OkxPrivateWebSocketArg::with_inst_type_and_id(
                                "orders", "ANY", inst_id,
                            )
                            .map_err(to_py_runtime_error)?,
                        ])
                        .await
                }
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (ccy=None))]
    fn subscribe_account<'py>(
        &self,
        py: Python<'py>,
        ccy: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(ccy) = ccy {
                client.subscribe_account_for_ccy(&ccy).await
            } else {
                client.subscribe_account().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (inst_type=None))]
    fn subscribe_positions<'py>(
        &self,
        py: Python<'py>,
        inst_type: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(inst_type) = inst_type {
                client.subscribe_positions_for_type(&inst_type).await
            } else {
                client.subscribe_positions().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn is_logged_in(&self) -> PyResult<bool> {
        let client = self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("OKX WebSocket client is busy."))?;
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
    m.add_class::<PythonOkxPublicWebSocketClient>()?;
    m.add_class::<PythonOkxPrivateWebSocketClient>()
}

fn okx_private_arg(
    channel: String,
    inst_type: Option<String>,
    inst_id: Option<String>,
    ccy: Option<String>,
) -> PyResult<dcex::ws::okx::OkxPrivateWebSocketArg> {
    use dcex::ws::okx::OkxPrivateWebSocketArg;

    match (inst_type, inst_id, ccy) {
        (None, None, None) => OkxPrivateWebSocketArg::new(channel),
        (Some(inst_type), None, None) => OkxPrivateWebSocketArg::with_inst_type(channel, inst_type),
        (None, Some(inst_id), None) => OkxPrivateWebSocketArg::with_inst_id(channel, inst_id),
        (Some(inst_type), Some(inst_id), None) => {
            OkxPrivateWebSocketArg::with_inst_type_and_id(channel, inst_type, inst_id)
        }
        (None, None, Some(ccy)) => OkxPrivateWebSocketArg::with_ccy(channel, ccy),
        (Some(inst_type), None, Some(ccy)) => {
            OkxPrivateWebSocketArg::with_inst_type_and_ccy(channel, inst_type, ccy)
        }
        (None, Some(inst_id), Some(ccy)) => {
            OkxPrivateWebSocketArg::with_inst_id_and_ccy(channel, inst_id, ccy)
        }
        (Some(inst_type), Some(inst_id), Some(ccy)) => {
            OkxPrivateWebSocketArg::with_inst_type_and_id_and_ccy(channel, inst_type, inst_id, ccy)
        }
    }
    .map_err(to_py_runtime_error)
}
