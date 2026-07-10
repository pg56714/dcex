use super::*;

#[pyclass(name = "ExtendedHttpClient")]
struct PythonExtendedHttpClient {
    client: ExtendedClient,
}

#[pymethods]
impl PythonExtendedHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        stark_private_key=None,
        stark_public_key=None,
        vault_number=None,
        client_id=None,
        timeout=10.0,
        base_url=None,
        user_agent="dcex-rust/0.1".to_string()
    ))]
    fn new(
        api_key: Option<String>,
        stark_private_key: Option<String>,
        stark_public_key: Option<String>,
        vault_number: Option<u32>,
        client_id: Option<String>,
        timeout: f64,
        base_url: Option<String>,
        user_agent: String,
    ) -> PyResult<Self> {
        let timeout = http_timeout(timeout)?;
        Ok(Self {
            client: ExtendedClient::with_base_url_and_stark(
                api_key,
                stark_private_key,
                stark_public_key,
                vault_number,
                client_id,
                timeout,
                base_url.unwrap_or_else(|| "https://api.starknet.extended.exchange".to_string()),
                user_agent,
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
        body=None,
        signed=false,
        headers=None
    ))]
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(
                method,
                path,
                params.unwrap_or_default(),
                body,
                signed,
                headers.unwrap_or_default(),
            )
        })
    }

    #[pyo3(signature = (
        method,
        path,
        params=None,
        body=None,
        signed=false,
        headers=None
    ))]
    fn request_raw_json_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let params = params.unwrap_or_default();
        let headers = headers.unwrap_or_default();
        python_json_http_request_async(py, async move {
            client
                .request_raw(method, path, params, body, signed, headers)
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
    m.add_class::<PythonExtendedHttpClient>()
}
