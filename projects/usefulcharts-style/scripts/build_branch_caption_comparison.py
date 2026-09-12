#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Build a private, equal-width image comparison for the caption revision."""

import hashlib
import html
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT/'projects/usefulcharts-style/artifacts/reviews/full-branches-v33'
DEST = ART/'comparison'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def panel(title, path, note):
    source = Path(os.path.relpath(path, DEST)).as_posix()
    return f'<article><h3>{html.escape(title)}</h3><p>{html.escape(note)}</p><div class="paper"><a href="{source}"><img src="{source}" alt="{html.escape(title)}"></a></div></article>'


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    images = ROOT/'projects/usefulcharts-style/artifacts/images'
    pairs = [
        ('Local family titles', [
            ('Before: complete records, no local titles', ART/'publishing-without-captions/poster.png',
             '70 institutions and 97 typed relationships. The frozen v32 runtime cannot place the same five requested captions; this completed control omits only those captions.'),
            ('After: the five requested family titles', ART/'captioned-publishing/poster.png',
             'The same 70 institutions and 97 relationships, with all five anchored titles. The original fields, name sizes and note sizes are preserved. This is a development case.')]),
        ('Original reference and current development output', [
            ('UsefulCharts reference', images/'reference-denominations.png',
             'Christian Denominations Family Tree, UsefulCharts. Private visual review only; different source data and record count. Equal display width is not an experimental control.'),
            ('Skill output', ART/'captioned-publishing/poster.png',
             'Fictional publishing history. Local family titles improve hierarchy; the long dotted influences and persistent column rhythm still weaken the comparison.')]),
        ('Full mural: rejected automatic alternatives', [
            ('Current published composition', ART/'gallery/atlas-of-inquiry.png',
             '141 institutions and 171 typed relationships. Complete contextual insets. The canonical gallery remains unchanged.'),
            ('Rejected: founded-year order', ART/'founded-reserved/poster.png',
             '141 institutions and 171 relationships; 112 crossings and one unrelated shared run. Context insets are omitted in this probe. The long vertical stretches weaken the page.'),
            ('Rejected: causal order', ART/'causal-reserved/poster.png',
             '141 institutions and 171 relationships; 114 crossings and one unrelated shared run. Context insets are omitted in this probe. The wide fan and long influences weaken the page.')]),
    ]
    sections = ''.join('<section><h2>'+html.escape(title)+'</h2><div class="grid">'+''.join(panel(*item) for item in items)+'</div></section>' for title,items in pairs)
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Branch captions: evidence and rejected alternatives</title><style>
    :root{font:16px/1.5 system-ui,sans-serif;color:#202629;background:#eceae5}body{margin:0}header,main{max-width:1680px;margin:auto;padding:24px 32px}header{padding-bottom:0}h1{font-size:30px;line-height:1.15;max-width:900px;margin:0 0 12px}header p{max-width:1000px;color:#535b5d}.bar{position:sticky;top:0;background:#eceae5ed;padding:12px 0;z-index:2;border-bottom:1px solid #bbb}button{font:inherit;border:1px solid #879397;border-radius:5px;background:white;padding:6px 14px;cursor:pointer}button[aria-pressed="true"]{background:#243d42;color:white}section{margin:25px 0 50px}h2{font-size:22px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px;align-items:start}article{min-width:0;background:white;border:1px solid #d0d3d1;padding:16px;border-radius:7px}h3{font-size:18px;margin:0 0 5px}article p{min-height:75px;margin:0 0 16px;font-size:14px;color:#565e60}.paper{overflow:auto;max-height:1600px;background:white;border:1px solid #e1e3df}.paper img{display:block;width:100%;height:auto}body.detail .paper img{width:1600px;max-width:none}.scope{background:#e1e7e7;padding:10px 14px;border-left:4px solid #33575e;font-size:14px}.ref{font-size:14px}a{color:#225765}footer{margin-top:40px;color:#566367;font-size:14px}@media(max-width:760px){header,main{padding:20px 14px}.grid{grid-template-columns:1fr}article p{min-height:0}h1{font-size:25px}}
    </style></head><body><header><h1>Branch captions: evidence and rejected alternatives</h1><p>A private review of the UsefulCharts-inspired skill. The illustrated output, editable source and independent audit are separate evidence requirements. Clean geometry does not establish equivalent composition.</p><p class="scope">Decision: retain the caption-aware composer and consistent poster export. Reject both complete mural reflows. Keep overall aesthetic parity unproven.</p><p class="ref">Reference: <a href="https://usefulcharts.com/products/christian-denominations-family-tree">Christian Denominations Family Tree — UsefulCharts</a>. Reference imagery is not part of the published skill or gallery.</p></header><main><div class="bar"><button id="fit" aria-pressed="true">Equal panel width</button> <button id="detail" aria-pressed="false">Equal 1600 px image width</button> <span>Click an image to open its full resolution.</span></div>''' + sections + '''<footer>2026-09-12 · Disclosed development evidence. These comparisons do not constitute a blind source-attribution test.</footer></main><script>for(const id of ['fit','detail'])document.getElementById(id).onclick=()=>{document.body.classList.toggle('detail',id==='detail');for(const key of ['fit','detail'])document.getElementById(key).setAttribute('aria-pressed',String(key===id))};</script></body></html>'''
    (DEST/'index.html').write_text(page, encoding='utf-8')
    records = [dict(title=title, images=[dict(title=item[0], path=str(item[1].relative_to(ROOT)), sha256=sha(item[1]), note=item[2]) for item in items]) for title,items in pairs]
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        tab = browser.new_page(viewport=dict(width=1500,height=1100))
        errors = [];tab.on('pageerror',lambda error:errors.append(str(error)))
        tab.goto((DEST/'index.html').as_uri());tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        tab.screenshot(path=str(DEST/'overview.png'),full_page=True)
        tab.locator('#detail').click()
        widths = tab.locator('.paper img').evaluate_all('(images)=>images.map(i=>i.getBoundingClientRect().width)')
        assert all(width == 1600 for width in widths), widths
        tab.locator('#fit').click();tab.set_viewport_size(dict(width=390,height=900))
        assert not tab.evaluate('document.documentElement.scrollWidth > innerWidth+1')
        assert not errors, errors
        browser.close()
    report=dict(status='pass', scope='Private visual review; no blind equivalence claim.', groups=records, controls=dict(image_count=len(widths),detail_width=1600,mobile_overflow=False,page_errors=errors))
    (DEST/'comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',images=len(widths),path=str(DEST/'index.html'))))


if __name__ == '__main__':
    main()
