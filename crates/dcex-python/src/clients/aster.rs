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
        let timeout = http_timeout(timeout)?;
        Ok(Self {
            client: AsterClient::with_base_urls(
                user_address,
                signer_address,
                private_key,
                timeout,
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
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = aster_market(market)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(method, market, path, params.unwrap_or_default(), signed)
        })
    }

    #[pyo3(signature = (method, path, params=None, signed=true))]
    fn request_raw_auto_json(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        python_json_http_request(py, move || {
            client.request_raw_auto_blocking(method, path, params.unwrap_or_default(), signed)
        })
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw_json_async<'py>(
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
        python_json_http_request_async(py, async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
        })
    }

    #[pyo3(signature = (method, path, params=None, signed=true))]
    fn request_raw_auto_json_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let params = params.unwrap_or_default();
        python_json_http_request_async(py, async move {
            client.request_raw_auto(method, path, params, signed).await
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        python_validated_request(py, method_name, params, |method_name, params| async move {
            client.public_request(&method_name, params).await
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
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        python_validated_request_async(py, method_name, params, |method_name, params| async move {
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
    fn private_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        python_validated_request(py, method_name, params, |method_name, params| async move {
            client.private_request(&method_name, params).await
        })
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
    fn private_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<PythonRequestParams>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        python_validated_request_async(py, method_name, params, |method_name, params| async move {
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
    m.add_class::<PythonAsterHttpClient>()
}
