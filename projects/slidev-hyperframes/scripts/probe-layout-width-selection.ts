#!/usr/bin/env -S npx tsx
// Run: node --experimental-strip-types <this-script> --output <project-artifact-directory>
// Evaluator-only diagnostic: use the exact current grader's selector against retained built outputs.
import {readFile,mkdir,writeFile,stat} from 'node:fs/promises'
import {existsSync} from 'node:fs'
import path from 'node:path'
import {createHash} from 'node:crypto'
import {createRequire,stripTypeScriptTypes} from 'node:module'
import http from 'node:http'
const args=process.argv.slice(2),output=path.resolve(args[args.indexOf('--output')+1])
const grader=path.resolve('projects/slidev-hyperframes/scripts/verify-generated-hyperframes-deck.ts')
const source=await readFile(grader,'utf8'),sha256=createHash('sha256').update(source).digest('hex')
function definition(name:string,next:string){const start=source.indexOf('async function '+name+'('),end=source.indexOf(next,start);return stripTypeScriptTypes(source.slice(start,end),{mode:'strip'})}
const selector=definition('constrainCell','\n\ntry{'),audit=definition('hostAudit','\nasync function capture')
const require=createRequire(path.resolve('skills/slidev-echarts/assets/examples/slidev-echarts/package.json'))
const {chromium}=require('playwright'),browser=await chromium.launch({headless:true}),results:any[]=[]
await mkdir(output,{recursive:true})
const mime:Record<string,string>={'.html':'text/html','.js':'text/javascript','.css':'text/css','.woff2':'font/woff2','.svg':'image/svg+xml','.json':'application/json'}
for(const form of [{owner:'echarts',id:'20261005-slidev-hyperframes-echarts-sol-contract',group:'pi-final'},{owner:'animejs',id:'20261005-slidev-hyperframes-animejs-sol-contract',group:'pi-final'},{owner:'standalone-engine',id:'20261005-slidev-hyperframes-echarts-sol-v2-natural-3',group:'pi-v2-final'},{owner:'scaffold-prototype',id:'scaffold-prototype',group:'generator-golden/prototype/verification',direct:true}]){
  const {owner,id,group}=form,html=path.resolve('projects/slidev-hyperframes/artifacts/'+group+('direct' in form?'':'/'+id)+'/http-html')
  const server=http.createServer(async(req,res)=>{try{let file=path.resolve(html,'.'+new URL(req.url||'/','http://local').pathname);if(!file.startsWith(html+path.sep)||!existsSync(file)||(await stat(file)).isDirectory())file=path.join(html,'index.html');res.writeHead(200,{'content-type':mime[path.extname(file)]||'application/octet-stream'}).end(await readFile(file))}catch(error){res.writeHead(500).end(String(error))}})
  await new Promise<void>(resolve=>server.listen(0,'127.0.0.1',resolve))
  const page=await browser.newPage({viewport:{width:1280,height:800}}),base='http://127.0.0.1:'+(server.address() as any).port
  const constrain=new Function('page',selector+'; return constrainCell')(page),hostAudit=new Function('page',audit+'; return hostAudit')(page)
  try{
    await page.goto(base+'/2?clicks=2',{waitUntil:'networkidle'})
    if(new URL(page.url()).hash.startsWith('#/'))await page.goto(base+'/#/2?clicks=2',{waitUntil:'networkidle'})
    const wrapper=page.locator('.hyperframe-slide:visible').first()
    await page.waitForFunction(()=>[...document.querySelectorAll<HTMLElement>('.hyperframe-slide')].some(e=>e.dataset.ready==='true'&&e.getBoundingClientRect().width>0),null,{timeout:45000})
    await page.screenshot({path:path.join(output,owner+'-base.png')})
    const initial=await hostAudit(wrapper),narrow=await constrain(680),narrowAudit=await hostAudit(wrapper)
    const contentGroupGlyphs=owner==='scaffold-prototype'?await page.evaluate(()=>[...document.querySelectorAll<HTMLElement>('[data-evaluator-hyperframes-cell] article')].flatMap(group=>{
      const outer=group.closest<HTMLElement>('[data-evaluator-hyperframes-cell]')!,inside=group.getBoundingClientRect(),outside=outer.getBoundingClientRect()
      return[...group.querySelectorAll<HTMLElement>('p,h2')].flatMap(text=>{const range=document.createRange();range.selectNodeContents(text);const crosses=(glyph:DOMRect,bounds:DOMRect)=>glyph.left<bounds.left-1||glyph.top<bounds.top-1||glyph.right>bounds.right+1||glyph.bottom>bounds.bottom+1;return[...range.getClientRects()].map(glyph=>({text:text.textContent,groupOverflow:getComputedStyle(group).overflow,glyph:{x:glyph.x,y:glyph.y,width:glyph.width,height:glyph.height},group:{x:inside.x,y:inside.y,width:inside.width,height:inside.height},outerCard:{x:outside.x,y:outside.y,width:outside.width,height:outside.height},crossesGroup:crosses(glyph,inside),crossesActualCard:crosses(glyph,outside)}))})
    })):undefined
    await page.screenshot({path:path.join(output,owner+'-actual-680.png')})
    let clippingNegative:any,cardNegative:any
    if(owner==='scaffold-prototype'){
      await page.evaluate(()=>{const group=document.querySelector<HTMLElement>('[data-evaluator-hyperframes-cell] article')!;group.dataset.evaluatorSavedStyle=group.getAttribute('style')||'';group.style.height='40px';group.style.overflow='hidden'})
      clippingNegative=await hostAudit(wrapper)
      await page.screenshot({path:path.join(output,'scaffold-prototype-deliberate-nested-clip.png')})
      await page.evaluate(()=>{const group=document.querySelector<HTMLElement>('[data-evaluator-hyperframes-cell] article')!;group.setAttribute('style',group.dataset.evaluatorSavedStyle!);delete group.dataset.evaluatorSavedStyle})
      await page.evaluate(()=>{const card=[...document.querySelectorAll<HTMLElement>('[data-evaluator-hyperframes-cell]')].find(card=>card.querySelector('article'))!;card.dataset.evaluatorSavedStyle=card.getAttribute('style')||'';card.style.height='40px';card.style.minHeight='40px'})
      cardNegative=await hostAudit(wrapper)
      await page.screenshot({path:path.join(output,'scaffold-prototype-deliberate-card-clip.png')})
      await page.evaluate(()=>{const card=[...document.querySelectorAll<HTMLElement>('[data-evaluator-hyperframes-cell]')].find(card=>card.querySelector('article'))!;card.setAttribute('style',card.dataset.evaluatorSavedStyle!);delete card.dataset.evaluatorSavedStyle})
      if(!clippingNegative.failures.includes('A visible cell label crosses an explicitly clipping descendant.'))throw Error('Explicit nested clip was not rejected')
      if(!cardNegative.failures.includes('A visible cell label crosses its actual card bounds.'))throw Error('Actual fixed-budget card clip was not rejected')
    }
    const restored=await constrain(null),restoreAudit=await hostAudit(wrapper)
    await page.screenshot({path:path.join(output,owner+'-restored.png')})
    results.push({id,diagnosticOnly:true,selectorPassed:Math.abs(narrow.parentWidth-680)<=1&&Math.abs(narrow.actualAvailableWidth-680)<=1&&!narrow.selectedCanvas&&narrow.spansBothCells,initial,narrow,narrowAudit,restored,restoreAudit,contentGroupGlyphs,clippingNegative,cardNegative})
    if(owner==='standalone-engine'){
      // Evaluator regression only: a fixed authored inline width must survive the ordinary container rule.
      await wrapper.evaluate((element:HTMLElement)=>{element.closest<HTMLElement>('[data-layout-mode]')!.style.width='800px'})
      const fixedWidth=await constrain(680)
      results.at(-1).fixedWidthNegative={expectedWidth:800,observed:fixedWidth.actualAvailableWidth,rejectedNarrow:Math.abs(fixedWidth.actualAvailableWidth-680)>1}
      if(Math.abs(fixedWidth.actualAvailableWidth-800)>1)results.at(-1).selectorPassed=false
    }
  }catch(error){results.push({id,diagnosticOnly:true,error:String(error)})}
  finally{await page.close();await new Promise<void>(resolve=>server.close(()=>resolve()))}
}
await browser.close()
await writeFile(path.join(output,'selection-verification.json'),JSON.stringify({diagnosticOnly:true,evaluatorSha256:sha256,results},null,2))
console.log(JSON.stringify({evaluatorSha256:sha256,results:results.map(({id,selectorPassed,narrow,narrowAudit,error})=>({id,selectorPassed,narrow,nativeGeometryFailures:narrowAudit?.failures,error}))},null,2))
if(results.some(result=>!result.selectorPassed))process.exitCode=1
