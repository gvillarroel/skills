#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Preserve metadata meaning while making capability sentences third person."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
ACTIONS = {"aggregate", "animate", "audit", "author", "browse", "build", "calculate", "choose", "choreograph", "combine", "compare", "compose", "consolidate", "convert", "create", "decompose", "design", "download", "edit", "evaluate", "execute", "export", "extract", "find", "generate", "inspect", "manage", "orchestrate", "present", "recompose", "record", "render", "restyle", "retrieve", "review", "search", "select", "show", "simplify", "split", "style", "synchronize", "transform", "troubleshoot", "update", "validate", "verify"}


def conjugate(match: re.Match) -> str:
    word = match[2]
    if word.lower() not in ACTIONS:
        return match[0]
    if word.endswith("y"):
        result = word[:-1] + "ies"
    elif word.endswith(("ch", "sh", "ss")):
        result = word + "es"
    else:
        result = word + "s"
    return match[1] + result


def main() -> None:
    changed = []
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        content = path.read_text(encoding="utf-8")
        metadata = yaml.safe_load(content.split("---", 2)[1])
        original = metadata["description"]
        opening, separator, rest = original.partition(". Use")
        # Convert only coordinated capability verbs; preserve trigger wording,
        # API names, and infinitive verbs within object/parameter descriptions.
        opening = re.sub(r"(^|,\s+(?:and\s+|or\s+)?|\band\s+|\bor\s+)([A-Za-z]+)(?=[\s,])", conjugate, opening)
        updated = opening + separator + rest
        if path.parent.name == "asciinema-real-command-video":
            updated = updated.replace("executable, action, processes,", "executable, action, process,")
        if path.parent.name == "jev-batch-decisions":
            updated = updated.replace("documents and records collections", "documents and record collections")
        if path.parent.name == "kenney-asset-search":
            updated = updated.replace("theme, category and styles,", "theme, category and style,")
        if updated == original:
            continue
        replacement = "description: " + json.dumps(updated, ensure_ascii=False)
        content = re.sub(r"^description:.*$", lambda _: replacement, content, count=1, flags=re.MULTILINE)
        path.write_text(content, encoding="utf-8", newline="\n")
        changed.append({"skill": path.parent.name, "before": original, "after": updated})
    output = ROOT / "projects/skill-authoring-audit/artifacts/manifests/description-voice.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(output.read_text(encoding="utf-8")) if output.is_file() else []
    preserved = {row["skill"]: row for row in existing}
    for row in changed:
        if row["skill"] in preserved:
            preserved[row["skill"]]["after"] = row["after"]
        else:
            preserved[row["skill"]] = row
    output.write_text(json.dumps(list(preserved.values()), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"changedDescriptions": len(changed), "skills": [row["skill"] for row in changed]}, indent=2))


if __name__ == "__main__":
    main()
