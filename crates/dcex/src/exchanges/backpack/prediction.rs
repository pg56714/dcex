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
#[path = "generated/prediction_schema.rs"]
mod endpoints;
impl BackpackClient {
    pub(in crate::exchanges::backpack) async fn prediction_schema_request(
        &self,
        name: &str,
        p: &BackpackParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(e) = endpoints::endpoint(name) else {
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
            crate::exchanges::schema::encode(f.key, v, f.kind)?;
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
