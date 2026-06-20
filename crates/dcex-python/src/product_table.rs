use super::*;
use std::io::{BufWriter, Write};

use pyo3::exceptions::{PyIndexError, PyTypeError};
use pyo3::types::{PyAny, PyDict};

const PRODUCT_TABLE_COLUMNS: [&str; 12] = [
    "exchange",
    "exchange_symbol",
    "product_symbol",
    "product_type",
    "exchange_type",
    "price_precision",
    "size_precision",
    "min_size",
    "base_currency",
    "quote_currency",
    "min_notional",
    "size_per_contract",
];

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

fn market_info_to_map(row: &MarketInfo) -> BTreeMap<String, String> {
    BTreeMap::from([
        ("exchange".to_string(), row.exchange.clone()),
        ("exchange_symbol".to_string(), row.exchange_symbol.clone()),
        ("product_symbol".to_string(), row.product_symbol.clone()),
        ("product_type".to_string(), row.product_type.clone()),
        ("exchange_type".to_string(), row.exchange_type.clone()),
        ("price_precision".to_string(), row.price_precision.clone()),
        ("size_precision".to_string(), row.size_precision.clone()),
        ("min_size".to_string(), row.min_size.clone()),
        ("base_currency".to_string(), row.base_currency.clone()),
        ("quote_currency".to_string(), row.quote_currency.clone()),
        ("min_notional".to_string(), row.min_notional.clone()),
        (
            "size_per_contract".to_string(),
            row.size_per_contract.clone(),
        ),
    ])
}

fn market_rows_to_maps(rows: &[MarketInfo]) -> Vec<BTreeMap<String, String>> {
    rows.iter().map(market_info_to_map).collect()
}

fn market_info_field<'a>(row: &'a MarketInfo, key: &str) -> Option<&'a str> {
    match key {
        "exchange" => Some(&row.exchange),
        "exchange_symbol" => Some(&row.exchange_symbol),
        "product_symbol" => Some(&row.product_symbol),
        "product_type" => Some(&row.product_type),
        "exchange_type" => Some(&row.exchange_type),
        "price_precision" => Some(&row.price_precision),
        "size_precision" => Some(&row.size_precision),
        "min_size" => Some(&row.min_size),
        "base_currency" => Some(&row.base_currency),
        "quote_currency" => Some(&row.quote_currency),
        "min_notional" => Some(&row.min_notional),
        "size_per_contract" => Some(&row.size_per_contract),
        _ => None,
    }
}

fn write_csv_field(writer: &mut impl Write, value: &str) -> std::io::Result<()> {
    let needs_quotes = value.contains([',', '"', '\n', '\r']);
    if needs_quotes {
        writer.write_all(b"\"")?;
        for character in value.chars() {
            if character == '"' {
                writer.write_all(b"\"\"")?;
            } else {
                let mut buffer = [0; 4];
                writer.write_all(character.encode_utf8(&mut buffer).as_bytes())?;
            }
        }
        writer.write_all(b"\"")?;
    } else {
        writer.write_all(value.as_bytes())?;
    }
    Ok(())
}

fn write_csv_record(writer: &mut impl Write, values: &[&str]) -> std::io::Result<()> {
    for (index, value) in values.iter().enumerate() {
        if index > 0 {
            writer.write_all(b",")?;
        }
        write_csv_field(writer, value)?;
    }
    writer.write_all(b"\n")?;
    Ok(())
}

#[pyclass(name = "ProductColumn")]
pub(crate) struct PythonProductColumn {
    values: Vec<String>,
}

#[pymethods]
impl PythonProductColumn {
    fn to_list(&self) -> Vec<String> {
        self.values.clone()
    }
}

#[pyclass(name = "ProductTable")]
pub(crate) struct PythonProductTable {
    pub(crate) table: ProductTable,
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
        market_rows_to_maps(self.table.rows())
    }

    fn to_dicts(&self) -> Vec<BTreeMap<String, String>> {
        self.rows()
    }

    #[getter]
    fn height(&self) -> usize {
        self.table.rows().len()
    }

    fn __len__(&self) -> usize {
        self.table.rows().len()
    }

    fn __getitem__<'py>(&self, py: Python<'py>, item: &Bound<'py, PyAny>) -> PyResult<Py<PyAny>> {
        if let Ok(key) = item.extract::<String>() {
            let values = column_values(&self.table, &key)?;
            return Ok(Py::new(py, PythonProductColumn { values })?.into_any());
        }

        if let Ok(index) = item.extract::<isize>() {
            let index = normalize_index(index, self.table.rows().len())?;
            let dict = PyDict::new(py);
            for (key, value) in market_info_to_map(&self.table.rows()[index]) {
                dict.set_item(key, value)?;
            }
            return Ok(dict.into_any().unbind());
        }

        Err(PyTypeError::new_err(
            "ProductTable indices must be integers or strings.",
        ))
    }

    fn write_csv(&self, path: &Bound<'_, PyAny>) -> PyResult<()> {
        let path = path.str()?.to_string();
        let file = std::fs::File::create(path).map_err(|error| {
            PyRuntimeError::new_err(format!("failed to create product table CSV: {error}"))
        })?;
        let mut writer = BufWriter::new(file);
        write_csv_record(&mut writer, &PRODUCT_TABLE_COLUMNS).map_err(|error| {
            PyRuntimeError::new_err(format!("failed to write product table CSV: {error}"))
        })?;
        for row in self.table.rows() {
            let values = PRODUCT_TABLE_COLUMNS
                .iter()
                .map(|key| market_info_field(row, key).unwrap_or_default())
                .collect::<Vec<_>>();
            write_csv_record(&mut writer, &values).map_err(|error| {
                PyRuntimeError::new_err(format!("failed to write product table CSV: {error}"))
            })?;
        }
        writer.flush().map_err(|error| {
            PyRuntimeError::new_err(format!("failed to flush product table CSV: {error}"))
        })?;
        Ok(())
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

fn column_values(table: &ProductTable, key: &str) -> PyResult<Vec<String>> {
    table
        .rows()
        .iter()
        .map(|row| {
            market_info_field(row, key)
                .map(str::to_string)
                .ok_or_else(|| PyValueError::new_err(format!("Key not found: {key}")))
        })
        .collect()
}

fn normalize_index(index: isize, len: usize) -> PyResult<usize> {
    let normalized = if index < 0 {
        len as isize + index
    } else {
        index
    };
    if normalized < 0 || normalized >= len as isize {
        return Err(PyIndexError::new_err("ProductTable index out of range."));
    }
    Ok(normalized as usize)
}

#[pyfunction]
#[pyo3(signature = (exchange_name=None, timeout=10.0))]
fn fetch_product_table(
    py: Python<'_>,
    exchange_name: Option<&str>,
    timeout: f64,
) -> PyResult<PythonProductTable> {
    if !timeout.is_finite() || timeout <= 0.0 {
        return Err(PyValueError::new_err(
            "HTTP timeout must be a positive finite number.",
        ));
    }
    let exchange = exchange_name.map(exchange_from_name).transpose()?;
    py.allow_threads(|| {
        block_on(
            async move { ProductTable::fetch(exchange, Duration::from_secs_f64(timeout)).await },
        )
    })
    .map(|table| PythonProductTable { table })
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
            .map(|table| PythonProductTable { table })
            .map_err(to_py_runtime_error)
    })
}
pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PythonProductColumn>()?;
    m.add_class::<PythonProductTable>()?;
    m.add_function(wrap_pyfunction!(fetch_product_table, m)?)?;
    m.add_function(wrap_pyfunction!(fetch_product_table_async, m)?)?;
    Ok(())
}
