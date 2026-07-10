pub(super) const BASE_URL: &str = "https://api.starknet.extended.exchange";
pub(super) const USER_AGENT: &str = "dcex-rust/0.1";

pub(super) const MARKETS: &str = "/api/v1/info/markets";
pub(super) const ASSETS: &str = "/api/v1/info/assets";
pub(super) const BUILDER_DASHBOARD: &str = "/api/v1/info/builder/dashboard";

pub(super) const ACCOUNT_INFO: &str = "/api/v1/user/account/info";
pub(super) const ACCOUNTS: &str = "/api/v1/user/accounts";
pub(super) const BALANCE: &str = "/api/v1/user/balance";
pub(super) const SPOT_BALANCES: &str = "/api/v1/user/spot/balances";
pub(super) const POSITIONS: &str = "/api/v1/user/positions";
pub(super) const POSITIONS_HISTORY: &str = "/api/v1/user/positions/history";
pub(super) const ORDERS: &str = "/api/v1/user/orders";
pub(super) const ORDERS_HISTORY: &str = "/api/v1/user/orders/history";
pub(super) const ORDER: &str = "/api/v1/user/order";
pub(super) const FILLS: &str = "/api/v1/user/trades";
pub(super) const FUNDING_PAYMENTS: &str = "/api/v1/user/funding/history";
pub(super) const LEVERAGE: &str = "/api/v1/user/leverage";
pub(super) const FEES: &str = "/api/v1/user/fees";
pub(super) const ASSET_OPERATIONS: &str = "/api/v1/user/assetOperations";
pub(super) const REBATES: &str = "/api/v1/user/rebates/stats";
pub(super) const BUILDER_TRADES: &str = "/api/v1/builder/trades";
pub(super) const BRIDGE_CONFIG: &str = "/api/v1/user/bridge/config";
pub(super) const BRIDGE_QUOTE: &str = "/api/v1/user/bridge/quote";
pub(super) const MASS_CANCEL: &str = "/api/v1/user/order/massCancel";
pub(super) const DEADMAN_SWITCH: &str = "/api/v1/user/deadmanswitch";
