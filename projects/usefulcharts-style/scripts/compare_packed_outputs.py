#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Display untouched medium-history forward outputs at equal widths."""

import html
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    root=Path(__file__).resolve().parents[3]
    output=root/'projects/usefulcharts-style/artifacts/reviews/packed-forward-comparison'
    output.mkdir(parents=True,exist_ok=True)
    choices=[('v14: rejected composition','usefulcharts-v14-libraries-20260912-2')]+[(f'v15: fresh trial {i}',f'usefulcharts-v15-libraries-20260912-{i}') for i in range(1,4)]
    figures=[];records=[]
    for label,run_id in choices:
        folder=root/'evaluations/runs'/run_id;image=folder/'workspace/result/poster.png'
        audit=json.loads((folder/'workspace/result/browser.json').read_text(encoding='utf-8'))
        manifest=json.loads((folder/'run-manifest.json').read_text(encoding='utf-8'))
        figures.append(f'<figure><figcaption><strong>{html.escape(label)}</strong><br>{audit["canvas"][0]:g} × {audit["canvas"][1]:g} · 50 records · 71 relationships</figcaption><a href="{image.as_uri()}"><img src="{image.as_uri()}" alt="{html.escape(label)}"></a></figure>')
        records.append(dict(id=run_id,payload=manifest['skill'],image=str(image),canvas=audit['canvas']))
    page_path=output/'index.html'
    page_path.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Measured institutional-story comparison</title><style>*{box-sizing:border-box}body{font:16px/1.5 Arial;margin:24px;background:#f3f1ea;color:#242321}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px}figure{margin:0}figcaption{margin:12px 0;min-height:58px}img{width:100%;height:auto;display:block}@media(max-width:1000px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}</style><h1>One source history, four untouched forward outputs</h1><p>All images use the same display width; aspect ratios are retained. Click to inspect the original PNG. The v14 output passes source/geometry checks but fails visual composition. The three v15 outputs improve readable type and hierarchy. Long lower routes and tall compositions remain visible limitations; this is an unblinded comparison, not proof of parity with UsefulCharts.</p><main class="grid">'''+''.join(figures)+'</main></html>',encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={'width':2400,'height':1600})
        page.goto(page_path.as_uri());page.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        page.screenshot(path=str(output/'comparison.png'),full_page=True);browser.close()
    (output/'comparison-manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',outputs=len(records),comparison=str(page_path))))


if __name__=='__main__':main()
