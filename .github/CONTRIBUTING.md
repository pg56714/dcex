# Contributing

Thank you for contributing to dcex. Before opening a large change, please discuss the scope in an issue or discussion so maintainers can confirm that it fits the project direction.

Please follow the [Code of Conduct](https://github.com/pg56714/dcex/blob/main/.github/CODE_OF_CONDUCT.md) in all project interactions.

## Project Scope

dcex focuses on market data, account queries, and trading/order APIs for cryptocurrency exchanges.

Current scope notes:

- External withdrawal creation endpoints are not currently wrapped.
- Options support is limited to exchange-specific APIs and is not normalized by the Product Table Manager.
- Examples should stay concise and read-only. Endpoint validation belongs in `tests`.

## Development Environment

1. Install `uv`: [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).
2. Create and sync the local environment:

   ```sh
   uv sync
   ```

3. Run the relevant quality checks before opening a pull request.

## Testing

The default test suite is offline and does not require exchange API keys or network access:

```sh
uv run pytest
```

Run focused offline unit tests:

```sh
uv run pytest tests/unit
```

Public live exchange tests are opt-in and require network access:

```sh
uv run pytest -m "live and not private"
```

Private live tests require the relevant exchange credentials from `.env.sample`.
Use marker filters to avoid unintended account changes:

```sh
uv run pytest tests/sync_support/binance tests/async_support/binance -m "live and private and not stateful and not generated"
```

Stateful tests can mutate exchange or account settings, such as leverage or position mode. Run them only when that is intentional:

```sh
uv run pytest tests/sync_support/okx tests/async_support/okx -m "live and private and stateful"
```

Generated-report tests request server-side report generation or downloadable files. Run them separately because they may consume low-frequency report quotas:

```sh
uv run pytest tests/sync_support/okx tests/async_support/okx -m "live and private and generated"
```

## Quality Checks

The CI workflow runs these checks:

```sh
cargo fmt --all --check
cargo check --workspace --all-features
cargo test --workspace --all-features
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest tests/unit
```

Run the same checks locally before opening a pull request when possible.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) in English:

```text
<type>(optional-scope): description
```

Common commit types:

| Type       | Use for                                        |
| ---------- | ---------------------------------------------- |
| `feat`     | New user-facing functionality                  |
| `fix`      | Bug fixes                                      |
| `docs`     | Documentation-only changes                     |
| `deps`     | Dependency updates                             |
| `perf`     | Performance improvements                       |
| `refactor` | Code restructuring without behavior changes    |
| `test`     | Test additions or updates                      |
| `ci`       | CI workflow changes                            |
| `build`    | Build system or packaging changes              |
| `chore`    | Maintenance that does not fit another category |
| `revert`   | Reverting a previous change                    |

Examples:

```text
docs: clarify supported endpoint scope
fix(binance): normalize futures order payload
feat(ptm): add exchange metadata lookup
```

Versioning and changelog updates are handled by the release workflow after changes are merged.

## Release Publishing

The release workflow detects Conventional Commit changes on `main` and plans
Python and Rust releases independently. For a bumped Python release, GitHub
Actions builds Python artifacts and publishes the package to PyPI using
Trusted Publishing.

The Rust crate `dcex` is versioned independently in `crates/dcex/Cargo.toml`
and published from matching `rust-v*` tags. For example, tag `rust-v0.1.0`
publishes crate version `0.1.0` to crates.io. Required Rust registry
credentials are provided through `CARGO_REGISTRY_TOKEN`.
The `crates/dcex-python` package is an internal PyO3 build crate and is not
published to crates.io; the Python package version is managed only in
`pyproject.toml`.

## Issues and Feature Requests

Use GitHub Issues for bug reports and scoped feature requests. For broad product ideas or design discussions, use GitHub Discussions first.

Good bug reports are:

- Reproducible: include steps or a minimal code sample.
- Specific: include the dcex version, Python version, operating system, exchange, and endpoint.
- Unique: check existing issues before opening a new one.
- Scoped: keep one bug per issue.

## Pull Requests

1. Search existing issues and pull requests to avoid duplicate work.
2. Fork the project and create a focused branch.
3. Keep the change scoped to one behavior or documentation topic.
4. Add or update tests when behavior changes.
5. Update README, examples, or contributing docs when public behavior or supported scope changes.
6. Run relevant quality checks.
7. Open a pull request and fill in the PR template.
