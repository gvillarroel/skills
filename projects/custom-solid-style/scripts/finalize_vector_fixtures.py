#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the solid-first policy to legacy vector gallery presentation only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "skills/vectorize-art-patterns/assets/examples"
MAPS = EXAMPLES / "vectorize-abstract-world-maps"
OUT = ROOT / "projects/custom-solid-style/artifacts/data"


def borderless_css(text: str) -> str:
    # Rounded silhouettes are geometry, and keyboard focus outlines remain visible.
    text = re.sub(r"(?m)^(\s*)border(?:-(?:top|right|bottom|left))?\s*:\s*[^;]+;", r"\1border: 0;", text)
    text = re.sub(r"(?m)^\s*border-color\s*:\s*[^;]+;\n?", "", text)
    text = re.sub(r"(--(?:ink|ink-soft|ink-dark|muted):)\s*#[0-9a-fA-F]{6}", r"\1 #000000", text)
    text = re.sub(r"color:\s*var\(--(?:red|red-dark|primary|primary-dark)\)", "color: #000000", text)
    text = text.replace("color: #ffccd5", "color: #ffffff")
    # Gaps made from a contrasting backing plane would recreate hairline borders.
    text = text.replace("background: #4f4f4f", "background: var(--ink)")
    text = text.replace("background: var(--line);", "background: transparent;")
    return text


css_path = EXAMPLES / "vectorize-art-patterns/gallery.css"
css_path.write_text(borderless_css(css_path.read_text(encoding="utf-8")), encoding="utf-8")
page_path = MAPS / "index.html"
page_path.write_text(borderless_css(page_path.read_text(encoding="utf-8")), encoding="utf-8")
palette_hash = hashlib.sha256((ROOT / "skills/vectorize-art-patterns/assets/palettes/colorsets.json").read_bytes()).hexdigest()
manifest_path = MAPS / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
records = []
for item in manifest["patterns"]:
    path = MAPS / item["file"]
    before = path.read_text(encoding="utf-8")
    before_tree = ET.fromstring(before)
    geometry = [(element.get("id"), element.get("d")) for element in before_tree.iter() if element.tag.endswith("}path")]
    removed = 0

    def strip_shape(match: re.Match[str]) -> str:
        global removed
        shape = match.group(0)
        fill = re.search(r'\bfill="([^"]+)"', shape)
        if not fill or fill[1] == "none" or 'id="world-coastline"' in shape:
            return shape
        if re.search(r'\bstroke="(?!none)[^"]+"', shape):
            removed += 1
        return re.sub(r'\s+stroke(?:-[a-z-]+)?="[^"]*"', "", shape)

    after = re.sub(r"<path\b[^>]*>", strip_shape, before)
    after = re.sub(r'("palette_contract_sha256":")([0-9a-f]{64})(")', lambda m: m[1] + palette_hash + m[3], after)
    after_tree = ET.fromstring(after)
    assert geometry == [(element.get("id"), element.get("d")) for element in after_tree.iter() if element.tag.endswith("}path")]
    path.write_text(after, encoding="utf-8")
    item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    records.append({"id": item["id"], "removedDecorativeOutlines": removed, "geometryPreserved": True, "sha256": item["sha256"]})
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "vector-fixture-finalization.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
print(json.dumps(records, indent=2))
