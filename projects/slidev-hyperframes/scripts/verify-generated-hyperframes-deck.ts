#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types projects/slidev-hyperframes/scripts/verify-generated-hyperframes-deck.ts --deck <authored-deck> --pack <isolated-skill>/assets/templates/slidev-hyperframes --output <project-artifacts>
// Evaluator dependencies: Node >=24, Playwright and Sharp from --browser-dependencies. Build dependencies are installed only from the submitted package.json in a disposable copy.
import { cp, mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { spawn } from 'node:child_process'
import { pathToFileURL } from 'node:url'
import http from 'node:http'

const args=process.argv.slice(2)
const arg=(key:string,fallback='')=>{const i=args.indexOf(key);return i<0?fallback:args[i+1]}
if(!arg('--deck')||!arg('--pack')||!arg('--output'))throw new Error('--deck, --pack and --output are required.')
const deck=path.resolve(arg('--deck')),pack=path.resolve(arg('--pack')),output=path.resolve(arg('--output'))
const working=path.join(output,'build-source'),html=path.join(output,'http-html')
const browserDependencies=path.resolve(arg('--browser-dependencies','skills/slidev-echarts/assets/examples/slidev-echarts/node_modules'))
const require=createRequire(path.join(browserDependencies,'../package.json'))
const {chromium}=require('playwright')
const sharp=require('sharp')
const evaluatorSha256=createHash('sha256').update(await readFile(process.argv[1])).digest('hex')
const cases:any[]=[],errors:string[]=[],requests:any[]=[],commands:any[]=[],fontMap=new Map<string,string>()
let sourceHashes:Record<string,string>={},sourceAfter:Record<string,string>={},packHashes:Record<string,string>={}
const add=(id:string,failures:string[],detail:any={})=>{const result={id,passed:failures.length===0,failures,...detail};cases.push(result);return result}
async function files(dir:string,prefix=''):Promise<string[]>{
  const found:string[]=[]
  for(const entry of await readdir(dir,{withFileTypes:true})){
    if(['node_modules','dist','.slidev','.git'].includes(entry.name))continue
    const relative=path.posix.join(prefix,entry.name)
    if(entry.isDirectory())found.push(...await files(path.join(dir,entry.name),relative))
    else if(entry.isFile())found.push(relative)
  }
  return found.sort()
}
async function digests(dir:string){return Object.fromEntries(await Promise.all((await files(dir)).map(async file=>[file,createHash('sha256').update(await readFile(path.join(dir,file))).digest('hex')]))) as Record<string,string>}
async function command(id:string,argv:string[],cwd:string){
  const began=Date.now()
  const result=await new Promise<{code:number,log:string}>(resolve=>{
    const child=spawn(process.execPath,argv,{cwd,windowsHide:true,env:{...process.env,NODE_ENV:id==='install'?undefined:'production'}})
    let log='';child.stdout.on('data',chunk=>log+=chunk);child.stderr.on('data',chunk=>log+=chunk)
    child.on('error',error=>{log+='\n'+String(error);resolve({code:1,log})})
    child.on('close',code=>resolve({code:code??1,log}))
  })
  const logPath=path.join(output,id+'.log');await writeFile(logPath,result.log)
  commands.push({id,executable:process.execPath,argv,cwd,exitCode:result.code,durationSeconds:(Date.now()-began)/1000,log:logPath})
  if(result.code)throw new Error(`${id} failed (${result.code}); see ${logPath}`)
}
const mime:Record<string,string>={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png'}
let server:http.Server|undefined,browser:any,page:any,hashRouting=false
function routeState(url:string){const original=new URL(url),route=original.hash.startsWith('#/')?new URL(original.hash.slice(1),'http://route'):original;return{slide:Number(route.pathname.split('/').filter(Boolean).pop()||1),clicks:Number(route.searchParams.get('clicks')||0)}}
async function openSlide(base:string,slide:number){await page.goto(hashRouting?base+'/#/'+slide+'?clicks=0':base+'/'+slide+'?clicks=0',{waitUntil:'networkidle'})}

async function wrappers(){return page.locator('.hyperframe-slide:visible')}
async function currentFrame(){
  const wrapper=(await wrappers()).first()
  await wrapper.waitFor({timeout:30000})
  await page.waitForFunction(()=>[...document.querySelectorAll<HTMLElement>('.hyperframe-slide')].some(element=>{
    const r=element.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(element).visibility!=='hidden'&&element.dataset.ready==='true'
  }),null,{timeout:45000})
  const handle=await wrapper.locator('iframe').first().elementHandle()
  const frame=handle?await handle.contentFrame():null
  if(!frame)throw new Error('The HTTP live/static composition did not have a native iframe.')
  await frame.locator('#tank-fill').waitFor({state:'attached',timeout:30000})
  return{wrapper,frame}
}
async function sceneAudit(frame:any,selectedPalette:any,rootQuery=''){
  return await frame.evaluate(async({palette,rootQuery}:any)=>{
    const root:Document|Element=rootQuery?document.querySelector(rootQuery)!:document;
    await document.fonts.ready
    const svg=root.querySelector<SVGSVGElement>('[data-scene-svg]')!
    const mark=(name:string)=>svg.querySelector('[data-scene-mark="'+name+'"]')||svg.querySelector('#'+name)
    const tank=mark('tank') as SVGRectElement,fill=mark('tank-fill') as SVGRectElement,parcel=mark('parcel') as SVGCircleElement,valve=mark('valve') as SVGCircleElement
    const failures:string[]=[],glyphs:any[]=[],paints:any[]=[],texts:any[]=[]
    function hex(value:string){const n=value.match(/[\d.]+/g)?.map(Number);if(value.startsWith('rgb')&&n&&n.length>=3){if(n[3]===0)return null;return'#'+n.slice(0,3).map(x=>Math.round(x).toString(16).padStart(2,'0')).join('')}return value==='none'||value==='transparent'?null:value.toLowerCase()}
    function luminance(value:string){const c=value.slice(1).match(/../g)!.map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722}
    function contrast(a:string,b:string){const x=luminance(a),y=luminance(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
    const allowed=palette.allowed
    const composition=root.querySelector<HTMLElement>('[data-composition-id]')
    const timeline=composition?(window as any).__timelines?.[composition.dataset.compositionId!]:undefined
    const sceneTime=composition?.dataset.sceneTime===undefined?null:Number(composition.dataset.sceneTime)
    const timelineTime=typeof timeline?.totalTime==='function'?timeline.totalTime():null
    const svgBounds=svg.getBoundingClientRect()
    if(svg.getAttribute('role')!=='img')failures.push('Composition SVG has no accessible image role.')
    for(const labelId of (svg.getAttribute('aria-labelledby')||'').split(/\s+/).filter(Boolean))if(![...svg.querySelectorAll('[id]')].some(element=>element.id===labelId&&element.textContent?.trim()))failures.push('Composition SVG has an unresolved accessible label: '+labelId)
    for(const element of [...svg.querySelectorAll<SVGElement>('rect,path,circle,text')]){
      const css=getComputedStyle(element)
      if(css.visibility==='hidden'||css.display==='none')continue
      for(const role of ['fill','stroke']){const paint=hex(css.getPropertyValue(role));if(paint){paints.push({id:element.id,role,paint});if(!allowed.includes(paint))failures.push(`${element.id||element.tagName}: undeclared ${role} ${paint}.`)}}
    }
    for(const text of [...svg.querySelectorAll<SVGTextElement>('text')]){
      const css=getComputedStyle(text),bounds=text.getBoundingClientRect(),ink=hex(css.fill)
      let opacity=1;for(let ancestor:Element|null=text;ancestor;ancestor=ancestor.parentElement)opacity*=Number(getComputedStyle(ancestor).opacity)
      if(!css.fontFamily.includes('Open Sans'))failures.push(`${text.id||text.textContent}: computed font is not Open Sans.`)
      if(Math.abs(opacity-1)>.0001)failures.push(`${text.id||text.textContent}: effective text opacity is ${opacity}.`)
      const backing=hex(getComputedStyle(svg.querySelector('rect')!).fill)!
      const best=contrast('#000000',backing)>=contrast('#ffffff',backing)?'#000000':'#ffffff'
      if(ink!==best||!ink||contrast(ink,backing)<4.5)failures.push(`${text.id||text.textContent}: text lacks maximum black/white contrast against the starter's actual surface.`)
      const range=document.createRange();range.selectNodeContents(text)
      for(const r of range.getClientRects())if(r.left < -1||r.top < -1||r.right>innerWidth+1||r.bottom>innerHeight+1||r.left<svgBounds.left-1||r.top<svgBounds.top-1||r.right>svgBounds.right+1||r.bottom>svgBounds.bottom+1)glyphs.push({text:text.textContent,x:r.x,y:r.y,width:r.width,height:r.height})
      const matrix=text.getScreenCTM(),svgScale=matrix?Math.sqrt(matrix.a*matrix.a+matrix.b*matrix.b):1
      texts.push({id:text.id,text:text.textContent,fontFamily:css.fontFamily,fontSize:css.fontSize,svgScale,glyphHeight:bounds.height,ink,opacity})
    }
    if(glyphs.length)failures.push(`${glyphs.length} text ranges cross the actual scene viewport/SVG.`)
    const loadedFonts=[...document.fonts].map(font=>({family:font.family,status:font.status,weight:font.weight}))
    if(!loadedFonts.some(font=>font.family.replace(/["']/g,'')==='Open Sans'&&font.status==='loaded'))failures.push('No actually loaded Open Sans face.')
    return{failures,sceneTime,timelineTime,levelText:mark('level-readout')?.textContent,valveText:mark('valve-readout')?.textContent,fillFraction:Number(fill.getAttribute('height'))/Number(tank.getAttribute('height')),parcelProgress:(Number(parcel.getAttribute('cx'))-Number(valve.getAttribute('cx')))/(Number(tank.getAttribute('x'))-Number(valve.getAttribute('cx'))),parcelVisibility:getComputedStyle(parcel).visibility,tankFill:hex(getComputedStyle(fill).fill),texts,paints,glyphs,loadedFonts,viewport:{width:innerWidth,height:innerHeight},svgBounds:{x:svgBounds.x,y:svgBounds.y,width:svgBounds.width,height:svgBounds.height}}
  },{palette:selectedPalette,rootQuery})
}
function expectedState(time:number){const progress=Math.max(0,Math.min(1,(time-2)/8));return{level:Math.round(progress*80),fill:progress*.8,parcel:progress,valve:time>=2&&time<10?'Open':'Closed'}}
function compareState(snapshot:any,time:number){const expected=expectedState(time),failures:string[]=[];if(snapshot.levelText!==expected.level+'%')failures.push(`Actual level ${snapshot.levelText}; expected ${expected.level}%.`);if(snapshot.valveText!==expected.valve)failures.push(`Actual valve ${snapshot.valveText}; expected ${expected.valve}.`);if(Math.abs(snapshot.fillFraction-expected.fill)>.002)failures.push(`Actual tank fill ${snapshot.fillFraction}; expected ${expected.fill}.`);if(Math.abs(snapshot.parcelProgress-expected.parcel)>.002)failures.push(`Actual parcel position ${snapshot.parcelProgress}; expected ${expected.parcel}.`);return failures}
function sameState(a:any,b:any){const timeStable=(a.timelineTime===null||b.timelineTime===null||Math.abs(a.timelineTime-b.timelineTime)<.002)&&(a.sceneTime===null||b.sceneTime===null||Math.abs(a.sceneTime-b.sceneTime)<.002);return timeStable&&a.levelText===b.levelText&&a.valveText===b.valveText&&Math.abs(a.fillFraction-b.fillFraction)<.002&&Math.abs(a.parcelProgress-b.parcelProgress)<.002}
async function hostAudit(wrapper:any){
  return await wrapper.evaluate(async(element:HTMLElement)=>{
    await document.fonts.ready
    const r=element.getBoundingClientRect(),cell=element.closest<HTMLElement>('[data-item-id],article,[data-evaluator-hyperframes-cell]'),cellBounds=cell?.getBoundingClientRect(),slide=element.closest<HTMLElement>('.slidev-layout'),slideBounds=slide?.getBoundingClientRect(),failures:string[]=[]
    if(r.left < -1||r.top < -1||r.right>innerWidth+1||r.bottom>innerHeight+1)failures.push('Player crosses browser viewport.')
    if(cellBounds&&(r.left<cellBounds.left-1||r.top<cellBounds.top-1||r.right>cellBounds.right+1||r.bottom>cellBounds.bottom+1))failures.push('Player crosses its live cell.')
    const immediateParent=element.parentElement!,parentBounds=immediateParent.getBoundingClientRect()
    if(parentBounds.width>0&&parentBounds.height>0&&(r.left<parentBounds.left-1||r.top<parentBounds.top-1||r.right>parentBounds.right+1||r.bottom>parentBounds.bottom+1))failures.push('Player crosses its actual containing box.')
    if(slideBounds&&(r.left<slideBounds.left-1||r.top<slideBounds.top-1||r.right>slideBounds.right+1||r.bottom>slideBounds.bottom+1))failures.push('Player crosses Slidev canvas.')
    const layout=element.closest<HTMLElement>('[data-layout-mode]')
    if(layout?.dataset.layoutFits==='false')failures.push('Live cell layout reports fits=false.')
    const font=getComputedStyle(element).fontFamily;if(!font.includes('Open Sans'))failures.push('Host player wrapper does not compute Open Sans.')
    const loadedFonts=[...document.fonts].map(font=>({family:font.family,status:font.status,weight:font.weight}))
    if(!loadedFonts.some(font=>font.family.replace(/["']/g,'')==='Open Sans'&&font.status==='loaded'))failures.push('Host document has no actually loaded Open Sans face.')
    const cells:any[]=[],typography:any[]=[],clippingBoundaries:any[]=[]
    const actualLayout=element.closest<HTMLElement>('[data-evaluator-hyperframes-width]')
    const cardSelector='[data-evaluator-hyperframes-cell],[data-item-id],article'
    const actualCards=[...(actualLayout?.querySelectorAll<HTMLElement>(cardSelector)||[])].filter(card=>{
      for(let ancestor=card.parentElement;ancestor&&ancestor!==actualLayout;ancestor=ancestor.parentElement)if(ancestor.matches(cardSelector))return false
      return true
    })
    for(const card of actualCards){
      const bounds=card.getBoundingClientRect(),layoutBounds=actualLayout!.getBoundingClientRect()
      if(!bounds.width||!bounds.height||getComputedStyle(card).visibility==='hidden')continue
      cells.push({tag:card.tagName,id:card.id,className:card.className,x:bounds.x,y:bounds.y,width:bounds.width,height:bounds.height})
      if(bounds.left<layoutBounds.left-1||bounds.top<layoutBounds.top-1||bounds.right>layoutBounds.right+1||bounds.bottom>layoutBounds.bottom+1)failures.push('An actual layout cell crosses the available two-cell container.')
      if(slideBounds&&(bounds.left<slideBounds.left-1||bounds.top<slideBounds.top-1||bounds.right>slideBounds.right+1||bounds.bottom>slideBounds.bottom+1))failures.push('An actual layout cell crosses the Slidev canvas.')
      for(const text of card.querySelectorAll<HTMLElement>('p,h1,h2,h3,h4,button')){
        const css=getComputedStyle(text),textBounds=text.getBoundingClientRect()
        if(!textBounds.width||!textBounds.height||css.visibility==='hidden'||css.display==='none')continue
        typography.push({text:text.textContent,fontFamily:css.fontFamily,fontSize:css.fontSize})
        if(!css.fontFamily.includes('Open Sans'))failures.push('A visible cell label does not compute Open Sans.')
        const range=document.createRange();range.selectNodeContents(text)
        for(const glyph of range.getClientRects()){
          if(glyph.left<bounds.left-1||glyph.top<bounds.top-1||glyph.right>bounds.right+1||glyph.bottom>bounds.bottom+1)failures.push('A visible cell label crosses its actual card bounds.')
          for(let ancestor:HTMLElement|null=text;ancestor&&ancestor!==card;ancestor=ancestor.parentElement){
            const ancestorCss=getComputedStyle(ancestor),clipBounds=ancestor.getBoundingClientRect()
            const clipBoth=/(?:^|\s)(?:paint|strict|content)(?:\s|$)/.test(ancestorCss.contain)||ancestorCss.clipPath!=='none'||ancestorCss.clip!=='auto'
            const clipsX=clipBoth||['hidden','clip','auto','scroll'].includes(ancestorCss.overflowX),clipsY=clipBoth||['hidden','clip','auto','scroll'].includes(ancestorCss.overflowY)
            if(!clipsX&&!clipsY)continue
            clippingBoundaries.push({tag:ancestor.tagName,className:ancestor.className,overflowX:ancestorCss.overflowX,overflowY:ancestorCss.overflowY,contain:ancestorCss.contain,text:text.textContent,bounds:{x:clipBounds.x,y:clipBounds.y,width:clipBounds.width,height:clipBounds.height}})
            if((clipsX&&(glyph.left<clipBounds.left-1||glyph.right>clipBounds.right+1))||(clipsY&&(glyph.top<clipBounds.top-1||glyph.bottom>clipBounds.bottom+1)))failures.push('A visible cell label crosses an explicitly clipping descendant.')
          }
        }
      }
    }
    return{failures,width:element.clientWidth,height:element.clientHeight,bounds:{x:r.x,y:r.y,width:r.width,height:r.height},containingBox:{x:parentBounds.x,y:parentBounds.y,width:parentBounds.width,height:parentBounds.height},cell:cellBounds?{x:cellBounds.x,y:cellBounds.y,width:cellBounds.width,height:cellBounds.height}:null,cells,typography,clippingBoundaries,ready:element.dataset.ready,status:element.dataset.status,paused:element.dataset.paused,sourceKind:element.dataset.sourceKind,colorset:element.dataset.colorset,static:element.dataset.static,font,loadedFonts}
  })
}
async function capture(id:string,time:number,palette:any,shot=true){
  const{wrapper,frame}=await currentFrame();await page.waitForTimeout(120)
  const scene=await sceneAudit(frame,palette),host=await hostAudit(wrapper)
  const iframeBounds=await wrapper.locator('iframe').first().boundingBox()
  const failures=[...scene.failures,...host.failures,...compareState(scene,time)]
  if(iframeBounds){const r=host.bounds;if(iframeBounds.x<r.x-1||iframeBounds.y<r.y-1||iframeBounds.x+iframeBounds.width>r.x+r.width+1||iframeBounds.y+iframeBounds.height>r.y+r.height+1)failures.push('Actual iframe crosses the player viewport.')}
  const fontKey=id.match(/^slide-(\d+)/)?.[1]||id
  for(const text of scene.texts){const key=fontKey+':'+(text.id||text.text);if(fontMap.has(key)&&fontMap.get(key)!==text.fontSize)failures.push('Authored scene font size changed across cue/container states: '+key);else fontMap.set(key,text.fontSize)}
  if(host.colorset!=='colorset1')failures.push('Selected palette is not colorset1.')
  if(host.paused!=='true')failures.push('Deterministic cue is not paused.')
  const hostScale=host.bounds.width/host.width,frameScale=iframeBounds?iframeBounds.width/scene.viewport.width:1
  const actualText=scene.texts.map((text:any)=>({...text,effectiveFontCssPx:parseFloat(text.fontSize)*text.svgScale*frameScale/hostScale}))
  const result=add(id,failures,{time,scene,host,iframeBounds,actualText})
  if(shot||failures.length)await page.screenshot({path:path.join(output,id+'.png'),fullPage:true})
  return{result,scene,frame,wrapper}
}
async function navigate(key:string){await page.evaluate(()=>document.activeElement instanceof HTMLElement&&document.activeElement.blur());await page.keyboard.press(key);await page.waitForTimeout(180)}
async function constrainCell(width:number|null){
  return await page.evaluate(async width=>{
    document.querySelector('#evaluator-hyperframes-width')?.remove()
    const wrapper=[...document.querySelectorAll<HTMLElement>('.hyperframe-slide')].find(element=>{const r=element.getBoundingClientRect();return r.width&&r.height&&getComputedStyle(element).visibility!=='hidden'})!
    const collection=wrapper.closest<HTMLElement>('.slidev-collection'),engine=wrapper.closest<HTMLElement>('[data-layout-mode]')
    let parent=collection||engine?.parentElement
    let kind=collection?'collection':engine?'layout-engine':'',cells:HTMLElement[]=[]
    if(engine)cells=[...engine.querySelectorAll<HTMLElement>('[data-item-id]')]
    if(engine&&parent){
      const css=getComputedStyle(parent),padded=parseFloat(css.paddingLeft)+parseFloat(css.paddingRight)>0
      if(parent.matches('.slidev-layout,.slidev-page')||padded){parent=engine;kind='layout-engine-self'}
    }
    if(!parent){
      for(let ancestor=wrapper.parentElement;ancestor&&!ancestor.classList.contains('slidev-layout');ancestor=ancestor.parentElement){
        const css=getComputedStyle(ancestor)
        if(!['grid','inline-grid','flex','inline-flex'].includes(css.display))continue
        const children=[...ancestor.children].filter(child=>{const r=child.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(child).visibility!=='hidden'}) as HTMLElement[]
        const own=children.find(child=>child.contains(wrapper))
        if(!own||children.length<2)continue
        const r=own.getBoundingClientRect()
        if(!children.some(child=>child!==own&&(child.getBoundingClientRect().left>=r.right-1||child.getBoundingClientRect().right<=r.left+1)))continue
        parent=ancestor;cells=children;kind='two-cell-'+css.display;break
      }
    }
    if(!parent)throw new Error('No actual two-cell layout ancestor spans the live composition and its explanation.')
    if(parent.matches('.slidev-layout,.slidev-page'))throw new Error('Slidev canvas cannot be an available layout-width target.')
    if(width===null)parent=(window as any).__hfWidthParent||parent
    else{(window as any).__hfWidthParent=parent;(window as any).__hfOriginalWidth=parent.clientWidth;(window as any).__hfWidthKind=kind}
    for(const cell of cells)cell.setAttribute('data-evaluator-hyperframes-cell','true')
    parent.setAttribute('data-evaluator-hyperframes-width','true')
    const selected=width??(window as any).__hfOriginalWidth
    const style=document.createElement('style');style.id='evaluator-hyperframes-width';style.textContent='.slidev-layout [data-evaluator-hyperframes-width]{width:'+selected+'px}';document.head.append(style)
    // Native layout engines update their item boxes after ResizeObserver and Vue render work.
    // Inspect the settled actual cells, rather than the synchronous pre-observer geometry.
    await new Promise(resolve=>setTimeout(resolve,350))
    const parentCss=getComputedStyle(parent),parentBounds=parent.getBoundingClientRect(),actualCells=[...parent.querySelectorAll<HTMLElement>('[data-evaluator-hyperframes-cell]')].map(cell=>{const r=cell.getBoundingClientRect();return{tag:cell.tagName,className:cell.className,x:r.x,y:r.y,width:r.width,height:r.height}})
    return{parentWidth:parent.clientWidth,actualAvailableWidth:engine?.clientWidth??parent.clientWidth,playerWidth:wrapper.clientWidth,selectionKind:(window as any).__hfWidthKind,selectedClass:parent.className,selectedCanvas:parent.matches('.slidev-layout,.slidev-page'),authoredInlineWidth:parent.style.width,computedDisplay:parentCss.display,computedFlexDirection:parentCss.flexDirection,computedColumnTracks:parentCss.gridTemplateColumns,parentBounds:{x:parentBounds.x,y:parentBounds.y,width:parentBounds.width,height:parentBounds.height},cells:actualCells,spansBothCells:actualCells.length>=2&&actualCells.every(r=>r.x>=parentBounds.left-1&&r.x+r.width<=parentBounds.right+1)}
  },width)
}

try{
  await mkdir(output,{recursive:true})
  sourceHashes=await digests(deck);packHashes=await digests(pack)
  const resourceFailures=Object.entries(packHashes).filter(([file,digest])=>sourceHashes[file]!==digest).map(([file])=>`Missing or changed copied resource: ${file}.`)
  add('immutable-runtime-copy',resourceFailures,{packHashes})
  if(resourceFailures.length)throw new Error('Copied runtime resources failed integrity before native checks.')
  const configuration=JSON.parse(await readFile(path.join(deck,'data/hyperframes-story.json'),'utf8'))
  add('editable-story-config',[JSON.stringify(configuration.cueTimes)!=='[0,4,9]'?'Cue times differ from [0,4,9].':'',configuration.exportTime!==9?'Export time differs from 9.':'',configuration.colorset!=='colorset1'?'Palette differs from colorset1.':''].filter(Boolean),{configuration})
  const pkg=JSON.parse(await readFile(path.join(deck,'package.json'),'utf8')),dependencies={...pkg.dependencies,...pkg.devDependencies}
  const packageFailures:string[]=[]
  for(const name of ['@slidev/cli','vue','@hyperframes/player'])if(!dependencies[name])packageFailures.push(`Required runtime dependency is not declared: ${name}.`)
  if(dependencies['@hyperframes/player']!=='0.8.134')packageFailures.push('Player dependency is not pinned to the supported 0.8.134.')
  if(!Object.keys(dependencies).some(name=>name.startsWith('@slidev/theme-')))packageFailures.push('Selected Slidev theme package is not declared.')
  for(const name of ['build','build:html'])if(!pkg.scripts?.[name])packageFailures.push(`Required package script is missing: ${name}.`)
  add('declared-package-build-contract',packageFailures,{dependencies,scripts:pkg.scripts})
  if(packageFailures.length)throw new Error('The submitted package is incomplete; evaluator will not repair it.')
  if(!args.includes('--skip-build')){
    await cp(deck,working,{recursive:true,filter:source=>!source.split(path.sep).some(part=>['node_modules','dist','.slidev'].includes(part))})
    const npm=path.join(path.dirname(process.execPath),'node_modules/npm/bin/npm-cli.js')
    if(!existsSync(npm))throw new Error('Evaluator npm executable is unavailable.')
    await command('install',[npm,'install','--no-audit','--no-fund'],working)
    await command('production-build',[npm,'run','build'],working)
    if(!existsSync(path.join(working,'dist/index.html')))throw new Error('Production build did not create dist/index.html.')
    await cp(path.join(working,'dist'),html,{recursive:true})
    await command('singlefile-build',[npm,'run','build:html'],working)
    if(!existsSync(path.join(working,'dist/slidev.html')))throw new Error('Direct-open build did not create dist/slidev.html.')
    const workingPackageSha=createHash('sha256').update(await readFile(path.join(working,'package.json'))).digest('hex')
    add('submitted-package-unchanged-by-build',workingPackageSha!==sourceHashes['package.json']?['A dependency install/build changed submitted package.json; no evaluator repair is accepted.']:[],{workingPackageSha,submittedPackageSha:sourceHashes['package.json']})
  }
  const localRequire=createRequire(path.join(working,'package.json'))
  const parser=await import(pathToFileURL(localRequire.resolve('@slidev/parser')).href)
  const parsedSlides=parser.parseSync(await readFile(path.join(deck,'slides.md'),'utf8'),path.join(deck,'slides.md')).slides
  add('native-parser-three-slides',parsedSlides.length!==3?['Submitted deck does not contain exactly three native Slidev slides.']:[],{count:parsedSlides.length})
  const palettes=JSON.parse(await readFile(path.join(pack,'public/hyperframes/colorsets.json'),'utf8')).colorsets
  const palette=palettes.colorset1
  server=http.createServer(async(request,response)=>{
    try{let candidate=path.resolve(html,'.'+decodeURIComponent(new URL(request.url||'/','http://local').pathname));if(candidate!==html&&!candidate.startsWith(html+path.sep)){response.writeHead(403).end();return}if(!existsSync(candidate)||(await stat(candidate)).isDirectory())candidate=path.join(html,'index.html');response.writeHead(200,{'content-type':mime[path.extname(candidate)]||'application/octet-stream'}).end(await readFile(candidate))}catch(error){response.writeHead(500).end(String(error))}
  })
  await new Promise<void>(resolve=>server!.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${(server.address() as any).port}`
  browser=await chromium.launch({headless:true});page=await browser.newPage({viewport:{width:1280,height:800}})
  page.on('pageerror',(error:Error)=>{if(!String(error).includes('Wake Lock permission request denied'))errors.push(String(error))})
  page.on('request',(request:any)=>{const url=request.url();if(!url.startsWith(base)&&!url.startsWith('data:')&&!url.startsWith('blob:'))requests.push({url,method:request.method()})})
  await page.goto(base+'/1?clicks=0',{waitUntil:'networkidle'});hashRouting=new URL(page.url()).hash.startsWith('#/')
  for(const slide of [1,2]){
    await openSlide(base,slide)
    const before=await capture(`slide-${slide}-cue-0`,0,palette)
    await navigate('ArrowRight');add(`slide-${slide}-native-click-1`,routeState(page.url()).slide!==slide||routeState(page.url()).clicks!==1?['First native click did not stay on the requested slide/click 1.']:[],{url:page.url()})
    const middle=await capture(`slide-${slide}-cue-4`,4,palette)
    await navigate('ArrowRight');add(`slide-${slide}-native-click-2`,routeState(page.url()).slide!==slide||routeState(page.url()).clicks!==2?['Second native click did not stay on the requested slide/click 2.']:[],{url:page.url()})
    const after=await capture(`slide-${slide}-cue-9`,9,palette)
    add(`slide-${slide}-actual-paint-change`,sameState(before.scene,middle.scene)||sameState(middle.scene,after.scene)?['Cue changes did not change actual readouts and geometry.']:[])
    await navigate('ArrowLeft');const replayMiddle=await capture(`slide-${slide}-back-4`,4,palette,false)
    await navigate('ArrowLeft');const replayBefore=await capture(`slide-${slide}-back-0`,0,palette,false)
    add(`slide-${slide}-backward-replay`,!sameState(before.scene,replayBefore.scene)||!sameState(middle.scene,replayMiddle.scene)?['Backward navigation did not restore the same actual state.']:[])
    await navigate('ArrowRight');await navigate('ArrowRight')
    if(slide===2){
      const original=(await hostAudit((await currentFrame()).wrapper)).width
      const narrow=await constrainCell(680);await page.waitForTimeout(350);await capture('slide-2-live-cell-inner-680',9,palette)
      add('actual-inner-width-680',[Math.abs(narrow.parentWidth-680)>1||Math.abs(narrow.actualAvailableWidth-680)>1?'Actual available inner layout did not become 680 CSS px.':'',narrow.selectedCanvas?'The evaluator selected the Slidev canvas instead of the layout container.':'',!narrow.spansBothCells?'Selected available-width ancestor does not visibly span both actual cells.':''].filter(Boolean),{narrow})
      await constrainCell(null);await page.waitForTimeout(350);const restored=await capture('slide-2-live-cell-inner-restored',9,palette,false)
      add('actual-cell-width-restored',Math.abs(restored.result.host.width-original)>1?['Actual live player width was not restored.']:[],{initialPlayerWidth:original,restoredPlayerWidth:restored.result.host.width})
    }
    await page.emulateMedia({reducedMotion:'reduce'});await capture(`slide-${slide}-reduced-motion`,9,palette,false);await page.emulateMedia({reducedMotion:'no-preference'})
    const play=page.getByRole('button',{name:/^Play animation$/i})
    if(!await play.count())add(`slide-${slide}-preview-control`,['No accessible Play animation button.'])
    else{
      await play.first().click();const playing=await currentFrame(),start=await sceneAudit(playing.frame,palette);await page.waitForTimeout(650);const progressed=await sceneAudit(playing.frame,palette)
      add(`slide-${slide}-preview-progress`,sameState(start,progressed)?['Play preview did not advance the actual scene.']:[],{start,progressed})
      add(`slide-${slide}-pause-control`,await page.getByRole('button',{name:/^Pause animation$/i}).count()?[]:['No accessible Pause animation control while playing.'])
      await navigate('ArrowRight');await page.waitForTimeout(250)
      let stopped:any,still:any,disposed=false
      try{stopped=await sceneAudit(playing.frame,palette);await page.waitForTimeout(600);still=await sceneAudit(playing.frame,palette)}catch{disposed=true}
      add(`slide-${slide}-inactive-lifecycle`,!disposed&&!sameState(stopped,still)?['Hidden animation kept changing after leaving its slide.']:[],{disposed,stopped,still})
      await navigate('ArrowLeft');await capture(`slide-${slide}-return-selected-cue`,9,palette,false)
      add(`slide-${slide}-no-duplicate-visible-player`,await (await wrappers()).count()!==1?['Repeated entry created multiple visible player wrappers.']:[])
    }
  }
  await openSlide(base,3);const exported=await capture('slide-3-http-static-9',9,palette)
  add('http-static-export-path',exported.result.host.static!=='true'?['Export slide did not choose the supported static view.']:[])
  await exported.wrapper.screenshot({path:path.join(output,'http-static-scene-9.png')})
  await page.goto(pathToFileURL(path.join(working,'dist/slidev.html')).href,{waitUntil:'load'});await page.waitForTimeout(700)
  for(let i=0;i<6;i++)await navigate('ArrowRight')
  const fallback=(await wrappers()).first();await fallback.waitFor({timeout:30000})
  await page.waitForFunction(()=>[...document.querySelectorAll<HTMLElement>('.hyperframe-slide')].some(element=>element.dataset.sourceKind==='fallback'&&element.dataset.ready==='true'&&element.getBoundingClientRect().width>0),null,{timeout:30000})
  await fallback.evaluate((element:HTMLElement)=>element.setAttribute('data-evaluator-fallback-active','true'))
  const fallbackScene=await sceneAudit(page.mainFrame(),palette,'[data-evaluator-fallback-active]')
  const fallbackHost=await hostAudit(fallback)
  const fileFailures=[...fallbackScene.failures,...fallbackHost.failures,...compareState(fallbackScene,9)]
  if(fallbackHost.sourceKind!=='fallback')fileFailures.push('Direct-open export did not select the deterministic fallback.')
  if(await fallback.locator('iframe').count())fileFailures.push('Direct-open fallback still contains a relative live iframe.')
  if(!sameState(fallbackScene,exported.scene))fileFailures.push('Direct-open actual still differs from the HTTP 9-second composition state.')
  add('file-protocol-static-fallback-9',fileFailures,{scene:fallbackScene,host:fallbackHost,url:page.url()})
  await page.screenshot({path:path.join(output,'slide-3-direct-open-static-9.png'),fullPage:true})
  await fallback.screenshot({path:path.join(output,'file-static-scene-9.png')})
  const httpImage=await sharp(path.join(output,'http-static-scene-9.png')).ensureAlpha().raw().toBuffer({resolveWithObject:true})
  const fileImage=await sharp(path.join(output,'file-static-scene-9.png')).resize(httpImage.info.width,httpImage.info.height).ensureAlpha().raw().toBuffer({resolveWithObject:true})
  let totalDifference=0,largeDifference=0
  for(let i=0;i<httpImage.data.length;i++){const delta=Math.abs(httpImage.data[i]-fileImage.data[i]);totalDifference+=delta;if(delta>20)largeDifference++}
  add('http-file-raster-review-evidence',[],{diagnosticOnly:true,width:httpImage.info.width,height:httpImage.info.height,meanAbsoluteChannelDifference:totalDifference/httpImage.data.length,fractionChannelsDifferingByMoreThan20:largeDifference/httpImage.data.length,images:['http-static-scene-9.png','file-static-scene-9.png'],manualComparisonRequired:true})
  const fallbackIds=await page.locator('.hyperframe-fallback [data-scene-svg] [id]').evaluateAll((elements:Element[])=>elements.map(element=>element.id))
  add('file-fallback-unique-accessibility-ids',new Set(fallbackIds).size!==fallbackIds.length?['Fallback composition IDs collide across mounted instances.']:[],{ids:fallbackIds})
  add('local-runtime-requests',requests.filter(request=>!request.url.startsWith('file:')).map(request=>'Unexpected nonlocal runtime request: '+request.url),{requests})
}catch(error){errors.push(String(error));add('native-execution',[String(error)])}
finally{
  if(browser)await browser.close()
  if(server)await new Promise<void>(resolve=>server!.close(()=>resolve()))
  sourceAfter=await digests(deck)
  add('authored-source-unchanged',JSON.stringify(sourceHashes)!==JSON.stringify(sourceAfter)?['Evaluator changed authored deck sources.']:[],{sourceHashes,sourceAfter})
  const report={passed:cases.every(result=>result.passed)&&errors.length===0,evaluatorSha256,deck,pack,output,cases,errors,requests,commands,packHashes,sourceHashes,sourceAfter}
  await writeFile(path.join(output,'verification.json'),JSON.stringify(report,null,2))
  console.log(JSON.stringify({passed:report.passed,cases:cases.length,failed:cases.filter(result=>!result.passed).map(({id,failures})=>({id,failures})),errors,evaluatorSha256,report:path.join(output,'verification.json')},null,2))
  if(!report.passed)process.exitCode=1
}
