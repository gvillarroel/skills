#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "pillow>=10.0.0"]
# ///
"""Verify real Mermaid CSS materialization and repeated-asset SVG composition."""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skill-root", type=Path, required=True)
    ap.add_argument("--artifacts", type=Path, required=True)
    args = ap.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.skill_root.resolve() / "scripts"))
    from audit_diagram import launch_browser
    from compose_diagram import compose, parse_svg
    artifacts = args.artifacts.resolve()
    sources = [artifacts / "svgs" / f"review-sequence.{kind}.svg" for kind in ("static", "prepared")]
    imgs = artifacts / "images"; imgs.mkdir(parents=True, exist_ok=True)
    source_root, vb, _ = parse_svg(sources[0], allow_style=True)
    with sync_playwright() as pw:
        browser = launch_browser(pw)
        page = browser.new_page(viewport={"width": 1000, "height": 700}, java_script_enabled=False)
        geometries = []
        for kind, source in zip(("static", "prepared"), sources):
            page.set_content('<html><body style="margin:0">' + source.read_text(encoding="utf-8") + '</body></html>')
            page.evaluate("([w,h])=>{const s=document.querySelector('svg');s.style.width=w+'px';s.style.height=h+'px';s.style.maxWidth='none';s.style.display='block'}", [vb[2], vb[3]])
            page.evaluate("document.fonts.ready")
            geometries.append(page.evaluate("() => [...document.querySelectorAll('text')].map(e=>{const b=e.getBoundingClientRect();return {text:e.textContent,box:[b.x,b.y,b.width,b.height],fill:getComputedStyle(e).fill}})"))
            page.locator('svg').first.screenshot(path=str(imgs / f'mermaid-{kind}.png'))
        browser.close()
    require_match = geometries[0] == geometries[1]
    a, b = [Image.open(imgs / f'mermaid-{kind}.png').convert('RGB') for kind in ('static', 'prepared')]
    pixel_equal = a.size == b.size and ImageChops.difference(a, b).getbbox() is None
    spec = {"version": 1, "title": "Verified import of a real Mermaid sequence",
        "thesis": "Two repeated source assets preserve style, accessible identity, and local SVG definitions.",
        "canvas": {"width": 2 * vb[2] + 120, "height": vb[3] + 150,
                   "displayWidth": 2 * vb[2] + 120, "minTextPx": 14, "margin": 20,
                   "gap": 40, "titleHeight": 55, "footerHeight": 20},
        "grid": {"columns": [1, 1], "rows": [1]}, "concepts": [{"id": "review", "label": "Review"}], "panels": []}
    for i in range(2):
        spec["panels"].append({"id": f"review-{i+1}", "title": f"Copy {i+1}", "question": "What happens before applying a change?",
            "claim": "Review precedes source modification.", "family": "sequence", "reason": "Ordered exchanges among three roles.",
            "alternative": "A matrix cannot encode message order.", "concepts": ["review"],
            "source": "../svgs/review-sequence.prepared.svg", "span": {"row": 1, "column": i+1, "rows": 1, "columns": 1}, "ports": {}})
    spec_path = artifacts / 'manifests' / 'mermaid-import.json'
    spec_path.write_text(json.dumps(spec, indent=2) + '\n', encoding='utf-8')
    svg, report = compose(spec, spec_path)
    output = artifacts / 'svgs' / 'mermaid-import.svg'
    output.write_text(svg, encoding='utf-8')
    parse_svg(output)
    result = {"ok": require_match and pixel_equal, "textGeometryAndFillEqual": require_match,
              "pixelsEqual": pixel_equal, "sourceViewBox": vb, "textCount": len(geometries[0]),
              "output": str(output), "repeatedPanels": len(report['panels'])}
    (artifacts / 'reviews' / 'mermaid-import.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
