#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory authored literal colors in the six diagram/Slidev bundles."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ["mermaid", "plantuml-colorset-renderer", "echarts-animated-svg", "slidev-echarts", "slidev-animejs", "slidev-quality-audit"]
palette = json.loads((ROOT / "skills/hyperframes-explainer/assets/palettes/colorsets.json").read_text())
sets = {name: set(data["allowed"]) for name, data in palette["colorsets"].items()}
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*[.\d]+)?\s*\)")
rows = []
for skill in SKILLS:
    for path in sorted((ROOT / "skills" / skill).rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".svg", ".html", ".css", ".js", ".mjs", ".ts", ".vue", ".py", ".mmd", ".puml", ".md"}:
            continue
        if any(part in {"node_modules", "dist", ".venv", "__pycache__"} for part in path.parts):
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        tokens = []
        for match in HEX.finditer(source):
            token = match.group().lower()
            if len(token) == 4:
                token = "#" + "".join(char * 2 for char in token[1:])
            if len(token) in {7, 9}:
                tokens.append(token[:7])
        tokens += ["#" + "".join(f"{int(v):02x}" for v in match.groups()) for match in RGB.finditer(source)]
        if tokens:
            colors = set(tokens)
            rows.append({"skill": skill, "path": path.relative_to(ROOT).as_posix(), "colors": sorted(colors), "fits": [name for name, allowed in sets.items() if colors <= allowed], "outsideColorset2": sorted(colors - sets["colorset2"])})
out = ROOT / "projects/colorset-audit/artifacts/data/diagram-literals.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
for skill in SKILLS:
    group = [row for row in rows if row["skill"] == skill]
    offenders = [row for row in group if row["outsideColorset2"]]
    print(skill, "coloredFiles", len(group), "offPaletteFiles", len(offenders), "offColors", dict(Counter(c for row in offenders for c in row["outsideColorset2"])))
print(out.relative_to(ROOT).as_posix())
