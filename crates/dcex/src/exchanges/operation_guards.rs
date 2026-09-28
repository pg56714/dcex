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
            "upgrade_to_uta"
                | "upgrade_classic_account"
                | "uta_delete_sub"
                | "set_uta_account_mode"
                | "set_futures_asset_mode"
                | "move_uta_positions"
                | "reverse_futures_position"
        ),
        "bingx" => matches!(method, "reverse_swap_position" | "set_swap_asset_mode"),
        "bybit" => matches!(method, "delete_api_key" | "modify_api_key"),
        "kucoin" => method == "set_uta_account_mode",
        "ondo" => method == "delete_api_key",
        "aster" => matches!(
            method,
            "exchange_futures_assets" | "trigger_futures_asset_exchange"
        ),
        _ => false,
    };
    if confirmed && !take_flag(&mut params, "confirm")? {
        return Err(invalid(method, "confirm=true is required"));
    }
    if exchange == "bybit" && method == "modify_api_key" && params.is_empty() {
        return Err(invalid(method, "at least one API key change is required"));
    }
    let scoped = match exchange {
        "bitget" => matches!(
            method,
            "close_futures_positions"
                | "close_uta_positions"
                | "cancel_futures_plan_orders"
                | "cancel_spot_plan_orders"
                | "classic_copytrading_future_copytrade_follower_close_positions"
                | "classic_copytrading_future_copytrade_trader_trader_order_close_positions"
        ),
        "bingx" => matches!(
            method,
            "close_coin_swap_all_positions" | "cancel_coin_swap_all_orders"
        ),
        "mexc" => method == "cancel_spot_all_orders",
        "kucoin" => matches!(
            method,
            "cancel_spot_stop_orders"
                | "cancel_futures_stop_orders"
                | "cancel_spot_oco_orders"
                | "cancel_margin_oco_orders"
        ),
        "backpack" => method == "cancel_open_strategies",
        _ => false,
    };
    if scoped {
        let all = take_flag(&mut params, "all_symbols")?;
        let symbol = params.iter().any(|(k, v)| {
            matches!(k.as_str(), "product_symbol" | "symbol") && !v.trim().is_empty()
        });
        let symbols = params
            .iter()
            .find(|(k, _)| k == "symbolList")
            .is_some_and(|(_, v)| {
                serde_json::from_str::<Vec<String>>(v).is_ok_and(|values| {
                    !values.is_empty() && values.iter().all(|v| !v.trim().is_empty())
                })
            });
        let ids = params.iter().any(|(k, v)| match k.as_str() {
            "trackingNo" => !v.trim().is_empty(),
            "orderIds" => !v.trim().is_empty() && v.split(',').all(|id| !id.trim().is_empty()),
            "orderIdList" => {
                serde_json::from_str::<Vec<serde_json::Value>>(v).is_ok_and(|values| {
                    !values.is_empty()
                        && values.iter().all(|item| {
                            ["orderId", "clientOid"].iter().any(|key| {
                                item.get(key)
                                    .and_then(serde_json::Value::as_str)
                                    .is_some_and(|id| !id.trim().is_empty())
                            })
                        })
                })
            }
            _ => false,
        });
        if all == (symbol || symbols || ids) {
            return Err(invalid(
                method,
                "provide a symbol, order IDs, or all_symbols=true, exclusively",
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
    fn order_ids_scope_cancellation_without_account_wide_permission() {
        for (exchange, method, key, ids) in [
            ("kucoin", "cancel_spot_stop_orders", "orderIds", "123,456"),
            ("kucoin", "cancel_spot_oco_orders", "orderIds", "123,456"),
            ("kucoin", "cancel_margin_oco_orders", "orderIds", "123,456"),
            (
                "bitget",
                "cancel_futures_plan_orders",
                "orderIdList",
                r#"[{"orderId":"123"}]"#,
            ),
        ] {
            for scope in [
                vec![(key.into(), ids.into())],
                vec![("product_symbol".into(), "BTC-USDT-SWAP".into())],
            ] {
                assert_eq!(validate(exchange, method, scope.clone()).unwrap(), scope);
                let mut conflicting = scope;
                conflicting.push(("all_symbols".into(), "true".into()));
                assert!(validate(exchange, method, conflicting).is_err());
            }
        }
    }

    #[test]
    fn local_flags_cannot_be_omitted_duplicated_or_sent_to_exchange() {
        for exchange in ["bybit", "ondo"] {
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
    fn an_empty_symbol_list_does_not_authorize_account_wide_cancellation() {
        for value in ["[]", "[\"\"]", "[\"   \"]", "null"] {
            assert!(
                validate(
                    "bitget",
                    "cancel_spot_plan_orders",
                    vec![("symbolList".into(), value.into())]
                )
                .is_err()
            );
        }
        let params = vec![("symbolList".into(), "[\"BTCUSDT\"]".into())];
        assert_eq!(
            validate("bitget", "cancel_spot_plan_orders", params.clone()).unwrap(),
            params
        );
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
