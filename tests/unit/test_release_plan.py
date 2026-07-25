"""Regression tests for release-planning safety checks."""

from __future__ import annotations

import pytest

from scripts.release_plan import (
    Commit,
    removed_exchanges,
    validate_breaking_exchange_removals,
)


def exchange_removal(subject: str, body: str = "") -> Commit:
    """Build a representative commit that removes one exchange integration."""
    return Commit(
        sha="a" * 40,
        subject=subject,
        body=body,
        paths=("dcex/examplex/__init__.py",),
        deleted_paths=(
            "dcex/examplex/__init__.py",
            "crates/dcex/src/exchanges/examplex/mod.rs",
        ),
    )


def test_exchange_removal_detection_deduplicates_components() -> None:
    """Treat Python and Rust deletions as one removed exchange."""
    assert removed_exchanges(exchange_removal("chore: remove exchange")) == ("examplex",)


@pytest.mark.parametrize(
    ("subject", "body"),
    (
        ("chore!: remove examplex exchange support", ""),
        ("chore: remove examplex exchange support", "BREAKING CHANGE: ExampleX removed."),
    ),
)
def test_breaking_exchange_removal_is_accepted(subject: str, body: str) -> None:
    """Accept either supported Conventional Commits breaking marker."""
    validate_breaking_exchange_removals([exchange_removal(subject, body)])


def test_unmarked_exchange_removal_is_rejected() -> None:
    """Reject exchange removal commits without a breaking marker."""
    with pytest.raises(ValueError, match="without a breaking-change marker"):
        validate_breaking_exchange_removals(
            [exchange_removal("chore: remove examplex exchange support")]
        )


def test_unrelated_file_deletion_is_not_treated_as_exchange_removal() -> None:
    """Ignore deleted files that are outside exchange integration paths."""
    commit = Commit(
        sha="b" * 40,
        subject="chore: remove obsolete test",
        body="",
        paths=("tests/unit/test_obsolete.py",),
        deleted_paths=("tests/unit/test_obsolete.py",),
    )
    validate_breaking_exchange_removals([commit])
