#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "pillow>=10.0.0"]
# ///
"""Capture controlled cases and their actual local text/background diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "projects/svg-text-contrast/artifacts"
sys.path.insert(0, str(ROOT / "skills/compose-synchronized-svg/scripts"))
from playwright.sync_api import sync_playwright
from text_contrast import audit_text_contrast

results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    for name in ("world-light", "near-threshold", "compact-dark", "light-mark"):
        for variant in ("before", "after"):
            page = browser.new_page(viewport={"width": 1800, "height": 1200})
            page.goto((ARTIFACTS / name / f"{variant}.svg").as_uri())
            page.wait_for_function("window.svgSync && document.documentElement.dataset.syncReady === 'true'")
            page.evaluate("() => {svgSync.pause(); svgSync.pauseCamera();svgSync.reset();}")
            page.wait_for_timeout(200)
            original = page.evaluate("() => svgSync.serializeSnapshot()")
            report = audit_text_contrast(page)
            assert original == page.evaluate("() => svgSync.serializeSnapshot()")
            page.screenshot(path=str(ARTIFACTS / name / f"{variant}.png"))
            if name == "world-light":
                page.locator(".navigation-hud").screenshot(path=str(ARTIFACTS / name / f"hud-{variant}.png"))
            (ARTIFACTS / name / f"text-{variant}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            summary = {"case": name, "variant": variant, **{key: value for key, value in report.items() if key != "findings"}}
            results.append(summary)
            print(json.dumps(summary))
            page.close()
    browser.close()
(ARTIFACTS / "case-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

titles = {"world-light": "Navigation: pair secondary text with the dark panel",
          "near-threshold": "Near-threshold text: protect its real background",
          "compact-dark": "Dark theme: keep labels outside colored ribbons",
          "light-mark": "Light concept marks: use a readable value-text color"}
cards = []
for name, title in titles.items():
    figures = []
    for variant in ("before", "after"):
        result = next(item for item in results if item["case"] == name and item["variant"] == variant)
        image = f"hud-{variant}.png" if name == "world-light" else f"{variant}.png"
        figures.append(f'<figure><figcaption><b>{variant.title()}</b> · {result["failed"]} contrast findings · '
                       f'{result["incomplete"]} incomplete</figcaption><a href="{name}/{variant}.svg">'
                       f'<img src="{name}/{image}" alt="{variant.title()}: {title}"></a></figure>')
    cards.append(f'<section><h2>{title}</h2><div class="pair">{"".join(figures)}</div></section>')
html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SVG text and background pairing</title><style>
*{box-sizing:border-box}body{margin:0;background:#f4f6f5;color:#203332;font:16px/1.5 system-ui,sans-serif}
main{max-width:1500px;margin:auto;padding:36px 24px}h1{font-size:34px;line-height:1.15;margin-bottom:12px}
p{max-width:900px}section{background:white;border:1px solid #d5dfdc;border-radius:14px;padding:24px;margin:28px 0}
h2{font-size:21px;margin-top:0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0;min-width:0}
figcaption{padding:8px 0;color:#425654}img{display:block;width:100%;height:auto;max-height:580px;object-fit:contain;border:1px solid #d5dfdc;border-radius:7px}
a{color:#156f65}code{background:#e9f0ed;padding:2px 5px}footer{font-size:14px;color:#586a68}
@media(max-width:760px){main{padding:20px 12px}.pair{grid-template-columns:1fr}section{padding:14px}h1{font-size:27px}}
</style><main><h1>Readable text starts with its actual background</h1>
<p>Controlled before/after renders use the same briefs, data, and scenarios. The generator now pairs inverse controls correctly,
keeps user-owned mark colors, protects label surfaces, and checks the painted background under the letters.</p>
<p>Click an image to open its standalone SVG. Counts apply to the captured initial view. Full browser audits also exercise scenarios,
focus, navigation views, and fallbacks. Unsupported text effects remain explicit incomplete findings.</p>'''
html += "".join(cards)
html += '<footer>Local evaluation · 2026-09-04 · Sources and reports remain beside each SVG. Text checks use a conservative 4.5:1 threshold; sampled checks are not a complete accessibility certification.</footer></main></html>'
(ARTIFACTS / "comparison.html").write_text(html, encoding="utf-8")
