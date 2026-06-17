use super::*;

#[pyclass(name = "LighterHttpClient")]
struct PythonLighterHttpClient {
    client: LighterClient,
}

#[pymethods]
impl PythonLighterHttpClient {
    #[new]
    #[pyo3(signature = (timeout=10.0, base_url=None))]
    fn new(timeout: f64, base_url: Option<String>) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: LighterClient::with_base_url(
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://mainnet.zklighter.elliot.ai".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        body=None,
        signed=false,
        headers=None,
        content_type="json"
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        content_type: &str,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let content_type = lighter_content_type(content_type)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                path,
                params.unwrap_or_default(),
                body.unwrap_or_default(),
                signed,
                headers.unwrap_or_default(),
                content_type,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        body=None,
        signed=false,
        headers=None,
        content_type="json"
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        content_type: &str,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let content_type = lighter_content_type(content_type)?;
        let params = params.unwrap_or_default();
        let body = body.unwrap_or_default();
        let headers = headers.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, path, params, body, signed, headers, content_type)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (path, params=None, headers=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        path: String,
        params: Option<Vec<(String, String)>>,
        headers: Option<BTreeMap<String, String>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        let headers = headers.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(path, params, headers).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (path, params=None, headers=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        path: String,
        params: Option<Vec<(String, String)>>,
        headers: Option<BTreeMap<String, String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        let headers = headers.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(path, params, headers)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonLighterHttpClient>()
}
