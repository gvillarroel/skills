#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Capture the changed illustration groups at identical native scales."""

from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3]
folder=root/'projects/usefulcharts-style/artifacts/reviews/contextual-art-final-comparison'
page=folder/'detail.html'
cards=[]
for label,file in [('Previous composition','before.svg'),('Revised composition','after.svg')]:
    cards.append(f'<section><h2>{label}</h2><div class="crop"><img src="{file}"></div></section>')
page.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Contextual illustration comparison</title><style>body{background:#e9e5d6;color:#292a23;font:18px Arial;margin:24px}main{display:flex;gap:24px}.crop{position:relative;width:700px;height:550px;overflow:hidden;border:1px solid #777}.crop img{position:absolute;width:1680px;height:2400px;max-width:none;left:-490px;top:-320px}h2{font-size:20px}</style><h1>Illustration groups at the same native scale</h1><main>'+''.join(cards)+'</main>',encoding='utf-8')
with sync_playwright() as p:
    browser=p.chromium.launch();tab=browser.new_page(viewport={'width':1500,'height':700})
    tab.goto(page.as_uri());tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
    tab.screenshot(path=str(folder/'detail.png'),full_page=True);browser.close()
print('Captured unchanged-size before and after details.')
