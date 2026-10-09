//! Constraints from the official Arcus OpenAPI request tables.
use crate::Result;
use crate::exchanges::arcus::params::invalid;
use std::collections::BTreeMap;
struct Field {
    name: &'static str,
    required: bool,
    integer: bool,
    minimum: u64,
    maximum: u64,
    choices: &'static [&'static str],
    csv: bool,
}
pub(super) fn validate(name: &str, params: &BTreeMap<String, String>) -> Result<()> {
    // Official query and path fields for routes without range constraints; path segments
    // use the library names `market` and `order_id`.
    let names_only: Option<&[&str]> = match name {
        "get_markets" => Some(&["market"]),
        "get_spot_assets" | "get_fee_tiers" => Some(&[]),
        "get_account" => Some(&["address", "accountIndex"]),
        "get_bbo" => Some(&["market"]),
        "get_l2_orderbook" => Some(&["market", "nLevels", "sigFigs", "roundStep"]),
        "get_positions" | "get_leverages" => Some(&["address", "accountIndex", "market"]),
        "get_open_orders" => Some(&[
            "address",
            "accountIndex",
            "market",
            "status",
            "limit",
            "from",
            "to",
        ]),
        "get_order_status" => Some(&["order_id", "address", "accountIndex"]),
        "get_fills" => Some(&[
            "address",
            "accountIndex",
            "market",
            "role",
            "side",
            "limit",
            "from",
            "to",
        ]),
        "get_transfer_updates" => Some(&["address", "accountIndex", "limit", "from", "to"]),
        _ => None,
    };
    if let Some(allowed) = names_only {
        if let Some(key) = params.keys().find(|key| !allowed.contains(&key.as_str())) {
            return Err(invalid(format!("unsupported {name} field: {key}")));
        }
        return Ok(());
    }
    let fields: &[Field] = match name {
        "get_trade" => &[
            Field {
                name: "trade_id",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "market",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
        ],
        "get_account_stats" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "include",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &["feeTier", "volumes"],
                csv: true,
            },
            Field {
                name: "windows",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &["24h", "7d", "30d"],
                csv: true,
            },
        ],
        "get_mid_prices" => &[Field {
            name: "market",
            required: false,
            integer: false,
            minimum: 0,
            maximum: 9223372036854775807,
            choices: &[],
            csv: false,
        }],
        "get_compliance" => &[Field {
            name: "address",
            required: false,
            integer: false,
            minimum: 0,
            maximum: 9223372036854775807,
            choices: &[],
            csv: false,
        }],
        "get_rate_limit" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
        ],
        "get_time" => &[],
        "get_fill" => &[
            Field {
                name: "trade_id",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
        ],
        "get_funding" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
            Field {
                name: "market",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "to",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1000,
                choices: &[],
                csv: false,
            },
        ],
        "get_interest" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "to",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1000,
                choices: &[],
                csv: false,
            },
        ],
        "get_live_prices" => &[Field {
            name: "market",
            required: false,
            integer: false,
            minimum: 0,
            maximum: 9223372036854775807,
            choices: &[],
            csv: false,
        }],
        "get_funding_rates" => &[
            Field {
                name: "market",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "to",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1000,
                choices: &[],
                csv: false,
            },
        ],
        "get_candles" => &[
            Field {
                name: "market",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "timeframe",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[
                    "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d", "3d", "1w",
                ],
                csv: false,
            },
            Field {
                name: "to",
                required: true,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "countback",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1500,
                choices: &[],
                csv: false,
            },
        ],
        "get_order_history" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
            Field {
                name: "market",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "side",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &["BUY", "SELL"],
                csv: false,
            },
            Field {
                name: "status",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[
                    "OPEN",
                    "UNTRIGGERED",
                    "FILLED",
                    "CANCELED",
                    "REJECTED",
                    "LIQUIDATED",
                    "ADL",
                ],
                csv: true,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1000,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "to",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
        ],
        "get_portfolio_history" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
        ],
        "get_trades" => &[
            Field {
                name: "market",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1000,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "to",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
        ],
        "get_spot_fills" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 1000,
                choices: &[],
                csv: false,
            },
            Field {
                name: "from",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "to",
                required: false,
                integer: true,
                minimum: 100000000000000,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
        ],
        "get_spot_positions" => &[
            Field {
                name: "address",
                required: true,
                integer: false,
                minimum: 0,
                maximum: 9223372036854775807,
                choices: &[],
                csv: false,
            },
            Field {
                name: "accountIndex",
                required: false,
                integer: true,
                minimum: 0,
                maximum: 9,
                choices: &[],
                csv: false,
            },
        ],
        "get_leaderboard" => &[
            Field {
                name: "window",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 0,
                choices: &["all", "30d", "24h"],
                csv: false,
            },
            Field {
                name: "sortBy",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 0,
                choices: &["volume", "pnl", "fees"],
                csv: false,
            },
            Field {
                name: "address",
                required: false,
                integer: false,
                minimum: 0,
                maximum: 0,
                choices: &[],
                csv: false,
            },
            Field {
                name: "limit",
                required: false,
                integer: true,
                minimum: 1,
                maximum: 100,
                choices: &[],
                csv: false,
            },
        ],
        "health" => &[],
        "get_service_info" => &[],
        _ => return Ok(()),
    };
    for key in params.keys() {
        if !fields.iter().any(|f| f.name == key) {
            return Err(invalid(format!("unsupported {name} field: {key}")));
        }
    }
    for field in fields {
        let Some(value) = params.get(field.name) else {
            if field.required {
                return Err(invalid(format!("{} is required", field.name)));
            }
            continue;
        };
        if value.trim().is_empty() {
            return Err(invalid(format!("{} must not be empty", field.name)));
        }
        if field.integer {
            let n = value
                .parse::<u64>()
                .map_err(|_| invalid(format!("{} must be an unsigned integer", field.name)))?;
            if !(field.minimum..=field.maximum).contains(&n) {
                return Err(invalid(format!(
                    "{} is outside the documented range",
                    field.name
                )));
            }
        }
        if !field.choices.is_empty() {
            let values = if field.csv {
                value.split(',').collect::<Vec<_>>()
            } else {
                vec![value.as_str()]
            };
            if values.iter().any(|v| {
                !field.choices.iter().any(|c| {
                    if ["side", "status"].contains(&field.name) {
                        c.eq_ignore_ascii_case(v)
                    } else {
                        c == v
                    }
                })
            }) {
                return Err(invalid(format!("invalid {}", field.name)));
            }
        }
    }
    if let Some(address) = params.get("address")
        && (address.len() != 42
            || !address.starts_with("0x")
            || !address[2..].bytes().all(|v| v.is_ascii_hexdigit()))
    {
        return Err(invalid("invalid wallet address"));
    }
    if let (Some(from), Some(to)) = (params.get("from"), params.get("to"))
        && from.parse::<u64>().ok() > to.parse::<u64>().ok()
    {
        return Err(invalid("from must not exceed to"));
    }
    if name == "get_candles" && params.contains_key("from") && params.contains_key("countback") {
        return Err(invalid("from and countback are mutually exclusive"));
    }
    if name == "get_fill"
        && params
            .get("trade_id")
            .is_some_and(|v| v.parse::<u64>().is_err())
    {
        return Err(invalid("fill trade_id must be an unsigned integer"));
    }
    Ok(())
}
