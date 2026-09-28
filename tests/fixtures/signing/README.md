# Independent signing fixtures

These fixtures were computed on 2026-09-27 and 2026-09-28 outside this repository using the
unmodified official SDKs at the commits recorded in each JSON file. The fixed
private key is public test data and is never used for a funded account.

- `lighter_official.json`: copy `lighter_generator.go` into `cmd/review-vectors/main.go`
  in the pinned lighter-go checkout and run `go run ./cmd/review-vectors`.
  It calls `L2CreateGroupedOrdersTxInfo.Hash(304)` directly. The prefix and
  individual folded hashes are recorded to distinguish order-folding regressions.
  Prefix/reversed cases test hashing only, not transaction eligibility.
- `hyperliquid_official.json`: run `hyperliquid_generator.py` in the pinned
  hyperliquid-python-sdk checkout with that SDK and its dependencies installed.
  It calls `sign_l1_action` and `action_hash`, and records MessagePack bytes.
  Mainnet/testnet, vault and expiry variants prevent accidental domain reuse.

- `lighter_withdraw_official.json`: run `go run /absolute/path/to/lighter_withdraw_generator.go`
  from the pinned lighter-go checkout. It calls the official `L2WithdrawTxInfo.Hash`
  and `L2ApproveIntegratorTxInfo.Hash` with and without nonce suppression. The fixture
  records chain ID, complete transaction inputs and expected Poseidon hashes. The
  L1 signature is caller-supplied test data; these vectors verify L2 hashing only.

The generators do not import dcex or contact an exchange.
