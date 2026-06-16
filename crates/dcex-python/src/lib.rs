use std::collections::BTreeMap;
use std::time::Duration;

use dcex::common::{self, OrderSide};
use dcex::exchange::ValidatedResponse;
use dcex::exchanges::aster::{AsterClient, AsterMarket};
use dcex::exchanges::backpack::{BackpackClient, SignaturePayload};
use dcex::exchanges::binance::{BinanceClient, BinanceMarket};
use dcex::exchanges::bingx::BingxClient;
use dcex::exchanges::bitget::BitgetClient;
use dcex::exchanges::bitmart::{BitmartClient, BitmartMarket};
use dcex::exchanges::bitmex::BitmexClient;
use dcex::exchanges::bybit::BybitClient;
use dcex::exchanges::gateio::GateioClient;
use dcex::exchanges::hyperliquid::HyperliquidClient;
use dcex::exchanges::kraken::{KrakenAuth, KrakenClient};
use dcex::exchanges::kucoin::{KucoinClient, KucoinMarket};
use dcex::exchanges::lighter::{LighterClient, LighterContentType};
use dcex::exchanges::mexc::{MexcApi, MexcClient};
use dcex::exchanges::okx::OkxClient;
use dcex::http::{
    block_on, AsyncHttpClient, BlockingHttpClient, HttpMethod, HttpRequest, HttpResponse,
};
use dcex::lighter;
use dcex::product_table::{MarketInfo, ProductFilter, ProductTable};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;

fn to_py_value_error(error: dcex::DcexError) -> PyErr {
    PyValueError::new_err(error.to_string())
}

fn to_py_runtime_error(error: dcex::DcexError) -> PyErr {
    match error {
        dcex::DcexError::InvalidInput(_) => to_py_value_error(error),
        _ => PyRuntimeError::new_err(error.to_string()),
    }
}

fn http_method(method: &str) -> PyResult<HttpMethod> {
    match method.to_ascii_uppercase().as_str() {
        "DELETE" => Ok(HttpMethod::Delete),
        "GET" => Ok(HttpMethod::Get),
        "PATCH" => Ok(HttpMethod::Patch),
        "POST" => Ok(HttpMethod::Post),
        "PUT" => Ok(HttpMethod::Put),
        _ => Err(PyValueError::new_err(format!(
            "unsupported HTTP method: {method}"
        ))),
    }
}

fn http_request(
    method: &str,
    base_url: String,
    path: String,
    query: Option<Vec<(String, String)>>,
    headers: Option<BTreeMap<String, String>>,
    body: Option<Vec<u8>>,
) -> PyResult<HttpRequest> {
    let mut request = HttpRequest::new(http_method(method)?, base_url, path);
    request.query = query.unwrap_or_default();
    request.headers = headers.unwrap_or_default();
    if let Some(body) = body {
        request = request.raw(body);
    }
    Ok(request)
}

type PythonHttpResponse = (u16, BTreeMap<String, String>, Py<PyBytes>);

fn python_http_response(response: HttpResponse) -> PythonHttpResponse {
    let body = Python::with_gil(|py| PyBytes::new(py, &response.body).unbind());
    (response.status, response.headers, body)
}

fn python_validated_response(response: ValidatedResponse) -> PyResult<PythonHttpResponse> {
    let body = serde_json::to_vec(&response.data)
        .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
    let body = Python::with_gil(|py| PyBytes::new(py, &body).unbind());
    Ok((response.status, response.headers, body))
}

fn exchange_from_name(name: &str) -> PyResult<dcex::exchange::Exchange> {
    dcex::exchange::Exchange::ALL
        .into_iter()
        .find(|exchange| exchange.as_str() == name)
        .ok_or_else(|| PyValueError::new_err(format!("Invalid exchange_name: {name}")))
}

fn market_info_from_map(mut row: BTreeMap<String, String>) -> PyResult<MarketInfo> {
    let mut take_required = |key: &str| {
        row.remove(key)
            .ok_or_else(|| PyValueError::new_err(format!("missing product table field: {key}")))
    };
    Ok(MarketInfo {
        exchange: take_required("exchange")?,
        exchange_symbol: take_required("exchange_symbol")?,
        product_symbol: take_required("product_symbol")?,
        product_type: take_required("product_type")?,
        exchange_type: take_required("exchange_type")?,
        price_precision: row.remove("price_precision").unwrap_or_default(),
        size_precision: row.remove("size_precision").unwrap_or_default(),
        min_size: row.remove("min_size").unwrap_or_default(),
        base_currency: row.remove("base_currency").unwrap_or_default(),
        quote_currency: row.remove("quote_currency").unwrap_or_default(),
        min_notional: row
            .remove("min_notional")
            .unwrap_or_else(|| "0".to_string()),
        size_per_contract: row
            .remove("size_per_contract")
            .unwrap_or_else(|| "1".to_string()),
    })
}

fn market_info_to_map(row: MarketInfo) -> BTreeMap<String, String> {
    BTreeMap::from([
        ("exchange".to_string(), row.exchange),
        ("exchange_symbol".to_string(), row.exchange_symbol),
        ("product_symbol".to_string(), row.product_symbol),
        ("product_type".to_string(), row.product_type),
        ("exchange_type".to_string(), row.exchange_type),
        ("price_precision".to_string(), row.price_precision),
        ("size_precision".to_string(), row.size_precision),
        ("min_size".to_string(), row.min_size),
        ("base_currency".to_string(), row.base_currency),
        ("quote_currency".to_string(), row.quote_currency),
        ("min_notional".to_string(), row.min_notional),
        ("size_per_contract".to_string(), row.size_per_contract),
    ])
}

fn market_rows_to_maps(rows: Vec<MarketInfo>) -> Vec<BTreeMap<String, String>> {
    rows.into_iter().map(market_info_to_map).collect()
}

#[pyclass(name = "ProductTable")]
struct PythonProductTable {
    table: ProductTable,
}

#[pymethods]
impl PythonProductTable {
    #[new]
    fn new(rows: Vec<BTreeMap<String, String>>) -> PyResult<Self> {
        let rows = rows
            .into_iter()
            .map(market_info_from_map)
            .collect::<PyResult<Vec<_>>>()?;
        Ok(Self {
            table: ProductTable::new(rows),
        })
    }

    fn rows(&self) -> Vec<BTreeMap<String, String>> {
        market_rows_to_maps(self.table.rows().to_vec())
    }

    #[pyo3(signature = (
        key,
        product_symbol=None,
        exchange=None,
        product_type=None,
        exchange_type=None,
        exchange_symbol=None
    ))]
    fn get(
        &self,
        key: &str,
        product_symbol: Option<&str>,
        exchange: Option<&str>,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
        exchange_symbol: Option<&str>,
    ) -> PyResult<String> {
        self.table
            .get(
                key,
                ProductFilter {
                    product_symbol,
                    exchange,
                    product_type,
                    exchange_type,
                    exchange_symbol,
                },
            )
            .map_err(to_py_value_error)
    }

    fn get_exchange_symbol(&self, exchange: &str, product_symbol: &str) -> PyResult<String> {
        self.table
            .get_exchange_symbol(exchange, product_symbol)
            .map_err(to_py_value_error)
    }

    #[pyo3(signature = (exchange, exchange_symbol, product_type=None, exchange_type=None))]
    fn get_product_symbol(
        &self,
        exchange: &str,
        exchange_symbol: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> PyResult<String> {
        self.table
            .get_product_symbol(exchange, exchange_symbol, product_type, exchange_type)
            .map_err(to_py_value_error)
    }

    #[pyo3(signature = (exchange, product_symbol=None, exchange_symbol=None))]
    fn get_product_type(
        &self,
        exchange: &str,
        product_symbol: Option<&str>,
        exchange_symbol: Option<&str>,
    ) -> PyResult<String> {
        self.table
            .get_product_type(exchange, product_symbol, exchange_symbol)
            .map_err(to_py_value_error)
    }

    #[pyo3(signature = (exchange, product_symbol=None, exchange_symbol=None))]
    fn get_exchange_type(
        &self,
        exchange: &str,
        product_symbol: Option<&str>,
        exchange_symbol: Option<&str>,
    ) -> PyResult<String> {
        self.table
            .get_exchange_type(exchange, product_symbol, exchange_symbol)
            .map_err(to_py_value_error)
    }

    fn get_base_currency(&self, exchange: &str, product_symbol: &str) -> PyResult<String> {
        self.table
            .get_base_currency(exchange, product_symbol)
            .map_err(to_py_value_error)
    }

    fn get_quote_currency(&self, exchange: &str, product_symbol: &str) -> PyResult<String> {
        self.table
            .get_quote_currency(exchange, product_symbol)
            .map_err(to_py_value_error)
    }

    fn get_trading_details(
        &self,
        exchange: &str,
        product_symbol: &str,
    ) -> PyResult<BTreeMap<String, String>> {
        let details = self
            .table
            .get_trading_details(exchange, product_symbol)
            .map_err(to_py_value_error)?;
        Ok(BTreeMap::from([
            ("price_precision".to_string(), details.price_precision),
            ("size_precision".to_string(), details.size_precision),
            ("min_size".to_string(), details.min_size),
            ("min_notional".to_string(), details.min_notional),
            ("size_per_contract".to_string(), details.size_per_contract),
        ]))
    }

    #[pyo3(signature = (exchange, product_type=None, exchange_type=None))]
    fn get_exchange_symbols(
        &self,
        exchange: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Vec<String> {
        self.table
            .get_exchange_symbols(exchange, product_type, exchange_type)
    }

    #[pyo3(signature = (exchange, product_type=None, exchange_type=None))]
    fn get_product_symbols(
        &self,
        exchange: &str,
        product_type: Option<&str>,
        exchange_type: Option<&str>,
    ) -> Vec<String> {
        self.table
            .get_product_symbols(exchange, product_type, exchange_type)
    }
}

#[pyfunction]
#[pyo3(signature = (exchange_name=None, timeout=10.0))]
fn fetch_product_table(
    py: Python<'_>,
    exchange_name: Option<&str>,
    timeout: f64,
) -> PyResult<Vec<BTreeMap<String, String>>> {
    if !timeout.is_finite() || timeout <= 0.0 {
        return Err(PyValueError::new_err(
            "HTTP timeout must be a positive finite number.",
        ));
    }
    let exchange = exchange_name.map(exchange_from_name).transpose()?;
    py.allow_threads(|| {
        block_on(async move {
            ProductTable::fetch(exchange, Duration::from_secs_f64(timeout))
                .await
                .map(ProductTable::into_rows)
        })
    })
    .map(market_rows_to_maps)
    .map_err(to_py_runtime_error)
}

#[pyfunction]
#[pyo3(signature = (exchange_name=None, timeout=10.0))]
fn fetch_product_table_async<'py>(
    py: Python<'py>,
    exchange_name: Option<String>,
    timeout: f64,
) -> PyResult<Bound<'py, PyAny>> {
    if !timeout.is_finite() || timeout <= 0.0 {
        return Err(PyValueError::new_err(
            "HTTP timeout must be a positive finite number.",
        ));
    }
    let exchange = exchange_name
        .as_deref()
        .map(exchange_from_name)
        .transpose()?;
    pyo3_async_runtimes::tokio::future_into_py(py, async move {
        ProductTable::fetch(exchange, Duration::from_secs_f64(timeout))
            .await
            .map(ProductTable::into_rows)
            .map(market_rows_to_maps)
            .map_err(to_py_runtime_error)
    })
}

fn binance_market(market: &str) -> PyResult<BinanceMarket> {
    match market.to_ascii_lowercase().as_str() {
        "futures" | "future" | "swap" => Ok(BinanceMarket::Futures),
        "spot" | "wallet" => Ok(BinanceMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Binance market: {market}"
        ))),
    }
}

fn parse_json_body(body: Option<Vec<u8>>) -> PyResult<Option<serde_json::Value>> {
    body.map(|body| {
        serde_json::from_slice(&body).map_err(|error| PyValueError::new_err(error.to_string()))
    })
    .transpose()
}

fn mexc_api(api: &str) -> PyResult<MexcApi> {
    match api.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(MexcApi::Contract),
        "spot" => Ok(MexcApi::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported MEXC API: {api}"
        ))),
    }
}

fn bitmart_market(market: &str) -> PyResult<BitmartMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(BitmartMarket::Futures),
        "spot" | "wallet" => Ok(BitmartMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported BitMart market: {market}"
        ))),
    }
}

fn kucoin_market(market: &str) -> PyResult<KucoinMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(KucoinMarket::Futures),
        "spot" | "wallet" => Ok(KucoinMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported KuCoin market: {market}"
        ))),
    }
}

fn kraken_auth(auth: &str) -> PyResult<KrakenAuth> {
    match auth.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(KrakenAuth::Futures),
        "spot" | "wallet" => Ok(KrakenAuth::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Kraken auth type: {auth}"
        ))),
    }
}

fn lighter_content_type(content_type: &str) -> PyResult<LighterContentType> {
    match content_type.to_ascii_lowercase().as_str() {
        "form" => Ok(LighterContentType::Form),
        "json" => Ok(LighterContentType::Json),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Lighter content type: {content_type}"
        ))),
    }
}

fn aster_market(market: &str) -> PyResult<AsterMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(AsterMarket::Futures),
        "spot" | "wallet" => Ok(AsterMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Aster market: {market}"
        ))),
    }
}

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
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        let timeout = Duration::from_secs_f64(timeout);
        Ok(Self {
            async_client: AsyncHttpClient::new(timeout).map_err(to_py_runtime_error)?,
            blocking_client: BlockingHttpClient::new(timeout).map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, base_url, path, query=None, headers=None, body=None))]
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

#[pyclass(name = "BinanceHttpClient")]
struct PythonBinanceHttpClient {
    client: BinanceClient,
}

#[pymethods]
impl PythonBinanceHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        timeout=10.0,
        spot_base_url=None,
        futures_base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        spot_base_url: Option<String>,
        futures_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BinanceClient::with_base_urls(
                api_key,
                api_secret,
                Duration::from_secs_f64(timeout),
                spot_base_url.unwrap_or_else(|| "https://api.binance.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://fapi.binance.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let market = binance_market(market)?;
        py.allow_threads(|| {
            self.client
                .request_blocking(method, market, path, params.unwrap_or_default(), signed)
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = binance_market(market)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request(method, market, path, params, signed)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let market = binance_market(market)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                market,
                path,
                params.unwrap_or_default(),
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = binance_market(market)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.private_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .private_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

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
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BingxClient::with_base_url(
                api_key,
                api_secret,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://open-api.bingx.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
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

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "BitgetHttpClient")]
struct PythonBitgetHttpClient {
    client: BitgetClient,
}

#[pymethods]
impl PythonBitgetHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        passphrase=None,
        timeout=10.0,
        base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BitgetClient::with_base_url(
                api_key,
                api_secret,
                passphrase,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://api.bitget.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw(
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
            self.client
                .request_raw_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
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
                .request_raw(method, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

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
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BitmartClient::with_base_urls(
                api_key,
                api_secret,
                memo,
                Duration::from_secs_f64(timeout),
                spot_base_url.unwrap_or_else(|| "https://api-cloud.bitmart.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://api-cloud-v2.bitmart.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, market, path, params=None, body=None, signed=true))]
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

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "BitmexHttpClient")]
struct PythonBitmexHttpClient {
    client: BitmexClient,
}

#[pymethods]
impl PythonBitmexHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, api_secret=None, timeout=10.0, base_url=None))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BitmexClient::with_base_url(
                api_key,
                api_secret,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://www.bitmex.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw(
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
            self.client
                .request_raw_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
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
                .request_raw(method, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "BybitHttpClient")]
struct PythonBybitHttpClient {
    client: BybitClient,
}

#[pymethods]
impl PythonBybitHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        recv_window=5000,
        sync_server_time=true,
        timeout=10.0,
        base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: BybitClient::with_base_url(
                api_key,
                api_secret,
                recv_window,
                sync_server_time,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://api.bybit.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw(
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
            self.client
                .request_raw_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
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
                .request_raw(method, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.private_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .private_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "GateioHttpClient")]
struct PythonGateioHttpClient {
    client: GateioClient,
}

#[pymethods]
impl PythonGateioHttpClient {
    #[new]
    #[pyo3(signature = (api_key=None, api_secret=None, timeout=10.0, base_url=None))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: GateioClient::with_base_url(
                api_key,
                api_secret,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://api.gateio.ws".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw(
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
            self.client
                .request_raw_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
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
                .request_raw(method, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "MexcHttpClient")]
struct PythonMexcHttpClient {
    client: MexcClient,
}

#[pymethods]
impl PythonMexcHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        timeout=10.0,
        base_url=None,
        contract_base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: f64,
        base_url: Option<String>,
        contract_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        let base_url = base_url.unwrap_or_else(|| "https://api.mexc.com".to_string());
        Ok(Self {
            client: MexcClient::with_base_urls(
                api_key,
                api_secret,
                Duration::from_secs_f64(timeout),
                base_url.clone(),
                contract_base_url.unwrap_or(base_url),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, api, path, params=None, body=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        api: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let api = mexc_api(api)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                api,
                path,
                params.unwrap_or_default(),
                body,
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, api, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        api: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let api = mexc_api(api)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, api, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "KucoinHttpClient")]
struct PythonKucoinHttpClient {
    client: KucoinClient,
}

#[pymethods]
impl PythonKucoinHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        passphrase=None,
        timeout=10.0,
        spot_base_url=None,
        futures_base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: f64,
        spot_base_url: Option<String>,
        futures_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: KucoinClient::with_base_urls(
                api_key,
                api_secret,
                passphrase,
                Duration::from_secs_f64(timeout),
                spot_base_url.unwrap_or_else(|| "https://api.kucoin.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://api-futures.kucoin.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, market, path, params=None, body=None, signed=true))]
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
        let market = kucoin_market(market)?;
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
        let market = kucoin_market(market)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, market, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "KrakenHttpClient")]
struct PythonKrakenHttpClient {
    client: KrakenClient,
}

#[pymethods]
impl PythonKrakenHttpClient {
    #[new]
    #[pyo3(signature = (
        spot_api_key=None,
        spot_api_secret=None,
        futures_api_key=None,
        futures_api_secret=None,
        timeout=10.0,
        spot_base_url=None,
        futures_base_url=None
    ))]
    #[allow(clippy::too_many_arguments)]
    fn new(
        spot_api_key: Option<String>,
        spot_api_secret: Option<String>,
        futures_api_key: Option<String>,
        futures_api_secret: Option<String>,
        timeout: f64,
        spot_base_url: Option<String>,
        futures_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: KrakenClient::with_base_urls(
                spot_api_key,
                spot_api_secret,
                futures_api_key,
                futures_api_secret,
                Duration::from_secs_f64(timeout),
                spot_base_url.unwrap_or_else(|| "https://api.kraken.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://futures.kraken.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, auth, path, params=None, json_body=None, signed=false))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        auth: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        json_body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let auth = kraken_auth(auth)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                auth,
                path,
                params.unwrap_or_default(),
                json_body,
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, auth, path, params=None, json_body=None, signed=false))]
    #[allow(clippy::too_many_arguments)]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        auth: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        json_body: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let auth = kraken_auth(auth)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, auth, path, params, json_body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

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

#[pyclass(name = "AsterHttpClient")]
struct PythonAsterHttpClient {
    client: AsterClient,
}

#[pymethods]
impl PythonAsterHttpClient {
    #[new]
    #[pyo3(signature = (
        user_address=None,
        signer_address=None,
        private_key=None,
        timeout=10.0,
        spot_base_url=None,
        futures_base_url=None
    ))]
    fn new(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: f64,
        spot_base_url: Option<String>,
        futures_base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: AsterClient::with_base_urls(
                user_address,
                signer_address,
                private_key,
                Duration::from_secs_f64(timeout),
                spot_base_url.unwrap_or_else(|| "https://sapi.asterdex.com".to_string()),
                futures_base_url.unwrap_or_else(|| "https://fapi.asterdex.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        let market = aster_market(market)?;
        py.allow_threads(|| {
            self.client.request_raw_blocking(
                method,
                market,
                path,
                params.unwrap_or_default(),
                signed,
            )
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, market, path, params=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        market: &str,
        path: String,
        params: Option<Vec<(String, String)>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        let market = aster_market(market)?;
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "HyperliquidHttpClient")]
struct PythonHyperliquidHttpClient {
    client: HyperliquidClient,
}

#[pymethods]
impl PythonHyperliquidHttpClient {
    #[new]
    #[pyo3(signature = (
        testnet=false,
        wallet_address=None,
        private_key=None,
        timeout=10.0,
        endpoint=None
    ))]
    fn new(
        testnet: bool,
        wallet_address: Option<String>,
        private_key: Option<String>,
        timeout: f64,
        endpoint: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        let default_endpoint = if testnet {
            "https://api.hyperliquid-testnet.xyz"
        } else {
            "https://api.hyperliquid.xyz"
        };
        Ok(Self {
            client: HyperliquidClient::with_endpoint(
                testnet,
                wallet_address,
                private_key,
                Duration::from_secs_f64(timeout),
                endpoint.unwrap_or_else(|| default_endpoint.to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    #[pyo3(signature = (method, path, query_json, action_msgpack=None, signed=true))]
    fn request_raw(
        &self,
        py: Python<'_>,
        method: &str,
        path: String,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<PythonHttpResponse> {
        let method = http_method(method)?;
        py.allow_threads(|| {
            self.client
                .request_raw_blocking(method, path, query_json, action_msgpack, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, query_json, action_msgpack=None, signed=true))]
    fn request_raw_async<'py>(
        &self,
        py: Python<'py>,
        method: &str,
        path: String,
        query_json: Vec<u8>,
        action_msgpack: Option<Vec<u8>>,
        signed: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let method = http_method(method)?;
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .request_raw(method, path, query_json, action_msgpack, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (query_json))]
    fn public_request(&self, py: Python<'_>, query_json: Vec<u8>) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        py.allow_threads(|| block_on(async move { client.public_request(query_json).await }))
            .map_err(to_py_runtime_error)
            .and_then(python_validated_response)
    }

    #[pyo3(signature = (query_json))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        query_json: Vec<u8>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(query_json)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyclass(name = "OkxHttpClient")]
struct PythonOkxHttpClient {
    client: OkxClient,
}

#[pymethods]
impl PythonOkxHttpClient {
    #[new]
    #[pyo3(signature = (
        api_key=None,
        api_secret=None,
        passphrase=None,
        flag="0".to_string(),
        timeout=10.0,
        base_url=None
    ))]
    fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        flag: String,
        timeout: f64,
        base_url: Option<String>,
    ) -> PyResult<Self> {
        if !timeout.is_finite() || timeout <= 0.0 {
            return Err(PyValueError::new_err(
                "HTTP timeout must be a positive finite number.",
            ));
        }
        Ok(Self {
            client: OkxClient::with_base_url(
                api_key,
                api_secret,
                passphrase,
                flag,
                Duration::from_secs_f64(timeout),
                base_url.unwrap_or_else(|| "https://openapi.okx.com".to_string()),
            )
            .map_err(to_py_runtime_error)?,
        })
    }

    fn set_product_table(&mut self, table: PyRef<'_, PythonProductTable>) {
        self.client.set_product_table(table.table.clone());
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw(
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
            self.client
                .request_raw_blocking(method, path, params.unwrap_or_default(), body, signed)
        })
        .map(python_http_response)
        .map_err(to_py_runtime_error)
    }

    #[pyo3(signature = (method, path, params=None, body=None, signed=true))]
    fn request_raw_async<'py>(
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
                .request_raw(method, path, params, body, signed)
                .await
                .map(python_http_response)
                .map_err(to_py_runtime_error)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.public_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn public_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .public_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request(
        &self,
        py: Python<'_>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<PythonHttpResponse> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        py.allow_threads(|| {
            block_on(async move { client.private_request(&method_name, params).await })
        })
        .map_err(to_py_runtime_error)
        .and_then(python_validated_response)
    }

    #[pyo3(signature = (method_name, params=None))]
    fn private_request_async<'py>(
        &self,
        py: Python<'py>,
        method_name: String,
        params: Option<Vec<(String, String)>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let client = self.client.clone();
        let params = params.unwrap_or_default();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            client
                .private_request(&method_name, params)
                .await
                .map_err(to_py_runtime_error)
                .and_then(python_validated_response)
        })
    }
}

#[pyfunction]
fn lighter_poseidon_hash_bytes(values: Vec<u64>) -> PyResult<Vec<u8>> {
    Ok(lighter::poseidon_hash_bytes(&values).to_vec())
}

#[pyfunction]
fn lighter_public_key_bytes(private_key: &[u8]) -> PyResult<Vec<u8>> {
    let scalar = lighter::private_key_from_bytes(private_key).map_err(to_py_value_error)?;
    lighter::public_key_bytes(&scalar)
        .map(|value| value.to_vec())
        .map_err(to_py_value_error)
}

#[pyfunction]
fn lighter_schnorr_sign(
    message_hash: &[u8],
    private_key: &[u8],
    nonce: &[u8],
) -> PyResult<Vec<u8>> {
    let private_key = lighter::private_key_from_bytes(private_key).map_err(to_py_value_error)?;
    let nonce =
        lighter::scalar_from_bytes(nonce, "Lighter nonce scalar").map_err(to_py_value_error)?;
    lighter::schnorr_sign_with_nonce(message_hash, &private_key, &nonce)
        .map(|value| value.to_vec())
        .map_err(to_py_value_error)
}

#[pyfunction]
fn lighter_sign_transaction(
    values: Vec<i128>,
    attributes: Vec<(u64, u64)>,
    payload_json: Vec<u8>,
    private_key: Vec<u8>,
    nonce: Vec<u8>,
) -> PyResult<(Py<PyBytes>, Py<PyBytes>)> {
    let (payload, message_hash) = lighter::sign_transaction_payload(
        &values,
        &attributes,
        &payload_json,
        &private_key,
        &nonce,
    )
    .map_err(to_py_value_error)?;
    Python::with_gil(|py| {
        Ok((
            PyBytes::new(py, &payload).unbind(),
            PyBytes::new(py, &message_hash).unbind(),
        ))
    })
}

#[pyfunction]
fn lighter_auth_token(
    expiry: u64,
    account_index: u64,
    api_key_index: u64,
    private_key: Vec<u8>,
    nonce: Vec<u8>,
) -> PyResult<String> {
    lighter::auth_token(expiry, account_index, api_key_index, &private_key, &nonce)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn exchange_names() -> Vec<String> {
    common::exchange_names()
        .into_iter()
        .map(str::to_string)
        .collect()
}

#[pyfunction]
fn order_side_parse(value: &str) -> PyResult<String> {
    OrderSide::parse(value)
        .map(|side| {
            if side.is_buy() {
                "BUY".to_string()
            } else {
                "SELL".to_string()
            }
        })
        .map_err(to_py_value_error)
}

#[pyfunction]
fn order_side_to_exchange(side: &str, exchange: &str) -> PyResult<String> {
    OrderSide::parse(side)
        .and_then(|side| side.to_exchange(exchange).map(str::to_string))
        .map_err(to_py_value_error)
}

#[pyfunction]
fn order_side_is_buy(side: &str) -> PyResult<bool> {
    OrderSide::parse(side)
        .map(OrderSide::is_buy)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn generate_timestamp_ms() -> PyResult<u64> {
    common::generate_timestamp_ms().map_err(to_py_runtime_error)
}

#[pyfunction]
fn generate_timestamp_iso() -> PyResult<String> {
    common::generate_timestamp_iso().map_err(to_py_runtime_error)
}

#[pyfunction]
fn get_decimal_places(value: f64) -> PyResult<u32> {
    common::get_decimal_places(value).map_err(to_py_value_error)
}

#[pyfunction]
fn reverse_decimal_places(decimal_places: i32) -> f64 {
    common::reverse_decimal_places(decimal_places)
}

#[pyfunction]
fn bybit_convert_timeframe(timeframe: &str) -> PyResult<String> {
    common::bybit_convert_timeframe(timeframe)
        .map(str::to_string)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn bitmart_convert_timeframe(timeframe: &str) -> PyResult<u32> {
    common::bitmart_convert_timeframe(timeframe).map_err(to_py_value_error)
}

#[pyfunction]
fn kucoin_convert_timeframe(timeframe: &str) -> PyResult<String> {
    common::kucoin_convert_timeframe(timeframe)
        .map(str::to_string)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn address_to_bytes(address: &str) -> PyResult<Py<PyBytes>> {
    let bytes = common::address_to_bytes(address).map_err(to_py_value_error)?;
    Python::with_gil(|py| Ok(PyBytes::new(py, &bytes).unbind()))
}

#[pyfunction]
fn sanitize_url(url: &str) -> String {
    common::sanitize_url(url)
}

#[pyfunction]
fn sanitize_message(message: &str) -> String {
    common::sanitize_message(message)
}

#[pyfunction]
fn sanitize_request(request: &str) -> String {
    common::sanitize_request(request)
}

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonAsterHttpClient>()?;
    m.add_class::<PythonBackpackHttpClient>()?;
    m.add_class::<PythonBinanceHttpClient>()?;
    m.add_class::<PythonBingxHttpClient>()?;
    m.add_class::<PythonBitgetHttpClient>()?;
    m.add_class::<PythonBitmartHttpClient>()?;
    m.add_class::<PythonBitmexHttpClient>()?;
    m.add_class::<PythonBybitHttpClient>()?;
    m.add_class::<PythonGateioHttpClient>()?;
    m.add_class::<PythonHyperliquidHttpClient>()?;
    m.add_class::<PythonHttpClient>()?;
    m.add_class::<PythonKrakenHttpClient>()?;
    m.add_class::<PythonKucoinHttpClient>()?;
    m.add_class::<PythonLighterHttpClient>()?;
    m.add_class::<PythonMexcHttpClient>()?;
    m.add_class::<PythonOkxHttpClient>()?;
    m.add_class::<PythonProductTable>()?;
    m.add_function(wrap_pyfunction!(lighter_poseidon_hash_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_public_key_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_schnorr_sign, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_sign_transaction, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_auth_token, m)?)?;
    m.add_function(wrap_pyfunction!(exchange_names, m)?)?;
    m.add_function(wrap_pyfunction!(order_side_parse, m)?)?;
    m.add_function(wrap_pyfunction!(order_side_to_exchange, m)?)?;
    m.add_function(wrap_pyfunction!(order_side_is_buy, m)?)?;
    m.add_function(wrap_pyfunction!(generate_timestamp_ms, m)?)?;
    m.add_function(wrap_pyfunction!(generate_timestamp_iso, m)?)?;
    m.add_function(wrap_pyfunction!(get_decimal_places, m)?)?;
    m.add_function(wrap_pyfunction!(reverse_decimal_places, m)?)?;
    m.add_function(wrap_pyfunction!(bybit_convert_timeframe, m)?)?;
    m.add_function(wrap_pyfunction!(bitmart_convert_timeframe, m)?)?;
    m.add_function(wrap_pyfunction!(kucoin_convert_timeframe, m)?)?;
    m.add_function(wrap_pyfunction!(address_to_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_url, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_message, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_request, m)?)?;
    m.add_function(wrap_pyfunction!(fetch_product_table, m)?)?;
    m.add_function(wrap_pyfunction!(fetch_product_table_async, m)?)?;
    Ok(())
}
