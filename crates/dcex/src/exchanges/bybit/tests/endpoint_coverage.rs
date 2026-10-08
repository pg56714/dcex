use super::helpers::*;

#[tokio::test]
async fn every_dispatch_name_hits_its_official_route() {
    let mut failures = Vec::new();
    for case in CASES {
        let (address, handle) = single_shot_server();
        let client = client(format!("http://{address}"));
        let result = if case.public {
            client.public_request(case.name, params(case)).await
        } else {
            client.private_request(case.name, params(case)).await
        };
        if let Err(error) = result {
            // The request never reached the server; connect once so the
            // server thread returns from `accept` and can be joined.
            drop(TcpStream::connect(address));
            let _ = handle.join();
            failures.push(format!("{}: request failed: {error}", case.name));
            continue;
        }
        let request = handle.join().expect("server");
        let request_line = request.lines().next().unwrap_or_default();
        let target = request_line.split(' ').nth(1).unwrap_or_default();
        let path = target.split('?').next().unwrap_or_default();
        let verb = request_line.split(' ').next().unwrap_or_default();
        if (verb, path) != (case.verb, case.path) {
            failures.push(format!(
                "{}: expected {} {}, got {verb} {path}",
                case.name, case.verb, case.path
            ));
        }
        let signed = request.to_ascii_lowercase().contains("\r\nx-bapi-sign:");
        if signed == case.public {
            failures.push(format!(
                "{}: expected signed={}, got signed={signed}",
                case.name, !case.public
            ));
        }
        if verb == "GET" && !request.ends_with("\r\n\r\n") {
            failures.push(format!("{}: GET request carried a body", case.name));
        }
    }
    assert!(failures.is_empty(), "{failures:#?}");
}

#[test]
fn every_endpoint_constant_has_a_route_case() {
    let source = [
        include_str!("../endpoints.rs"),
        include_str!("../schemas/table_account.json"),
        include_str!("../schemas/table_announcements.json"),
        include_str!("../schemas/table_api_keys.json"),
        include_str!("../schemas/table_convert.json"),
        include_str!("../schemas/table_leveraged_tokens.json"),
        include_str!("../schemas/table_loan.json"),
        include_str!("../schemas/table_margin.json"),
        include_str!("../schemas/table_market.json"),
        include_str!("../schemas/table_options.json"),
        include_str!("../schemas/table_portfolio_margin.json"),
        include_str!("../schemas/table_subaccount.json"),
        include_str!("../schemas/table_trading.json"),
        include_str!("../schemas/table_travel_rule.json"),
        include_str!("../schemas/table_wallet.json"),
        include_str!("../schemas/table_withdrawals.json"),
        include_str!("../strategy.rs"),
        include_str!("../market.rs"),
        include_str!("../account.rs"),
    ]
    .join("\n");
    let constants: BTreeSet<&str> = source
        .split('"')
        .filter(|segment| segment.starts_with("/v5/"))
        .collect();
    let covered: BTreeSet<&str> = CASES.iter().map(|case| case.path).collect();
    let missing: Vec<&&str> = constants
        .iter()
        .filter(|path| **path != "/v5/market/time" && !covered.contains(**path))
        .collect();
    assert!(
        missing.is_empty(),
        "endpoint constants without a route case: {missing:#?}"
    );
    let unknown: Vec<&&str> = covered
        .iter()
        .filter(|path| !constants.contains(**path))
        .collect();
    assert!(
        unknown.is_empty(),
        "route cases for unknown paths: {unknown:#?}"
    );
}

#[test]
fn route_case_names_are_unique() {
    let mut seen = BTreeSet::new();
    for case in CASES {
        assert!(seen.insert(case.name), "duplicate case {}", case.name);
    }
}

#[tokio::test]
async fn every_typed_wrapper_reaches_dispatch() {
    // The typed Rust methods must reach the same dispatch Python calls by name.
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = client(url.clone());
    crate::exchanges::wrapper_dispatch::assert_dispatch(
        "bybit",
        "BybitClient",
        |name, public, params| {
            let client = &client;
            async move {
                if public {
                    client.public_request(name, params).await
                } else {
                    client.private_request(name, params).await
                }
            }
        },
    )
    .await;
}
