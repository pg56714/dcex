//! Transfers request handlers.

mod fund_dispatch {
    use crate::exchange::ValidatedResponse;
    use crate::{DcexError, Result};
    use serde_json::Value;

    use super::super::client::ExtendedClient;
    use super::super::endpoints::*;
    use super::super::params::{
        ExtendedParams, body_object, json_string, json_u64, object_required,
        validate_positive_decimal,
    };

    impl ExtendedClient {
        pub(in crate::exchanges::extended) async fn dispatch_submit_internal_transfer(
            &self,
            params: &ExtendedParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["body"], &[])?;
            let body = params.body_required()?;
            let object = body_object(&body, "internal transfer")?;
            let from = json_u64(object, "fromAccount", true)?.expect("required");
            let to = json_u64(object, "toAccount", true)?.expect("required");
            if from == to {
                return Err(DcexError::InvalidInput(
                    "Extended internal transfer requires distinct subaccounts".into(),
                ));
            }
            let amount = json_string(object, "amount", true)?.expect("required");
            validate_positive_decimal("amount", amount)?;
            json_string(object, "transferredAsset", true)?;
            let settlement = object_required(object, "settlement")?;
            let settlement = settlement.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Extended transfer settlement must be an object".into())
            })?;
            for key in [
                "amount",
                "expirationTimestamp",
                "nonce",
                "receiverPositionId",
                "senderPositionId",
            ] {
                json_u64(settlement, key, true)?;
            }
            for key in ["assetId", "receiverPublicKey", "senderPublicKey"] {
                json_string(settlement, key, true)?;
            }
            let signature = object_required(settlement, "signature")?;
            let signature = signature.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Extended transfer signature must be an object".into())
            })?;
            for key in ["r", "s"] {
                json_string(signature, key, true)?;
            }
            self.private_post_value(INTERNAL_TRANSFER, Value::Object(object.clone()), Vec::new())
                .await
        }
    }
}
