#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Compose labeled review sheets around unchanged, hash-bound comparison images."""
from pathlib import Path
import base64
import hashlib
import json
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT / 'artifacts/exploration-input-b'
    out = ROOT / 'artifacts/exploration-input-c'
    out.mkdir(parents=True, exist_ok=False)
    (out / 'raw').mkdir()
    manifest = dict(subject='bsd', candidates=[], reference={}, source_inventory='bsd-source.json', files={},
                    normalization='Unchanged cohort-B chart images, composed with a neutral identifier outside the chart. The whole images share a width; detail crops retain the previous protocol.', raw_source_hashes={})
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport=dict(width=1400, height=1100), device_scale_factor=1)
        for ident, old in [('CEDAR', 'B'), ('MAPLE', 'A'), ('REFERENCE', 'reference')]:
            entry = dict(candidate=ident) if ident != 'REFERENCE' else dict(source_url='https://usefulcharts.com/products/european-royal-family-tree')
            for kind in ['whole', 'detail']:
                raw = source / f'bsd-{old}-{kind}.png'
                name = f'bsd-{ident.lower()}-{kind}.png'
                shutil.copy2(raw, out / 'raw' / raw.name)
                manifest['raw_source_hashes']['raw/' + raw.name] = sha(raw)
                data = base64.b64encode(raw.read_bytes()).decode()
                page.set_content(f'<style>body{{margin:0;background:#eee;font:26px Arial}}header{{padding:18px 26px;box-sizing:border-box;height:70px;background:#eee;color:#111;font-weight:700}}img{{display:block;width:1400px;height:auto}}</style><header>{ident} / {kind.upper()} / input/{name}</header><img src="data:image/png;base64,{data}">')
                page.locator('img').evaluate('(e)=>e.decode()')
                page.screenshot(path=str(out / name), full_page=True)
                manifest['files'][name] = sha(out / name)
                entry[kind] = name
            if ident == 'REFERENCE':
                manifest['reference'] = entry
            else:
                manifest['candidates'].append(entry)
        browser.close()
    shutil.copy2(source / 'bsd-source.json', out / 'bsd-source.json')
    manifest['files']['bsd-source.json'] = sha(out / 'bsd-source.json')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(files=len(manifest['files']), raw_files=len(manifest['raw_source_hashes']))))


if __name__ == '__main__':
    main()
