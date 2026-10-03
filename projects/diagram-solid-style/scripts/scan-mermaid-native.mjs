// Run: node projects/diagram-solid-style/scripts/scan-mermaid-native.mjs
import {createRequire} from 'node:module'
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
const root=new URL('../../../',import.meta.url)
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root))
const {chromium}=require('playwright')
const gallery=new URL('skills/mermaid/assets/examples/mermaid-max-complexity/',root)
const manifest=JSON.parse(readFileSync(new URL('gallery.json',gallery),'utf8'))
const out=new URL('projects/diagram-solid-style/artifacts/native-scan/',root);mkdirSync(out,{recursive:true})
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1800,height:1500}})
const rows=[]
for(const item of manifest.patterns) for(const [field,state] of [['staticSvg','static'],['animatedSvg','settled'],['animatedSvg','mid-reveal']]) {
 const file=item[field]
 await page.goto(new URL(file,gallery).href)
 await page.evaluate(async()=>{await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))})
 const animationState=await page.evaluate(state=>{const animations=document.getAnimations();const ends=animations.map(a=>a.effect?.getComputedTiming().endTime).filter(v=>Number.isFinite(v));const end=Math.max(0,...ends);for(const a of animations){a.pause();a.currentTime=state==='mid-reveal'?end/2:end+1000}return {animationCount:animations.length,timelineEndMs:end,sampleMs:state==='mid-reveal'?end/2:end+1000}},state)
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))
 const revealMetrics=await page.evaluate(()=>{const targets=[...new Set(document.getAnimations().filter(a=>a.effect?.getKeyframes().some(k=>'opacity' in k)).map(a=>a.effect.target))];return {opacityRevealTargets:targets.length,hiddenRevealTargets:targets.filter(e=>parseFloat(getComputedStyle(e).opacity)<=.001).length,partialRevealTargets:targets.filter(e=>{const o=parseFloat(getComputedStyle(e).opacity);return o>.001&&o<.999}).length}})
 const contrastFindings=await page.evaluate(state=>{
  const reveals=new Set(document.getAnimations().filter(a=>a.effect?.getKeyframes().some(k=>'opacity' in k)).map(a=>a.effect.target))
  const revealPartial=e=>{let opacity=1,animated=false;for(let p=e;p;p=p.parentElement){opacity*=parseFloat(getComputedStyle(p).opacity);animated ||= reveals.has(p)}return state==='mid-reveal'&&animated&&opacity<.999}
  const lum=rgb=>rgb.map(c=>c/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4).reduce((s,c,i)=>s+c*[.2126,.7152,.0722][i],0)
  const paint=e=>{const s=getComputedStyle(e),rgba=s.fill.match(/[\d.]+/g)?.map(Number);if(!rgba||rgba.length<3)return null;return {rgb:rgba.slice(0,3),alpha:(rgba[3]??1)*parseFloat(s.fillOpacity)*parseFloat(s.opacity)}}
  const shapes=[...document.querySelectorAll('rect,circle,ellipse,polygon,path')].filter(e=>{const s=getComputedStyle(e),p=paint(e),b=e.getBoundingClientRect();return p&&p.alpha>0&&b.width>2&&b.height>2&&s.display!=='none'&&!e.closest('defs,marker,clipPath')&&!['wardley-background','background','section'].some(c=>e.classList.contains(c))})
  const contains=(e,x,y)=>{if(typeof e.isPointInFill!=='function')return false;const m=e.getScreenCTM();return m&&e.isPointInFill(new DOMPoint(x,y).matrixTransform(m.inverse()))}
  return [...document.querySelectorAll('text,tspan,foreignObject div,foreignObject span,foreignObject p')].filter(t=>t.textContent.trim()&&![...t.children].some(c=>c.textContent.trim())).flatMap(t=>{
   const b=t.getBoundingClientRect();if(b.width<=0||b.height<=0)return []
   const x=(b.left+b.right)/2,y=(b.top+b.bottom)/2
   const inside=shapes.filter(e=>contains(e,x,y))
   // Compose actual paint-order layers at the label center, including RGBA,
   // fill-opacity, Venn paths and the Cynefin central ellipse.
   const marker=t.closest('.sequenceNumber')?document.querySelector('[id$="-sequencenumber"] circle'):null
   const backing=marker?[marker]:inside
   const shape=backing.at(-1);if(!shape||revealPartial(shape)||revealPartial(t))return []
   let fill=[255,255,255];for(const layer of backing){const p=paint(layer);if(p)fill=p.rgb.map((c,i)=>c*p.alpha+fill[i]*(1-p.alpha))}
   const l=lum(fill);const expected=(l+.05)/.05>=1.05/(l+.05)?'rgb(0, 0, 0)':'rgb(255, 255, 255)'
   const actual=getComputedStyle(t)[t.namespaceURI==='http://www.w3.org/2000/svg'?'fill':'color'];return actual===expected?[]:[{text:t.textContent.slice(0,70),actual,expected,effectiveBacking:fill,fill:getComputedStyle(shape).fill,shapeClass:shape.getAttribute('class'),textClass:t.getAttribute('class'),referencedMarker:!!marker,parentClass:shape.parentElement?.getAttribute('class')}]
  })
 },state)
 const candidates=await page.evaluate(()=>[...document.querySelectorAll('rect,circle,ellipse,polygon,path')].flatMap(e=>{
  const s=getComputedStyle(e);if(['none','transparent'].includes(s.fill))return []
  const parents=[];for(let p=e.parentElement;p&&parents.length<3;p=p.parentElement)parents.push({tag:p.tagName,id:p.id,class:p.getAttribute('class')})
  const box=e.getBoundingClientRect()
  const inner=[...document.querySelectorAll('text,foreignObject')].filter(t=>{const b=t.getBoundingClientRect();return b.width>0&&b.height>0&&b.left>=box.left-1&&b.right<=box.right+1&&b.top>=box.top-1&&b.bottom<=box.bottom+1}).map(t=>({text:t.textContent.slice(0,100),fill:getComputedStyle(t).fill,color:getComputedStyle(t).color}))
  return [{tag:e.tagName,id:e.id,class:e.getAttribute('class'),fill:s.fill,stroke:s.stroke,width:s.strokeWidth,opacity:s.opacity,fillOpacity:s.fillOpacity,overflow:e.getAttribute('data-colorset-overflow'),bounds:{width:box.width,height:box.height},parents,inner}]
 }))
 rows.push({id:item.id??item.patternId??item.family,path:file,state,animationState:{...animationState,...revealMetrics},candidates,contrastFindings})
}
await browser.close();writeFileSync(new URL('native-paints.json',out),JSON.stringify(rows,null,2)+'\n')
for(const row of rows) {
 const rim=row.candidates.filter(e=>e.bounds.width>0&&e.bounds.height>0&&!e.fill.endsWith(', 0)')&&e.stroke!=='none'&&parseFloat(e.width)>0&&e.stroke!==e.fill)
 console.log(JSON.stringify({id:row.id,path:row.path,state:row.state,filled:row.candidates.length,rims:rim.map(({tag,class:c,fill,stroke,width,parents,inner})=>({tag,class:c,fill,stroke,width,parents,inner}))}))
}

const summaries=rows.map(row=>{
 const rims=row.candidates.filter(e=>e.bounds.width>0&&e.bounds.height>0&&!e.fill.endsWith(', 0)')&&e.stroke!=='none'&&parseFloat(e.width)>0&&e.stroke!==e.fill)
 const classified=rims.map(e=>({...e,reason:e.overflow==='true'?'palette-overflow':e.class==='face'||e.class==='mouth'?'journey-emotion-line-art':/\btask\b.*crit/i.test(e.class??'')?'gantt-critical-status':/^wardley-(build|buy|outsource)-overlay$/.test(e.class??'')?'wardley-procurement-overlay':null}))
 return {path:row.path,state:row.state,animationState:row.animationState,filledPaintCount:row.candidates.length,classifiedRims:classified.map(({class:c,reason,fill,stroke,width})=>({class:c,reason,fill,stroke,width})),unexplainedRims:classified.filter(e=>!e.reason),contrastFindings:row.contrastFindings}
})
const summary={passed:summaries.every(r=>r.unexplainedRims.length===0&&r.contrastFindings.length===0),staticFixtures:62,animatedFixtures:62,states:summaries.length,statesCovered:['static','settled','mid-reveal'],contrastPolicy:'Label-center isPointInFill tests include closed filled paths and partial containment. Actual RGBA/fill-opacity layers are composited in paint order over white canvas. Sequence number text is paired explicitly with its referenced marker circle despite zero marker bounds.',revealPolicy:'CSS opacity animation targets/ancestors are sampled at half of the common global end time; partial reveal is intentional and skipped for contrast, while fill-opacity remains a separate paint property. Hidden/partial reveal target counts are recorded for every state.',zeroAreaAndCanvasPolicy:'Zero-area metadata rectangles, transparent/canvas-only layers, and invisible clip geometry are excluded from decorative rim checks.',rows:summaries}
writeFileSync(new URL('native-style-summary.json',out),JSON.stringify(summary,null,2)+'\n')
console.log(JSON.stringify({passed:summary.passed,states:summary.states,unexplainedRims:summaries.reduce((n,r)=>n+r.unexplainedRims.length,0),contrastFindings:summaries.reduce((n,r)=>n+r.contrastFindings.length,0)}))
if(!summary.passed)process.exitCode=1
