#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Compare all preserved family repetitions at the same display width."""

import argparse
import html
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[3];args.output.mkdir(parents=True,exist_ok=True)
    records=[];sections=[]
    for repetition in [1,2,3]:
        cards=[]
        for version in [18,19]:
            run=root/f'evaluations/runs/usefulcharts-v{version}-family-20260912-{repetition}'
            strict=json.loads((run/'evaluation-result.json').read_text())['passed']
            image=run/'workspace/result/poster.png'
            cards.append(f'<figure><figcaption>v{version} · repetition {repetition} · strict {"pass" if strict else "fail"}</figcaption><a href="{image.as_uri()}"><img src="{image.as_uri()}" alt="Family poster v{version}, repetition {repetition}"></a></figure>')
            records.append(dict(version=version,repetition=repetition,strict_pass=strict,image=str(image.relative_to(root))))
        sections.append(f'<section id="repetition-{repetition}"><h2>Repetition {repetition}</h2><div class="pair">'+''.join(cards)+'</div></section>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>Family composition revision</title>
<style>body{margin:0;background:#f6f4ed;color:#252820;font:16px/1.5 Arial,sans-serif;padding:24px}h1{font-size:30px}p{max-width:900px}.pair{display:grid;grid-template-columns:640px 640px;gap:24px}figure{margin:0}figcaption{font-weight:bold;margin:12px 0}img{display:block;width:640px;height:auto}section{margin:32px 0;border-top:1px solid #bcb8a9}</style>
<h1>All family composition trials</h1><p>Left: initial v18. Right: revised v19. All pages use the same display width and retain their aspect ratio. Click a poster for its full-resolution image. Strict execution, fact preservation and visual quality are separate judgments. This comparison does not establish parity with UsefulCharts.</p>'''+''.join(sections)+'</html>'
    path=args.output/'index.html';path.write_text(page,encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch();tab=browser.new_page(viewport={'width':1352,'height':1100})
        tab.goto(path.resolve().as_uri());tab.evaluate('document.fonts.ready')
        tab.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
        for i in [1,2,3]:tab.locator(f'#repetition-{i}').screenshot(path=str(args.output/f'repetition-{i}.png'))
        browser.close()
    (args.output/'manifest.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',posters=len(records),comparison=str(path))))


if __name__=='__main__':main()
