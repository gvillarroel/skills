#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Verify finite contrasting overflow, allocation order and Python/JS parity."""
import importlib.util
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/custom-solid-style/artifacts/data"


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


d3 = load("skills/d3/scripts/colorset_adapter.py")
proc = load("skills/procedural-svg-animation/scripts/solid_style.py")
palettes = json.loads(d3.CONTRACT.read_text(encoding="utf-8"))["colorsets"]
report = []
with sync_playwright() as engine:
    browser = engine.chromium.launch(channel="msedge")
    page = browser.new_page()
    page.set_content("<body></body>")
    page.evaluate("palettes=>window.D3_SOLID_PALETTES=palettes", palettes)
    page.add_script_tag(path=str(d3.SOLID_RUNTIME))
    for colorset, palette in palettes.items():
        for canvas in ("#ffffff", "#1c1c1c"):
            solids = [paint for paint in dict.fromkeys(palette["solidSequence"]) if paint != canvas]
            count = len(solids)
            indices = set(range(count)) | {100000}
            for offset, fill in enumerate(solids):
                level = proc.luminance(fill)
                pool = [paint for paint in dict.fromkeys(palette["allowed"]) if paint != fill and
                        (max(level, proc.luminance(paint)) + .05) / (min(level, proc.luminance(paint)) + .05) >= 3]
                for variant in range(len(pool) * 9 + 2):
                    index = (variant + 1) * count + offset
                    indices.add(index)
                    style = d3.category_style(index, palette, canvas)
                    assert style == proc.category_style(index, palette, canvas)
                    if variant >= len(pool) * 9:
                        assert style["tier"] == "structural" and style["strokeWidth"] == 0 and style["cue"] == "label-symbol-or-split"
                    else:
                        assert style["tier"] == "overflow" and style["stroke"] == pool[variant % len(pool)]
                        assert style["strokeWidth"] == 1 + variant // (len(pool) * 3) <= 3
                        assert style["strokeDasharray"] == (None, "6 4", "1 3")[(variant // len(pool)) % 3]
            indices = sorted(indices)
            expected = [d3.category_style(index, palette, canvas) for index in indices]
            actual = page.evaluate("args=>args.indices.map(index=>D3SolidStyle.categoryStyle(index,args.colorset,args.canvas))", dict(indices=indices,colorset=colorset,canvas=canvas))
            assert actual == expected
            assert all(style["tier"] == "solid" and style["stroke"] == "none" for style in actual[:count])
            assert len({style["fill"] for style in actual[:count]}) == count
            assert actual[-1]["tier"] == "structural" and actual[-1]["strokeWidth"] == 0
            report.append(dict(colorset=colorset,canvas=canvas,solidCount=count,checkedIndices=len(indices),longBoundary=100000,passed=True))
    browser.close()
(OUT / "overflow-boundary-check.json").write_text(json.dumps(dict(passed=True,checks=report),indent=2)+"\n",encoding="utf-8")
print(json.dumps(dict(passed=True,checks=report)))
