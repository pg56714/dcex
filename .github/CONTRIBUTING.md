# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.
Please note we have a [code of conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## Development environment setup

1. Download uv [Official Documentation](https://docs.astral.sh/uv/getting-started/installation/)
2. Create a virtual environment:
   ```sh
   uv venv
   ```
3. Activate the virtual environment:
   - **Windows**:
     ```sh
     .venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```sh
     source .venv/bin/activate
     ```
4. Install dependencies:
   ```sh
   uv sync
   ```
5. Run the project:

   ```sh
   uv run ooo.py
   ```

6. Install git hooks:

   ```sh
   pre-commit install
   ```

7. Run pre commit checks on all files:

   ```sh
   pre-commit run --all-files
   ```

8. commit your changes:
   ```sh
   git add .
   cz commit
   ```

### Commit message rules

Consider following the below format for the commit message:

Commit Type:
`feat | fix | docs | deps | perf | revert | chore | style | refactor | test | ci | build `

**Examples**

- `feat:` create a new feature.
- `fix:` resolve a bug.
- `docs:` update documentation only.
- `deps:` update dependencies.
- `perf:` improve performance without changing functionality.
- `revert:` revert a previous change.

- `chore:` routine maintenance or dependency updates.
- `style:` apply code style changes (e.g., formatting).
- `refactor:` restructure code without changing behavior.
- `test:` add or update tests.
- `ci:` update CI configuration.
- `build:` changes that affect the build system or external dependencies.

**Version bump behavior (Semantic Versioning)**

When using `release-please`, commit types determine how the next version is bumped:

| Commit Type                                         | Version Bump           | Example             |
| --------------------------------------------------- | ---------------------- | ------------------- |
| `chore`, `style`, `refactor`, `test`, `ci`, `build` | ❌ Ignored for release | No version bump     |
| `fix`, `docs`, `deps`, `perf`, `revert`             | 🩹 Patch               | `0.1.26` → `0.1.27` |
| `feat`                                              | 🌟 Minor               | `0.1.26` → `0.2.0`  |
| `feat!` or `BREAKING CHANGE:`                       | 🚨 Major (≥1.0.0)      | `1.0.0` → `2.0.0`   |

> 💡 For versions under `0.x`, `feat:` still triggers a **minor** bump (`0.1.0` → `0.2.0`). To change this behavior, set `"bump-minor-pre-major": false` in `.release-please-config.json`.

### Using Commitizen

This project uses [Commitizen](https://commitizen-tools.github.io/commitizen/) to standardize commit messages and enable automated versioning and changelog generation.

Instead of manually typing commit messages, you can run:

```sh
cz commit
```

This will guide you through an interactive prompt to compose a conventional commit message, ensuring compatibility with our release automation system.

> 💡 **Reminder**: Commit messages using `feat:`, `fix:`, or `perf:` will trigger automatic version bumps and changelog generation via GitHub Actions (`release-please`).

If you prefer to write your own commit messages, please follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format:

```
<type>(optional-scope): description
```

**Examples:**

- `feat(auth): add OAuth2 login support`
- `fix(api): handle timeout edge case`
- `refactor: simplify data parser logic`

Releases are handled automatically via GitHub Actions and [release-please](https://github.com/googleapis/release-please), based on your commit history.

> 💡 You do not need to run `cz bump` manually — versioning and changelogs are managed automatically.

## Issues and feature requests

You've found a bug in the source code, a mistake in the documentation or maybe you'd like a new feature? You can help us by [submitting an issue on GitHub](https://github.com/pg56714/dcex/issues). Before you create an issue, make sure to search the issue archive -- your issue may have already been addressed!

Please try to create bug reports that are:

- _Reproducible._ Include steps to reproduce the problem.
- _Specific._ Include as much detail as possible: which version, what environment, etc.
- _Unique._ Do not duplicate existing opened issues.
- _Scoped to a Single Bug._ One bug per report.

If you have any great ideas of Feature Request, please avoid adding it to the Issues section in Github and instead [start a new Discussion on Github](https://github.com/pg56714/dcex/discussions/categories/ideas). This allows the maintainers and the member a common place to discuss about the Request. Make sure to check if your request or idea has already been discussed or closed to avoid duplication.

**Even better: Submit a pull request with a fix or new feature!**

### How to submit a Pull Request

1. Search our repository for open or closed [Pull Requests](https://github.com/pg56714/dcex/pulls) that relate to your submission. You don't want to duplicate effort.
2. Fork the project.
3. Create your feature branch (`git checkout -b feat/amazing_feature`).
4. Commit your changes (`git commit -m 'feat: add amazing_feature'`). Please follow the specification mentioned above for your commit messages.
5. Push to the branch (`git push origin feat/amazing_feature`).
6. [Open a Pull Request](https://github.com/pg56714/dcex/compare?expand=1).
7. Make sure to fill in the all the details in the Pull Request to make it easier for the reviewers. Make sure to refer to any discussion or Issues that your PR is fixing.
