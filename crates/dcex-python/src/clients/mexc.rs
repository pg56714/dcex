use super::*;

#[pyclass(name = "MexcHttpClient")]
struct PythonMexcHttpClient {
    client: MexcClient,
}

#[pymethods]
impl PythonMexcHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        timeout=10.0,
        base_url=None,
        contract_base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        base_url: Option<String>,
        contract_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        let base_url = base_url.unwrap_or_else(|| "https://api.mexc.com".to_string());
        Ok(Self {
            client: MexcClient::with_base_urls(
                api_key,
                api_secret,
                Duration::from_secs_f64(timeout),
                base_url.clone(),
                contract_base_url.unwrap_or(base_url),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, api, path, params=None, body=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        api: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let api = mexc_api(api)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                api,
                path,
                params.unwrap_or_default(),
                body,
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, api, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        api: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let api = mexc_api(api)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, api, path, params, body, signed)
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
    m.add_class::<PythonMexcHttpClient>()
}
