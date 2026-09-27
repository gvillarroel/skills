#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Create a compact local review of the changed runtime defaults."""

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/library-composition/artifacts"
rows = [
    ("D3 process", "flow.html", "64 to 32 px nodes; 16 px labels retained. Default SVG height: 520 to 180 px."),
    ("D3 stage template", "stages.html", "132 to 100 px boxes; canvas height 420 to 320 px. Neutral surfaces and red emphasis."),
    ("D3 operations dashboard", "dashboard/index.html", "Outer padding 24 to 12 px. Gray secondary panels replace pastel highlights. Quantitative geometry stays intact."),
    ("Three.js orbit", "three.html", "Neutral materials, a red focal object, and white lights. Compact controls preserve depth and the motion envelope."),
]
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge")
    for label, relative, _ in rows:
        for variant in ("baseline", "current"):
            path = OUT / variant / relative
            page = browser.new_page(viewport={"width": 1280, "height": 844})
            page.goto(path.as_uri())
            page.wait_for_timeout(1400)
            target = page.locator("main") if relative == "three.html" else page.locator("svg").first
            name = "dashboard" if relative.startswith("dashboard/") else Path(relative).stem
            target.screenshot(path=str(OUT / variant / f"{name}-review.png"))
            page.close()
    browser.close()
cards = []
for label, relative, note in rows:
    name = "dashboard" if relative.startswith("dashboard/") else Path(relative).stem
    views = "".join(f'<figure><figcaption>{caption}</figcaption><a href="{variant}/{relative}"><img alt="{label}: {caption}" src="{variant}/{name}-review.png"></a></figure>' for variant, caption in (("baseline", "Before"), ("current", "Updated")))
    cards.append(f'<section><h2>{label}</h2><p>{note}</p><div class="pair">{views}</div></section>')
html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compact composition review</title><style>
*{box-sizing:border-box}body{margin:0;padding:24px;background:#f7f7f7;color:#333e48;font:16px/1.5 Arial,sans-serif}main{max-width:1440px;margin:auto}h1{margin:0;font-size:28px}h2{margin:0 0 8px;font-size:21px}p{margin:8px 0 16px}section{margin:20px 0;padding:12px;background:#fff;border:1px solid #cfcfcf}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0;min-width:0}figcaption{font-weight:bold;margin:0 0 8px}img{display:block;width:100%;height:auto;border:1px solid #e7e7e7}a{color:#9e1b32}small{color:#4f4f4f}@media(max-width:800px){body{padding:12px}.pair{grid-template-columns:1fr}}
</style><main><h1>Compact composition · D3 and Three.js</h1><p>White and gray structure, deliberate red emphasis, and smaller boxes and panels. Click a preview to open the live artifact.</p><p><strong>Mobile:</strong> the Three.js stage changes from 320 px to about 206 px at a 390 px viewport, with 44 px touch controls. D3 preserves native label size inside scrollable diagrams.</p>'''+"".join(cards)+'''<p><a href="current/three-extended.html">Explicit colorset2 example</a> · <a href="current/three-many.html">Twelve orbiting objects</a> · <a href="comparison.json">Browser measurements</a></p><small>Local runtime review; historical published galleries are preserved. Images show different animation instants.</small></main></html>'''
(OUT / "comparison.html").write_text(html, encoding="utf-8")
print(OUT / "comparison.html")
