# Intermediate commit deployment restriction

Do not deploy the commits from `610eafb0` through `93da40ff`, inclusive. Ondo `batch_cancel_orders` in that range serializes `orderIDs` as a JSON array instead of the required comma-separated query value. The first corrected commit is `2b36ecce`; the published Python `0.34.0` / Rust `rust-v0.12.0` release at `dbdd3a8b` includes that fix.

| Commits / issue | Correction | Impact |
|---|---|---|
| `610eafb0`, `6018ae33`, `41b76a7d`, `900692fb`: stale `fund_nondispatch_arms.json` hash | `93da40ff` updates the exact Binance dust validation statement pin | Their ownership tests fail in isolation. |
| `610eafb0` through `93da40ff`, inclusive: Ondo batch-cancel CSV becomes JSON | `2b36ecce` preserves CSV after endpoint normalization | Batch cancellation is unusable; do not deploy this range. |

Compilation alone did not expose these failures. The commits were already published, so their trees and boundaries remain unchanged. Validate each future commit with its affected tests before committing, including ownership pins and request-wire assertions when changing serialization. A passing final branch does not imply that every intermediate commit passes.

This restriction concerns the listed intermediate commits, not the corrected published `0.34.0` release.
