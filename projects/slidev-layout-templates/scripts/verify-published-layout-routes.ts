#!/usr/bin/env -S npx tsx
// Local: node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-published-layout-routes.ts --base-url dist/pages --output projects/slidev-layout-templates/artifacts/published-layouts-local
// Published: use --base-url https://gvillarroel.github.io/skills/ after the Pages deployment succeeds.
// Dependencies: Node >=24 and Playwright from --dependencies (the Slidev ECharts acceptance fixture by default).
// --base-url accepts an HTTP(S) site root or a local Pages directory served automatically on an ephemeral port.
// All generated evidence stays in ignored project artifacts; the verifier never changes fixtures or runtime resources.
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import http from 'node:http'

const args=process.argv.slice(2)
function argument(name:string,fallback=''){const index=args.indexOf(name);return index<0?fallback:args[index+1]}
const root=process.cwd()
const input=argument('--base-url','dist/pages')
const output=path.resolve(argument('--output','projects/slidev-layout-templates/artifacts/published-layouts'))
const dependencies=path.resolve(argument('--dependencies','skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const palettePath=path.resolve(argument('--palette-source','skills/slidev-echarts/assets/palettes/colorsets.json'))
const palettes=JSON.parse(await readFile(palettePath,'utf8')).colorsets
const paletteSha=createHash('sha256').update(await readFile(palettePath)).digest('hex')
const {chromium}=createRequire(path.join(dependencies,'../package.json'))('playwright')
await mkdir(output,{recursive:true})
let server:http.Server|undefined
let baseUrl:string
if(/^https?:\/\//i.test(input))baseUrl=new URL(input.endsWith('/')?input:input+'/').href
else {
  const pagesRoot=path.resolve(input)
  if(!existsSync(path.join(pagesRoot,'index.html')))throw new Error(`Local Pages index is missing: ${path.join(pagesRoot,'index.html')}`)
  const mime:Record<string,string>={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png','.gif':'image/gif','.webp':'image/webp'}
  server=http.createServer(async(request,response)=>{
    try {
      let candidate=path.resolve(pagesRoot,`.${decodeURIComponent(new URL(request.url||'/','http://local').pathname)}`)
      if(!candidate.startsWith(pagesRoot+path.sep)&&candidate!==pagesRoot){response.writeHead(403).end();return}
      if(!existsSync(candidate)){response.writeHead(404).end('Not found');return}
      if((await stat(candidate)).isDirectory())candidate=path.join(candidate,'index.html')
      response.writeHead(200,{'content-type':mime[path.extname(candidate)]||'application/octet-stream','cache-control':'no-store'}).end(await readFile(candidate))
    }catch(error){response.writeHead(500).end(String(error))}
  })
  await new Promise<void>(resolve=>server!.listen(0,'127.0.0.1',resolve))
  baseUrl=`http://127.0.0.1:${(server.address() as {port:number}).port}/`
}
const modes=[
  {slug:'dynamic-columns',mode:'columns',title:'Dynamic Columns',colorset:'colorset1'},
  {slug:'dynamic-grid',mode:'grid',title:'Dynamic Component Grid',colorset:'colorset2'},
  {slug:'masonry-rows',mode:'masonry-rows',title:'Masonry Across Three Rows',colorset:'colorset1'},
  {slug:'masonry-columns',mode:'masonry-columns',title:'Masonry Down Columns',colorset:'colorset1'},
]
const catalog=[
  {id:'plan',title:'Plan',body:'Set the next outcome.',detail:'Set the next outcome and agree on clear evidence of progress.',metric:74},
  {id:'research',title:'Research',body:'Collect useful evidence.',detail:'Collect useful evidence from interviews, source documents, and observed behavior.',metric:58},
  {id:'design',title:'Design',body:'Make the idea concrete.',detail:'Build a small prototype.',metric:82},
  {id:'build',title:'Build',body:'Ship a working increment.',detail:'Ship a working increment, keep the scope focused, and record the decisions behind the implementation.',metric:63},
  {id:'measure',title:'Measure',body:'Track the same metric.',detail:'Track the same metric before and after the change.',metric:91},
  {id:'review',title:'Review',body:'Check facts and usability.',detail:'Review facts and usability, then resolve the remaining questions.',metric:67},
  {id:'release',title:'Release',body:'Publish the approved work.',detail:'Publish the approved work and document the next step.',metric:88},
  {id:'support',title:'Support',body:'Answer the next question.',detail:'Answer the next question with a reusable explanation.',metric:79},
  {id:'learn',title:'Learn',body:'Promote what worked.',detail:'Promote what worked into a repeatable practice and retain the evidence.',metric:55},
  {id:'improve',title:'Improve',body:'Refine the next iteration.',detail:'Refine the next iteration using observations from the last release.',metric:72},
  {id:'share',title:'Share',body:'Make the result discoverable.',detail:'Make the result discoverable for the next person who needs it.',metric:84},
]
const browser=await chromium.launch({headless:true})
const results:any[]=[],traversals:any[]=[],defaults:any[]=[],indexCards:any[]=[],errors:string[]=[],browserMessages:any[]=[]
function collectErrors(page:any,surface:string){
  page.on('pageerror',(error:Error)=>browserMessages.push({surface,type:'pageerror',message:String(error)}))
  page.on('console',(message:any)=>{if(message.type()==='error')browserMessages.push({surface,type:'console',message:message.text()})})
}
async function settled(locator:any){
  let prior='',same=0
  for(let attempt=0;attempt<30;attempt++){
    const current=await locator.evaluate((element:HTMLElement)=>JSON.stringify([element.dataset,element.querySelector<HTMLElement>('[data-layout-mode]')?.dataset,[...element.querySelectorAll<HTMLElement>('[data-item-id]')].map(card=>[card.dataset.itemId,card.offsetLeft,card.offsetTop,card.clientWidth,card.clientHeight])]))
    same=current===prior?same+1:0;prior=current
    if(same>=2)return
    await locator.page().waitForTimeout(60)
  }
  throw new Error('Published layout did not settle in 1.8 seconds.')
}
async function audit(locator:any,descriptor:any,expected:any){
  const result=await locator.evaluate((element:HTMLElement,{descriptor,expected,palettes,catalog}:any)=>{
    const failures:string[]=[],frame=element.querySelector<HTMLElement>('[data-layout-mode]')!,frameBounds=frame.getBoundingClientRect(),bounds=element.getBoundingClientRect()
    const palette=palettes[descriptor.colorset],solid=palette.solidSequence.filter((fill:string)=>fill!=='#ffffff')
    const within=(r:DOMRect,b:DOMRect)=>r.left>=b.left-.5&&r.top>=b.top-.5&&r.right<=b.right+.5&&r.bottom<=b.bottom+.5
    const viewport=(r:DOMRect)=>r.left>=-.5&&r.top>=-.5&&r.right<=innerWidth+.5&&r.bottom<=innerHeight+.5
    const rect=(r:DOMRect)=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height})
    function hex(css:string){const channels=css.match(/^rgba?\(([^)]+)\)$/)?.[1].split(',').map(Number);return channels&&channels.length>=3&&(channels.length===3||channels[3]===1)?'#'+channels.slice(0,3).map(v=>Math.round(v).toString(16).padStart(2,'0')).join(''):null}
    function effectiveOpacity(node:Element){let opacity=1;for(let parent:Element|null=node;parent;parent=parent.parentElement)opacity*=Number(getComputedStyle(parent).opacity);return opacity}
    function backing(node:Element){for(let parent:Element|null=node;parent;parent=parent.parentElement){const fill=hex(getComputedStyle(parent).backgroundColor);if(fill)return fill}return null}
    function luminance(color:string){const c=color.slice(1).match(/../g)!.map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722}
    function contrast(a:string,b:string){const x=luminance(a),y=luminance(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
    function glyphs(node:Element,boundary:DOMRect){const failures:any[]=[];const walker=document.createTreeWalker(node,NodeFilter.SHOW_TEXT);for(let text=walker.nextNode();text;text=walker.nextNode()){if(!text.textContent?.trim())continue;for(let offset=0;offset<text.textContent.length;offset++){if(!text.textContent[offset].trim())continue;const range=document.createRange();range.setStart(text,offset);range.setEnd(text,offset+1);for(const r of range.getClientRects())if(!within(r as DOMRect,boundary)||!viewport(r as DOMRect))failures.push({text:text.textContent[offset],bounds:rect(r as DOMRect)})}}return failures}
    const cards=[...frame.querySelectorAll<HTMLElement>('[data-item-id]')].map(card=>{
      const css=getComputedStyle(card),r=card.getBoundingClientRect(),id=card.dataset.itemId!,index=catalog.findIndex((item:any)=>item.id===id),requested=catalog[index],fill=hex(css.backgroundColor),ink=hex(css.color)
      if(index<0||fill!==solid[index])failures.push(id+': paint differs from the complete category manifest')
      if(!fill||!palette.allowed.includes(fill)||ink!==palette.textOnFill[fill]||effectiveOpacity(card)!==1)failures.push(id+': fill/text is not opaque exact palette paint with maximum black/white contrast')
      if(parseFloat(css.borderTopWidth)!==0||parseFloat(css.borderRightWidth)!==0||parseFloat(css.borderBottomWidth)!==0||parseFloat(css.borderLeftWidth)!==0)failures.push(id+': decorative border appears before solid capacity is exhausted')
      if(!within(r,frameBounds)||!viewport(r))failures.push(id+': card crosses frame or viewport')
      const title=card.querySelector<HTMLElement>('.layout-demo-card-title')!,body=card.querySelector<HTMLElement>('.layout-demo-card-body')!
      if(title?.textContent!==requested?.title||body?.textContent!==(descriptor.mode==='masonry-columns'?requested?.detail:requested?.body))failures.push(id+': complete requested title/body differs')
      const labels=[title,body].filter(Boolean).map((label,labelIndex)=>{
        const style=getComputedStyle(label),color=hex(style.color),actualBacking=backing(label),opacity=effectiveOpacity(label),badGlyphs=glyphs(label,r)
        if(color!==palette.textOnFill[actualBacking!]||!actualBacking||contrast(color!,actualBacking)<4.5||opacity!==1)failures.push(id+': label loses actual backing contrast or opacity')
        if(style.fontSize!==(labelIndex===0?'16px':'14px')||!style.fontFamily.includes('Open Sans'))failures.push(id+': fixed Open Sans 16/14 px typography changed')
        if(badGlyphs.length)failures.push(id+': '+badGlyphs.length+' individual glyphs cross card or viewport bounds')
        return {ink:color,backing:actualBacking,opacity,font:style.fontSize,family:style.fontFamily,glyphErrors:badGlyphs}
      })
      const svg=card.querySelector<SVGElement>('.layout-demo-metric')
      if(descriptor.mode==='grid'){
        if(!svg||svg.getAttribute('aria-label')!==requested.metric+' percent complete'||!within(svg.getBoundingClientRect(),r))failures.push(id+': custom SVG metric is absent, clipped, or mislabeled')
        for(const [pathIndex,mark]of [...svg?.querySelectorAll('path')||[]].entries()){const style=getComputedStyle(mark);if(hex(style.stroke)!==palette.textOnFill[fill!]||effectiveOpacity(mark)!==1||parseFloat(style.strokeWidth)!==(pathIndex===0?2:6))failures.push(id+': SVG metric loses exact opaque inside ink or quantitative track/value stroke widths')}
      }else if(svg)failures.push(id+': unexpected metric outside the grid example')
      return{id,category:card.dataset.categoryId,fill,ink,labels,rect:rect(r),row:Number(card.dataset.row),column:Number(card.dataset.column),height:card.offsetHeight,width:card.offsetWidth}
    })
    const overlap:any[]=[]
    for(let first=0;first<cards.length;first++)for(let second=first+1;second<cards.length;second++){const a=cards[first].rect,b=cards[second].rect;if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>.5&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>.5)overlap.push([cards[first].id,cards[second].id])}
    if(overlap.length)failures.push('Native cards overlap.')
    const actual={count:Number(element.dataset.count),columns:Number(element.dataset.columns),page:Number(element.dataset.page),pages:Number(element.dataset.pages),order:element.dataset.order,colorset:element.dataset.colorset}
    for(const [key,value]of Object.entries(expected))if((actual as any)[key]!==value)failures.push('Requested '+key+' differs from native metadata.')
    if(frame.dataset.layoutFits!=='true'||frame.dataset.layoutMode!==descriptor.mode||frame.dataset.colorset!==descriptor.colorset||Number(frame.dataset.page)!==expected.page||Number(frame.dataset.pages)!==expected.pages)failures.push('Native mode/palette/page/capacity metadata differs from the requested state.')
    if(Number(frame.dataset.configuredRows)!==(descriptor.mode==='grid'?2:3))failures.push('Configured tracks changed from the published contract.')
    if(!viewport(bounds)||!viewport(frameBounds)||hex(getComputedStyle(frame).backgroundColor)!=='#ffffff')failures.push('Published frame crosses the viewport or loses its opaque white canvas.')
    if(descriptor.mode==='grid'&&cards.length&&Math.max(...cards.map(card=>card.height))-Math.min(...cards.map(card=>card.height))>.5)failures.push('Grid cells no longer have a uniform selected-page height.')
    if(descriptor.mode==='masonry-rows'){
      if(cards.length>=3&&new Set(cards.map(card=>card.row)).size!==3)failures.push('A complete horizontal masonry page does not occupy three literal rows.')
      for(const row of new Set(cards.map(card=>card.row))){const members=cards.filter(card=>card.row===row);if(Math.max(...members.map(card=>card.rect.top))-Math.min(...members.map(card=>card.rect.top))>.5)failures.push('Horizontal masonry is not aligned on its literal rows.')}
    }
    const controls=[...element.querySelectorAll<HTMLButtonElement>('[data-layout-control]')].map(button=>{
      const style=getComputedStyle(button),action=button.dataset.layoutControl!,pressed=button.getAttribute('aria-pressed')==='true',fill=hex(style.backgroundColor),ink=hex(style.color),opacity=effectiveOpacity(button)
      if(fill!==(pressed?'#9e1b32':'#e7e7e7')||ink!==(pressed?'#ffffff':'#000000')||style.fontSize!=='12px'||!style.fontFamily.includes('Open Sans'))failures.push(action+': control loses exact shared palette or fixed typography')
      if(!button.disabled&&(opacity!==1||contrast(fill!,ink!)<4.5))failures.push(action+': active control loses opacity or contrast')
      if(action.startsWith('items-')&&pressed!==(Number(action.slice(6))===expected.count))failures.push(action+': item control state is stale')
      if(action.startsWith('columns-')&&pressed!==(Number(action.slice(8))===expected.columns))failures.push(action+': column control state is stale')
      if(action==='reverse'&&pressed!==(expected.order==='reversed'))failures.push('Reverse control state is stale.')
      if(action==='page-previous'&&button.disabled!==(expected.page===1)||action==='page-next'&&button.disabled!==(expected.page===expected.pages))failures.push(action+': pager disabled state is stale')
      const clipped=glyphs(button,bounds);if(clipped.length)failures.push(action+': control glyphs cross the wrapper or viewport')
      return{action,pressed,disabled:button.disabled,fill,ink,opacity,font:style.fontSize,family:style.fontFamily,glyphErrors:clipped}
    })
    const budget=descriptor.mode==='masonry-rows'?9:descriptor.mode==='grid'?expected.columns*2:descriptor.mode==='masonry-columns'?Math.min(6,expected.columns*2):expected.columns*3
    const ids=catalog.slice(0,expected.count).map((item:any)=>item.id);if(expected.order==='reversed')ids.reverse()
    const visible=ids.slice((expected.page-1)*budget,expected.page*budget)
    if(JSON.stringify(cards.map(card=>card.id))!==JSON.stringify(visible))failures.push('Rendered source IDs differ from the independently planned current page.')
    return{passed:!failures.length,failures,...actual,fits:frame.dataset.layoutFits,configuredRows:Number(frame.dataset.configuredRows),occupiedRows:Number(frame.dataset.occupiedRows),requiredHeight:Number(frame.dataset.requiredHeight),height:frame.clientHeight,withinViewport:viewport(bounds)&&viewport(frameBounds),cards,controls,overlap}
  },{descriptor,expected,palettes,catalog})
  return result
}
try{
  const index=await browser.newPage({viewport:{width:1600,height:1000}});collectErrors(index,'catalog')
  const response=await index.goto(baseUrl,{waitUntil:'networkidle'})
  if(!response||response.status()<200||response.status()>=400)errors.push('Canonical examples index did not return a successful HTTP response.')
  for(const skill of ['slidev-echarts','slidev-animejs']){
    const selector=`a#example-set-${skill}[data-example-id="${skill}"][data-pattern-id="${skill}"][data-example-source="${skill}"]`
    const locator=index.locator(selector),count=await locator.count()
    if(count!==1){errors.push(`Catalog must contain exactly one canonical ${skill} card; found ${count}.`);continue}
    await locator.scrollIntoViewIfNeeded()
    const card=await locator.evaluate((element:HTMLAnchorElement)=>({id:element.id,exampleId:element.dataset.exampleId,patternId:element.dataset.patternId,source:element.dataset.exampleSource,href:element.href,text:element.innerText,visible:!!element.getClientRects().length}))
    const expected=new URL(`examples/${skill}/`,baseUrl).href
    if(card.href!==expected||!card.visible)errors.push(`Catalog ${skill} link differs from its visible canonical route.`)
    indexCards.push(card);await index.screenshot({path:path.join(output,`catalog-${skill}.png`)})
  }
  await index.close()
  for(const skill of ['slidev-echarts','slidev-animejs']){
    const page=await browser.newPage({viewport:{width:1600,height:900}});collectErrors(page,skill)
    const start=skill==='slidev-echarts'?38:32
    for(const [offset,descriptor]of modes.entries()){
      const slide=start+offset,pattern=skill+'-'+descriptor.slug,url=new URL(`examples/${skill}/#/${slide}`,baseUrl).href
      const response=await page.goto(url,{waitUntil:'networkidle'})
      // Playwright returns null for same-document hash navigation. The dedicated
      // native ID/heading checks below verify that each hash reached its slide.
      if(response&&(response.status()<200||response.status()>=400)||!response&&page.url()!==url)errors.push(pattern+': route did not return a successful response or reach its requested hash.')
      const locator=page.locator('#'+pattern);await locator.waitFor({state:'visible'});await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(800);await settled(locator)
      const metadataCount=await page.locator(`[data-pattern-id="${pattern}"]`).count(),localId=await locator.getAttribute('data-example-id'),headline=await page.locator(`.slidev-page-${slide} h1`).innerText()
      if(metadataCount!==1||localId!==descriptor.slug||headline!==descriptor.title)errors.push(pattern+': canonical ID, local example ID, or dedicated slide heading differs.')
      const defaultBudget=descriptor.mode==='masonry-rows'?9:descriptor.mode==='grid'?6:descriptor.mode==='masonry-columns'?6:9
      const defaultState=await audit(locator,descriptor,{count:7,columns:3,page:1,pages:Math.ceil(7/defaultBudget),order:'source',colorset:descriptor.colorset})
      defaults.push({skill,pattern,slide,url,httpStatus:response?.status()??'same-document hash navigation',headline,metadataCount,localId,...defaultState});await page.screenshot({path:path.join(output,pattern+'-default.png')})
      for(const columns of descriptor.mode==='masonry-rows'?[3]:[2,3,4]){
        if(descriptor.mode!=='masonry-rows'){await locator.locator(`[data-layout-control="columns-${columns}"]`).click();await settled(locator)}
        for(const count of [3,7,11]){
          await locator.locator(`[data-layout-control="items-${count}"]`).click();await settled(locator)
          for(const order of ['source','reversed']){
            if(order==='reversed'){await locator.locator('[data-layout-control="reverse"]').click();await settled(locator)}
            while(Number(await locator.getAttribute('data-page'))>1){await locator.locator('[data-layout-control="page-previous"]').click();await settled(locator)}
            const budget=descriptor.mode==='masonry-rows'?9:descriptor.mode==='grid'?columns*2:descriptor.mode==='masonry-columns'?Math.min(6,columns*2):columns*3,pages=Math.ceil(count/budget),visited:string[]=[]
            for(let current=1;current<=pages;current++){
              if(current>1){await locator.locator('[data-layout-control="page-next"]').click();await settled(locator)}
              const state=await audit(locator,descriptor,{count,columns,page:current,pages,order,colorset:descriptor.colorset})
              Object.assign(state,{skill,pattern,slide,url});results.push(state);visited.push(...state.cards.map((card:any)=>card.id))
              if(!state.passed&&results.filter(value=>!value.passed).length<=20)await page.screenshot({path:path.join(output,`${pattern}-${count}-${columns}-${order}-${current}-failure.png`)})
            }
            const expected=catalog.slice(0,count).map(item=>item.id);if(order==='reversed')expected.reverse()
            traversals.push({skill,pattern,count,columns,order,pages,visited,expected,passed:JSON.stringify(visited)===JSON.stringify(expected)&&new Set(visited).size===visited.length})
            if(order==='reversed'){await locator.locator('[data-layout-control="reverse"]').click();await settled(locator)}
          }
        }
      }
      console.log(JSON.stringify({pattern,url,states:results.filter(value=>value.pattern===pattern).length,passed:results.filter(value=>value.pattern===pattern).every(value=>value.passed)}))
    }
    await page.close()
  }
}catch(error){errors.push(String(error))}
finally{await browser.close();if(server)await new Promise<void>(resolve=>server!.close(()=>resolve()))}
const wakeLocks=browserMessages.filter(value=>value.message.includes('Wake Lock permission request denied'))
const unexpectedConsole=browserMessages.filter(value=>!value.message.includes('Wake Lock permission request denied'))
if(results.length!==188||traversals.length!==120||defaults.length!==8||indexCards.length!==2)errors.push(`Published coverage differs from the qualified contract: ${results.length}/188 states, ${traversals.length}/120 traversals, ${defaults.length}/8 routes, ${indexCards.length}/2 catalog cards.`)
const report={date:new Date().toISOString(),passed:!errors.length&&!unexpectedConsole.length&&results.every(value=>value.passed)&&defaults.every(value=>value.passed)&&traversals.every(value=>value.passed),input,baseUrl,palettePath,paletteSha,indexCards,defaults,results,traversals,errors,wakeLocks,unexpectedConsole}
await writeFile(path.join(output,'verification.json'),JSON.stringify(report,null,2)+'\n')
const summary={date:report.date,passed:report.passed,input,baseUrl,states:results.length,traversals:traversals.length,routes:defaults.length,catalogCards:indexCards.length,failedStates:results.filter(value=>!value.passed).map(({pattern,count,columns,order,page,failures})=>({pattern,count,columns,order,page,failures})),failedDefaults:defaults.filter(value=>!value.passed).map(({pattern,failures})=>({pattern,failures})),failedTraversals:traversals.filter(value=>!value.passed),errors,unexpectedConsole,knownHeadlessWakeLockDenials:wakeLocks.length,paletteSha,report:path.join(output,'verification.json')}
await writeFile(path.join(output,'summary.json'),JSON.stringify(summary,null,2)+'\n')
console.log(JSON.stringify(summary,null,2))
if(!report.passed)process.exitCode=1
