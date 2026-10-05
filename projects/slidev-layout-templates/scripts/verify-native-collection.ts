#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-layout-templates/scripts/verify-native-collection.ts --template skills/slidev-echarts/assets/templates/slidev-layouts
// Dependencies: Node >=24; @slidev/cli, @slidev/theme-default, Vue and Playwright from --dependencies (the owning fixture by default).
// Evaluator-owned native tests. Generated decks, builds, JSON and screenshots stay in ignored project artifacts.
import { readFile, writeFile, mkdir, cp, symlink, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import { spawn } from 'node:child_process'
import http from 'node:http'

const args = process.argv.slice(2)
const smoke = args.includes('--smoke')
function argument(name: string, fallback = '') { const index = args.indexOf(name); return index < 0 ? fallback : args[index + 1] }
const root = process.cwd()
const template = path.resolve(argument('--template', 'skills/slidev-echarts/assets/templates/slidev-layouts'))
const dependencies = path.resolve(argument('--dependencies', 'skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const output = path.resolve(argument('--output', 'projects/slidev-layout-templates/artifacts/native-collection'))
const deck = path.join(output, 'deck'), html = path.join(output, 'html')
const require = createRequire(path.join(dependencies, '../package.json'))
const { chromium } = require('playwright')
const palettes = JSON.parse(await readFile(path.resolve(argument('--palette-source', 'skills/slidev-echarts/assets/palettes/colorsets.json')), 'utf8')).colorsets
const sourceFiles = ['components/SlidevCollection.vue', 'components/SlidevLayout.vue', 'lib/slidev-layouts.mjs']
const sourceHashes: Record<string, string> = {}
await mkdir(path.join(deck, 'components'), { recursive: true }); await mkdir(path.join(deck, 'lib'), { recursive: true })
for (const file of sourceFiles) {
  const bytes = await readFile(path.join(template, file))
  sourceHashes[file] = createHash('sha256').update(bytes).digest('hex')
  await cp(path.join(template, file), path.join(deck, file))
}
for (const [flag, file] of [['--expect-layout-sha', 'components/SlidevLayout.vue'], ['--expect-helper-sha', 'lib/slidev-layouts.mjs'], ['--expect-collection-sha', 'components/SlidevCollection.vue']]) {
  if (argument(flag) && argument(flag) !== sourceHashes[file]) throw new Error(`${file} differs from the requested frozen digest.`)
}
const titles = ['Plan', 'Research', 'Design', 'Build', 'Measure', 'Review', 'Release', 'Support', 'Learn', 'Improve', 'Share']
const bodies = [
  'Set the outcome and agree on clear evidence of progress.',
  'Collect useful evidence from interviews, source documents, and observed behavior.',
  'Build a small prototype.',
  'Ship a working increment, keep the scope focused, and record the decisions behind the implementation.',
  'Track the same metric before and after the change.',
  'Review facts and usability, then resolve the remaining questions.',
  'Publish the approved work.',
  'Answer the next question with the complete evidence.',
  'Record what changed and why.',
  'Use the result to select the next experiment.',
  'Share the decision and the next step.',
]
const items = titles.map((title, index) => ({ id: `card-${String(index + 1).padStart(2, '0')}`, title, body: bodies[index] }))
await writeFile(path.join(deck, 'package.json'), JSON.stringify({ private: true, type: 'module', dependencies: { '@slidev/cli': '52.16.0', '@slidev/theme-default': '0.25.0', vue: '3.5.38' } }, null, 2))
await writeFile(path.join(deck, 'slides.md'), '---\ntheme: default\nlayout: none\nfonts:\n  sans: Open Sans\n---\n\n<CollectionCase />\n')
await writeFile(path.join(deck, 'components/CollectionCase.vue'), `<script setup>
import { computed, reactive, onMounted, nextTick } from 'vue'
import SlidevCollection from './SlidevCollection.vue'
const source = ${JSON.stringify(items)}
const state = reactive({ count:3, mode:'columns', columns:2, rows:3, width:880, height:330, gap:12, minItemWidth:180, minItemHeight:72, pageSize:undefined, colorset:'colorset1', reversed:false, filtered:false, manifest:true, oversized:false, lateCopy:false, custom:false, mount:0, ready:false })
const authored = computed(() => source.map((item,index) => state.lateCopy && index===3 ? {...item,body:Array.from({length:5},()=> 'Preserve the evidence and record the next decision.').join(' ')} : item))
const active = computed(() => {
  if (state.oversized) return [{ id:source[0].id, title:'Individually oversized copy', body:Array.from({length:80},(_,index)=>'Sentence '+(index+1)+': Preserve every requested word.').join(' ') }]
  let selected=authored.value.slice(0,state.count)
  if (state.filtered) selected=selected.filter((_,index)=>index%2===0)
  if (state.reversed) selected=[...selected].reverse()
  return selected
})
const full = computed(() => state.oversized ? active.value : state.reversed ? [...authored.value].reverse() : authored.value)
const presented = computed(() => state.filtered ? active.value : full.value)
onMounted(async () => {
  window.__collectionCase={ state, source, authored, active, async set(change) {
    state.ready=false; Object.assign(state,change); await nextTick(); await document.fonts.ready
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))
    state.ready=true
  } }
  await window.__collectionCase.set({})
})
</script>
<template>
  <main id="collection-case" :style="{width:state.width+'px'}">
    <h1>Collection runtime verification</h1>
    <SlidevCollection :key="state.mount" :items="presented" :count="state.filtered ? active.length : state.count" :mode="state.mode" :columns="state.columns" :rows="state.rows" :height="state.height" :gap="state.gap" :min-item-width="state.minItemWidth" :min-item-height="state.minItemHeight" :page-size="state.pageSize" :colorset="state.colorset" :category-order="state.manifest ? source.map(item=>item.id) : undefined" label="Delivery collection">
      <template v-if="state.custom" #item="{ item, color, box }">
        <div data-fixed-slot="true" :style="{width:box.contentWidth+'px',height:box.contentHeight+'px',fontFamily:'Open Sans, Arial, sans-serif',color:color.ink}">
          <h3 style="font-size:16px;line-height:1.2;margin:0 0 6px;opacity:1;color:inherit">{{ item.title }}</h3>
          <svg :width="box.contentWidth" :height="Math.max(1,box.contentHeight-26)" role="img" :aria-label="item.title+' metric'" style="display:block;color:inherit"><text x="0" y="18" style="font-size:14px;font-family:inherit" fill="currentColor">Evidence</text><path :d="'M0 30H'+Math.max(1,box.contentWidth)" stroke="currentColor" stroke-width="2" opacity="1"/><path :d="'M0 30H'+Math.max(1,box.contentWidth*.65)" stroke="currentColor" stroke-width="6" opacity="1"/></svg>
        </div>
      </template>
    </SlidevCollection>
  </main>
</template>
<style scoped>
#collection-case{position:absolute;left:40px;top:24px;font-family:'Open Sans',Arial,sans-serif;color:#000000;background:#ffffff}
h1{font-size:24px;line-height:1.3;margin:0 0 16px;color:#000000}
</style>
`)
if (!existsSync(path.join(deck, 'node_modules'))) await symlink(dependencies, path.join(deck, 'node_modules'), 'junction')
if (!args.includes('--skip-build')) {
  const build = await new Promise<{ code: number, log: string }>(resolve => {
    const child = spawn(process.execPath, [require.resolve('@slidev/cli/bin/slidev.mjs'), 'build', 'slides.md', '--base', './', '--out', html], { cwd: deck, windowsHide: true, env: { ...process.env, NODE_ENV:'production' } })
    let log = ''; child.stdout.on('data', data => log += data); child.stderr.on('data', data => log += data)
    child.on('close', code => resolve({ code:code ?? 1, log }))
  })
  await writeFile(path.join(output,'build.log'), build.log)
  if (build.code) throw new Error(`Native collection fixture build failed; inspect ${path.join(output,'build.log')}`)
}
const mime: Record<string,string> = { '.html':'text/html', '.js':'text/javascript', '.mjs':'text/javascript', '.css':'text/css', '.json':'application/json', '.svg':'image/svg+xml', '.woff2':'font/woff2' }
const server = http.createServer(async (request,response) => {
  try {
    let candidate = path.resolve(html, `.${decodeURIComponent(new URL(request.url || '/', 'http://local').pathname)}`)
    if (!candidate.startsWith(html+path.sep) && candidate !== html) { response.writeHead(403).end(); return }
    if (!existsSync(candidate) || (await stat(candidate)).isDirectory()) candidate=path.join(html,'index.html')
    response.writeHead(200,{'content-type':mime[path.extname(candidate)] || 'application/octet-stream'}).end(await readFile(candidate))
  } catch(error) { response.writeHead(500).end(String(error)) }
})
await new Promise<void>(resolve=>server.listen(0,'127.0.0.1',resolve))
const port=(server.address() as {port:number}).port
const browser=await chromium.launch({headless:true})
const page=await browser.newPage({viewport:{width:1280,height:800}})
const errors: string[] = [], wakeLocks: string[] = [], cases: any[] = [], sequences: any[] = []
page.on('pageerror',(error:Error)=>String(error).includes('Wake Lock permission request denied')?wakeLocks.push(String(error)):errors.push(String(error)))
page.on('console',(message:any)=>{ if (message.type()==='error' && !message.text().includes('Wake Lock permission request denied')) errors.push(message.text()) })

async function settle() {
  let previous='', stable=0
  for (let attempt=0;attempt<30;attempt++) {
    const current=await page.evaluate(()=>{
      const owner=document.querySelector<HTMLElement>('[data-collection-page]')
      const frame=owner?.querySelector<HTMLElement>('[data-layout-mode]')
      if(owner?.dataset.collectionQualified==='false' || owner?.dataset.collectionFits==='pending')return 'pending-'+performance.now()
      return JSON.stringify([owner?.dataset,frame?.dataset,[...frame?.querySelectorAll('[data-item-id]') || []].map(element=>[element.getAttribute('data-item-id'),(element as HTMLElement).clientWidth,(element as HTMLElement).clientHeight])])
    })
    stable=current===previous?stable+1:0; previous=current
    if (stable>=2) return
    await page.waitForTimeout(80)
  }
  throw new Error('Collection geometry did not settle in 2.4 seconds.')
}
async function change(values: any) { await page.evaluate(values=>(window as any).__collectionCase.set(values),values); await settle() }
async function capture(id: string, negative=false, screenshot=false) {
  const colorset=await page.evaluate(()=>(window as any).__collectionCase.state.colorset)
  const expectedPalette=palettes[colorset]
  const result=await page.evaluate(({allowed,sequence,textOnFill,negative})=>{
    const owner=(window as any).__collectionCase, state={...owner.state}
    const parent=document.querySelector<HTMLElement>('[data-collection-page]')!
    const frame=parent.querySelector<HTMLElement>('[data-layout-mode]')!
    const outer=parent.getBoundingClientRect(), frameBounds=frame.getBoundingClientRect()
    const scale=frameBounds.width/frame.clientWidth, failures:string[]=[], glyphs:any[]=[], paints:any[]=[], fonts:any[]=[]
    const normalize=(r:DOMRect)=>({x:(r.left-frameBounds.left)/scale,y:(r.top-frameBounds.top)/scale,width:r.width/scale,height:r.height/scale})
    function hex(css:string) {
      const channels=css.match(/[\d.]+/g)?.map(Number)
      if (css.startsWith('rgb') && channels && channels.length>=3) return channels.length>3 && channels[3]!==1 ? null : '#'+channels.slice(0,3).map(n=>Math.round(n).toString(16).padStart(2,'0')).join('')
      return /^#[0-9a-f]{6}$/i.test(css)?css.toLowerCase():null
    }
    function luminance(color:string) { const channels=color.slice(1).match(/../g)!.map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4); return channels[0]*.2126+channels[1]*.7152+channels[2]*.0722 }
    function contrast(a:string,b:string) { const x=luminance(a),y=luminance(b); return (Math.max(x,y)+.05)/(Math.min(x,y)+.05) }
    function effectiveOpacity(element:Element) { let value=1; for(let ancestor:Element|null=element;ancestor;ancestor=ancestor.parentElement) value*=Number(getComputedStyle(ancestor).opacity); return value }
    function backing(element:Element) { for(let ancestor:Element|null=element;ancestor;ancestor=ancestor.parentElement) { const fill=hex(getComputedStyle(ancestor).backgroundColor); if(fill)return fill } return null }
    function auditText(element:HTMLElement|SVGElement,card:HTMLElement|null) {
      const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT); let node=walker.nextNode()
      while(node) {
        if(node.textContent?.trim()) {
          const label=node.parentElement!, css=getComputedStyle(label), ink=label instanceof SVGElement?hex(css.fill):hex(css.color), fill=backing(label), opacity=effectiveOpacity(label)
          if(opacity!==1)failures.push('Text effective opacity is not 1: '+node.textContent)
          if(!ink || !allowed.includes(ink))failures.push('Text uses undeclared paint: '+ink)
          if(!fill || !ink || ink!==textOnFill[fill] || contrast(ink,fill)<4.5) failures.push('Text does not use opaque maximum black/white contrast on its actual backing: '+node.textContent)
          if(!css.fontFamily.includes('Open Sans'))failures.push('Text font family is not Open Sans: '+css.fontFamily)
          if(card) {
            const expected=label.closest('h3')?16:14
            if(parseFloat(css.fontSize)!==expected)failures.push('Declared '+expected+'px typography was changed to '+css.fontSize)
            fonts.push({text:node.textContent,size:css.fontSize,family:css.fontFamily})
          }
          const boundary=(card || parent).getBoundingClientRect(), text=node.textContent!
          for(let offset=0;offset<text.length;offset++) {
            if(!text[offset].trim())continue
            const range=document.createRange();range.setStart(node,offset);range.setEnd(node,offset+1)
            for(const r of range.getClientRects())if(r.left<boundary.left-.75 || r.top<boundary.top-.75 || r.right>boundary.right+.75 || r.bottom>boundary.bottom+.75)glyphs.push({text:text[offset],content:text,bounds:normalize(r as DOMRect)})
          }
        }
        node=walker.nextNode()
      }
    }
    const rendered=[...frame.querySelectorAll<HTMLElement>('[data-item-id]')].map(element=>{
      const css=getComputedStyle(element), fill=hex(css.backgroundColor), ink=hex(css.color), id=element.dataset.itemId!, natural=owner.authored.value.find((item:any)=>item.id===id)
      const index=owner.source.findIndex((item:any)=>item.id===id)
      if(fill!==sequence.filter((v:string)=>v!=='#ffffff')[index])failures.push(id+': category paint differs from its complete-manifest index')
      if(ink!==textOnFill[fill!])failures.push(id+': inside ink does not maximize black/white contrast')
      if(effectiveOpacity(element)!==1)failures.push(id+': card fill is translucent')
      if(!allowed.includes(fill) || !allowed.includes(ink))failures.push(id+': undeclared card paint')
      if(parseFloat(css.borderTopWidth)!==0)failures.push(id+': premature decorative category border')
      if(!state.custom && !state.oversized && (!element.textContent?.includes(natural?.title)||!element.textContent?.includes(natural?.body)))failures.push(id+': full requested copy was not preserved')
      const rect=element.getBoundingClientRect()
      if(!negative && (rect.left<frameBounds.left-.75 || rect.top<frameBounds.top-.75 || rect.right>frameBounds.right+.75 || rect.bottom>frameBounds.bottom+.75))failures.push(id+': card crosses frame')
      auditText(element,element)
      paints.push({id,fill,ink})
      return {id,category:element.dataset.categoryId,row:Number(element.dataset.row),column:Number(element.dataset.column),fill,ink,...normalize(rect)}
    })
    const overlaps:any[]=[]
    for(let i=0;i<rendered.length;i++)for(let j=i+1;j<rendered.length;j++){const a=rendered[i],b=rendered[j];if(Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>.5 && Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>.5)overlaps.push([a.id,b.id])}
    if(overlaps.length)failures.push('Card pairs overlap.')
    if(glyphs.length && !negative)failures.push(glyphs.length+' individual glyphs cross their card/pager boundaries.')
    const fits=frame.dataset.layoutFits==='true'
    if(negative?fits:!fits)failures.push(negative?'Individually oversized content claims to fit.':'Delivered collection state does not fit.')
    if(!negative && (outer.left<0 || outer.top<0 || outer.right>innerWidth+.75 || outer.bottom>innerHeight+.75))failures.push('Collection including pager crosses the viewport.')
    if(parent.clientWidth!==state.width || frame.clientWidth!==state.width)failures.push('Requested real inner width was not applied.')
    const currentPage=Number(parent.dataset.collectionPage), totalPages=Number(parent.dataset.collectionPages), budget=Number(parent.dataset.collectionBudget), count=Number(parent.dataset.collectionCount), columns=Number(parent.dataset.collectionColumns)
    if(parent.dataset.collectionMode!==state.mode || parent.dataset.colorset!==state.colorset || frame.dataset.layoutMode!==state.mode || frame.dataset.colorset!==state.colorset)failures.push('Mode or palette metadata is stale.')
    if(parent.dataset.collectionFits!==String(fits))failures.push('Public parent capacity disagrees with the native frame.')
    if(columns!==Math.min(state.columns,Math.max(1,Math.floor((state.width+state.gap)/(state.minItemWidth+state.gap)))))failures.push('Effective columns do not clamp the requested columns to the actual readable-width capacity.')
    if(!Number.isInteger(currentPage)||!Number.isInteger(totalPages)||!Number.isInteger(budget)||budget<1)failures.push('Collection pagination metadata is invalid.')
    if(Number(frame.dataset.page)!==currentPage || Number(frame.dataset.pages)!==totalPages)failures.push('Parent and native page metadata disagree.')
    const selected=state.oversized?[{id:owner.source[0].id}]:state.filtered?owner.active.value:state.reversed?[...owner.source].reverse().slice(0,state.count):owner.source.slice(0,state.count)
    if(count!==selected.length)failures.push('Collection count metadata differs from selected items.')
    if(totalPages!==Math.max(1,Math.ceil(selected.length/budget)))failures.push('Collection page count does not match its budget.')
    if(JSON.stringify(rendered.map(item=>item.id))!==JSON.stringify(selected.slice((currentPage-1)*budget,currentPage*budget).map((item:any)=>item.id)))failures.push('Native source order/page selection differs from current collection budget.')
    const pager=[...parent.querySelectorAll<HTMLButtonElement>('[data-page-action]')].map(button=>{
      const css=getComputedStyle(button),fill=hex(css.backgroundColor),ink=hex(css.color)
      if(!allowed.includes(fill)||!allowed.includes(ink))failures.push('Pager uses undeclared palette paint.')
      if(fill!==(button.disabled?'#e7e7e7':'#9e1b32') || ink!==(button.disabled?'#000000':'#ffffff'))failures.push('Pager differs from shared exact primary/on-primary or quiet/ink tokens.')
      if(!button.disabled && (effectiveOpacity(button)!==1 || contrast(fill!,ink!)<4.5))failures.push('Active pager label loses opacity or contrast.')
      if(!css.fontFamily.includes('Open Sans'))failures.push('Pager font family differs from Open Sans.')
      if(parseFloat(css.fontSize)!==14)failures.push('Pager typography changed from its declared 14px size.')
      if(button.getAttribute('aria-label')!==(button.dataset.pageAction==='previous'?'Previous page':'Next page'))failures.push('Pager action lacks its exact accessible label.')
      return {action:button.dataset.pageAction,disabled:button.disabled,fill,ink,opacity:effectiveOpacity(button),label:button.getAttribute('aria-label')||button.textContent}
    })
    if(!pager.some(button=>button.action==='previous') || !pager.some(button=>button.action==='next'))failures.push('Both accessible pager actions are missing.')
    for(const button of pager)if(button.disabled!==(button.action==='previous'?currentPage===1:currentPage===totalPages))failures.push('Pager disabled state disagrees with page metadata.')
    const nav=parent.querySelector('nav'); if(nav)auditText(nav as HTMLElement,null)
    if(state.mode==='masonry-rows'){
      if(Number(frame.dataset.configuredRows)!==state.rows)failures.push('Horizontal masonry changed its literal configured row count.')
      if(rendered.length>=state.rows && new Set(rendered.map(card=>card.row)).size!==state.rows)failures.push('A complete horizontal masonry page does not occupy all literal rows.')
      for(const row of new Set(rendered.map(card=>card.row))){const members=rendered.filter(card=>card.row===row);if(Math.max(...members.map(card=>card.y))-Math.min(...members.map(card=>card.y))>.5)failures.push('Horizontal masonry cards are not aligned on their literal row.')}
    }
    if(state.mode==='grid' && rendered.length && Math.max(...rendered.map(card=>card.height))-Math.min(...rendered.map(card=>card.height))>.5)failures.push('Grid cards do not share one uniform selected-page height.')
    const animations=parent.getAnimations({subtree:true}).map(animation=>({playState:animation.playState,duration:animation.effect?.getComputedTiming().duration}))
    if(matchMedia('(prefers-reduced-motion: reduce)').matches && animations.some(animation=>animation.playState==='running'&&Number(animation.duration)>0))failures.push('Reduced-motion state retains running motion.')
    const slot=[...parent.querySelectorAll<HTMLElement>('[data-fixed-slot]')].map(element=>({width:element.clientWidth,height:element.clientHeight,card:element.closest('[data-item-id]')?.getAttribute('data-item-id')}))
    if(state.custom&&slot.length!==rendered.length)failures.push('The complete custom slot was not rendered for every card.')
    const accessibleNegative=negative?{containsAllCopy:frame.textContent?.includes(selected.length===1?(state.oversized?Array.from({length:80},(_,index)=>'Sentence '+(index+1)+': Preserve every requested word.').join(' '):''):''),overflow:getComputedStyle(frame).overflow,scrollHeight:frame.scrollHeight,clientHeight:frame.clientHeight,scrollWidth:frame.scrollWidth,clientWidth:frame.clientWidth,role:frame.getAttribute('role'),label:frame.getAttribute('aria-label'),tabIndex:frame.tabIndex,budget}:null
    if(negative && (!accessibleNegative?.containsAllCopy || !['auto','scroll'].includes(accessibleNegative.overflow) || accessibleNegative.scrollHeight<=accessibleNegative.clientHeight || budget!==1 || accessibleNegative.tabIndex!==0 || accessibleNegative.role!=='region' || !accessibleNegative.label))failures.push('Oversized copy is not fully retained in an accessible single-card scrolling fallback.')
    return {passed:failures.length===0,failures,state,fits,page:currentPage,pages:totalPages,budget,count,columns,configuredRows:Number(frame.dataset.configuredRows),occupiedRows:Number(frame.dataset.occupiedRows),width:frame.clientWidth,height:frame.clientHeight,requiredWidth:Number(frame.dataset.requiredWidth),requiredHeight:Number(frame.dataset.requiredHeight),cards:rendered,pager,fonts,glyphs,overlaps,paints,animations,slot,accessibleNegative}
  },{allowed:expectedPalette.allowed,sequence:expectedPalette.solidSequence,textOnFill:expectedPalette.textOnFill,negative})
  Object.assign(result,{id,negative})
  cases.push(result)
  if(screenshot || (!result.passed && cases.filter(value=>!value.passed).length<=20))await page.screenshot({path:path.join(output,id+'.png'),fullPage:true})
  return result
}
async function walk(id:string, values:any, screenshot=false) {
  await change(values)
  // Always navigate through the public native controls, including after a count/filter reset.
  for(let guard=0;guard<20 && await page.locator('[data-page-action="previous"]').isEnabled();guard++) { await page.locator('[data-page-action="previous"]').click(); await settle() }
  const visited:string[]=[], identity:Record<string,string>={}, geometry:any[]=[]
  for(let pageNumber=1;pageNumber<=20;pageNumber++) {
    const value=await capture(id+'-page-'+pageNumber,false,screenshot&&pageNumber===1)
    visited.push(...value.cards.map((card:any)=>card.id)); for(const card of value.cards){identity[card.id]=card.fill;geometry.push({id:card.id,width:card.width,height:card.height})}
    if(await page.locator('[data-page-action="next"]').isDisabled())break
    await page.locator('[data-page-action="next"]').click();await settle()
  }
  const expected=await page.evaluate(()=>{const owner=(window as any).__collectionCase;return owner.state.filtered?owner.active.value.map((item:any)=>item.id):(owner.state.reversed?[...owner.source].reverse():owner.source).slice(0,owner.state.count).map((item:any)=>item.id)})
  const sequence={id,passed:JSON.stringify(visited)===JSON.stringify(expected)&&new Set(visited).size===visited.length,expected,visited,identity,geometry}
  sequences.push(sequence)
  console.log(JSON.stringify({sequence:id,pages:visited.length===0?0:cases[cases.length-1].pages,items:visited.length,passed:sequence.passed}))
  return sequence
}

try {
  await page.goto(`http://127.0.0.1:${port}/1`,{waitUntil:'networkidle'});await page.waitForFunction(()=>(window as any).__collectionCase?.state.ready,{timeout:30000});await settle()
  await page.emulateMedia({colorScheme:'light',reducedMotion:'no-preference'})
  for(const colorset of ['colorset1','colorset2'])for(const mode of ['columns','grid','masonry-columns','masonry-rows'])for(const count of [3,7,11])for(const width of [880,680,480]) {
    if(smoke && (colorset!=='colorset1' || count!==11 || width===680))continue
    const columns=count===3?2:count===7?3:4
    const collection=await walk(`${colorset}-${mode}-${count}-${width}`,{colorset,mode,count,columns,width,height:330,reversed:false,filtered:false,manifest:true,oversized:false,custom:false},count===11&&width===880)
    if(count===11&&width===880&&mode==='masonry-columns' && Math.max(...collection.geometry.map((card:any)=>card.height))-Math.min(...collection.geometry.map((card:any)=>card.height))<20) {collection.passed=false;(collection as any).failure='Final eleven-card column masonry does not preserve meaningful natural-height variation.'}
    if(count===11&&mode==='masonry-rows' && new Set(collection.geometry.map((card:any)=>Math.round(card.width))).size<3) {collection.passed=false;(collection as any).failure='Final eleven-card row masonry does not demonstrate variable preferred widths.'}
  }
  for(const colorset of ['colorset1','colorset2'])for(const mode of ['columns','grid','masonry-columns','masonry-rows']) {
    if(smoke)continue
    await walk(`${colorset}-${mode}-continuity-base`,{colorset,mode,count:11,columns:4,width:480,reversed:false,filtered:false,manifest:true})
    await walk(`${colorset}-${mode}-continuity-reverse`,{reversed:true})
    await walk(`${colorset}-${mode}-continuity-filter`,{reversed:false,filtered:true})
    await walk(`${colorset}-${mode}-continuity-restore`,{count:3,columns:2,filtered:false})
    // Omitted manifest must still allocate against the complete supplied collection before count/pagination.
    const freshMount=await page.evaluate(()=>(window as any).__collectionCase.state.mount+1)
    await walk(`${colorset}-${mode}-full-source-registry-hidden`,{count:3,columns:2,manifest:false,reversed:false,mount:freshMount})
    await walk(`${colorset}-${mode}-full-source-registry`,{count:11,columns:4,reversed:true})
  }
  for(const media of [{colorScheme:'dark',reducedMotion:'no-preference'}, {colorScheme:'dark',reducedMotion:'reduce'}]) {
    if(smoke)continue
    await page.emulateMedia(media)
    for(const colorset of ['colorset1','colorset2'])for(const mode of ['columns','grid','masonry-columns','masonry-rows'])await walk(`${colorset}-${mode}-${media.reducedMotion==='reduce'?'reduced-motion':'dark'}`,{colorset,mode,count:11,columns:4,width:480,reversed:false,filtered:false,manifest:true,oversized:false,custom:false})
  }
  await page.emulateMedia({colorScheme:'light',reducedMotion:'no-preference'})
  // A genuinely taller later card must qualify before the first page, not silently repartition visited IDs.
  for(const colorset of ['colorset1','colorset2'])for(const width of [880,480]){
    const freshLongMount=await page.evaluate(()=>(window as any).__collectionCase.state.mount+1)
    await walk(`${colorset}-later-copy-${width}`,{colorset,mode:'masonry-rows',count:11,columns:4,width,rows:3,height:330,gap:12,minItemWidth:180,minItemHeight:72,pageSize:undefined,reversed:false,filtered:false,manifest:true,oversized:false,lateCopy:true,custom:false,mount:freshLongMount},true)
  }
  await change({lateCopy:false})
  // Real outer-width and semantic-setting edits must reset desired capacity without a feedback loop.
  for(const mode of ['columns','grid','masonry-columns','masonry-rows']){
    if(smoke)continue
    await walk(`${mode}-settings-baseline`,{mode,colorset:'colorset1',count:11,columns:4,width:480,rows:3,height:330,gap:12,minItemWidth:180,minItemHeight:72,pageSize:undefined,reversed:false,filtered:false,manifest:true,oversized:false,custom:false})
    for(const [name,values] of [['page-size',{pageSize:1}],['huge-page-size',{pageSize:100000}],['rows',{pageSize:undefined,rows:2}],['height',{height:350}],['gap',{gap:16}],['minimum-width',{minItemWidth:200}],['minimum-height',{minItemHeight:80}],['width-grow',{width:880}],['width-restore',{width:480}],['restore',{rows:3,height:330,gap:12,minItemWidth:180,minItemHeight:72}]] as [string,any][]){
      await walk(`${mode}-settings-${name}`,values)
      const first=cases[cases.length-1]
      if(name==='page-size'&&first.budget!==1){first.passed=false;first.failures.push('Changing explicit pageSize did not reset the desired budget.')}
      if(name==='huge-page-size'){
        if(first.budget>first.count){first.passed=false;first.failures.push('Desired pageSize 100000 was not bounded by the active item count.')}
        const initialBudget=first.budget
        for(let tick=1;tick<=3;tick++){await settle();const value=await capture(`${mode}-huge-budget-settle-${tick}`);if(value.budget!==initialBudget){value.passed=false;value.failures.push('Settled huge desired page budget continued changing.')}}
      }
    }
  }
  for(const colorset of ['colorset1','colorset2']) {
    const freshCustomMount=await page.evaluate(()=>(window as any).__collectionCase.state.mount+1)
    await walk(`${colorset}-custom-budget-880`,{colorset,mode:'grid',count:3,columns:3,width:880,rows:3,height:330,gap:12,minItemWidth:180,minItemHeight:72,pageSize:undefined,reversed:false,filtered:false,manifest:true,oversized:false,custom:true,mount:freshCustomMount},true)
    await walk(`${colorset}-custom-budget-480`,{width:480},true)
    const first=await capture(`${colorset}-custom-settle-start`)
    for(let tick=1;tick<=3;tick++){await settle();const value=await capture(`${colorset}-custom-settle-${tick}`);if(JSON.stringify(value.slot)!==JSON.stringify(first.slot)){value.passed=false;value.failures.push('Fixed inner content-budget slot grew during repeated settling.')}}
    await change({colorset,mode:'grid',count:1,columns:1,width:480,height:330,oversized:true,custom:false})
    const negative=await capture(`${colorset}-negative-individual-copy`,true,true)
    await page.locator('[data-layout-mode]').focus();await page.keyboard.press('End');await page.waitForTimeout(500)
    const keyboard=await page.locator('[data-layout-mode]').evaluate(element=>({focused:document.activeElement===element,scrollTop:element.scrollTop,lastSentenceVisible:(()=>{const p=element.querySelector('p')!,node=p.firstChild!,range=document.createRange();range.setStart(node,node.textContent!.length-1);range.setEnd(node,node.textContent!.length);const glyph=range.getBoundingClientRect(),bounds=element.getBoundingClientRect();return glyph.top>=bounds.top && glyph.bottom<=bounds.bottom})()}))
    Object.assign(negative.accessibleNegative,{keyboard})
    if(!keyboard.focused || keyboard.scrollTop<=0 || !keyboard.lastSentenceVisible){negative.passed=false;negative.failures.push('Keyboard focus/End did not make the last oversized sentence reachable inside its region.')}
  }
} catch(error) {errors.push(String(error))}
finally {await browser.close();await new Promise<void>(resolve=>server.close(()=>resolve()))}
const report={date:new Date().toISOString(),profile:smoke?'smoke':'full',passed:cases.every(value=>value.passed)&&sequences.every(value=>value.passed)&&errors.length===0,sourceHashes,template,dependencies,cases,sequences,errors,wakeLocks}
await writeFile(path.join(output,'verification.json'),JSON.stringify(report,null,2)+'\n')
console.log(JSON.stringify({passed:report.passed,cases:cases.length,sequences:sequences.length,failures:cases.filter(value=>!value.passed).map(({id,failures})=>({id,failures})),failedSequences:sequences.filter(value=>!value.passed).map(({id,expected,visited,failure})=>({id,expected,visited,failure})),errors,sourceHashes,report:path.join(output,'verification.json')},null,2))
if(!report.passed)process.exitCode=1
