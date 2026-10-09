use super::helpers::*;

#[tokio::test]
async fn unknown_dispatch_names_are_rejected_without_network() {
    let client = BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client");
    let error = client
        .public_request("get_not_a_bybit_endpoint", Vec::new())
        .await
        .expect_err("public");
    assert!(
        error
            .to_string()
            .contains("unsupported Bybit public method")
    );
    let error = client
        .private_request("get_not_a_bybit_endpoint", Vec::new())
        .await
        .expect_err("private");
    assert!(
        error
            .to_string()
            .contains("unsupported Bybit private method")
    );
}

#[tokio::test]
async fn strategies_reject_inconsistent_fields_before_network() {
    let client = client("http://127.0.0.1:9".to_string());
    const TWAP: &[(&str, &str)] = &[
        ("category", "UTA_USDT"),
        ("product_symbol", "BTC-USDT-SWAP"),
        ("side", "Buy"),
        ("strategyType", "twap"),
        ("size", "1"),
        ("duration", "600"),
    ];
    let pov_params = r#"{"mode":"TradedVolume","participationRate":"5","referenceWindow":"60"}"#;
    let pov: Vec<(&str, &str)> = vec![
        ("category", "UTA_USDT"),
        ("symbol", "BTCUSDT"),
        ("side", "Buy"),
        ("strategyType", "pov"),
        ("size", "1"),
        ("povParams", pov_params),
    ];
    let with = |base: &[(&'static str, &'static str)], extra: &[(&'static str, &'static str)]| {
        let mut params: Vec<(&str, &str)> = base
            .iter()
            .filter(|(key, _)| extra.iter().all(|(other, _)| other != key))
            .copied()
            .collect();
        params.extend(extra.iter().filter(|(_, value)| !value.is_empty()));
        params
    };
    let pov_with = |extra: &[(&'static str, &'static str)]| {
        let mut params: Vec<(&str, &str)> = pov
            .iter()
            .filter(|(key, _)| extra.iter().all(|(other, _)| other != key))
            .copied()
            .collect();
        params.extend(extra.iter().filter(|(_, value)| !value.is_empty()));
        params
    };
    type Case<'a> = (&'a str, Vec<(&'a str, &'a str)>, &'a str);
    let cases: Vec<Case> = vec![
        (
            "create_strategy",
            with(TWAP, &[("symbol", "BTCUSDT")]),
            "provide only one symbol parameter",
        ),
        (
            "create_strategy",
            with(
                TWAP,
                &[
                    ("product_symbol", ""),
                    ("category", ""),
                    ("symbol", "BTCUSDT"),
                ],
            ),
            "category is required for native symbols",
        ),
        (
            "create_strategy",
            with(TWAP, &[("category", "UTA_SPOT")]),
            "category does not match",
        ),
        (
            "create_strategy",
            with(
                TWAP,
                &[("product_symbol", "BTC-EUR-SWAP"), ("category", "")],
            ),
            "unsupported strategy product symbol/category",
        ),
        (
            "create_strategy",
            with(TWAP, &[("maker_only", "true"), ("postOnly", "1")]),
            "mutually exclusive",
        ),
        (
            "create_strategy",
            with(TWAP, &[("maker_only", "yes")]),
            "maker_only must be boolean",
        ),
        (
            "create_strategy",
            with(TWAP, &[("chaseDistance", "1"), ("chasePercentE4", "1")]),
            "chaseDistance and chasePercentE4 are mutually exclusive",
        ),
        (
            "create_strategy",
            with(TWAP, &[("subSize", "1"), ("orderCount", "2")]),
            "subSize, subPositionValue and orderCount are mutually exclusive",
        ),
        (
            "create_strategy",
            with(TWAP, &[("positionValue", "10")]),
            "provide exactly one of size or positionValue",
        ),
        (
            "create_strategy",
            with(TWAP, &[("limitPrice", "0")]),
            "limitPrice must be positive",
        ),
        (
            "create_strategy",
            with(TWAP, &[("leverageType", "1")]),
            "leverageType is only supported for UTA_SPOT",
        ),
        (
            "create_strategy",
            with(TWAP, &[("duration", "610")]),
            "TWAP duration must be divisible",
        ),
        (
            "create_strategy",
            with(
                TWAP,
                &[("strategyType", "chaseOrder"), ("chasePercentE4", "900")],
            ),
            "chasePercentE4 must be 0..=500",
        ),
        (
            "create_strategy",
            with(TWAP, &[("strategyType", "iceberg"), ("duration", "")]),
            "iceberg requires subSize, subPositionValue or orderCount",
        ),
        (
            "create_strategy",
            with(
                TWAP,
                &[
                    ("strategyType", "iceberg"),
                    ("duration", ""),
                    ("orderCount", "300"),
                ],
            ),
            "orderCount must be 1..=200",
        ),
        (
            "create_strategy",
            pov_with(&[("interval", "x")]),
            "invalid interval",
        ),
        (
            "create_strategy",
            pov_with(&[("interval", "2")]),
            "POV interval must be 0 or 5..=3600",
        ),
        (
            "create_strategy",
            pov_with(&[("size", "")]),
            "POV requires a size, value, duration or one-time stop condition",
        ),
        (
            "create_strategy",
            pov_with(&[("povParams", "[]")]),
            "povParams must be an object",
        ),
        (
            "create_strategy",
            pov_with(&[(
                "povParams",
                r#"{"mode":"TradedVolume","participationRate":"5","x":1}"#,
            )]),
            "unsupported povParams field",
        ),
        (
            "create_strategy",
            pov_with(&[(
                "povParams",
                r#"{"mode":"TradedVolume","participationRate":5}"#,
            )]),
            "participationRate must be a decimal string",
        ),
        (
            "create_strategy",
            pov_with(&[(
                "povParams",
                r#"{"mode":"TradedVolume","participationRate":"5.25"}"#,
            )]),
            "at most one decimal",
        ),
        (
            "create_strategy",
            pov_with(&[(
                "povParams",
                r#"{"mode":"TradedVolume","participationRate":"5","referenceWindow":"30"}"#,
            )]),
            "referenceWindow must be a string integer",
        ),
        (
            "create_strategy",
            pov_with(&[(
                "povParams",
                r#"{"mode":"SameSideLiquidity","participationRate":"5","depthReference":11}"#,
            )]),
            "depthReference must be an integer from 1 to 10",
        ),
        (
            "create_strategy",
            pov_with(&[("povParams", r#"{"mode":"Volume","participationRate":"5"}"#)]),
            "unsupported POV mode",
        ),
        (
            "create_strategy",
            pov_with(&[("limitPrice", "1")]),
            "unsupported strategy parameter: limitPrice",
        ),
        (
            "create_strategy",
            with(TWAP, &[("side", " ")]),
            "strategy parameters must not be empty",
        ),
        (
            "get_strategy_list",
            vec![("strategyType", "grid")],
            "unsupported strategyType",
        ),
        (
            "get_strategy_list",
            vec![("category", "UTA_OPTION")],
            "unsupported category",
        ),
        (
            "get_strategy_orders",
            vec![("strategyId", "s1"), ("status", "1")],
            "unsupported status",
        ),
        (
            "get_strategy_list",
            vec![("beginTimeE0", "5"), ("endTimeE0", "4")],
            "beginTimeE0 must not exceed endTimeE0",
        ),
    ];
    for (method, params, expected) in cases {
        let params = params
            .into_iter()
            .map(|(key, value)| (key.to_string(), value.to_string()))
            .collect();
        let error = client
            .private_request(method, params)
            .await
            .expect_err(expected)
            .to_string();
        assert!(error.contains(expected), "{method} {expected}: {error}");
    }
}

/// Answers every request with a Bybit success envelope (or `time_body` for the server
/// time endpoint) and records each request.
fn recording_server(
    time_body: &'static str,
) -> (String, std::sync::Arc<std::sync::Mutex<Vec<String>>>) {
    let listener = std::net::TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let seen = std::sync::Arc::new(std::sync::Mutex::new(Vec::new()));
    let log = seen.clone();
    thread::spawn(move || {
        for stream in listener.incoming() {
            let Ok(mut stream) = stream else { break };
            let mut request = Vec::new();
            let mut buffer = [0u8; 8192];
            loop {
                let Ok(size) = stream.read(&mut buffer) else {
                    break;
                };
                if size == 0 {
                    break;
                }
                request.extend_from_slice(&buffer[..size]);
                let text = String::from_utf8_lossy(&request);
                if let Some((head, body)) = text.split_once("\r\n\r\n") {
                    let length = head
                        .lines()
                        .find_map(|line| {
                            line.to_ascii_lowercase()
                                .strip_prefix("content-length:")
                                .and_then(|value| value.trim().parse::<usize>().ok())
                        })
                        .unwrap_or(0);
                    if body.len() >= length {
                        break;
                    }
                }
            }
            let text = String::from_utf8_lossy(&request).into_owned();
            let body = if text.starts_with("GET /v5/market/time") {
                time_body
            } else {
                r#"{"retCode":0,"retMsg":"OK","result":{}}"#
            };
            log.lock().unwrap().push(text);
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                body.len()
            );
            let _ = stream.write_all(response.as_bytes());
        }
    });
    (url, seen)
}

fn market(
    product_symbol: &str,
    exchange_symbol: &str,
    exchange_type: &str,
    product_type: &str,
    quote: &str,
) -> crate::product_table::MarketInfo {
    crate::product_table::MarketInfo {
        exchange: "bybit".into(),
        exchange_symbol: exchange_symbol.into(),
        product_symbol: product_symbol.into(),
        product_type: product_type.into(),
        exchange_type: exchange_type.into(),
        quote_currency: quote.into(),
        base_currency: "BTC".into(),
        ..Default::default()
    }
}

#[tokio::test]
async fn loaded_tables_map_strategy_and_batch_symbols_to_native_markets() {
    let (url, seen) = recording_server("{}");
    let client = client(url).with_product_table(crate::product_table::ProductTable::new(vec![
        market("BTC-USDT-SPOT", "BTCUSDT", "spot", "spot", "USDT"),
        market("BTC-USDT-SWAP", "BTCUSDT", "linear", "swap", "USDT"),
        market("BTC-USDC-SWAP", "BTCPERP", "linear", "swap", "USDC"),
        market("BTC-USD-SWAP", "BTCUSD", "inverse", "swap", "USD"),
        market(
            "BTC-USD-260327-FUTURES",
            "BTCUSDH26",
            "inverse",
            "futures",
            "USD",
        ),
        market(
            "BTC-USDT-260327-FUTURES",
            "BTC-27MAR26",
            "linear",
            "futures",
            "USDT",
        ),
        market(
            "BTC-USDT-260327-C-1-OPTION",
            "BTC-27MAR26-1-C",
            "option",
            "option",
            "USDT",
        ),
    ]));
    for (product_symbol, native, category) in [
        ("BTC-USDT-SPOT", "BTCUSDT", "UTA_SPOT"),
        ("BTC-USDT-SWAP", "BTCUSDT", "UTA_USDT"),
        ("BTC-USDC-SWAP", "BTCPERP", "UTA_USDC"),
        ("BTC-USD-SWAP", "BTCUSD", "UTA_INVERSE"),
        ("BTC-USD-260327-FUTURES", "BTCUSDH26", "UTA_INVERSE_FUTURE"),
        ("BTC-USDT-260327-FUTURES", "BTC-27MAR26", "UTA_USDT_FUTURE"),
    ] {
        let params = [
            ("product_symbol", product_symbol),
            ("side", "Buy"),
            ("strategyType", "twap"),
            ("size", "1"),
            ("duration", "600"),
        ]
        .iter()
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect();
        client
            .private_request("create_strategy", params)
            .await
            .expect(product_symbol);
        let request = seen.lock().unwrap().pop().unwrap();
        let body: serde_json::Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).unwrap()).unwrap();
        assert_eq!(body["symbol"], native, "{product_symbol}");
        assert_eq!(body["category"], category, "{product_symbol}");
    }
    let orders = serde_json::json!([
        {"symbol": "BTC-USDT-SWAP", "side": "Buy", "orderType": "Market", "qty": "1"},
        {"symbol": "BTCUSDT", "side": "Sell", "orderType": "Market", "qty": "1"},
    ]);
    client
        .private_request(
            "place_batch_order",
            vec![
                ("category".into(), "linear".into()),
                ("request".into(), orders.to_string()),
            ],
        )
        .await
        .expect("batch");
    let request = seen.lock().unwrap().pop().unwrap();
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).unwrap()).unwrap();
    assert_eq!(body["request"][0]["symbol"], "BTCUSDT");
    assert_eq!(body["request"][1]["symbol"], "BTCUSDT");
}

#[tokio::test]
async fn signed_requests_use_the_server_clock_once_when_syncing() {
    let ahead_ms = (std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64
        + 3_600_000)
        .to_string();
    let time_body: &'static str = Box::leak(
        format!(r#"{{"retCode":0,"retMsg":"OK","result":{{"timeSecond":"0","timeNano":"{ahead_ms}000000"}}}}"#)
            .into_boxed_str(),
    );
    let (url, seen) = recording_server(time_body);
    let client = BybitClient::with_base_url(
        Some("api-key".to_string()),
        Some("api-secret".to_string()),
        5_000,
        true,
        Duration::from_secs(10),
        url,
    )
    .expect("client");
    for _ in 0..2 {
        client
            .private_request(
                "get_wallet_balance",
                vec![("accountType".into(), "UNIFIED".into())],
            )
            .await
            .expect("wallet balance");
    }
    let requests = seen.lock().unwrap().clone();
    assert_eq!(
        requests
            .iter()
            .filter(|request| request.starts_with("GET /v5/market/time"))
            .count(),
        1,
        "{requests:?}"
    );
    let timestamp: u64 = requests
        .last()
        .unwrap()
        .lines()
        .find_map(|line| {
            line.to_ascii_lowercase()
                .strip_prefix("x-bapi-timestamp:")
                .map(|v| v.trim().to_string())
        })
        .unwrap()
        .parse()
        .unwrap();
    assert!(
        timestamp >= ahead_ms.parse::<u64>().unwrap() - 60_000,
        "{timestamp}"
    );
}
