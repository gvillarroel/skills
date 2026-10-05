#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read original statuses so this audit cannot clear unrelated open gates."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
source = subprocess.run(["git", "show", "HEAD:SKILLS.md"], cwd=root, capture_output=True,
                        text=True, encoding="utf-8", check=True).stdout
for line in source.splitlines():
    if not line.startswith("| "):
        continue
    cells = line.split("|")
    if len(cells) >= 6 and (root / "skills" / cells[1].strip() / "SKILL.md").is_file():
        print(json.dumps({"skill": cells[1].strip(), "originalStatus": cells[2].strip()}))
