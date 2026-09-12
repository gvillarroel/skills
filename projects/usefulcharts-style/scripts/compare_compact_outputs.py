#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Show preserved independent forward outputs at equal display widths."""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    root=Path(__file__).resolve().parents[3];runs=root/'evaluations/runs'
    output=root/'projects/usefulcharts-style/artifacts/reviews/compact-forward-comparison'
    output.mkdir(parents=True,exist_ok=True)
    sections=[];records=[]
    for case,title,sub,png,viewer in [('cohorts','Partnered genealogy','result','poster.png','poster.html'),
                                     ('transport','Parallel transport history','museum','preview.png','viewer.html')]:
        figures=[]
        for version,label in [('v11','Previous skill: first forward run'),('v13','Revised skill: first forward run')]:
            folder=runs/f'usefulcharts-{case}-{version}-20260911-gpt55-1'/'workspace'/sub
            image=folder/png;link=folder/viewer
            if not image.is_file() or not link.is_file():raise FileNotFoundError(folder)
            figures.append(f'<figure><figcaption>{label}</figcaption><a href="{link.as_uri()}"><img src="{image.as_uri()}" alt="{title}: {version}"></a></figure>')
            records.append(dict(case=case,version=version,preview=str(image),viewer=str(link)))
        sections.append(f'<section id="{case}"><h2>{title}</h2><div class="pair">'+''.join(figures)+'</div></section>')
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Compact poster forward comparison</title><style>*{box-sizing:border-box}body{margin:32px auto;padding:0 24px;max-width:1480px;background:#f5f4ef;color:#242720;font:17px/1.5 Arial}h1{font-size:42px;line-height:1.1}p{max-width:1000px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}figure{margin:0}figcaption{font-weight:bold;margin:10px 0}img{width:100%;display:block}section{margin:48px 0}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>What changed when the skill was used from scratch?</h1><p>These are preserved GPT-5.5 forward outputs from isolated runtime-only workspaces. No author edits were applied to either output. Both columns have the same display width; the native page proportions are retained. Click an image to inspect the editable poster.</p><p>The genealogy prompt was clarified after the first run: its original transitive family rules overlapped after a marriage. The revised prompt explicitly names every category member. Its composition comparison is still informative, but this is not a controlled test of category inference.</p><p>All data is fictional. This comparison demonstrates compact composition and readable type; it does not establish indistinguishability from UsefulCharts.</p>'''+''.join(sections)+'</html>'
    page_path=output/'index.html';page_path.write_text(document,encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={'width':1500,'height':1200})
        page.goto(page_path.as_uri());page.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        for case in ('cohorts','transport'):page.locator(f'#{case}').screenshot(path=str(output/f'{case}.png'))
        browser.close()
    (output/'manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',comparison=str(page_path),cases=2)))


if __name__=='__main__':main()
