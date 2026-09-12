#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Retain source bytes and compare scientific illustrations inside white panels."""

import argparse
import hashlib
import html
import json
import struct
import shutil
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright


SOURCES=[('microscope-psf','Microscope (PSF).png'),('theodolite-psf','Theodolite (PSF).png'),
         ('cogwheel-psf','Cogwheel 1 (PSF).png'),('compass-card-psf','Compass Card (PSF).png'),
         ('printing-press-bookman','Bookman Ornament, Printing Press 12044.svg')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--register',action='store_true',help='Copy only the four inspected, accepted illustrations into the canonical bundle.')
    args=parser.parse_args()
    folder=Path(__file__).resolve().parent.parent/'artifacts/images/panel-illustrations'
    folder.mkdir(parents=True,exist_ok=True);records=[];cards=[]
    for art_id,title in SOURCES:
        canonical=title.replace(' ','_');md5=hashlib.md5(canonical.encode()).hexdigest()
        url=f'https://upload.wikimedia.org/wikipedia/commons/{md5[0]}/{md5[:2]}/'+urllib.parse.quote(canonical)
        path=folder/(art_id+Path(title).suffix)
        if not path.exists():
            print(f'Downloading {title}',flush=True)
            time.sleep(3)
            request=urllib.request.Request(url,headers={'User-Agent':'EducationalPosterResearch/1.0 (local source review)'})
            for attempt in range(2):
                try:
                    with urllib.request.urlopen(request,timeout=45) as response:path.write_bytes(response.read())
                    break
                except urllib.error.HTTPError as error:
                    if error.code!=429 or attempt:raise
                    delay=max(30,min(60,int(error.headers.get('Retry-After','45'))))
                    print(f'Source rate limit; waiting {delay} seconds before one retry.',flush=True)
                    time.sleep(delay)
        content=path.read_bytes()
        if path.suffix=='.png':width,height=struct.unpack('>II',content[16:24])
        else:
            svg=ET.fromstring(content);view=list(map(float,svg.attrib['viewBox'].split()));width,height=view[2:]
        item=dict(id=art_id,file=path.name,title=title,creator='American Type Founders Company' if art_id.endswith('bookman') else 'Pearson Scott Foresman',
            source='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(canonical),image_url=url,
            width=width,height=height,mime_type='image/svg+xml' if path.suffix=='.svg' else 'image/png',
            rights='Public domain, published in the United States in 1923.' if art_id.endswith('bookman') else 'Public-domain dedication by Pearson Scott Foresman; Wikimedia VRT ticket 2010061110041093.',
            retrieved='2026-09-12',sha256=hashlib.sha256(content).hexdigest(),bytes=len(content),modified=False)
        records.append(item)
        cards.append(f'<article><h2>{html.escape(title)}</h2><div class="large"><img src="{path.as_uri()}"></div><div class="sample"><span><img src="{path.as_uri()}"></span><b>Institute of<br>Scientific Study</b></div></article>')
    page_path=folder/'index.html'
    page_path.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Source artwork on diagram panels</title><style>body{font:18px Arial;background:#edead8;margin:28px}main{display:grid;grid-template-columns:repeat(5,1fr);gap:20px}h2{font-size:17px;min-height:45px}.large{height:240px;background:white;display:flex;align-items:center;justify-content:center}.large img{max-width:100%;max-height:240px}.sample{display:flex;margin-top:24px;background:#77bddd;align-items:center;gap:9px;font-size:13px}.sample span{width:50px;height:50px;background:white;display:flex;align-items:center;justify-content:center}.sample img{max-width:46px;max-height:46px}</style><h1>Original source images at source-review and diagram-panel sizes</h1><p>Unmodified bytes. White panels are intentional; this does not imply transparent image backgrounds.</p><main>'''+''.join(cards)+'</main></html>',encoding='utf-8')
    (folder/'sources.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    if args.register:
        target=Path(__file__).resolve().parents[3]/'skills/usefulcharts-style/assets/illustrations'
        manifest_path=target/'provenance.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        choices={
            'theodolite-psf':('Surveyor using a theodolite',1268081031,'Undated explanatory drawing; extracted file uploaded on 2020-03-27.'),
            'cogwheel-psf':('Two meshing cogwheels',1115939209,'Undated explanatory drawing; extracted file uploaded on 2020-11-28.'),
            'compass-card-psf':('Compass card with directional markings',None,'Undated explanatory drawing; file uploaded on 2007-09-04.'),
            'printing-press-bookman':('Bookman printing press ornament',1169853785,'Published in the 1923 American Type Founders specimen book.')}
        for record in records:
            if record['id'] not in choices:continue
            item=dict(record);title,revision,note=choices[item['id']]
            item.update(title=title,source_url=item.pop('source'),date_note=note+' Contextual illustration, not an institutional logo or evidence of a fictional event.',
                background='Placed on an intentional white image panel; source bytes are unchanged. The PNG sources retain their white field.')
            if revision:item['source_revision']=revision
            assert hashlib.sha256((folder/item['file']).read_bytes()).hexdigest()==item['sha256']
            shutil.copyfile(folder/item['file'],target/item['file'])
            manifest['items']=[old for old in manifest['items'] if old['id']!=item['id']]+[item]
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={'width':1450,'height':700})
        page.goto(page_path.as_uri());page.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        page.screenshot(path=str(folder/'review.png'),full_page=True);browser.close()
    print(json.dumps(dict(status='pass',sources=len(records),folder=str(folder),bytes=sum(r['bytes'] for r in records))))


if __name__=='__main__':main()
