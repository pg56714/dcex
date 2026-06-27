use std::sync::Arc;

use dcex::ws::backpack::{BackpackPrivateWebSocket, BackpackPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "BackpackPublicWebSocketClient")]
struct PythonBackpackPublicWebSocketClient {
    client: Arc<Mutex<BackpackPublicWebSocket>>,
}

#[pyclass(name = "BackpackPrivateWebSocketClient")]
struct PythonBackpackPrivateWebSocketClient {
    client: Arc<Mutex<BackpackPrivateWebSocket>>,
}

#[pymethods]
impl PythonBackpackPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            BackpackPublicWebSocket::with_url(base_url, Duration::from_secs_f64(timeout))
        } else {
            BackpackPublicWebSocket::new(Duration::from_secs_f64(timeout))
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        let mut client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Backpack WebSocket client is busy; try again later.")
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

    #[pyo3(signature = (product_symbol, speed=None))]
    fn subscribe_depth<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        speed: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(speed) = speed {
                client
                    .subscribe_depth_with_speed(&product_symbol, &speed)
                    .await
            } else {
                client.subscribe_depth(&product_symbol).await
            }
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
            let mut client = client.lock().await;
            if let Some(speed) = speed {
                client
                    .subscribe_orderbook_with_speed(&product_symbol, &speed)
                    .await
            } else {
                client.subscribe_orderbook(&product_symbol).await
            }
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

    fn subscribe_liquidation<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_liquidation()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_mark_price<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_mark_price(&product_symbol)
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

    fn subscribe_open_interest<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_open_interest(&product_symbol)
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
impl PythonBackpackPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (api_key, api_secret, window=5000, timeout=10.0, base_url=None))]
    fn new(
        api_key: String,
        api_secret: String,
        window: u64,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            BackpackPrivateWebSocket::with_url(
                api_key,
                api_secret,
                window,
                base_url,
                Duration::from_secs_f64(timeout),
            )
        } else {
            BackpackPrivateWebSocket::new(
                api_key,
                api_secret,
                window,
                Duration::from_secs_f64(timeout),
            )
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        let mut client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Backpack WebSocket client is busy; try again later.")
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

    #[pyo3(signature = (product_symbol=None))]
    fn subscribe_orders<'py>(
        &self,
        py: Python<'py>,
        product_symbol: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(product_symbol) = product_symbol {
                client.subscribe_orders_for_symbol(&product_symbol).await
            } else {
                client.subscribe_orders().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol=None))]
    fn subscribe_positions<'py>(
        &self,
        py: Python<'py>,
        product_symbol: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(product_symbol) = product_symbol {
                client.subscribe_positions_for_symbol(&product_symbol).await
            } else {
                client.subscribe_positions().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (product_symbol=None))]
    fn subscribe_rfq<'py>(
        &self,
        py: Python<'py>,
        product_symbol: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(product_symbol) = product_symbol {
                client.subscribe_rfq_for_symbol(&product_symbol).await
            } else {
                client.subscribe_rfq().await
            }
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
    m.add_class::<PythonBackpackPublicWebSocketClient>()?;
    m.add_class::<PythonBackpackPrivateWebSocketClient>()?;
    Ok(())
}
