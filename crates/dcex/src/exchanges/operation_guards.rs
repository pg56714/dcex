//! Local consent flags are validated and removed before exchange serialization.
use crate::{DcexError, Result};

pub(super) fn validate(
    exchange: &str,
    method: &str,
    mut params: Vec<(String, String)>,
) -> Result<Vec<(String, String)>> {
    let confirmed = match exchange {
        "bitget" => matches!(
            method,
            "switch_to_classic_account"
                | "delete_uta_subaccount"
                | "set_uta_account_mode"
                | "move_uta_positions"
        ),
        "bingx" => matches!(method, "reverse_swap_position" | "set_swap_asset_mode"),
        "bybit" => matches!(method, "delete_api_key" | "modify_api_key"),
        "aster" => matches!(method, "trigger_futures_asset_exchange"),
        _ => false,
    };
    if confirmed && !take_flag(&mut params, "confirm")? {
        return Err(invalid(method, "confirm=true is required"));
    }
    if exchange == "bybit" && method == "modify_api_key" && params.is_empty() {
        return Err(invalid(method, "at least one API key change is required"));
    }
    let scoped = match exchange {
        "bitget" => method == "close_uta_positions",
        "bingx" => matches!(
            method,
            "close_coin_swap_all_positions" | "cancel_coin_swap_all_orders"
        ),
        "mexc" => method == "cancel_spot_all_orders",
        "backpack" => method == "cancel_open_strategies",
        "ondo" => method == "cancel_spot_orders",
        _ => false,
    };
    if scoped {
        let all = take_flag(&mut params, "all_symbols")?;
        let symbol = params.iter().any(|(k, v)| {
            matches!(k.as_str(), "product_symbol" | "symbol" | "market") && !v.trim().is_empty()
        });
        let symbols = params
            .iter()
            .find(|(k, _)| k == "symbolList")
            .is_some_and(|(_, v)| {
                serde_json::from_str::<Vec<String>>(v).is_ok_and(|values| {
                    !values.is_empty() && values.iter().all(|v| !v.trim().is_empty())
                })
            });
        if all == (symbol || symbols) {
            return Err(invalid(
                method,
                "provide a symbol or all_symbols=true, exclusively",
            ));
        }
    }
    if exchange == "backpack" && method == "vault_redeem" {
        let all = take_flag(&mut params, "all")?;
        let quantity = params
            .iter()
            .any(|(k, v)| k == "vaultTokenQuantity" && !v.trim().is_empty());
        if all == quantity {
            return Err(invalid(
                method,
                "provide vaultTokenQuantity or all=true, exclusively",
            ));
        }
    }
    Ok(params)
}

fn take_flag(params: &mut Vec<(String, String)>, flag: &str) -> Result<bool> {
    let values: Vec<_> = params
        .iter()
        .filter(|(key, _)| key == flag)
        .map(|(_, v)| v.as_str())
        .collect();
    let value = match values.as_slice() {
        [] | ["false"] => false,
        ["true"] => true,
        _ => return Err(invalid(flag, "must be a single boolean")),
    };
    params.retain(|(key, _)| key != flag);
    Ok(value)
}

fn invalid(method: &str, message: &str) -> DcexError {
    DcexError::InvalidInput(format!("{method}: {message}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn local_flags_cannot_be_omitted_duplicated_or_sent_to_exchange() {
        for exchange in ["bybit"] {
            assert!(validate(exchange, "delete_api_key", vec![]).is_err());
            for value in ["false", "1", "True", ""] {
                assert!(
                    validate(
                        exchange,
                        "delete_api_key",
                        vec![("confirm".into(), value.into())]
                    )
                    .is_err()
                );
            }
            let flag = ("confirm".into(), "true".into());
            assert!(
                validate(exchange, "delete_api_key", vec![flag.clone()])
                    .unwrap()
                    .is_empty()
            );
            assert!(validate(exchange, "delete_api_key", vec![flag.clone(), flag]).is_err());
        }
        assert!(
            validate(
                "bybit",
                "modify_api_key",
                vec![("confirm".into(), "true".into())]
            )
            .is_err()
        );
    }

    #[test]
    fn vault_redemption_requires_explicit_all_flag() {
        assert!(validate("backpack", "vault_redeem", vec![]).is_err());
        assert!(
            validate(
                "backpack",
                "vault_redeem",
                vec![("all".into(), "true".into())]
            )
            .unwrap()
            .is_empty()
        );
    }
}
