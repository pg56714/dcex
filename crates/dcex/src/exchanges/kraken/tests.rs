use super::signing::{encode_params, futures_signature, spot_signature};

const SECRET: &str = "c2VjcmV0";
const NONCE: &str = "1700000000000000000";

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
fn query_encoding_uses_uri_percent_encoding() {
    assert_eq!(
        encode_params(&[("greeting".to_string(), "hello world".to_string())]),
        "greeting=hello%20world"
    );
}
