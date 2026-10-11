use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;

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

    /// `PUT /fapi/v1/listenKey` takes no parameters: the listen key is bound to
    /// the API key, so Binance extends the account's active key.
    pub async fn keep_alive_futures_listen_key(&self) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Put,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            Vec::new(),
        )
        .await
    }

    /// `DELETE /fapi/v1/listenKey` takes no parameters: it closes the account's
    /// active listen key.
    pub async fn close_futures_listen_key(&self) -> Result<ValidatedResponse> {
        self.api_key_request(
            HttpMethod::Delete,
            BinanceMarket::Futures,
            FUTURES_USER_DATA_STREAM,
            Vec::new(),
        )
        .await
    }
}
