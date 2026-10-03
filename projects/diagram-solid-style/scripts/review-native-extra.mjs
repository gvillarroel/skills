// Run: node projects/diagram-solid-style/scripts/review-native-extra.mjs
import {createRequire} from 'node:module'
import {writeFileSync,mkdirSync} from 'node:fs'
import {fileURLToPath} from 'node:url'
const root=new URL('../../../',import.meta.url)
const require=createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root))
const {chromium}=require('playwright')
const out=new URL('projects/diagram-solid-style/artifacts/review/',root);mkdirSync(out,{recursive:true})
const browser=await chromium.launch({headless:true})
const page=await browser.newPage({viewport:{width:1900,height:1500}})
const results=[]
for(const [id,path] of [
 ['mermaid-c4-cs1','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset1/c4.static.svg'],
 ['plantuml-deployment-cs2','skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/deployment.svg'],
]) {
 await page.goto(new URL(path,root).href)
 await page.evaluate(async()=>{await document.fonts.ready;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))})
 await page.locator('svg').first().screenshot({path:fileURLToPath(new URL(id+'.png',out))})
 const paints=await page.evaluate(()=>[...document.querySelectorAll('rect,circle,ellipse,polygon,path')].map(e=>{const s=getComputedStyle(e);return {tag:e.tagName,id:e.id,class:e.getAttribute('class'),fill:s.fill,stroke:s.stroke,strokeWidth:s.strokeWidth,fillOpacity:s.fillOpacity,opacity:s.opacity}}))
 results.push({id,path,paintCount:paints.length,paints})
}
await browser.close()
writeFileSync(new URL('extra-native-review.json',out),JSON.stringify(results,null,2)+'\n')
console.log(JSON.stringify(results.map(({id,path,paintCount})=>({id,path,paintCount}))))
