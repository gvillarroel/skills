#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "playwright>=1.55,<2", "Pillow>=11,<13"]
# ///
"""Verify source CSS/SVG paint order over actual opaque Manim delivery tiles."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from PIL import Image, ImageColor

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/arrow-contrast-composition/artifacts/manim-backing"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "skills/manim-svg-video/scripts"))
spec = importlib.util.spec_from_file_location("compositor", ROOT / "skills/manim-svg-video/scripts/compose_svg_video.py")
m = importlib.util.module_from_spec(spec)
sys.modules["compositor"] = m
spec.loader.exec_module(m)
baseline = (ROOT / "projects/arrow-contrast-composition/artifacts/baseline/manim-marker.svg").read_text()
variants = {
    "transparent": "",
    "css-white": "<style>svg{background-color:#ffffff}</style>",
    "css-alpha-white": "<style>svg{background-color:rgba(255,255,255,.5)}</style>",
    "rect-white": '<rect width="360" height="180" fill="#ffffff"/>',
    "rect-alpha-white": '<rect width="360" height="180" fill="#ffffff" fill-opacity=".5"/>',
    "css-alpha-rect-alpha": '<style>svg{background-color:rgba(255,255,255,.5)}</style><rect width="360" height="180" fill="#007298" fill-opacity=".5"/>',
    "css-white-rect-alpha": '<style>svg{background-color:#ffffff}</style><rect width="360" height="180" fill="#333e48" fill-opacity=".5"/>',
    "css-alpha-rect-opaque": '<style>svg{background-color:rgba(255,255,255,.5)}</style><rect width="360" height="180" fill="#333e48"/>',
}
results = []

def luminance(color):
    values = [v / 255 for v in color]
    values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return sum(v * w for v, w in zip(values, [.2126, .7152, .0722]))

def contrast(left, right):
    a, b = sorted([luminance(left), luminance(right)])
    return (b + .05) / (a + .05)

for tile in ["#ffffff", "#333e48"]:
    for variant, backing in variants.items():
        ident = variant + ("-white" if tile == "#ffffff" else "-dark")
        source = OUT / (ident + ".svg")
        source.write_text(baseline.replace('<rect width="360" height="180" fill="#ffffff"/>', backing), encoding="utf-8")
        args = SimpleNamespace(import_mode="auto", render_source="final", snapshot_seconds=0,
                               preserve_source_media=[source], tile_fill=tile)
        asset = m.prepare_asset(m.Asset(source, source, ident), len(results) + 1, args, OUT)
        audit = json.loads(asset.prepared_source.with_suffix(".arrow-audit.json").read_text())
        assert audit["deliveryBacking"] == tile and audit["headCount"] == 1 and audit["shaftCount"] == 1
        assert {i["kind"] for i in audit["issues"]} <= {"arrow-low-contrast"}
        png = Image.open(asset.prepared_source).convert("RGBA")
        composed = Image.alpha_composite(Image.new("RGBA", png.size, ImageColor.getrgb(tile) + (255,)), png)
        point = (int(180 * png.width / 360), int(75 * png.height / 180))
        pixel = composed.getpixel(point)[:3]
        reported = audit["records"][0]["at"]["background"]
        # PNG quantizes alpha to eight bits; the native geometry sampler may
        # retain the CSS fill-opacity float. Check their actual backing agreement.
        assert max(abs(a - b) for a, b in zip(pixel, reported)) <= 1.1, (ident, pixel, reported)
        minimum = min(r["minimum"] for r in audit["records"] if r.get("minimum") is not None)
        assert abs(minimum - contrast((105, 105, 105), pixel)) < .04, (ident, minimum, pixel)
        assert audit["sourceMediaPreservation"]["authoredQualityPassed"] == (not audit["issues"])
        assert bool(audit["issues"]) == (minimum < 3 - 1e-10)
        composed.save(OUT / (ident + "-delivery.png"))
        results.append({"id": ident, "tile": tile, "sourceCssBacking": audit["sourceCssBacking"],
                        "sourcePixelAlpha": png.getpixel(point)[3], "actualCompositePixel": pixel,
                        "reportedBacking": reported, "minimum": minimum,
                        "authoredQualityPassed": audit["sourceMediaPreservation"]["authoredQualityPassed"],
                        "retainedFindings": audit["issues"]})

source = OUT / "root-image.svg"
source.write_text(baseline.replace('<rect width="360" height="180" fill="#ffffff"/>', '<style>svg{background-image:linear-gradient(white,black)}</style>'), encoding="utf-8")
args = SimpleNamespace(import_mode="auto", render_source="final", snapshot_seconds=0,
                       preserve_source_media=[source], tile_fill="#333e48")
try:
    m.prepare_asset(m.Asset(source, source, "root-image"), len(results) + 1, args, OUT)
    raise AssertionError("Source preservation must not waive unsupported root CSS backing")
except RuntimeError as error:
    assert "Unsupported SVG root background image" in str(error)
    results.append({"id": "unsupported-root-image-refused", "reason": str(error)})

(OUT / "results.json").write_text(json.dumps({"passed": True, "cases": results}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"passed": True, "cases": len(results), "matrixCases": 16,
                  "acceptedAuthored": sum(r.get("authoredQualityPassed", False) for r in results)}))
