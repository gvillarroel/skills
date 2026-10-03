// Run: npx tsx projects/solid-colorset-style/scripts/review-native-mermaid.ts
// Requires tsx and Playwright; use the installed acceptance fixture dependency runtime.
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
async function main() {
const root=pathToFileURL(process.cwd()+'/');
const artifactRoot=new URL('projects/solid-colorset-style/artifacts/',root);
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root));
const {chromium}=require('playwright');
const gallery=new URL('skills/mermaid/assets/examples/mermaid-max-complexity/',root);
const manifest=JSON.parse(readFileSync(new URL('gallery.json',gallery),'utf8'));
const browser=await chromium.launch({headless:true});
try {
const page=await browser.newPage({viewport:{width:1800,height:1500}});
const rows=[];
const hash=url=>createHash('sha256').update(readFileSync(url)).digest('hex');
const initial=Object.fromEntries(manifest.patterns.map(item=>[item.staticSvg,hash(new URL(item.staticSvg,gallery))]));
for(const item of manifest.patterns) {
 await page.goto(new URL(item.staticSvg,gallery).href);
 await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))});
 const review=await page.evaluate(String.raw`(() => {
  const leaf=[...document.querySelectorAll('text,tspan,foreignObject div,foreignObject span,foreignObject p')].filter(e=>e.textContent.trim()&&!Array.from(e.children).some(c=>c.textContent.trim()));
  const rgb=s=>s.match(/[\d.]+/g)?.map(Number);
  const lum=a=>a.map(c=>c/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4).reduce((s,c,i)=>s+c*[.2126,.7152,.0722][i],0);
  const findings=[];
  const outsideActorFindings=[];
  const rims=[...document.querySelectorAll('rect,circle,ellipse,polygon,path')].flatMap(e=>{
   const s=getComputedStyle(e),b=e.getBoundingClientRect(),alpha=(rgb(s.fill)?.[3]??1)*parseFloat(s.fillOpacity)*parseFloat(s.opacity);
   if(!b.width||!b.height||s.fill==='none'||alpha===0||s.stroke==='none'||parseFloat(s.strokeWidth)===0||s.stroke===s.fill||e.closest('marker'))return [];
   const c=e.getAttribute('class')??'';
   const reason=e.getAttribute('data-colorset-overflow')==='true'?'palette-overflow':['face','mouth'].includes(c)?'journey-emotion-line-art':/\btask\b.*crit/i.test(c)?'gantt-critical-status':/^wardley-(build|buy|outsource)-overlay$/.test(c)?'wardley-procurement-overlay':null;
   return [{tag:e.tagName,class:c,fill:s.fill,stroke:s.stroke,width:s.strokeWidth,reason}];
  });
  const fills=[...document.querySelectorAll('rect,circle,ellipse,polygon,path')].filter(e=>{const s=getComputedStyle(e),b=e.getBoundingClientRect();return s.fill!=='none'&&b.width>2&&b.height>2&&!e.closest('marker')&&s.display!=='none'&&(rgb(s.fill)?.[3]??1)>0});
  for(const text of leaf) {
   const b=text.getBoundingClientRect();if(!b.width||!b.height)continue;
   const center=new DOMPoint((b.left+b.right)/2,(b.top+b.bottom)/2);
   const numberMarker=text.closest('.sequenceNumber')?document.querySelector('marker[id$="sequencenumber"] circle'):null;
   const backing=numberMarker??fills.filter(e=>{
    const a=e.getBoundingClientRect();if(!(center.x>=a.left&&center.x<=a.right&&center.y>=a.top&&center.y<=a.bottom))return false;
    try{return e.isPointInFill(center.matrixTransform(e.getScreenCTM().inverse()))}catch{return false}
   }).sort((a,c)=>a.getBoundingClientRect().width*a.getBoundingClientRect().height-c.getBoundingClientRect().width*c.getBoundingClientRect().height)[0];
   if(!backing||['background','wardley-background','section'].some(c=>backing.classList.contains(c)))continue;
   const s=getComputedStyle(backing),rgba=rgb(s.fill);if(!rgba||rgba.length<3)continue;
   const alpha=(rgba[3]??1)*parseFloat(s.fillOpacity)*parseFloat(s.opacity);
   const composed=rgba.slice(0,3).map(c=>alpha*c+(1-alpha)*255),l=lum(composed);
   const expected=(l+.05)/.05>=1.05/(l+.05)?'rgb(0, 0, 0)':'rgb(255, 255, 255)';
   const actual=getComputedStyle(text)[text.namespaceURI==='http://www.w3.org/2000/svg'?'fill':'color'];
   if(actual!==expected)findings.push({text:text.textContent.trim(),tag:text.tagName,textClass:text.getAttribute('class'),actual,expected,backingTag:backing.tagName,backingClass:backing.getAttribute('class'),markerBacking:Boolean(numberMarker),fill:s.fill,fillOpacity:s.fillOpacity,textBounds:{x:b.x,y:b.y,width:b.width,height:b.height}});
  }
  for(const group of document.querySelectorAll('.actor-man'))for(const text of group.querySelectorAll('text,tspan')) {
   if(Array.from(text.children).some(c=>c.textContent.trim())||!text.textContent.trim())continue;
   const actual=getComputedStyle(text).fill;
   if(actual!=='rgb(0, 0, 0)')outsideActorFindings.push({text:text.textContent.trim(),actual,expected:'rgb(0, 0, 0)',reason:'native stick-man caption lies outside filled head/body on white or pale control-region backing'});
  }
  return {leafCount:leaf.length,filledCount:fills.length,findings,outsideActorFindings,classifiedRims:rims.filter(r=>r.reason),unexplainedRims:rims.filter(r=>!r.reason)};
 })()`);
 rows.push({id:item.id??item.patternId??item.family,path:item.staticSvg,...review});
}
for(const family of ['sequence','venn','radar','cynefin']) {
 await page.goto(new URL(`svg/colorset1/${family}.static.svg`,gallery).href);
 await page.locator('svg').screenshot({path:fileURLToPath(new URL(`composition-native-${family}-review.png`,artifactRoot))});
}
writeFileSync(new URL('composition-native-label-review.json',artifactRoot),JSON.stringify(rows,null,2)+'\n');
const final=Object.fromEntries(manifest.patterns.map(item=>[item.staticSvg,hash(new URL(item.staticSvg,gallery))]));
const changedPaths=Object.keys(initial).filter(path=>initial[path]!==final[path]);
writeFileSync(new URL('composition-native-label-review-meta.json',artifactRoot),JSON.stringify({checkedAtUtc:new Date().toISOString(),staticCount:rows.length,stable:changedPaths.length===0,changedPaths,initialHashes:initial,finalHashes:final,contrastFindings:rows.reduce((n,row)=>n+row.findings.length,0),outsideActorFindings:rows.reduce((n,row)=>n+row.outsideActorFindings.length,0),unexplainedRims:rows.reduce((n,row)=>n+row.unexplainedRims.length,0),classifiedRims:rows.reduce((n,row)=>n+row.classifiedRims.length,0),method:'Actual computed leaf paint against native filled shape at text center via isPointInFill; excludes background/stage layers; explicit sequenceNumber-marker paint pairing; independently checks actor-man captions outside filled body; alpha composed over published white canvas. Contrasting filled rims are classified only for explicit palette overflow, journey emotion glyphs, critical status and procurement glyphs.'},null,2)+'\n');
console.log(JSON.stringify(rows.filter(r=>r.findings.length).map(({id,findings})=>({id,findings})),null,2));
if(changedPaths.length||rows.some(row=>row.findings.length||row.outsideActorFindings.length||row.unexplainedRims.length))throw new Error('Native Mermaid acceptance failed; inspect artifact reports.');
} finally {await browser.close();}
}
main().catch(error=>{console.error(error);process.exitCode=1});
