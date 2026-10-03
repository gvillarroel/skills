#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pillow>=11"]
# ///
"""Audit image placement and text contrast against the actual composed backdrop."""
from pathlib import Path
from functools import lru_cache
import json
import math
import argparse
from PIL import Image
from playwright.sync_api import sync_playwright

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/'artifacts/space-edition'
REVIEW=OUT/'reviews/final'


@lru_cache(maxsize=262144)
def luminance(rgb):
    linear=[c/3294.6 if c<=10.31475 else ((c/255+.055)/1.055)**2.4 for c in rgb[:3]]
    return sum(a*b for a,b in zip(linear,(.2126,.7152,.0722)))


def main():
    global OUT,REVIEW
    parser=argparse.ArgumentParser()
    parser.add_argument('--numeric',action='store_true')
    parser.add_argument('--flow',action='store_true')
    args=parser.parse_args()
    if args.numeric:OUT=PROJECT/'artifacts/numeric-edition';REVIEW=OUT/'reviews/final'
    if args.flow:OUT=PROJECT/'artifacts/flow-edition';REVIEW=OUT/'reviews/final'
    svg=(OUT/'svgs/star-trek-starships.svg').read_text(encoding='utf-8')
    layout=json.loads((OUT/'reviews/layout.json').read_text())
    width,height=layout['width'],layout['height']
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        tab=browser.new_page(viewport={'width':width,'height':1000},device_scale_factor=1)
        tab.set_content('<style>body{margin:0}svg{display:block}::-webkit-scrollbar{display:none}</style>'+svg)
        tab.evaluate('document.fonts.ready')
        geometry=tab.evaluate('''(numeric)=>{
          const box=e=>{const b=e.getBBox();return {x:b.x,y:b.y,w:b.width,h:b.height}};
          const texts=[...document.querySelectorAll('text')].map(e=>({...box(e),text:e.textContent,record:e.closest('.record')?.dataset.id||null,size:+e.getAttribute('font-size'),color:getComputedStyle(e).fill.match(/[0-9.]+/g).map(Number)}));
          const art=[...document.querySelectorAll('.ship-art')].map(e=>({...box(e),id:e.dataset.ship}));
          const collisions=[];
          for(const a of art)for(const b of texts)if(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y)collisions.push({ship:a.id,text:b.text,record:b.record});
          const root=document.querySelector('svg'),items=[...root.children],first=items.findIndex(e=>e.tagName==='rect');
          if(numeric){for(const e of root.querySelectorAll('text'))e.style.display='none'}
          else for(let i=0;i<items.length;i++)if(items[i].tagName!=='defs'&&!(i>=first&&i<first+3))items[i].style.display='none';
          return {texts,art,collisions};
        }''',args.numeric or args.flow)
        background=Image.new('RGB',(width,height))
        for offset in range(0,height,1000):
            actual=tab.evaluate('(y)=>{window.scrollTo(0,y);return scrollY}',offset)
            target=REVIEW/f'background-{offset:05}.png'
            tab.screenshot(path=str(target),animations='disabled')
            top=round(offset-actual)
            background.paste(Image.open(target).crop((0,top,width,top+min(1000,height-offset))),(0,offset))
        browser.close()
    contrasts=[]
    for t in geometry['texts']:
        rect=(max(0,math.floor(t['x'])),max(0,math.floor(t['y'])),min(width,math.ceil(t['x']+t['w'])),min(height,math.ceil(t['y']+t['h'])))
        foreground=luminance(tuple(t['color']))
        colors=set(background.crop(rect).getdata())
        ratios=[(max(foreground,luminance(c))+.05)/(min(foreground,luminance(c))+.05) for c in colors]
        contrasts.append(dict(text=t['text'],record=t['record'],size=t['size'],minimum=min(ratios),required=3 if t['size']>=24 else 4.5))
    failures=[t for t in contrasts if t['minimum']<t['required']]
    assets=[]
    for file in ['enterprise-nx.png','voyager.png','defiant.png','discovery.png','protostar.png','klingon-bird.png','nebula-background.png']:
        im=Image.open(PROJECT/'artifacts/images/space-edition'/file)
        assets.append(dict(file=file,mode=im.mode,size=im.size,alpha_extrema=im.getchannel('A').getextrema() if 'A' in im.getbands() else None))
    result=dict(status='pass' if not failures and not geometry['collisions'] else 'fail',text_count=len(contrasts),text_background_minimum=min(t['minimum'] for t in contrasts),contrast_method='WCAG luminance on the brightest/worst actual background pixel anywhere inside every complete browser text bounding box, before text paint; 4.5 small text and 3 large text.',contrast_failures=failures,image_text_collisions=geometry['collisions'],illustration_placements=geometry['art'],assets=assets,contrasts=contrasts)
    (REVIEW/'art-audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in {'contrasts','illustration_placements','assets'}}))
    assert result['status']=='pass'


if __name__=='__main__':main()
