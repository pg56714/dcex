use std::env;
use std::time::Instant;

use dcex::lighter;
use serde_json::json;

const HASH_VALUES: [u64; 7] = [
    3451004116618606032,
    11263134342958518251,
    10957204882857370932,
    5369763041201481933,
    7695734348563036858,
    1393419330378128434,
    7387917082382606332,
];
const PRIVATE_KEY_LIMBS: [u64; 5] = [
    12235002942052073545,
    1175977464658719998,
    8536934969147463310,
    6524687619313720391,
    2922072024880609112,
];
const NONCE_LIMBS: [u64; 5] = [
    5245666847777449560,
    15178169970799106939,
    4403065012435293749,
    15306540389399388999,
    8935555081913173844,
];
const MESSAGE_HASH: [u8; 40] = [
    75, 162, 23, 206, 189, 130, 135, 116, 208, 17, 34, 133, 252, 57, 153, 153, 217, 246, 24, 101,
    174, 219, 16, 135, 63, 111, 132, 83, 80, 54, 214, 250, 124, 121, 245, 49, 2, 215, 21, 238,
];
const TX_VALUES: [i128; 16] = [304, 14, 11, 1_590_000, 12, 3, 4, 5, 6, 7, 1, 0, 2, 0, 0, 8];
const TX_ATTRIBUTES: [(u64, u64); 3] = [(1, 9), (2, 10), (4, 1)];
const TX_PAYLOAD_JSON: &[u8] = br#"{"AccountIndex":12,"ApiKeyIndex":3,"MarketIndex":4,"ClientOrderIndex":5,"BaseAmount":6,"Price":7,"IsAsk":1,"Type":0,"TimeInForce":2,"ReduceOnly":0,"TriggerPrice":0,"OrderExpiry":8,"ExpiredAt":1590000,"Nonce":11}"#;

fn env_positive_usize(name: &str, default: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .filter(|value| *value > 0)
        .unwrap_or(default)
}

fn scalar_bytes(limbs: [u64; 5]) -> [u8; 40] {
    let mut bytes = [0u8; 40];
    for (index, limb) in limbs.iter().enumerate() {
        bytes[index * 8..(index + 1) * 8].copy_from_slice(&limb.to_le_bytes());
    }
    bytes
}

fn env_nonnegative_usize(name: &str, default: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(default)
}

fn median(values: &mut [f64]) -> f64 {
    values.sort_by(|left, right| left.total_cmp(right));
    let midpoint = values.len() / 2;
    if values.len() % 2 == 0 {
        (values[midpoint - 1] + values[midpoint]) / 2.0
    } else {
        values[midpoint]
    }
}

fn measure<F, T>(mut callback: F, iterations: usize, warmup: usize, inner_loops: usize) -> f64
where
    F: FnMut() -> dcex::Result<T>,
{
    for _ in 0..warmup {
        for _ in 0..inner_loops {
            callback().expect("warmup callback");
        }
    }

    let mut elapsed_ms = Vec::with_capacity(iterations);
    for _ in 0..iterations {
        let start = Instant::now();
        for _ in 0..inner_loops {
            callback().expect("benchmark callback");
        }
        elapsed_ms.push(start.elapsed().as_secs_f64() * 1_000.0 / inner_loops as f64);
    }
    median(&mut elapsed_ms)
}

fn hash() -> dcex::Result<Vec<u8>> {
    Ok(lighter::poseidon_hash_bytes(&HASH_VALUES).to_vec())
}

fn signature() -> dcex::Result<Vec<u8>> {
    let private_key_bytes = scalar_bytes(PRIVATE_KEY_LIMBS);
    let nonce_bytes = scalar_bytes(NONCE_LIMBS);
    let private_key = lighter::private_key_from_bytes(&private_key_bytes)?;
    let nonce = lighter::scalar_from_bytes(&nonce_bytes, "nonce")?;
    lighter::schnorr_sign_with_nonce(&MESSAGE_HASH, &private_key, &nonce).map(Vec::from)
}

fn transaction_payload() -> dcex::Result<Vec<u8>> {
    let private_key_bytes = scalar_bytes(PRIVATE_KEY_LIMBS);
    let nonce_bytes = scalar_bytes(NONCE_LIMBS);
    lighter::sign_transaction_payload(
        &TX_VALUES,
        &TX_ATTRIBUTES,
        TX_PAYLOAD_JSON,
        &private_key_bytes,
        &nonce_bytes,
    )
    .map(|(payload, _)| payload)
}

fn main() {
    let iterations = env_positive_usize("DCEX_BENCH_ITERATIONS", 20);
    let warmup = env_nonnegative_usize("DCEX_BENCH_WARMUP", 3);
    let inner_loops = env_positive_usize("DCEX_BENCH_INNER_LOOPS", 1);

    let rows = vec![
        json!({
            "operation": "Cryptographic hash",
            "rust_median_ms": measure(hash, iterations, warmup, inner_loops),
        }),
        json!({
            "operation": "Schnorr signature",
            "rust_median_ms": measure(signature, iterations, warmup, inner_loops),
        }),
        json!({
            "operation": "Transaction payload signing",
            "rust_median_ms": measure(transaction_payload, iterations, warmup, inner_loops),
        }),
    ];

    if env::var("DCEX_BENCH_OUTPUT")
        .map(|value| value.eq_ignore_ascii_case("json"))
        .unwrap_or(false)
    {
        println!("{}", json!({ "rows": rows }));
    } else {
        println!("| Operation | Rust median ms |");
        println!("| --------- | -------------- |");
        for row in rows {
            println!(
                "| {} | {:.6} |",
                row["operation"].as_str().expect("operation"),
                row["rust_median_ms"].as_f64().expect("rust_median_ms")
            );
        }
    }
}
