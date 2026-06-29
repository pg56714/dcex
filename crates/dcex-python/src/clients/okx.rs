use super::*;

#[pyclass(name = "OkxHttpClient")]
struct PythonOkxHttpClient {
    client: OkxClient,
}

#[pymethods]
impl PythonOkxHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        passphrase=None,
        flag="0".to_string(),
        timeout=10.0,
        base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        flag: String,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = http_timeout(timeout)?;
        Ok(Self {
            client: OkxClient::with_base_url(
                api_key,
                api_secret,
                passphrase,
                flag,
                timeout,
                base_url.unwrap_or_else(|| "https://openapi.okx.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_json_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let params = params.unwrap_or_default();
        python_json_http_request_async(py, async move {
            client.request_raw(method, path, params, body, signed).await
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
    m.add_class::<PythonOkxHttpClient>()
}
