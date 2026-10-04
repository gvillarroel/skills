#!/usr/bin/env node
// Read-only publication audit. Run: node --experimental-strip-types projects/colorset-priority/scripts/audit_public_echarts.ts --expected-ref <commit>
import { execFileSync } from 'node:child_process'
import { readFile, mkdir, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { createHash } from 'node:crypto'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..')
const arg = key => process.argv.includes(key) ? process.argv[process.argv.indexOf(key) + 1] : null
const expectedRef = arg('--expected-ref')
const preview = arg('--preview-file')
if (!preview && !/^[a-f0-9]{40}$/.test(expectedRef || '')) throw new Error('Provide the exact full release commit SHA')
const source = 'skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html'
const url = arg('--url') || 'https://gvillarroel.github.io/skills/examples/echarts-animated-svg/'
const output = resolve(root, 'projects/colorset-priority/artifacts/reviews', preview ? 'echarts-public-preview' : `echarts-public-${expectedRef.slice(0,12)}`)
await mkdir(output, { recursive: true })
const sha = bytes => createHash('sha256').update(bytes).digest('hex')
const committed = preview ? await readFile(resolve(root, preview)) : execFileSync('git', ['show', `${expectedRef}:${source}`], { cwd: root })
const expected = preview ? Buffer.from(committed.toString('utf8').split(/\r?\n/).map(line => line.trimEnd()).join('\n').replace(/\n*$/, '\n')) : execFileSync('uv', ['run', '--script', 'projects/colorset-priority/scripts/verify_publication.py', '--expected-ref', expectedRef, '--emit-expected', source], { cwd: root, maxBuffer: 2*1024*1024 })
const response = preview ? null : await fetch(url + '?release=' + expectedRef)
const published = preview ? committed : Buffer.from(await response.arrayBuffer())
const findings = []
if (!preview && (!response.ok || !published.equals(expected))) findings.push({ message: 'Published ECharts gallery bytes differ from the exact committed Pages resource', status: response.status, expectedSha256: sha(expected), observedSha256: sha(published) })
const paletteSource = preview ? await readFile(resolve(root, 'skills/echarts-animated-svg/assets/palettes/colorsets.json')) : execFileSync('git', ['show', `${expectedRef}:skills/echarts-animated-svg/assets/palettes/colorsets.json`], { cwd: root })
const palette = [...new Set(paletteSource.toString('utf8').match(/#[0-9a-fA-F]{6}/g).map(value => value.toLowerCase()))]
const { chromium } = await import(pathToFileURL(resolve(root, 'skills/echarts-animated-svg/assets/examples/echarts-animated-svg/node_modules/playwright/index.mjs')))
const browser = await chromium.launch({ headless: true })
const states = []
const values = [[12,18,24,30,38],[10,16,22,28,34],[14,20,26,36,48],[16,24,32,46,60]]
try {
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport, reducedMotion: 'reduce', deviceScaleFactor: 1 })
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    if (preview) await page.goto(pathToFileURL(resolve(root, preview)).href, { waitUntil: 'networkidle' })
    else await page.goto(url + '?release=' + expectedRef, { waitUntil: 'networkidle' })
    await page.waitForSelector('.chart-card svg')
    const state = await page.evaluate(({ palette, values }) => {
      const rgb = value => { const parts = value.match(/[\d.]+/g); return /^rgba?\(/.test(value) && parts ? parts.map(Number) : null }
      const hex = channels => '#' + channels.slice(0,3).map(value => Math.round(value).toString(16).padStart(2,'0')).join('')
      const lum = channels => channels.slice(0,3).map(value => value/255).map(value => value<=.04045 ? value/12.92 : ((value+.055)/1.055)**2.4).reduce((sum,value,index) => sum+value*[.2126,.7152,.0722][index],0)
      const contrast = (a,b) => (Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05)
      const bw = channels => contrast(channels,[0,0,0]) >= contrast(channels,[255,255,255]) ? '#000000' : '#ffffff'
      const opacity = element => { let alpha=1; for(let node=element;node&&node.tagName!=='svg';node=node.parentElement) alpha*=Number(getComputedStyle(node).opacity); return alpha }
      const primitives = svg => [...svg.querySelectorAll('path,rect,polygon,polyline,line,circle,ellipse')].filter(node => !node.closest('defs,clipPath,mask'))
      const has = (element,point,kind) => typeof element[kind]==='function' && element[kind](new DOMPoint(point.x,point.y).matrixTransform(element.getScreenCTM().inverse()))
      const inkAt = (svg,point) => {
        let paint=[255,255,255]
        for (const node of primitives(svg)) {
          const style=getComputedStyle(node)
          for (const [channel,test,alphaName] of [['fill','isPointInFill','fillOpacity'],['stroke','isPointInStroke','strokeOpacity']]) {
            const color=rgb(style[channel]); if(!color || !has(node,point,test)) continue
            const alpha=(color[3]??1)*opacity(node)*Number(style[alphaName])
            paint=paint.map((value,index)=>color[index]*alpha+value*(1-alpha))
          }
        }
        return hex(paint)
      }
      const cards=[...document.querySelectorAll('.chart-card')], invalidPaints=[], paints=new Set()
      const cardRows=cards.map(card => {
        const svg=card.querySelector('svg'), marks=[...svg.querySelectorAll('path,rect,circle,ellipse,polygon,polyline,line,text,stop')].filter(node=>!node.closest('clipPath,mask'))
        for(const node of marks) for(const channel of node.tagName==='stop'?['stopColor']:['fill','stroke']) {
          const color=rgb(getComputedStyle(node)[channel]); if(!color) continue
          const token=hex(color);paints.add(token);if(!palette.includes(token))invalidPaints.push({id:card.id,tag:node.tagName,channel,paint:token})
        }
        const box=svg.getBoundingClientRect()
        return {id:card.id,type:card.dataset.chartType,marks:marks.length,nativeMarks:svg.querySelectorAll('[ecmeta_series_index]').length,svgBounds:{x:box.x,y:box.y,width:box.width,height:box.height}}
      })
      const boxCard=cards.find(card=>card.dataset.chartType==='boxplot'),boxSvg=boxCard.querySelector('svg')
      const boxes=[...boxSvg.querySelectorAll('path[ecmeta_series_index="0"][ecmeta_data_index]')].filter(node=>getComputedStyle(node).fill!=='none').map(body=>{
        const index=Number(body.getAttribute('ecmeta_data_index')),stats=values[index],bounds=body.getBoundingClientRect(),style=getComputedStyle(body),fill=rgb(style.fill)
        const medianY=bounds.y+(stats[4]-stats[2])/(stats[4]-stats[0])*bounds.height
        const samples=[.25,.5,.75].map(fraction=>({x:bounds.x+bounds.width*fraction,y:medianY,paint:inkAt(boxSvg,{x:bounds.x+bounds.width*fraction,y:medianY})}))
        const faceTop=bounds.y+(stats[4]-stats[3])/(stats[4]-stats[0])*bounds.height,faceBottom=bounds.y+(stats[4]-stats[1])/(stats[4]-stats[0])*bounds.height
        return {index,fill:hex(fill),stroke:hex(rgb(style.stroke)),opacity:opacity(body)*Number(style.fillOpacity),expectedMedian:bw(fill),samples,hoverPoint:{x:bounds.x+bounds.width*.25,y:faceTop+(faceBottom-faceTop)*.3},nativePath:body.getAttribute('d')}
      })
      const graphs=cards.filter(card=>['graph','hub-graph'].includes(card.dataset.chartType)).map(card=>{
        const svg=card.querySelector('svg'),native=[...svg.querySelectorAll('path[ecmeta_series_index][ecmeta_data_index]')]
        const filled=native.filter(node=>getComputedStyle(node).fill!=='none'),bodies=filled.filter(node=>node.getAttribute('d')?.includes('A')),otherFilledGlyphs=filled.filter(node=>!node.getAttribute('d')?.includes('A')),edges=native.filter(node=>getComputedStyle(node).fill==='none')
        const nodes=bodies.map(body=>{
          const style=getComputedStyle(body),fill=rgb(style.fill),bounds=body.getBoundingClientRect()
          const labels=[...svg.querySelectorAll('text')].filter(text=>{const box=text.getBoundingClientRect();return has(body,{x:box.x+box.width/2,y:box.y+box.height/2},'isPointInFill')}).map(text=>({label:text.textContent,ink:hex(rgb(getComputedStyle(text).fill)),expectedInk:bw(fill)}))
          return {index:Number(body.getAttribute('ecmeta_data_index')),fill:hex(fill),stroke:style.stroke,opacity:opacity(body)*Number(style.fillOpacity),labels,nativePath:body.getAttribute('d'),bounds:{x:bounds.x,y:bounds.y,width:bounds.width,height:bounds.height}}
        })
        return {id:card.id,otherFilledGlyphs:otherFilledGlyphs.map(node=>({nativePath:node.getAttribute('d'),index:Number(node.getAttribute('ecmeta_data_index'))})),scope:'Committed gallery source uses undirected circular/fixed graphs with native circle nodes and no arrow symbols. Every filled native path must be an arc node; unexpected non-arc glyphs fail this declared scope. Directed native arrow clearance is covered by isolated accepted contracts.',nodes,edges:edges.map(edge=>{const style=getComputedStyle(edge),color=rgb(style.stroke),alpha=opacity(edge)*Number(style.strokeOpacity),composite=color.map(value=>value*alpha+255*(1-alpha));return {index:Number(edge.getAttribute('ecmeta_data_index')),stroke:hex(color),opacity:alpha,canvasContrast:contrast(composite,[255,255,255]),nativePath:edge.getAttribute('d')}})}
      })
      return {cards:cardRows,paints:[...paints].sort(),invalidPaints,boxes,graphs,duplicateIds:cards.length-new Set(cards.map(card=>card.id)).size,overflow:document.documentElement.scrollWidth>innerWidth+1}
    }, { palette, values })
    if(state.cards.length!==43 || state.cards.some(row=>row.marks<1 || row.svgBounds.width<200 || row.svgBounds.height<140) || state.duplicateIds || state.overflow) findings.push({viewport,message:'Published native gallery count/geometry/IDs fail',cards:state.cards.length,overflow:state.overflow})
    findings.push(...state.invalidPaints.map(row=>({viewport,message:'SVG paint is outside the committed bundled palette',...row})))
    if(state.boxes.length!==4) findings.push({viewport,message:'Published native four-box body inventory differs',boxes:state.boxes.length})
    for(const box of state.boxes) if(box.opacity!==1 || box.fill!==box.stroke || box.samples.some(sample=>sample.paint!==box.expectedMedian)) findings.push({viewport,message:'Actual public boxplot median/body paint fails',...box})
    for(const graph of state.graphs) {
      if(graph.otherFilledGlyphs.length || !graph.nodes.length || !graph.edges.length) findings.push({viewport,message:'Published undirected circle graph native glyph inventory differs',graph:graph.id,otherFilledGlyphs:graph.otherFilledGlyphs})
      for(const node of graph.nodes) if(node.opacity!==1 || node.labels.some(label=>label.ink!==label.expectedInk)) findings.push({viewport,message:'Actual public native graph node/inside label paint fails',graph:graph.id,...node})
    }
    const hover=[]
    for(const box of state.boxes) {
      const card=page.locator('.chart-card[data-chart-type="boxplot"]');await card.scrollIntoViewIfNeeded()
      const hoverState=await page.evaluate(index=>{const body=document.querySelector(`.chart-card[data-chart-type="boxplot"] path[ecmeta_series_index="0"][ecmeta_data_index="${index}"]`),b=body.getBoundingClientRect();return {x:b.x+b.width*.25,y:b.y+b.height*.45}},box.index)
      await page.mouse.move(hoverState.x,hoverState.y);await page.waitForTimeout(50)
      const observed=await page.evaluate(({index,stats})=>{
        const svg=document.querySelector('.chart-card[data-chart-type="boxplot"] svg'),body=svg.querySelector(`path[ecmeta_series_index="0"][ecmeta_data_index="${index}"]`),line=svg.querySelector(`[data-native-median="0:${index}"]`),style=getComputedStyle(body),b=body.getBoundingClientRect()
        const hex=value=>'#'+value.match(/[\d.]+/g).slice(0,3).map(value=>Number(value).toString(16).padStart(2,'0')).join('')
        const c=style.fill.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4),lum=c.reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0)
        const y=b.y+(stats[4]-stats[2])/(stats[4]-stats[0])*b.height,samples=[.25,.5,.75].map(fraction=>{const p=new DOMPoint(b.x+b.width*fraction,y).matrixTransform(line.getScreenCTM().inverse());return line.isPointInStroke(p)})
        return {index,fill:hex(style.fill),medianInk:hex(getComputedStyle(line).stroke),expectedInk:(lum+.05)/.05>=1.05/(lum+.05)?'#000000':'#ffffff',medianSamplesCovered:samples,nativePath:body.getAttribute('d')}
      },{index:box.index,stats:values[box.index]})
      if(observed.medianInk!==observed.expectedInk || observed.medianSamplesCovered.some(value=>!value) || observed.nativePath!==box.nativePath) findings.push({viewport,message:'Public SSR boxplot hover median qualification fails',...observed})
      hover.push(observed);await page.mouse.move(0,0)
    }
    for(const type of ['boxplot','graph','hub-graph']) await page.locator(`.chart-card[data-chart-type="${type}"]`).screenshot({path:resolve(output,`${viewport.width}-${type}.png`),animations:'disabled'})
    if(errors.length) findings.push({viewport,message:'Published gallery browser errors',errors})
    states.push({viewport,...state,hover,errors});await page.close()
  }
}
finally {await browser.close()}
const report={ok:!findings.length,mode:preview?'nonpublication-preview':'exact-commit-publication',expectedRef,source,url,publication:{status:response?.status??null,committedSha256:sha(committed),expectedPagesSha256:sha(expected),publishedSha256:sha(published),exactPagesBytes:published.equals(expected),expectedMethod:preview?'preview-text-canonicalization':'exact-committed-Pages-builder-replay-v2'},auditorCorrection:{previousReport:'report-source-only-v1.json',reason:'The first public byte oracle omitted the existing Pages catalog metadata and favicon insertions. Its original failure is retained. Expected public bytes now come from verify_publication.py replaying the exact committed scripts/build-pages.py transformations; visual paint, median, hover and geometry criteria are unchanged.',skillRuntimeAndFrozenEvaluationsUnchanged:true},method:'Read-only actual SVG browser paints and native hit tests. Independent median coordinates derive from committed five-number source facts and native whisker extents; normal median paint sampled at three span points in SVG paint order. Public SSR hover checks native owner/median paint and actual stroke coverage. Palette inventory and graph node/inside-label observations cover all43 cards at desktop/mobile. Undirected graph edges are reported separately from directed arrow acceptance contracts.',states,findings}
await writeFile(resolve(output,'report.json'),JSON.stringify(report,null,2)+'\n')
console.log(JSON.stringify({ok:report.ok,mode:report.mode,expectedRef,publicByteMatch:report.publication.exactPagesBytes,cards:states.map(state=>state.cards.length),medianSamples:states.reduce((sum,state)=>sum+state.boxes.length*3,0),graphs:states.map(state=>state.graphs.length),findingCount:findings.length,findings,output},null,2))
if(findings.length)process.exitCode=1
