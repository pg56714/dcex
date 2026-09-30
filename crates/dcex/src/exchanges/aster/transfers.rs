//! Fund movement and batch request implementations.

mod client_operations {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::aster::client::*;

    use crate::exchanges::aster::signing::{encode_params, sign_message};
    use crate::http::HttpMethod;

    use crate::{DcexError, Result};

    impl AsterClient {
        /// Transfers within one master/sub-account family using the approved agent.
        /// Not verified live: the official V3 parameter table specifies `signer`, but
        /// its generic signing template also includes `user`. This implementation
        /// follows the endpoint table pending an authoritative signed example.
        /// https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        pub(in crate::exchanges::aster) async fn sub_account_transfer(
            &self,
            params: &crate::exchanges::aster::params::AsterParams,
        ) -> Result<ValidatedResponse> {
            let signer = self.signer_address.as_deref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Aster sub-account transfers require an approved signer.".into(),
                )
            })?;
            let key = self.private_key.as_ref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Aster sub-account transfers require the signer private key.".into(),
                )
            })?;
            let mut pairs = params.only(&["toAccountAddress", "asset", "amount", "kindType"]);
            pairs.push(("nonce".into(), self.next_nonce()?.to_string()));
            pairs.push(("signer".into(), signer.into()));
            pairs.extend(params.only(&["fromAccountAddress"]));
            let signature = sign_message(&encode_params(&pairs), key)?;
            pairs.push(("signature".into(), signature));
            // Already signed in this endpoint's specified field order.
            self.request(
                HttpMethod::Post,
                AsterMarket::Futures,
                "/fapi/v3/subAccountTransfer",
                pairs,
                false,
            )
            .await
        }
    }
}

mod wrappers {
    use crate::exchanges::aster::AsterClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; AsterClient;
     public [

     ];
     private [
    transfer_sub_account(
                to_account_address => "toAccountAddress",
                asset => "asset",
                amount => "amount",
                kind_type => "kindType"
            ),
    transfer_spot_futures(
                amount => "amount",
                asset => "asset",
                client_tran_id => "clientTranId",
                kind_type => "kindType"
            ),
    create_prediction_asset_wallet_transfer(
                amount => "amount",
                asset => "asset",
                client_tran_id => "clientTranId",
                kind_type => "kindType"
            )
     ];
    }
}

mod fund_dispatch {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::http::HttpMethod;

    use super::super::client::{AsterClient, AsterMarket};
    use super::super::endpoints::*;
    use super::super::params::AsterParams;

    impl AsterClient {
        pub(in crate::exchanges::aster) async fn dispatch_transfer_spot_futures(
            &self,
            params: &AsterParams,
        ) -> Result<ValidatedResponse> {
            let market = params.get("market").unwrap_or("spot").to_ascii_lowercase();
            let (market, path) = match market.as_str() {
                "spot" => (AsterMarket::Spot, SPOT_TRANSFER),
                "futures" => (AsterMarket::Futures, FUTURES_TRANSFER),
                _ => unreachable!("validated Aster transfer market"),
            };
            self.signed(
                HttpMethod::Post,
                market,
                path,
                params.only(&["amount", "asset", "clientTranId", "kindType"]),
            )
            .await
        }
    }
}

impl super::client::AsterClient {
    pub(in crate::exchanges::aster) async fn transfers_prediction_dispatch(
        &self,
        name: &str,
        p: &super::params::AsterParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.prediction_dispatch_transport(name, p, public).await
    }
}
