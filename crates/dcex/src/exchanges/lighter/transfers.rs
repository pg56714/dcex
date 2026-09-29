//! Transfers requests.

mod wrappers {
    use crate::exchanges::lighter::LighterClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; LighterClient;
     public [

     ];
     private [
    get_transfer_fee_info(),
    get_transfer_history()
     ];
    }
}

impl super::client::LighterClient {
    pub(in crate::exchanges::lighter) async fn transfers_field_schema_request(
        &self,
        name: &str,
        p: &super::params::LighterParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Transfers)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.field_schema_request_transport(name, p).await
    }
}
