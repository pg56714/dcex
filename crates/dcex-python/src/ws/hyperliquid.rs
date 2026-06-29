use std::sync::Arc;

use dcex::ws::hyperliquid::{HyperliquidPrivateWebSocket, HyperliquidPublicWebSocket};
use serde_json::Value;
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "HyperliquidPublicWebSocketClient")]
struct PythonHyperliquidPublicWebSocketClient {
    client: Arc<Mutex<HyperliquidPublicWebSocket>>,
}

#[pyclass(name = "HyperliquidPrivateWebSocketClient")]
struct PythonHyperliquidPrivateWebSocketClient {
    client: Arc<Mutex<HyperliquidPrivateWebSocket>>,
}

#[pymethods]
impl PythonHyperliquidPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (testnet=false, timeout=10.0, base_url=None))]
    fn new(testnet: bool, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            HyperliquidPublicWebSocket::with_url(base_url, timeout)
        } else {
            HyperliquidPublicWebSocket::new(testnet, timeout)
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

    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        subscription_json: Vec<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let subscription = parse_subscription(subscription_json)?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(subscription)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        subscription_json: Vec<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let subscription = parse_subscription(subscription_json)?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(subscription)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (dex=None))]
    fn subscribe_all_mids<'py>(
        &self,
        py: Python<'py>,
        dex: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(dex) = dex {
                client.subscribe_all_mids_for_dex(&dex).await
            } else {
                client.subscribe_all_mids().await
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

    #[pyo3(signature = (product_symbol, n_sig_figs=None, mantissa=None))]
    fn subscribe_l2_book<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
        n_sig_figs: Option<u64>,
        mantissa: Option<u64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            match (n_sig_figs, mantissa) {
                (None, None) => client.subscribe_l2_book(&product_symbol).await,
                (Some(n_sig_figs), None) => {
                    client
                        .subscribe_l2_book_with_n_sig_figs(&product_symbol, n_sig_figs)
                        .await
                }
                (None, Some(mantissa)) => {
                    client
                        .subscribe_l2_book_with_mantissa(&product_symbol, mantissa)
                        .await
                }
                (Some(n_sig_figs), Some(mantissa)) => {
                    client
                        .subscribe_l2_book_with_precision(&product_symbol, n_sig_figs, mantissa)
                        .await
                }
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_bbo<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_bbo(&product_symbol)
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

    fn subscribe_active_asset_ctx<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_active_asset_ctx(&product_symbol)
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
impl PythonHyperliquidPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (user, testnet=false, timeout=10.0, base_url=None))]
    fn new(user: String, testnet: bool, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            HyperliquidPrivateWebSocket::with_url(user, base_url, timeout)
        } else {
            HyperliquidPrivateWebSocket::new(user, testnet, timeout)
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn user(&self) -> PyResult<String> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Hyperliquid WebSocket client is busy; try again later.")
        })?;
        Ok(client.user().to_string())
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

    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        subscription_json: Vec<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let subscription = parse_subscription(subscription_json)?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(subscription)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(
        &self,
        py: Python<'py>,
        subscription_json: Vec<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let subscription = parse_subscription(subscription_json)?;
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(subscription)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (subscription_type, dex=None))]
    fn subscribe_user_subscription<'py>(
        &self,
        py: Python<'py>,
        subscription_type: String,
        dex: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(dex) = dex {
                client
                    .subscribe_user_subscription_for_dex(&subscription_type, &dex)
                    .await
            } else {
                client.subscribe_user_subscription(&subscription_type).await
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (subscription_type, dex=None))]
    fn unsubscribe_user_subscription<'py>(
        &self,
        py: Python<'py>,
        subscription_type: String,
        dex: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(dex) = dex {
                client
                    .unsubscribe_user_subscription_for_dex(&subscription_type, &dex)
                    .await
            } else {
                client
                    .unsubscribe_user_subscription(&subscription_type)
                    .await
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_notifications<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_notifications()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_web_data3<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_web_data3()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (dex=None))]
    fn subscribe_clearinghouse_state<'py>(
        &self,
        py: Python<'py>,
        dex: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(dex) = dex {
                client.subscribe_clearinghouse_state_for_dex(&dex).await
            } else {
                client.subscribe_clearinghouse_state().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (dex=None))]
    fn subscribe_open_orders<'py>(
        &self,
        py: Python<'py>,
        dex: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(dex) = dex {
                client.subscribe_open_orders_for_dex(&dex).await
            } else {
                client.subscribe_open_orders().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_order_updates<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_order_updates()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_user_events<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_user_events()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (aggregate_by_time=None))]
    fn subscribe_user_fills<'py>(
        &self,
        py: Python<'py>,
        aggregate_by_time: Option<bool>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(aggregate_by_time) = aggregate_by_time {
                client
                    .subscribe_user_fills_with_aggregate_by_time(aggregate_by_time)
                    .await
            } else {
                client.subscribe_user_fills().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_user_fundings<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_user_fundings()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_user_non_funding_ledger_updates<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_user_non_funding_ledger_updates()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (dex=None))]
    fn subscribe_twap_states<'py>(
        &self,
        py: Python<'py>,
        dex: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(dex) = dex {
                client.subscribe_twap_states_for_dex(&dex).await
            } else {
                client.subscribe_twap_states().await
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_user_twap_slice_fills<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_user_twap_slice_fills()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_user_twap_history<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_user_twap_history()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_active_asset_data<'py>(
        &self,
        py: Python<'py>,
        product_symbol: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_active_asset_data(&product_symbol)
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

fn parse_subscription(subscription_json: Vec<u8>) -> PyResult<Value> {
    serde_json::from_slice(&subscription_json)
        .map_err(|error| PyValueError::new_err(error.to_string()))
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonHyperliquidPublicWebSocketClient>()?;
    m.add_class::<PythonHyperliquidPrivateWebSocketClient>()?;
    Ok(())
}
