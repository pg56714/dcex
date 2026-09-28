//! Vault operations.
use crate::exchange::ValidatedResponse;
use crate::exchanges::backpack::{BackpackClient, params::BackpackParams};
use crate::http::HttpMethod;
use crate::{DcexError, Result};
use serde_json::{Map, Value};
struct Field {
    key: &'static str,
    kind: &'static str,
    required: bool,
    choices: &'static [&'static str],
}
struct Endpoint {
    path: &'static str,
    method: HttpMethod,
    instruction: Option<&'static str>,
    fields: &'static [Field],
}
fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_vaults" => Endpoint {
            path: "/api/v1/vaults",
            method: HttpMethod::Get,
            instruction: None,
            fields: &[],
        },
        "vault_mint" => Endpoint {
            path: "/api/v1/vault/mint",
            method: HttpMethod::Post,
            instruction: Some("vaultMint"),
            fields: &[
                Field {
                    key: "vaultId",
                    kind: "integer",
                    required: true,
                    choices: &[],
                },
                Field {
                    key: "symbol",
                    kind: "string",
                    required: true,
                    choices: &[],
                },
                Field {
                    key: "quantity",
                    kind: "string",
                    required: true,
                    choices: &[],
                },
                Field {
                    key: "autoBorrow",
                    kind: "boolean",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "autoLendRedeem",
                    kind: "boolean",
                    required: false,
                    choices: &[],
                },
            ],
        },
        "vault_redeem" => Endpoint {
            path: "/api/v1/vault/redeem",
            method: HttpMethod::Post,
            instruction: Some("vaultRedeemRequest"),
            fields: &[
                Field {
                    key: "vaultId",
                    kind: "integer",
                    required: true,
                    choices: &[],
                },
                Field {
                    key: "vaultTokenQuantity",
                    kind: "string",
                    required: false,
                    choices: &[],
                },
            ],
        },
        "vault_redeem_cancel" => Endpoint {
            path: "/api/v1/vault/redeem",
            method: HttpMethod::Delete,
            instruction: Some("vaultRedeemCancel"),
            fields: &[Field {
                key: "vaultId",
                kind: "integer",
                required: true,
                choices: &[],
            }],
        },
        "get_vault_pending_redeems" => Endpoint {
            path: "/api/v1/vault/redeems/pending",
            method: HttpMethod::Get,
            instruction: Some("vaultPendingRedeemsQuery"),
            fields: &[Field {
                key: "vaultId",
                kind: "integer",
                required: true,
                choices: &[],
            }],
        },
        "get_vault_nav" => Endpoint {
            path: "/api/v1/vault/nav",
            method: HttpMethod::Get,
            instruction: Some("vaultNavQuery"),
            fields: &[],
        },
        "get_vault_history" => Endpoint {
            path: "/api/v1/vaults/history",
            method: HttpMethod::Get,
            instruction: None,
            fields: &[
                Field {
                    key: "interval",
                    kind: "string",
                    required: true,
                    choices: &["1d", "1w", "1month", "1year"],
                },
                Field {
                    key: "vaultId",
                    kind: "integer",
                    required: false,
                    choices: &[],
                },
            ],
        },
        _ => return None,
    })
}
impl BackpackClient {
    pub(in crate::exchanges::backpack) async fn vault_schema_request(
        &self,
        name: &str,
        p: &BackpackParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(e) = endpoint(name) else {
            return Ok(None);
        };
        if public != e.instruction.is_none() {
            return Ok(None);
        }
        let keys: Vec<&str> = e.fields.iter().map(|f| f.key).collect();
        p.ensure_allowed(&keys, &[])?;
        let mut body = Map::new();
        let mut query = Vec::new();
        for f in e.fields {
            let Some(v) = p.get(f.key) else {
                if f.required {
                    return Err(DcexError::InvalidInput(format!("{} is required", f.key)));
                }
                continue;
            };
            if v.is_empty() || (!f.choices.is_empty() && !f.choices.contains(&v)) {
                return Err(DcexError::InvalidInput(format!("invalid {}", f.key)));
            }
            let value = match f.kind {
                "integer" => Value::from(
                    v.parse::<u64>()
                        .map_err(|_| DcexError::InvalidInput("invalid unsigned integer".into()))?,
                ),
                "boolean" => Value::from(
                    v.parse::<bool>()
                        .map_err(|_| DcexError::InvalidInput("invalid boolean".into()))?,
                ),
                _ => Value::String(v.to_string()),
            };
            if ["quantity", "vaultTokenQuantity"].contains(&f.key)
                && !crate::common::is_positive_plain_decimal(v)
            {
                return Err(DcexError::InvalidInput("quantity must be positive".into()));
            }
            if f.key == "vaultId" && v.parse::<u32>().is_err() {
                return Err(DcexError::InvalidInput("vaultId must be uint32".into()));
            }
            query.push((f.key.to_string(), v.to_string()));
            body.insert(f.key.to_string(), value);
        }
        let data = if public {
            self.public_get(e.path, query).await?
        } else if e.method == HttpMethod::Get {
            self.private_get(e.path, query, e.instruction.unwrap())
                .await?
        } else if e.method == HttpMethod::Post {
            self.private_post_value(e.path, Value::Object(body), e.instruction.unwrap())
                .await?
        } else {
            self.private_delete_value(e.path, Value::Object(body), e.instruction.unwrap())
                .await?
        };
        Ok(Some(data))
    }
}
