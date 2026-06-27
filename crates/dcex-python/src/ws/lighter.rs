use std::sync::Arc;

use dcex::ws::lighter::{LighterPrivateWebSocket, LighterPublicWebSocket};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "LighterPublicWebSocketClient")]
struct PythonLighterPublicWebSocketClient {
    client: Arc<Mutex<LighterPublicWebSocket>>,
}

#[pyclass(name = "LighterPrivateWebSocketClient")]
struct PythonLighterPrivateWebSocketClient {
    client: Arc<Mutex<LighterPrivateWebSocket>>,
}

#[pymethods]
impl PythonLighterPublicWebSocketClient {
    #[new]
    #[pyo3(signature = (testnet=false, timeout=10.0, base_url=None))]
    fn new(testnet: bool, timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let client = if let Some(base_url) = base_url {
            LighterPublicWebSocket::with_url(base_url, Duration::from_secs_f64(timeout))
        } else {
            LighterPublicWebSocket::new(testnet, Duration::from_secs_f64(timeout))
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

    fn subscribe<'py>(&self, py: Python<'py>, channel: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe(&channel)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(&self, py: Python<'py>, channel: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&channel)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_orderbook<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_orderbook(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_ticker<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_ticker(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_market_stats<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_market_stats(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_all_market_stats<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_all_market_stats()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_trades<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_trades(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_klines<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
        resolution: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_klines(market_id, &resolution)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_mark_price_klines<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
        resolution: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_mark_price_klines(market_id, &resolution)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_spot_market_stats<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_spot_market_stats(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_all_spot_market_stats<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_all_spot_market_stats()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_height<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_height()
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
impl PythonLighterPrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (
        account_index,
        api_key_index,
        api_private_key,
        testnet=false,
        timeout=10.0,
        ws_base_url=None,
        http_base_url=None
    ))]
    fn new(
        account_index: u64,
        api_key_index: u64,
        api_private_key: String,
        testnet: bool,
        timeout: f64,
        ws_base_url: Option<String>,
        http_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "WebSocket timeout must be a positive finite number.",
            ));
        }
        let timeout = Duration::from_secs_f64(timeout);
        let client = match (ws_base_url, http_base_url) {
            (None, None) => LighterPrivateWebSocket::new(
                account_index,
                api_key_index,
                api_private_key,
                testnet,
                timeout,
            ),
            (ws_base_url, http_base_url) => LighterPrivateWebSocket::with_urls(
                account_index,
                api_key_index,
                api_private_key,
                ws_base_url.unwrap_or_else(|| {
                    if testnet {
                        "wss://testnet.zklighter.elliot.ai/stream".to_string()
                    } else {
                        "wss://mainnet.zklighter.elliot.ai/stream".to_string()
                    }
                }),
                http_base_url.unwrap_or_else(|| {
                    if testnet {
                        "https://testnet.zklighter.elliot.ai".to_string()
                    } else {
                        "https://mainnet.zklighter.elliot.ai".to_string()
                    }
                }),
                timeout,
            ),
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn account_index(&self) -> PyResult<u64> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Lighter WebSocket client is busy; try again later.")
        })?;
        Ok(client.account_index())
    }

    #[pyo3(signature = (deadline=None, api_key_index=None))]
    fn create_auth_token(
        &self,
        deadline: Option<u64>,
        api_key_index: Option<u64>,
    ) -> PyResult<String> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Lighter WebSocket client is busy; try again later.")
        })?;
        match (deadline, api_key_index) {
            (None, None) => client.create_auth_token(),
            (Some(deadline), None) => client.create_auth_token_with_deadline(deadline),
            (None, Some(api_key_index)) => {
                client.create_auth_token_with_api_key_index(api_key_index)
            }
            (Some(deadline), Some(api_key_index)) => {
                client.create_auth_token_with_deadline_and_api_key_index(deadline, api_key_index)
            }
        }
        .map_err(to_py_runtime_error)
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

    #[pyo3(signature = (channel, auth=None))]
    fn subscribe<'py>(
        &self,
        py: Python<'py>,
        channel: String,
        auth: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let mut client = client.lock().await;
            if let Some(auth) = auth {
                client.subscribe_with_auth(&channel, auth).await
            } else {
                client.subscribe(&channel).await
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn unsubscribe<'py>(&self, py: Python<'py>, channel: String) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .unsubscribe(&channel)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_authenticated<'py>(
        &self,
        py: Python<'py>,
        channel: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_authenticated(&channel)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_all<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_all()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_market<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_market(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_user_stats<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_user_stats()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_tx<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_tx()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_all_orders<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_all_orders()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_pool_data<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_pool_data()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_pool_info<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_pool_info()
                .await
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

    fn subscribe_account_orders<'py>(
        &self,
        py: Python<'py>,
        market_id: u64,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_orders(market_id)
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_all_trades<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_all_trades()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_all_positions<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_all_positions()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_all_assets<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_all_assets()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_account_spot_avg_entry_prices<'py>(
        &self,
        py: Python<'py>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_account_spot_avg_entry_prices()
                .await
                .map_err(to_py_runtime_error)
        })
    }

    fn subscribe_rfq<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .lock()
                .await
                .subscribe_rfq()
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
    m.add_class::<PythonLighterPublicWebSocketClient>()?;
    m.add_class::<PythonLighterPrivateWebSocketClient>()?;
    Ok(())
}
