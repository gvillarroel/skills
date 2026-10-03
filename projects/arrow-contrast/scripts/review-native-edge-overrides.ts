// Run: node --experimental-strip-types projects/arrow-contrast/scripts/review-native-edge-overrides.ts --phase final
// To reproduce a retained baseline, add --phase before --module <immutable-helper-path>.
// Dependencies: ECharts and Playwright from the existing acceptance renderer package.
import {createRequire} from 'node:module'
import {createHash} from 'node:crypto'
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs'
import {fileURLToPath,pathToFileURL} from 'node:url'
import {resolve} from 'node:path'
const root=new URL('../../../',import.meta.url),args=process.argv.slice(2)
const value=flag=>args.includes(flag)?args[args.indexOf(flag)+1]:undefined
const phase=value('--phase')??'final';if(!['before','final'].includes(phase))throw Error('Use --phase before|final')
const helperPath=value('--module')?pathToFileURL(resolve(value('--module'))):new URL('skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs',root)
const helper=await import(helperPath.href),helperSha256=createHash('sha256').update(readFileSync(helperPath)).digest('hex')
const slidevHelperSha256=createHash('sha256').update(readFileSync(new URL('skills/slidev-echarts/assets/templates/echarts-colorsets.mjs',root))).digest('hex')
if(phase==='final'&&helperSha256!==slidevHelperSha256)throw Error('Final helper copies must be byte-identical')
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root)),echarts=require('echarts'),{chromium}=require('playwright')
const out=new URL(`projects/arrow-contrast/artifacts/reviews/edge-overrides-${phase}/`,root);mkdirSync(out,{recursive:true})
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:400,height:280}})
const base={backgroundColor:'#ffffff',animation:false,xAxis:{min:0,max:1},yAxis:{min:0,max:1}}
const line=(effect,edge={})=>({...base,series:[{type:'lines',coordinateSystem:'cartesian2d',symbol:'none',lineStyle:{color:'#cfcfcf',opacity:.25},effect:{show:true,symbol:'arrow',symbolSize:16,period:1,delay:0,trailLength:0,...effect},data:[{coords:[[0,.2],[1,.8]],...edge}]}]})
const mark=(symbol,terminalStyle={})=>({...base,series:[{type:'line',symbol:'none',lineStyle:{opacity:0},data:[[0,0],[1,1]],markLine:{...(symbol===undefined?{}:{symbol}),lineStyle:{color:'#cfcfcf',opacity:.25},data:[[{coord:[0,.2],symbol:'circle',...terminalStyle},{coord:[1,.8],symbol:'arrow',...terminalStyle}]]}}]})
const cases=[
 {id:'markline-terminal-none',option:mark('none'),ssr:true},
 {id:'markline-terminal-array',option:mark(['circle','none']),ssr:true},
 {id:'markline-terminal-itemstyle',option:mark(undefined,{itemStyle:{color:'#ffffff',opacity:.1}}),ssr:true},
 {id:'effect-default-color',option:line({})},
 {id:'effect-inherited-show',option:line({},{effect:{color:'#cfcfcf'}})},
 {id:'effect-edge-show-false',option:line({},{effect:{show:false,color:'#cfcfcf'}})},
 {id:'effect-series-opacity',option:line({color:'#000000',opacity:.1})},
 {id:'effect-edge-opacity',option:line({},{effect:{color:'#000000',opacity:.1}})},
]
const signature=series=>JSON.stringify(series.map(s=>({symbol:s.symbol,effectShow:s.effect?.show,effectSymbol:s.effect?.symbol,edgeShow:s.data?.map(e=>e.effect?.show),edgeSymbol:s.data?.map(e=>e.effect?.symbol),markSymbol:s.markLine?.symbol,terminalSymbols:s.markLine?.data?.map(pair=>pair.map(e=>e.symbol))})))
const states=[]
for(const colorset of ['colorset1','colorset2'])for(const test of cases)for(const mode of test.ssr?['ssr','client']:['client']){
 const original=structuredClone(test.option),option=helper.prepareColorsetOption(structuredClone(original),colorset),flagsPreserved=signature(original.series)===signature(option.series)
 const id=`${colorset}-${test.id}-${mode}`
 if(mode==='ssr'){
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:400,height:280});chart.setOption(option)
  const svg=chart.renderToSVGString();chart.dispose();const path=new URL(id+'.svg',out);writeFileSync(path,svg);await page.goto(path.href)
 }else{
  await page.goto('about:blank')
  await page.setContent('<html><body style="margin:0;background:white"><div id="chart" style="width:400px;height:280px"></div></body></html>')
  await page.addScriptTag({path:fileURLToPath(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/node_modules/echarts/dist/echarts.js',root))})
  await page.evaluate(option=>{window.reviewChart=echarts.init(document.querySelector('#chart'),null,{renderer:'svg'});window.reviewChart.setOption(option)},option)
  await page.waitForTimeout(350)
 }
 await page.evaluate(async()=>{await document.fonts.ready;await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))})
 const records=await page.evaluate(()=>{
  const lum=rgb=>rgb.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0)
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05)
  const effectiveOpacity=e=>{let result=1;for(let p=e;p;p=p.parentElement)result*=Number(getComputedStyle(p).opacity);return result}
  return [...document.querySelectorAll('path')].filter(p=>!p.closest('defs')).flatMap(p=>{
   const css=getComputedStyle(p),head=css.fill!=='none',opacity=effectiveOpacity(p)*Number(head?css.fillOpacity:css.strokeOpacity)
   if(opacity<=0)return []
   if(!head){if(css.stroke==='none')return [];const length=p.getTotalLength(),a=p.getPointAtLength(0),b=p.getPointAtLength(length);if(length<200||Math.abs(a.x-b.x)<50||Math.abs(a.y-b.y)<50)return []}
   const paint=head?css.fill:css.stroke,channels=paint.match(/[\d.]+/g)?.slice(0,3).map(Number)
   if(!channels)return []
   return [{part:head?'head':'shaft',path:p.getAttribute('d'),paint,opacity,contrast:ratio(channels.map(v=>v*opacity+255*(1-opacity)),[255,255,255])}]
  })
 })
 const svg=await page.evaluate(()=>document.querySelector('svg').outerHTML);writeFileSync(new URL(id+'.svg',out),svg)
 await page.screenshot({path:fileURLToPath(new URL(id+'.png',out))})
 if(mode==='client')await page.evaluate(()=>window.reviewChart.dispose())
 states.push({id,colorset,case:test.id,mode,flagsPreserved,shaftCount:records.filter(r=>r.part==='shaft').length,headCount:records.filter(r=>r.part==='head').length,minimumShaftContrast:Math.min(...records.filter(r=>r.part==='shaft').map(r=>r.contrast)),minimumHeadContrast:Math.min(...records.filter(r=>r.part==='head').map(r=>r.contrast)),glyphPaths:records.filter(r=>r.part==='head').map(r=>r.path).sort(),records,passed:flagsPreserved&&records.some(r=>r.part==='shaft')&&records.some(r=>r.part==='head')&&records.every(r=>r.contrast>=3)})
}
await browser.close()
const report={date:'2026-10-03',phase,helperSha256,slidevHelperSha256,scope:'Finite native markLine endpoint overrides and actual client moving effect color/show/opacity inheritance on a white declared canvas, both palettes. Ordinary Cartesian axes; no custom symbols or region crossings.',passed:states.every(s=>s.passed),states}
writeFileSync(new URL('report.json',out),JSON.stringify(report,null,2)+'\n')
if(phase==='final'){
 const before=JSON.parse(readFileSync(new URL('projects/arrow-contrast/artifacts/reviews/edge-overrides-before/report.json',root),'utf8'))
 const rows=states.map(after=>{const prior=before.states.find(s=>s.id===after.id);return {id:after.id,colorset:after.colorset,mode:after.mode,beforePassed:prior?.passed,afterPassed:after.passed,flagsPreserved:after.flagsPreserved,glyphGeometryPreserved:JSON.stringify(prior?.glyphPaths)===JSON.stringify(after.glyphPaths),beforeShaftContrast:prior?.minimumShaftContrast,afterShaftContrast:after.minimumShaftContrast,beforeHeadContrast:prior?.minimumHeadContrast,afterHeadContrast:after.minimumHeadContrast}})
 const compact={date:'2026-10-03',beforeHelperSha256:before.helperSha256,finalHelperSha256:helperSha256,finalHelperCopiesIdentical:helperSha256===slidevHelperSha256,statesPerPhase:states.length,baselineFailureStates:rows.filter(r=>!r.beforePassed).length,finalFailureStates:rows.filter(r=>!r.afterPassed).length,passed:report.passed&&rows.every(r=>r.flagsPreserved&&r.glyphGeometryPreserved),scope:report.scope,states:rows}
 writeFileSync(new URL('evaluations/arrow-contrast-diagrams/echarts-overrides-20261003.json',root),JSON.stringify(compact,null,2)+'\n')
 console.log(JSON.stringify({phase,helperSha256,states:states.length,passed:compact.passed,failureStates:compact.finalFailureStates,baselineFailureStates:compact.baselineFailureStates}))
 if(!compact.passed)process.exitCode=1
}else console.log(JSON.stringify({phase,helperSha256,states:states.length,expectedFailureStates:states.filter(s=>!s.passed).length}))
