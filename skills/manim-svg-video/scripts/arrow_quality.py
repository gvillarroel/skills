#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Measure actual SVG arrow paint, including instanced markers and alpha backings."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ARROW_AUDIT = r"""(options = {}) => {
 options=options||{};
 const root=document.querySelector(options.selector||'svg');
 const issues=[],records=[],signalOverlays=[],all=[...root.querySelectorAll('*')],order=new Map(all.map((e,i)=>[e,i]));
 for(const e of root.querySelectorAll('[data-arrow-issue]'))issues.push({kind:'arrow-routing-failure',id:e.dataset.arrowId,reason:e.dataset.arrowIssue});
 const excluded=e=>!!e.closest('defs,clipPath,mask,marker,pattern,symbol');
 const ctx=document.createElementNS('http://www.w3.org/1999/xhtml','canvas').getContext('2d',{willReadFrequently:true});
 function rgba(value,context) {
  if(value==='context-stroke')value=context?.stroke;
  if(value==='context-fill')value=context?.fill;
  if(!value||value==='none'||value.startsWith('url('))return null;
  ctx.clearRect(0,0,1,1);ctx.fillStyle=value;ctx.fillRect(0,0,1,1);
  const p=ctx.getImageData(0,0,1,1).data;return [p[0],p[1],p[2],p[3]/255];
 }
 function alpha(e,stop=null) {
  let a=1;for(let n=e;n&&n!==stop;n=n.parentElement){const s=getComputedStyle(n);
   if(s.display==='none'||s.visibility!=='visible')return 0;
   a*=+s.opacity;
   for(const f of s.filter.matchAll(/opacity\((\d+(?:\.\d+)?)(%)?\)/g))a*=+f[1]/(f[2]?100:1);
  }return a;
 }
 const geometry=all.filter(e=>e instanceof SVGGeometryElement&&!excluded(e)&&alpha(e)>0);
 function local(e,p){const m=e.getScreenCTM();return m&&Math.abs(m.a*m.d-m.b*m.c)>1e-12?new DOMPoint(p.x,p.y).matrixTransform(m.inverse()):null;}
 function hit(e,p,channel) {const q=local(e,p);if(!q)return false;
  return channel==='fill'?e.isPointInFill(q):e.isPointInStroke(q);
 }
 const blend=(base,c,a)=>base.map((v,i)=>v*(1-a)+c[i]*a);
 function surface(p,arrow,parts,arrowKind) {
  let bg=rgba(options.canvas||getComputedStyle(document.body||document.documentElement).backgroundColor)||[255,255,255,1];
  bg=blend([255,255,255],bg,bg[3]);let cover=0,coverElement=null;
  for(const e of geometry){
   if(parts.has(e)||e.closest('[data-arrow-id]')===arrow.closest('[data-arrow-id]')&&arrow.closest('[data-arrow-id]'))continue;
   const s=getComputedStyle(e);
   if(s.fill.startsWith('url(')&&hit(e,p,'fill'))issues.push({kind:'arrow-complex-backing',arrow:arrow.id||arrow.dataset.arrowId||null,paint:s.fill,x:p.x,y:p.y});
   // Connector crossings are checked by routing audits; narrow shafts do not
   // define a backing region. Filled bodies/regions still contribute here.
   for(const channel of ['fill']){
    const c=rgba(s[channel]);if(!c||!hit(e,p,channel))continue;
    // This exact connector-owned moving token is a semantic overlay, not a
    // node/region/label backing. Heads are never exempted from its coverage.
    if(arrowKind==='shaft'&&e.matches('[data-relationship-pulse="true"]')&&e.closest('[data-relationship-id]')){
     signalOverlays.push({arrow:arrow.id||arrow.dataset.arrowId||null,owner:e.closest('[data-relationship-id]').dataset.relationshipId,x:p.x,y:p.y,reason:'connector-owned moving signal crossing'});continue;
    }
    if(channel==='stroke'&&parseFloat(s.strokeWidth)<=0)continue;
    const a=c[3]*+s[channel+'Opacity']*alpha(e);
    if(order.get(e)>order.get(arrow)){cover=1-(1-cover)*(1-a);if(a>.98)coverElement=e.id||e.getAttribute('class')||e.dataset.nodeId||e.tagName;}
    else bg=blend(bg,c,a);
   }
  }return {bg,cover,coverElement};
 }
 const lum=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
 const contrast=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
 function check(arrow,channel,points,paint,opacity,kind,parts,id) {
  let minimum=Infinity,visible=0,covered=0,at=null,occluders=new Set();
  for(const p of points){
   if(p.x<0||p.y<0||p.x>innerWidth||p.y>innerHeight)continue;
   const {bg,cover,coverElement}=surface(p,arrow,parts,kind);
   if(cover>.98){covered++;occluders.add(coverElement);continue;}
   const ink=blend(bg,paint,paint[3]*opacity),ratio=contrast(ink,bg);visible++;
   if(ratio<minimum){minimum=ratio;at={x:p.x,y:p.y,background:bg,paint:ink};}
  }
  const record={id,kind,channel,samples:points.length,visible,covered,occluders:[...occluders],minimum:Number.isFinite(minimum)?minimum:null,at};records.push(record);
  if(visible&&minimum<3-1e-10)issues.push({...record,kind:'arrow-low-contrast'});
  if(kind==='shaft'&&covered>0)issues.push({...record,kind:'arrow-shaft-occluded'});
  if(kind==='head'&&covered>0)issues.push({...record,kind:'arrow-head-occluded'});
  return record;
 }
 const shafts=geometry.filter(e=>e.hasAttribute('data-arrow-shaft')||getComputedStyle(e).markerEnd!=='none'||getComputedStyle(e).markerStart!=='none'||getComputedStyle(e).markerMid!=='none');
 for(const arrow of shafts) {
  const style=getComputedStyle(arrow),paint=rgba(style.stroke),opacity=alpha(arrow)*+style.strokeOpacity;
  if(style.markerMid!=='none')issues.push({kind:'arrow-unsupported-mid-marker',id:arrow.id||arrow.dataset.arrowId||null,reason:'Materialize intermediate heads as tagged ordinary paths, or verify their actual pixel geometry separately.'});
  if(!opacity)continue;
  if(!paint){issues.push({kind:'arrow-unsupported-paint',id:arrow.id||arrow.dataset.arrowId||null,channel:'stroke',paint:style.stroke});continue;}
  const id=arrow.dataset.arrowId||arrow.closest('[data-arrow-id]')?.dataset.arrowId||arrow.id||'arrow-'+shafts.indexOf(arrow);
  const parts=new Set([arrow,...(arrow.closest('[data-arrow-id]')?.querySelectorAll('[data-arrow-head]')||[])]);
  const length=arrow.getTotalLength(),raw=arrow.getScreenCTM();if(!raw||Math.abs(raw.a*raw.d-raw.b*raw.c)<1e-12)continue;
  const m=new DOMMatrix([raw.a,raw.b,raw.c,raw.d,raw.e,raw.f]),scale=Math.hypot(m.a,m.b);
  const count=Math.max(3,Math.min(160,Math.ceil(length*scale/5))),points=[];
  for(let i=0;i<count;i++){const p=arrow.getPointAtLength(length*(i+.5)/count);points.push(new DOMPoint(p.x,p.y).matrixTransform(m));}
  check(arrow,'stroke',points,paint,opacity,'shaft',parts,id);
  const actualWidth=parseFloat(style.strokeWidth)*(style.vectorEffect==='non-scaling-stroke'?1:scale);
  if(actualWidth<1.25)issues.push({kind:'arrow-too-thin',id,width:actualWidth});
  for(const end of ['start','end']) {
   const value=style[end==='end'?'markerEnd':'markerStart'],match=value?.match(/#([^"\)]+)/);
   if(!match)continue;
   const marker=root.querySelector('#'+CSS.escape(match[1]));if(!marker){issues.push({kind:'arrow-marker-missing',id,end});continue;}
   const p=arrow.getPointAtLength(end==='end'?length:0),q=arrow.getPointAtLength(end==='end'?Math.max(0,length-.2):Math.min(length,.2));
   let angle=Math.atan2(end==='end'?p.y-q.y:q.y-p.y,end==='end'?p.x-q.x:q.x-p.x)*180/Math.PI;
   const orient=marker.getAttribute('orient')||'0';
   if(!orient.startsWith('auto'))angle=parseFloat(orient)||0;else if(end==='start'&&orient==='auto-start-reverse')angle+=180;
   const unit=marker.getAttribute('markerUnits')==='userSpaceOnUse'?1:parseFloat(style.strokeWidth);
   const vb=marker.viewBox.baseVal,mw=marker.markerWidth.baseVal.value,mh=marker.markerHeight.baseVal.value;
   const sx=vb.width?mw/vb.width:1,sy=vb.height?mh/vb.height:1;
   const uniform=Math.min(sx,sy),none=marker.getAttribute('preserveAspectRatio')==='none';
   const ax=none?sx:uniform,ay=none?sy:uniform;
   const refX=marker.refX.baseVal.value,refY=marker.refY.baseVal.value;
   const instance=m.translate(p.x,p.y).rotate(angle).scale(unit).scale(ax,ay).translate(-refX,-refY);
   const beforeHead=records.length;
   for(const child of marker.querySelectorAll('path,polygon,polyline,circle,rect,ellipse')) {
    let matrix=instance;const chain=[];for(let n=child;n&&n!==marker;n=n.parentElement)chain.unshift(n);
    for(const n of chain){const t=n.transform?.baseVal.consolidate();if(t)matrix=matrix.multiply(t.matrix);}
    const css=getComputedStyle(child),b=child.getBBox(),samples=[];
    for(const u of [.18,.35,.5,.65,.82])for(const v of [.18,.35,.5,.65,.82]){
     const a=new DOMPoint(b.x+b.width*u,b.y+b.height*v);
     if(child.isPointInFill(a))samples.push(a.matrixTransform(matrix));
    }
    const c=rgba(css.fill,style);if(css.fill!=='none'&&!c)issues.push({kind:'arrow-unsupported-paint',id,end,channel:'fill',paint:css.fill});if(c)check(arrow,'fill',samples,c,alpha(arrow)*+css.fillOpacity*alpha(child,marker.parentElement),'head',parts,id+':'+end);
    const stroke=rgba(css.stroke,style);
    if(stroke&&parseFloat(css.strokeWidth)>0){
     const length=child.getTotalLength(),strokes=[];
     for(let i=0;i<20;i++){const p=child.getPointAtLength(length*(i+.5)/20);strokes.push(new DOMPoint(p.x,p.y).matrixTransform(matrix));}
     check(arrow,'stroke',strokes,stroke,alpha(arrow)*+css.strokeOpacity*alpha(child,marker.parentElement),'head',parts,id+':'+end+':stroke');
    }
    const tipOffset=b.x+b.width-refX;
    if(end==='end'&&Math.abs(tipOffset*ax*unit*scale)>.6)issues.push({kind:'arrow-marker-tip-offset',id,end,offset:tipOffset*ax*unit*scale});
   }
   if(records.slice(beforeHead).every(r=>r.visible===0)&&records.some(r=>r.id===id&&r.kind==='shaft'&&r.visible>0))issues.push({kind:'arrow-head-invisible-or-clipped',id,end});
  }
 }
 for(const head of geometry.filter(e=>e.hasAttribute('data-arrow-head'))) {
  const css=getComputedStyle(head),channel=css.fill!=='none'?'fill':'stroke',paint=rgba(css[channel]);if(!paint){issues.push({kind:'arrow-unsupported-paint',id:head.id||head.dataset.arrowId||null,channel,paint:css[channel]});continue;}
  const b=head.getBBox(),m=head.getScreenCTM(),points=[];
  if(channel==='stroke'){const length=head.getTotalLength();for(let i=0;i<16;i++){const p=head.getPointAtLength(length*(i+.5)/16);points.push(new DOMPoint(p.x,p.y).matrixTransform(m));}}
  else for(const u of [.2,.4,.6,.8])for(const v of [.2,.4,.6,.8]){const p=new DOMPoint(b.x+b.width*u,b.y+b.height*v);if(head.isPointInFill(p))points.push(p.matrixTransform(m));}
  const id=head.dataset.arrowId||head.closest('[data-arrow-id]')?.dataset.arrowId||head.id;
  const parts=new Set(head.closest('[data-arrow-id]')?.querySelectorAll('[data-arrow-shaft],[data-arrow-head]')||[head]);
  check(head,channel,points,paint,alpha(head)*+css[channel+'Opacity'],'head',parts,id);
 }
 return {minimumContrast:3,signalOverlays,shaftCount:shafts.length,headCount:records.filter(r=>r.kind==='head').length,records,issues};
}"""

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--report',required=True,type=Path)
    parser.add_argument('--width',type=int,default=1600)
    parser.add_argument('--height',type=int)
    parser.add_argument('--selector',default='svg')
    args=parser.parse_args()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':args.width,'height':args.height or 1200})
        page.goto(args.source.resolve().as_uri());page.evaluate('document.fonts.ready')
        if args.source.suffix.lower()=='.svg':
            height=page.evaluate("([selector,width,height]) => {const svg=document.querySelector(selector),b=svg.viewBox.baseVal;const h=height||Math.round(width*b.height/b.width);svg.setAttribute('width',width);svg.setAttribute('height',h);svg.style.width=width+'px';svg.style.height=h+'px';return h;}",[args.selector,args.width,args.height])
            page.set_viewport_size({'width':args.width,'height':height})
        if page.evaluate('typeof window.svgSync === "object"'):
            page.evaluate('() => {svgSync.pause();svgSync.pauseCamera();}')
        report=page.evaluate(ARROW_AUDIT,{'selector':args.selector})
        report['source']=str(args.source);report['browser']=browser.version
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        browser.close()
    print(json.dumps({'shaftCount':report['shaftCount'],'headCount':report['headCount'],'issues':report['issues']}))
    return 1 if report['issues'] else 0

if __name__=='__main__':raise SystemExit(main())
