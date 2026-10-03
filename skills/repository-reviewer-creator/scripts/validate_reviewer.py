#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Validate a generated reviewer's portable structure and evidence index."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import yaml

_AUTHORING_SPEC = importlib.util.spec_from_file_location("reviewer_authoring_checks", Path(__file__).with_name("check_skill_authoring.py"))
assert _AUTHORING_SPEC and _AUTHORING_SPEC.loader
_AUTHORING = importlib.util.module_from_spec(_AUTHORING_SPEC)
_AUTHORING_SPEC.loader.exec_module(_AUTHORING)
check_skill = _AUTHORING.check_skill


REQUIRED = (
    "SKILL.md",
    "references/repository-profile.json",
    "references/review-rules.md",
    "references/safety-and-checks.md",
)
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
PLACEHOLDER_RE = re.compile(r"(?<!\$)\{\{[A-Z][A-Z0-9_]*\}\}|\b(?:INSERT_HERE|REPLACE_ME)\b")
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\)")


def portable_path(value: object, *, allow_dot: bool = False) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    if value == ".":
        return allow_dot
    return not path.is_absolute() and ".." not in path.parts and value != "./"


def within(path: Path, root: Path) -> bool:
    return path.resolve().is_relative_to(root.resolve())


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)

    def nonempty(value: object, label: str) -> bool:
        valid = isinstance(value, str) and bool(value.strip())
        if not valid:
            fail(f"{label}: expected a non-empty string")
        return valid

    def path_list(value: object, label: str) -> None:
        if not isinstance(value, list) or not value:
            fail(f"{label}: expected a non-empty list of repository-relative paths")
            return
        for path in value:
            if not portable_path(path):
                fail(f"{label}: non-portable path {path!r}")

    if not root.is_dir():
        return {"passed": False, "errors": ["Reviewer directory does not exist"], "root": str(root)}

    authoring = check_skill(root)
    for issue in authoring["issues"]:
        fail(f"{issue['path']}: authoring/{issue['code']}: {issue['message']}")

    for relative in REQUIRED:
        path = root / relative
        if not within(path, root):
            fail(f"{relative}: resolved path escapes the reviewer bundle")
        elif not path.is_file() or path.stat().st_size == 0:
            fail(f"{relative}: required non-empty file is missing")

    skill_path = root / "SKILL.md"
    if skill_path.is_file() and within(skill_path, root):
        content = skill_path.read_text(encoding="utf-8-sig")
        frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", content, re.DOTALL)
        if not frontmatter:
            fail("SKILL.md: missing YAML frontmatter")
        else:
            try:
                metadata = yaml.safe_load(frontmatter.group(1))
            except yaml.YAMLError:
                metadata = None
            if not isinstance(metadata, dict) or set(metadata) != {"name", "description"}:
                fail("SKILL.md: frontmatter must contain only name and description")
            else:
                name = metadata["name"]
                if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) >= 64:
                    fail("SKILL.md: invalid lowercase-hyphen-case name or length")
                elif name != root.name:
                    fail("SKILL.md: name must match its directory")
                nonempty(metadata["description"], "SKILL.md description")
            if not content[frontmatter.end():].strip():
                fail("SKILL.md: procedural body is empty")

    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not within(path, root):
            fail(f"{relative}: resolved path escapes the reviewer bundle")
            continue
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".json", ".yaml", ".yml"}:
            continue
        content = path.read_text(encoding="utf-8-sig")
        if PLACEHOLDER_RE.search(content):
            fail(f"{relative}: unresolved template marker")
        if path.suffix != ".md":
            continue
        for match in LINK_RE.finditer(content):
            target = unquote(match.group(1).strip("<>"))
            parsed = urlsplit(target)
            if parsed.scheme in {"https", "http", "mailto"}:
                continue
            if target.startswith("#"):
                continue
            if parsed.scheme or parsed.netloc or target.startswith(("/", "\\")):
                fail(f"{relative}: non-portable Markdown link {target!r}")
                continue
            destination = path.parent / parsed.path
            if not within(destination, root) or not destination.exists():
                fail(f"{relative}: Markdown link is missing or outside the bundle: {target!r}")

    profile_path = root / REQUIRED[1]
    profile = None
    if profile_path.is_file() and within(profile_path, root):
        try:
            profile = json.loads(profile_path.read_text(encoding="utf-8-sig"))
        except (ValueError, UnicodeError) as error:
            fail(f"repository-profile.json: invalid JSON ({error})")
    if not isinstance(profile, dict):
        fail("repository-profile.json: expected an object")
        return {"passed": False, "errors": errors, "root": str(root)}

    if type(profile.get("schema_version")) is not int or profile["schema_version"] != 1:
        fail("schema_version: expected integer 1")
    repository = profile.get("repository")
    if not isinstance(repository, dict):
        fail("repository: expected an object")
    else:
        for key in ("name", "identity", "revision", "inspected_at"):
            nonempty(repository.get(key), f"repository.{key}")
        try:
            dt.date.fromisoformat(repository.get("inspected_at", ""))
        except (TypeError, ValueError):
            fail("repository.inspected_at: expected an ISO date")
        path_list(repository.get("fingerprint_paths"), "repository.fingerprint_paths")
        identity = repository.get("identity")
        if isinstance(identity, str) and urlsplit(identity).username:
            fail("repository.identity: remove embedded URL credentials")

    read_sources: set[str] = set()
    unavailable_sources: set[str] = set()

    def records(field: str) -> list[dict]:
        values = profile.get(field)
        if not isinstance(values, list) or not values:
            fail(f"{field}: expected a non-empty list")
            return []
        result = []
        for index, record in enumerate(values):
            if not isinstance(record, dict):
                fail(f"{field}[{index}]: expected an object")
            else:
                result.append(record)
        return result

    source_ids: set[str] = set()
    for index, source in enumerate(records("sources")):
        label = f"sources[{index}]"
        for key in ("id", "kind", "location", "note"):
            nonempty(source.get(key), f"{label}.{key}")
        identifier = source.get("id")
        if isinstance(identifier, str):
            if identifier in source_ids:
                fail(f"{label}: duplicate source ID {identifier!r}")
            source_ids.add(identifier)
        status = source.get("status")
        if not isinstance(status, str) or status not in {"read", "unavailable", "not-applicable"}:
            fail(f"{label}.status: invalid read status")
        elif status == "read" and isinstance(identifier, str):
            read_sources.add(identifier)
        elif status == "unavailable" and isinstance(identifier, str):
            unavailable_sources.add(identifier)
        location = source.get("location")
        if isinstance(location, str):
            parsed = urlsplit(location)
            if parsed.username:
                fail(f"{label}.location: remove embedded URL credentials")
            elif parsed.scheme in {"https", "http"}:
                pass
            elif location.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", location):
                fail(f"{label}.location: use a portable evidence location")

    def evidence(record: dict, label: str, *, allow_unavailable: bool = False) -> None:
        values = record.get("evidence")
        if not isinstance(values, list) or not values:
            fail(f"{label}.evidence: expected inspected source IDs")
            return
        for identifier in values:
            accepted = read_sources | unavailable_sources if allow_unavailable else read_sources
            if not isinstance(identifier, str) or identifier not in accepted:
                fail(f"{label}.evidence: source was not inspected: {identifier!r}")

    for index, component in enumerate(records("components")):
        label = f"components[{index}]"
        for key in ("name", "purpose"):
            nonempty(component.get(key), f"{label}.{key}")
        path_list(component.get("paths"), f"{label}.paths")
        evidence(component, label)

    rule_ids: set[str] = set()
    for index, rule in enumerate(records("rules")):
        label = f"rules[{index}]"
        for key in ("id", "when", "invariant", "failure", "pass_case"):
            nonempty(rule.get(key), f"{label}.{key}")
        identifier = rule.get("id")
        if isinstance(identifier, str):
            if not NAME_RE.fullmatch(identifier) or len(identifier) > 64:
                fail(f"{label}.id: use lowercase-hyphen-case, at most 64 characters")
            if identifier in rule_ids:
                fail(f"{label}: duplicate rule ID {identifier!r}")
            rule_ids.add(identifier)
        if not isinstance(rule.get("kind"), str) or rule["kind"] not in {"requirement", "observed-contract", "recommendation"}:
            fail(f"{label}.kind: invalid evidence classification")
        path_list(rule.get("paths"), f"{label}.paths")
        evidence(rule, label)

    for index, check in enumerate(records("checks")):
        label = f"checks[{index}]"
        for key in ("name", "command", "purpose", "side_effects"):
            nonempty(check.get(key), f"{label}.{key}")
        if not portable_path(check.get("cwd"), allow_dot=True):
            fail(f"{label}.cwd: use a repository-relative working directory")
        if not isinstance(check.get("execution"), str) or check["execution"] not in {"safe-local", "isolated-only", "manual-only", "unavailable"}:
            fail(f"{label}.execution: invalid execution classification")
        evidence(check, label, allow_unavailable=check.get("execution") == "unavailable")

    gaps = profile.get("coverage_gaps")
    if not isinstance(gaps, list) or any(not isinstance(item, str) or not item.strip() for item in gaps):
        fail("coverage_gaps: expected a list of non-empty strings")

    return {
        "passed": not errors,
        "errors": errors,
        "root": str(root),
        "source_count": len(source_ids),
        "rule_count": len(rule_ids),
        "limitations": "Structure and evidence references only; inspect rule accuracy, execution safety, and review behavior separately.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviewer", type=Path, help="Generated reviewer directory")
    parser.add_argument("--report-only", action="store_true", help="Return diagnostics without a failing process exit; passed remains false for invalid output")
    args = parser.parse_args()
    try:
        report = validate(args.reviewer)
    except (OSError, UnicodeError, ValueError) as error:
        report = {"passed": False, "errors": [f"Could not inspect reviewer: {error}"]}
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] or args.report_only else 1


if __name__ == "__main__":
    sys.exit(main())
