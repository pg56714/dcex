//! Stark-curve primitives for Extended order signing: field elements, Starknet Poseidon,
//! RFC 6979 nonces and ECDSA signing.
//!
//! Field and scalar arithmetic run in constant-time Montgomery form, and scalar multiplication
//! uses complete projective formulas with a branch-free double-and-add, so the private key and
//! nonce never select a code path.

use std::fmt::{Debug, Display, Formatter};
use std::ops::{Add, AddAssign};
use std::sync::OnceLock;

use crypto_bigint::ctutils::CtLt;
use crypto_bigint::modular::ConstMontyForm;
use crypto_bigint::{CtAssign, U256, const_monty_params};
use hmac::{Hmac, KeyInit, Mac};
use num_bigint::BigUint;
use sha2::{Digest, Sha256};

const_monty_params!(
    FieldModulus,
    U256,
    "0800000000000011000000000000000000000000000000000000000000000001",
    "Stark field prime p = 2^251 + 17 * 2^192 + 1"
);
const_monty_params!(
    OrderModulus,
    U256,
    "0800000000000010ffffffffffffffffb781126dcae7b2321e66a241adc64d2f",
    "Stark curve group order n"
);

type Fp = ConstMontyForm<FieldModulus, { U256::LIMBS }>;
type Scalar = ConstMontyForm<OrderModulus, { U256::LIMBS }>;

const CURVE_ORDER: U256 =
    U256::from_be_hex("0800000000000010ffffffffffffffffb781126dcae7b2321e66a241adc64d2f");
/// Signature components and message hashes must stay below 2^251.
const ELEMENT_UPPER_BOUND: U256 =
    U256::from_be_hex("0800000000000000000000000000000000000000000000000000000000000000");
const CURVE_BETA: U256 =
    U256::from_be_hex("06f21413efbe40de150e596d72f7a8c5609ad26c15c915c1f4cdfcb99cee9e89");
/// 3 * beta mod p, used by the complete addition formulas.
const CURVE_B3: Fp = Fp::new(&U256::from_be_hex(
    "04d63c3bcf3ac2783f2b0c4858e6fa5021d07744415b4145de69f62cd6cbdb99",
));
const GENERATOR_X: U256 =
    U256::from_be_hex("01ef15c18599971b7beced415a40f0c7deacfd9b0d1819e03d723d8bc943cfca");
const GENERATOR_Y: U256 =
    U256::from_be_hex("005668060aa49730b7be4801df46ec62de53ecd11abe43a32873000c36e8dc1f");

const POSEIDON_FULL_ROUNDS: usize = 8;
const POSEIDON_PARTIAL_ROUNDS: usize = 83;
const POSEIDON_ROUNDS: usize = POSEIDON_FULL_ROUNDS + POSEIDON_PARTIAL_ROUNDS;

/// Element of the Stark prime field, always reduced below p.
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Felt(Fp);

impl Felt {
    pub const ZERO: Self = Self(Fp::ZERO);
    pub const ONE: Self = Self(Fp::ONE);

    /// Parses up to 64 hex digits with an optional `0x` prefix; values must be below p.
    pub fn from_hex(value: &str) -> std::result::Result<Self, &'static str> {
        let digits = match value.strip_prefix("0x") {
            Some(rest) if !rest.is_empty() => rest,
            _ => value,
        };
        if digits.is_empty() {
            return Err("empty hex string");
        }
        if !digits.bytes().all(|byte| byte.is_ascii_hexdigit()) {
            return Err("invalid hex string");
        }
        if digits.len() > 64 {
            return Err("hex string is too big");
        }
        let padded = format!("{digits:0>64}");
        let mut bytes = [0u8; 32];
        hex::decode_to_slice(padded, &mut bytes).map_err(|_| "invalid hex string")?;
        let value = U256::from_be_slice(&bytes);
        if !value.ct_lt(Fp::MODULUS.as_ref()).to_bool() {
            return Err("value is not below the Stark field prime");
        }
        Ok(Self(Fp::new(&value)))
    }

    /// Interprets 32 big-endian bytes as an integer reduced modulo p.
    pub fn from_bytes_be(bytes: &[u8; 32]) -> Self {
        Self(Fp::new(&U256::from_be_slice(bytes)))
    }

    pub fn to_bytes_be(&self) -> [u8; 32] {
        uint_to_bytes(&self.0.retrieve())
    }

    /// Lowercase hex with a `0x` prefix and no leading zeros.
    pub fn to_hex_string(&self) -> String {
        let encoded = hex::encode(self.to_bytes_be());
        let trimmed = encoded.trim_start_matches('0');
        if trimmed.is_empty() {
            "0x0".to_string()
        } else {
            format!("0x{trimmed}")
        }
    }

    fn to_uint(self) -> U256 {
        self.0.retrieve()
    }
}

impl Display for Felt {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", BigUint::from_bytes_be(&self.to_bytes_be()))
    }
}

impl Debug for Felt {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.to_hex_string())
    }
}

impl From<u32> for Felt {
    fn from(value: u32) -> Self {
        Self::from(u64::from(value))
    }
}

impl From<u64> for Felt {
    fn from(value: u64) -> Self {
        Self(Fp::new(&U256::from_u64(value)))
    }
}

/// Negative values map to p - |value|.
impl From<i64> for Felt {
    fn from(value: i64) -> Self {
        let magnitude = Self::from(value.unsigned_abs());
        if value < 0 {
            Self(magnitude.0.neg())
        } else {
            magnitude
        }
    }
}

impl Add for Felt {
    type Output = Self;

    fn add(self, rhs: Self) -> Self {
        Self(self.0.add(&rhs.0))
    }
}

impl AddAssign for Felt {
    fn add_assign(&mut self, rhs: Self) {
        self.0 = self.0.add(&rhs.0);
    }
}

/// Sponge over the Starknet Hades permutation (rate 2, capacity 1), matching
/// `poseidon_hash_many` with its `1` padding.
#[derive(Clone, Default)]
pub struct PoseidonHasher {
    state: [Fp; 3],
    buffer: Option<Fp>,
}

impl PoseidonHasher {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn update(&mut self, message: Felt) {
        match self.buffer.take() {
            Some(previous) => {
                self.state[0] = self.state[0].add(&previous);
                self.state[1] = self.state[1].add(&message.0);
                hades_permutation(&mut self.state);
            }
            None => self.buffer = Some(message.0),
        }
    }

    pub fn finalize(mut self) -> Felt {
        match self.buffer.take() {
            Some(last) => {
                self.state[0] = self.state[0].add(&last);
                self.state[1] = self.state[1].add(&Fp::ONE);
            }
            None => self.state[0] = self.state[0].add(&Fp::ONE),
        }
        hades_permutation(&mut self.state);
        Felt(self.state[0])
    }
}

/// Round constants from cairo-lang: `sha256("Hades{index}") mod p`.
fn poseidon_round_constants() -> &'static [[Fp; 3]; POSEIDON_ROUNDS] {
    static CONSTANTS: OnceLock<[[Fp; 3]; POSEIDON_ROUNDS]> = OnceLock::new();
    CONSTANTS.get_or_init(|| {
        let mut constants = [[Fp::ZERO; 3]; POSEIDON_ROUNDS];
        for (round, row) in constants.iter_mut().enumerate() {
            for (column, constant) in row.iter_mut().enumerate() {
                let digest: [u8; 32] =
                    Sha256::digest(format!("Hades{}", round * 3 + column)).into();
                *constant = Felt::from_bytes_be(&digest).0;
            }
        }
        constants
    })
}

fn hades_permutation(state: &mut [Fp; 3]) {
    let half_full_rounds = POSEIDON_FULL_ROUNDS / 2;
    for (round, constants) in poseidon_round_constants().iter().enumerate() {
        for (value, constant) in state.iter_mut().zip(constants) {
            *value = value.add(constant);
        }
        if round < half_full_rounds || round >= half_full_rounds + POSEIDON_PARTIAL_ROUNDS {
            for value in state.iter_mut() {
                *value = cube(value);
            }
        } else {
            state[2] = cube(&state[2]);
        }
        // MDS matrix [[3, 1, 1], [1, -1, 1], [1, 1, -2]].
        let sum = state[0].add(&state[1]).add(&state[2]);
        state[0] = sum.add(&state[0].double());
        state[1] = sum.sub(&state[1].double());
        state[2] = sum.sub(&state[2].double().add(&state[2]));
    }
}

fn cube(value: &Fp) -> Fp {
    value.square().mul(value)
}

/// Deterministic nonce per RFC 6979 (HMAC-SHA256), with the 256-bit candidate shifted right by
/// 4 bits as cairo-lang and starknet-crypto do. `seed` adds extra entropy for retries.
pub fn rfc6979_generate_k(message_hash: &Felt, private_key: &Felt, seed: Option<&Felt>) -> Felt {
    let private_key = private_key.to_bytes_be();
    let message_hash = message_hash.to_bytes_be();
    let seed_bytes = seed.map(Felt::to_bytes_be).unwrap_or([0u8; 32]);
    let seed_start = seed_bytes
        .iter()
        .position(|byte| *byte != 0)
        .unwrap_or(seed_bytes.len());
    let extra = &seed_bytes[seed_start..];

    let mut key = [0u8; 32];
    let mut value = [1u8; 32];
    for separator in [0u8, 1] {
        key = hmac_sha256_parts(
            &key,
            &[&value, &[separator], &private_key, &message_hash, extra],
        );
        value = hmac_sha256_parts(&key, &[&value]);
    }
    loop {
        value = hmac_sha256_parts(&key, &[&value]);
        let candidate = U256::from_be_slice(&value).shr(4);
        let in_range = (!candidate.is_zero()) & candidate.ct_lt(&CURVE_ORDER);
        if in_range.to_bool() {
            return Felt(Fp::new(&candidate));
        }
        key = hmac_sha256_parts(&key, &[&value, &[0]]);
        value = hmac_sha256_parts(&key, &[&value]);
    }
}

fn hmac_sha256_parts(key: &[u8], parts: &[&[u8]]) -> [u8; 32] {
    let mut mac = Hmac::<Sha256>::new_from_slice(key).expect("HMAC accepts any key length");
    for part in parts {
        mac.update(part);
    }
    mac.finalize().into_bytes().into()
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SignError {
    InvalidMessageHash,
    InvalidK,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Signature {
    pub r: Felt,
    pub s: Felt,
}

/// Stark ECDSA: r = x(k * G), s = (message + r * private_key) / k mod n.
pub fn sign(
    private_key: &Felt,
    message: &Felt,
    k: &Felt,
) -> std::result::Result<Signature, SignError> {
    if !below_element_bound(*message) {
        return Err(SignError::InvalidMessageHash);
    }
    if *k == Felt::ZERO {
        return Err(SignError::InvalidK);
    }

    let (r, _) = ProjectivePoint::generator()
        .mul(&k.to_uint())
        .to_affine()
        .ok_or(SignError::InvalidK)?;
    let r = Felt(r);
    if r == Felt::ZERO || !below_element_bound(r) {
        return Err(SignError::InvalidK);
    }

    let k_inverse =
        Option::<Scalar>::from(Scalar::new(&k.to_uint()).invert()).ok_or(SignError::InvalidK)?;
    let s = Scalar::new(&r.to_uint())
        .mul(&Scalar::new(&private_key.to_uint()))
        .add(&Scalar::new(&message.to_uint()))
        .mul(&k_inverse)
        .retrieve();
    let s = Felt(Fp::new(&s));
    if s == Felt::ZERO || !below_element_bound(s) {
        return Err(SignError::InvalidK);
    }
    Ok(Signature { r, s })
}

fn below_element_bound(value: Felt) -> bool {
    value.to_uint().ct_lt(&ELEMENT_UPPER_BOUND).to_bool()
}

/// Projective point on y^2 = x^3 + x + beta; the identity is (0, 1, 0).
#[derive(Clone, Copy)]
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

    /// Complete addition for short Weierstrass curves with a = 1 (Renes, Costello and Batina
    /// 2016, algorithm 1); also valid for doubling and the identity, so it never branches.
    fn add(&self, other: &Self) -> Self {
        let (x1, y1, z1) = (self.x, self.y, self.z);
        let (x2, y2, z2) = (other.x, other.y, other.z);

        let mut t0 = x1.mul(&x2);
        let mut t1 = y1.mul(&y2);
        let mut t2 = z1.mul(&z2);
        let mut t3 = x1.add(&y1).mul(&x2.add(&y2));
        let mut t4 = t0.add(&t1);
        t3 = t3.sub(&t4);
        t4 = x1.add(&z1).mul(&x2.add(&z2));
        let mut t5 = t0.add(&t2);
        t4 = t4.sub(&t5);
        t5 = y1.add(&z1).mul(&y2.add(&z2));
        let mut x3 = t1.add(&t2);
        t5 = t5.sub(&x3);
        let mut z3 = t4;
        x3 = CURVE_B3.mul(&t2);
        z3 = x3.add(&z3);
        x3 = t1.sub(&z3);
        z3 = t1.add(&z3);
        let mut y3 = x3.mul(&z3);
        t1 = t0.double().add(&t0);
        t4 = CURVE_B3.mul(&t4);
        t1 = t1.add(&t2);
        t2 = t0.sub(&t2);
        t4 = t4.add(&t2);
        t0 = t1.mul(&t4);
        y3 = y3.add(&t0);
        t0 = t5.mul(&t4);
        x3 = t3.mul(&x3);
        x3 = x3.sub(&t0);
        t0 = t3.mul(&t1);
        z3 = t5.mul(&z3);
        z3 = z3.add(&t0);

        Self {
            x: x3,
            y: y3,
            z: z3,
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
    fn to_affine(self) -> Option<(Fp, Fp)> {
        let z_inverse = Option::<Fp>::from(self.z.invert())?;
        Some((self.x.mul(&z_inverse), self.y.mul(&z_inverse)))
    }
}

fn uint_to_bytes(value: &U256) -> [u8; 32] {
    let mut bytes = [0u8; 32];
    bytes.copy_from_slice(&value.to_be_bytes());
    bytes
}

#[cfg(test)]
mod tests {
    use super::*;

    fn felt(value: &str) -> Felt {
        Felt::from_hex(value).unwrap()
    }

    fn public_key(private_key: &Felt) -> Felt {
        let (x, _) = ProjectivePoint::generator()
            .mul(&private_key.to_uint())
            .to_affine()
            .unwrap();
        Felt(x)
    }

    #[test]
    fn felt_parsing_and_formatting_match_starknet_types() {
        assert_eq!(felt("0x0").to_hex_string(), "0x0");
        assert_eq!(felt("0x00ab").to_hex_string(), "0xab");
        assert_eq!(felt("AB").to_hex_string(), "0xab");
        assert_eq!(felt("0x1").to_string(), "1");
        // Values at or above p are rejected, while byte input is reduced.
        assert!(
            Felt::from_hex("0x800000000000011000000000000000000000000000000000000000000000001")
                .is_err()
        );
        assert_eq!(
            felt("0x800000000000011000000000000000000000000000000000000000000000000") + Felt::ONE,
            Felt::ZERO
        );
        let mut p_plus_one = [0u8; 32];
        hex::decode_to_slice(
            "0800000000000011000000000000000000000000000000000000000000000002",
            &mut p_plus_one,
        )
        .unwrap();
        assert_eq!(Felt::from_bytes_be(&p_plus_one), Felt::ONE);
        assert_eq!(
            Felt::from(-1i64).to_hex_string(),
            "0x800000000000011000000000000000000000000000000000000000000000000"
        );
        assert_eq!(Felt::from(-1i64) + Felt::ONE, Felt::ZERO);
        assert!(Felt::from_hex("").is_err());
        assert!(Felt::from_hex("0x").is_err());
        assert!(Felt::from_hex("0xzz").is_err());
        assert!(Felt::from_hex(&format!("0x{}", "1".repeat(65))).is_err());
    }

    #[test]
    fn generator_is_on_curve_and_has_curve_order() {
        let generator = ProjectivePoint::generator();
        let (x, y) = generator.to_affine().unwrap();
        let rhs = x.square().mul(&x).add(&x).add(&Fp::new(&CURVE_BETA));
        assert_eq!(y.square(), rhs);
        let beta = Fp::new(&CURVE_BETA);
        assert_eq!(CURVE_B3, beta.double().add(&beta));
        assert!(generator.mul(&CURVE_ORDER).to_affine().is_none());
        let doubled = generator.add(&generator).to_affine().unwrap();
        assert_eq!(
            generator.mul(&U256::from_u64(2)).to_affine().unwrap(),
            doubled
        );
    }

    #[test]
    fn public_key_matches_known_stark_key_pair() {
        // starknet-crypto `get_public_key` test vectors.
        assert_eq!(
            public_key(&felt(
                "0x03c1e9550e66958296d11b60f8e8e7a7ad990d07fa65d5f7652c4a6c87d4e3cc"
            )),
            felt("0x077a3b314db07c45076d11f62b6f9e748a39790441823307743cf00d6597ea43")
        );
        assert_eq!(
            public_key(&felt("0x12")),
            felt("0x019661066e96a8b9f06a1d136881ee924dfb6a885239caa5fd3f87a54c6b25c4")
        );
    }

    #[test]
    fn hades_permutation_matches_reference_vector() {
        let mut state = [felt("0x9").0, felt("0xb").0, felt("0x2").0];
        hades_permutation(&mut state);
        assert_eq!(
            state.map(|value| Felt(value).to_hex_string()),
            [
                "0x510f3a3faf4084e3b1e95fd44c30746271b48723f7ea9c8be6a9b6b5408e7e6",
                "0x4f511749bd4101266904288021211333fb0a514cb15381af087462fa46e6bd9",
                "0x186f6dd1a6e79cb1b66d505574c349272cd35c07c223351a0990410798bb9d8",
            ]
        );
    }

    #[test]
    fn nonce_and_signature_match_starknet_crypto_vectors() {
        // Generated with starknet-crypto 0.8.1 before it was replaced.
        let vectors = [
            (
                "0x11af3c801d3f78137f603aebb81902e5082ba59858b588e343c67726439adbf",
                "0x6c1259cebd03c2a08381e8c8c29d6d2b3d1172b466071ffbe271a86db772edc",
                None,
                "0x776bbdb51f80a1690c91812609c583cc9e88477bebc38e74472b39cd7f6e4bf",
                "0x31fdc17b21cf53ccbbf736a5e73d3b9a40c12b44d64854d5feef9c9c5d2c7ac",
                "0x6b1a7289906f51bff80f93fd37fbb00227c76110f9c6a66671135bd68f0e894",
            ),
            (
                "0x4716e1e6ced8126ccb870213498f7f59f07b27a78869b5ab0ba91e47f6200eb",
                "0x486b3d3cdbdf6136d0844c269e7693f3681da7f6993082d5b928e2c987d857d",
                Some("0xc72b4c36d0db7fed"),
                "0x1c0b8a2d5f75319f98d698ba9fad251b78572cecd5906f4d9f336780c4169bb",
                "0x6416371546b6a0c5a8973a749043c976f63caee0a8df3380820b937cbf3f39d",
                "0x441999b0127795f3f8e49511280591b87b7accfb11bbadb829a9e7ee15e2050",
            ),
            (
                "0x8c963fec9930413938db73f7c63261339247122b630645bf738c03552ef109",
                "0x142b62177b913c2c59667325ba0d165915f56001e016987adbf0dc4667fea94",
                None,
                "0x2691abec7e42dea2daf42ea0abced4995ec4e95ab92796d4e21bac6d11b21c",
                "0x785d8593e94ce542c0f3f278e82edc34b795ed7987251b943393142c7d58da0",
                "0x16c4b60723eb4297e201112150ca3fc0e0b4e9f10025738eaffd012fc20b99c",
            ),
            (
                "0x24e33be0e0963ae6fd639ef214a7eb8bd41cefd6aca44453b518b6fa91c618c",
                "0x415c013ef24eccd3126aa3cf0f03654093c91e735a6c338754ce389cb6640be",
                Some("0x7497c7f897b9a0e"),
                "0x3aea5333f08b07ed77326a7d9f28e6d293f44d7416d2417d36aced90094cb24",
                "0x494c158ebd19bf9d114da230ae6220bc1f6771228dd17e4d1f15f1969560f1b",
                "0x229861ebc80e03917e4569e7ab8cd095858a714ad39781045658b09c45bf95f",
            ),
        ];
        for (message, private_key, seed, k, r, s) in vectors {
            let (message, private_key) = (felt(message), felt(private_key));
            let seed = seed.map(felt);
            let nonce = rfc6979_generate_k(&message, &private_key, seed.as_ref());
            assert_eq!(nonce, felt(k));
            let signature = sign(&private_key, &message, &nonce).unwrap();
            assert_eq!(signature.r, felt(r));
            assert_eq!(signature.s, felt(s));
        }
    }

    #[test]
    fn signing_rejects_message_hash_out_of_range() {
        assert_eq!(
            sign(
                &Felt::ONE,
                &felt("0x800000000000000000000000000000000000000000000000000000000000000"),
                &Felt::ONE,
            ),
            Err(SignError::InvalidMessageHash)
        );
        assert_eq!(
            sign(&Felt::ONE, &Felt::ONE, &Felt::ZERO),
            Err(SignError::InvalidK)
        );
    }
}
