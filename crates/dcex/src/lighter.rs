use num_bigint::BigUint;
use num_traits::Zero;
use std::sync::OnceLock;

use base64::Engine;
use serde_json::{Map, Value};

use crate::{DcexError, Result};

const GOLDILOCKS_ORDER: u64 = 0xffff_ffff_0000_0001;
const GOLDILOCKS_EPSILON: u64 = 0xffff_ffff;
const FP5_ROOT: u64 = 1_041_288_259_238_279_555;
const FP5_ZERO: Fp5 = [0, 0, 0, 0, 0];
const FP5_ONE: Fp5 = [1, 0, 0, 0, 0];
const SCALAR_ORDER_DECIMAL: &[u8] =
    b"106799351671714695104148491657179270274505774058172723015913968518\
5762082554198619328292418486241";

type Fp5 = [u64; 5];

const EXTERNAL_CONSTANTS: [[u64; 12]; 8] = [
    [
        15492826721047263190,
        11728330187201910315,
        8836021247773420868,
        16777404051263952451,
        5510875212538051896,
        6173089941271892285,
        2927757366422211339,
        10340958981325008808,
        8541987352684552425,
        9739599543776434497,
        15073950188101532019,
        12084856431752384512,
    ],
    [
        4584713381960671270,
        8807052963476652830,
        54136601502601741,
        4872702333905478703,
        5551030319979516287,
        12889366755535460989,
        16329242193178844328,
        412018088475211848,
        10505784623379650541,
        9758812378619434837,
        7421979329386275117,
        375240370024755551,
    ],
    [
        3331431125640721931,
        15684937309956309981,
        578521833432107983,
        14379242000670861838,
        17922409828154900976,
        8153494278429192257,
        15904673920630731971,
        11217863998460634216,
        3301540195510742136,
        9937973023749922003,
        3059102938155026419,
        1895288289490976132,
    ],
    [
        5580912693628927540,
        10064804080494788323,
        9582481583369602410,
        10186259561546797986,
        247426333829703916,
        13193193905461376067,
        6386232593701758044,
        17954717245501896472,
        1531720443376282699,
        2455761864255501970,
        11234429217864304495,
        4746959618548874102,
    ],
    [
        13571697342473846203,
        17477857865056504753,
        15963032953523553760,
        16033593225279635898,
        14252634232868282405,
        8219748254835277737,
        7459165569491914711,
        15855939513193752003,
        16788866461340278896,
        7102224659693946577,
        3024718005636976471,
        13695468978618890430,
    ],
    [
        8214202050877825436,
        2670727992739346204,
        16259532062589659211,
        11869922396257088411,
        3179482916972760137,
        13525476046633427808,
        3217337278042947412,
        14494689598654046340,
        15837379330312175383,
        8029037639801151344,
        2153456285263517937,
        8301106462311849241,
    ],
    [
        13294194396455217955,
        17394768489610594315,
        12847609130464867455,
        14015739446356528640,
        5879251655839607853,
        9747000124977436185,
        8950393546890284269,
        10765765936405694368,
        14695323910334139959,
        16366254691123000864,
        15292774414889043182,
        10910394433429313384,
    ],
    [
        17253424460214596184,
        3442854447664030446,
        3005570425335613727,
        10859158614900201063,
        9763230642109343539,
        6647722546511515039,
        909012944955815706,
        18101204076790399111,
        11588128829349125809,
        15863878496612806566,
        5201119062417750399,
        176665553780565743,
    ],
];

const INTERNAL_CONSTANTS: [u64; 22] = [
    11921381764981422944,
    10318423381711320787,
    8291411502347000766,
    229948027109387563,
    9152521390190983261,
    7129306032690285515,
    15395989607365232011,
    8641397269074305925,
    17256848792241043600,
    6046475228902245682,
    12041608676381094092,
    12785542378683951657,
    14546032085337914034,
    3304199118235116851,
    16499627707072547655,
    10386478025625759321,
    13475579315436919170,
    16042710511297532028,
    1411266850385657080,
    9024840976168649958,
    14047056970978379368,
    838728605080212101,
];

const MATRIX_DIAGONAL: [u64; 12] = [
    0xc3b6c08e23ba9300,
    0xd84b5de94a324fb6,
    0x0d0c371c5b35b84f,
    0x7964f570e7188037,
    0x5daf18bbd996604b,
    0x6743bc47b9595257,
    0x05528b9362c59bb70,
    0xac45e25b7127b68b,
    0xa2077d7dfbb606b5,
    0xf3faac6faee378ae,
    0x0c6388b51545e883,
    0xd27dbb6944917b60,
];

const GENERATOR_X: Fp5 = [
    12883135586176881569,
    4356519642755055268,
    5248930565894896907,
    2165973894480315022,
    2448410071095648785,
];

#[derive(Clone, Copy)]
struct Point {
    x: Fp5,
    z: Fp5,
    u: Fp5,
    t: Fp5,
}

const NEUTRAL: Point = Point {
    x: FP5_ZERO,
    z: FP5_ONE,
    u: FP5_ZERO,
    t: FP5_ONE,
};

const GENERATOR: Point = Point {
    x: GENERATOR_X,
    z: FP5_ONE,
    u: FP5_ONE,
    t: [4, 0, 0, 0, 0],
};

fn scalar_order() -> &'static BigUint {
    static VALUE: OnceLock<BigUint> = OnceLock::new();
    VALUE
        .get_or_init(|| BigUint::parse_bytes(SCALAR_ORDER_DECIMAL, 10).expect("valid scalar order"))
}

fn field(value: u64) -> u64 {
    value % GOLDILOCKS_ORDER
}

fn add_mod(left: u64, right: u64) -> u64 {
    let (sum, carry) = left.overflowing_add(right);
    let reduced = if carry {
        sum.wrapping_add(GOLDILOCKS_EPSILON)
    } else {
        sum
    };
    if reduced >= GOLDILOCKS_ORDER {
        reduced - GOLDILOCKS_ORDER
    } else {
        reduced
    }
}

fn sub_mod(left: u64, right: u64) -> u64 {
    let (difference, borrow) = left.overflowing_sub(right);
    if borrow {
        difference.wrapping_sub(GOLDILOCKS_EPSILON)
    } else {
        difference
    }
}

fn mul_mod(left: u64, right: u64) -> u64 {
    reduce_u128(left as u128 * right as u128)
}

fn reduce_u128(value: u128) -> u64 {
    let low = value as u64;
    let high = (value >> 64) as u64;
    let high_low = high & GOLDILOCKS_EPSILON;
    let high_high = high >> 32;

    let (difference, borrow) = low.overflowing_sub(high_high);
    let difference = if borrow {
        difference.wrapping_sub(GOLDILOCKS_EPSILON)
    } else {
        difference
    };
    add_mod(difference, high_low * GOLDILOCKS_EPSILON)
}

fn pow_mod(mut base: u64, mut exponent: u64) -> u64 {
    let mut result = 1u64;
    while exponent != 0 {
        if exponent & 1 == 1 {
            result = mul_mod(result, base);
        }
        base = mul_mod(base, base);
        exponent >>= 1;
    }
    result
}

fn fp5_add(left: &Fp5, right: &Fp5) -> Fp5 {
    let mut result = [0u64; 5];
    for index in 0..5 {
        result[index] = add_mod(left[index], right[index]);
    }
    result
}

fn fp5_sub(left: &Fp5, right: &Fp5) -> Fp5 {
    let mut result = [0u64; 5];
    for index in 0..5 {
        result[index] = sub_mod(left[index], right[index]);
    }
    result
}

fn fp5_mul(left: &Fp5, right: &Fp5) -> Fp5 {
    let mut product = [0u64; 9];
    for (left_index, left_limb) in left.iter().enumerate() {
        for (right_index, right_limb) in right.iter().enumerate() {
            let index = left_index + right_index;
            product[index] = add_mod(product[index], mul_mod(*left_limb, *right_limb));
        }
    }
    for degree in (5..=8).rev() {
        product[degree - 5] = add_mod(product[degree - 5], mul_mod(3, product[degree]));
    }
    [product[0], product[1], product[2], product[3], product[4]]
}

fn fp5_square(value: &Fp5) -> Fp5 {
    fp5_mul(value, value)
}

fn fp5_scalar_mul(value: &Fp5, scalar: u64) -> Fp5 {
    let mut result = [0u64; 5];
    for index in 0..5 {
        result[index] = mul_mod(value[index], scalar);
    }
    result
}

fn fp5_frobenius(value: &Fp5, count: usize) -> Fp5 {
    let count = count % 5;
    if count == 0 {
        return *value;
    }
    let root = pow_mod(FP5_ROOT, count as u64);
    let mut factor = 1u64;
    let mut result = [0u64; 5];
    for (index, limb) in value.iter().enumerate() {
        result[index] = mul_mod(*limb, factor);
        factor = mul_mod(factor, root);
    }
    result
}

fn fp5_inv(value: &Fp5) -> Fp5 {
    if *value == FP5_ZERO {
        return FP5_ZERO;
    }
    let d = fp5_frobenius(value, 1);
    let e = fp5_mul(&d, &fp5_frobenius(&d, 1));
    let f = fp5_mul(&e, &fp5_frobenius(&e, 2));
    let norm = fp5_mul(value, &f)[0];
    fp5_scalar_mul(&f, pow_mod(norm, GOLDILOCKS_ORDER - 2))
}

fn encode_fp5(value: &Fp5) -> [u8; 40] {
    let mut out = [0u8; 40];
    for (index, limb) in value.iter().enumerate() {
        out[index * 8..(index + 1) * 8].copy_from_slice(&limb.to_le_bytes());
    }
    out
}

fn external_linear_layer(state: &mut [u64; 12]) {
    for offset in [0usize, 4, 8] {
        let x0 = state[offset];
        let x1 = state[offset + 1];
        let x2 = state[offset + 2];
        let x3 = state[offset + 3];
        let t01 = add_mod(x0, x1);
        let t23 = add_mod(x2, x3);
        let total = add_mod(t01, t23);
        state[offset] = add_mod(add_mod(total, t01), x1);
        state[offset + 1] = add_mod(add_mod(total, x1), mul_mod(2, x2));
        state[offset + 2] = add_mod(add_mod(total, t23), x3);
        state[offset + 3] = add_mod(add_mod(total, x3), mul_mod(2, x0));
    }
    let mut sums = [0u64; 4];
    for index in 0..4 {
        sums[index] = add_mod(add_mod(state[index], state[index + 4]), state[index + 8]);
    }
    for index in 0..12 {
        state[index] = add_mod(state[index], sums[index % 4]);
    }
}

fn internal_linear_layer(state: &mut [u64; 12]) {
    let mut total = 0u64;
    for value in state.iter() {
        total = add_mod(total, *value);
    }
    for (index, diagonal) in MATRIX_DIAGONAL.iter().enumerate() {
        state[index] = add_mod(total, mul_mod(state[index], *diagonal));
    }
}

fn poseidon_permute(state: &mut [u64; 12]) {
    external_linear_layer(state);
    for round_index in 0..4 {
        for index in 0..12 {
            state[index] = add_mod(state[index], EXTERNAL_CONSTANTS[round_index][index]);
            state[index] = pow_mod(state[index], 7);
        }
        external_linear_layer(state);
    }
    for constant in INTERNAL_CONSTANTS {
        state[0] = add_mod(state[0], constant);
        state[0] = pow_mod(state[0], 7);
        internal_linear_layer(state);
    }
    for round_index in 4..8 {
        for index in 0..12 {
            state[index] = add_mod(state[index], EXTERNAL_CONSTANTS[round_index][index]);
            state[index] = pow_mod(state[index], 7);
        }
        external_linear_layer(state);
    }
}

fn poseidon_hash(values: &[u64], output_count: usize) -> Vec<u64> {
    let mut state = [0u64; 12];
    for chunk in values.chunks(8) {
        for (index, value) in chunk.iter().enumerate() {
            state[index] = field(*value);
        }
        poseidon_permute(&mut state);
    }
    let mut output = Vec::with_capacity(output_count);
    while output.len() < output_count {
        let remaining = output_count - output.len();
        output.extend_from_slice(&state[..remaining.min(8)]);
        if output.len() < output_count {
            poseidon_permute(&mut state);
        }
    }
    output
}

impl Point {
    fn add(&self, other: &Self) -> Self {
        let t1 = fp5_mul(&self.x, &other.x);
        let t2 = fp5_mul(&self.z, &other.z);
        let t3 = fp5_mul(&self.u, &other.u);
        let t4 = fp5_mul(&self.t, &other.t);
        let t5 = fp5_sub(
            &fp5_mul(&fp5_add(&self.x, &self.z), &fp5_add(&other.x, &other.z)),
            &fp5_add(&t1, &t2),
        );
        let t6 = fp5_sub(
            &fp5_mul(&fp5_add(&self.u, &self.t), &fp5_add(&other.u, &other.t)),
            &fp5_add(&t3, &t4),
        );
        let curve_b = [0, 263, 0, 0, 0];
        let curve_b_times_two = [0, 526, 0, 0, 0];
        let t7 = fp5_add(&t1, &fp5_mul(&t2, &curve_b));
        let t8 = fp5_mul(&t4, &t7);
        let t9 = fp5_mul(
            &t3,
            &fp5_add(&fp5_mul(&t5, &curve_b_times_two), &fp5_scalar_mul(&t7, 2)),
        );
        let t10 = fp5_mul(&fp5_add(&t4, &fp5_scalar_mul(&t3, 2)), &fp5_add(&t5, &t7));
        Self {
            x: fp5_mul(&fp5_sub(&t10, &t8), &curve_b),
            z: fp5_sub(&t8, &t9),
            u: fp5_mul(&t6, &fp5_sub(&fp5_mul(&t2, &curve_b), &t1)),
            t: fp5_add(&t8, &t9),
        }
    }

    fn double(&self) -> Self {
        let t1 = fp5_mul(&self.z, &self.t);
        let t2 = fp5_mul(&t1, &self.t);
        let x1 = fp5_square(&t2);
        let z1 = fp5_mul(&t1, &self.u);
        let t3 = fp5_square(&self.u);
        let w1 = fp5_sub(
            &t2,
            &fp5_mul(&t3, &fp5_scalar_mul(&fp5_add(&self.x, &self.z), 2)),
        );
        let t4 = fp5_square(&z1);
        Self {
            x: fp5_mul(&t4, &[0, 1052, 0, 0, 0]),
            z: fp5_square(&w1),
            u: fp5_sub(
                &fp5_square(&fp5_add(&w1, &z1)),
                &fp5_add(&t4, &fp5_square(&w1)),
            ),
            t: fp5_sub(
                &fp5_scalar_mul(&x1, 2),
                &fp5_add(&fp5_scalar_mul(&t4, 4), &fp5_square(&w1)),
            ),
        }
    }

    fn encode(&self) -> Fp5 {
        fp5_mul(&self.t, &fp5_inv(&self.u))
    }
}

fn generator_table() -> &'static Vec<[Point; 16]> {
    static TABLE: OnceLock<Vec<[Point; 16]>> = OnceLock::new();
    TABLE.get_or_init(|| {
        let mut windows = Vec::with_capacity(80);
        let mut base = GENERATOR;
        for _ in 0..80 {
            let mut table = [NEUTRAL; 16];
            table[1] = base;
            for index in 2..16 {
                table[index] = table[index - 1].add(&base);
            }
            windows.push(table);
            for _ in 0..4 {
                base = base.double();
            }
        }
        windows
    })
}

fn generator_mul(scalar: &BigUint) -> Point {
    let bytes = scalar.to_bytes_le();
    let mut result = NEUTRAL;
    for (window_index, table) in generator_table().iter().enumerate() {
        let byte = bytes.get(window_index / 2).copied().unwrap_or_default();
        let digit = if window_index % 2 == 0 {
            byte & 0x0f
        } else {
            byte >> 4
        };
        if digit != 0 {
            result = result.add(&table[digit as usize]);
        }
    }
    result
}

pub fn scalar_from_bytes(value: &[u8], name: &str) -> Result<BigUint> {
    if value.len() != 40 {
        return Err(DcexError::InvalidInput(format!(
            "{name} must contain exactly 40 bytes."
        )));
    }
    let scalar = BigUint::from_bytes_le(value) % scalar_order();
    if scalar.is_zero() {
        return Err(DcexError::InvalidInput(format!(
            "{name} is outside the valid range."
        )));
    }
    Ok(scalar)
}

pub fn private_key_from_bytes(private_key: &[u8]) -> Result<BigUint> {
    if private_key.len() != 40 {
        return Err(DcexError::InvalidInput(
            "Lighter API private key must contain exactly 40 bytes.".to_string(),
        ));
    }
    let scalar = BigUint::from_bytes_le(private_key) % scalar_order();
    if scalar.is_zero() {
        return Err(DcexError::InvalidInput(
            "Lighter API private key must not reduce to zero.".to_string(),
        ));
    }
    Ok(scalar)
}

pub fn public_key_bytes(private_key: &BigUint) -> Result<[u8; 40]> {
    if private_key.is_zero() || private_key >= scalar_order() {
        return Err(DcexError::InvalidInput(
            "Lighter private scalar is outside the valid range.".to_string(),
        ));
    }
    Ok(encode_fp5(&generator_mul(private_key).encode()))
}

pub fn poseidon_hash_bytes(values: &[u64]) -> [u8; 40] {
    let hash = poseidon_hash(values, 5);
    encode_fp5(&[hash[0], hash[1], hash[2], hash[3], hash[4]])
}

pub fn transaction_hash(values: &[i128], attributes: &[(u64, u64)]) -> [u8; 40] {
    let values = values.iter().map(|value| *value as u64).collect::<Vec<_>>();
    let transaction_hash = poseidon_hash_bytes(&values);
    if attributes.is_empty() {
        return transaction_hash;
    }

    let mut attributes = attributes.to_vec();
    attributes.sort_by_key(|(attribute_type, _)| *attribute_type);
    attributes.truncate(4);
    let mut attribute_values = Vec::with_capacity(8);
    for index in 0..4 {
        if let Some((attribute_type, value)) = attributes.get(index) {
            attribute_values.extend_from_slice(&[*attribute_type, *value]);
        } else {
            attribute_values.extend_from_slice(&[0, 0]);
        }
    }
    let attributes_hash = poseidon_hash_bytes(&attribute_values);
    let combined = transaction_hash
        .chunks_exact(8)
        .chain(attributes_hash.chunks_exact(8))
        .map(|chunk| u64::from_le_bytes(chunk.try_into().expect("8-byte chunk")))
        .collect::<Vec<_>>();
    poseidon_hash_bytes(&combined)
}

pub fn sign_transaction_payload(
    values: &[i128],
    attributes: &[(u64, u64)],
    payload_json: &[u8],
    private_key: &[u8],
    nonce: &[u8],
) -> Result<(Vec<u8>, [u8; 40])> {
    let message_hash = transaction_hash(values, attributes);
    let private_key = private_key_from_bytes(private_key)?;
    let nonce = scalar_from_bytes(nonce, "Lighter nonce scalar")?;
    let signature = schnorr_sign_with_nonce(&message_hash, &private_key, &nonce)?;
    let mut payload: Value = serde_json::from_slice(payload_json)
        .map_err(|error| DcexError::Decode(error.to_string()))?;
    let payload = payload.as_object_mut().ok_or_else(|| {
        DcexError::InvalidInput("Lighter transaction payload must be a JSON object.".to_string())
    })?;
    payload.insert(
        "Sig".to_string(),
        Value::String(base64::engine::general_purpose::STANDARD.encode(signature)),
    );
    if attributes.is_empty() {
        payload.insert("L2TxAttributes".to_string(), Value::Null);
    } else {
        let attributes = attributes
            .iter()
            .map(|(key, value)| (key.to_string(), Value::from(*value)))
            .collect::<Map<_, _>>();
        payload.insert("L2TxAttributes".to_string(), Value::Object(attributes));
    }
    let payload =
        serde_json::to_vec(&payload).map_err(|error| DcexError::Decode(error.to_string()))?;
    Ok((payload, message_hash))
}

pub fn auth_token(
    expiry: u64,
    account_index: u64,
    api_key_index: u64,
    private_key: &[u8],
    nonce: &[u8],
) -> Result<String> {
    let message = format!("{expiry}:{account_index}:{api_key_index}");
    let fields = message
        .as_bytes()
        .chunks(8)
        .map(|chunk| {
            let mut bytes = [0u8; 8];
            bytes[..chunk.len()].copy_from_slice(chunk);
            u64::from_le_bytes(bytes)
        })
        .collect::<Vec<_>>();
    let message_hash = poseidon_hash_bytes(&fields);
    let private_key = private_key_from_bytes(private_key)?;
    let nonce = scalar_from_bytes(nonce, "Lighter nonce scalar")?;
    let signature = schnorr_sign_with_nonce(&message_hash, &private_key, &nonce)?;
    Ok(format!("{message}:{}", hex::encode(signature)))
}

pub fn schnorr_sign_with_nonce(
    message_hash: &[u8],
    private_key: &BigUint,
    nonce: &BigUint,
) -> Result<[u8; 80]> {
    if message_hash.len() != 40 {
        return Err(DcexError::InvalidInput(
            "Lighter message hash must contain exactly 40 bytes.".to_string(),
        ));
    }
    if private_key.is_zero() || private_key >= scalar_order() {
        return Err(DcexError::InvalidInput(
            "Lighter private scalar is outside the valid range.".to_string(),
        ));
    }
    if nonce.is_zero() || nonce >= scalar_order() {
        return Err(DcexError::InvalidInput(
            "Lighter nonce scalar is outside the valid range.".to_string(),
        ));
    }

    let mut message = [0u64; 5];
    for (index, chunk) in message_hash.chunks_exact(8).enumerate() {
        message[index] = u64::from_le_bytes(chunk.try_into().expect("8-byte chunk"));
    }

    let encoded_r = generator_mul(nonce).encode();
    let mut challenge_input = Vec::with_capacity(10);
    challenge_input.extend_from_slice(&encoded_r);
    challenge_input.extend_from_slice(&message);
    let challenge_fp5 = poseidon_hash(&challenge_input, 5);
    let challenge_bytes = encode_fp5(&[
        challenge_fp5[0],
        challenge_fp5[1],
        challenge_fp5[2],
        challenge_fp5[3],
        challenge_fp5[4],
    ]);
    let challenge = BigUint::from_bytes_le(&challenge_bytes) % scalar_order();
    let product = (challenge * private_key) % scalar_order();
    let response = if nonce >= &product {
        nonce - &product
    } else {
        nonce + scalar_order() - &product
    };

    let mut signature = [0u8; 80];
    let response_bytes = response.to_bytes_le();
    signature[..response_bytes.len().min(40)]
        .copy_from_slice(&response_bytes[..response_bytes.len().min(40)]);
    signature[40..].copy_from_slice(&challenge_bytes);
    Ok(signature)
}

#[cfg(test)]
mod tests {
    use super::*;
    use num_traits::One;

    fn scalar(limbs: &[u64]) -> BigUint {
        let mut bytes = Vec::with_capacity(limbs.len() * 8);
        for limb in limbs {
            bytes.extend_from_slice(&limb.to_le_bytes());
        }
        BigUint::from_bytes_le(&bytes)
    }

    fn limbs(value: &[u8]) -> Vec<u64> {
        value
            .chunks_exact(8)
            .map(|chunk| u64::from_le_bytes(chunk.try_into().expect("8-byte chunk")))
            .collect()
    }

    #[test]
    fn poseidon_matches_official_vector() {
        let result = poseidon_hash_bytes(&[
            3451004116618606032,
            11263134342958518251,
            10957204882857370932,
            5369763041201481933,
            7695734348563036858,
            1393419330378128434,
            7387917082382606332,
        ]);

        assert_eq!(
            limbs(&result),
            vec![
                17992684813643984528,
                5243896189906434327,
                7705560276311184368,
                2785244775876017560,
                14449776097783372302,
            ]
        );
    }

    #[test]
    fn public_key_for_scalar_one_is_generator_encoding() {
        let public_key = public_key_bytes(&BigUint::one()).expect("public key");
        let mut expected = [0u8; 40];
        expected[..8].copy_from_slice(&4u64.to_le_bytes());
        assert_eq!(public_key, expected);
    }

    #[test]
    fn schnorr_matches_official_vector() {
        let private_key = scalar(&[
            12235002942052073545,
            1175977464658719998,
            8536934969147463310,
            6524687619313720391,
            2922072024880609112,
        ]);
        let nonce = scalar(&[
            5245666847777449560,
            15178169970799106939,
            4403065012435293749,
            15306540389399388999,
            8935555081913173844,
        ]);
        let message_hash = encode_fp5(&[
            8398652514106806347,
            11069112711939986896,
            9732488227085561369,
            18076754337204438535,
            17155407358725346236,
        ]);

        let signature =
            schnorr_sign_with_nonce(&message_hash, &private_key, &nonce).expect("signature");

        assert_eq!(
            limbs(&signature[..40]),
            vec![
                6950590877883398434,
                17178336263794770543,
                11012823478139181320,
                16445091359523510936,
                5882925226143600273,
            ]
        );
        assert_eq!(
            limbs(&signature[40..]),
            vec![
                4544744459434870309,
                4180764085957612004,
                3024669018778978615,
                15433417688859446606,
                6775027260348937828,
            ]
        );
    }

    #[test]
    fn transaction_attributes_change_hash() {
        let plain = transaction_hash(&[304, 15, -1], &[]);
        let attributed = transaction_hash(&[304, 15, -1], &[(4, 1)]);
        assert_ne!(plain, attributed);
    }
}
