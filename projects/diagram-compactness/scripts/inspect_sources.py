#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print bounded source excerpts for the diagram compactness audit."""
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding="utf-8")

root = Path(__file__).resolve().parents[3]
if len(sys.argv) == 1:
    names = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    for line in (root / "SKILLS.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and line.split("|")[1].strip() in names:
            print(line[:1500])
else:
    for argument in sys.argv[1:]:
        target = (root / argument).resolve()
        target.relative_to(root)
        print(f"\nSOURCE: {argument}\n")
        print(target.read_text(encoding="utf-8")[:24000])
