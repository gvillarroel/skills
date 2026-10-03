// Run: node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/inventory-native-arrows.ts
import {createRequire} from 'node:module'
import {readFileSync,writeFileSync,readdirSync,mkdirSync} from 'node:fs'
const root=new URL('../../../',import.meta.url)
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root))
const {chromium}=require('playwright')
const mermaid=new URL('skills/mermaid/assets/examples/mermaid-max-complexity/',root)
const manifest=JSON.parse(readFileSync(new URL('gallery.json',mermaid),'utf8'))
const files=manifest.patterns.flatMap(p=>[['staticSvg','static'],['animatedSvg','settled'],['animatedSvg','mid-reveal']].map(([key,state])=>({renderer:'mermaid',path:new URL(p[key],mermaid).href,state})))
for(const folder of ['plantuml-colorset-renderer','plantuml-colorset-renderer-cs1']){
 const base=new URL('skills/plantuml-colorset-renderer/assets/examples/'+folder+'/svg/',root)
 for(const name of readdirSync(base).filter(n=>n.endsWith('.svg')))files.push({renderer:'plantuml',path:new URL(name,base).href,state:'static'})
}
for(const name of readdirSync(new URL('skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/assets/animated-svg/',root)).filter(n=>n.endsWith('.svg'))){
 const path=new URL('skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/assets/animated-svg/'+name,root).href
 files.push({renderer:'animejs',path,state:'settled'},{renderer:'animejs',path,state:'mid-reveal'})
}
const out=new URL('projects/arrow-contrast-diagrams/artifacts/',root);mkdirSync(out,{recursive:true})
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1900,height:1600}})
const rows=[]
for(const entry of files){
 await page.goto(entry.path)
 await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))})
 await page.evaluate(state=>{const a=document.getAnimations(),end=Math.max(0,...a.map(x=>x.effect?.getComputedTiming().endTime).filter(Number.isFinite));for(const x of a){x.pause();x.currentTime=state==='mid-reveal'?end/2:end+1000}},entry.state)
 await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))))
 const result=await page.evaluate(({renderer,state})=>{
  const svg=document.querySelector('svg'),family=svg.getAttribute('aria-roledescription')||svg.getAttribute('data-diagram-type')||'asset'
  const lum=rgb=>rgb.map(c=>c/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4).reduce((s,c,i)=>s+c*[.2126,.7152,.0722][i],0)
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05)
  const color=value=>{const n=value.match(/[\d.]+/g)?.map(Number);return n&&n.length>=3?{rgb:n.slice(0,3),alpha:n[3]??1}:null}
  const opacity=e=>{let o=1;for(let p=e;p;p=p.parentElement)o*=parseFloat(getComputedStyle(p).opacity);return o}
  const reveals=new Set(document.getAnimations().filter(a=>a.effect?.getKeyframes().some(k=>'opacity'in k)).map(a=>a.effect.target))
  const revealing=e=>{for(let p=e;p;p=p.parentElement)if(reveals.has(p)&&opacity(e)<.999)return true;return false}
  const all=[...svg.querySelectorAll('path,line,polyline,polygon')]
  const shafts=all.filter(e=>{
   if(e.closest('defs,marker,clipPath'))return false
   const s=getComputedStyle(e),c=(e.getAttribute('class')||'').split(/\s+/).filter(c=>!c.startsWith('am-')).join(' '),m=s.markerEnd!=='none'||s.markerStart!=='none'
   if(m&&(s.markerEnd+s.markerStart).includes('sequencenumber')&&parseFloat(s.strokeWidth)===0)return false
   if(s.stroke==='none'||parseFloat(s.strokeWidth)===0)return false
   return m||/(arrow|relation|edge|link|message-line|messageLine)/i.test(c)||e.closest('g.link')||renderer==='plantuml'&&!['JSON','YAML'].includes(family)&&!e.closest('g.entity')&&s.fill==='none'
  })
  const heads=all.filter(e=>{if(e.closest('defs,marker,clipPath,g.entity'))return false;const s=getComputedStyle(e),b=e.getBoundingClientRect(),c=e.getAttribute('class')||'';return s.fill!=='none'&&b.width>0&&b.height>0&&(/^(arrow|message-arrow|arrowhead)$/i.test(c)||renderer==='plantuml'&&e.tagName==='polygon'&&Math.max(b.width,b.height)<20)})
  const connections=new Set([...shafts,...heads])
  const shapes=[...svg.querySelectorAll('rect,circle,ellipse,polygon,path')].filter(e=>{const s=getComputedStyle(e),b=e.getBoundingClientRect(),p=color(s.fill);return !e.closest('defs,marker,clipPath')&&!connections.has(e)&&p&&p.alpha>0&&b.width>0&&b.height>0&&s.display!=='none'&&opacity(e)>0})
  const contains=(e,p)=>{const m=e.getScreenCTM();return m&&typeof e.isPointInFill==='function'&&e.isPointInFill(p.matrixTransform(m.inverse()))}
  const backing=(p,connection)=>{let rgb=[255,255,255],occluded=false,transientOcclusion=false;const layers=[];for(const e of shapes)if(contains(e,p)){const s=getComputedStyle(e),c=color(s.fill),a=c.alpha*parseFloat(s.fillOpacity)*opacity(e);rgb=c.rgb.map((v,i)=>v*a+rgb[i]*(1-a));const above=connection&&(connection.compareDocumentPosition(e)&Node.DOCUMENT_POSITION_FOLLOWING);if(above&&a>=.999)occluded=true;if(above&&revealing(e)&&state==='mid-reveal')transientOcclusion=true;layers.push({class:e.getAttribute('class'),fill:s.fill,aboveConnection:!!above,transientOcclusion:above&&revealing(e)})}return {rgb,layers,occluded,transientOcclusion}}
  const records=[]
  for(const e of shafts){
   const s=getComputedStyle(e),p=color(s.stroke),length=e.getTotalLength?.();if(!p||!length)continue
   const samples=[]
   for(const t of [.015,.05,.2,.4,.6,.8,.95,.985]){const point=e.getPointAtLength(length*t).matrixTransform(e.getScreenCTM()),bg=backing(point,e),alpha=p.alpha*parseFloat(s.strokeOpacity)*opacity(e),paint=p.rgb.map((v,i)=>v*alpha+bg.rgb[i]*(1-alpha));samples.push({t,ratio:ratio(paint,bg.rgb),background:bg.rgb,layers:bg.layers,occluded:bg.occluded,transientOcclusion:bg.transientOcclusion})}
   const markers=[]
   for(const [key,t] of [['markerStart',0],['markerEnd',1]]){
    const ref=s[key].match(/#([^"')]+)/)?.[1],marker=ref&&document.getElementById(ref);if(!marker)continue
    const anchor=e.getPointAtLength(length*t),near=e.getPointAtLength(t?Math.max(0,length-.1):Math.min(.1,length))
    const angle=Math.atan2(t?anchor.y-near.y:near.y-anchor.y,t?anchor.x-near.x:near.x-anchor.x)*180/Math.PI+(t===0&&marker.getAttribute('orient')==='auto-start-reverse'?180:0)
    const units=marker.getAttribute('markerUnits')==='userSpaceOnUse'?1:parseFloat(s.strokeWidth)
    const vb=marker.viewBox.baseVal,hasVB=vb.width>0,scale=hasVB?Math.min(marker.markerWidth.baseVal.value/vb.width,marker.markerHeight.baseVal.value/vb.height):1
    const matrix=e.getScreenCTM().translate(anchor.x,anchor.y).rotate(angle).scale(units*scale).translate(-marker.refX.baseVal.value,-marker.refY.baseVal.value)
    for(const child of marker.querySelectorAll('path,polygon,circle,polyline,line,rect')){
     const ms=getComputedStyle(child),fill=color(ms.fill),stroke=color(ms.stroke),bb=child.getBBox(),points=[]
     // White interiors in cardinality glyphs are structural voids: their visible
     // stroke carries the symbol and must contrast. Filled solid heads use fill.
     if(fill&&!(stroke&&parseFloat(ms.strokeWidth)>0))for(const dx of [.3,.5,.7])for(const dy of [.3,.5,.7]){const pt=new DOMPoint(bb.x+bb.width*dx,bb.y+bb.height*dy);if(child.isPointInFill(pt))points.push([pt,fill,'fill'])}
     if(stroke&&child.getTotalLength?.()>0)for(const q of [.1,.3,.5,.7,.9])points.push([child.getPointAtLength(child.getTotalLength()*q),stroke,'stroke'])
     for(const [local,c,paintRole] of points){const point=local.matrixTransform(matrix),bg=backing(point,e),a=c.alpha*opacity(e),paint=c.rgb.map((v,i)=>v*a+bg.rgb[i]*(1-a));markers.push({ref,role:key,paintRole,fill:ms.fill,stroke:ms.stroke,ratio:ratio(paint,bg.rgb),background:bg.rgb,layers:bg.layers,occluded:bg.occluded})}
    }
   }
   const visible=[...samples,...markers].filter(x=>!x.occluded&&!x.transientOcclusion),min=Math.min(...visible.map(x=>x.ratio))
   records.push({tag:e.tagName,class:e.getAttribute('class'),id:e.id,stroke:s.stroke,opacity:opacity(e),length,minContrast:min,revealIntentional:state==='mid-reveal'&&revealing(e),samples,markers})
  }
  for(const e of heads){const b=e.getBoundingClientRect(),point=new DOMPoint((b.left+b.right)/2,(b.top+b.bottom)/2),bg=backing(point),s=getComputedStyle(e),p=color(s.fill),a=p.alpha*parseFloat(s.fillOpacity)*opacity(e),paint=p.rgb.map((v,i)=>v*a+bg.rgb[i]*(1-a));records.push({tag:e.tagName,class:e.getAttribute('class'),id:e.id,fill:s.fill,opacity:opacity(e),minContrast:ratio(paint,bg.rgb),head:true,background:bg.rgb,layers:bg.layers,revealIntentional:state==='mid-reveal'&&revealing(e)})}
  return {family,shaftCount:shafts.length,headCount:heads.length,records}
 },entry)
 rows.push({...entry,...result})
}
await browser.close()
writeFileSync(new URL('native-arrow-inventory.json',out),JSON.stringify(rows,null,2)+'\n')
const summary=rows.map(row=>({renderer:row.renderer,path:row.path.replace(root.href,''),family:row.family,state:row.state,shaftCount:row.shaftCount,headCount:row.headCount,findings:row.records.filter(r=>!r.revealIntentional&&r.minContrast<3)}))
writeFileSync(new URL('native-arrow-summary.json',out),JSON.stringify(summary,null,2)+'\n')
console.log(JSON.stringify({states:rows.length,shafts:rows.reduce((n,r)=>n+r.shaftCount,0),heads:rows.reduce((n,r)=>n+r.headCount,0),findingStates:summary.filter(r=>r.findings.length).length,findings:summary.reduce((n,r)=>n+r.findings.length,0)}))
