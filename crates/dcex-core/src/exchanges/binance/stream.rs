use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::ensure_futures_listen_key_market;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::Result;

impl BinanceClient {
    pub async fn create_futures_listen_key(&self) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Post,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            Vec::new(),
        )
        .await
    }

    pub async fn keep_alive_futures_listen_key(
        &self,
        listen_key: &str,
    ) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Put,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            vec![("listenKey".to_string(), listen_key.to_string())],
        )
        .await
    }

    pub async fn close_futures_listen_key(&self, listen_key: &str) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Delete,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            vec![("listenKey".to_string(), listen_key.to_string())],
        )
        .await
    }

    pub async fn get_listen_key(&self, market_type: &str) -> Result<ValidatedResponse> {
        ensure_futures_listen_key_market(market_type)?;
        self.create_futures_listen_key().await
    }

    pub async fn keep_alive_listen_key(
        &self,
        listen_key: &str,
        market_type: &str,
    ) -> Result<ValidatedResponse> {
        ensure_futures_listen_key_market(market_type)?;
        self.keep_alive_futures_listen_key(listen_key).await
    }

    pub async fn close_listen_key(
        &self,
        listen_key: &str,
        market_type: &str,
    ) -> Result<ValidatedResponse> {
        ensure_futures_listen_key_market(market_type)?;
        self.close_futures_listen_key(listen_key).await
    }
}
