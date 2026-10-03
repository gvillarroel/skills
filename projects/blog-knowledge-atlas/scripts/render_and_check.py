#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2", "pypdf>=5,<7"]
# ///
"""Render the actual PDFs and independently inspect source, text and routing."""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from atlas_core import ROOT, OUT, SOURCES, tag


def normal(text):
    return ' '.join(unicodedata.normalize('NFKC', str(text)).split())


def intersects(a, b, epsilon=.8):
    return a['x'] < b['x'] + b['w'] - epsilon and a['x'] + a['w'] > b['x'] + epsilon and a['y'] < b['y'] + b['h'] - epsilon and a['y'] + a['h'] > b['y'] + epsilon


def render(case, browser):
    out = OUT / case
    m = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
    w, h = m['canvas']
    svg = (out / 'poster.svg').read_text(encoding='utf-8')
    page = browser.new_page(viewport=dict(width=w, height=min(1500, h)))
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.set_content('<!doctype html><html><head><style>html,body{margin:0}body>svg{display:block}</style></head><body>' + svg + '</body></html>')
    page.evaluate('document.fonts.ready')
    b = page.evaluate('''() => {
      const svg=document.querySelector('body>svg');
      return {texts:[...svg.querySelectorAll('text')].map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height,owner:e.closest('[data-record-id]')?.dataset.recordId||null}}),
      dates:[...svg.querySelectorAll('[data-date-owner]')].map(e=>({owner:e.dataset.dateOwner,year:+e.dataset.year,x:+e.getAttribute('cx')})),
      records:[...svg.querySelectorAll('[data-record-id]')].map(e=>({id:e.dataset.recordId,text:[...e.querySelectorAll('text')].map(t=>t.textContent).join(' ')}))};
    }''')
    page.locator('body>svg').screenshot(path=str(out / 'poster.png'))
    page.set_viewport_size(dict(width=w, height=h))
    dx, dy, dw, dh = m['detail']
    page.screenshot(path=str(out / 'detail.png'), clip=dict(x=dx, y=dy, width=dw, height=dh))
    page.pdf(path=str(out / 'raw.pdf'), width=f'{w}px', height=f'{h}px', print_background=True, margin=dict(top='0', bottom='0', left='0', right='0'))
    page.add_style_tag(content='body>svg{width:1800px;height:auto}')
    page.set_viewport_size(dict(width=1800, height=1200))
    page.locator('body>svg').screenshot(path=str(out / 'preview.png'))
    page.close()
    issues = []
    for t in b['texts']:
        if t['x'] < 0 or t['y'] < 0 or t['x'] + t['w'] > w + 1 or t['y'] + t['h'] > h + 1:
            issues.append(dict(type='outside-canvas', text=t['text']))
    for i, a in enumerate(b['texts']):
        for bb in b['texts'][i + 1:]:
            if intersects(a, bb):
                issues.append(dict(type='text-text', texts=[a['text'], bb['text']]))
        for image in m['images']:
            if intersects(a, image):
                issues.append(dict(type='image-text', image=image['id'], text=a['text']))
    for route in m['routes']:
        for a, bb in zip(route['points'], route['points'][1:]):
            seg = dict(x=min(a[0], bb[0]) - .7, y=min(a[1], bb[1]) - .7, w=max(1.4, abs(a[0] - bb[0]) + 1.4), h=max(1.4, abs(a[1] - bb[1]) + 1.4))
            for t in b['texts']:
                if intersects(seg, t, .2):
                    issues.append(dict(type='route-text', route=route['id'], text=t['text']))
            for im in m['images']:
                if intersects(seg, im, .2):
                    issues.append(dict(type='route-image', route=route['id'], image=im['id']))
    observed = {r['id']: normal(r['text']) for r in b['records']}
    for r in m['records']:
        for field in ['title', 'detail']:
            if normal(r[field]) not in observed.get(r['id'], ''):
                issues.append(dict(type='missing-record-field', record=r['id'], field=field))
    if len(set(r['id'] for r in m['records'])) != len(m['records']):
        issues.append(dict(type='duplicate-record-id'))
    if case == '01-history':
        required = json.loads((OUT / 'data/milestones.json').read_text(encoding='utf-8'))
        dates = {r['owner']: r for r in b['dates']}
        if len(dates) != 60:
            issues.append(dict(type='date-count', actual=len(dates)))
        for n in required:
            seg = next(s for s in reversed(m['time_segments']) if s['start'] <= n['year'] <= s['end'])
            xx = seg['x'] + (n['year'] - seg['start']) / (seg['end'] - seg['start']) * seg['width']
            if n['id'] not in dates or dates[n['id']]['year'] != n['year'] or abs(dates[n['id']]['x'] - xx) > .01:
                issues.append(dict(type='wrong-date-x', record=n['id']))
            for text in [n['title'], n['note']]:
                if normal(text) not in observed.get(n['id'], ''):
                    issues.append(dict(type='milestone-source-loss', record=n['id']))
    # Create vector PDF links after rendering, preserving every source association.
    reader = PdfReader(out / 'raw.pdf')
    writer = PdfWriter()
    writer.append(reader)
    writer.add_metadata({'/Title': m['title'], '/Author': 'Blog knowledge atlas / source text by '+('Gerardo Villarroel' if case=='03-evaluation' else 'Guillermo Villarroel'), '/Subject': m['subtitle']})
    for r in m['records']:
        writer.add_uri(0, r['url'], RectangleObject([r['x'] * .75, (h - r['y'] - r['h']) * .75, (r['x'] + r['w']) * .75, (h - r['y']) * .75]), border=[0, 0, 0])
    with (out / 'poster.pdf').open('wb') as stream:
        writer.write(stream)
    final = PdfReader(out / 'poster.pdf')
    extracted = normal(final.pages[0].extract_text())
    missing_pdf = []
    for r in m['records']:
        for field in ['title', 'detail']:
            if normal(r[field]) not in extracted:
                missing_pdf.append(dict(record=r['id'], field=field))
    issues.extend(dict(type='pdf-text-loss', **v) for v in missing_pdf)
    annotations = [a.get_object().get('/A', {}).get('/URI') for a in final.pages[0].get('/Annots', [])]
    if len(annotations) != len(m['records']):
        issues.append(dict(type='pdf-link-count', actual=len(annotations)))
    subprocess.run(['pdftoppm', '-singlefile', '-scale-to', '1800', '-png', str(out / 'poster.pdf'), str(out / 'pdf-preview')], check=True, capture_output=True)
    report = dict(case=case, records=len(m['records']), illustrations=len(m['images']), dates=len(b['dates']), pdf_pages=len(final.pages), pdf_links=len(annotations), svg_sha256=hashlib.sha256((out/'poster.svg').read_bytes()).hexdigest(), pdf_sha256=hashlib.sha256((out / 'poster.pdf').read_bytes()).hexdigest(), errors=errors, issues=issues, technical_pass=not issues and not errors)
    (out / 'browser-measurements.json').write_text(json.dumps(b, indent=2) + '\n', encoding='utf-8')
    (out / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ['issues', 'svg_sha256', 'pdf_sha256']} | {'issue_count': len(issues), 'first_issues': issues[:16]}))
    return report


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        results = [render(case, browser) for case in sys.argv[1:] or ['01-history', '02-agent', '03-evaluation']]
        browser.close()
    retained=[json.loads((OUT/c/'checks.json').read_text()) for c in ['01-history','02-agent','03-evaluation'] if (OUT/c/'checks.json').exists()]
    (OUT / 'reviews/technical.json').write_text(json.dumps(retained, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
