use super::*;

#[pyclass(name = "LighterCredentials", frozen)]
#[derive(Clone)]
struct PythonLighterCredentials {
    credentials: LighterCredentials,
}

#[pymethods]
impl PythonLighterCredentials {
    #[new]
    fn new(account_index: u64, api_key_index: u64, api_private_key: String) -> PyResult<Self> {
        Ok(Self {
            credentials: LighterCredentials::new(account_index, api_key_index, api_private_key)
                .map_err(to_py_value_error)?,
        })
    }

    #[staticmethod]
    #[pyo3(signature = (network="mainnet"))]
    fn from_env(network: &str) -> PyResult<Self> {
        let network = lighter_network(network)?;
        Ok(Self {
            credentials: LighterCredentials::from_env(network).map_err(to_py_value_error)?,
        })
    }

    #[getter]
    fn account_index(&self) -> u64 {
        self.credentials.account_index()
    }

    #[getter]
    fn api_key_index(&self) -> u64 {
        self.credentials.api_key_index()
    }

    #[getter]
    fn api_private_key(&self) -> &str {
        self.credentials.api_private_key()
    }

    fn __repr__(&self) -> String {
        format!(
            "LighterCredentials(account_index={}, api_key_index={}, api_private_key='[REDACTED]')",
            self.credentials.account_index(),
            self.credentials.api_key_index()
        )
    }
}

#[pyclass(name = "LighterHttpClient")]
struct PythonLighterHttpClient {
    client: LighterClient,
}

#[pymethods]
impl PythonLighterHttpClient {
    #[new]
    #[pyo3(signature = (
        timeout=10.0,
        base_url=None,
        account_index=None,
        api_key_index=None,
        api_private_key=None,
        network="mainnet",
        chain_id=None
    ))]
    fn new(
        timeout: f64,
        base_url: Option<String>,
        account_index: Option<u64>,
        api_key_index: Option<u64>,
        api_private_key: Option<String>,
        network: &str,
        chain_id: Option<u64>,
    ) -> PyResult<Self> {
        let timeout = http_timeout(timeout)?;
        let network = lighter_network(network)?;
        let client = if let Some(base_url) = base_url {
            if let Some(chain_id) = chain_id {
                LighterClient::with_base_url_credentials_and_chain_id(
                    timeout,
                    base_url,
                    chain_id,
                    account_index,
                    api_key_index,
                    api_private_key,
                )
            } else {
                LighterClient::with_base_url_and_credentials(
                    timeout,
                    base_url,
                    account_index,
                    api_key_index,
                    api_private_key,
                )
            }
        } else {
            if chain_id.is_some() {
                return Err(PyValueError::new_err(
                    "Lighter chain_id is only valid with a custom base_url.",
                ));
            }
            LighterClient::with_network_and_credentials(
                timeout,
                network,
                account_index,
                api_key_index,
                api_private_key,
            )
        };
        Ok(Self {
            client: client.map_err(to_py_runtime_error)?,
        })
    }

    #[staticmethod]
    #[pyo3(signature = (timeout=10.0, network="mainnet"))]
    fn from_env(timeout: f64, network: &str) -> PyResult<Self> {
        let client =
            LighterClient::with_env_credentials(http_timeout(timeout)?, lighter_network(network)?)
                .map_err(to_py_runtime_error)?;
        Ok(Self { client })
    }

    fn network(&self) -> Option<&'static str> {
        self.client.network().map(LighterNetwork::as_str)
    }

    fn base_url(&self) -> &str {
        self.client.base_url()
    }

    fn chain_id(&self) -> Option<u64> {
        self.client.chain_id()
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
        headers=None,
        content_type="json"
    ))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_json(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<(String, String)>>,
        signed: bool,
        headers: Option<BTreeMap<String, String>>,
        content_type: &str,
    ) -> PyResult<PythonJsonResponse> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let content_type = lighter_content_type(content_type)?;
        python_json_http_request(py, move || {
            client.request_raw_blocking(
                method,
                path,
                params.unwrap_or_default(),
                body.unwrap_or_default(),
                signed,
                headers.unwrap_or_default(),
                content_type,
            )
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
    fn request_raw_json_async<'py>(
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
        python_json_http_request_async(py, async move {
            client
                .request_raw(method, path, params, body, signed, headers, content_type)
                .await
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn sign_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<(u64, String, String, Option<String>)> {
        let params = params.unwrap_or_default();
        py.allow_threads(|| self.client.sign_request_blocking(method_name, params))
            .map(|tx| (tx.tx_type, tx.tx_info, tx.tx_hash, None))
            .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn sign_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .sign_request(&method_name, params)
                .await
                .map(|tx| (tx.tx_type, tx.tx_info, tx.tx_hash, None::<String>))
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (deadline=None, api_key_index=None))]
    fn create_auth_token(
        &self,
        deadline: Option<u64>,
        api_key_index: Option<u64>,
    ) -> PyResult<String> {
        match (deadline, api_key_index) {
            (None, None) => self.client.create_auth_token(),
            (Some(deadline), None) => self.client.create_auth_token_with_deadline(deadline),
            (None, Some(api_key_index)) => self
                .client
                .create_auth_token_with_api_key_index(api_key_index),
            (Some(deadline), Some(api_key_index)) => self
                .client
                .create_auth_token_with_deadline_and_api_key_index(deadline, api_key_index),
        }
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (deadline=None, api_key_index=None))]
    fn create_auth_token_async<'py>(
        &self,
        py: Python<'py>,
        deadline: Option<u64>,
        api_key_index: Option<u64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            match (deadline, api_key_index) {
                (None, None) => client.create_auth_token(),
                (Some(deadline), None) => client.create_auth_token_with_deadline(deadline),
                (None, Some(api_key_index)) => {
                    client.create_auth_token_with_api_key_index(api_key_index)
                }
                (Some(deadline), Some(api_key_index)) => client
                    .create_auth_token_with_deadline_and_api_key_index(deadline, api_key_index),
            }
            .map_err(to_py_runtime_error)
        })
    }

    fn check_client(&self, py: Python<'_>) -> PyResult<Option<String>> {
        py.allow_threads(|| self.client.check_client_blocking())
            .map_err(to_py_runtime_error)
    }

    fn check_client_async<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client.check_client().await.map_err(to_py_runtime_error)
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
    m.add_class::<PythonLighterCredentials>()?;
    m.add_class::<PythonLighterHttpClient>()
}
