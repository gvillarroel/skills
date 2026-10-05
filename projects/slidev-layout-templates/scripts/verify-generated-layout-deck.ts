#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-generated-layout-deck.ts --deck evaluations/runs/<run-id>/workspace/deck --output projects/slidev-layout-templates/artifacts/pi/<run-id>
// Dependencies: Node >=24; @slidev/cli, @slidev/theme-default and playwright from --dependencies (existing fixture by default).
// Inspect final native states independently of an isolated author's report. Never copy evaluator files into the skill bundle.
import { readFile, writeFile, mkdir, symlink, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import http from 'node:http'

const evaluatorSha256=createHash('sha256').update(await readFile(process.argv[1])).digest('hex')
const args = process.argv.slice(2)
function arg(name: string, fallback = '') { const i=args.indexOf(name); return i>=0?args[i+1]:fallback }
const deck=path.resolve(arg('--deck'))
if (!arg('--deck')) throw new Error('--deck is required.')
const output=path.resolve(arg('--output','projects/slidev-layout-templates/artifacts/generated-deck'))
const html=path.resolve(arg('--html',path.join(output,'html')))
const dependencies=path.resolve(arg('--dependencies','skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const paletteSource=path.resolve(arg('--palette-source','skills/slidev-echarts/assets/palettes/colorsets.json'))
const require=createRequire(path.join(dependencies,'../package.json'))
const {chromium}=require('playwright')
const palettes=JSON.parse(await readFile(paletteSource,'utf8')).colorsets
await mkdir(output,{recursive:true})
const runtimeFiles=['components/SlidevLayout.vue','lib/slidev-layouts.mjs'];if(existsSync(path.join(deck,'components/SlidevCollection.vue')))runtimeFiles.push('components/SlidevCollection.vue')
const hashes=Object.fromEntries(await Promise.all(runtimeFiles.map(async file=>[file,createHash('sha256').update(await readFile(path.join(deck,file))).digest('hex')])))
for (const [flag,file] of [['--expect-helper-sha','lib/slidev-layouts.mjs'],['--expect-component-sha','components/SlidevLayout.vue'],['--expect-collection-sha','components/SlidevCollection.vue']]) if(arg(flag)&&arg(flag)!==hashes[file]) throw new Error(`Frozen runtime digest mismatch: ${file}`)
const parsed=JSON.parse(await readFile(path.join(deck,'data/cards.json'),'utf8'))
const data=Array.isArray(parsed)?parsed:parsed.cards||parsed.items
if(!Array.isArray(data)||data.length!==11) throw new Error('The editable data must contain all eleven requested card records.')
const expectedTitles=['Intake','Scope','Research','Draft','Diagram','Review','Revise','Check','Approve','Publish','Archive']
for(let i=0;i<11;i++) if(data[i].id!==`card-${String(i+1).padStart(2,'0')}`||data[i].title!==expectedTitles[i]||!String(data[i].body||'').trim()) throw new Error(`Missing or altered identity/title/body for card ${i+1}.`)
if(!existsSync(path.join(deck,'node_modules'))) await symlink(dependencies,path.join(deck,'node_modules'),'junction')
if(!args.includes('--skip-build')) {
  const cli=require.resolve('@slidev/cli/bin/slidev.mjs')
  const built=await new Promise<{code:number,stdout:string}>(resolve=>{
    const child=spawn(process.execPath,[cli,'build','slides.md','--base','./','--out',html],{cwd:deck,windowsHide:true,env:{...process.env,NODE_ENV:'production'}})
    let stdout='';child.stdout.on('data',d=>stdout+=d);child.stderr.on('data',d=>stdout+=d);child.on('close',code=>resolve({code:code??1,stdout}))
  })
  await writeFile(path.join(output,'build.log'),built.stdout)
  if(built.code) throw new Error(`Generated deck build failed: ${path.join(output,'build.log')}`)
}
const mime:Record<string,string>={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2'}
const server=http.createServer(async(request,response)=>{
  try{let candidate=path.resolve(html,`.${decodeURIComponent(new URL(request.url||'/','http://local').pathname)}`);if(!candidate.startsWith(html+path.sep)&&candidate!==html){response.writeHead(403).end();return}if(!existsSync(candidate)||(await stat(candidate)).isDirectory())candidate=path.join(html,'index.html');response.writeHead(200,{'content-type':mime[path.extname(candidate)]||'application/octet-stream'}).end(await readFile(candidate))}catch(error){response.writeHead(500).end(String(error))}
})
await new Promise<void>(r=>server.listen(0,'127.0.0.1',r))
const base=`http://127.0.0.1:${(server.address() as {port:number}).port}`
const browser=await chromium.launch({headless:true})
const page=await browser.newPage({viewport:{width:1280,height:800}})
const errors:string[]=[]
page.on('pageerror',(error:Error)=>{if(!String(error).includes('Wake Lock permission request denied'))errors.push(String(error))})
const results:any[]=[]
const modes=['columns','grid','masonry-rows','masonry-columns']
const colorMap=new Map<string,string>()
const fontMap=new Map<string,string>()

async function capture(id:string,expectedMode:string,count:number,columns:number,shot=false,allowAdaptive=false) {
  await page.evaluate(()=>document.fonts.ready)
  await page.waitForTimeout(250)
  const audit=await page.evaluate(({palettes,expectedMode,count,columns,data,allowAdaptive})=>{
    function hex(v:string){const n=v.match(/[\d.]+/g)?.map(Number);if(v.startsWith('rgb')&&n&&n.length>=3){if(n[3]===0)return null;return '#'+n.slice(0,3).map(n=>Math.round(n).toString(16).padStart(2,'0')).join('')}return v==='transparent'||v==='none'?null:v.toLowerCase()}
    function l(v:string){const c=v.slice(1).match(/../g)!.map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722}
    function contrast(a:string,b:string){const x=l(a),y=l(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
    const surfaces=[...document.querySelectorAll<HTMLElement>('[data-layout-mode]')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.height&&getComputedStyle(e).visibility!=='hidden'})
    const surface=surfaces[0]
    if(!surface)return{passed:false,failures:['No visible native layout frame.'],cards:[],pages:0,page:0}
    const bounds=surface.getBoundingClientRect(),scale=bounds.width/surface.clientWidth
    const failures:string[]=[],clipped:any[]=[],outside:any[]=[],overlap:any[]=[]
    if(bounds.left < -1 || bounds.top < -1 || bounds.right > innerWidth+1 || bounds.bottom > innerHeight+1)failures.push('Layout frame crosses the browser viewport.')
    const selected=surface.dataset.colorset||''
    const palette=palettes[selected]
    if(!palette)failures.push('Layout did not declare an exact bundled palette.')
    if(selected!=='colorset1')failures.push('Task requested the default colorset1.')
    if(surface.dataset.layoutMode!==expectedMode)failures.push(`Wrong layout mode ${surface.dataset.layoutMode}; expected ${expectedMode}.`)
    if(surface.dataset.layoutFits!=='true')failures.push('Published state reports fits=false.')
    if(expectedMode!=='masonry-rows'){const actual=Number(surface.dataset.configuredColumns);if(allowAdaptive?!(actual>=1&&actual<=columns):actual!==columns)failures.push(`Expected ${allowAdaptive?'at most ':''}${columns} configured columns.`)}
    if(expectedMode==='masonry-rows'&&Number(surface.dataset.configuredRows)!==3)failures.push('Horizontal masonry does not configure exactly three literal rows.')
    const cards=[...surface.querySelectorAll<HTMLElement>('[data-item-id]')].map(element=>{
      const r=element.getBoundingClientRect(),css=getComputedStyle(element),id=element.dataset.itemId!
      const fill=hex(css.backgroundColor),ink=hex(css.color)
      const source=data.find((item:any)=>item.id===id)
      if(!source)failures.push(`Unexpected card identity ${id}.`)
      else if(!element.textContent?.includes(source.title)||!element.textContent?.includes(source.body))failures.push(`${id}: complete requested title/body was not rendered.`)
      if(fill&&(!palette||!palette.allowed.includes(fill)))failures.push(`${id}: undeclared fill ${fill}.`)
      const identityIndex=data.findIndex((item:any)=>item.id===id)
      const expectedFill=palette?.solidSequence.filter((fill:string)=>fill!=='#ffffff')[identityIndex]
      if(expectedFill&&fill!==expectedFill)failures.push(`${id}: fill ${fill} differs from its complete persistent category allocation ${expectedFill}.`)
      if(ink&&(!palette||!palette.allowed.includes(ink)))failures.push(`${id}: undeclared text ${ink}.`)
      if(fill&&ink!== (contrast('#000000',fill)>=contrast('#ffffff',fill)?'#000000':'#ffffff'))failures.push(`${id}: text differs from maximum black/white contrast.`)
      if(fill&&ink&&contrast(fill,ink)<4.5)failures.push(`${id}: text contrast below 4.5:1.`)
      if(parseFloat(css.borderTopWidth)>0)failures.push(`${id}: decorative border before unique solids are exhausted.`)
      if(r.left<bounds.left-1||r.top<bounds.top-1||r.right>bounds.right+1||r.bottom>bounds.bottom+1)outside.push(id)
      const textFonts=new Set<string>(),semanticFonts=new Set<string>()
      const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT);let node=walker.nextNode()
      while(node){if(node.textContent?.trim()){const range=document.createRange();range.selectNodeContents(node);for(const glyph of range.getClientRects())if(glyph.left<r.left-1||glyph.top<r.top-1||glyph.right>r.right+1||glyph.bottom>r.bottom+1)clipped.push({id,text:node.textContent});const style=getComputedStyle(node.parentElement!);let opacity=1;for(let a:Element|null=node.parentElement;a;a=a.parentElement){opacity*=Number(getComputedStyle(a).opacity);if(a===surface)break}if(Math.abs(opacity-1)>.0001)failures.push(`${id}: label effective opacity is ${opacity}.`);textFonts.add(style.fontSize);const nodeText=node.textContent?.trim()||'';const semantic=Boolean(source && nodeText && nodeText!==source.id && !/^\d+$/.test(nodeText) && (nodeText===source.title || source.body.includes(nodeText) || nodeText.includes(source.title)));if(semantic)semanticFonts.add(style.fontSize);const color=hex(style.color);if(color&&(!palette||!palette.allowed.includes(color)))failures.push(`${id}: undeclared descendant text ${color}.`);let backing=fill;for(let a:Element|null=node.parentElement;a&&a!==element.parentElement;a=a.parentElement){const paint=hex(getComputedStyle(a).backgroundColor);if(paint){backing=paint;break}}if(color&&backing){const best=contrast('#000000',backing)>=contrast('#ffffff',backing)?'#000000':'#ffffff';if(color!==best)failures.push(`${id}: text '${nodeText}' is not maximum black/white contrast against its actual backing ${backing}.`);if(contrast(color,backing)<4.5)failures.push(`${id}: text '${nodeText}' contrast is below 4.5:1 against its actual backing.`)}}node=walker.nextNode()}
      return{id,fill,ink,textFonts:[...textFonts].sort(),semanticFonts:[...semanticFonts].sort(),row:Number(element.dataset.row),column:Number(element.dataset.column),x:(r.left-bounds.left)/scale,y:(r.top-bounds.top)/scale,width:r.width/scale,height:r.height/scale}
    })
    if(outside.length)failures.push(`${outside.length} cards cross layout frame bounds.`)
    if(clipped.length)failures.push(`${clipped.length} glyph ranges cross card bounds.`)
    for(let i=0;i<cards.length;i++)for(let j=i+1;j<cards.length;j++){const a=cards[i],b=cards[j];if(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>.5&&Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>.5)overlap.push([a.id,b.id])}
    if(overlap.length)failures.push(`${overlap.length} overlapping card pairs.`)
    if(expectedMode==='masonry-rows'&&cards.length>=3){const rows=[...new Set(cards.map(c=>c.row))];if(rows.length!==3)failures.push('Horizontal masonry does not occupy three literal rows.');for(const row of rows){const members=cards.filter(c=>c.row===row);if(Math.max(...members.map(c=>c.y))-Math.min(...members.map(c=>c.y))>.5)failures.push(`Row ${row} does not share a common top edge.`)}}
    if(expectedMode==='grid'){for(const row of [...new Set(cards.map(c=>c.row))]){const members=cards.filter(c=>c.row===row);if(Math.max(...members.map(c=>c.height))-Math.min(...members.map(c=>c.height))>.5)failures.push(`Grid row ${row} does not have equal cell heights.`)}}
    const controls:any[]=[]
    for(const button of [...document.querySelectorAll<HTMLButtonElement>('button')].filter(button=>/^(Previous page|Next page)$/i.test(button.textContent?.trim()||'')&&button.getBoundingClientRect().width&&button.getBoundingClientRect().height&&getComputedStyle(button).visibility!=='hidden')){
      const buttonBounds=button.getBoundingClientRect();if(buttonBounds.left < -1 || buttonBounds.top < -1 || buttonBounds.right > innerWidth+1 || buttonBounds.bottom > innerHeight+1)failures.push(`Page control ${button.textContent?.trim()} crosses the viewport.`)
      const css=getComputedStyle(button),ink=hex(css.color);let backing=hex(css.backgroundColor)
      for(let ancestor=button.parentElement;!backing&&ancestor;ancestor=ancestor.parentElement)backing=hex(getComputedStyle(ancestor).backgroundColor)
      backing ||= '#ffffff'
      const active=!button.disabled&&button.getAttribute('aria-disabled')!=='true'
      const paints=[ink,backing]
      for(const side of ['Top','Right','Bottom','Left'])if(parseFloat(css[`border${side}Width` as any])>0)paints.push(hex(css[`border${side}Color` as any]))
      if(css.outlineStyle!=='none'&&parseFloat(css.outlineWidth)>0)paints.push(hex(css.outlineColor))
      if(paints.some(paint=>paint&&(!palette||!palette.allowed.includes(paint))))failures.push(`Page control ${button.textContent?.trim()} uses undeclared paint.`)
      let opacity=1;for(let ancestor:Element|null=button;ancestor;ancestor=ancestor.parentElement)opacity*=Number(getComputedStyle(ancestor).opacity)
      const ratio=ink?contrast(ink,backing):0
      if(active&&(ratio<4.5||Math.abs(opacity-1)>.0001))failures.push(`Active page control ${button.textContent?.trim()} lacks opaque readable text.`)
      controls.push({name:button.textContent?.trim(),active,ink,backing,ratio,opacity,paints})
    }
    const pages=Number(surface.dataset.pages),page=Number(surface.dataset.page)
    if(!Number.isInteger(pages)||pages<1||!Number.isInteger(page)||page<1||page>pages)failures.push('Invalid pagination metadata.')
    if(cards.some(c=>!data.slice(0,count).some((d:any)=>d.id===c.id)))failures.push('A later card was exposed before its requested click state.')
    return{passed:!failures.length,failures,mode:surface.dataset.layoutMode,colorset:selected,configuredColumns:Number(surface.dataset.configuredColumns),configuredRows:Number(surface.dataset.configuredRows),width:surface.clientWidth,height:surface.clientHeight,pages,page,cards,controls,clipped,outside,overlap}
  },{palettes,expectedMode,count,columns,data,allowAdaptive})
  for(const card of audit.cards){if(colorMap.has(card.id)&&colorMap.get(card.id)!==card.fill){audit.passed=false;audit.failures.push(`${card.id}: color changed across slides/counts/pages.`)}else colorMap.set(card.id,card.fill);const fonts=JSON.stringify(card.textFonts),fontKey=expectedMode+':'+card.id;if(fontMap.has(fontKey)&&fontMap.get(fontKey)!==fonts){audit.passed=false;audit.failures.push(`${card.id}: authored typography changed across count/page/resize states.`)}else fontMap.set(fontKey,fonts)}
  if(shot||!audit.passed)await page.screenshot({path:path.join(output,`${id}.png`),fullPage:true})
  Object.assign(audit,{id});results.push(audit)
  return audit
}

async function walkCollection(id:string,mode:string,count:number,columns:number,allowAdaptive=false,shot=false,variation=false) {
  // Controls own page state. Reset through their public accessible behavior.
  for(let attempt=0;attempt<20;attempt++){
    const current=Number(await page.locator('[data-layout-mode]:visible').first().getAttribute('data-page'))
    if(current<=1)break
    const previous=page.getByRole('button',{name:/^Previous page$/i})
    if(!await previous.count()){results.push({id:id+'-previous-control',passed:false,failures:['A selected later page needs an accessible Previous page control.']});break}
    try{await previous.first().click({timeout:1500})}catch(error){results.push({id:id+'-previous-reachable',passed:false,failures:['Previous page is blocked or outside the usable presentation area.'],interactionError:String(error)});break}await page.waitForTimeout(100)
  }
  const first=await capture(id+'-page-1',mode,count,columns,shot,allowAdaptive)
  const visited=first.cards.map((card:any)=>card.id),geometry=[...first.cards]
  for(let pageNumber=2;pageNumber<=first.pages;pageNumber++){
    const next=page.getByRole('button',{name:/^Next page$/i})
    if(!await next.count()){results.push({id:id+'-pagination-control',passed:false,failures:['Multiple pages require an accessible Next page button.']});break}
    try{await next.first().click({timeout:1500})}catch(error){results.push({id:id+'-next-reachable',passed:false,failures:['Next page is blocked or outside the usable presentation area.'],interactionError:String(error)});break}
    const value=await capture(id+'-page-'+pageNumber,mode,count,columns,false,allowAdaptive)
    if(value.page!==pageNumber){value.passed=false;value.failures.push('Next page control did not advance the selected page.')}
    visited.push(...value.cards.map((card:any)=>card.id));geometry.push(...value.cards)
  }
  if(visited.length!==count||new Set(visited).size!==count||data.slice(0,count).some((item:any)=>!visited.includes(item.id)))results.push({id:id+'-complete-collection',passed:false,failures:['Expected all '+count+' active cards exactly once across pages.'],visited})
  if(variation&&['masonry-rows','masonry-columns'].includes(mode)){const field=mode==='masonry-rows'?'width':'height';const distinct=new Set(geometry.map((card:any)=>Math.round(card[field])));if(distinct.size<2)results.push({id:id+'-masonry-variation',passed:false,failures:['The final masonry composition needs at least two actual card '+field+'s.']})}
  return first
}

async function setInnerWidth(width:number|null){
  return await page.evaluate(width=>{
    document.querySelector('#evaluator-inner-width')?.remove()
    document.querySelectorAll('[data-evaluator-container]').forEach(element=>element.removeAttribute('data-evaluator-container'))
    const surface=[...document.querySelectorAll<HTMLElement>('[data-layout-mode]')].find(e=>{const r=e.getBoundingClientRect();return r.width&&r.height&&getComputedStyle(e).visibility!=='hidden'&&r.left>=0&&r.top>=0})!
    if(width!==null){
      const parent=(surface.closest('.slidev-collection')||surface.parentElement)!;(window as any).__evaluatorContainer={element:parent,width:parent.clientWidth};parent.setAttribute('data-evaluator-container','true')
      const style=document.createElement('style');style.id='evaluator-inner-width';style.textContent='[data-evaluator-container]{width:'+width+'px!important;max-width:'+width+'px!important}[data-evaluator-container]>[data-layout-mode]{max-width:100%!important}';document.head.append(style)
    }else{
      const original=(window as any).__evaluatorContainer
      if(original?.element?.isConnected){original.element.setAttribute('data-evaluator-container','true');const style=document.createElement('style');style.id='evaluator-inner-width';style.textContent='[data-evaluator-container]{width:'+original.width+'px!important;max-width:'+original.width+'px!important}[data-evaluator-container]>[data-layout-mode]{max-width:100%!important}';document.head.append(style)}
    }
    return surface.clientWidth
  },width)
}

try{
  for(let slide=1;slide<=4;slide++)for(let click=0;click<=2;click++){
    const count=[3,7,11][click],columns=[2,3,4][click],id='slide-'+slide+'-click-'+click,mode=modes[slide-1]
    await page.goto(base+'/'+slide+'?clicks='+click,{waitUntil:'networkidle'})
    await page.locator('[data-layout-mode]:visible').first().waitFor({timeout:30000})
    const initial=await walkCollection(id,mode,count,columns,false,true,click===2)
    await setInnerWidth(680)
    await page.waitForTimeout(300)
    const narrow=await walkCollection(id+'-inner-680',mode,count,columns,true,true)
    if(narrow.width>681){narrow.passed=false;narrow.failures.push('The actual native layout frame did not narrow to at most 680 CSS pixels.')}
    await setInnerWidth(null)
    await page.waitForTimeout(300)
    const restored=await walkCollection(id+'-inner-restored',mode,count,columns,false)
    if(Math.abs(restored.width-initial.width)>1){restored.passed=false;restored.failures.push('The actual inner width was not restored.')}
    await page.setViewportSize({width:1024,height:768})
    await capture(id+'-viewport-resize',mode,count,columns)
    await page.setViewportSize({width:1280,height:800})
    await page.emulateMedia({reducedMotion:'reduce'})
    await capture(id+'-reduced-motion',mode,count,columns)
    await page.emulateMedia({reducedMotion:'no-preference'})
  }
  // Verify actual native navigation, rather than treating forged query states as proof of a click story.
  for(let slide=1;slide<=4;slide++){
    await page.goto(base+'/'+slide+'?clicks=0',{waitUntil:'networkidle'})
    await page.locator('[data-layout-mode]:visible').first().waitFor({timeout:30000})
    for(let click=1;click<=2;click++){
      await page.evaluate(()=>document.activeElement instanceof HTMLElement&&document.activeElement.blur())
      await page.keyboard.press('ArrowRight');await page.waitForTimeout(250)
      const url=new URL(page.url())
      if(url.pathname!=='/'+slide||Number(url.searchParams.get('clicks'))!==click)results.push({id:'slide-'+slide+'-native-click-'+click,passed:false,failures:['Native ArrowRight did not advance the requested Slidev click on the same slide.'],url:page.url()})
      else await capture('slide-'+slide+'-native-click-'+click,modes[slide-1],[3,7,11][click],[2,3,4][click])
    }
  }
}catch(error){errors.push(String(error));results.push({id:'native-execution',passed:false,failures:['Native qualification could not complete.'],executionError:String(error)})}finally{await browser.close();await new Promise<void>(r=>server.close(()=>r()))}
const report={passed:results.every(r=>r.passed)&&!errors.length,evaluatorSha256,deck,sourceHashes:hashes,cases:results,errors}
await writeFile(path.join(output,'verification.json'),JSON.stringify(report,null,2))
console.log(JSON.stringify({passed:report.passed,evaluatorSha256,cases:results.length,failed:results.filter(r=>!r.passed).map(({id,failures})=>({id,failures})),errors,sourceHashes:hashes,report:path.join(output,'verification.json')},null,2))
if(!report.passed)process.exitCode=1
