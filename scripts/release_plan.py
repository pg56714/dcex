# ruff: noqa: D100,D101,D103,I001,S603,S607
from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclasses.dataclass(frozen=True)
class ComponentConfig:
    name: str
    version_file: Path
    changelog_file: Path
    body_file: str
    tag_prefix: str
    tag_regex: re.Pattern[str]
    include_prefixes: tuple[str, ...]
    include_files: tuple[str, ...]
    version_regex: re.Pattern[str]


@dataclasses.dataclass(frozen=True)
class Commit:
    sha: str
    subject: str
    body: str
    paths: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class ParsedCommit:
    change_type: str
    description: str
    bump: str | None
    breaking: bool


COMPONENTS: dict[str, ComponentConfig] = {
    "python": ComponentConfig(
        name="python",
        version_file=Path("pyproject.toml"),
        changelog_file=Path("CHANGELOG.md"),
        body_file="python-body.md",
        tag_prefix="",
        tag_regex=re.compile(r"^(?P<version>\d+\.\d+\.\d+)$"),
        include_prefixes=(
            "dcex/",
            "crates/dcex-python/",
            "examples/",
            "tests/",
            "LICENSES/",
        ),
        include_files=(
            ".python-version",
            "pyproject.toml",
            "uv.lock",
            "README.md",
            "THIRD_PARTY_NOTICES.md",
            "LICENSE",
            "product_table.csv",
        ),
        version_regex=re.compile(r'(?m)^(version\s*=\s*")(?P<version>[^"]+)(")$'),
    ),
    "rust": ComponentConfig(
        name="rust",
        version_file=Path("crates/dcex/Cargo.toml"),
        changelog_file=Path("crates/dcex/CHANGELOG.md"),
        body_file="rust-body.md",
        tag_prefix="rust-v",
        tag_regex=re.compile(r"^rust-v(?P<version>\d+\.\d+\.\d+)$"),
        include_prefixes=("crates/dcex/",),
        include_files=("Cargo.toml", "Cargo.lock"),
        version_regex=re.compile(r'(?m)^(version\s*=\s*")(?P<version>[^"]+)(")$'),
    ),
}


CHANGELOG_GROUPS = (
    ("breaking", "BREAKING CHANGE"),
    ("feat", "Feat"),
    ("fix", "Fix"),
    ("refactor", "Refactor"),
    ("perf", "Perf"),
)


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def run_git_with_input(args: list[str], input_text: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=input_text,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout


def normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"unsupported version: {version}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def bump_version(current: str, bump: str, major_version_zero: bool = True) -> str:
    major, minor, patch = parse_version(current)
    if bump == "major":
        if major_version_zero:
            minor += 1
            patch = 0
        else:
            major += 1
            minor = 0
            patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "patch":
        patch += 1
    else:
        raise ValueError(f"unsupported bump: {bump}")
    return format_version((major, minor, patch))


def read_version(config: ComponentConfig) -> str:
    text = (ROOT / config.version_file).read_text(encoding="utf-8")
    match = config.version_regex.search(text)
    if not match:
        raise ValueError(f"cannot find version in {config.version_file}")
    return match.group("version")


def write_version(config: ComponentConfig, version: str) -> None:
    path = ROOT / config.version_file
    text = path.read_text(encoding="utf-8")
    updated, count = config.version_regex.subn(
        lambda match: f"{match.group(1)}{version}{match.group(3)}",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError(f"cannot update version in {config.version_file}")
    path.write_text(updated, encoding="utf-8")


def update_cargo_lock(package_name: str, version: str) -> None:
    path = ROOT / "Cargo.lock"
    if not path.exists():
        return

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    block_start: int | None = None
    changed = False

    def update_block(start: int, end: int) -> None:
        nonlocal changed
        block = "".join(lines[start:end])
        if f'name = "{package_name}"' not in block:
            return
        for index in range(start, end):
            if lines[index].startswith("version = "):
                newline = "\n" if lines[index].endswith("\n") else ""
                lines[index] = f'version = "{version}"{newline}'
                changed = True
                return

    for index, line in enumerate(lines):
        if line.strip() == "[[package]]":
            if block_start is not None:
                update_block(block_start, index)
            block_start = index
    if block_start is not None:
        update_block(block_start, len(lines))

    if changed:
        path.write_text("".join(lines), encoding="utf-8")


def tag_for(config: ComponentConfig, version: str) -> str:
    return f"{config.tag_prefix}{version}"


def matching_tags(config: ComponentConfig) -> dict[str, str]:
    tags = run_git(["tag", "--list", "--merged", "HEAD"]).splitlines()
    matches: dict[str, str] = {}
    for tag in tags:
        match = config.tag_regex.match(tag)
        if match:
            matches[match.group("version")] = tag
    return matches


def latest_matching_tag(config: ComponentConfig) -> str | None:
    matches = matching_tags(config)
    if not matches:
        return None
    version = max(matches, key=parse_version)
    return matches[version]


def commits_since(tag: str | None) -> list[Commit]:
    rev_range = f"{tag}..HEAD" if tag else "HEAD"
    raw = run_git(["log", "--format=%H%x1f%s%x1f%b%x1e", rev_range])
    records: list[tuple[str, str, str]] = []
    for record in raw.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        sha, subject, body = (record.split("\x1f", 2) + ["", ""])[:3]
        records.append((sha, subject, body))

    paths_by_sha = paths_for_commits([sha for sha, _, _ in records])
    commits: list[Commit] = []
    for sha, subject, body in records:
        commits.append(
            Commit(sha=sha, subject=subject, body=body, paths=tuple(paths_by_sha.get(sha, ())))
        )
    return commits


def paths_for_commits(shas: list[str]) -> dict[str, list[str]]:
    if not shas:
        return {}

    raw = run_git_with_input(
        ["diff-tree", "--stdin", "--name-only", "-r"],
        "\n".join(shas) + "\n",
    )
    paths_by_sha: dict[str, list[str]] = {}
    current_sha: str | None = None
    sha_pattern = re.compile(r"^[0-9a-f]{40}$")
    for line in raw.splitlines():
        if sha_pattern.match(line):
            current_sha = line
            paths_by_sha.setdefault(current_sha, [])
            continue
        if current_sha and line:
            paths_by_sha[current_sha].append(normalize_path(line))
    return paths_by_sha


def path_matches(config: ComponentConfig, path: str) -> bool:
    normalized = normalize_path(path)
    return normalized in config.include_files or any(
        normalized.startswith(prefix) for prefix in config.include_prefixes
    )


def parse_conventional_commit(commit: Commit) -> ParsedCommit | None:
    match = re.match(
        r"^(?P<type>[A-Za-z]+)(?:\([^)]+\))?(?P<bang>!)?: (?P<description>.+)$",
        commit.subject,
    )
    if not match:
        return None

    change_type = match.group("type").lower()
    breaking = bool(match.group("bang")) or bool(
        re.search(r"(?m)^BREAKING[- ]CHANGE:", commit.body)
    )
    bump: str | None
    if breaking:
        bump = "major"
    elif change_type == "feat":
        bump = "minor"
    elif change_type in {"fix", "perf", "refactor"}:
        bump = "patch"
    else:
        bump = None

    return ParsedCommit(
        change_type=change_type,
        description=match.group("description").strip(),
        bump=bump,
        breaking=breaking,
    )


def strongest_bump(parsed_commits: list[ParsedCommit]) -> str | None:
    order = {"patch": 1, "minor": 2, "major": 3}
    bumps = [commit.bump for commit in parsed_commits if commit.bump]
    if not bumps:
        return None
    return max(bumps, key=lambda bump: order[bump])


def build_changelog(version: str, parsed_commits: list[ParsedCommit]) -> str:
    today = dt.date.today().isoformat()
    lines = [f"## {version} ({today})", ""]
    used_any = False

    for key, title in CHANGELOG_GROUPS:
        if key == "breaking":
            commits = [commit for commit in parsed_commits if commit.breaking]
        else:
            commits = [
                commit
                for commit in parsed_commits
                if commit.change_type == key and not commit.breaking
            ]
        if not commits:
            continue
        used_any = True
        lines.extend([f"### {title}", ""])
        lines.extend(f"- {commit.description}" for commit in commits)
        lines.append("")

    if not used_any:
        lines.extend(["### Changed", "", "- Initial release.", ""])

    return "\n".join(lines).rstrip() + "\n"


def prepend_changelog(path: Path, section: str) -> None:
    full_path = ROOT / path
    if full_path.exists():
        current = full_path.read_text(encoding="utf-8").lstrip("\ufeff").lstrip()
        full_path.write_text(f"{section}\n{current}", encoding="utf-8")
    else:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(section, encoding="utf-8")


def plan_component(name: str, body_dir: Path) -> dict[str, Any]:
    config = COMPONENTS[name]
    current_version = read_version(config)
    expected_current_tag = tag_for(config, current_version)
    tags = matching_tags(config)
    previous_tag = tags.get(current_version) or latest_matching_tag(config)
    commits = commits_since(previous_tag)
    relevant_commits = [
        commit for commit in commits if any(path_matches(config, path) for path in commit.paths)
    ]
    parsed_commits = [
        parsed
        for commit in relevant_commits
        if (parsed := parse_conventional_commit(commit)) is not None
    ]
    bump = strongest_bump(parsed_commits)
    is_initial_release = expected_current_tag not in tags

    if is_initial_release and name == "rust":
        next_version = current_version
        release = True
        planned_bump = "initial"
    elif bump:
        next_version = bump_version(current_version, bump)
        release = True
        planned_bump = bump
    else:
        next_version = current_version
        release = False
        planned_bump = None

    next_tag = tag_for(config, next_version) if release else None
    body_path = body_dir / config.body_file

    return {
        "name": name,
        "release": release,
        "bump": planned_bump,
        "detected_bump": bump,
        "current_version": current_version,
        "next_version": next_version if release else None,
        "previous_tag": previous_tag,
        "next_tag": next_tag,
        "changelog": normalize_path(str(config.changelog_file)),
        "body_path": normalize_path(str(body_path)),
        "commit_count": len(relevant_commits),
        "commits": [
            {
                "sha": commit.sha,
                "subject": commit.subject,
                "paths": list(commit.paths),
            }
            for commit in relevant_commits
        ],
    }


def build_plan(component: str, body_dir: Path) -> dict[str, Any]:
    names = tuple(COMPONENTS) if component == "all" else (component,)
    plan: dict[str, Any] = {name: plan_component(name, body_dir) for name in names}
    plan["any_release"] = any(plan[name]["release"] for name in names)
    return plan


def apply_plan(plan: dict[str, Any], body_dir: Path) -> None:
    body_dir.mkdir(parents=True, exist_ok=True)
    for name, component_plan in plan.items():
        if name not in COMPONENTS or not component_plan.get("release"):
            continue
        config = COMPONENTS[name]
        next_version = component_plan["next_version"]
        commits = [
            Commit(
                sha=item["sha"],
                subject=item["subject"],
                body=run_git(["log", "-1", "--format=%b", item["sha"]]),
                paths=tuple(item["paths"]),
            )
            for item in component_plan["commits"]
        ]
        parsed_commits = [
            parsed
            for commit in commits
            if (parsed := parse_conventional_commit(commit)) is not None
        ]
        changelog_section = build_changelog(next_version, parsed_commits)

        write_version(config, next_version)
        if name == "rust":
            update_cargo_lock("dcex", next_version)
        prepend_changelog(config.changelog_file, changelog_section)
        (body_dir / config.body_file).write_text(changelog_section, encoding="utf-8")


def write_github_outputs(plan: dict[str, Any], output_path: Path) -> None:
    lines: list[str] = []
    for name in COMPONENTS:
        component = plan.get(name, {})
        lines.extend(
            [
                f"{name}_release={str(component.get('release', False)).lower()}",
                f"{name}_version={component.get('next_version') or ''}",
                f"{name}_tag={component.get('next_tag') or ''}",
                f"{name}_body_path={component.get('body_path') or ''}",
            ]
        )
    lines.append(f"any_release={str(plan.get('any_release', False)).lower()}")
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")


def print_text_plan(plan: dict[str, Any]) -> None:
    for name in COMPONENTS:
        if name not in plan:
            continue
        component = plan[name]
        print(f"{name.title()}:")
        print(f"  release: {str(component['release']).lower()}")
        print(f"  previous tag: {component['previous_tag'] or 'none'}")
        print(f"  current version: {component['current_version']}")
        print(f"  bump: {component['bump'] or 'none'}")
        print(f"  next version: {component['next_version'] or 'none'}")
        print(f"  next tag: {component['next_tag'] or 'none'}")
        print(f"  changelog: {component['changelog']}")
        print(f"  relevant commits: {component['commit_count']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plan package releases without mixing tag namespaces."
    )
    parser.add_argument("--component", choices=("all", *COMPONENTS), default="all")
    parser.add_argument("--apply", action="store_true", help="update version and changelog files")
    parser.add_argument("--body-dir", default=".release")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--github-output", help="append GitHub Actions outputs to this file")
    args = parser.parse_args(argv)

    body_dir = Path(args.body_dir)
    plan = build_plan(args.component, body_dir)

    if args.apply:
        apply_plan(plan, body_dir)

    if args.github_output:
        write_github_outputs(plan, Path(args.github_output))

    if args.format == "json":
        print(json.dumps(plan, indent=2))
    else:
        print_text_plan(plan)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
