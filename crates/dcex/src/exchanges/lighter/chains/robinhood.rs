use super::LighterEndpointProfile;

pub const ROBINHOOD: LighterEndpointProfile = LighterEndpointProfile {
    name: "robinhood",
    api_url: "https://api.rh.lighter.xyz",
    ws_url: "wss://api.rh.lighter.xyz/stream",
    chain_id: 466_324,
};

pub const ROBINHOOD_TESTNET: LighterEndpointProfile = LighterEndpointProfile {
    name: "robinhood_testnet",
    api_url: "https://api.rh-testnet.lighter.xyz",
    ws_url: "wss://api.rh-testnet.lighter.xyz/stream",
    chain_id: 300,
};
