// Run: node --experimental-strip-types projects/arrow-contrast/scripts/review-slidev-routes.ts
// Requires Playwright declared by the owning ECharts acceptance fixture.
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root=new URL('../../../',import.meta.url);
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root));
const {chromium}=require('playwright');
const source=readFileSync(new URL('skills/slidev-echarts/assets/examples/slidev-echarts/slides.md',root),'utf8').replaceAll('\r','');
const sections=source.replace(/^---\n[\s\S]*?\n---\n/,'').split(/\n---\n/);
const slide=sections.findIndex(section=>section.includes('chart-type="lines"'))+1;
const expectedRoutes=JSON.parse(readFileSync(new URL('skills/slidev-echarts/assets/examples/slidev-echarts/data/spatial.json',root),'utf8')).routes.length;
if(!slide)throw Error('No route acceptance slide');
const html=new URL('projects/slidev-echarts-validation/artifacts/html/index.html',root);
const art=new URL('projects/arrow-contrast/artifacts/slidev/',root);mkdirSync(art,{recursive:true});
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1280,height:720}}),errors=[],hostWarnings=[];
page.on('pageerror',error=>{if(error.message==='Wake Lock permission request denied')hostWarnings.push(error.message);else errors.push(error.message);});
const states=[];
for(const motion of ['no-preference','reduce'])for(const step of [0,1])for(const width of [1280,1600]){
 await page.setViewportSize({width,height:Math.round(width*9/16)});await page.emulateMedia({reducedMotion:motion});
 await page.goto(html.href+`#/${slide}?clicks=${step}`);await page.locator('[data-chart-type="lines"]:visible svg').waitFor();
 await page.waitForTimeout(1200);
 const result=await page.locator('[data-chart-type="lines"]:visible svg').evaluate(svg=>{
  const color=s=>{const c=s.match(/[\d.]+/g)?.map(Number);return c?.length>=3?c.slice(0,3):null;};
  const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
  const alpha=e=>{let a=1;for(let p=e;p;p=p.parentElement)a*=Number(getComputedStyle(p).opacity);return a;};
  const all=[...svg.querySelectorAll('path')],heads=all.filter(e=>/^M0 0L/.test(e.getAttribute('d'))&&getComputedStyle(e).fill!=='none');
  const shafts=all.filter(e=>/[Qq]/.test(e.getAttribute('d'))&&getComputedStyle(e).fill==='none'&&getComputedStyle(e).stroke!=='none');
  const bodies=[...svg.querySelectorAll('path,rect,circle,polygon')].filter(e=>!e.closest('defs')&&!heads.includes(e)&&color(getComputedStyle(e).fill));
  const surface=(p,owner)=>{let bg=[255,255,255],covered=[];for(const body of bodies){if(body===owner||!body.isPointInFill(p.matrixTransform(body.getScreenCTM().inverse())))continue;const s=getComputedStyle(body),c=color(s.fill),a=alpha(body)*Number(s.fillOpacity);bg=bg.map((v,i)=>v*(1-a)+c[i]*a);if(body.tagName!=='rect')covered.push(body.tagName);}return {bg,covered};};
  const records=[];
  for(const [kind,elements] of [['shaft',shafts],['head',heads]])for(const e of elements){const css=getComputedStyle(e),paint=color(css[kind==='shaft'?'stroke':'fill']),a=alpha(e)*Number(css[kind==='shaft'?'strokeOpacity':'fillOpacity']),samples=[];
   if(kind==='shaft'){const length=e.getTotalLength();for(const f of [.12,.32,.5,.68,.88])samples.push(e.getPointAtLength(length*f).matrixTransform(e.getScreenCTM()));}
   else{const b=e.getBBox();for(const u of [.2,.4,.6,.8])for(const v of [.2,.4,.6,.8]){const p=new DOMPoint(b.x+b.width*u,b.y+b.height*v);if(e.isPointInFill(p))samples.push(p.matrixTransform(e.getScreenCTM()));}}
   const points=samples.map(p=>{const b=surface(p,e);return {contrast:ratio(paint.map((v,i)=>v*a+b.bg[i]*(1-a)),b.bg),...b};});
   records.push({kind,paint:css[kind==='shaft'?'stroke':'fill'],effectiveOpacity:a,width:css.strokeWidth,minimumContrast:Math.min(...points.map(p=>p.contrast)),points});}
  return {shaftCount:shafts.length,headCount:heads.length,records};
 });
 const id=`${motion}-${step}-${width}`;await page.screenshot({path:fileURLToPath(new URL(id+'.png',art))});
 states.push({id,motion,step,width,...result,passed:result.shaftCount===expectedRoutes&&result.headCount===expectedRoutes&&result.records.every(r=>r.minimumContrast>=3&&r.points.every(p=>p.covered.length===0))});
}
await browser.close();
const widths=states.filter(s=>s.width===1280&&s.motion==='no-preference').map(s=>s.records.filter(r=>r.kind==='shaft').map(r=>r.width));
const clickChange=JSON.stringify(widths[0])!==JSON.stringify(widths[1]);
const report={date:'2026-10-03',passed:errors.length===0&&clickChange&&states.every(s=>s.passed),slide,expectedRoutes,errors,hostWarnings,clickChange,states,
 scope:'Actual built offline Slidev route slide: click states0/1, resize1280/1600, normal/reduced motion, native curved arrow heads outside radius4 targets. Browser SVG geometry/composite check; antialias edge pixels are not categorical paint.',
 probeRepair:'Initial probe guessed3routes but the fixture has4. Raw failed scan is retained under projects/arrow-contrast/artifacts/slidev/initial-probe.json. Exact offline Wake Lock permission denial is a host warning and does not change arrow paint or geometry; all other page errors fail.'};
writeFileSync(new URL('evaluations/arrow-contrast/slidev-routes-20261003.json',root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,slide,expectedRoutes,states:states.length,errors,hostWarnings,clickChange,failures:states.filter(s=>!s.passed).map(s=>({id:s.id,shafts:s.shaftCount,heads:s.headCount}))},null,2));
if(!report.passed)process.exitCode=1;
