//! Withdrawal requests and validation.

mod account_requests {
    use crate::exchanges::extended::{
        client::ExtendedClient,
        endpoints::BRIDGE_QUOTE,
        params::{ExtendedParams, body_object, json_string, json_u64, object_required},
    };
    use crate::{DcexError, Result, exchange::ValidatedResponse};
    use serde_json::Value;
    impl ExtendedClient {
        pub(in crate::exchanges::extended) async fn commit_bridge_quote_request(
            &self,
            params: &ExtendedParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["id"], &[])?;
            let id = params.required("id")?;
            self.request(
                crate::http::HttpMethod::Post,
                BRIDGE_QUOTE,
                vec![("id".into(), id.into())],
                None,
                true,
                Default::default(),
            )
            .await
        }

        pub(in crate::exchanges::extended) async fn create_withdrawal_signed_request(
            &self,
            params: &ExtendedParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["body"], &[])?;
            let body: Value = serde_json::from_str(params.required("body")?)
                .map_err(|_| DcexError::InvalidInput("Extended body must be valid JSON".into()))?;
            let object = body_object(&body, "withdrawal")?;
            for key in object.keys() {
                if ![
                    "chainId",
                    "accountId",
                    "amount",
                    "asset",
                    "settlement",
                    "quoteId",
                    "description",
                ]
                .contains(&key.as_str())
                {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported Extended withdrawal field: {key}"
                    )));
                }
            }
            for key in ["chainId", "amount", "asset"] {
                json_string(object, key, true)?;
            }
            json_u64(object, "accountId", true)?;
            if !crate::common::is_positive_plain_decimal(
                json_string(object, "amount", true)?.expect("required"),
            ) {
                return Err(DcexError::InvalidInput(
                    "Extended amount requires a positive plain decimal string".into(),
                ));
            }
            if object["chainId"] != "STRK" {
                json_string(object, "quoteId", true)?;
            }
            if let Some(description) = json_string(object, "description", false)?
                && description.chars().count() > 250
            {
                return Err(DcexError::InvalidInput(
                    "Extended description must not exceed 250 characters".into(),
                ));
            }
            let settlement = object_required(object, "settlement")?
                .as_object()
                .ok_or_else(|| {
                    DcexError::InvalidInput("Extended settlement must be an object".into())
                })?;
            for key in ["recipient", "collateralId", "amount"] {
                json_string(settlement, key, true)?;
            }
            for key in ["positionId", "salt"] {
                json_u64(settlement, key, true)?;
            }
            let expiration = object_required(settlement, "expiration")?
                .as_object()
                .ok_or_else(|| {
                    DcexError::InvalidInput("Extended expiration must be an object".into())
                })?;
            json_u64(expiration, "seconds", true)?;
            let signature = object_required(settlement, "signature")?
                .as_object()
                .ok_or_else(|| {
                    DcexError::InvalidInput("Extended signature must be an object".into())
                })?;
            for key in ["r", "s"] {
                json_string(signature, key, true)?;
            }
            self.private_post_value(
                "/api/v1/user/withdrawal",
                Value::Object(object.clone()),
                Vec::new(),
            )
            .await
        }
    }
}
