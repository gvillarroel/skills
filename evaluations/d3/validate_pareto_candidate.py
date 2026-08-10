#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate and profile one immutable D3 Pareto candidate bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

from verify_pareto_task import bundle_profile, runtime_files


EXPECTED_PATTERN_COUNT = 238
REQUIRED_RESOURCES = (
    "SKILL.md",
    "agents/openai.yaml",
    "assets/palettes/colorsets.json",
    "assets/vendor/d3.v7.9.0.min.js",
    "references/pattern-index.md",
    "references/pattern-routing.md",
    "references/pattern-selection-contracts.md",
    "references/evaluation-rubric.md",
    "references/recomposition-recipes.md",
    "references/palette-contract.md",
    "references/pattern-catalog.md",
    "scripts/build_contract_artifact.py",
    "scripts/build_evaluation_report.py",
    "scripts/check_palette_contract.py",
    "scripts/check_recomposition_contract.py",
    "scripts/check_self_contained_html.py",
    "scripts/check_visual_contract.py",
    "scripts/render_d3_svg.py",
    "scripts/validate_logo_artifact.py",
)
PATH_TOKEN = re.compile(r"`((?:skills/d3/)?(?:references|scripts|assets)/[^`]+)`")
INDEX_PATTERN = re.compile(r"`(references/patterns/[a-z0-9-]+\.md)`")
RETIRED_D3_SKILL = re.compile(
    r"skills/d3-(?:animated-svg|composition-evaluator|composition-recomposer|logo-design)(?:/|\b)"
)


def digest_files(root: Path, files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix()
        payload = path.read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(payload)).encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        stat = path.stat(follow_symlinks=False)
    except OSError:
        return True
    attributes = getattr(stat, "st_file_attributes", 0)
    reparse_flag = getattr(os, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def frontmatter_findings(skill_text: str) -> list[str]:
    if not skill_text.startswith("---\n"):
        return ["SKILL.md does not start with YAML frontmatter"]
    parts = skill_text.split("---", 2)
    if len(parts) < 3:
        return ["SKILL.md frontmatter is not closed"]
    fields = {
        line.split(":", 1)[0].strip()
        for line in parts[1].splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    findings: list[str] = []
    if fields != {"name", "description"}:
        findings.append(f"Frontmatter fields must be name and description only, found {sorted(fields)}")
    if not re.search(r"(?m)^name:\s*d3\s*$", parts[1]):
        findings.append("Frontmatter name is not d3")
    return findings


def normalize_token(token: str) -> str | None:
    token = token.strip().rstrip(".,;:").replace("\\", "/")
    token = token.split(maxsplit=1)[0]
    if token.startswith("skills/d3/"):
        token = token.removeprefix("skills/d3/")
    token = token.split("#", 1)[0]
    if any(character in token for character in "<>{}*"):
        return None
    if token.startswith("assets/examples/"):
        return None
    return token


def path_findings(root: Path, markdown: list[Path]) -> list[str]:
    findings: list[str] = []
    for source in markdown:
        text = source.read_text(encoding="utf-8", errors="replace")
        for match in PATH_TOKEN.finditer(text):
            token = normalize_token(match.group(1))
            if token and not (root / token).exists():
                findings.append(
                    f"Missing routed resource {token} from {source.relative_to(root).as_posix()}"
                )
    return sorted(set(findings))


def validate(root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve()
    findings: list[str] = []
    if not (root / "SKILL.md").is_file():
        return {"ok": False, "candidate": str(root), "findings": ["Missing SKILL.md"]}

    files = runtime_files(root)
    markdown = sorted(path for path in files if path.suffix.casefold() == ".md")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    findings.extend(frontmatter_findings(skill_text))

    for relative in REQUIRED_RESOURCES:
        if not (root / relative).is_file():
            findings.append(f"Missing required runtime resource: {relative}")

    for path in [root, *root.rglob("*")]:
        if is_reparse_point(path):
            findings.append(f"Link or reparse point is forbidden: {path.relative_to(root)}")

    findings.extend(path_findings(root, markdown))
    joined_markdown = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in markdown
    )
    if RETIRED_D3_SKILL.search(joined_markdown):
        findings.append("Candidate routes to a retired sibling D3 skill")
    if "assets/examples" in skill_text.replace("\\", "/"):
        findings.append("SKILL.md routes normal use into acceptance examples")

    pattern_files = sorted((root / "references" / "patterns").glob("*.md"))
    if len(pattern_files) != EXPECTED_PATTERN_COUNT:
        findings.append(
            f"Expected {EXPECTED_PATTERN_COUNT} compact pattern references, found {len(pattern_files)}"
        )
    index_text = (root / "references" / "pattern-index.md").read_text(encoding="utf-8")
    indexed = set(INDEX_PATTERN.findall(index_text))
    actual = {
        path.relative_to(root).as_posix()
        for path in pattern_files
    }
    if indexed != actual:
        missing = sorted(actual - indexed)
        stale = sorted(indexed - actual)
        findings.append(
            f"Pattern index mismatch: missing={missing[:5]}, stale={stale[:5]}"
        )

    profile = bundle_profile(root, policy)
    findings.extend(profile["findings"])
    result = {
        "ok": not findings,
        "candidate": str(root),
        "sha256": digest_files(root, files),
        "fileCount": len(files),
        "byteCount": sum(path.stat().st_size for path in files),
        "patternReferenceCount": len(pattern_files),
        "bundleProfile": profile,
        "findings": sorted(set(findings)),
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--dataset-manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.dataset_manifest.read_text(encoding="utf-8"))
    result = validate(args.candidate, manifest["bundleProfile"])
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
