#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inspect distinct institutional emblems beside their former aliased drawings."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/usefulcharts-style/scripts'))
from editorial_art import symbol


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    previous = subprocess.check_output(['git', 'show', '3b524e6320914e52deb137347c8a02c8cc9306a5:skills/usefulcharts-style/scripts/editorial_art.py'], cwd=ROOT)
    path = args.output / 'baseline_art.py'
    path.write_bytes(previous)
    spec = importlib.util.spec_from_file_location('baseline_art', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    kinds = ['star', 'sun', 'compass', 'astrolabe', 'orbit', 'globe', 'wheel', 'gear', 'lens', 'prism', 'anchor', 'ship', 'tower', 'observatory']
    def view(mark, size):
        return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" aria-hidden="true">{mark}</svg>'
    rows = []
    for kind in kinds:
        before, after = module.symbol(kind, '#77BDDD'), symbol(kind, '#77BDDD')
        rows.append(f'<tr data-emblem-id="{kind}"><th>{kind}</th><td>{view(before, 88)}</td><td>{view(after, 88)}</td><td>{view(after,29)} {view(after,37)} {view(after,50)}</td></tr>')
    page = args.output / 'comparison.html'
    page.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Semantic emblem comparison</title>
<style>body{background:#eeeada;color:#25251f;font:16px/1.45 Arial;margin:24px}h1{font-size:26px}p{max-width:900px}table{border-collapse:collapse;background:#fffef4}td,th{border-bottom:1px solid #d6d1bf;padding:8px 20px;text-align:left}svg{vertical-align:middle}th:first-child{width:160px}thead th{background:#8c332b;color:white}td:last-child{min-width:220px}svg{overflow:visible}</style>
<h1>Distinct subjects need distinct silhouettes</h1><p>Original vector devices for educational posters. Former aliases are compared with revised marks, including the actual small 29-, 37- and 50-unit footprints. These are illustrative symbols, not historical institutional logos.</p><table><thead><tr><th>Subject</th><th>Previous</th><th>Revised</th><th>Small print sizes</th></tr></thead><tbody>'''+''.join(rows)+'</tbody></table></html>', encoding='utf-8')
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        tab = browser.new_page(viewport={'width': 1060, 'height': 900})
        tab.goto(page.resolve().as_uri())
        tab.evaluate('document.fonts.ready')
        tab.screenshot(path=str(args.output / 'comparison.png'), full_page=True)
        assert tab.locator('[data-emblem-id]').count() == len(kinds)
        browser.close()
    result = dict(count=len(kinds), previous_unique=len({module.symbol(kind, '#77BDDD') for kind in kinds}),
                  revised_unique=len({symbol(kind, '#77BDDD') for kind in kinds}),
                  screenshot_sha256=hashlib.sha256((args.output / 'comparison.png').read_bytes()).hexdigest(),
                  scope='Direct review required; distinct serialized marks alone do not prove good visual identity.')
    (args.output / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
