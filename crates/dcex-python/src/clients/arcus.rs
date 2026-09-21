use super::*;

#[pyclass(name = "ArcusSpotHttpClient")]
struct PythonArcusSpotHttpClient {
    client: ArcusSpotClient,
}

#[pymethods]
impl PythonArcusSpotHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, testnet=false, timeout=10.0, base_url=None))]
    fn new(
        api_key: Option<String>,
        testnet: bool,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let mut client = ArcusSpotClient::new(api_key, testnet, http_timeout(timeout)?)
            .map_err(to_py_runtime_error)?;
        if let Some(base_url) = base_url {
            client = client
                .with_base_url(base_url)
                .map_err(to_py_runtime_error)?;
        }
        Ok(Self { client })
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

#[pyclass(name = "ArcusHttpClient")]
struct PythonArcusHttpClient {
    client: ArcusClient,
}

#[pymethods]
impl PythonArcusHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, api_secret=None, address=None, account_index=0, testnet=false, timeout=10.0, base_url=None))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        address: Option<String>,
        account_index: u8,
        testnet: bool,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        let mut client = ArcusClient::new(
            api_key,
            api_secret,
            address,
            account_index,
            testnet,
            http_timeout(timeout)?,
        )
        .map_err(to_py_runtime_error)?;
        if let Some(base_url) = base_url {
            client = client
                .with_base_url(base_url)
                .map_err(to_py_runtime_error)?;
        }
        Ok(Self { client })
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
    module.add_class::<PythonArcusHttpClient>()?;
    module.add_class::<PythonArcusSpotHttpClient>()
}
