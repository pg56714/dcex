use super::LighterEndpointProfile;

pub const MAINNET: LighterEndpointProfile = LighterEndpointProfile {
    name: "mainnet",
    api_url: "https://mainnet.zklighter.elliot.ai",
    ws_url: "wss://mainnet.zklighter.elliot.ai/stream",
    chain_id: 304,
};

pub const TESTNET: LighterEndpointProfile = LighterEndpointProfile {
    name: "testnet",
    api_url: "https://testnet.zklighter.elliot.ai",
    ws_url: "wss://testnet.zklighter.elliot.ai/stream",
    chain_id: 300,
};
