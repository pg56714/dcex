use super::*;

#[pyclass(name = "AsterHttpClient")]
struct PythonAsterHttpClient {
    client: AsterClient,
}

#[pymethods]
impl PythonAsterHttpClient {
    #[new]
    #[pyo3(signature = (
        user_address=None,
        signer_address=None,
        private_key=None,
        timeout=10.0,
        spot_base_url=None,
        futures_base_url=None
    ))]
    fn new(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: f64,
        spot_base_url: Option<String>,
        futures_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: AsterClient::with_base_urls(
                user_address,
                signer_address,
                private_key,
                Duration::from_secs_f64(timeout),
                spot_base_url.unwrap_or_else(|| "https://sapi.asterdex.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://fapi.asterdex.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let market = aster_market(market)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                market,
                path,
                params.unwrap_or_default(),
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = aster_market(market)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.private_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .private_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonAsterHttpClient>()
}
