use std::sync::OnceLock;

use crypto_bigint::modular::ConstMontyForm;
use crypto_bigint::{CtAssign, U256, const_monty_params};
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

const_monty_params!(
    FieldModulus,
    U256,
    "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
    "secp256k1 field prime p = 2^256 - 2^32 - 977"
);

type Fp = ConstMontyForm<FieldModulus, { U256::LIMBS }>;

const_monty_params!(
    OrderModulus,
    U256,
    "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141",
    "secp256k1 group order n"
);

type Scalar = ConstMontyForm<OrderModulus, { U256::LIMBS }>;

/// 3 * b for y^2 = x^3 + 7, used by the complete addition formulas.
const CURVE_B3: Fp = Fp::new(&U256::from_u64(21));
const GENERATOR_X: U256 =
    U256::from_be_hex("79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798");
const GENERATOR_Y: U256 =
    U256::from_be_hex("483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8");

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
        let (x, y) = generator_multiple(&nonce);
        let r = &x % n;
        if r.is_zero() {
            state.reject()?;
            continue;
        }
        // s = (z + r * d) / k mod n. The nonce and the key are secret, so this stays in
        // constant-time arithmetic like the multiplication above.
        let nonce_inverse = Option::<Scalar>::from(scalar(&nonce).invert())
            .expect("a nonce in 1..n is invertible modulo the prime n");
        let s = scalar(&r)
            .mul(&scalar(&private_key))
            .add(&scalar(&z))
            .mul(&nonce_inverse);
        let mut s = uint_to_biguint(&s.retrieve());
        if s.is_zero() {
            state.reject()?;
            continue;
        }

        let mut recovery_id = u8::from(x >= *n) << 1;
        if (&y & BigUint::one()) == BigUint::one() {
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

/// `scalar * G` in affine coordinates, for a scalar in `1..n`.
///
/// The scalar is the signing nonce, so the multiplication runs over all 256 bits with
/// complete formulas and a constant-time select: the nonce never chooses a code path.
fn generator_multiple(scalar: &BigUint) -> (BigUint, BigUint) {
    let mut bytes = [0u8; 32];
    write_biguint_32(scalar, &mut bytes);
    let (x, y) = ProjectivePoint::generator()
        .mul(&U256::from_be_slice(&bytes))
        .into_affine()
        .expect("a scalar in 1..n is never a multiple of the group order");
    (field_to_biguint(&x), field_to_biguint(&y))
}

fn field_to_biguint(value: &Fp) -> BigUint {
    uint_to_biguint(&value.retrieve())
}

fn uint_to_biguint(value: &U256) -> BigUint {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&value.to_be_bytes());
    BigUint::from_bytes_be(&bytes)
}

/// A value below the group order as a scalar.
fn scalar(value: &BigUint) -> Scalar {
    let mut bytes = [0u8; 32];
    write_biguint_32(value, &mut bytes);
    Scalar::new(&U256::from_be_slice(&bytes))
}

struct ProjectivePoint {
    x: Fp,
    y: Fp,
    z: Fp,
}

impl ProjectivePoint {
    const IDENTITY: Self = Self {
        x: Fp::ZERO,
        y: Fp::ONE,
        z: Fp::ZERO,
    };

    fn generator() -> Self {
        Self {
            x: Fp::new(&GENERATOR_X),
            y: Fp::new(&GENERATOR_Y),
            z: Fp::ONE,
        }
    }

    /// Complete addition for short Weierstrass curves (Renes, Costello and Batina 2016,
    /// algorithm 1) with a = 0; also valid for doubling and the identity, so it never
    /// branches.
    fn add(&self, other: &Self) -> Self {
        let (x1, y1, z1) = (self.x, self.y, self.z);
        let (x2, y2, z2) = (other.x, other.y, other.z);

        let t0 = x1.mul(&x2);
        let t1 = y1.mul(&y2);
        let t2 = z1.mul(&z2);
        // The cross terms x1*y2 + x2*y1, x1*z2 + x2*z1 and y1*z2 + y2*z1.
        let t3 = x1.add(&y1).mul(&x2.add(&y2)).sub(&t0.add(&t1));
        let t4 = x1.add(&z1).mul(&x2.add(&z2)).sub(&t0.add(&t2));
        let t5 = y1.add(&z1).mul(&y2.add(&z2)).sub(&t1.add(&t2));

        let b3_t2 = CURVE_B3.mul(&t2);
        let b3_t4 = CURVE_B3.mul(&t4);
        let difference = t1.sub(&b3_t2);
        let sum = t1.add(&b3_t2);
        let three_t0 = t0.double().add(&t0);

        Self {
            x: t3.mul(&difference).sub(&t5.mul(&b3_t4)),
            y: difference.mul(&sum).add(&three_t0.mul(&b3_t4)),
            z: t5.mul(&sum).add(&t3.mul(&three_t0)),
        }
    }

    /// Double-and-add-always over all 256 bits with a constant-time select.
    fn mul(&self, scalar: &U256) -> Self {
        let mut result = Self::IDENTITY;
        for bit in (0..U256::BITS).rev() {
            result = result.add(&result);
            let sum = result.add(self);
            result.ct_assign(&sum, scalar.bit(bit));
        }
        result
    }

    fn ct_assign(&mut self, other: &Self, choice: crypto_bigint::Choice) {
        self.x.ct_assign(&other.x, choice);
        self.y.ct_assign(&other.y, choice);
        self.z.ct_assign(&other.z, choice);
    }

    /// Affine coordinates, or `None` for the identity.
    fn into_affine(self) -> Option<(Fp, Fp)> {
        let z_inverse = Option::<Fp>::from(self.z.invert())?;
        Some((self.x.mul(&z_inverse), self.y.mul(&z_inverse)))
    }
}

fn write_biguint_32(value: &BigUint, output: &mut [u8]) {
    let bytes = value.to_bytes_be();
    output[32 - bytes.len()..].copy_from_slice(&bytes);
}

fn parse_hex(value: &[u8]) -> BigUint {
    BigUint::parse_bytes(value, 16).expect("valid secp256k1 constant")
}

fn secp_n() -> &'static BigUint {
    static VALUE: OnceLock<BigUint> = OnceLock::new();
    VALUE.get_or_init(|| {
        parse_hex(b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141")
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    // The textbook affine arithmetic the projective code replaced, kept as an oracle.
    #[derive(Clone, Debug)]
    struct Point {
        x: BigUint,
        y: BigUint,
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

    fn secp_p() -> &'static BigUint {
        static VALUE: OnceLock<BigUint> = OnceLock::new();
        VALUE.get_or_init(|| {
            parse_hex(b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F")
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

    #[test]
    fn projective_multiples_match_the_affine_reference() {
        let order = secp_n();
        let mut scalars = vec![
            BigUint::one(),
            BigUint::from(2u8),
            BigUint::from(3u8),
            BigUint::from(0xffff_ffffu32),
            order - BigUint::one(),
            order - BigUint::from(2u8),
            order >> 1,
            BigUint::one() << 255,
        ];
        let mut seed = keccak256(b"dcex secp256k1 scalars");
        for _ in 0..24 {
            let scalar = BigUint::from_bytes_be(&seed) % order;
            if !scalar.is_zero() {
                scalars.push(scalar);
            }
            seed = keccak256(&seed);
        }
        for scalar in scalars {
            let expected = scalar_mul(&generator(), &scalar);
            assert_eq!(
                generator_multiple(&scalar),
                (expected.x, expected.y),
                "scalar {scalar:x}"
            );
        }
    }

    #[test]
    fn complete_addition_handles_identity_and_doubling() {
        let affine = |point: ProjectivePoint| {
            point
                .into_affine()
                .map(|(x, y)| (field_to_biguint(&x), field_to_biguint(&y)))
        };
        let g = ProjectivePoint::generator;
        let double = point_double(&generator()).expect("2G");
        let triple = point_add(&double, &generator()).expect("3G");

        assert_eq!(affine(g().add(&ProjectivePoint::IDENTITY)), affine(g()));
        assert_eq!(affine(ProjectivePoint::IDENTITY.add(&g())), affine(g()));
        assert_eq!(affine(g().add(&g())), Some((double.x, double.y)));
        assert_eq!(affine(g().add(&g()).add(&g())), Some((triple.x, triple.y)));
        assert!(affine(ProjectivePoint::IDENTITY.add(&ProjectivePoint::IDENTITY)).is_none());
        // n * G is the identity: (n - 1) * G + G.
        let order_minus_one = secp_n() - BigUint::one();
        let mut bytes = [0u8; 32];
        write_biguint_32(&order_minus_one, &mut bytes);
        let last = g().mul(&U256::from_be_slice(&bytes));
        assert!(affine(last.add(&g())).is_none());
    }

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
