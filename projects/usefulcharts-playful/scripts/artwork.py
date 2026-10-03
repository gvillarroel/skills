#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Place intact artwork through SVG viewports and render portable poster evidence."""
from pathlib import Path
import base64
import hashlib
import json
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
def tag(n):return '{'+NS+'}'+n
def rect(root,x,y,w,h,fill='#0B1B2A',stroke=None,rx=0):
    a=dict(x=str(x),y=str(y),width=str(w),height=str(h),fill=fill,rx=str(rx))
    if stroke:a['stroke']=stroke
    return ET.SubElement(root,tag('rect'),a)
def txt(root,x,y,value,size=20,color='#EAF3F4',weight='400',**attrs):
    a=dict(x=str(x),y=str(y),fill=color,**{'font-size':str(size),'font-weight':weight,'font-family':'Arial,sans-serif','data-background':'#0B1B2A'})
    a.update(attrs);e=ET.SubElement(root,tag('text'),a);e.text=value;return e
def art(root,path,box,identifier,anchors,groups,explanation,crop=None):
    path=Path(path);iw,ih=Image.open(path).size;sx,sy,cw,ch=crop or (0,0,iw,ih)
    x,y,w,h=box;scale=min(w/cw,h/ch);x+=(w-cw*scale)/2;y+=(h-ch*scale)/2;w=cw*scale;h=ch*scale
    defs=root.find(tag('defs'))
    if defs is None:defs=ET.SubElement(root,tag('defs'))
    identifier_asset='asset-'+hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    if defs.find(f".//*[@id='{identifier_asset}']") is None:
        ET.SubElement(defs,tag('image'),dict(id=identifier_asset,width=str(iw),height=str(ih),href='data:image/'+('jpeg' if path.suffix.lower() in ['.jpg','.jpeg'] else 'png')+';base64,'+base64.b64encode(path.read_bytes()).decode()))
    el=ET.SubElement(root,tag('svg'),dict(x=str(x),y=str(y),width=str(w),height=str(h),viewBox=f'{sx} {sy} {cw} {ch}',overflow='hidden',**{'data-art-id':identifier,'data-art-anchor':' '.join(anchors),'data-art-group':' '.join(groups),'data-art-role':'subject','aria-label':explanation}))
    if path.name in ('discovery.png','protostar.png','klingon-bird.png','enterprise-original.jpg','mars96-dlr.jpg'):
        el.set('style','mix-blend-mode:screen')
    ET.SubElement(el,tag('use'),dict(href='#'+identifier_asset))
    return dict(placement_id=identifier,asset_id=path.stem,path=str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),anchors=anchors,groups=groups,explanation=explanation,box=dict(x=x,y=y,w=w,h=h),recognized_at_placed_size=False)
def save(root,out,arts,source):
    out.mkdir(parents=True,exist_ok=True);h=float(root.get('height'))
    for a in arts:a['region']=['upper','middle','lower'][min(2,int(3*a['box']['y']/h))]
    (out/'poster.svg').write_text(ET.tostring(root,encoding='unicode'),encoding='utf-8')
    (out/'art-map.json').write_text(json.dumps(arts,indent=2)+'\n')
    (out/'source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def render(out,detail=None):
    svg=(out/'poster.svg').read_text(encoding='utf-8');root=ET.fromstring(svg);w,h=[float(root.get(k)) for k in ('width','height')]
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport=dict(width=int(w),height=min(1500,int(h))))
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content('<html><head><style>html,body{margin:0}body>svg{display:block}</style></head><body>'+svg+'</body></html>');page.evaluate('document.fonts.ready')
        info=page.evaluate('''() => {const s=document.querySelector('body>svg');return {texts:[...s.querySelectorAll('text')].map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height}}),images:[...s.querySelectorAll('[data-art-id]')].map(e=>({id:e.dataset.artId,x:+e.getAttribute('x'),y:+e.getAttribute('y'),w:+e.getAttribute('width'),h:+e.getAttribute('height')}))}}''')
        page.locator('body > svg').screenshot(path=str(out/'poster.png'))
        if detail:
            page.set_viewport_size(dict(width=int(w),height=int(h)))
            page.screenshot(path=str(out/'detail.png'),clip=dict(zip(('x','y','width','height'),detail)))
        page.pdf(path=str(out/'poster.pdf'),width=f'{w}px',height=f'{h}px',print_background=True,margin=dict(top='0',bottom='0',left='0',right='0'))
        page.add_style_tag(content='body>svg{width:1800px;height:auto}');page.set_viewport_size(dict(width=1800,height=1100));page.locator('body > svg').screenshot(path=str(out/'preview.png'))
        browser.close()
    overlaps=[]
    def intersect(a,b):return a['x']<b['x']+b['w']-1 and a['x']+a['w']>b['x']+1 and a['y']<b['y']+b['h']-1 and a['y']+a['h']>b['y']+1
    for a in info['images']:
        for t in info['texts']:
            if intersect(a,t):overlaps.append(dict(image=a['id'],text=t['text']))
    info.update(canvas=[w,h],errors=errors,image_text_overlaps=overlaps,svg_sha256=hashlib.sha256(svg.encode()).hexdigest())
    (out/'render.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(dict(case=out.name,canvas=[w,h],images=len(info['images']),image_text_overlaps=overlaps[:12],errors=errors)))

if __name__=='__main__':
    import sys
    render(Path(sys.argv[1]))
