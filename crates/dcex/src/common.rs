//! Compatibility exports for shared utility functions.
pub use crate::address::address_to_bytes;
pub(crate) use crate::decimal::is_positive_plain_decimal;
pub use crate::decimal::{get_decimal_places, reverse_decimal_places};
pub use crate::exchange::exchange_names;
pub use crate::order_side::OrderSide;
pub use crate::sanitization::{sanitize_message, sanitize_request, sanitize_url};
pub use crate::time::{format_timestamp_iso, generate_timestamp_iso, generate_timestamp_ms};
pub use crate::timeframe::{bybit_convert_timeframe, kucoin_convert_timeframe};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn order_side_matches_python_mapping() {
        assert_eq!(
            OrderSide::parse(" buy ")
                .expect("side")
                .to_exchange("bybit")
                .expect("mapping"),
            "Buy"
        );
        assert!(OrderSide::Sell.to_exchange("hyperliquid").is_err());
    }

    #[test]
    fn decimal_helpers_match_python_behavior() {
        assert_eq!(get_decimal_places(0.001).expect("places"), 3);
        assert_eq!(get_decimal_places(1e-7).expect("places"), 7);
        assert_eq!(get_decimal_places(1.0).expect("places"), 0);
        assert_eq!(reverse_decimal_places(3), 0.001);
    }

    #[test]
    fn timestamp_format_matches_python_iso_shape() {
        assert_eq!(format_timestamp_iso(0), "1970-01-01T00:00:00.000Z");
        assert_eq!(
            format_timestamp_iso(1_700_000_000_123),
            "2023-11-14T22:13:20.123Z"
        );
    }

    #[test]
    fn request_sanitization_removes_credentials() {
        assert_eq!(
            sanitize_request(
                "POST https://user:password@api.example.com/order?signature=secret | Body: x"
            ),
            "POST https://api.example.com/order"
        );
        let message = sanitize_message(
            "failed for https://api.example.com/order?signature=url-secret with api_key=private",
        );
        assert_eq!(
            message,
            "failed for https://api.example.com/order with <redacted>"
        );
    }
}
