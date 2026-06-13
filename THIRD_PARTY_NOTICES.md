# Third-Party Notices

## Lighter cryptography

`dcex/lighter/_crypto.py` contains a modified Python port of cryptographic
algorithms and constants from:

- [elliottech/lighter-go](https://github.com/elliottech/lighter-go)
- [elliottech/poseidon_crypto](https://github.com/elliottech/poseidon_crypto)

Both upstream projects are licensed under the Apache License, Version 2.0.
The dcex port translates the required ECgFp5, Poseidon2, and Schnorr
operations to Python and limits the implementation to Lighter HTTP signing.

The Apache License, Version 2.0 is included in
`LICENSES/Apache-2.0.txt`.
