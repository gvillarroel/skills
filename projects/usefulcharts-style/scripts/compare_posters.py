#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Build local-only reference/before/after evidence without publishing reference art."""

import argparse
import html
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,required=True)
    parser.add_argument('--before-revision',required=True)
    parser.add_argument('--artifacts',type=Path,required=True)
    parser.add_argument('--after-prefix',default='final')
    parser.add_argument('--comparison-name',default='comparison')
    parser.add_argument('--before-label',default='Rejected first version')
    args=parser.parse_args();root=args.repository.resolve();artifacts=args.artifacts.resolve()
    folder=artifacts/'reviews'/args.comparison_name;folder.mkdir(parents=True,exist_ok=True)
    gallery=root/'skills/usefulcharts-style/assets/examples/usefulcharts-style'
    samples=[('aurelian-families','royal','Genealogy'),('atlas-of-inquiry','denominations','Institutional lineage'),('five-regional-histories','history','Parallel history')]
    rows=[];records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={'width':1800,'height':2700},device_scale_factor=1)
        for name,ref,title in samples:
            before=folder/f'{name}-before.svg'
            path=f'skills/usefulcharts-style/assets/examples/usefulcharts-style/{name}.svg'
            before.write_bytes(subprocess.check_output(['git','show',f'{args.before_revision}:{path}'],cwd=root))
            page.goto(before.as_uri());page.evaluate('document.fonts.ready')
            before_png=folder/f'{name}-before.png';page.locator('svg').first.screenshot(path=str(before_png))
            reference=artifacts/f'images/reference-{ref}.png';after=artifacts/f'images/{args.after_prefix}-{name}.png'
            figures=''.join(f'<figure><figcaption>{html.escape(label)}</figcaption><a href="{file.as_uri()}"><img src="{file.as_uri()}" alt="{html.escape(title)}: {html.escape(label)}"></a></figure>' for label,file in [('Official reference',reference),(args.before_label,before_png),('Revised skill example',after)])
            rows.append(f'<section id="{name}"><h2>{title}</h2><div class="triptych">{figures}</div></section>')
            records.append(dict(id=name,reference=str(reference),before_revision=args.before_revision,before=str(before_png),after=str(after)))
        document='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Poster comparison evidence</title><style>*{box-sizing:border-box}body{font:16px/1.5 Arial;margin:24px;background:#f5f4f0;color:#222}h1{font-size:32px}.triptych{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}figure{margin:0}figcaption{font-size:20px;font-weight:bold;margin:10px 0}img{width:100%;height:auto;display:block}section{margin:40px 0}a{color:inherit}</style><h1>UsefulCharts reference / previous revision / current candidate</h1><p>Local critique evidence. Reference previews belong to UsefulCharts and are not redistributed with the public gallery. All three images use the same display width. Aspect-ratio differences are retained. Click any image for its full resolution. This is an unblinded author review, not an indistinguishability experiment.</p>'''+''.join(rows)+'</html>'
        report=folder/'index.html';report.write_text(document,encoding='utf-8')
        page.set_viewport_size({'width':1800,'height':1200});page.goto(report.as_uri())
        page.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        for name,_,_ in samples:page.locator(f'#{name}').screenshot(path=str(folder/f'{name}-comparison.png'))
        browser.close()
    (folder/'comparison-manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'pass','comparison':str(report),'examples':len(records)}))


if __name__=='__main__':main()
