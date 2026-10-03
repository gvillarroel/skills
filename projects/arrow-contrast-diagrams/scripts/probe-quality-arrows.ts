// Run: node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/probe-quality-arrows.ts
// Dependencies: existing acceptance deck's Playwright and TypeScript; no skill runtime dependency.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {createRequire} from 'node:module'
const root=new URL('../../../',import.meta.url)
const require=createRequire(new URL('skills/slidev-echarts/assets/examples/slidev-echarts/package.json',root))
const {chromium}=require('playwright'),ts=require('typescript')
const source=readFileSync(new URL('skills/slidev-quality-audit/scripts/audit-slidev-quality.ts',root),'utf8')
const code=source.slice(source.indexOf('async function inspectState('),source.indexOf('async function parseSlides('))
const inspect=eval(ts.transpileModule(code+'\ninspectState',{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText)
const options={minFontSize:10,minContrast:4.5,largeTextContrast:3,overflowTolerance:3,safeMargin:0,overlapRatio:.2,maxWords:300,maxTextBlocks:30,ignoreSelector:'[data-ignore]',allowOverflowSelector:'[data-allow-overflow]',allowHiddenSelector:'[data-allow-hidden]',colorset:'colorset1',paletteColors:['#ffffff','#000000','#9e1b32','#828282','#cfcfcf','#696969']}
const marker=(paint,extra='')=>`<defs><marker id="head" markerUnits="userSpaceOnUse" viewBox="0 0 10 10" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto" ${extra}><polygon points="0,0 10,5 0,10" fill="${paint}"/></marker></defs>`
const line=(paint,extra='')=>`<path data-arrow-id="review-edge" d="M80 130L320 130" fill="none" stroke="${paint}" stroke-width="3" ${extra}/>`
const cases=[
 {id:'low-shaft',svg:line('#cfcfcf'),rules:['arrow-low-contrast']},
 {id:'low-head',svg:marker('#ffffff')+line('#000000','marker-end="url(#head)"'),rules:['arrow-low-contrast']},
 {id:'safe-head-shaft',svg:marker('#000000')+line('#000000','marker-end="url(#head)"'),rules:[]},
 {id:'dark-filled-path',svg:'<path d="M40 40H360V220H40Z" fill="#9e1b32"/>'+marker('#ffffff')+line('#ffffff','marker-end="url(#head)"'),rules:[]},
 {id:'alpha-region',svg:'<path d="M40 40H360V220H40Z" fill="rgba(0,0,0,.2)"/>'+line('#828282'),rules:['arrow-low-contrast']},
 {id:'alpha-shaft',svg:line('#000000','stroke-opacity=".2"'),rules:['arrow-low-contrast']},
 {id:'alpha-canvas',canvas:'rgba(0,0,0,.25)',svg:line('#828282'),rules:['arrow-low-contrast']},
 {id:'covered-head',svg:marker('#000000')+line('#000000','marker-end="url(#head)"')+'<rect x="307" y="115" width="40" height="30" fill="#9e1b32"/>',rules:['arrowhead-covered']},
 {id:'transformed-instance',svg:marker('#000000')+'<g transform="translate(10 5) rotate(3 80 130)">'+line('#000000','marker-end="url(#head)"')+'</g>',rules:[]},
 {id:'solid-explicit-head',svg:'<polygon data-arrow-id="head-only" points="290,120 310,130 290,140" fill="#ffffff"/>',rules:['arrow-low-contrast']},
]
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1024,height:768}}),results=[]
const errors=[];page.on('pageerror',error=>errors.push(String(error)))
for(const test of cases){
 await page.setContent(`<style>body{margin:0;background:white}.slidev-layout{width:800px;height:600px;background:${test.canvas??'white'};padding:20px;box-sizing:border-box}svg{width:400px;height:260px}</style><div class="slidev-layout"><h1>Arrow review</h1><svg viewBox="0 0 400 260">${test.svg}</svg></div>`)
 const inspection=await inspect(page,options)
 const actual=[...new Set(inspection.findings.map(f=>f.ruleId).filter(id=>id.startsWith('arrow')))].sort()
 const expected=[...test.rules].sort(),passed=JSON.stringify(actual)===JSON.stringify(expected)
 results.push({id:test.id,passed,expected,actual,findings:inspection.findings.filter(f=>f.ruleId.startsWith('arrow'))})
}
await browser.close()
const out=new URL('projects/arrow-contrast-diagrams/artifacts/',root);mkdirSync(out,{recursive:true})
writeFileSync(new URL('quality-arrow-probe.json',out),JSON.stringify({passed:results.every(r=>r.passed)&&errors.length===0,errors,results},null,2)+'\n')
console.log(JSON.stringify({cases:results.length,passed:results.every(r=>r.passed),errors,failures:results.filter(r=>!r.passed)}))
if(results.some(r=>!r.passed)||errors.length)process.exitCode=1
