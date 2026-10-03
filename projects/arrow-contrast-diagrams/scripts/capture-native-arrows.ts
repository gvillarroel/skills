// Run: node --experimental-strip-types projects/arrow-contrast-diagrams/scripts/capture-native-arrows.ts
// Dependency: Playwright from the installed acceptance renderer project.
import {createRequire} from 'node:module'
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs'
import {fileURLToPath} from 'node:url'
const root=new URL('../../../',import.meta.url),require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root))
const {chromium}=require('playwright'),browser=await chromium.launch({headless:true})
const out=new URL('projects/arrow-contrast-diagrams/artifacts/screenshots/',root);mkdirSync(out,{recursive:true})
const files=[]
if(process.argv.includes('--runtime')){
 for(const kind of ['static','animated'])files.push({id:`runtime-mermaid-${kind}`,path:`evaluations/runs/arrow-native-mermaid-luna2-20261003/workspace/diagram.${kind}.svg`})
 files.push({id:'runtime-plantuml-deployment',path:'evaluations/runs/arrow-native-plantuml-colorset-renderer-luna2-20261003/workspace/renders/svg/deployment.svg'})
}else if(process.argv.includes('--occlusion')){
 for(const family of ['gitgraph','mindmap','timeline','architecture','wardley'])files.push({id:`occlusion-${family}-colorset2`,path:`skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset2/${family}.static.svg`})
 for(const family of ['ebnf','gantt','regex'])files.push({id:`occlusion-plantuml-${family}-colorset2`,path:`skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/${family}.svg`})
}else{
 for(const cs of ['colorset1','colorset2'])for(const family of ['c4','er','event-modeling','cynefin'])files.push({id:`${family}-${cs}`,path:`skills/mermaid/assets/examples/mermaid-max-complexity/svg/${cs}/${family}.static.svg`})
 files.push({id:'plantuml-deployment-colorset2',path:'skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/deployment.svg'})
}
for(const fixture of files){
 const page=await browser.newPage({viewport:{width:1400,height:1800}})
 await page.goto(new URL(fixture.path,root).href)
 await page.evaluate(()=>{const svg=document.querySelector('svg');svg.style.width='1200px';svg.style.height='auto'})
 await page.evaluate(async()=>{await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))})
 if(process.argv.includes('--runtime'))await page.evaluate(()=>{const animations=document.getAnimations(),end=Math.max(0,...animations.map(a=>a.effect?.getComputedTiming().endTime).filter(Number.isFinite));for(const animation of animations){animation.pause();animation.currentTime=end+1000}})
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))
 const clip=await page.evaluate(()=>{const b=document.querySelector('svg').getBoundingClientRect();return {x:Math.max(0,b.x),y:Math.max(0,b.y),width:b.width,height:b.height}})
 await page.screenshot({path:fileURLToPath(new URL(fixture.id+'.png',out)),clip})
 await page.close()
}
await browser.close();console.log(JSON.stringify({screenshots:files.length}))
