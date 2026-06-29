use super::*;

#[pyclass(name = "BitmartHttpClient")]
struct PythonBitmartHttpClient {
    client: BitmartClient,
}

#[pymethods]
impl PythonBitmartHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        memo=None,
        timeout=10.0,
        spot_base_url=None,
        futures_base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        memo: Option<String>,
        timeout: f64,
        spot_base_url: Option<String>,
        futures_base_url: Option<String>,
    ) -> PyResult<Self> {
        let timeout = http_timeout(timeout)?;
        Ok(Self {
            client: BitmartClient::with_base_urls(
                api_key,
                api_secret,
                memo,
                timeout,
                spot_base_url.unwrap_or_else(|| "https://api-cloud.bitmart.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://api-cloud-v2.bitmart.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, market, path, params=None, body=None, signed=true))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let market = bitmart_market(market)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                market,
                path,
                params.unwrap_or_default(),
                body,
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, market, path, params=None, body=None, signed=true))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = bitmart_market(market)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(
                method,
                market,
                path,
                params.unwrap_or_default(),
                body,
                signed,
            )
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_auto(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        py.allow_threads(|| {
            self.client.request_raw_auto_blocking(
                method,
                path,
                params.unwrap_or_default(),
                body,
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_auto_json(
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
            client.request_raw_auto_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
    }

    #[pyo3(signature = (method, market, path, params=None, body=None, signed=true))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = bitmart_market(market)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, market, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method, market, path, params=None, body=None, signed=true))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_json_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = bitmart_market(market)?;
        let params = params.unwrap_or_default();
        python_json_http_request_async(py, async move {
            client
                .request_raw(method, market, path, params, body, signed)
                .await
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_auto_async<'py>(
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
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw_auto(method, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_auto_json_async<'py>(
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
            client
                .request_raw_auto(method, path, params, body, signed)
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
    m.add_class::<PythonBitmartHttpClient>()
}
