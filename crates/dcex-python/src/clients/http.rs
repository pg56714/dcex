use super::*;

#[pyclass(name = "HttpClient")]
struct PythonHttpClient {
    async_client: AsyncHttpClient,
    blocking_client: BlockingHttpClient,
}

#[pymethods]
impl PythonHttpClient {
    #[new]
    #[pyo3(signature = (timeout=10.0))]
    fn new(timeout: f64) -> PyResult<Self> {
        let timeout = http_timeout(timeout)?;
        Ok(Self {
            async_client: AsyncHttpClient::new(timeout).map_err(to_py_runtime_error)?,
            blocking_client: BlockingHttpClient::new(timeout).map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, base_url, path, query=None, headers=None, body=None))]
    #[allow(clippy::too_many_arguments)]
    fn request(
        &self,
        py: Python<'_>,
        method: &str,
        base_url: String,
        path: String,
        query: Option<Vec<(String, String)>>,
        headers: Option<BTreeMap<String, String>>,
        body: Option<Vec<u8>>,
    ) -> PyResult<PythonHttpResponse> {
        let request = http_request(method, base_url, path, query, headers, body)?;
        py.allow_threads(|| self.blocking_client.execute(request))
            .map(python_http_response)
            .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, base_url, path, query=None, headers=None, body=None))]
    #[allow(clippy::too_many_arguments)]
    fn request_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        base_url: String,
        path: String,
        query: Option<Vec<(String, String)>>,
        headers: Option<BTreeMap<String, String>>,
        body: Option<Vec<u8>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.async_client.clone();
        let request = http_request(method, base_url, path, query, headers, body)?;
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .execute(request)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonHttpClient>()
}
