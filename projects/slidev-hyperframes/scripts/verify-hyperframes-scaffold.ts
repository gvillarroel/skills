#!/usr/bin/env -S node --experimental-strip-types
// Run: node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-hyperframes-scaffold.ts
// Uses owning fixture's existing qualified dependency tree; the independent release golden installs its own submitted package.
import { createRequire } from 'node:module'
import { resolve, join, relative } from 'node:path'
import { mkdir, mkdtemp, readFile, writeFile, symlink } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { createServer } from 'node:http'
import { stat } from 'node:fs/promises'
import { pathToFileURL } from 'node:url'
import assert from 'node:assert/strict'

const root = resolve(import.meta.dirname, '../../..')
const output = resolve(root, 'projects/slidev-hyperframes/artifacts/scaffold-native')
await mkdir(output, { recursive: true })
const run = await mkdtemp(join(output, 'run-')), deck = join(run, 'deck')
const owner = resolve(root, 'skills/slidev-echarts')
const dependencies = join(owner, 'assets/examples/slidev-echarts/node_modules')
const require = createRequire(join(dependencies, '../package.json'))
const { chromium } = require('playwright')
const execute = promisify(execFile)
const checks = [], errors = [], requests = [], commands = []
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
for (const [name, version] of Object.entries({ mermaid:'11.15.0', '@slidev/types':'52.16.0', '@hyperframes/player':'0.8.134', vue:'3.5.38' }))
  assert.equal(JSON.parse(await readFile(join(dependencies, name, 'package.json'), 'utf8')).version, version)
const generator = await execute('uv', ['run','--script',join(owner,'scripts/scaffold_hyperframes_deck.py'),'--deck',deck], { cwd:root, maxBuffer:1_000_000 })
await writeFile(join(run, 'generation.log'), generator.stdout+generator.stderr)
await symlink(dependencies, join(deck, 'node_modules'), 'junction')
const original = JSON.parse(await readFile(resolve(root, 'projects/slidev-hyperframes/artifacts/frozen-runtime-candidate-epoch2.json'), 'utf8'))['slidev-echarts'].files
async function coreUnchanged() {
  for (const [name, record] of Object.entries(original)) {
    if (name.startsWith('references/') || name === 'scripts/check_hyperframes_deck.py') continue
    assert.equal(hash(await readFile(join(deck, name))), record.sha256, name)
  }
}
await coreUnchanged()
const slides = await readFile(join(deck, 'slides.md'), 'utf8')
await writeFile(join(deck, 'slides.md'), slides+'\n---\nlayout: default\n---\n\n# Plain Mermaid diagnostic\n\n```mermaid\nsequenceDiagram\n participant A as Inlet\n participant B as Tank\n A->>B: Transfer\n Note over B: Stored\n```\n\n---\nlayout: default\n---\n\n# Explicit source override diagnostic\n\n```mermaid\nflowchart LR\n A[Source override] --> B[Preserved]\n style A fill:#45842a,stroke:#000000,color:#000000\n```\n')
async function build(label, html=false) {
  const argv = html ? ['--experimental-strip-types','scripts/build-hyperframes-html.ts'] : [join(dependencies,'@slidev/cli/bin/slidev.mjs'),'build','--base','./']
  const result = await execute(process.execPath, argv, {cwd:deck,maxBuffer:30_000_000})
  await writeFile(join(run,label+'.log'),result.stdout+result.stderr)
  commands.push({label,argv,passed:true})
}
await build('colorset1-build')
const mime = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.woff2':'font/woff2','.svg':'image/svg+xml'}
const server = createServer(async(req,res)=>{
  try {
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname)
    let file=resolve(deck,'dist','.'+pathname)
    if (relative(join(deck,'dist'),file).startsWith('..')) throw Error('Outside root')
    if (!(await stat(file).catch(()=>null))?.isFile()) file=join(deck,'dist/index.html')
    const contents=await readFile(file)
    res.writeHead(200,{'Content-Type':mime[file.slice(file.lastIndexOf('.'))]||'application/octet-stream'})
    res.end(contents)
  } catch {res.writeHead(404);res.end('Not found')}
})
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve))
const base='http://127.0.0.1:'+server.address().port
const browser=await chromium.launch({headless:true}), page=await browser.newPage({viewport:{width:1280,height:800}})
page.on('pageerror',error=>errors.push(error.message));page.on('request',request=>requests.push(request.url()))
function check(id, condition, detail={}) {assert.ok(condition,id+': '+JSON.stringify(detail));checks.push({id,...detail})}
async function open(slide,seconds=0) {
  await page.goto(base+'/'+slide+'?clicks=0')
  await page.waitForSelector('.hyperframe-slide:visible[data-ready="true"][data-time="'+seconds+'"]')
}
async function live() {
  const wrapper=page.locator('.hyperframe-slide:visible').first(), iframe=await wrapper.locator('iframe').elementHandle()
  const frame=await iframe.contentFrame(), bounds=await iframe.boundingBox()
  const actual=await frame.evaluate(()=>{
    const scene=document.querySelector('[data-composition-id]'), text=document.querySelector('[data-scene-mark="level-readout"]'), fill=document.querySelector('[data-scene-mark="tank-fill"]'),tank=document.querySelector('[data-scene-mark="tank"]')
    return {time:Number(scene.dataset.sceneTime),level:text.textContent,fill:fill.getAttribute('fill'),fraction:Number(fill.getAttribute('height'))/Number(tank.getAttribute('height')),font:getComputedStyle(text).fontFamily,fontSize:Number.parseFloat(getComputedStyle(text).fontSize),fontLoaded:document.fonts.check('600 24px "Open Sans"'),width:innerWidth}
  })
  return {...actual,effectiveFontSize:actual.fontSize*bounds.width/actual.width}
}
async function control() {
  return page.locator('.hyperframe-preview:visible').first().evaluate(root=>{
    const button=root.querySelector('button'),player=root.querySelector('.hyperframe-slide')
    if(!button)return{count:0,height:root.clientHeight,sceneHeight:player.clientHeight}
    const br=button.getBoundingClientRect(),pr=player.getBoundingClientRect(),style=getComputedStyle(button)
    const hit=document.elementFromPoint(br.x+br.width/2,br.y+br.height/2)
    return {count:1,height:root.clientHeight,sceneHeight:player.clientHeight,buttonHeight:button.clientHeight,gap:br.top-pr.bottom,hit:hit===button||button.contains(hit),font:style.fontFamily,fontSize:style.fontSize,background:style.backgroundColor,ink:style.color,opacity:style.opacity,loaded:document.fonts.check('700 16px "Open Sans"'),disabled:button.disabled}
  })
}
try {
  await open(1)
  for(const [key,seconds]of [['ArrowRight',4],['ArrowRight',9],['ArrowLeft',4],['ArrowLeft',0]]){
    await page.keyboard.press(key);await page.waitForSelector('.hyperframe-slide:visible[data-ready="true"][data-time="'+seconds+'"]')
    const state=await live();check('forward/back actual '+seconds,state.time===seconds&&state.level===(seconds===0?'0%':seconds===4?'20%':'70%'),state)
  }
  const hero=await control(), state=await live()
  check('qualified hero control row',hero.height===378&&hero.sceneHeight===330&&hero.buttonHeight===38&&hero.hit&&hero.loaded&&hero.opacity==='1'&&state.fontLoaded&&state.effectiveFontSize>=14,{hero,state})
  await page.getByRole('button',{name:'Play animation',exact:true}).click()
  await page.waitForFunction(()=>Number(document.querySelector('.hyperframe-preview[data-preview-playing="true"] .hyperframe-slide').dataset.time)>.2)
  const played=(await live()).time
  await page.getByRole('button',{name:'Pause animation',exact:true}).click()
  await page.waitForTimeout(80)
  const pausedAt=(await live()).time
  await page.waitForTimeout(200)
  const afterPause=(await live()).time
  check('preview pause preserves clock',played>0&&pausedAt>=played&&Math.abs(afterPause-pausedAt)<.01,{played,pausedAt,afterPause})
  await page.evaluate(()=>document.activeElement?.blur())
  await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowRight');await page.waitForSelector('.hyperframe-slide:visible[data-time="9"][data-ready="true"]')
  await page.getByRole('button',{name:'Play animation',exact:true}).click();await page.waitForTimeout(250)
  await page.evaluate(()=>document.activeElement?.blur());await page.keyboard.press('ArrowRight')
  await page.waitForSelector('[data-story-variant="cell"]:visible .hyperframe-slide[data-ready="true"]')
  await page.keyboard.press('ArrowLeft');await page.waitForSelector('.hyperframe-slide:visible[data-time="9"][data-ready="true"]')
  check('leave and paused reentry',await page.getByRole('button',{name:'Play animation',exact:true}).isVisible()&&(await live()).time===9)
  await page.emulateMedia({reducedMotion:'reduce'})
  await page.waitForFunction(()=>[...document.querySelectorAll('.hyperframe-preview-control')].some(el=>el.getBoundingClientRect().width>0&&el.disabled))
  check('reduced-motion controls disabled',await page.getByRole('button',{name:'Play animation',exact:true}).isDisabled())
  await page.emulateMedia({reducedMotion:'no-preference'})
  for(const width of [880,680,480]){
    await open(2)
    await page.locator('[data-story-variant="cell"]:visible').evaluate((node,width)=>{node.style.width=width+'px'},width)
    await page.waitForFunction(()=>[...document.querySelectorAll('.slidev-collection')].some(el=>el.getBoundingClientRect().width>0&&el.dataset.collectionQualified==='true'))
    await page.waitForTimeout(250)
    const cards=[]
    while(true){
      const collection=page.locator('.slidev-collection:visible').first()
      const attrs=await collection.evaluate(node=>({fits:node.dataset.collectionFits||node.querySelector('[data-fits]')?.getAttribute('data-fits'),ids:[...node.querySelectorAll('[data-item-id]')].map(el=>el.getAttribute('data-item-id'))}))
      assert.equal(attrs.fits,'true',JSON.stringify(attrs));cards.push(...attrs.ids)
      if(await page.locator('.hyperframe-slide:visible').count()){
        const cell=await live(),button=await control()
        check('cell logical budget '+width,cell.fontLoaded&&cell.effectiveFontSize>=14&&button.hit&&button.sceneHeight>=152&&button.height===button.sceneHeight+48,{cell,button})
      }
      const next=collection.getByRole('button',{name:'Next page',exact:true})
      if(await next.isDisabled())break
      await next.click();await page.waitForTimeout(220)
    }
    check('complete stable cell pagination '+width,JSON.stringify(cards)===JSON.stringify(['mechanism','explanation']),{cards})
    await page.screenshot({path:join(run,'cell-'+width+'.png')})
  }
  await open(3,9)
  check('static controls omitted',(await control()).count===0&&(await live()).fraction===.7)
  await page.screenshot({path:join(run,'static-9.png')})
  for(const selected of ['colorset1','colorset2']){
    if(selected==='colorset2'){
      await page.goto('about:blank')
      const cfg=JSON.parse(await readFile(join(deck,'data/hyperframes-story.json'),'utf8'));cfg.colorset=selected;cfg.titles.hero='Edited JSON title';await writeFile(join(deck,'data/hyperframes-story.json'),JSON.stringify(cfg,null,2)+'\n');await build('colorset2-build')
    }
    await open(1)
    const actual=await live(),button=await control()
    check('starter palette '+selected,actual.fill===(selected==='colorset1'?'#9e1b32':'#007298')&&button.loaded&&button.opacity==='1',{actual,button})
    if(selected==='colorset2')check('JSON heading edits live',await page.locator('.story-heading:visible').textContent()==='Edited JSON title')
    await page.goto(base+'/4');await page.waitForSelector('.slidev-layout:visible svg[aria-roledescription="sequence"]')
    const diagram=await page.locator('.slidev-layout:visible svg[aria-roledescription="sequence"]').evaluate(svg=>({note:getComputedStyle(svg.querySelector('rect.note')).fill,font:getComputedStyle(svg.querySelector('text')).fontFamily,loaded:document.fonts.check('16px "Open Sans"')}))
    check('plain Mermaid shared defaults '+selected,diagram.loaded&&diagram.font.includes('Open Sans')&&(diagram.note===(selected==='colorset1'?'#000000':'#45842a')||diagram.note===(selected==='colorset1'?'rgb(0, 0, 0)':'rgb(69, 132, 42)')),{diagram})
    await page.screenshot({path:join(run,'mermaid-'+selected+'.png')})
    await page.goto(base+'/5');await page.waitForSelector('.slidev-layout:visible svg[aria-roledescription="flowchart-v2"]')
    const override=await page.locator('.slidev-layout:visible svg[aria-roledescription="flowchart-v2"] .node rect').first().evaluate(node=>getComputedStyle(node).fill)
    check('explicit Mermaid source override '+selected,override==='rgb(69, 132, 42)',{override})
  }
  await page.goto('about:blank')
  await build('singlefile-build',true)
  const filePage=await browser.newPage(),fileErrors=[],fileRequests=[]
  filePage.on('pageerror',error=>fileErrors.push(error.message));filePage.on('request',request=>fileRequests.push(request.url()))
  await filePage.goto(pathToFileURL(join(deck,'dist/slidev.html')).href)
  await filePage.waitForSelector('.hyperframe-slide:visible[data-ready="true"][data-source-kind="fallback"]')
  const fallback=await filePage.locator('.hyperframe-preview:visible').evaluate(root=>({controls:root.querySelectorAll('button').length,font:document.fonts.check('700 16px "Open Sans"'),level:root.querySelector('[data-scene-mark="level-readout"]').textContent}))
  check('direct-open default fallback controls/fonts',fallback.controls===0&&fallback.font&&fallback.level==='0%',fallback)
  await filePage.goto(pathToFileURL(join(deck,'dist/slidev.html')).href+'#/3')
  await filePage.waitForSelector('.hyperframe-slide:visible[data-ready="true"][data-time="9"]')
  const final=await filePage.locator('.hyperframe-slide:visible [data-scene-mark="level-readout"]').textContent()
  check('direct-open deterministic static frame',final==='70%'&&fileErrors.length===0&&fileRequests.every(url=>/^(file|data):/.test(url)),{final,fileErrors,external:fileRequests.filter(url=>! /^(file|data):/.test(url))})
  await filePage.screenshot({path:join(run,'file-static-9.png')})
  await coreUnchanged();check('all14 previous core resources unchanged',true)
  check('no browser errors or remote resources',errors.length===0&&requests.every(url=>url.startsWith(base)),{errors,external:requests.filter(url=>!url.startsWith(base))})
  const report={passed:true,checks:checks.length,cases:checks,run,deck,commands,errors,coreUnchanged:true,freshInstall:false,dependencyHost:dependencies}
  await writeFile(join(output,'verification.json'),JSON.stringify(report,null,2)+'\n')
  console.log(JSON.stringify({passed:true,checks:checks.length,report:join(output,'verification.json')},null,2))
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
