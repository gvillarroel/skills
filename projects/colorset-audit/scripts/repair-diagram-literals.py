#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Repair reviewed obsolete authored color literals; never edit source data or IDs."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
REPLACEMENTS = {
    "#eef2f7":"#f7f7f7", "#99f6e4":"#cdf3ff", "#fecdd3":"#ffccd5", "#fed7aa":"#ffe5cc",
    "#3730a3":"#431f47", "#c7d2fe":"#652f6c", "#ccfbf1":"#cdf3ff", "#ecfdf5":"#dbffcc", "#eefdf7":"#dbffcc",
    "#1e293b":"#333e48", "#0f172a":"#1c1c1c", "#fcd34d":"#f1c319", "#fde68a":"#fff4cc", "#eff6ff":"#cdf3ff",
    "#b7b7b7":"#b5b5b5", "#9f9f9f":"#9c9c9c", "#878787":"#828282",
}
reviewed = [
    ROOT / "skills/slidev-echarts/assets/examples/slidev-echarts",
    ROOT / "skills/slidev-animejs/assets/examples/slidev-animejs",
    ROOT / "skills/slidev-animejs/assets/templates/slidev-svg-asset-pack",
    ROOT / "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/scripts",
    ROOT / "skills/slidev-echarts/references",
    ROOT / "skills/slidev-animejs/references",
]
changed=[]
for folder in reviewed:
    for path in folder.rglob("*"):
        if not path.is_file() or path.suffix not in {".css", ".js", ".mjs", ".vue", ".md", ".svg"} or any(part in {"node_modules", "dist"} for part in path.parts):
            continue
        old=path.read_text(encoding="utf-8")
        new=re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: REPLACEMENTS.get(m.group().lower(), m.group()), old)
        new=re.sub(r"rgba?\(\s*15\s*,\s*23\s*,\s*42\s*,", "rgba(28, 28, 28,", new)
        new=re.sub(r"rgba?\(\s*148\s*,\s*163\s*,\s*184\s*,", "rgba(156, 156, 156,", new)
        new=re.sub(r"rgba?\(\s*15\s*,\s*118\s*,\s*110\s*,", "rgba(0, 114, 152,", new)
        if new != old:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(ROOT).as_posix())
print("\n".join(changed))
