use std::time::Instant;

use dcex::lighter::{poseidon_hash_bytes, scalar_from_bytes, schnorr_sign_with_nonce};

fn main() {
    let private_key = scalar_from_bytes(&[1; 40], "private key").expect("private key");
    let nonce = scalar_from_bytes(&[2; 40], "nonce").expect("nonce");
    let message_hash = poseidon_hash_bytes(&(0..16).collect::<Vec<_>>());

    let cold_start = Instant::now();
    schnorr_sign_with_nonce(&message_hash, &private_key, &nonce).expect("signature");
    println!(
        "cold start: {:.3} ms",
        cold_start.elapsed().as_secs_f64() * 1_000.0
    );

    for _ in 0..9 {
        schnorr_sign_with_nonce(&message_hash, &private_key, &nonce).expect("signature");
    }

    let iterations = 1_000;
    let start = Instant::now();
    for _ in 0..iterations {
        schnorr_sign_with_nonce(&message_hash, &private_key, &nonce).expect("signature");
    }
    let elapsed = start.elapsed();
    let micros = elapsed.as_secs_f64() * 1_000_000.0 / f64::from(iterations);
    println!("{micros:.3} us/op");
}
