#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Capture equal-native-scale note groups without changing the source artwork."""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3]
folder=root/'projects/usefulcharts-style/artifacts/reviews/note-hierarchy-final-comparison'
cards=[]
for title,year,x,width,height in [('Trade and roads',1100,500,620,490),('Navigation and instruments',1480,875,660,720)]:
    for version in ('before','after'):
        data=json.loads((folder/(version+'.json')).read_text())
        y=190+(year-data['time']['start'])/(data['time']['end']-data['time']['start'])*(data['height']-302)
        cards.append(f'<section><h2>{title} · {version}</h2><div class="crop" style="width:{width}px;height:{height}px"><img src="{version}.svg" style="width:{data["width"]}px;left:{-x}px;top:{-y}px"></div></section>')
page=folder/'detail.html'
page.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Note hierarchy details</title><style>body{background:#e9e5d6;color:#292a23;font:18px Arial;margin:24px}main{display:grid;grid-template-columns:repeat(2,680px);gap:24px}.crop{position:relative;overflow:hidden;border:1px solid #777}.crop img{position:absolute;height:auto;max-width:none}h2{font-size:20px}</style><h1>Context groups at the same native scale</h1><main>'+''.join(cards)+'</main>',encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch();tab=browser.new_page(viewport={'width':1470,'height':1000})
    tab.goto(page.as_uri());tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
    tab.screenshot(path=str(folder/'detail.png'),full_page=True);browser.close()
print('Captured complete trade and navigation groups at matching native scales.')
