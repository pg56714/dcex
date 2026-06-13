"""
Pure Python primitives required for Lighter transaction signing.

The implementation follows the public ECgFp5, Poseidon2, and Schnorr
specifications used by Lighter. It intentionally exposes only the operations
needed by the HTTP signer.

Reference implementations:
- https://github.com/elliottech/lighter-go (Apache-2.0)
- https://github.com/elliottech/poseidon_crypto (Apache-2.0)

This file is a modified Python port of portions of those implementations.
See LICENSES/Apache-2.0.txt and THIRD_PARTY_NOTICES.md.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass

_GOLDILOCKS_ORDER = 0xFFFFFFFF00000001
_SCALAR_ORDER = int(
    "106799351671714695104148491657179270274505774058172723015913968518"
    "5762082554198619328292418486241"
)
_FP5_ROOT = 1041288259238279555
_FP5_ZERO = (0, 0, 0, 0, 0)
_FP5_ONE = (1, 0, 0, 0, 0)

_EXTERNAL_CONSTANTS = (
    (
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
    ),
    (
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
    ),
    (
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
    ),
    (
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
    ),
    (
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
    ),
    (
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
    ),
    (
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
    ),
    (
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
    ),
)

_INTERNAL_CONSTANTS = (
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
)

_MATRIX_DIAGONAL = (
    0xC3B6C08E23BA9300,
    0xD84B5DE94A324FB6,
    0x0D0C371C5B35B84F,
    0x7964F570E7188037,
    0x5DAF18BBD996604B,
    0x6743BC47B9595257,
    0x5528B9362C59BB70,
    0xAC45E25B7127B68B,
    0xA2077D7DFBB606B5,
    0xF3FAAC6FAEE378AE,
    0x0C6388B51545E883,
    0xD27DBB6944917B60,
)

_GENERATOR_X = (
    12883135586176881569,
    4356519642755055268,
    5248930565894896907,
    2165973894480315022,
    2448410071095648785,
)


def _fp5_add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((left[index] + right[index]) % _GOLDILOCKS_ORDER for index in range(5))


def _fp5_sub(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((left[index] - right[index]) % _GOLDILOCKS_ORDER for index in range(5))


def _fp5_neg(value: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(-limb % _GOLDILOCKS_ORDER for limb in value)


def _fp5_mul(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    product = [0] * 9
    for left_index, left_limb in enumerate(left):
        for right_index, right_limb in enumerate(right):
            product[left_index + right_index] += left_limb * right_limb
    for degree in range(8, 4, -1):
        product[degree - 5] += 3 * product[degree]
    return tuple(limb % _GOLDILOCKS_ORDER for limb in product[:5])


def _fp5_square(value: tuple[int, ...]) -> tuple[int, ...]:
    return _fp5_mul(value, value)


def _fp5_scalar_mul(value: tuple[int, ...], scalar: int) -> tuple[int, ...]:
    return tuple(limb * scalar % _GOLDILOCKS_ORDER for limb in value)


def _fp5_frobenius(value: tuple[int, ...], count: int = 1) -> tuple[int, ...]:
    count %= 5
    if count == 0:
        return value
    root = pow(_FP5_ROOT, count, _GOLDILOCKS_ORDER)
    factor = 1
    result = []
    for limb in value:
        result.append(limb * factor % _GOLDILOCKS_ORDER)
        factor = factor * root % _GOLDILOCKS_ORDER
    return tuple(result)


def _fp5_inv(value: tuple[int, ...]) -> tuple[int, ...]:
    if value == _FP5_ZERO:
        return _FP5_ZERO
    d = _fp5_frobenius(value)
    e = _fp5_mul(d, _fp5_frobenius(d))
    f = _fp5_mul(e, _fp5_frobenius(e, 2))
    norm = _fp5_mul(value, f)[0]
    return _fp5_scalar_mul(f, pow(norm, _GOLDILOCKS_ORDER - 2, _GOLDILOCKS_ORDER))


def _fp5_encode(value: tuple[int, ...]) -> bytes:
    return b"".join(limb.to_bytes(8, "little") for limb in value)


def _external_linear_layer(state: list[int]) -> None:
    for offset in range(0, 12, 4):
        x0, x1, x2, x3 = state[offset : offset + 4]
        t01 = x0 + x1
        t23 = x2 + x3
        total = t01 + t23
        state[offset] = total + t01 + x1
        state[offset + 1] = total + x1 + 2 * x2
        state[offset + 2] = total + t23 + x3
        state[offset + 3] = total + x3 + 2 * x0
    sums = [sum(state[index::4]) for index in range(4)]
    for index in range(12):
        state[index] = (state[index] + sums[index % 4]) % _GOLDILOCKS_ORDER


def _internal_linear_layer(state: list[int]) -> None:
    total = sum(state) % _GOLDILOCKS_ORDER
    for index, diagonal in enumerate(_MATRIX_DIAGONAL):
        state[index] = (total + state[index] * diagonal) % _GOLDILOCKS_ORDER


def _poseidon_permute(state: list[int]) -> None:
    _external_linear_layer(state)
    for round_index in range(4):
        for index in range(12):
            state[index] = (
                state[index] + _EXTERNAL_CONSTANTS[round_index][index]
            ) % _GOLDILOCKS_ORDER
            state[index] = pow(state[index], 7, _GOLDILOCKS_ORDER)
        _external_linear_layer(state)
    for constant in _INTERNAL_CONSTANTS:
        state[0] = (state[0] + constant) % _GOLDILOCKS_ORDER
        state[0] = pow(state[0], 7, _GOLDILOCKS_ORDER)
        _internal_linear_layer(state)
    for round_index in range(4, 8):
        for index in range(12):
            state[index] = (
                state[index] + _EXTERNAL_CONSTANTS[round_index][index]
            ) % _GOLDILOCKS_ORDER
            state[index] = pow(state[index], 7, _GOLDILOCKS_ORDER)
        _external_linear_layer(state)


def _poseidon_hash(values: list[int], output_count: int = 5) -> tuple[int, ...]:
    state = [0] * 12
    for offset in range(0, len(values), 8):
        for index, value in enumerate(values[offset : offset + 8]):
            state[index] = value % _GOLDILOCKS_ORDER
        _poseidon_permute(state)
    output: list[int] = []
    while len(output) < output_count:
        output.extend(state[: min(8, output_count - len(output))])
        if len(output) < output_count:
            _poseidon_permute(state)
    return tuple(output)


@dataclass(frozen=True, slots=True)
class _Point:
    x: tuple[int, ...]
    z: tuple[int, ...]
    u: tuple[int, ...]
    t: tuple[int, ...]

    def add(self, other: _Point) -> _Point:
        t1 = _fp5_mul(self.x, other.x)
        t2 = _fp5_mul(self.z, other.z)
        t3 = _fp5_mul(self.u, other.u)
        t4 = _fp5_mul(self.t, other.t)
        t5 = _fp5_sub(
            _fp5_mul(_fp5_add(self.x, self.z), _fp5_add(other.x, other.z)),
            _fp5_add(t1, t2),
        )
        t6 = _fp5_sub(
            _fp5_mul(_fp5_add(self.u, self.t), _fp5_add(other.u, other.t)),
            _fp5_add(t3, t4),
        )
        curve_b = (0, 263, 0, 0, 0)
        curve_b_times_two = (0, 526, 0, 0, 0)
        t7 = _fp5_add(t1, _fp5_mul(t2, curve_b))
        t8 = _fp5_mul(t4, t7)
        t9 = _fp5_mul(
            t3,
            _fp5_add(_fp5_mul(t5, curve_b_times_two), _fp5_scalar_mul(t7, 2)),
        )
        t10 = _fp5_mul(
            _fp5_add(t4, _fp5_scalar_mul(t3, 2)),
            _fp5_add(t5, t7),
        )
        return _Point(
            x=_fp5_mul(_fp5_sub(t10, t8), curve_b),
            z=_fp5_sub(t8, t9),
            u=_fp5_mul(t6, _fp5_sub(_fp5_mul(t2, curve_b), t1)),
            t=_fp5_add(t8, t9),
        )

    def double(self) -> _Point:
        t1 = _fp5_mul(self.z, self.t)
        t2 = _fp5_mul(t1, self.t)
        x1 = _fp5_square(t2)
        z1 = _fp5_mul(t1, self.u)
        t3 = _fp5_square(self.u)
        w1 = _fp5_sub(
            t2,
            _fp5_mul(t3, _fp5_scalar_mul(_fp5_add(self.x, self.z), 2)),
        )
        t4 = _fp5_square(z1)
        return _Point(
            x=_fp5_mul(t4, (0, 1052, 0, 0, 0)),
            z=_fp5_square(w1),
            u=_fp5_sub(
                _fp5_square(_fp5_add(w1, z1)),
                _fp5_add(t4, _fp5_square(w1)),
            ),
            t=_fp5_sub(
                _fp5_scalar_mul(x1, 2),
                _fp5_add(_fp5_scalar_mul(t4, 4), _fp5_square(w1)),
            ),
        )

    def encode(self) -> tuple[int, ...]:
        return _fp5_mul(self.t, _fp5_inv(self.u))


_NEUTRAL = _Point(_FP5_ZERO, _FP5_ONE, _FP5_ZERO, _FP5_ONE)
_GENERATOR = _Point(_GENERATOR_X, _FP5_ONE, _FP5_ONE, (4, 0, 0, 0, 0))


def _point_mul(point: _Point, scalar: int) -> _Point:
    result = _NEUTRAL
    addend = point
    while scalar:
        if scalar & 1:
            result = result.add(addend)
        addend = addend.double()
        scalar >>= 1
    return result


def private_key_from_bytes(private_key: bytes) -> int:
    """Convert a 40-byte Lighter private key into its scalar value."""
    if len(private_key) != 40:
        raise ValueError("Lighter API private key must contain exactly 40 bytes.")
    scalar = int.from_bytes(private_key, "little") % _SCALAR_ORDER
    if scalar == 0:
        raise ValueError("Lighter API private key must not reduce to zero.")
    return scalar


def public_key_bytes(private_key: int) -> bytes:
    """Derive the encoded Lighter public key for a private scalar."""
    return _fp5_encode(_point_mul(_GENERATOR, private_key).encode())


def poseidon_hash_bytes(values: list[int]) -> bytes:
    """Hash Goldilocks field values into one encoded Fp5 element."""
    return _fp5_encode(_poseidon_hash(values))


def schnorr_sign(message_hash: bytes, private_key: int, nonce: int | None = None) -> bytes:
    """Create an ECgFp5 Schnorr signature for an encoded Fp5 message hash."""
    if len(message_hash) != 40:
        raise ValueError("Lighter message hash must contain exactly 40 bytes.")
    if not 0 < private_key < _SCALAR_ORDER:
        raise ValueError("Lighter private scalar is outside the valid range.")
    if nonce is not None and not 0 < nonce < _SCALAR_ORDER:
        raise ValueError("Lighter nonce scalar is outside the valid range.")
    message = tuple(
        int.from_bytes(message_hash[offset : offset + 8], "little") for offset in range(0, 40, 8)
    )
    random_scalar = nonce
    while not random_scalar:
        random_scalar = secrets.randbelow(_SCALAR_ORDER)
    encoded_r = _point_mul(_GENERATOR, random_scalar).encode()
    challenge_fp5 = _poseidon_hash([*encoded_r, *message])
    challenge = sum(limb << (64 * index) for index, limb in enumerate(challenge_fp5))
    challenge %= _SCALAR_ORDER
    response = (random_scalar - challenge * private_key) % _SCALAR_ORDER
    return response.to_bytes(40, "little") + challenge.to_bytes(40, "little")
