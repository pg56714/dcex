macro_rules! impl_exchange_method_wrappers {
    (
        $client:ty;
        public [$($public_method:ident),* $(,)?];
        private [$($private_method:ident),* $(,)?] $(;)?
    ) => {
        impl $client {
            $(
                pub async fn $public_method(
                    &self,
                    params: Vec<(String, String)>,
                ) -> crate::Result<crate::exchange::ValidatedResponse> {
                    self.public_request(stringify!($public_method), params).await
                }
            )*

            $(
                pub async fn $private_method(
                    &self,
                    params: Vec<(String, String)>,
                ) -> crate::Result<crate::exchange::ValidatedResponse> {
                    self.private_request(stringify!($private_method), params).await
                }
            )*
        }
    };
}

pub(crate) use impl_exchange_method_wrappers;

pub mod aster;
pub mod backpack;
pub mod binance;
pub mod bingx;
pub mod bitget;
pub mod bitmart;
pub mod bitmex;
pub mod bybit;
pub mod gateio;
pub mod hyperliquid;
pub mod kraken;
pub mod kucoin;
pub mod lighter;
pub mod mexc;
pub mod okx;
