use super::*;

#[pyclass(name = "BackpackHttpClient")]
struct PythonBackpackHttpClient {
    client: BackpackClient,
}

#[pymethods]
impl PythonBackpackHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        window=5000,
        timeout=10.0,
        base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        window: u64,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BackpackClient::with_base_url(
                api_key,
                api_secret,
                window,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://api.backpack.exchange".to_string()),
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
        instruction=None,
        signature_payload=None,
        headers=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
        instruction: Option<String>,
        signature_payload: Option<SignaturePayload>,
        headers: Option<BTreeMap<String, String>>,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                path,
                params.unwrap_or_default(),
                body,
                signed,
                instruction,
                signature_payload,
                headers.unwrap_or_default(),
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
        instruction=None,
        signature_payload=None,
        headers=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
        instruction: Option<String>,
        signature_payload: Option<SignaturePayload>,
        headers: Option<BTreeMap<String, String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let params = params.unwrap_or_default();
        let headers = headers.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(
                    method,
                    path,
                    params,
                    body,
                    signed,
                    instruction,
                    signature_payload,
                    headers,
                )
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (path, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        path: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| block_on(async move { client.public_request(path, params).await }))
            .map_err(to_py_runtime_error)
            .and_then(python_validated_response)
    }

    #[pyo3(signature = (path, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        path: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(path, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonBackpackHttpClient>()
}
