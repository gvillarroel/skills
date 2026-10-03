#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Freeze neutral image pairs and original reference views for isolated critique."""
import base64
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright
from artwork import ROOT,REPO

def main():
    name=sys.argv[1] if len(sys.argv)>1 else 'exploration-input';out=ROOT/'artifacts'/name;out.mkdir(parents=True,exist_ok=False);subjects=[]
    with sync_playwright() as p:
        b=p.chromium.launch();page=b.new_page(viewport=dict(width=1200,height=1050))
        for case,order,refname,url in [('instruments',[3,2],'denominations','https://usefulcharts.com/products/christian-denominations-family-tree'),('bsd',[2,3],'royal','https://usefulcharts.com/products/european-royal-family-tree')]:
            if name.endswith('-b'):order=list(reversed(order))
            candidates=[]
            for letter,revision in zip('AB',order):
                path=ROOT/f'artifacts/revision-{revision}'/case;whole=f'{case}-{letter}-whole.png';detail=f'{case}-{letter}-detail.png';shutil.copy2(path/'preview.png',out/whole)
                root=ET.parse(path/'poster.svg').getroot();w,h=map(float,[root.get('width'),root.get('height')]);root.set('viewBox',f'{w*.04} {h*.20} {w*.72} {h*.48}');root.set('width','1200');root.set('height','1050')
                page.set_content('<style>body{margin:0}</style>'+ET.tostring(root,encoding='unicode'));page.evaluate('document.fonts.ready');page.screenshot(path=str(out/detail))
                candidates.append(dict(candidate=letter,whole=whole,detail=detail))
            ref=REPO/f'projects/usefulcharts-style/artifacts/images/reference-{refname}.png';rw,rh=Image.open(ref).size;refwhole=f'{case}-reference-whole.png';refdetail=f'{case}-reference-detail.png';shutil.copy2(ref,out/refwhole)
            data=base64.b64encode(ref.read_bytes()).decode();page.set_content(f'<style>body{{margin:0}}</style><svg width="1200" height="1050" viewBox="{rw*.04} {rh*.20} {rw*.72} {rh*.48}"><image width="{rw}" height="{rh}" href="data:image/png;base64,{data}"/></svg>');page.screenshot(path=str(out/refdetail))
            source=ROOT/'artifacts/revision-3'/case/'source.json';shutil.copy2(source,out/f'{case}-source.json')
            subjects.append(dict(subject=case,candidates=candidates,reference=dict(whole=refwhole,detail=refdetail,source_url=url),source_inventory=f'{case}-source.json'))
        b.close()
    manifest=dict(subjects=subjects,normalization='Candidates have equal whole-view width. Detail views use equal relative body crops, rendered in the same viewport.',files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir()) if f.is_file()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(subjects=len(subjects),files=len(manifest['files']))))
if __name__=='__main__':main()
