#!/usr/bin/env -S npx tsx
// Run: npx tsx projects/diagram-solid-style/scripts/capture-native-review.ts
// Requires tsx and Playwright from the existing ECharts acceptance project.
import { createRequire } from 'node:module'
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
async function main() {
const root=resolve(__dirname,'../../..')
const require=createRequire(resolve(root,'skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json'))
const {chromium}=require('playwright')
const folder=resolve(root,'projects/diagram-solid-style/artifacts/review')
mkdirSync(folder,{recursive:true})
const cases=[
 ['Mermaid CS1: nine roles','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset1/flowchart.static.svg'],
 ['Mermaid CS2: nine roles','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset2/flowchart.static.svg'],
 ['Mermaid CS2: opaque pie','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset2/pie.static.svg'],
 ['Mermaid CS2: event roles','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset2/event-modeling.static.svg'],
 ['Mermaid CS2: Kanban sections','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset2/kanban.static.svg'],
 ['Mermaid CS2: domain fills','skills/mermaid/assets/examples/mermaid-max-complexity/svg/colorset2/cynefin.static.svg'],
 ['PlantUML CS1: components','skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/svg/component.svg'],
 ['PlantUML CS2: components','skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/component.svg'],
 ['PlantUML CS2: activity arrows','skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/activity.svg'],
 ['PlantUML CS2: compartments','skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/class.svg'],
 ['Anime.js: solid dashboard','skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/assets/animated-svg/stagger-dashboard.svg'],
 ['Anime.js: solid badge','skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/assets/animated-svg/morphing-badge.svg'],
]
const cards=cases.map(([title,path])=>`<article><h2>${title}</h2><div><img alt="${title}" src="data:image/svg+xml;base64,${readFileSync(resolve(root,path)).toString('base64')}"></div></article>`).join('')
writeFileSync(resolve(folder,'contact.html'),`<!doctype html><meta charset="utf-8"><title>Native solid style review</title><style>*{box-sizing:border-box}body{margin:0;padding:16px;background:#f7f7f7;font:18px Arial;color:#000000}main{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}article{background:#ffffff;padding:14px;min-width:0;overflow:hidden}h2{font-size:20px;margin:0 0 12px}article div{height:302px;display:flex;align-items:center;justify-content:center}article img{width:100%;height:100%;object-fit:contain}</style><main>${cards}</main>`)
const browser=await chromium.launch({headless:true})
const page=await browser.newPage({viewport:{width:2240,height:1110},deviceScaleFactor:1})
await page.goto(pathToFileURL(resolve(folder,'contact.html')).href)
await page.evaluate(async()=>{await document.fonts.ready;await new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve())))})
await page.screenshot({path:resolve(folder,'native-contact.png'),fullPage:true})
const stats=await page.evaluate(()=>({cards:document.querySelectorAll('article').length,loadedImages:[...document.querySelectorAll('article img')].filter((e)=>e instanceof HTMLImageElement&&e.complete&&e.naturalWidth>0).length,overflow:[...document.querySelectorAll('article')].filter(e=>e.scrollWidth>e.clientWidth+1).length}))
writeFileSync(resolve(folder,'browser-review.json'),JSON.stringify(stats,null,2)+'\n')
await browser.close()
console.log(JSON.stringify(stats))
}
main().catch((error)=>{console.error(error);process.exitCode=1})
