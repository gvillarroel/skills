#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Check a standalone skill's measurable authoring and navigation contracts.

Run with uv run --script check_skill_authoring.py <skill-directory>.
These checks do not grade instruction accuracy or agent behavior.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


MAX_NAME = 63  # Repository convention is stricter than the platform's 64 maximum.
MAX_DESCRIPTION = 1024
MAX_BODY_LINES = 499  # The authoring guide recommends fewer than 500 lines.
LONG_REFERENCE_LINES = 100
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
LINK_RE = re.compile(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[\"'][^\"']*[\"'])?\)")
INLINE_RESOURCE_RE = re.compile(r"`(references/[A-Za-z0-9_./-]+(?:#[A-Za-z0-9_-]+)?)`")
WINDOWS_RESOURCE_RE = re.compile(r"(?:\b(?:references|scripts|assets)\\[A-Za-z0-9_]|\b[A-Za-z]:\\[A-Za-z0-9_])")
IGNORED_DIRS = {"node_modules", "__pycache__", ".git", ".cache", ".pytest_cache", ".ruff_cache", ".venv", "dist", "output", "test-results", "playwright-report"}
DESCRIPTION_ACTIONS = {"animate", "audit", "author", "build", "calculate", "choose", "combine", "compare", "compose", "convert", "create", "decompose", "design", "download", "edit", "evaluate", "export", "extract", "find", "generate", "inspect", "manage", "orchestrate", "present", "process", "recompose", "record", "render", "restyle", "retrieve", "review", "search", "select", "show", "simplify", "split", "style", "synchronize", "transform", "troubleshoot", "update", "validate", "verify"}


class UniqueLoader(yaml.SafeLoader):
    """Reject silently overwritten frontmatter keys."""


def unique_mapping(loader: UniqueLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise yaml.constructor.ConstructorError(None, None, "duplicate or non-string mapping key", key_node.start_mark)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def without_fences(content: str) -> str:
    """Hide fenced code while retaining line numbers, including four-backtick fences."""
    result = []
    fence = None
    for line in content.splitlines():
        if fence:
            if re.fullmatch(r"\s{0,3}" + re.escape(fence[0]) + r"{" + str(fence[1]) + r",}\s*", line):
                fence = None
            result.append("")
            continue
        start = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if start:
            fence = (start[1][0], len(start[1]))
            result.append("")
        else:
            result.append(line)
    return "\n".join(result)


def headings(content: str) -> list[tuple[int, str, str]]:
    seen: dict[str, int] = {}
    result = []
    for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*#*\s*$", without_fences(content), re.MULTILINE):
        title = match[2]
        plain = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", title)
        slug = re.sub(r"[^\w\s-]", "", plain.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.append((len(match[1]), title, slug + (f"-{count}" if count else "")))
    return result


def references_from_entry(content: str) -> set[str]:
    prose = without_fences(content)
    candidates = [match[1].strip("<>") for match in LINK_RE.finditer(prose)]
    candidates += [match[1] for match in INLINE_RESOURCE_RE.finditer(prose)]
    return {unquote(urlsplit(value).path).removeprefix("./") for value in candidates if value.startswith(("references/", "./references/"))}


def check_skill(root: Path, *, profile: str = "source") -> dict:
    """Audit an arbitrary bundle without discovering siblings or repository context."""
    root = root.resolve()
    issues: list[dict] = []

    def fail(code: str, path: Path, message: str) -> None:
        issues.append({"code": code, "path": path.relative_to(root).as_posix(), "message": message})

    entry = root / "SKILL.md"
    if not entry.is_file():
        return {"passed": False, "skill": root.name, "issues": [{"code": "missing-entry", "path": "SKILL.md", "message": "SKILL.md is required"}], "metrics": {}}
    try:
        content = entry.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        fail("entry-encoding", entry, f"Cannot read UTF-8 entrypoint: {error}")
        return {"passed": False, "skill": root.name, "issues": issues, "metrics": {}}
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
    metadata = None
    if not match:
        fail("frontmatter", entry, "Start SKILL.md with closed YAML frontmatter")
    else:
        try:
            metadata = yaml.load(match[1], Loader=UniqueLoader)
        except yaml.YAMLError as error:
            fail("frontmatter", entry, f"Invalid or duplicate YAML fields: {error}")
        else:
            if metadata is None:
                fail("frontmatter-fields", entry, "Frontmatter must contain name and description")
    if metadata is not None:
        if not isinstance(metadata, dict) or set(metadata) != {"name", "description"}:
            fail("frontmatter-fields", entry, "Frontmatter must contain only name and description")
        else:
            name, description = metadata["name"], metadata["description"]
            if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > MAX_NAME or name != root.name:
                fail("skill-name", entry, "Use a matching lowercase hyphen-case name shorter than 64 characters")
            if isinstance(name, str) and any(reserved in name for reserved in ("anthropic", "claude")):
                fail("reserved-name", entry, "Skill names must not contain reserved vendor names")
            if not isinstance(description, str) or not description.strip() or len(description) > MAX_DESCRIPTION:
                fail("description-length", entry, "Description must be nonempty and at most 1024 characters")
            elif "<" in description or ">" in description:
                fail("description-tags", entry, "Description must not contain angle brackets or XML tags")
            elif re.search(r"\bI(?:\s|['’])|\b(?:we|our|you|your)\b", description, re.IGNORECASE):
                fail("description-person", entry, "Describe the capability and trigger without first- or second-person address")
            elif description.split()[0].lower().rstrip(",") in DESCRIPTION_ACTIONS:
                fail("description-voice", entry, "Use a descriptive third-person opening, such as 'Reviews changes', rather than an imperative")

    body = content[match.end():] if match else content
    body_lines = len(body.splitlines())
    if not body.strip():
        fail("empty-body", entry, "Add a concrete procedural workflow")
    if body_lines > MAX_BODY_LINES:
        fail("body-size", entry, "Keep the SKILL.md body below 500 lines")
    routes = references_from_entry(body)
    references = sorted(path for path in (root / "references").rglob("*.md") if not any(part in IGNORED_DIRS for part in path.relative_to(root).parts))
    long_references = 0
    for path in [entry, *references]:
        if not path.resolve().is_relative_to(root):
            fail("resource-escape", path, "Resources must resolve inside the bundle")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            fail("reference-encoding", path, f"Cannot read UTF-8 guidance: {error}")
            continue
        if WINDOWS_RESOURCE_RE.search(text):
            fail("windows-path", path, "Use forward slashes in resource paths, including command examples")
        if path == entry:
            continue
        relative = path.relative_to(root).as_posix()
        if relative not in routes:
            fail("reference-route", path, "Link each runtime reference file directly from SKILL.md")
        if len(text.splitlines()) > LONG_REFERENCE_LINES:
            long_references += 1
            section_list = headings(text)
            toc_match = re.search(r"^#{1,3}\s+(?:Contents|Table of contents)\s*$", without_fences(text), re.MULTILINE | re.IGNORECASE)
            if not toc_match or len(text[:toc_match.start()].splitlines()) > 25:
                fail("reference-contents", path, "References longer than 100 lines need a contents section near the top")
            else:
                toc = without_fences(text)[toc_match.end():]
                toc = re.split(r"^#{1,6}\s", toc, maxsplit=1, flags=re.MULTILINE)[0]
                anchors = {slug for _, _, slug in section_list}
                local_links = [unquote(link[1][1:]) for link in LINK_RE.finditer(toc) if link[1].startswith("#")]
                if not local_links or any(anchor not in anchors for anchor in local_links):
                    fail("reference-contents-links", path, "Contents must contain working links to the reference's headings")

    if profile == "runtime" and (root / "assets/examples").exists():
        fail("runtime-fixtures", root / "assets/examples", "Runtime bundles must exclude acceptance fixtures")
    return {"passed": not issues, "skill": root.name, "issues": issues, "metrics": {"bodyLines": body_lines, "entryBytes": entry.stat().st_size, "referenceCount": len(references), "longReferenceCount": long_references}, "limitations": "Static authoring checks only; review semantics, script execution, routing, and isolated agent outcomes separately."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill", type=Path)
    parser.add_argument("--profile", choices=("source", "runtime", "full"), default="source")
    args = parser.parse_args()
    report = check_skill(args.skill, profile=args.profile)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
