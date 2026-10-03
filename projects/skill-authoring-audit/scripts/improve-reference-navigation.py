#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Apply the audited navigation-only repairs while preserving existing guidance."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("authoring_checks", ROOT / "skills/repository-reviewer-creator/scripts/check_skill_authoring.py")
assert SPEC and SPEC.loader
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)
COLLECTIONS = {
    "d3": ("references/patterns", "Named visual mechanisms and geometry recipes"),
    "slidev-echarts": ("references/charts", "Chart-specific data, modules, motion, and pitfalls"),
    "slidev-animejs": ("references/animations", "Animation-specific APIs, lifecycle, and pitfalls"),
}


def with_contents(text: str) -> str:
    toc = re.search(r"^#{1,3}\s+(?:Contents|Table of contents)\s*\n", CHECKS.without_fences(text), re.MULTILINE | re.IGNORECASE)
    if toc:
        following = re.search(r"^#{1,3}\s+", CHECKS.without_fences(text)[toc.end():], re.MULTILINE)
        end = toc.end() + following.start() if following else len(text)
        text = text[:toc.start()] + text[end:]
    title = re.search(r"^#\s+.+\n", text)
    if not title:
        raise ValueError("Reference lacks a title")
    sections = [(heading, slug) for level, heading, slug in CHECKS.headings(text) if level == 2]
    if not sections:
        # A long single-section recipe still needs a named, previewable section.
        text = text[:title.end()] + "\n## Recipe\n" + text[title.end():]
        sections = [("Recipe", "recipe")]
    toc_lines = ["", "## Contents", "", *[f"- [{heading}](#{slug})" for heading, slug in sections], ""]
    return text[:title.end()] + "\n".join(toc_lines) + "\n" + text[title.end():].lstrip("\n")


def main() -> None:
    repairs = []
    for skill in sorted((ROOT / "skills").iterdir()):
        if not skill.is_dir() or not (skill / "SKILL.md").exists():
            continue
        audit = CHECKS.check_skill(skill)
        for issue in audit["issues"]:
            if issue["code"] not in {"reference-contents", "reference-contents-links", "windows-path"}:
                continue
            path = skill / issue["path"]
            text = path.read_text(encoding="utf-8")
            if issue["code"].startswith("reference-contents"):
                text = with_contents(text)
            elif issue["code"] == "windows-path":
                text = re.sub(r"(?:[A-Za-z]:\\|\b(?:skills|references|scripts|assets)\\)[^\s`]+", lambda match: match[0].replace("\\", "/"), text)
            path.write_text(text, encoding="utf-8", newline="\n")
            repairs.append({"path": path.relative_to(ROOT).as_posix(), "code": issue["code"]})
        missing = [issue["path"] for issue in audit["issues"] if issue["code"] == "reference-route"]
        if missing:
            entry = skill / "SKILL.md"
            collection = COLLECTIONS.get(skill.name)
            rows = []
            if collection and any(path.startswith(collection[0] + "/") for path in missing):
                rows.append(f"- {collection[1]}: [{collection[0]}/]({collection[0]}/). Select a matching filename here and read that file in full; avoid chaining index reads.")
                missing = [path for path in missing if not path.startswith(collection[0] + "/")]
            for relative in missing:
                heading = next((title for level, title, _ in CHECKS.headings((skill / relative).read_text(encoding="utf-8")) if level == 1), Path(relative).stem.replace("-", " ").title())
                rows.append(f"- [{heading}]({relative}).")
            if rows:
                text = entry.read_text(encoding="utf-8").rstrip() + "\n\n## Additional reference routes\n\nRead only the resource matching the task.\n\n" + "\n".join(rows) + "\n"
                entry.write_text(text, encoding="utf-8", newline="\n")
                repairs.append({"path": entry.relative_to(ROOT).as_posix(), "code": "reference-route", "routes": len(rows)})
    destination = ROOT / "projects/skill-authoring-audit/artifacts/manifests/navigation-repairs.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(repairs, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repairCount": len(repairs), "changedFiles": len({row["path"] for row in repairs}), "repairs": repairs}, indent=2))


if __name__ == "__main__":
    main()
