use super::*;

#[pyclass(name = "HyperliquidHttpClient")]
struct PythonHyperliquidHttpClient {
    client: HyperliquidClient,
}

#[pymethods]
impl PythonHyperliquidHttpClient {
    #[new]
    #[pyo3(signature = (
        testnet=false,
        wallet_address=None,
        private_key=None,
        timeout=10.0,
        endpoint=None
    ))]
    fn new(
        testnet: bool,
        wallet_address: Option<String>,
        private_key: Option<String>,
        timeout: f64,
        endpoint: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        let default_endpoint = if testnet {
            "https://api.hyperliquid-testnet.xyz"
        } else {
            "https://api.hyperliquid.xyz"
        };
        Ok(Self {
            client: HyperliquidClient::with_endpoint(
                testnet,
                wallet_address,
                private_key,
                Duration::from_secs_f64(timeout),
                endpoint.unwrap_or_else(|| default_endpoint.to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, path, query_json, action_msgpack=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        py.allow_threads(|| {
            self.client
                .request_raw_blocking(method, path, query_json, action_msgpack, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, query_json, action_msgpack=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, path, query_json, action_msgpack, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (query_json))]
    fn public_request(&self, py: Python<'_>, query_json: Vec<u8>) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        py.allow_threads(|| block_on(async move { client.public_request(query_json).await }))
            .map_err(to_py_runtime_error)
            .and_then(python_validated_response)
    }

    #[pyo3(signature = (query_json))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        query_json: Vec<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(query_json)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonHyperliquidHttpClient>()
}
