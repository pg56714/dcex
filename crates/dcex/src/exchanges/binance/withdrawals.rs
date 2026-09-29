//! Schema-driven fund operations.

impl super::client::BinanceClient {
    pub(in crate::exchanges::binance) async fn withdrawals_table_request(
        &self,
        name: &str,
        params: &super::params::PublicParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Withdrawals)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::BinanceClient {
    pub(in crate::exchanges::binance) async fn withdrawals_field_schema_request(
        &self,
        name: &str,
        p: &super::params::PublicParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Withdrawals)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.field_schema_request_transport(name, p).await
    }
}

impl super::client::BinanceClient {
    pub(in crate::exchanges::binance) async fn withdrawals_catalog_request(
        &self,
        name: &str,
        p: &super::params::PublicParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Withdrawals)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.catalog_request_transport(name, p, public).await
    }
}
