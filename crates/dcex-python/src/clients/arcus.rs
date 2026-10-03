use super::*;

#[pyclass(name = "ArcusSpotHttpClient")]
struct PythonArcusSpotHttpClient {
    client: ArcusSpotClient,
}

#[pymethods]
impl PythonArcusSpotHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, testnet=false, timeout=10.0, base_url=None, wallet_address=None, rpc_url=None))]
    fn new(
        api_key: Option<String>,
        testnet: bool,
        timeout: f64,
        base_url: Option<String>,
        wallet_address: Option<String>,
        rpc_url: Option<String>,
    ) -> PyResult<Self> {
        let mut client = ArcusSpotClient::new(api_key, testnet, http_timeout(timeout)?)
            .map_err(to_py_runtime_error)?;
        if let Some(base_url) = base_url {
            client = client
                .with_base_url(base_url)
                .map_err(to_py_runtime_error)?;
        }
        if let Some(wallet_address) = wallet_address {
            client = client
                .with_wallet_address(wallet_address)
                .map_err(to_py_runtime_error)?;
        }
        if let Some(rpc_url) = rpc_url {
            client = client.with_rpc_url(rpc_url).map_err(to_py_runtime_error)?;
        }
        Ok(Self { client })
    }

    #[pyo3(signature = (quote_json, taker, signature, permits_json=None, route_tag=None, builder_fee_bps=None))]
    #[allow(clippy::too_many_arguments)]
    fn build_signed_quote_json(
        &self,
        py: Python<'_>,
        quote_json: String,
        taker: String,
        signature: String,
        permits_json: Option<String>,
        route_tag: Option<String>,
        builder_fee_bps: Option<u16>,
    ) -> PyResult<Py<PyAny>> {
        let quote = serde_json::from_str(&quote_json)
            .map_err(|error| PyValueError::new_err(format!("invalid Arcus quote JSON: {error}")))?;
        let permits = permits_json
            .map(|value| {
                serde_json::from_str(&value).map_err(|error| {
                    PyValueError::new_err(format!("invalid Arcus permits JSON: {error}"))
                })
            })
            .transpose()?;
        let body = self
            .client
            .build_signed_quote_with_fee(
                quote,
                &taker,
                &signature,
                permits,
                route_tag.as_deref(),
                builder_fee_bps,
            )
            .map_err(to_py_runtime_error)?;
        json_value_to_py(py, &body)
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
    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }
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

    fn sign_websocket_request(
        &self,
        py: Python<'_>,
        id: u64,
        method_name: String,
        params: Vec<(String, String)>,
    ) -> PyResult<String> {
        let client = self.client.clone();
        py.allow_threads(move || {
            dcex::http::block_on(async move {
                client
                    .sign_websocket_request(id, &method_name, params)
                    .await
            })
        })
        .map(|v| v.to_string())
        .map_err(to_py_runtime_error)
    }
    fn sign_websocket_request_async<'py>(
        &self,
        py: Python<'py>,
        id: u64,
        method_name: String,
        params: Vec<(String, String)>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .sign_websocket_request(id, &method_name, params)
                .await
                .map(|v| v.to_string())
                .map_err(to_py_runtime_error)
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
    module.add_class::<PythonArcusHttpClient>()?;
    module.add_class::<PythonArcusSpotHttpClient>()
}
