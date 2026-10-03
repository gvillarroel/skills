#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pillow>=11", "pymupdf>=1.25"]
# ///
"""Render the actual vector poster, audit geometry, and proof the vector PDF."""
from pathlib import Path
import argparse
import json
from PIL import Image
from playwright.sync_api import sync_playwright
import pymupdf

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/"artifacts"


def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--version',default='final')
    parser.add_argument('--pdf',action='store_true')
    parser.add_argument('--space',action='store_true',help='Render the separate space edition')
    parser.add_argument('--lineages',action='store_true',help='Render the compact shared-lineage edition')
    parser.add_argument('--numeric',action='store_true',help='Render the shared calendar-axis edition')
    parser.add_argument('--flow',action='store_true',help='Render the full-context shared-track prototype')
    args=parser.parse_args()
    if args.space:OUT=PROJECT/'artifacts/space-edition'
    if args.lineages:OUT=PROJECT/'artifacts/lineages-edition'
    if args.numeric:OUT=PROJECT/'artifacts/numeric-edition'
    if args.flow:OUT=PROJECT/'artifacts/flow-edition'
    layout=json.loads((OUT/'reviews/layout.json').read_text())
    svg=(OUT/'svgs/star-trek-starships.svg').read_text(encoding='utf-8')
    W,H=layout['width'],layout['height']
    html=f'<!doctype html><html><meta charset="utf-8"><style>html,body{{margin:0;padding:0}}::-webkit-scrollbar{{display:none}}svg{{display:block;width:{W}px;height:{H}px}}@page{{margin:0}}</style><body>{svg}</body></html>'
    review=OUT/'reviews'/args.version;review.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        page=browser.new_page(viewport={'width':W,'height':1000},device_scale_factor=1)
        page.set_content(html,wait_until='load')
        page.evaluate('document.fonts.ready')
        audit=page.evaluate('''() => {
          const svg=document.querySelector('svg'),v=svg.viewBox.baseVal;
          const texts=[...svg.querySelectorAll('text')].map((e,i)=>{const b=e.getBBox();return {i,text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height,role:e.dataset.role,record:e.closest('.record')?.dataset.id||null}});
          const outside=texts.filter(b=>b.x<0||b.y<0||b.x+b.w>v.width+.1||b.y+b.h>v.height+.1);
          const overlaps=[];
          for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){let a=texts[i],b=texts[j];if(a.x<b.x+b.w-.6&&a.x+a.w>b.x+.6&&a.y<b.y+b.h-.6&&a.y+a.h>b.y+.6)overlaps.push({a:a.text,b:b.text,record_a:a.record,record_b:b.record})}
          const overflow=[];for(const e of svg.querySelectorAll('.record,.continuation')){let r=e.querySelector('.hit-area').getBBox();for(let t of e.querySelectorAll('text')){let b=t.getBBox();if(b.x<r.x-.1||b.y<r.y-.1||b.x+b.width>r.x+r.width+.8||b.y+b.height>r.y+r.height+.8)overflow.push({id:e.dataset.id,text:t.textContent})}}
          return {text_count:texts.length,record_count:svg.querySelectorAll('.record').length,font_barlow:document.fonts.check('700 28px Barlow'),outside,overlaps,envelope_overflow:overflow,texts};
        }''')
        (review/'browser-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
        # Screenshot through a bounded viewport; large single-surface captures are unreliable.
        im=Image.new('RGB',(W,H))
        for offset in range(0,H,1000):
            tile=review/f'tile-{offset:05}.png'
            actual=page.evaluate('(y)=>{window.scrollTo(0,y);return window.scrollY}',offset)
            page.screenshot(path=str(tile),full_page=False,animations='disabled',timeout=60000)
            top=round(offset-actual);hh=min(1000,H-offset)
            im.paste(Image.open(tile).crop((0,top,W,top+hh)),(0,offset))
        im.save(OUT/'images/star-trek-starships.png')
        im.resize((1200,round(H*1200/W)),Image.Resampling.LANCZOS).save(review/'full.png')
        im.resize((1600,round(H*1600/W)),Image.Resampling.LANCZOS).save(OUT/'images/star-trek-starships-preview.png')
        header_height=345 if args.flow else 402 if args.numeric else min(H,1014)
        im.crop((0,0,W,header_height)).resize((1800,round(header_height*1800/W)),Image.Resampling.LANCZOS).save(review/'header.png')
        for r in layout['regions']:
            x,y=round(r['x']),round(r['y']);ww,hh=round(r['w']),min(round(r['h']),1350)
            im.crop((x,y,x+ww,y+hh)).save(review/(r['id']+'-detail.png'))
        if args.pdf:
            page.evaluate('window.scrollTo(0,0)')
            print_width=W/100 if args.numeric or args.flow else 48 if args.lineages else 36
            inches=print_width*H/W
            page.add_style_tag(content=f'@media print{{html,body{{width:{print_width}in!important;height:{inches}in!important}}svg{{width:{print_width}in!important;height:{inches}in!important}}}}')
            page.pdf(path=str(OUT/'documents/star-trek-starships.pdf'),width=f'{print_width}in',height=f'{inches}in',print_background=True,scale=1,margin={'top':'0','right':'0','bottom':'0','left':'0'})
        browser.close()
    if args.pdf:
        doc=pymupdf.open(OUT/'documents/star-trek-starships.pdf')
        data=json.loads((PROJECT/'data/ships.json').read_text(encoding='utf-8'));ships={s['id']:s for s in data['ships']}
        assert len(doc)==1,len(doc)
        sx=doc[0].rect.width/W;sy=doc[0].rect.height/H
        for b in layout['boxes']:
            box=pymupdf.Rect(b['x']*sx,b['y']*sy,(b['x']+b['w'])*sx,(b['y']+b['h'])*sy)
            doc[0].insert_link({'kind':pymupdf.LINK_URI,'from':box,'uri':data['sources'][ships[b['id']]['source']]['url']})
        doc.saveIncr()
        page=doc[0];scale=1200/page.rect.width
        page.get_pixmap(matrix=pymupdf.Matrix(scale,scale)).save(str(review/'pdf-proof.png'))
        report=dict(pages=len(doc),text_characters=len(page.get_text()),page_size=[page.rect.width,page.rect.height],source_links=len(page.get_links()),fonts=page.get_fonts())
        (review/'pdf-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(version=args.version,records=audit['record_count'],outside=len(audit['outside']),overlaps=len(audit['overlaps']),envelope_overflow=len(audit['envelope_overflow']),review=str(review))))


if __name__=='__main__':main()
