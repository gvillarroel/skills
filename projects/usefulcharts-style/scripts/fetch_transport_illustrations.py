#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Retain and visually sample unchanged public-domain transport drawings."""

import hashlib
import html
import json
import urllib.parse
import urllib.request
import urllib.error
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright

FILES={
    'square-rigged-ship':'Square-rigged (PSF).svg',
    'suspension-bridge':'Suspension bridge (PSF).svg',
    'stagecoach':'Stagecoach (PSF).svg',
}


def main():
    folder=Path(__file__).resolve().parent.parent/'artifacts/images/transport-illustrations'
    folder.mkdir(parents=True,exist_ok=True);records=[];cards=[]
    for name,title in FILES.items():
        canonical=title.replace(' ','_');digest=hashlib.md5(canonical.encode()).hexdigest()
        url=f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/'+urllib.parse.quote(canonical)
        path=folder/f'{name}.svg'
        if not path.exists():
            request=urllib.request.Request(url,headers={'User-Agent':'EducationalPosterResearch/1.0'})
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(request,timeout=30) as response:content=response.read()
                    break
                except urllib.error.HTTPError as error:
                    if error.code!=429 or attempt==2:raise
                    time.sleep(10*(attempt+1))
            path.write_bytes(content)
            time.sleep(3)
        content=path.read_bytes();svg=ET.fromstring(content)
        record=dict(id=name,file=path.name,source_title=title,image_url=url,source_url='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(canonical),
            width=svg.get('width'),height=svg.get('height'),viewBox=svg.get('viewBox'),sha256=hashlib.sha256(content).hexdigest(),bytes=len(content),modified=False)
        records.append(record)
        cards.append(f'<section><h2>{html.escape(title)}</h2><div class="large"><img src="{path.name}"></div><div class="small"><img src="{path.name}"></div></section>')
    page=folder/'index.html'
    page.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Transport illustration inspection</title><style>body{background:#EDEAD8;color:#242720;font:16px Arial;margin:24px}main{display:grid;grid-template-columns:repeat(3,1fr);gap:30px}h2{font-size:19px}.large{height:350px;display:flex;align-items:center;border:1px solid #aaa}.large img{max-width:100%;max-height:330px}.small{margin-top:35px;height:180px}.small img{width:140px;height:120px;object-fit:contain}img{display:block}</style><h1>Unmodified drawings on poster paper</h1><main>'+''.join(cards)+'</main>',encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch();tab=browser.new_page(viewport={'width':1500,'height':800});tab.goto(page.resolve().as_uri())
        tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        tab.screenshot(path=str(folder/'contact.png'),full_page=True);browser.close()
    (folder/'downloads.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(records))


if __name__=='__main__':main()
