use std::sync::Arc;

use dcex::ws::binance::{
    BinanceEquityWebSocket, BinancePrivateWebSocket, BinancePublicWebSocket, BinanceWebSocketApi,
    BinanceWebSocketApiMarket,
};
use tokio::sync::Mutex;

use super::*;

#[pyclass(name = "BinancePublicWebSocketClient")]
struct PythonBinancePublicWebSocketClient {
    client: Arc<Mutex<BinancePublicWebSocket>>,
}

#[pyclass(name = "BinancePrivateWebSocketClient")]
struct PythonBinancePrivateWebSocketClient {
    client: Arc<Mutex<BinancePrivateWebSocket>>,
}

#[pyclass(name = "BinanceEquityWebSocketClient")]
struct PythonBinanceEquityWebSocketClient {
    client: Arc<Mutex<BinanceEquityWebSocket>>,
}

#[pymethods]
impl PythonBinanceEquityWebSocketClient {
    #[new]
    #[pyo3(signature = (
        stream,
        product_symbol=None,
        interval=None,
        listen_key=None,
        timeout=10.0,
        base_url=None
    ))]
    fn new(
        stream: String,
        product_symbol: Option<String>,
        interval: Option<String>,
        listen_key: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(base_url) = base_url {
            BinanceEquityWebSocket::with_base_url(
                &stream,
                product_symbol.as_deref(),
                interval.as_deref(),
                listen_key.as_deref(),
                timeout,
                base_url,
            )
        } else {
            BinanceEquityWebSocket::new(
                &stream,
                product_symbol.as_deref(),
                interval.as_deref(),
                listen_key.as_deref(),
                timeout,
            )
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn url(&self) -> PyResult<String> {
        let client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Binance Equity WebSocket client is busy; try again later.")
        })?;
        Ok(client.url().to_string())
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
impl PythonBinancePublicWebSocketClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None, profile="spot"))]
    fn new(timeout: f64, base_url: Option<String>, profile: &str) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        let client = BinancePublicWebSocket::with_profile_url(profile, base_url, timeout)
            .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(Mutex::new(client)),
        })
    }

    fn url(&self) -> PyResult<String> {
        let client = self
            .client
            .try_lock()
            .map_err(|_| PyRuntimeError::new_err("Binance WebSocket client is busy"))?;
        Ok(client.url().to_string())
    }

    fn set_product_table(&self, table: PyRef<'_, PythonProductTable>) -> PyResult<()> {
        let mut client = self.client.try_lock().map_err(|_| {
            PyRuntimeError::new_err("Binance WebSocket client is busy; try again later.")
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
impl PythonBinancePrivateWebSocketClient {
    #[new]
    #[pyo3(signature = (
        api_key,
        api_secret,
        timeout=10.0,
        spot_http_base_url=None,
        futures_http_base_url=None,
        ws_base_url=None,
        profile="futures",
        coin_futures_http_base_url=None,
        options_http_base_url=None,
        portfolio_margin_http_base_url=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        api_key: String,
        api_secret: String,
        timeout: f64,
        spot_http_base_url: Option<String>,
        futures_http_base_url: Option<String>,
        ws_base_url: Option<String>,
        profile: &str,
        coin_futures_http_base_url: Option<String>,
        options_http_base_url: Option<String>,
        portfolio_margin_http_base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = websocket_timeout(timeout)?;
        if api_key.trim().is_empty() || api_secret.trim().is_empty() {
            return Err(PyValueError::new_err(
                "Binance API key and secret must not be empty.",
            ));
        }
        let mut http_client = dcex::exchanges::binance::BinanceClient::with_all_base_urls(
            Some(api_key),
            Some(api_secret),
            timeout,
            spot_http_base_url.unwrap_or_else(|| "https://api.binance.com".into()),
            futures_http_base_url.unwrap_or_else(|| "https://fapi.binance.com".into()),
            options_http_base_url.unwrap_or_else(|| "https://eapi.binance.com".into()),
        )
        .map_err(to_py_runtime_error)?;
        if let Some(url) = coin_futures_http_base_url {
            http_client = http_client.with_coin_futures_base_url(url);
        }
        if let Some(url) = portfolio_margin_http_base_url {
            http_client = http_client.with_portfolio_margin_base_url(url);
        }
        let client =
            BinancePrivateWebSocket::with_profile(http_client, profile, timeout, ws_base_url)
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
            PyRuntimeError::new_err("Binance WebSocket client is busy; try again later.")
        })?;
        Ok(client.listen_key().map(ToString::to_string))
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
    m.add_class::<PythonBinanceWebSocketApiClient>()?;
    m.add_class::<PythonBinancePublicWebSocketClient>()?;
    m.add_class::<PythonBinancePrivateWebSocketClient>()?;
    m.add_class::<PythonBinanceEquityWebSocketClient>()
}

#[pyclass(name = "BinanceWebSocketApiClient")]
struct PythonBinanceWebSocketApiClient {
    client: Arc<BinanceWebSocketApi>,
}

#[pymethods]
impl PythonBinanceWebSocketApiClient {
    #[new]
    #[pyo3(signature = (market="spot", api_key=None, api_secret=None, ed25519_seed=None, timeout=10.0, base_url=None))]
    fn new(
        market: &str,
        api_key: Option<String>,
        api_secret: Option<String>,
        ed25519_seed: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let market = match market {
            "spot" => BinanceWebSocketApiMarket::Spot,
            "futures" => BinanceWebSocketApiMarket::Futures,
            "coin_futures" => BinanceWebSocketApiMarket::CoinFutures,
            _ => {
                return Err(PyValueError::new_err(
                    "market must be spot, futures or coin_futures",
                ));
            }
        };
        let timeout = websocket_timeout(timeout)?;
        let client = if let Some(url) = base_url {
            BinanceWebSocketApi::with_url(market, api_key, api_secret, ed25519_seed, timeout, url)
        } else {
            BinanceWebSocketApi::new(market, api_key, api_secret, ed25519_seed, timeout)
        }
        .map_err(to_py_runtime_error)?;
        Ok(Self {
            client: Arc::new(client),
        })
    }
    fn connect<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client.connect().await.map_err(to_py_runtime_error)
        })
    }
    fn close<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client.close().await.map_err(to_py_runtime_error)
        })
    }
    fn request<'py>(
        &self,
        py: Python<'py>,
        method: String,
        params_json: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params =
            serde_json::from_str(&params_json).map_err(|e| PyValueError::new_err(e.to_string()))?;
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request(&method, params)
                .await
                .map_err(to_py_runtime_error)
        })
    }
    fn recv<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            let body = client.recv_bytes().await.map_err(to_py_runtime_error)?;
            Python::with_gil(|py| Ok(PyBytes::new(py, &body).unbind()))
        })
    }
}
