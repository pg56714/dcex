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
        let timeout = http_timeout(timeout)?;
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
                timeout,
                endpoint.unwrap_or_else(|| default_endpoint.to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, path, query_json, action_msgpack=None, signed=true))]
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(method, path, query_json, action_msgpack, signed)
        })
    }

    #[pyo3(signature = (method, path, query_json, action_msgpack=None, signed=true))]
    fn request_raw_json_async<'py>(
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
        python_json_http_request_async(py, async move {
            client
                .request_raw(method, path, query_json, action_msgpack, signed)
                .await
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_json(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        python_validated_json_request(py, method_name, params, |method_name, params| async move {
            client.public_request(&method_name, params).await
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_json_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        python_validated_json_request_async(
            py,
            method_name,
            params,
            |method_name, params| async move { client.public_request(&method_name, params).await },
        )
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request_json(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        python_validated_json_request(py, method_name, params, |method_name, params| async move {
            client.private_request(&method_name, params).await
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request_json_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        python_validated_json_request_async(
            py,
            method_name,
            params,
            |method_name, params| async move { client.private_request(&method_name, params).await },
        )
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonHyperliquidHttpClient>()
}
