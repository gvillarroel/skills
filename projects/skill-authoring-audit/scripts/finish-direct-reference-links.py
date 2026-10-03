#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Expose every runtime reference directly while keeping entrypoints below 500 lines."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("authoring_links", ROOT / "skills/repository-reviewer-creator/scripts/check_skill_authoring.py")
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def main() -> None:
    records = []
    for name in ("d3", "slidev-animejs", "slidev-echarts"):
        skill = ROOT / "skills" / name
        entry = skill / "SKILL.md"
        text = entry.read_text(encoding="utf-8")
        text = re.sub(r"^- .+: \[references/(?:patterns|animations|charts)/\].*\n", "", text, flags=re.MULTILINE)
        linked = CHECKER.references_from_entry(text)
        missing = [path for path in sorted((skill / "references").rglob("*.md")) if path.relative_to(skill).as_posix() not in linked]
        if missing:
            rows = []
            for path in missing:
                relative = path.relative_to(skill).as_posix()
                label = path.stem.replace("-", " ")
                rows.append(f"- [{label}]({relative}).")
            text = text.rstrip() + "\n\n## Direct recipe links\n\nSelect the matching recipe and read it in full.\n\n" + "\n".join(rows) + "\n"
        entry.write_text(text, encoding="utf-8", newline="\n")
        records.append({"skill": name, "addedLinks": len(missing), "bodyLines": len(text.split("---", 2)[2].splitlines())})
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
