use super::helpers::*;

#[test]
fn spot_signature_matches_python_vector() {
    assert_eq!(
        spot_signature(
            "/0/private/Balance",
            NONCE,
            "nonce=1700000000000000000&asset=BTC+USD",
            SECRET,
        )
        .expect("signature"),
        "WEQePGAjbQaKqtYh0z8ylm5D/0D60D6FAQXlHzu7dDclIHTnRqYoAijaRpRtwLIoj4hnPnEPFO2nXwS+c+BhPQ=="
    );
}

#[test]
fn futures_signature_matches_python_vector() {
    assert_eq!(
        futures_signature(
            "/derivatives/api/v3/sendorder",
            "symbol=PI_XBTUSD&side=buy",
            NONCE,
            SECRET,
        )
        .expect("signature"),
        "W2YL8mj+KExVX/X6fTAPvwlPPo6EP14ISry2Bv5BfJsBu4tDy6PUc1nVNu3OKXcJXrliaG19axFphls37F14zQ=="
    );
}

#[test]
fn spot_account_id_is_a_signed_query_parameter() {
    let client = KrakenClient::new(
        Some("key".into()),
        Some(SECRET.into()),
        None,
        None,
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            crate::http::HttpMethod::Post,
            super::super::client::KrakenAuth::Spot,
            "/0/private/Balance",
            vec![
                ("account_id".into(), "WX6V-JUKW-KKPB-QE36".into()),
                ("rebase_multiplier".into(), "base".into()),
            ],
            None,
            true,
            NONCE,
        )
        .expect("request");
    // The official SDK signs the request URI, query included; account_id stays out of the body.
    let path = "/0/private/Balance?account_id=WX6V-JUKW-KKPB-QE36";
    let body = format!("nonce={NONCE}&rebase_multiplier=base");
    assert_eq!(request.path, path);
    assert!(matches!(&request.body, crate::http::RequestBody::Raw(raw) if raw == body.as_bytes()));
    assert_eq!(
        request.headers.get("API-Sign").map(String::as_str),
        Some(
            spot_signature(path, NONCE, &body, SECRET)
                .expect("signature")
                .as_str()
        )
    );
    let empty = client.build_request(
        crate::http::HttpMethod::Post,
        super::super::client::KrakenAuth::Spot,
        "/0/private/Balance",
        vec![("account_id".into(), " ".into())],
        None,
        true,
        NONCE,
    );
    assert!(
        empty.is_err(),
        "an empty wallet selector never reaches the wire"
    );
}
