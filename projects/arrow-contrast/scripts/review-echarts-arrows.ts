// Run with Node's TypeScript runner: node --experimental-strip-types projects/arrow-contrast/scripts/review-echarts-arrows.ts --phase before|final
// Uses ECharts and Playwright declared by the owning acceptance fixture package.
import {createRequire} from 'node:module';
import {mkdirSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {prepareColorsetOption,insetCartesianArrowRoutes} from '../../../skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs';
const root=new URL('../../../',import.meta.url);
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root));
const echarts=require('echarts'),{chromium}=require('playwright');
const phase=process.argv[process.argv.indexOf('--phase')+1];
if(!['before','final'].includes(phase))throw Error('Pass --phase before or final');
const artifacts=new URL(`projects/arrow-contrast/artifacts/echarts-${phase}/`,root);
mkdirSync(artifacts,{recursive:true});
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:560,height:280}});
const states=[];
for(const colorset of ['colorset1','colorset2'])for(const background of ['#ffffff','#f7f7f7'])for(const family of (phase==='final'?['graph','routes']:['graph'])){
 let option=prepareColorsetOption(family==='graph'?{backgroundColor:background,animation:false,
  series:[{type:'graph',layout:'none',symbolSize:60,edgeSymbol:['none','arrow'],edgeSymbolSize:16,
   data:[{id:'a',name:'Origin',x:100,y:100},{id:'b',name:'Target',x:400,y:100}],
   links:[{source:'a',target:'b',lineStyle:{color:'#cfcfcf',opacity:.25}}],
   label:{show:true},lineStyle:{color:'#cfcfcf',opacity:.25},
   emphasis:{lineStyle:{opacity:.25}},blur:{lineStyle:{opacity:.25}}}]}:{backgroundColor:background,animation:false,
   grid:{top:56,right:28,bottom:38,left:44},xAxis:{min:0,max:70},yAxis:{min:0,max:90},
   series:[{type:'lines',coordinateSystem:'cartesian2d',symbol:['circle','arrow'],symbolSize:[5,11],lineStyle:{color:'#007298',curveness:.18,opacity:.72},
    data:[{coords:[[0,22],[28,44]]},{coords:[[28,44],[62,58]]},{coords:[[8,15],[18,78]]}]},
    {type:'scatter',symbolSize:8,data:[[0,22],[28,44],[62,58],[18,78],[8,15]]}]},colorset);
 const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:560,height:280});
 chart.setOption(option);
 if(family==='routes'){option=insetCartesianArrowRoutes(option,chart,7);chart.setOption(option);}
 const text=chart.renderToSVGString();chart.dispose();
 const id=colorset+'-'+background.slice(1)+(family==='routes'?'-routes':''),svg=new URL(id+'.svg',artifacts);
 writeFileSync(svg,text);
 await page.goto(svg.href);await page.evaluate(()=>document.fonts.ready);
 const measured=await page.evaluate(()=>{
  const svg=document.querySelector('svg');
  const rgb=s=>s.match(/[\d.]+/g)?.slice(0,3).map(Number);
  const lum=c=>c.map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4).reduce((sum,x,i)=>sum+x*[.2126,.7152,.0722][i],0);
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
  const filled=[...svg.querySelectorAll('path,circle,rect')].filter(e=>!e.closest('defs')&&getComputedStyle(e).fill!=='none');
  const paths=[...svg.querySelectorAll('path')].filter(e=>!e.closest('defs'));
  const heads=paths.filter(e=>{const b=e.getBoundingClientRect();return e.getAttribute('ecmeta_series_index')==='0'&&getComputedStyle(e).fill!=='none'&&b.width<=25&&b.height<=25&&!/[Aa]/.test(e.getAttribute('d'));});
  const shafts=paths.filter(e=>e.getAttribute('ecmeta_series_index')==='0'&&getComputedStyle(e).fill==='none'&&getComputedStyle(e).stroke!=='none');
  const alpha=e=>{let a=1;for(let p=e;p;p=p.parentElement)a*=Number(getComputedStyle(p).opacity);return a;};
  const inside=(e,p)=>e.isPointInFill(p.matrixTransform(e.getScreenCTM().inverse()));
  function localBacking(p,owner){let backing=[255,255,255],covered=[];for(const e of filled){if(e===owner||heads.includes(e)||!inside(e,p))continue;const css=getComputedStyle(e),c=rgb(css.fill),a=alpha(e)*Number(css.fillOpacity);backing=backing.map((v,i)=>v*(1-a)+c[i]*a);if(e.tagName!=='rect')covered.push(e.tagName);}return {backing,covered};}
  const records=[];
  for(const shaft of shafts){const css=getComputedStyle(shaft),paint=rgb(css.stroke),length=shaft.getTotalLength(),a=alpha(shaft)*Number(css.strokeOpacity),points=[];
   for(const f of [.1,.3,.5,.7,.9]){const p=shaft.getPointAtLength(length*f).matrixTransform(shaft.getScreenCTM()),b=localBacking(p,shaft);points.push({ratio:ratio(paint.map((v,i)=>v*a+b.backing[i]*(1-a)),b.backing),...b});}
   records.push({part:'shaft',paint:css.stroke,effectiveOpacity:a,minimumContrast:Math.min(...points.map(p=>p.ratio)),points});}
  for(const head of heads){const css=getComputedStyle(head),paint=rgb(css.fill),box=head.getBBox(),a=alpha(head)*Number(css.fillOpacity),points=[];
   for(const u of [.2,.4,.6,.8])for(const v of [.2,.4,.6,.8]){const p=new DOMPoint(box.x+box.width*u,box.y+box.height*v);if(!head.isPointInFill(p))continue;const b=localBacking(p.matrixTransform(head.getScreenCTM()),head);points.push({ratio:ratio(paint.map((x,i)=>x*a+b.backing[i]*(1-a)),b.backing),...b});}
   records.push({part:'head',paint:css.fill,effectiveOpacity:a,minimumContrast:Math.min(...points.map(p=>p.ratio)),points});}
  return {shaftCount:shafts.length,headCount:heads.length,records};
 });
 await page.screenshot({path:fileURLToPath(new URL(id+'.png',artifacts))});
 states.push({id,family,colorset,background,artifact:fileURLToPath(svg).replace(fileURLToPath(root),'').replaceAll('\\','/'),
  preparedLinks:option.series[0].links,preparedLineStyle:option.series[0].lineStyle,...measured,
  passed:measured.shaftCount===(family==='graph'?1:3)&&measured.headCount===(family==='graph'?1:3)&&measured.records.every(r=>r.minimumContrast>=3&&r.points.every(p=>p.covered.length===0))});
}
await browser.close();
const report={date:'2026-10-03',phase,passed:states.every(s=>s.passed),states,
 scope:'Independent native ECharts SSR graph and curved continuous Cartesian lines: explicit pale low-alpha edge input, actual filled arrowhead geometry and shaft paint on white/quiet canvases in both palettes. Cartesian tips are inset outside radius-four endpoint marks. Arbitrary custom renderers and filled route crossings require their own actual-backing inspection.'};
const out=new URL(`evaluations/arrow-contrast/echarts-${phase}-20261003.json`,root);
writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({phase,passed:report.passed,states:states.length,minima:states.map(s=>s.records.map(r=>({part:r.part,minimum:r.minimumContrast})))},null,2));
if(phase==='final'&&!report.passed)process.exitCode=1;
