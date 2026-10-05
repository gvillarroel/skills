#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11"]
# ///
"""Compare immutable native screenshots before diagnosing apparent font changes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "projects/diagram-compactness/artifacts/reviews/compact-slidev-echarts-20261004-sol-first-probe-final-natural-2/independent-deck"
OUTPUT = ROOT / "projects/diagram-compactness/artifacts/reviews/caption-pixel-diagnosis"
OUTPUT.mkdir(parents=True, exist_ok=True)
patches = {"receive-glyphs": (110, 421, 180, 457),
           "retest-glyphs": (535, 320, 622, 355),
           "caption-leading-glyph": (520, 420, 550, 460),
           "caption-route": (495, 413, 671, 493)}
report = {"sourceDimensions": {}, "patches": {}, "originalsUnchanged": True}
for name, bounds in patches.items():
    compared = []
    for state in ("resized", "reduced-motion"):
        path = SOURCE / f"{state}.png"
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as native:
            report["sourceDimensions"][state] = list(native.size)
            patch = native.convert("RGB").crop(bounds)
        payload = patch.tobytes()
        compared.append(payload)
        patch.save(OUTPUT / f"{state}-{name}.png")
        patch.resize((patch.width * 4, patch.height * 4), Image.Resampling.NEAREST).save(OUTPUT / f"{state}-{name}-4x.png")
        report["patches"].setdefault(name, {})[state] = {"sha256": hashlib.sha256(payload).hexdigest(), "bounds": list(bounds)}
        report["originalsUnchanged"] &= before == hashlib.sha256(path.read_bytes()).hexdigest()
    report["patches"][name]["pixelIdentical"] = compared[0] == compared[1]
    report["patches"][name]["differentChannelValues"] = sum(first != second for first, second in zip(*compared, strict=True))
result = OUTPUT / "comparison.json"
result.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
