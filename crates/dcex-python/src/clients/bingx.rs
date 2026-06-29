use super::*;

#[pyclass(name = "BingxHttpClient")]
struct PythonBingxHttpClient {
    client: BingxClient,
}

#[pymethods]
impl PythonBingxHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, api_secret=None, timeout=10.0, base_url=None))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = http_timeout(timeout)?;
        Ok(Self {
            client: BingxClient::with_base_url(
                api_key,
                api_secret,
                timeout,
                base_url.unwrap_or_else(|| "https://open-api.bingx.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        signed=true,
        headers=None,
        json_body=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        json_body: Option<Vec<u8>>,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let headers = headers.unwrap_or_default().into_iter().collect();
        let json_body = parse_json_body(json_body)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                path,
                params.unwrap_or_default(),
                signed,
                headers,
                json_body,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        signed=true,
        headers=None,
        json_body=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        json_body: Option<Vec<u8>>,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let headers = headers.unwrap_or_default().into_iter().collect();
        let json_body = parse_json_body(json_body)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(
                method,
                path,
                params.unwrap_or_default(),
                signed,
                headers,
                json_body,
            )
        })
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        signed=true,
        headers=None,
        json_body=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        json_body: Option<Vec<u8>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let params = params.unwrap_or_default();
        let headers = headers.unwrap_or_default().into_iter().collect();
        let json_body = parse_json_body(json_body)?;
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, path, params, signed, headers, json_body)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        signed=true,
        headers=None,
        json_body=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_json_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        json_body: Option<Vec<u8>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let params = params.unwrap_or_default();
        let headers = headers.unwrap_or_default().into_iter().collect();
        let json_body = parse_json_body(json_body)?;
        python_json_http_request_async(py, async move {
            client
                .request_raw(method, path, params, signed, headers, json_body)
                .await
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
    m.add_class::<PythonBingxHttpClient>()
}
