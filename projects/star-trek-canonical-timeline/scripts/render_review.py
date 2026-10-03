#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pillow>=11", "pymupdf>=1.25"]
# ///
"""Render the SVG in Chromium, inspect real text bounds, and export vector PDF."""
from pathlib import Path
import argparse
import json
import math
from PIL import Image
from playwright.sync_api import sync_playwright
import pymupdf

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/"artifacts"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--version",default="final")
    parser.add_argument("--pdf",action="store_true")
    args=parser.parse_args()
    layout=json.loads((OUT/"reviews/layout.json").read_text())
    svg=(OUT/"svgs/star-trek-timeline.svg").read_text(encoding="utf-8")
    html=f'<!doctype html><html><meta charset="utf-8"><style>html,body{{margin:0;padding:0}}svg{{display:block;width:{layout["width"]}px;height:{layout["height"]}px}}@page{{margin:0}}</style><body>{svg}</body></html>'
    review=OUT/"reviews"/args.version;review.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(channel="chrome",headless=True)
        page=browser.new_page(viewport={"width":layout["width"],"height":1000},device_scale_factor=1)
        page.set_content(html,wait_until="load")
        page.evaluate("document.fonts.ready")
        audit=page.evaluate('''() => {
          const svg=document.querySelector('svg'),v=svg.viewBox.baseVal;
          const texts=[...svg.querySelectorAll('text')].map((e,i)=>{const b=e.getBBox();return {i,text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height,role:e.dataset.role,record:e.closest('.record')?.id||null}});
          const outside=texts.filter(b=>b.x<0||b.y<0||b.x+b.w>v.width+.1||b.y+b.h>v.height+.1);
          const overlaps=[];
          for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){let a=texts[i],b=texts[j];if(a.x<b.x+b.w-.6&&a.x+a.w>b.x+.6&&a.y<b.y+b.h-.6&&a.y+a.h>b.y+.6)overlaps.push({a:a.text,b:b.text,record_a:a.record,record_b:b.record})}
          const envelopeOverflow=[];for(const e of svg.querySelectorAll('.record')){let r=e.querySelector('.hit-area').getBBox();for(let t of e.querySelectorAll('text')){let b=t.getBBox();if(b.x<r.x-.1||b.y<r.y-.1||b.x+b.width>r.x+r.width+.8||b.y+b.height>r.y+r.height+.8)envelopeOverflow.push({id:e.id,text:t.textContent,b:{x:b.x,y:b.y,w:b.width,h:b.height},r:{x:r.x,y:r.y,w:r.width,h:r.height}})}}
          return {text_count:texts.length,record_count:svg.querySelectorAll('.record').length,font_barlow:document.fonts.check('700 28px Barlow'),outside,overlaps,envelope_overflow:envelopeOverflow,texts};
        }''')
        (review/"browser-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
        # Tile large posters to stay below Chrome's single-surface capture budget.
        im=Image.new('RGB',(layout['width'],layout['height']))
        for offset in range(0,layout['height'],1000):
            tile=review/f'tile-{offset:05}.png'
            actual=page.evaluate('(y)=>{window.scrollTo(0,y);return window.scrollY}',offset)
            page.screenshot(path=str(tile),full_page=False,animations='disabled',timeout=60000)
            top=round(offset-actual);height=min(1000,layout['height']-offset)
            im.paste(Image.open(tile).crop((0,top,layout['width'],top+height)),(0,offset))
        im.save(OUT/"images/star-trek-timeline.png")
        im.resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS).save(review/"full.png")
        im.resize((1600,round(im.height*1600/im.width)),Image.Resampling.LANCZOS).save(OUT/"images/star-trek-preview.png")
        for region in layout["regions"]:
            if region["id"] in {"founding","dominion-war","future","main","branches"}:
                y=round(region["y"]);h=min(round(region["h"]),1400)
                im.crop((0,y,min(1800,im.width),y+h)).save(review/(region["id"]+"-detail.png"))
        if args.pdf:
            # 36-inch width; vector text and paths remain sharp at any print scale.
            page.evaluate('window.scrollTo(0,0)')
            page.add_style_tag(content=f'@media print{{html,body{{width:36in!important;height:{36*layout["height"]/layout["width"]}in!important}}svg{{width:36in!important;height:{36*layout["height"]/layout["width"]}in!important}}}}')
            page.pdf(path=str(OUT/"documents/star-trek-timeline.pdf"),width="36in",height=f'{36*layout["height"]/layout["width"]}in',print_background=True,scale=1,margin={"top":"0","right":"0","bottom":"0","left":"0"})
        browser.close()
    (review/"browser-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8")
    if args.pdf:
        doc=pymupdf.open(OUT/"documents/star-trek-timeline.pdf")
        data=json.loads((PROJECT/'data/timeline.json').read_text(encoding='utf-8'))
        events={e['id']:e for key in ['events','origins','future','branches'] for e in data[key]}
        if len(doc)==1:
            sx=doc[0].rect.width/layout['width'];sy=doc[0].rect.height/layout['height']
            for b in layout['boxes']:
                r=pymupdf.Rect(b['x']*sx,b['y']*sy,(b['x']+b['w'])*sx,(b['y']+b['h'])*sy)
                doc[0].insert_link({'kind':pymupdf.LINK_URI,'from':r,'uri':data['sources'][events[b['id']]['source']]['url']})
            doc.saveIncr()
        pdfreport=dict(pages=len(doc),text_characters=sum(len(p.get_text()) for p in doc),page_sizes=[[p.rect.width,p.rect.height] for p in doc])
        if len(doc)==1:
            page=doc[0];scale=1200/page.rect.width
            page.get_pixmap(matrix=pymupdf.Matrix(scale,scale)).save(str(review/"pdf-proof.png"))
        (review/"pdf-audit.json").write_text(json.dumps(pdfreport,indent=2)+"\n")
    print(json.dumps({"version":args.version,"records":audit["record_count"],"outside":len(audit["outside"]),"overlaps":len(audit["overlaps"]),"envelope_overflow":len(audit["envelope_overflow"]),"directory":str(review)}))

if __name__=="__main__":main()
