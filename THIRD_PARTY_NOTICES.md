# Third-Party Notices

## Lighter cryptography

`dcex/lighter/_crypto.py` and `crates/dcex/src/lighter.rs` contain modified
ports of cryptographic algorithms and constants from:

- [elliottech/lighter-go](https://github.com/elliottech/lighter-go)
- [elliottech/poseidon_crypto](https://github.com/elliottech/poseidon_crypto)

Both upstream projects are licensed under the Apache License, Version 2.0.
The dcex ports translate the required ECgFp5, Poseidon2, and Schnorr
operations and limit the implementation to Lighter HTTP signing.

The Apache License, Version 2.0 is included in
`LICENSES/Apache-2.0.txt`.
