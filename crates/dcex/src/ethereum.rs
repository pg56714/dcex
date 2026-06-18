use std::sync::OnceLock;

use num_bigint::BigUint;
use num_traits::{One, Zero};

use crate::crypto::hmac_sha256;
use crate::{DcexError, Result};

const KECCAK_RATE: usize = 136;
const KECCAK_ROUND_CONSTANTS: [u64; 24] = [
    0x0000_0000_0000_0001,
    0x0000_0000_0000_8082,
    0x8000_0000_0000_808a,
    0x8000_0000_8000_8000,
    0x0000_0000_0000_808b,
    0x0000_0000_8000_0001,
    0x8000_0000_8000_8081,
    0x8000_0000_0000_8009,
    0x0000_0000_0000_008a,
    0x0000_0000_0000_0088,
    0x0000_0000_8000_8009,
    0x0000_0000_8000_000a,
    0x0000_0000_8000_808b,
    0x8000_0000_0000_008b,
    0x8000_0000_0000_8089,
    0x8000_0000_0000_8003,
    0x8000_0000_0000_8002,
    0x8000_0000_0000_0080,
    0x0000_0000_0000_800a,
    0x8000_0000_8000_000a,
    0x8000_0000_8000_8081,
    0x8000_0000_0000_8080,
    0x0000_0000_8000_0001,
    0x8000_0000_8000_8008,
];
const KECCAK_ROTATIONS: [[u32; 5]; 5] = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14],
];

#[derive(Clone, Debug)]
struct Point {
    x: BigUint,
    y: BigUint,
}

pub fn keccak256(data: &[u8]) -> [u8; 32] {
    let mut state = [0u64; 25];
    let mut chunks = data.chunks_exact(KECCAK_RATE);
    for block in &mut chunks {
        absorb_block(&mut state, block);
        keccak_f1600(&mut state);
    }

    let remainder = chunks.remainder();
    let mut block = [0u8; KECCAK_RATE];
    block[..remainder.len()].copy_from_slice(remainder);
    block[remainder.len()] = 0x01;
    block[KECCAK_RATE - 1] |= 0x80;
    absorb_block(&mut state, &block);
    keccak_f1600(&mut state);

    let mut output = [0u8; 32];
    for (index, chunk) in output.chunks_mut(8).enumerate() {
        chunk.copy_from_slice(&state[index].to_le_bytes());
    }
    output
}

pub fn recoverable_sign(digest: &[u8; 32], private_key: &[u8; 32]) -> Result<[u8; 65]> {
    let n = secp_n();
    let private_key = BigUint::from_bytes_be(private_key);
    if private_key.is_zero() || &private_key >= n {
        return Err(DcexError::InvalidInput(
            "secp256k1 private key is outside the valid range.".to_string(),
        ));
    }
    let z = BigUint::from_bytes_be(digest) % n;
    let mut state = Rfc6979::new(&private_key, digest)?;

    loop {
        let nonce = state.next_nonce()?;
        let point = scalar_mul(&generator(), &nonce);
        let r = &point.x % n;
        if r.is_zero() {
            state.reject()?;
            continue;
        }
        let nonce_inverse = nonce.modpow(&(n - BigUint::from(2u8)), n);
        let mut s = (nonce_inverse * (&z + (&r * &private_key))) % n;
        if s.is_zero() {
            state.reject()?;
            continue;
        }

        let mut recovery_id = u8::from(point.x >= *n) << 1;
        if (&point.y & BigUint::one()) == BigUint::one() {
            recovery_id |= 1;
        }
        if s > n >> 1 {
            s = n - s;
            recovery_id ^= 1;
        }

        let mut signature = [0u8; 65];
        write_biguint_32(&r, &mut signature[..32]);
        write_biguint_32(&s, &mut signature[32..64]);
        signature[64] = recovery_id;
        return Ok(signature);
    }
}

struct Rfc6979 {
    key: [u8; 32],
    value: [u8; 32],
}

impl Rfc6979 {
    fn new(private_key: &BigUint, digest: &[u8; 32]) -> Result<Self> {
        let mut private_key_bytes = [0u8; 32];
        write_biguint_32(private_key, &mut private_key_bytes);
        let digest = BigUint::from_bytes_be(digest) % secp_n();
        let mut digest_bytes = [0u8; 32];
        write_biguint_32(&digest, &mut digest_bytes);

        let mut state = Self {
            key: [0u8; 32],
            value: [1u8; 32],
        };
        let mut seed = Vec::with_capacity(97);
        seed.extend_from_slice(&state.value);
        seed.push(0);
        seed.extend_from_slice(&private_key_bytes);
        seed.extend_from_slice(&digest_bytes);
        state.key = hmac_sha256(&state.key, &seed)?;
        state.value = hmac_sha256(&state.key, &state.value)?;

        seed.clear();
        seed.extend_from_slice(&state.value);
        seed.push(1);
        seed.extend_from_slice(&private_key_bytes);
        seed.extend_from_slice(&digest_bytes);
        state.key = hmac_sha256(&state.key, &seed)?;
        state.value = hmac_sha256(&state.key, &state.value)?;
        Ok(state)
    }

    fn next_nonce(&mut self) -> Result<BigUint> {
        loop {
            self.value = hmac_sha256(&self.key, &self.value)?;
            let candidate = BigUint::from_bytes_be(&self.value);
            if !candidate.is_zero() && candidate < *secp_n() {
                return Ok(candidate);
            }
            self.reject()?;
        }
    }

    fn reject(&mut self) -> Result<()> {
        let mut payload = Vec::with_capacity(33);
        payload.extend_from_slice(&self.value);
        payload.push(0);
        self.key = hmac_sha256(&self.key, &payload)?;
        self.value = hmac_sha256(&self.key, &self.value)?;
        Ok(())
    }
}

fn absorb_block(state: &mut [u64; 25], block: &[u8]) {
    for (index, lane) in block.chunks_exact(8).enumerate() {
        state[index] ^= u64::from_le_bytes(lane.try_into().expect("8-byte lane"));
    }
}

fn keccak_f1600(state: &mut [u64; 25]) {
    for round_constant in KECCAK_ROUND_CONSTANTS {
        let mut column = [0u64; 5];
        for x in 0..5 {
            column[x] = state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20];
        }
        let mut delta = [0u64; 5];
        for x in 0..5 {
            delta[x] = column[(x + 4) % 5] ^ column[(x + 1) % 5].rotate_left(1);
        }
        for y in 0..5 {
            for x in 0..5 {
                state[x + 5 * y] ^= delta[x];
            }
        }

        let mut rotated = [0u64; 25];
        for y in 0..5 {
            for x in 0..5 {
                rotated[y + 5 * ((2 * x + 3 * y) % 5)] =
                    state[x + 5 * y].rotate_left(KECCAK_ROTATIONS[x][y]);
            }
        }
        for y in 0..5 {
            for x in 0..5 {
                state[x + 5 * y] = rotated[x + 5 * y]
                    ^ ((!rotated[(x + 1) % 5 + 5 * y]) & rotated[(x + 2) % 5 + 5 * y]);
            }
        }
        state[0] ^= round_constant;
    }
}

fn generator() -> Point {
    Point {
        x: secp_gx().clone(),
        y: secp_gy().clone(),
    }
}

fn scalar_mul(point: &Point, scalar: &BigUint) -> Point {
    let mut result: Option<Point> = None;
    let mut addend = point.clone();
    let mut scalar = scalar.clone();
    while !scalar.is_zero() {
        if (&scalar & BigUint::one()) == BigUint::one() {
            result = Some(match result {
                Some(current) => point_add(&current, &addend).expect("non-infinite scalar sum"),
                None => addend.clone(),
            });
        }
        addend = point_double(&addend).expect("non-infinite generator multiple");
        scalar >>= 1;
    }
    result.expect("non-zero scalar")
}

fn point_add(left: &Point, right: &Point) -> Option<Point> {
    let p = secp_p();
    if left.x == right.x {
        if (&left.y + &right.y) % p == BigUint::zero() {
            return None;
        }
        return point_double(left);
    }
    let numerator = mod_sub(&right.y, &left.y, p);
    let denominator = mod_sub(&right.x, &left.x, p);
    let slope = numerator * denominator.modpow(&(p - BigUint::from(2u8)), p) % p;
    let x = mod_sub(&mod_sub(&(&slope * &slope % p), &left.x, p), &right.x, p);
    let y = mod_sub(&(&slope * mod_sub(&left.x, &x, p) % p), &left.y, p);
    Some(Point { x, y })
}

fn point_double(point: &Point) -> Option<Point> {
    if point.y.is_zero() {
        return None;
    }
    let p = secp_p();
    let numerator = BigUint::from(3u8) * &point.x * &point.x % p;
    let denominator = BigUint::from(2u8) * &point.y % p;
    let slope = numerator * denominator.modpow(&(p - BigUint::from(2u8)), p) % p;
    let x = mod_sub(
        &(&slope * &slope % p),
        &(BigUint::from(2u8) * &point.x % p),
        p,
    );
    let y = mod_sub(&(&slope * mod_sub(&point.x, &x, p) % p), &point.y, p);
    Some(Point { x, y })
}

fn mod_sub(left: &BigUint, right: &BigUint, modulus: &BigUint) -> BigUint {
    if left >= right {
        (left - right) % modulus
    } else {
        (modulus - ((right - left) % modulus)) % modulus
    }
}

fn write_biguint_32(value: &BigUint, output: &mut [u8]) {
    let bytes = value.to_bytes_be();
    output[32 - bytes.len()..].copy_from_slice(&bytes);
}

fn parse_hex(value: &[u8]) -> BigUint {
    BigUint::parse_bytes(value, 16).expect("valid secp256k1 constant")
}

fn secp_p() -> &'static BigUint {
    static VALUE: OnceLock<BigUint> = OnceLock::new();
    VALUE.get_or_init(|| {
        parse_hex(b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F")
    })
}

fn secp_n() -> &'static BigUint {
    static VALUE: OnceLock<BigUint> = OnceLock::new();
    VALUE.get_or_init(|| {
        parse_hex(b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141")
    })
}

fn secp_gx() -> &'static BigUint {
    static VALUE: OnceLock<BigUint> = OnceLock::new();
    VALUE.get_or_init(|| {
        parse_hex(b"79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798")
    })
}

fn secp_gy() -> &'static BigUint {
    static VALUE: OnceLock<BigUint> = OnceLock::new();
    VALUE.get_or_init(|| {
        parse_hex(b"483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8")
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn keccak_matches_known_vector() {
        assert_eq!(
            hex::encode(keccak256(b"")),
            "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
        );
    }

    #[test]
    fn recoverable_signature_matches_hyperliquid_vector() {
        let digest =
            hex::decode("dec5a4add734140f9c8784a1afb7a23520cb9ff27de78094f2f15d219df2fa52")
                .expect("digest");
        let private_key = [0x11u8; 32];
        let signature =
            recoverable_sign(digest.as_slice().try_into().expect("digest"), &private_key)
                .expect("signature");

        assert_eq!(
            hex::encode(&signature[..32]),
            "193f5e88d621ca384beca6146a4c059b8716d5ad3da0404f6cd36f020fc87671"
        );
        assert_eq!(
            hex::encode(&signature[32..64]),
            "0c3767a2287482caef8a77be7b5c76eac08d9d8fb3080c53033e394bbb35d047"
        );
        assert_eq!(signature[64], 0);
    }
}
