#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare staged SSR native geometry/paint/text with committed gallery baseline."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "daaee75353c63ed6dde204d57cfdbae6b9936586"  # Qualified baseline HEAD before grayscale changes.
PROJECT = ROOT / "projects/grayscale-interleave"
RELATIVE = "skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html"
STAGED = PROJECT / "artifacts/staged-blobs/echarts-head-native/assets/examples/echarts-animated-svg/index.html"
OUT = PROJECT / "artifacts/reviews/echarts-head-native-final/head-native-comparison.json"


class NativeSvgParser(HTMLParser):
    """Read the delivered inline SVG as HTML, including boolean data attributes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attributes = {
            name: re.sub(r"zr\d+", "zr-instance", value) if value is not None else None
            for name, value in attrs if name not in {"id", "data-zr-dom-id"}
        }
        entry = [tag, attributes, []]
        if tag != "style":
            self.entries.append(entry)
        self.stack.append(entry)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            raise ValueError(f"Malformed inline SVG closing tag: {tag}")
        self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.stack and self.stack[-1][0] != "style" and data.strip():
            self.stack[-1][2].append(data.strip())


def signatures(source: str) -> dict:
    cards = re.findall(
        r'<article\b[^>]*data-example-id="([^"]+)"[^>]*>(.*?)</article>',
        source, flags=re.DOTALL,
    )
    result = {}
    for key, body in cards:
        match = re.search(r'<svg\b.*?</svg>', body, flags=re.DOTALL)
        if match is None:
            raise ValueError(f"No native SVG for {key}")
        parser = NativeSvgParser()
        parser.feed(match.group(0))
        parser.close()
        if parser.stack:
            raise ValueError(f"Unclosed native SVG for {key}")
        result[key] = parser.entries
    if len(result) != 43:
        raise ValueError(f"Expected 43 uniquely named native cards, received {len(result)}")
    return result


def main() -> None:
    before_bytes = subprocess.run(
        ["git", "show", f"{BASE}:{RELATIVE}"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    after_bytes = STAGED.read_bytes()
    before = signatures(before_bytes.decode("utf-8"))
    after = signatures(after_bytes.decode("utf-8"))
    if set(before) != set(after):
        raise ValueError("Native card identities changed")
    rows = []
    metadata_only = []
    for key in before:
        differences = []
        for index in range(max(len(before[key]), len(after[key]))):
            old = before[key][index] if index < len(before[key]) else None
            new = after[key][index] if index < len(after[key]) else None
            if old != new:
                differences.append({"index": index, "before": old, "after": new})
        rows.append({"id": key, "same": not differences, "differenceCount": len(differences), "differences": differences[:8]})
        if differences:
            pure_metadata = True
            for difference in differences:
                old, new = difference["before"], difference["after"]
                if old is None or new is None or old[0] != "svg" or new[0] != "svg":
                    pure_metadata = False
                    break
                old_attrs, new_attrs = dict(old[1]), dict(new[1])
                old_id = old_attrs.pop("data-native-boxplot-chart", "")
                new_id = new_attrs.pop("data-native-boxplot-chart", "")
                if (old_attrs != new_attrs or old[2] != new[2]
                        or not re.fullmatch(r"boxplot-ec_\d+", old_id)
                        or not re.fullmatch(r"boxplot-ec_\d+", new_id)):
                    pure_metadata = False
                    break
            if pure_metadata:
                metadata_only.append(key)
    report = {
        "baselineRef": BASE,
        "all43NativeGeometryPaintTextUnchanged": all(row["same"] or row["id"] in metadata_only for row in rows),
        "nonRenderingMetadataChanges": metadata_only,
        "headIndexSha256": hashlib.sha256(before_bytes).hexdigest(),
        "stagedIndexSha256": hashlib.sha256(after_bytes).hexdigest(),
        "ignored": "Native renderer instance IDs and embedded generated animation stylesheet only; retain native paths, transforms, fills, strokes, font attributes, clip references, text and other structural attributes.",
        "cards": rows,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": OUT.relative_to(ROOT).as_posix(), "all43NativeGeometryPaintTextUnchanged": report["all43NativeGeometryPaintTextUnchanged"], "rawAttributeSameCount": sum(row["same"] for row in rows), "total": len(rows), "changed": [row["id"] for row in rows if not row["same"]], "nonRenderingMetadataChanges": metadata_only, "headIndexSha256": report["headIndexSha256"], "stagedIndexSha256": report["stagedIndexSha256"]}, indent=2))


if __name__ == "__main__":
    main()
