//! Prediction operations.
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
        "get_prediction_events" => Endpoint {
            path: "/api/v1/prediction",
            method: HttpMethod::Get,
            instruction: None,
            fields: &[
                Field {
                    key: "symbol",
                    kind: "string",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "tagSlug",
                    kind: "string",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "eventSlug",
                    kind: "string",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "seriesSlug",
                    kind: "string",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "resolved",
                    kind: "boolean",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "sortBy",
                    kind: "string",
                    required: false,
                    choices: &["volume", "resolvedAt", "startDate", "endDate"],
                },
                Field {
                    key: "sortDirection",
                    kind: "string",
                    required: false,
                    choices: &["Asc", "Desc"],
                },
                Field {
                    key: "limit",
                    kind: "integer",
                    required: false,
                    choices: &[],
                },
                Field {
                    key: "offset",
                    kind: "integer",
                    required: false,
                    choices: &[],
                },
            ],
        },
        "get_prediction_tags" => Endpoint {
            path: "/api/v1/prediction/tags",
            method: HttpMethod::Get,
            instruction: None,
            fields: &[],
        },
        _ => return None,
    })
}
impl BackpackClient {
    pub(in crate::exchanges::backpack) async fn prediction_schema_request(
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
