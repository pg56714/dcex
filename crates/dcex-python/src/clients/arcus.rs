use super::*;

#[pyclass(name = "ArcusHttpClient")]
struct PythonArcusHttpClient {
    client: ArcusClient,
}

#[pymethods]
impl PythonArcusHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, api_secret=None, address=None, account_index=0, testnet=false, timeout=10.0))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        address: Option<String>,
        account_index: u8,
        testnet: bool,
        timeout: f64,
    ) -> PyResult<Self> {
        Ok(Self {
            client: ArcusClient::new(
                api_key,
                api_secret,
                address,
                account_index,
                testnet,
                http_timeout(timeout)?,
            )
            .map_err(to_py_runtime_error)?,
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
        python_validated_json_request(py, method_name, params, |name, params| async move {
            client.public_request(&name, params).await
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
        python_validated_json_request_async(py, method_name, params, |name, params| async move {
            client.public_request(&name, params).await
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
        python_validated_json_request(py, method_name, params, |name, params| async move {
            client.private_request(&name, params).await
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
        python_validated_json_request_async(py, method_name, params, |name, params| async move {
            client.private_request(&name, params).await
        })
    }
}

pub(super) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonArcusHttpClient>()
}
