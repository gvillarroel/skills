#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Verify that portable SVG preserves page-defined label and box styles."""

from pathlib import Path
import subprocess
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "projects/library-composition/artifacts"
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=OUT) as temporary:
    folder = Path(temporary)
    html = folder / "styled.html"
    svg = folder / "styled.svg"
    html.write_text('''<!doctype html><html><style>
    :root{--ink:#333e48;--red:#9e1b32}text{font:700 16px Arial;fill:var(--ink)}
    .node{fill:#ffffff;stroke:var(--red);stroke-width:2px}
    </style><body><svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset1" width="480" height="160" viewBox="0 0 480 160">
    <title>Capture test</title><desc>Styled node and label.</desc>
    <rect class="node" x="20" y="20" width="220" height="32"/><text id="label" x="30" y="41">Portable composition</text>
    </svg></body></html>''', encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "skills/d3/scripts/render_d3_svg.py"), str(html), "--output", str(svg), "--wait-ms", "0"], check=True)
    subprocess.run([sys.executable, str(ROOT / "skills/d3/scripts/check_palette_contract.py"), str(svg), "--colorset", "colorset1"], check=True, capture_output=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        page = browser.new_page()
        records = []
        for path in (html, svg):
            page.goto(path.as_uri())
            records.append(page.evaluate('''() => {const t=document.querySelector('#label'),r=document.querySelector('.node'),s=getComputedStyle(t),rs=getComputedStyle(r);return {family:s.fontFamily,size:s.fontSize,weight:s.fontWeight,fill:s.fill,boxFill:rs.fill,stroke:rs.stroke,strokeWidth:rs.strokeWidth,textWidth:t.getBBox().width}}'''))
        assert records[0] == records[1], records
        browser.close()
    print("Portable SVG retains exact computed font, color, stroke, and label width.")
