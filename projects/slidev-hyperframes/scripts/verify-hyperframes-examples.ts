#!/usr/bin/env -S npx tsx
// Run with Node >=24: node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-hyperframes-examples.ts --base-url dist/pages --output projects/slidev-hyperframes/artifacts/fixture-verification
// Dependencies: Playwright from --dependencies; defaults to the existing ECharts acceptance fixture installation.
// --base-url accepts a published HTTP(S) site root or an owned local Pages-style directory.
// Use --skip-catalog for a source build containing examples/<owner>/ without the main examples index.
// Use --file-html <single-file HTML> to qualify ECharts direct-open fallback and its existing chart route.
import { readFile, writeFile, mkdir, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createRequire } from 'node:module'
import { createHash } from 'node:crypto'
import http from 'node:http'
import { pathToFileURL } from 'node:url'

const args=process.argv.slice(2)
function argument(name:string,fallback=''){const index=args.indexOf(name);return index<0?fallback:args[index+1]}
const input=argument('--base-url','dist/pages')
const output=path.resolve(argument('--output','projects/slidev-hyperframes/artifacts/fixture-verification'))
const dependencies=path.resolve(argument('--dependencies','skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const {chromium}=createRequire(path.join(dependencies,'../package.json'))('playwright')
const palettePath=path.resolve('skills/slidev-echarts/assets/palettes/colorsets.json')
const paletteBytes=await readFile(palettePath)
const colorset=JSON.parse(paletteBytes.toString()).colorsets.colorset1
const tokens=[...new Set<string>(JSON.stringify(colorset).match(/#[0-9a-f]{6}/gi)||[])].map(token=>token.toLowerCase())
await mkdir(output,{recursive:true})
let server:http.Server|undefined
let baseUrl:string
if(/^https?:\/\//i.test(input))baseUrl=new URL(input.endsWith('/')?input:input+'/').href
else {
  const directory=path.resolve(input)
  if(!existsSync(directory))throw Error(`Local build directory does not exist: ${directory}`)
  const mime:Record<string,string>={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.woff':'font/woff','.png':'image/png'}
  server=http.createServer(async(request,response)=>{
    try {
      let file=path.resolve(directory,`.${decodeURIComponent(new URL(request.url||'/','http://local').pathname)}`)
      if(file!==directory&&!file.startsWith(directory+path.sep)){response.writeHead(403).end();return}
      if(!existsSync(file)){response.writeHead(404).end('Not found');return}
      if((await stat(file)).isDirectory())file=path.join(file,'index.html')
      response.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream','cache-control':'no-store'}).end(await readFile(file))
    }catch(error){response.writeHead(500).end(String(error))}
  })
  await new Promise<void>(resolve=>server!.listen(0,'127.0.0.1',resolve))
  baseUrl=`http://127.0.0.1:${(server.address() as {port:number}).port}/`
}
const browser=await chromium.launch({headless:true})
const states:any[]=[],errors:string[]=[],messages:any[]=[],catalog:any[]=[],captures:any[]=[],sceneRequests:any[]=[]
const cueTimes=[0,3,6,9]
const cueModels=[{level:0,parcel:0,open:false},{level:10,parcel:.125,open:true},{level:40,parcel:.5,open:true},{level:70,parcel:.875,open:true}]
function collect(page:any,surface:string){
  page.on('pageerror',(error:Error)=>messages.push({surface,type:'pageerror',message:String(error)}))
  page.on('console',(message:any)=>{if(message.type()==='error')messages.push({surface,type:'console',message:message.text()})})
  page.on('request',(request:any)=>{try{if(request.frame().parentFrame())sceneRequests.push({surface,url:request.url(),type:request.resourceType(),local:!/^https?:/.test(request.url())||new URL(request.url()).origin===new URL(baseUrl).origin})}catch{}})
}
async function record(name:string,callback:()=>Promise<any>){
  try {const result=await callback();states.push({name,passed:true,...result});return result}
  catch(error){states.push({name,passed:false,error:String(error)});return undefined}
}
function assert(condition:any,message:string){if(!condition)throw Error(message)}
async function settle(wrapper:any){
  await wrapper.waitFor({state:'visible'})
  await wrapper.page().evaluate(()=>document.fonts.ready)
  await wrapper.page().waitForTimeout(250)
}
async function playerScene(wrapper:any){
  const player=wrapper.locator('hyperframes-player').first()
  await player.waitFor({state:'visible',timeout:20000})
  await wrapper.page().waitForFunction((element:Element)=>element.closest('.hyperframe-slide')?.getAttribute('data-ready')==='true',await player.elementHandle(),{timeout:20000})
  const iframe=player.locator('iframe')
  await iframe.waitFor({state:'visible'})
  const handle=await iframe.elementHandle()
  const frame=await handle.contentFrame()
  assert(frame,'Official player iframe is unavailable.')
  await frame.locator('[data-scene-svg]').waitFor({state:'visible'})
  await frame.evaluate(()=>document.fonts.ready)
  await frame.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))
  const scaling=await iframe.evaluate((element:HTMLIFrameElement)=>({scale:element.getBoundingClientRect().width/element.clientWidth,width:element.getBoundingClientRect().width,height:element.getBoundingClientRect().height}))
  return {player,iframe,frame,scaling}
}
async function actualTime(scene:any){return Number(await scene.frame.locator('[data-scene-time]').getAttribute('data-scene-time'))}
async function appliedCue(scene:any,target:number){
  await scene.player.page().waitForFunction(({element,target}:{element:Element,target:number})=>{const root=element.closest('.hyperframe-slide');return root?.getAttribute('data-ready')==='true'&&Math.abs(Number(root.getAttribute('data-time'))-target)<.08},{element:await scene.player.elementHandle(),target},{timeout:10000})
  return await scene.player.evaluate((element:any)=>({ready:element.closest('.hyperframe-slide').dataset.ready,paused:element.paused,time:element.currentTime,assetsReady:element.assetsReady,sourceKind:element.closest('.hyperframe-slide').dataset.sourceKind}))
}
async function auditMechanism(scene:any,expected:{level:number,parcel:number,open:boolean}){
  const geometry=await scene.frame.locator('[data-scene-svg]').evaluate((element:SVGSVGElement)=>{
    const mark=(name:string)=>element.querySelector<SVGGraphicsElement>(`[data-scene-mark="${name}"]`)!
    const tank=mark('tank').getBBox(),fill=mark('tank-fill').getBBox(),valve=mark('valve'),parcel=mark('parcel')
    const valveX=Number(valve.getAttribute('cx')),parcelX=Number(parcel.getAttribute('cx'))
    return{level:fill.height/tank.height*100,fillBottom:fill.y+fill.height,tankBottom:tank.y+tank.height,parcel:(parcelX-valveX)/(tank.x-valveX),parcelVisible:getComputedStyle(parcel).visibility==='visible',valveStroke:valve.nextElementSibling?.getAttribute('d'),levelLabel:mark('level-readout').textContent,valveLabel:mark('valve-readout').textContent}
  })
  assert(Math.abs(geometry.level-expected.level)<.05,'Actual tank fill geometry does not match the independent level.')
  assert(Math.abs(geometry.fillBottom-geometry.tankBottom)<.05,'Actual tank fill does not accumulate from the tank floor.')
  assert(Math.abs(geometry.parcel-expected.parcel)<.002&&geometry.parcelVisible===expected.open,'Actual parcel geometry/visibility does not match the independent transport state.')
  assert(geometry.levelLabel===Math.round(expected.level)+'%'&&geometry.valveLabel===(expected.open?'Open':'Closed'),'Actual readouts do not match the independent mechanism state.')
  const coordinates=geometry.valveStroke?.match(/-?\d+(?:\.\d+)?/g)?.map(Number)||[]
  assert(coordinates.length===4&&Math.abs(coordinates[3]-coordinates[1]-(expected.open?0:24))<.05,'Actual valve stroke does not match its open/closed state.')
  return geometry
}
async function auditScene(svg:any,scale=1){
  return await svg.evaluate((element:SVGSVGElement,{tokens,scale}:any)=>{
    const failures:string[]=[],viewBox=element.viewBox.baseVal
    const normalize=(css:string)=>{const values=css.match(/^rgba?\(([^)]+)\)$/)?.[1].split(',').map(Number);return values&&(values.length===3||values[3]===1)?'#'+values.slice(0,3).map(value=>Math.round(value).toString(16).padStart(2,'0')).join(''):null}
    const labels=[...element.querySelectorAll<SVGTextElement>('text')].map(text=>{
      const style=getComputedStyle(text),box=text.getBBox(),ctm=text.getCTM()!,rootMatrix=element.getCTM()!,local=rootMatrix.inverse().multiply(ctm)
      const corners=[[box.x,box.y],[box.x+box.width,box.y],[box.x,box.y+box.height],[box.x+box.width,box.y+box.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(local))
      const size=Number.parseFloat(style.fontSize)*Math.hypot(ctm.a,ctm.b)*scale
      let opacity=1;for(let ancestor:Element|null=text;ancestor;ancestor=ancestor.parentElement)opacity*=Number(getComputedStyle(ancestor).opacity)
      const inside=corners.every(point=>point.x>=viewBox.x-.5&&point.y>=viewBox.y-.5&&point.x<=viewBox.x+viewBox.width+.5&&point.y<=viewBox.y+viewBox.height+.5)
      if(!inside)failures.push(`Clipped scene label: ${text.textContent}`)
      if(size<14-.05)failures.push(`Scene label is below 14 effective pixels: ${text.textContent} (${size})`)
      if(!style.fontFamily.includes('Open Sans'))failures.push(`Scene label is missing Open Sans: ${text.textContent}`)
      if(opacity!==1)failures.push(`Scene label is not opaque: ${text.textContent}`)
      const ink=normalize(style.fill);if(ink!=='#000000'&&ink!=='#ffffff')failures.push(`Scene label ink is not black/white: ${text.textContent} (${ink})`)
      const screenCenter=new DOMPoint(box.x+box.width/2,box.y+box.height/2).matrixTransform(text.getScreenCTM()!)
      const backing=document.elementsFromPoint(screenCenter.x,screenCenter.y).filter(node=>node!==text&&!node.contains(text)).map(node=>normalize(getComputedStyle(node).fill)||normalize(getComputedStyle(node).backgroundColor)).find(Boolean)||normalize(getComputedStyle(document.body).backgroundColor)
      const luminance=(hex:string)=>{const channels=[1,3,5].map(index=>parseInt(hex.slice(index,index+2),16)/255).map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4);return channels[0]*.2126+channels[1]*.7152+channels[2]*.0722}
      const contrast=ink&&backing?(Math.max(luminance(ink),luminance(backing))+.05)/(Math.min(luminance(ink),luminance(backing))+.05):0
      if(contrast<4.5)failures.push(`Scene label contrast is below 4.5 on its actual backing: ${text.textContent} (${ink}/${backing}: ${contrast})`)
      return{text:text.textContent,font:style.fontFamily,fontPx:style.fontSize,effectiveFontPx:size,opacity,ink,backing,contrast,inside,rect:{left:Math.min(...corners.map(point=>point.x)),right:Math.max(...corners.map(point=>point.x)),top:Math.min(...corners.map(point=>point.y)),bottom:Math.max(...corners.map(point=>point.y))}}
    })
    for(let index=0;index<labels.length;index++)for(const other of labels.slice(index+1)){const label=labels[index],a=label.rect,b=other.rect;if(a.left<b.right-.5&&a.right>b.left+.5&&a.top<b.bottom-.5&&a.bottom>b.top+.5)failures.push(`Scene labels overlap: ${label.text}/${other.text}`)}
    const paints=[...new Set([...element.querySelectorAll('*')].flatMap(node=>{const style=getComputedStyle(node);return[normalize(style.fill),normalize(style.stroke)].filter(Boolean)}))]
    for(const paint of paints)if(!tokens.includes(paint))failures.push(`Non-palette scene paint: ${paint}`)
    if(!labels.length)failures.push('Scene contains no readable SVG labels.')
    if(!paints.includes('#9e1b32'))failures.push('Scene is missing the colorset1 primary mechanism paint.')
    const fontFaces=[...document.fonts].map(face=>({family:face.family,status:face.status}))
    if(!fontFaces.some(face=>face.family.replaceAll('"','')==='Open Sans'&&face.status==='loaded'))failures.push('Local Open Sans font was not loaded in the scene document.')
    return{passed:!failures.length,failures,labels,paints,fontFaces}
  },{tokens,scale})
}
async function auditWrapper(wrapper:any){
  const geometry=await wrapper.evaluate((element:HTMLElement)=>{
    const bounds=element.getBoundingClientRect(),cards=[...element.querySelectorAll<HTMLElement>('[data-item-id]')].map(card=>({id:card.dataset.itemId,rect:card.getBoundingClientRect().toJSON()}))
    const fits=[...element.querySelectorAll<HTMLElement>('[data-layout-fits]')].map(frame=>frame.dataset.layoutFits)
    const overlaps=cards.flatMap((card,index)=>cards.slice(index+1).filter(other=>card.rect.left<other.rect.right-.5&&card.rect.right>other.rect.left+.5&&card.rect.top<other.rect.bottom-.5&&card.rect.bottom>other.rect.top+.5).map(other=>[card.id,other.id]))
    return{width:bounds.width,height:bounds.height,withinViewport:bounds.left>=-.5&&bounds.top>=-.5&&bounds.right<=innerWidth+.5&&bounds.bottom<=innerHeight+.5,cards,fits,overlaps}
  })
  assert(geometry.withinViewport,'Fixture wrapper crosses the native viewport.')
  assert(!geometry.overlaps.length,'Collection cards overlap.')
  assert(geometry.fits.every(value=>value==='true'),'Collection capacity is not qualified as fitting.')
  return geometry
}
async function auditPreview(wrapper:any,sceneHeight:number,expectControls=true){
  const preview=wrapper.locator('.hyperframe-preview').first();assert(await preview.count()===1,'Reusable preview component is missing.')
  const geometry=await preview.evaluate((element:HTMLElement)=>{const scene=element.querySelector<HTMLElement>('.hyperframe-slide')!,button=element.querySelector<HTMLButtonElement>('.hyperframe-preview-control'),sceneRect=scene.getBoundingClientRect(),controlRect=button?.getBoundingClientRect();return{sceneCssHeight:Number.parseFloat(getComputedStyle(scene).height),sceneClientHeight:scene.clientHeight,previewClientHeight:element.clientHeight,controls:element.dataset.previewControls,ready:element.dataset.previewReady,playing:element.dataset.previewPlaying,control:button?{name:button.getAttribute('aria-label'),pressed:button.getAttribute('aria-pressed'),font:getComputedStyle(button).fontFamily,fontPx:Number.parseFloat(getComputedStyle(button).fontSize),opacity:getComputedStyle(button).opacity,ink:getComputedStyle(button).color,fill:getComputedStyle(button).backgroundColor,hit:document.elementFromPoint(controlRect!.x+controlRect!.width/2,controlRect!.y+controlRect!.height/2)===button,belowScene:controlRect!.top>=sceneRect.bottom-.5,widthFits:controlRect!.right<=element.getBoundingClientRect().right+.5}:null}})
  assert(geometry.sceneCssHeight===sceneHeight&&geometry.sceneClientHeight===sceneHeight,'Preview uses visual pixels instead of the requested CSS logical scene height.')
  assert(geometry.previewClientHeight===sceneHeight+(expectControls?48:0),'Preview does not reserve the documented scene and control rows.')
  assert(geometry.controls===String(expectControls),'Preview control omission does not match the rendering context.')
  if(expectControls){assert(geometry.control?.hit&&geometry.control?.belowScene&&geometry.control?.widthFits,'Preview control is obscured, overlaps the scene or crosses its width.');assert(geometry.control?.font.includes('Open Sans')&&geometry.control.fontPx===16&&geometry.control.opacity==='1','Preview control typography is not fixed, opaque Open Sans.');assert(['rgb(0, 0, 0)','rgb(255, 255, 255)'].includes(geometry.control.ink),'Preview control does not use black/white ink.');const rgb=(value:string)=>value.match(/\d+(?:\.\d+)?/g)!.slice(0,3).map(Number),fill=rgb(geometry.control.fill),ink=rgb(geometry.control.ink),hex='#'+fill.map(value=>value.toString(16).padStart(2,'0')).join('');assert(tokens.includes(hex),'Preview control backing is outside the selected palette.');const luminance=(values:number[])=>{const [r,g,b]=values.map(value=>value/255).map(value=>value<=.04045?value/12.92:((value+.055)/1.055)**2.4);return r*.2126+g*.7152+b*.0722};const ratio=(Math.max(luminance(fill),luminance(ink))+.05)/(Math.min(luminance(fill),luminance(ink))+.05);assert(ratio>=4.5,'Preview control ink does not contrast with its actual backing.')}
  else assert(geometry.control===null,'Preview exposes a play control in a noninteractive context.')
  return geometry
}
try {
  if(!args.includes('--skip-catalog')){
    const page=await browser.newPage({viewport:{width:1600,height:1000}});collect(page,'catalog')
    const response=await page.goto(baseUrl,{waitUntil:'domcontentloaded'});assert(response?.status()===200,'Canonical examples index must return HTTP 200.')
    for(const owner of ['slidev-echarts','slidev-animejs']){
      const card=page.locator(`#example-set-${owner}[data-example-id="${owner}"][data-pattern-id="${owner}"]`)
      assert(await card.count()===1,owner+': canonical examples card is missing or ambiguous.')
      assert((await card.innerText()).includes('HyperFrames'),owner+': catalog card does not mention HyperFrames.')
      assert(await card.getAttribute('href')===`examples/${owner}/`,owner+': catalog route changed.')
      catalog.push({owner,passed:true,text:await card.innerText()})
    }
    await page.close()
  }
  for(const owner of ['slidev-echarts','slidev-animejs']){
    const start=owner==='slidev-echarts'?42:36
    const page=await browser.newPage({viewport:{width:1600,height:900}});collect(page,owner)
    const route=(offset:number)=>new URL(`examples/${owner}/#/${start+offset}`,baseUrl).href
    await page.goto(route(0),{waitUntil:'domcontentloaded'})
    const live=page.locator('#'+owner+'-hyperframes');await settle(live)
    let scene=await playerScene(live)
    for(const index of [0,1,2,3,1,0])await record(owner+': cue '+index,async()=>{
      await live.locator(`[data-hyperframes-cue="${index}"]`).click()
      await page.waitForTimeout(200)
      const readiness=await appliedCue(scene,cueTimes[index])
      const time=await actualTime(scene);assert(Math.abs(time-cueTimes[index])<.08,'Iframe clock does not match the selected cue.')
      const model=await scene.frame.locator('[data-scene-time]').evaluate((element:HTMLElement)=>({level:Number(element.dataset.level),parcel:Number(element.dataset.parcelProgress),open:element.dataset.valveOpen==='true'||element.dataset.valveOpen==='1'}))
      assert(Math.abs(model.level-cueModels[index].level)<.05&&Math.abs(model.parcel-cueModels[index].parcel)<.002&&model.open===cueModels[index].open,'Native valve, tank and parcel state do not match the independent cue model.')
      const paint=await auditScene(scene.frame.locator('[data-scene-svg]'),scene.scaling.scale);assert(paint.passed,paint.failures.join('; '))
      return{time,readiness,model,mechanism:await auditMechanism(scene,cueModels[index]),paint,geometry:await auditWrapper(live)}
    })
    await record(owner+': native Slidev click forward/back',async()=>{
      await live.locator('.hyperframes-context').click()
      await page.keyboard.press('ArrowRight');await page.waitForTimeout(250)
      assert(Number(await live.getAttribute('data-cue-index'))===1,'Native forward click did not advance the scene cue.')
      const forward=await appliedCue(scene,3)
      assert(Math.abs(await actualTime(scene)-3)<.08,'Native forward click did not seek the iframe.')
      await page.keyboard.press('ArrowLeft');await page.waitForTimeout(250)
      assert(Number(await live.getAttribute('data-cue-index'))===0,'Native backward click did not restore the scene cue.')
      const backward=await appliedCue(scene,0)
      assert(Math.abs(await actualTime(scene))<.08,'Native backward click did not restore the iframe.')
      return{forward,backward}
    })
    await record(owner+': play/pause/leave/return',async()=>{
      const controls=await auditPreview(live,282)
      await live.locator('.hyperframe-preview-control').click();const before=await actualTime(scene);await page.waitForTimeout(700);const after=await actualTime(scene)
      assert(after>before+.25,'Official player did not advance while playing.')
      assert(await live.locator('.hyperframe-preview-control').getAttribute('aria-label')==='Pause animation','Playing preview does not expose its pause action.')
      await live.locator('.hyperframe-preview-control').click();await page.waitForTimeout(100);const pausedTime=await actualTime(scene);await page.waitForTimeout(350)
      assert(Math.abs(await actualTime(scene)-pausedTime)<.06,'Native Pause animation does not freeze the official clock.')
      assert(await live.locator('.hyperframe-preview-control').getAttribute('aria-pressed')==='false','Paused preview retains its pressed state.')
      await live.locator('.hyperframe-preview-control').click();await page.waitForTimeout(100)
      await page.goto(route(1),{waitUntil:'domcontentloaded'});await page.waitForTimeout(250)
      const stopped=await actualTime(scene);await page.waitForTimeout(450);assert(Math.abs(await actualTime(scene)-stopped)<.06,'Inactive scene clock continues advancing.')
      await page.goto(route(0),{waitUntil:'domcontentloaded'});await settle(live)
      assert(await live.locator('.hyperframe-preview-control').getAttribute('aria-pressed')==='false','Returning to the slide resumed its preview control.')
      scene=await playerScene(live);const returned=await actualTime(scene);await page.waitForTimeout(350);assert(Math.abs(await actualTime(scene)-returned)<.06,'Returned scene is not paused.')
      return{before,after,pausedTime,stopped,returned,controls}
    })
    await page.screenshot({path:path.join(output,owner+'-hyperframes-live.png')});captures.push(owner+'-hyperframes-live.png')
    await page.goto(route(1),{waitUntil:'domcontentloaded'})
    const cells=page.locator('#'+owner+'-hyperframes-cells');await settle(cells)
    for(const width of [885,680,480])for(const mode of ['columns','masonry-columns'])await record(owner+`: cells ${mode} width${width}`,async()=>{
      await cells.evaluate((element:HTMLElement,width:number)=>{element.style.width=width+'px'},width)
      await cells.locator(`[data-hyperframes-layout="${mode}"]`).click();await page.waitForTimeout(350)
      const collection=cells.locator('[data-collection-page]'),ids:string[]=[]
      while(Number(await collection.getAttribute('data-collection-page'))>1){await collection.locator('[data-page-action="previous"]').click();await page.waitForTimeout(200)}
      const pages=Number(await collection.getAttribute('data-collection-pages'));let paint
      for(let pageIndex=1;pageIndex<=pages;pageIndex++){
        if(pageIndex>1){await collection.locator('[data-page-action="next"]').click();await page.waitForTimeout(250)}
        const geometry=await auditWrapper(cells);ids.push(...geometry.cards.map((card:any)=>card.id))
        if(await cells.locator('hyperframes-player').count()){
          const cellScene=await playerScene(cells);await auditPreview(cells,162);paint=await auditScene(cellScene.frame.locator('[data-scene-svg]'),cellScene.scaling.scale);assert(paint.passed,paint.failures.join('; '))
        }
      }
      assert(JSON.stringify(ids)===JSON.stringify(['mechanism','relationships','assumptions']),`Collection pagination does not cover all components once in order: ${JSON.stringify({width,mode,pages,ids,currentPage:await collection.getAttribute('data-collection-page')})}`)
      return{width,mode,pages,ids,paint}
    })
    await page.reload({waitUntil:'domcontentloaded'});await settle(cells)
    await record(owner+': default collection capture readiness',async()=>{
      assert(await cells.getAttribute('data-layout-choice')==='columns','Default collection capture did not restore its authored layout.')
      const collection=cells.locator('[data-collection-page]');assert(await collection.getAttribute('data-collection-page')==='1','Default collection capture did not restore its first page.')
      const snapshot=await playerScene(cells),paint=await auditScene(snapshot.frame.locator('[data-scene-svg]'),snapshot.scaling.scale);assert(paint.passed,paint.failures.join('; '))
      return{time:await actualTime(snapshot),paint,mechanism:await auditMechanism(snapshot,cueModels[0]),geometry:await auditWrapper(cells)}
    })
    await page.screenshot({path:path.join(output,owner+'-hyperframes-cells.png')});captures.push(owner+'-hyperframes-cells.png')
    await page.goto(route(2),{waitUntil:'domcontentloaded'})
    const exported=page.locator('#'+owner+'-hyperframes-export');await settle(exported)
    await record(owner+': explicit static export',async()=>{
      const instances=exported.locator('.hyperframe-slide');assert(await instances.count()===2,'Static HTTP export must expose two deterministic official scene snapshots.')
      const paints=[]
      for(let index=0;index<2;index++){
        const instance=instances.nth(index),snapshot=await playerScene(instance),requestedTime=index===0?0:9
        await instance.page().waitForTimeout(200)
        assert(await instance.getAttribute('data-ready')==='true','Static snapshot is not ready.')
        assert(await instance.getAttribute('data-static')==='true','Static snapshot does not expose its export contract.')
        assert(await instance.getAttribute('data-paused')==='true'&&await snapshot.player.evaluate((element:any)=>element.paused),'Static official scene is not paused.')
        const time=await actualTime(snapshot);assert(Math.abs(time-requestedTime)<.08,'Static official scene does not match the requested export time.')
        const level=Number(await snapshot.frame.locator('[data-scene-time]').getAttribute('data-level'));assert(Math.abs(level-(index===0?0:70))<.05,'Static tank level does not match the independent export model.')
        const mechanism=await auditMechanism(snapshot,cueModels[index===0?0:3])
        const paint=await auditScene(snapshot.frame.locator('[data-scene-svg]'),snapshot.scaling.scale);assert(paint.passed,paint.failures.join('; '));paints.push({requestedTime,time,level,mechanism,paint})
      }
      return{paint:paints,geometry:await auditWrapper(exported)}
    })
    await page.screenshot({path:path.join(output,owner+'-hyperframes-export.png')});captures.push(owner+'-hyperframes-export.png')
    for(const width of [680,480])await record(owner+`: static snapshots width${width}`,async()=>{
      await exported.evaluate((element:HTMLElement,width:number)=>{element.style.width=width+'px'},width);await page.waitForTimeout(350)
      const collection=exported.locator('[data-collection-page]'),ids:string[]=[],paints=[]
      while(Number(await collection.getAttribute('data-collection-page'))>1){await collection.locator('[data-page-action="previous"]').click();await page.waitForTimeout(200)}
      const pages=Number(await collection.getAttribute('data-collection-pages'))
      for(let pageIndex=1;pageIndex<=pages;pageIndex++){
        if(pageIndex>1){await collection.locator('[data-page-action="next"]').click();await page.waitForTimeout(300)}
        ids.push(...(await auditWrapper(exported)).cards.map((card:any)=>card.id))
        for(const instance of await exported.locator('.hyperframe-slide').all()){
          const snapshot=await playerScene(instance),time=await actualTime(snapshot),expected=time<.08?cueModels[0]:cueModels[3]
          assert(await instance.getAttribute('data-static')==='true'&&await snapshot.player.evaluate((element:any)=>element.paused),'Responsive export scene is not explicitly paused/static.')
          const paint=await auditScene(snapshot.frame.locator('[data-scene-svg]'),snapshot.scaling.scale);assert(paint.passed,paint.failures.join('; '));paints.push({time,paint,mechanism:await auditMechanism(snapshot,expected)})
        }
      }
      assert(JSON.stringify(ids)===JSON.stringify(['closed','open']),'Responsive export pagination must cover both snapshots once.')
      return{width,pages,ids,paints}
    })
    await page.close()
    await record(owner+': reduced motion and dark system preference',async()=>{
      const preference=await browser.newPage({viewport:{width:1600,height:900},reducedMotion:'reduce',colorScheme:'dark'});collect(preference,owner+' preferences')
      try{
        await preference.goto(route(0),{waitUntil:'domcontentloaded'});const wrapper=preference.locator('#'+owner+'-hyperframes');await settle(wrapper)
        await wrapper.locator('[data-hyperframes-cue="3"]').click();await preference.waitForTimeout(250);const snapshot=await playerScene(wrapper)
        assert(Math.abs(await actualTime(snapshot)-9)<.08,'Reduced motion changed cue geometry.')
        assert(await wrapper.locator('.hyperframe-preview-control').isDisabled(),'Reduced motion must disable the reusable preview control.');const before=await actualTime(snapshot);await preference.waitForTimeout(400)
        assert(Math.abs(await actualTime(snapshot)-before)<.06&&await snapshot.player.evaluate((element:any)=>element.paused),'Reduced motion allows the official clock to play.')
        const paint=await auditScene(snapshot.frame.locator('[data-scene-svg]'),snapshot.scaling.scale);assert(paint.passed,paint.failures.join('; '))
        return{time:before,paint,mechanism:await auditMechanism(snapshot,cueModels[3]),geometry:await auditWrapper(wrapper)}
      }finally{await preference.close()}
    })
    for(const viewport of [{width:1280,height:720},{width:980,height:551}])await record(owner+`: preview logical sizing viewport${viewport.width}`,async()=>{
      const responsive=await browser.newPage({viewport});collect(responsive,owner+' responsive')
      try{
        const views=[]
        for(const offset of [0,1]){
          await responsive.goto(route(offset),{waitUntil:'domcontentloaded'});const wrapper=responsive.locator('#'+owner+(offset===0?'-hyperframes':'-hyperframes-cells'));await settle(wrapper)
          const snapshot=await playerScene(wrapper),paint=await auditScene(snapshot.frame.locator('[data-scene-svg]'),snapshot.scaling.scale);assert(paint.passed,paint.failures.join('; '))
          const controls=await auditPreview(wrapper,offset===0?282:162);await wrapper.locator('.hyperframe-preview-control').click();const before=await actualTime(snapshot);await responsive.waitForTimeout(350);assert(await actualTime(snapshot)>before+.15,'Responsive preview Play is intercepted or inactive.');await wrapper.locator('.hyperframe-preview-control').click()
          views.push({offset,paint,controls,geometry:await auditWrapper(wrapper)})
        }
        return{viewport,views}
      }finally{await responsive.close()}
    })
  }
  if(argument('--file-html')){
    const fileUrl=pathToFileURL(path.resolve(argument('--file-html'))).href
    const page=await browser.newPage({viewport:{width:1600,height:900}});collect(page,'direct-file')
    try{
      await record('direct-file: existing ECharts chart',async()=>{
        await page.goto(fileUrl+'#/1',{waitUntil:'domcontentloaded'});await page.waitForTimeout(350)
        await page.getByRole('heading',{name:'Slidev + Apache ECharts',exact:true}).waitFor({state:'visible'})
        const canvas=page.locator('[data-example-id="market-mix"] .echart-canvas canvas').first()
        await canvas.waitFor({state:'visible'})
        const paintedPixels=await canvas.evaluate((element:HTMLCanvasElement)=>{const data=element.getContext('2d')!.getImageData(0,0,element.width,element.height).data;let painted=0;for(let index=3;index<data.length;index+=4)if(data[index]>0)painted++;return painted})
        assert(paintedPixels>100,'Existing direct-open ECharts chart contains no real painted marks.')
        return{fileUrl,paintedPixels}
      })
      await record('direct-file: default native scene fallback',async()=>{
        await page.goto(fileUrl+'#/42',{waitUntil:'domcontentloaded'});const wrapper=page.locator('#slidev-echarts-hyperframes');await settle(wrapper)
        const instance=wrapper.locator('.hyperframe-slide')
        assert(await instance.getAttribute('data-source-kind')==='fallback','Direct file does not select the documented native fallback.')
        const preview=await auditPreview(wrapper,282,false)
        assert(await wrapper.locator('hyperframes-player').count()===0,'Direct file unexpectedly requires an HTTP official player.')
        const frames=[]
        for(const index of [0,3,1,0]){
          await wrapper.locator(`[data-hyperframes-cue="${index}"]`).click();await page.waitForTimeout(200)
          assert(await instance.getAttribute('data-ready')==='true'&&Math.abs(Number(await instance.getAttribute('data-time'))-cueTimes[index])<.08,'Direct-file fallback is not ready at its requested cue.')
          const paint=await auditScene(wrapper.locator('[data-scene-svg]'));assert(paint.passed,paint.failures.join('; '));frames.push({index,paint,mechanism:await auditMechanism({frame:wrapper},cueModels[index])})
        }
        await page.screenshot({path:path.join(output,'direct-file-live.png')})
        return{fileUrl,frames,preview,geometry:await auditWrapper(wrapper),capture:'direct-file-live.png'}
      })
      await record('direct-file: deterministic export snapshots',async()=>{
        await page.goto(fileUrl+'#/44',{waitUntil:'domcontentloaded'});const wrapper=page.locator('#slidev-echarts-hyperframes-export');await settle(wrapper)
        const instances=wrapper.locator('.hyperframe-slide');assert(await instances.count()===2,'Direct-file static snapshots are missing.')
        const snapshots=[]
        for(let index=0;index<2;index++){
          const instance=instances.nth(index),requestedTime=index===0?0:9
          assert(await instance.getAttribute('data-source-kind')==='fallback'&&await instance.getAttribute('data-static')==='true','Direct-file snapshot is not a static native fallback.')
          assert(await instance.getAttribute('data-ready')==='true'&&Math.abs(Number(await instance.getAttribute('data-time'))-requestedTime)<.08,'Direct-file snapshot does not match its requested time.')
          const paint=await auditScene(instance.locator('[data-scene-svg]'));assert(paint.passed,paint.failures.join('; '));snapshots.push({requestedTime,paint,mechanism:await auditMechanism({frame:instance},cueModels[index===0?0:3])})
        }
        await page.screenshot({path:path.join(output,'direct-file-export.png')})
        return{fileUrl,snapshots,geometry:await auditWrapper(wrapper),capture:'direct-file-export.png'}
      })
    }finally{await page.close()}
  }
}catch(error){errors.push(String(error))}
finally{await browser.close();if(server)await new Promise<void>(resolve=>server!.close(()=>resolve()))}
const expectedWakeLocks=messages.filter(value=>value.message.includes('Wake Lock permission request denied'))
const unexpectedMessages=messages.filter(value=>!value.message.includes('Wake Lock permission request denied'))
const externalSceneRequests=sceneRequests.filter(request=>!request.local)
const report={date:new Date().toISOString(),passed:!errors.length&&!unexpectedMessages.length&&!externalSceneRequests.length&&states.every(state=>state.passed)&&captures.length===6,input,baseUrl,paletteSha:createHash('sha256').update(paletteBytes).digest('hex'),states,catalog,captures,errors,unexpectedMessages,expectedWakeLocks,sceneRequests,externalSceneRequests}
await writeFile(path.join(output,'verification.json'),JSON.stringify(report,null,2)+'\n')
const summary={date:report.date,passed:report.passed,states:states.length,failedStates:states.filter(state=>!state.passed),catalogCards:catalog.length,captures:captures.length,errors,unexpectedMessages,externalSceneRequests,knownHeadlessWakeLockDenials:expectedWakeLocks.length,report:path.join(output,'verification.json')}
await writeFile(path.join(output,'summary.json'),JSON.stringify(summary,null,2)+'\n')
console.log(JSON.stringify(summary,null,2))
if(!report.passed)process.exitCode=1
