#!/usr/bin/env -S npx tsx
// Diagnostic only. Run: npx tsx projects/plantuml-style-repair/scripts/audit_native_gallery.ts --phase baseline-expanded
// Node 24's native TypeScript runner also works: node projects/plantuml-style-repair/scripts/audit_native_gallery.ts --phase current
// Publication gate: append --published --expected-ref <full-40-hex-commit-sha> --require-clean.
// Uses bundled Playwright, no renderer, native finisher, or palette-helper imports.
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const {execFileSync} = require('child_process');
const {chromium} = require('C:/Users/villa/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = 'C:/Users/villa/dev/skills';
const out = path.join(root,'projects/plantuml-style-repair/artifacts');
const phase = process.argv.includes('--phase') ? process.argv[process.argv.indexOf('--phase')+1] : 'current';
if (!/^[a-z0-9-]+$/.test(phase)) throw new Error('Phase must use lowercase hyphen-case');
const publishedRequested=process.argv.includes('--published');
const expectedRef=process.argv.includes('--expected-ref')?process.argv[process.argv.indexOf('--expected-ref')+1]:null;
if(publishedRequested&&(!expectedRef||!/^[a-f0-9]{40}$/i.test(expectedRef)))throw new Error('--published requires --expected-ref with the full 40-hex commit SHA');
if(expectedRef&&(!/^[a-f0-9]{40}$/i.test(expectedRef)||execFileSync('git',['cat-file','-t',expectedRef],{cwd:root,encoding:'utf8'}).trim()!=='commit'))throw new Error('--expected-ref must resolve to a commit');
const committedBytes=relative=>execFileSync('git',['show',`${expectedRef}:${relative.replaceAll('\\','/')}`],{cwd:root,maxBuffer:64*1024*1024});
const screenshotDir=path.join(out,'screenshots',phase);fs.mkdirSync(screenshotDir,{recursive:true});
fs.mkdirSync(path.join(out,'reviews'),{recursive:true});
const skill = path.join(root,'skills/plantuml-colorset-renderer');
const galleries = {colorset2:'plantuml-colorset-renderer',colorset1:'plantuml-colorset-renderer-cs1'};
const semanticReviewIds=['activity','sdl','state','sequence','component','class','object','ie','deployment','packetdiag','timing','ditaa','chen','json','yaml','ebnf','regex','archimate','gantt','mindmap','wbs','nwdiag'];
const sha = text => crypto.createHash('sha256').update(text).digest('hex');
const signatureDifferences=(native,mounted)=>{const differences=[];for(const key of Object.keys(native)){if(JSON.stringify(native[key])===JSON.stringify(mounted[key]))continue;if(Array.isArray(native[key])&&Array.isArray(mounted[key])){for(let index=0;index<Math.max(native[key].length,mounted[key].length);index++)if(JSON.stringify(native[key][index])!==JSON.stringify(mounted[key][index]))differences.push({field:key,index,native:native[key][index],mounted:mounted[key][index]});}else differences.push({field:key,native:native[key],mounted:mounted[key]});}return differences};
const server = http.createServer((req,res)=>{
  const target = path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if (!target.startsWith(root.replaceAll('/',path.sep))) {res.writeHead(403).end();return;}
  let file = target; if(fs.existsSync(file)&&fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
  if(!fs.existsSync(file)){res.writeHead(404).end();return;}
  const ext=path.extname(file);res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png'})[ext]||'application/octet-stream');
  res.end(fs.readFileSync(file));
});
async function auditSvg(page, content, fixtureId, colorset, selector='svg'){
  if(content!==null){
    await page.setContent('<!doctype html><body style="margin:0;background:white"></body>');
    await page.evaluate(text=>{const doc=new DOMParser().parseFromString(text,'image/svg+xml');document.body.append(document.importNode(doc.documentElement,true));},content);
  }
  return await page.evaluate(({fixtureId,colorset,selector})=>{
    const svg=document.querySelector(selector);
    const sizeTolerance=.000001;
    const geom=[...svg.querySelectorAll('rect,ellipse,circle,path,polygon,polyline,line')].filter(e=>!e.closest('defs'));
    const vb=svg.viewBox.baseVal;
    const rgb=c=>{const n=c.match(/\d+(?:\.\d+)?/g);return n?n.slice(0,3).map(Number):[255,255,255]};
    const alpha=c=>{const n=c.match(/\d+(?:\.\d+)?/g);return n&&n.length>3?Number(n[3]):1};
    const blend=(paint,base,opacity)=>{const a=alpha(paint)*opacity,p=rgb(paint),b=rgb(base);return `rgb(${p.map((v,i)=>v*a+b[i]*(1-a)).join(', ')})`};
    const lum=c=>rgb(c).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
    const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
    const matrix=svg.getScreenCTM();
    const pointToLocal=(e,p)=>new DOMPoint(p.x,p.y).matrixTransform(matrix).matrixTransform(e.getScreenCTM().inverse());
    const hit=(e,p)=>{try{return e.isPointInFill(pointToLocal(e,p))}catch{return false}};
    const css=e=>getComputedStyle(e);
    const paintOrder=new Map([...svg.querySelectorAll('*')].map((e,i)=>[e,i]));
    const opacity=e=>{let a=1;for(let p=e;p instanceof SVGElement;p=p.parentElement)a*=+css(p).opacity;return a};
    const fill=e=>css(e).fill;
    // SVG lines have no fill area even when computed fill inherits black.
    // Chromium isPointInFill(line) can nevertheless hit its zero-area contour.
    const painted=geom.filter(e=>e.localName!=='line'&&fill(e)!=='none'&&Number(css(e).fillOpacity)>0&&Number(css(e).opacity)>0);
    const rootPoint=(e,p)=>new DOMPoint(p.x,p.y).matrixTransform(e.getScreenCTM()).matrixTransform(matrix.inverse());
    const box=e=>{const r=e.getBBox(),ps=[{x:r.x,y:r.y},{x:r.x+r.width,y:r.y},{x:r.x+r.width,y:r.y+r.height},{x:r.x,y:r.y+r.height}].map(p=>rootPoint(e,p));return {x:Math.min(...ps.map(p=>p.x)),y:Math.min(...ps.map(p=>p.y)),width:Math.max(...ps.map(p=>p.x))-Math.min(...ps.map(p=>p.x)),height:Math.max(...ps.map(p=>p.y))-Math.min(...ps.map(p=>p.y))}};
    const shapeId=e=>e.id||`${fixtureId}-${e.localName}-${geom.indexOf(e)}`;
    const canvas=e=>{const b=box(e);return b.x<=.1&&b.y<=.1&&b.width>=vb.width-.2&&b.height>=vb.height-.2};
    // Exact contour contact has no interior area; probe only .0001 units to
    // reject floating-point boundary hits while retaining narrow actual insets.
    const interiorHit=(e,p)=>[{x:p.x,y:p.y},{x:p.x-.0001,y:p.y},{x:p.x+.0001,y:p.y},{x:p.x,y:p.y-.0001},{x:p.x,y:p.y+.0001}].every(q=>hit(e,q));
    const rootCanvas=blend(css(svg).backgroundColor,'rgb(255, 255, 255)',1);
    const canvasFill=painted.filter(canvas).reduce((paint,e)=>blend(fill(e),paint,opacity(e)*+css(e).fillOpacity),rootCanvas);
    const backdrop=(p,exclude=new Set(),before=null)=>{let color=rootCanvas,id='canvas';for(const e of painted){if(!exclude.has(e)&&(!before||paintOrder.get(e)<paintOrder.get(before))&&interiorHit(e,p)){color=blend(fill(e),color,opacity(e)*+css(e).fillOpacity);id=canvas(e)?'canvas':shapeId(e)}}return {color,id}};
    const occluded=(e,p,exclude=new Set())=>painted.some(paint=>!exclude.has(paint)&&paintOrder.get(paint)>paintOrder.get(e)&&interiorHit(paint,p));
    const texts=[...svg.querySelectorAll('text')].map((e,i)=>{
      const b=box(e),points=[.2,.5,.8].map(f=>({x:b.x+b.width*f,y:b.y+b.height*.5}));
      const backings=points.map(p=>backdrop(p));
      const color=fill(e);const scores=backings.map(b=>({backing:b.color,shapeId:b.id,contrast:ratio(blend(color,b.color,opacity(e)*+css(e).fillOpacity),b.color),black:ratio('rgb(0, 0, 0)',b.color),white:ratio('rgb(255, 255, 255)',b.color)}));
      const black=Math.min(...scores.map(s=>s.black)),white=Math.min(...scores.map(s=>s.white));
      const expected=black>=white?'rgb(0, 0, 0)':'rgb(255, 255, 255)';
      return {id:`${fixtureId}-text-${i}`,label:e.textContent,box:b,fill:color,backings:[...new Set(backings.map(b=>b.color))],backingShapeIds:[...new Set(backings.map(b=>b.id))],contrast:Math.min(...scores.map(s=>s.contrast)),expected,optimal:color===expected,insideBody:backings.some(b=>b.id!=='canvas'),scores};
    });
    const visibleLabel=t=>t.label.replace(/[\s\uFFFD\u00A0]/g,'').length>0;
    const bodies=painted.filter(e=>!canvas(e)&&texts.some(t=>visibleLabel(t)&&t.backingShapeIds.includes(shapeId(e)))).map(e=>{
      const st=css(e),b=box(e);return {id:shapeId(e),tag:e.localName,box:b,fill:st.fill,opacity:st.opacity,fillOpacity:st.fillOpacity,stroke:st.stroke,strokeWidth:parseFloat(st.strokeWidth),outlined:st.stroke!=='none'&&parseFloat(st.strokeWidth)>0&&+st.strokeOpacity>0,labels:texts.filter(t=>t.backingShapeIds.includes(shapeId(e))).map(t=>t.label),entity:e.closest('.entity')?.getAttribute('data-entity')||e.closest('.entity')?.id||null,link:!!e.closest('.link')};
    });
    const arrows=[];
    for(const g of svg.querySelectorAll('g.link,g.message')){
      const members=geom.filter(e=>g.contains(e)),exclude=new Set(members);
      const targetId=g.getAttribute('data-entity-2');
      const targetGroup=targetId?svg.querySelector(`[id="${CSS.escape(targetId)}"]`):null;
      const targetPaints=targetGroup?painted.filter(e=>targetGroup.contains(e)):[];
      const insideTarget=p=>targetPaints.some(e=>[{x:p.x,y:p.y},{x:p.x-.5,y:p.y},{x:p.x+.5,y:p.y},{x:p.x,y:p.y-.5},{x:p.x,y:p.y+.5}].every(q=>hit(e,q)));
      const touchesTarget=p=>targetPaints.some(e=>hit(e,p));
      const shaft=members.find(e=>['path','line','polyline'].includes(e.localName)&&fill(e)==='none'&&css(e).stroke!=='none');
      if(!shaft)continue;
      const sample=(e)=>{const len=e.getTotalLength(),step=Math.max(1,Math.ceil(len)),samples=[];for(let i=0;i<=step;i++){const p=rootPoint(e,e.getPointAtLength(len*i/step));if(occluded(e,p,exclude))continue;const b=backdrop(p,exclude,e),s=css(e),paint=s.stroke==='none'?fill(e):s.stroke;const a=opacity(e)*(s.stroke==='none'?+s.fillOpacity:+s.strokeOpacity);samples.push({x:p.x,y:p.y,part:s.stroke==='none'?'fill':'stroke',backing:b.color,backingId:b.id,contrast:ratio(blend(paint,b.color,a),b.color)});}return samples};
      const points=sample(shaft),heads=members.filter(e=>e!==shaft&&['polygon','path','line','polyline','ellipse','circle'].includes(e.localName)).map(e=>{
        let points=[];try{points=sample(e)}catch{};
        const s=css(e),b=box(e),hollow=fill(e)==='rgb(255, 255, 255)'&&s.stroke!=='none'&&parseFloat(s.strokeWidth)>0;
        if(fill(e)!=='none'&&!hollow){
          for(let x=b.x+.5;x<b.x+b.width;x+=1)for(let y=b.y+.5;y<b.y+b.height;y+=1){const p={x,y};if(hit(e,p)&&!occluded(e,p,exclude)){const back=backdrop(p,exclude,e);points.push({x,y,part:'fill',backing:back.color,backingId:back.id,contrast:ratio(blend(fill(e),back.color,opacity(e)*+s.fillOpacity),back.color)});}}
        }
        const strokePoints=points.filter(p=>p.part==='stroke'),halfStroke=parseFloat(s.strokeWidth)/2;
        const strokeEnvelopeTouches=strokePoints.filter(p=>[0,1,2,3,4,5,6,7].some(i=>touchesTarget({x:p.x+Math.cos(i*Math.PI/4)*halfStroke,y:p.y+Math.sin(i*Math.PI/4)*halfStroke}))).length;
        return {id:shapeId(e),tag:e.localName,fill:fill(e),stroke:s.stroke,strokeWidth:parseFloat(s.strokeWidth),box:b,hollow,minimumContrast:points.length?Math.min(...points.map(p=>p.contrast)):null,minimumFillContrast:points.some(p=>p.part==='fill')?Math.min(...points.filter(p=>p.part==='fill').map(p=>p.contrast)):null,minimumStrokeContrast:points.some(p=>p.part==='stroke')?Math.min(...points.filter(p=>p.part==='stroke').map(p=>p.contrast)):null,backings:[...new Set(points.map(p=>p.backing))],bodyOverlapSamples:points.filter(p=>p.backingId!=='canvas').length,targetInteriorOverlapSamples:points.filter(p=>insideTarget(p)).length,targetStrokeEnvelopeContactSamples:strokeEnvelopeTouches,targetPaints:targetPaints.map(shapeId),nativeClearance:e.getAttribute('data-arrow-clearance'),totalSamples:points.length};
      });
      arrows.push({id:g.id||shaft.id,source:g.getAttribute('data-entity-1'),target:g.getAttribute('data-entity-2'),shaftId:shapeId(shaft),shaftStroke:css(shaft).stroke,shaftWidth:parseFloat(css(shaft).strokeWidth),minimumContrast:Math.min(...points.map(p=>p.contrast)),backings:[...new Set(points.map(p=>p.backing))],badSamples:points.filter(p=>p.contrast<3),heads});
    }
    // Ungrouped primitives are checked independently of native grouping metadata.
    // Family role decisions are explicit below; measurement uses browser geometry.
    const connectorFamilies=new Set(['activity','sdl','ebnf','regex','mindmap','wbs','nwdiag','json','yaml','gantt']);
    const primitiveTraces=[];
    if(connectorFamilies.has(fixtureId)||fixtureId==='negative-controls'){
      for(const e of geom){
        if(e.closest('.entity,.participant,.link,.message'))continue;
        const s=css(e),b=box(e);
        const head=(['activity','sdl','gantt','negative-controls'].includes(fixtureId)&&e.localName==='polygon'||['json','yaml','ebnf','regex'].includes(fixtureId)&&e.localName==='path'&&fill(e)!=='none')&&Math.min(b.width,b.height)<=12+sizeTolerance&&Math.max(b.width,b.height)<=14+sizeTolerance;
        const port=['json','yaml','ebnf','regex'].includes(fixtureId)&&['ellipse','circle'].includes(e.localName)&&b.width<=8+sizeTolerance&&b.height<=8+sizeTolerance;
        const shaft=['path','line','polyline'].includes(e.localName)&&s.stroke!=='none'&&fill(e)==='none';
        if(!head&&!shaft&&!port)continue;
        // The shaft/head/port of the same connector is foreground, never its backing.
        // Exclude those small native glyphs while retaining every category surface.
        const exclude=new Set([e,...geom.filter(other=>{
          const bb=box(other);return ((['activity','sdl','gantt','negative-controls'].includes(fixtureId)&&other.localName==='polygon'||['json','yaml','ebnf','regex'].includes(fixtureId)&&other.localName==='path'&&fill(other)!=='none')&&Math.min(bb.width,bb.height)<=12+sizeTolerance&&Math.max(bb.width,bb.height)<=14+sizeTolerance)||(['json','yaml','ebnf','regex'].includes(fixtureId)&&['ellipse','circle'].includes(other.localName)&&bb.width<=8+sizeTolerance&&bb.height<=8+sizeTolerance);
        })]);const points=[];const len=e.getTotalLength(),steps=Math.max(1,Math.ceil(len));
        for(let i=0;i<=steps;i++){
          const p=rootPoint(e,e.getPointAtLength(len*i/steps));if(occluded(e,p,exclude))continue;const back=backdrop(p,exclude,e);
          const visible=[];if(s.stroke!=='none')visible.push({part:'stroke',paint:s.stroke,opacity:opacity(e)*+s.strokeOpacity});if((head||port)&&fill(e)!=='none')visible.push({part:'fill',paint:fill(e),opacity:opacity(e)*+s.fillOpacity});
          for(const v of visible)points.push({x:p.x,y:p.y,part:v.part,backing:back.color,backingId:back.id,contrast:ratio(blend(v.paint,back.color,v.opacity),back.color)});
        }
        primitiveTraces.push({id:shapeId(e),role:head?'arrowhead':port?'connector-port':'connector-track',tag:e.localName,box:b,fill:fill(e),stroke:s.stroke,strokeWidth:parseFloat(s.strokeWidth),minimumContrast:Math.min(...points.map(p=>p.contrast)),backings:[...new Set(points.map(p=>p.backing))],badSamples:points.filter(p=>p.contrast<3),bodyOverlapSamples:head?points.filter(p=>p.backingId!=='canvas').length:null,totalSamples:points.length});
      }
    }
    const invisibleOpenDetails=geom.filter(e=>e.localName==='path'&&fill(e)==='none'&&css(e).stroke==='none'&&e.closest('.entity,.participant')).map(e=>({id:shapeId(e),box:box(e),group:e.closest('.entity,.participant').id}));
    const invisibleSmallDetails=painted.filter(e=>{const b=box(e);if(!e.closest('.entity')||b.width>20||b.height>12)return false;const exclude=new Set([e]),center={x:b.x+b.width/2,y:b.y+b.height/2};return fill(e)===backdrop(center,exclude).color&&css(e).stroke==='none'}).map(e=>({id:shapeId(e),box:box(e),group:e.closest('.entity').id,fill:fill(e)}));
    const ganttTaskBodies=fixtureId==='gantt'?painted.filter(e=>e.localName==='rect'&&+e.getAttribute('rx')>0&&box(e).height<35).map(e=>({id:shapeId(e),box:box(e),fill:fill(e),stroke:css(e).stroke,strokeWidth:parseFloat(css(e).strokeWidth)})):[];
    const packetFields=fixtureId==='packetdiag'?painted.filter(e=>e.localName==='rect'&&box(e).height>10).map(e=>({id:shapeId(e),box:box(e),fill:fill(e),stroke:css(e).stroke,strokeWidth:parseFloat(css(e).strokeWidth),separatorContrast:css(e).stroke==='none'?0:ratio(css(e).stroke,fill(e))})):[];
    return {fixtureId,colorset,svgType:svg.getAttribute('data-diagram-type'),width:vb.width,height:vb.height,canvasFill,bodies,texts,arrows,primitiveTraces,invisibleOpenDetails,invisibleSmallDetails,ganttTaskBodies,packetFields,geometryCount:geom.length,filledShapeCount:painted.length};
  },{fixtureId,colorset,selector});
}
async function auditMountedAspect(page, colorset, viewport, scope='local'){
  return await page.evaluate(({colorset,viewport,scope})=>({colorset,viewport,scope,cards:[...document.querySelectorAll('.example-card')].map(card=>{
    const svg=card.querySelector('svg'),img=card.querySelector('img');
    const frame=card.querySelector('.viz-frame'),frameBox=frame.getBoundingClientRect(),frameRatioParts=getComputedStyle(frame).aspectRatio.split('/').map(Number),expectedFrameRatio=frameRatioParts[0]/(frameRatioParts[1]||1),frameRatio=frameBox.width/frameBox.height;
    const framePreserved=Number.isFinite(expectedFrameRatio)&&Math.abs(frameRatio/expectedFrameRatio-1)<.005;
    const frameEvidence={frameWidth:frameBox.width,frameHeight:frameBox.height,expectedFrameRatio,frameRatio,framePreserved};
    if(svg){
      const matrix=svg.getScreenCTM(),scaleX=matrix?Math.hypot(matrix.a,matrix.b):0,scaleY=matrix?Math.hypot(matrix.c,matrix.d):0;
      const uniform=scaleX>0&&scaleY>0&&Math.abs(scaleX/scaleY-1)<.00001;
      return {patternId:card.dataset.patternId,fixtureId:card.dataset.exampleId,format:'svg',preserveAspectRatio:svg.getAttribute('preserveAspectRatio'),scaleX,scaleY,inlineWidth:svg.style.width,inlineHeight:svg.style.height,...frameEvidence,preservesDimensions:uniform&&svg.getAttribute('preserveAspectRatio')==='xMidYMid meet'&&!svg.style.width&&!svg.style.height&&framePreserved};
    }
    if(img){const b=img.getBoundingClientRect(),naturalRatio=img.naturalWidth/img.naturalHeight;return {patternId:card.dataset.patternId,fixtureId:card.dataset.exampleId,format:'png',naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,displayWidth:b.width,displayHeight:b.height,...frameEvidence,preservesDimensions:img.naturalWidth>0&&img.naturalHeight>0&&b.width>0&&b.height>0&&Math.abs(b.width/b.height/naturalRatio-1)<.001&&framePreserved};}
    return {patternId:card.dataset.patternId,fixtureId:card.dataset.exampleId,format:null,preservesDimensions:false};
  })}),{colorset,viewport,scope});
}
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const port=server.address().port,browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const reports=[];
 const screenshotEvidence=[];
 for(const [colorset,dir] of Object.entries(galleries)){
   const galleryRoot=path.join(skill,'assets/examples',dir);const metadata=JSON.parse(fs.readFileSync(path.join(galleryRoot,'coverage.json'),'utf8'));
   for(const item of metadata.items){
     const data=fs.readFileSync(path.join(galleryRoot,item.asset));
     if(item.assetFormat!=='svg'){
       const patternId=`plantuml-${item.id}-${colorset==='colorset1'?'cs1':'cs2'}`;
       await page.setContent(`<!doctype html><body style="margin:0;background:white"><img src="data:image/png;base64,${data.toString('base64')}" alt="${item.id}"></body>`);
       await page.locator('img').evaluate(img=>img.decode());
       const dimensions=await page.locator('img').evaluate(img=>({width:img.naturalWidth,height:img.naturalHeight}));
       const screenshot=path.join(screenshotDir,`${item.id}-${colorset}-native.png`);
       await page.locator('img').screenshot({path:screenshot});
       reports.push({fixtureId:item.id,patternId,colorset,asset:item.asset,assetFormat:item.assetFormat,sha256:sha(data),dimensions,review:'raster-manual'});
       screenshotEvidence.push({patternId,asset:item.asset,format:item.assetFormat,viewport:'native',screenshot:path.relative(root,screenshot),dimensions});
       continue;
     }
     const report=await auditSvg(page,data.toString(),item.id,colorset);report.asset=item.asset;report.sha256=sha(data);report.patternId=`plantuml-${({'usecase':'use-case',math:'asciimath',latex:'jlatexmath',ie:'ie-er',chen:'chen-er',files:'file-tree',packetdiag:'packet'})[item.id]||item.id}-${colorset==='colorset1'?'cs1':'cs2'}`;
     reports.push(report);
     const screenshot=path.join(screenshotDir,`${item.id}-${colorset}-native.png`);
     await page.locator('svg').screenshot({path:screenshot});
     screenshotEvidence.push({patternId:report.patternId,asset:item.asset,format:item.assetFormat,viewport:'native',screenshot:path.relative(root,screenshot),dimensions:{width:report.width,height:report.height}});
   }
 }
 const galleryEvidence=[];
 const galleryPaintParity=[];
 const galleryAspectEvidence=[];
 const paintSignature=r=>JSON.stringify({canvasFill:r.canvasFill,bodies:r.bodies.map(b=>[b.id,b.fill,b.stroke,b.strokeWidth,b.opacity,b.fillOpacity]),texts:r.texts.map(t=>[t.label,t.fill,t.backings,t.expected,t.optimal]),arrows:r.arrows.map(a=>[a.id,a.shaftStroke,a.shaftWidth,a.minimumContrast,a.heads.map(h=>[h.fill,h.stroke,h.minimumContrast])]),primitives:r.primitiveTraces.map(p=>[p.id,p.fill,p.stroke,p.strokeWidth,p.minimumContrast])});
 const comparePaint=(raw,mounted,details={})=>({patternId:raw.patternId,colorset:raw.colorset,...details,matched:paintSignature(raw)===paintSignature(mounted),nativeSignatureSha256:sha(paintSignature(raw)),mountedSignatureSha256:sha(paintSignature(mounted)),differences:signatureDifferences(JSON.parse(paintSignature(raw)),JSON.parse(paintSignature(mounted))),mountedTextFailures:mounted.texts.filter(t=>!t.optimal).map(t=>t.label),mountedArrowFailures:mounted.arrows.filter(a=>a.minimumContrast<3).map(a=>a.id),mountedPrimitiveFailures:mounted.primitiveTraces.filter(p=>p.minimumContrast<3).map(p=>p.id)});
 for(const colorset of ['colorset2','colorset1']){
   const url=`http://127.0.0.1:${port}/skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/?theme=${colorset}`;
   await page.goto(url);await page.waitForSelector('body[data-load-state="loaded"]');await page.waitForTimeout(2600);
   galleryEvidence.push(await page.evaluate(()=>({url:location.href,theme:document.body.dataset.colorSet,report:document.querySelector('#active-render-report').href,cards:[...document.querySelectorAll('.example-card')].map(c=>({patternId:c.dataset.patternId,exampleId:c.dataset.exampleId,loadState:c.querySelector('.svg-mount').dataset.loadState,source:c.dataset.source,svgColorset:c.querySelector('svg')?.getAttribute('data-colorset')||null,svgType:c.querySelector('svg')?.getAttribute('data-diagram-type')||null,raster:c.querySelector('img')?.src||null})),overflow:document.documentElement.scrollWidth>innerWidth})));
   galleryAspectEvidence.push(await auditMountedAspect(page,colorset,'desktop'));
   for(const raw of reports.filter(r=>r.colorset===colorset&&r.texts)){
     const mounted=await auditSvg(page,null,raw.fixtureId,colorset,`article[data-example-id="${raw.fixtureId}"] svg`);
     galleryPaintParity.push(comparePaint(raw,mounted));
   }
   await page.screenshot({path:path.join(screenshotDir,`gallery-${colorset}-desktop.png`),fullPage:true});
   for(const id of semanticReviewIds){
     const card=page.locator(`[data-example-id="${id}"]`),screenshot=path.join(screenshotDir,`gallery-${id}-${colorset}.png`);
     await card.screenshot({path:screenshot});
     screenshotEvidence.push({patternId:await card.getAttribute('data-pattern-id'),fixtureId:id,viewport:'desktop',screenshot:path.relative(root,screenshot)});
   }
   await page.setViewportSize({width:390,height:844});
   galleryEvidence.push(await page.evaluate(()=>({viewport:'mobile',theme:document.body.dataset.colorSet,cards:document.querySelectorAll('.example-card').length,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(e=>!e.complete||e.naturalWidth===0).length})));
   galleryAspectEvidence.push(await auditMountedAspect(page,colorset,'mobile'));
   await page.screenshot({path:path.join(screenshotDir,`gallery-${colorset}-mobile.png`),fullPage:true});
   for(const id of semanticReviewIds){
     const card=page.locator(`[data-example-id="${id}"]`),screenshot=path.join(screenshotDir,`gallery-${id}-${colorset}-mobile.png`);
     await card.screenshot({path:screenshot});
     screenshotEvidence.push({patternId:await card.getAttribute('data-pattern-id'),fixtureId:id,viewport:'mobile',screenshot:path.relative(root,screenshot)});
   }
   await page.setViewportSize({width:1440,height:1000});
 }
 const publishedEvidence=[];
 const publishedPaintParity=[];
 if(publishedRequested){
   const publicRoot='https://gvillarroel.github.io/skills/examples/';
   const nativePage=await browser.newPage({viewport:{width:1440,height:1000}});
   for(const [colorset,dir] of Object.entries(galleries)){
     const local=path.join(skill,'assets/examples',dir),relativeRoot=`skills/plantuml-colorset-renderer/assets/examples/${dir}`;
     const metadata=JSON.parse(committedBytes(`${relativeRoot}/coverage.json`).toString('utf8'));
     const resources=['coverage.json','render-report.json',...metadata.items.map(item=>item.asset)];
     if(resources.length!==30)throw new Error(`Expected 30 committed resources for ${colorset}, found ${resources.length}`);
     const resourceEvidence=[];
     for(let offset=0;offset<resources.length;offset+=6){
       resourceEvidence.push(...await Promise.all(resources.slice(offset,offset+6).map(async resource=>{
         const url=`${publicRoot}${dir}/${resource}`;
         const canonicalPath=`${relativeRoot}/${resource}`,expected=committedBytes(canonicalPath),working=fs.readFileSync(path.join(local,resource));
         const localEqualsExpectedBytes=working.equals(expected);
         const localDiffersOnlyByCRLF=!localEqualsExpectedBytes&&/\.(svg|json)$/.test(resource)&&Buffer.from(working.toString('utf8').replace(/\r\n/g,'\n')).equals(expected);
         const binding={resource,url,canonicalPath,expectedRef,expectedBlobSha256:sha(expected),localSha256:sha(working),localEqualsExpectedBytes,localDiffersOnlyByCRLF,localBindingDiagnostic:localEqualsExpectedBytes?'Working tree bytes equal the committed Git blob':localDiffersOnlyByCRLF?'Working tree CRLF becomes LF in the committed Git blob; public SHA comparison remains exact':'Working tree differs from the committed Git blob beyond CRLF-to-LF normalization'};
         try{const response=await fetch(url,{signal:AbortSignal.timeout(15000)}),data=Buffer.from(await response.arrayBuffer());return {...binding,status:response.status,mime:response.headers.get('content-type'),sha256:sha(data),matchesExpected:data.equals(expected),matchesLocal:data.equals(working)};}catch(e){return {...binding,error:String(e)}};
       })));
     }
     const expectedNativeReports=[];
     for(const item of metadata.items.filter(item=>item.assetFormat==='svg')){
       const bytes=committedBytes(`${relativeRoot}/${item.asset}`),raw=await auditSvg(nativePage,bytes.toString('utf8'),item.id,colorset);
       raw.patternId=reports.find(r=>r.fixtureId===item.id&&r.colorset===colorset)?.patternId;
       if(!raw.patternId)throw new Error(`Committed fixture ${item.id} has no independently reviewed local pattern binding`);
       raw.sha256=sha(bytes);expectedNativeReports.push(raw);
     }
     await page.goto(`${publicRoot}plantuml-colorset-renderer/?theme=${colorset}`,{waitUntil:'domcontentloaded'});
     await page.waitForSelector('body[data-load-state="loaded"]',{timeout:45000});await page.waitForTimeout(2600);
     const state=await page.evaluate(()=>({url:location.href,theme:document.body.dataset.colorSet,report:document.querySelector('#active-render-report').href,loaded:[...document.querySelectorAll('.example-card')].map(c=>({exampleId:c.dataset.exampleId,patternId:c.dataset.patternId,source:c.dataset.source,loadState:c.querySelector('.svg-mount').dataset.loadState,svgColorset:c.querySelector('svg')?.getAttribute('data-colorset')||null})),overflow:document.documentElement.scrollWidth>innerWidth}));
     for(const raw of expectedNativeReports){const mounted=await auditSvg(page,null,raw.fixtureId,colorset,`article[data-example-id="${raw.fixtureId}"] svg`);publishedPaintParity.push(comparePaint(raw,mounted,{scope:'published',viewport:'desktop',expectedRef,expectedBlobSha256:raw.sha256}));}
     galleryAspectEvidence.push(await auditMountedAspect(page,colorset,'desktop','published'));
     await page.screenshot({path:path.join(screenshotDir,`published-${colorset}-desktop.png`),fullPage:true});
     await page.setViewportSize({width:390,height:844});
     const mobile=await page.evaluate(()=>({viewport:'mobile',theme:document.body.dataset.colorSet,cards:document.querySelectorAll('.example-card').length,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(e=>!e.complete||e.naturalWidth===0).length}));
     for(const raw of expectedNativeReports){const mounted=await auditSvg(page,null,raw.fixtureId,colorset,`article[data-example-id="${raw.fixtureId}"] svg`);publishedPaintParity.push(comparePaint(raw,mounted,{scope:'published',viewport:'mobile',expectedRef,expectedBlobSha256:raw.sha256}));}
     galleryAspectEvidence.push(await auditMountedAspect(page,colorset,'mobile','published'));
     await page.screenshot({path:path.join(screenshotDir,`published-${colorset}-mobile.png`),fullPage:true});
     await page.locator('[data-example-id="ditaa"]').screenshot({path:path.join(screenshotDir,`published-ditaa-${colorset}-mobile.png`)});
     await page.setViewportSize({width:1440,height:1000});
     publishedEvidence.push({colorset,expectedRef,resourceEvidence,state,mobile});
   }
   await nativePage.close();
 }
 const negativeSvg='<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200" viewBox="0 0 400 200"><rect id="decorative-body" x="10" y="10" width="100" height="50" fill="#9e1b32" stroke="#000000" stroke-width="2"/><text id="canvas-white" x="150" y="35" fill="white">White canvas text</text><text x="15" y="40" fill="white">Body</text><g class="link" id="bad-shaft"><path d="M10 100 L100 100" fill="none" stroke="#e7e7e7" stroke-width="2"/><polygon id="bad-head" points="100,100 90,96 90,104" fill="#e7e7e7" stroke="#e7e7e7"/></g><g class="link" id="faded-shaft"><path d="M10 130 L100 130" fill="none" stroke="#000000" stroke-opacity="0.25" stroke-width="2"/></g><line id="ungrouped-bad-track" x1="150" y1="100" x2="240" y2="100" fill="none" stroke="#cfcfcf" stroke-width="2"/><polygon id="ungrouped-bad-head" points="240,100 230,96 230,104" fill="#cfcfcf" stroke="#cfcfcf"/></svg>';
 const additionalControls='<g class="entity" id="target-body"><rect x="270" y="70" width="75" height="65" fill="#000000"/><text x="290" y="110" fill="white">Target</text></g><g class="link" id="inset-head" data-entity-2="target-body"><path d="M240 95 L280 95" fill="none" stroke="#e77204" stroke-width="2"/><polygon id="inset-head-shape" points="285,95 275,91 275,99" fill="#e77204" stroke="#e77204"/></g><g class="link" id="bad-fill-head"><path d="M150 160 L210 160" fill="none" stroke="#000000" stroke-width="2"/><polygon id="bad-fill-head-shape" points="220,160 210,156 210,164" fill="#e7e7e7" stroke="#000000"/></g><g class="link" id="hollow-symbol"><path d="M150 185 L210 185" fill="none" stroke="#000000" stroke-width="2"/><polygon id="hollow-symbol-shape" points="210,185 216,179 222,185 216,191" fill="#ffffff" stroke="#000000"/></g><rect id="solid-positive" x="120" y="65" width="90" height="30" fill="#9e1b32"/><text x="130" y="85" fill="white">Solid</text>';
 const measurementControlShapes='<line id="zero-area-fill-line" x1="300" y1="20" x2="350" y2="20" stroke="#000000"/><g class="link" id="line-fill-positive"><path d="M300 20 L350 20" fill="none" stroke="#9e1b32" stroke-width="2"/></g><g class="link" id="occluded-tail-positive"><path d="M300 50 L355 50" fill="none" stroke="#696969" stroke-width="2"/></g><rect id="occluding-later-body" x="330" y="40" width="35" height="20" fill="#9e1b32"/><rect id="boundary-body" x="330" y="145" width="35" height="35" fill="#9e1b32"/><g class="link" id="boundary-only-positive"><path d="M300 155 L330 155" fill="none" stroke="#696969" stroke-width="1.5"/></g><g class="link" id="narrow-inset-negative"><path d="M300 170 L330.02 170" fill="none" stroke="#696969" stroke-width="1.5"/></g>';
 const negatives=await auditSvg(page,negativeSvg.replace('</svg>',additionalControls+measurementControlShapes+'</svg>'),'negative-controls','colorset1');
 const negativeGates={whiteTextCanvas:negatives.texts.some(t=>t.label==='White canvas text'&&t.contrast===1&&!t.optimal),decorativeBodyOutline:negatives.bodies.some(b=>b.id==='decorative-body'&&b.outlined),lowContrastShaft:negatives.arrows.some(a=>a.id==='bad-shaft'&&a.minimumContrast<3),lowContrastHead:negatives.arrows.some(a=>a.heads.some(h=>h.id==='bad-head'&&h.minimumContrast<3)),lowContrastHeadFillWithBlackBorder:negatives.arrows.some(a=>a.heads.some(h=>h.id==='bad-fill-head-shape'&&h.minimumFillContrast<3&&h.minimumStrokeContrast>=3)),fadedShaft:negatives.arrows.some(a=>a.id==='faded-shaft'&&a.minimumContrast<3),ungroupedTrack:negatives.primitiveTraces.some(t=>t.id==='ungrouped-bad-track'&&t.minimumContrast<3),ungroupedHead:negatives.primitiveTraces.some(t=>t.id==='ungrouped-bad-head'&&t.minimumContrast<3),targetInsetHead:negatives.arrows.some(a=>a.heads.some(h=>h.id==='inset-head-shape'&&h.minimumContrast>=3&&h.targetInteriorOverlapSamples>0))};
 const positiveGates={solidBody:negatives.bodies.some(b=>b.id==='solid-positive'&&!b.outlined),solidText:negatives.texts.some(t=>t.label==='Solid'&&t.optimal),hollowSymbol:negatives.arrows.some(a=>a.heads.some(h=>h.id==='hollow-symbol-shape'&&h.hollow&&h.minimumContrast>=3))};
 const measurementGates={lineHasNoPaintedFill:negatives.arrows.some(a=>a.id==='line-fill-positive'&&a.minimumContrast>=3),laterOpaqueBodyHidesStroke:negatives.arrows.some(a=>a.id==='occluded-tail-positive'&&a.minimumContrast>=3),zeroAreaBoundaryContact:negatives.arrows.some(a=>a.id==='boundary-only-positive'&&a.minimumContrast>=3),narrowRealInsetStillFails:negatives.arrows.some(a=>a.id==='narrow-inset-negative'&&a.minimumContrast<3)};
 if(Object.values(negativeGates).some(v=>!v))throw new Error(`Independent audit missed negative controls: ${JSON.stringify(negativeGates)}`);
 if(Object.values(positiveGates).some(v=>!v))throw new Error(`Independent audit rejected positive controls: ${JSON.stringify(positiveGates)}`);
 if(Object.values(measurementGates).some(v=>!v))throw new Error(`Independent audit measurement control failed: ${JSON.stringify(measurementGates)}`);
 const findings=[];
 const galleryAspectFailures=galleryAspectEvidence.flatMap(e=>e.cards.filter(c=>!c.preservesDimensions).map(c=>({scope:e.scope,viewport:e.viewport,colorset:e.colorset,...c})));
 const galleryFailures=galleryEvidence.filter(e=>e.overflow||e.brokenImages>0||Array.isArray(e.cards)&&e.cards.some(c=>c.loadState!=='loaded'||c.svgColorset!==null&&c.svgColorset!==e.theme));
 const publicationFailures=publishedEvidence.flatMap(e=>[
   ...e.resourceEvidence.filter(r=>r.status!==200||!r.matchesExpected).map(r=>({colorset:e.colorset,kind:'public-resource-binding',expectedRef,resource:r.resource,status:r.status,expectedBlobSha256:r.expectedBlobSha256,publishedSha256:r.sha256,error:r.error})),
   ...e.resourceEvidence.filter(r=>!r.localEqualsExpectedBytes&&!r.localDiffersOnlyByCRLF).map(r=>({colorset:e.colorset,kind:'local-to-expected-binding',expectedRef,resource:r.resource,detail:r.localBindingDiagnostic})),
   ...(e.state.overflow||e.state.loaded.length!==28||e.state.loaded.some(c=>c.loadState!=='loaded'||c.svgColorset!==null&&c.svgColorset!==e.colorset)?[{colorset:e.colorset,kind:'public-desktop-gallery-binding',state:e.state}]:[]),
   ...(e.mobile.overflow||e.mobile.brokenImages>0||e.mobile.cards!==28?[{colorset:e.colorset,kind:'public-mobile-gallery-binding',state:e.mobile}]:[])
 ]);
 for(const parity of publishedPaintParity)if(!parity.matched||parity.mountedTextFailures.length||parity.mountedArrowFailures.length||parity.mountedPrimitiveFailures.length)publicationFailures.push({kind:'public-gallery-paint-parity',...parity});
 const add=(r,kind,id,detail)=>findings.push({patternId:r.patternId,fixtureId:r.fixtureId,colorset:r.colorset,kind,id,detail});
 for(const r of reports.filter(r=>r.texts)){
   if(r.canvasFill!=='rgb(255, 255, 255)')add(r,'nonwhite-canvas',r.patternId,{fill:r.canvasFill});
   for(const t of r.texts)if(t.label.replace(/[\s\uFFFD\u00A0]/g,'')&&!t.optimal)add(r,'text-not-maximum-contrast',t.id,{label:t.label,fill:t.fill,expected:t.expected,contrast:t.contrast,backings:t.backings});
   for(const b of r.bodies){
     // Timing contours and packet field boundaries encode data, not decorative node borders.
     // Containers and Gantt calendar bands are layout surfaces, not categories.
     if(['timing','packetdiag','gantt'].includes(r.fixtureId)||r.fixtureId==='usecase'&&b.tag==='rect'||r.fixtureId==='deployment'&&!b.entity)continue;
     if(b.outlined)add(r,'decorative-body-outline',b.id,{labels:b.labels,stroke:b.stroke,width:b.strokeWidth});
     if(b.fill===r.canvasFill)add(r,'category-body-matches-canvas',b.id,{labels:b.labels,fill:b.fill,canvasFill:r.canvasFill});
     if(+b.opacity<1||+b.fillOpacity<1)add(r,'nonopaque-category-body',b.id,{opacity:b.opacity,fillOpacity:b.fillOpacity});
   }
   for(const b of r.ganttTaskBodies){if(b.fill==='rgb(255, 255, 255)')add(r,'category-body-matches-canvas',b.id,{role:'task bar'});if(b.stroke!=='none'&&b.strokeWidth>0)add(r,'decorative-body-outline',b.id,{role:'task bar',stroke:b.stroke,width:b.strokeWidth});}
   for(const d of r.invisibleOpenDetails)add(r,'invisible-semantic-open-detail',d.id,d);
   for(const d of r.invisibleSmallDetails)add(r,'invisible-semantic-icon-detail',d.id,d);
   for(const a of r.arrows){if(a.minimumContrast<3-1e-6)add(r,'low-contrast-shaft',a.id,{contrast:a.minimumContrast,backings:a.backings});for(const h of a.heads){if(h.minimumContrast<3-1e-6)add(r,'low-contrast-head',h.id,{contrast:h.minimumContrast,backings:h.backings});if(h.targetInteriorOverlapSamples>0)add(r,'head-in-target-interior',h.id,{samples:h.targetInteriorOverlapSamples});}}
   for(const p of r.primitiveTraces)if(p.minimumContrast<3-1e-6)add(r,`low-contrast-${p.role}`,p.id,{contrast:p.minimumContrast,backings:p.backings,badSamples:p.badSamples.length});
   for(const f of r.packetFields)if(f.separatorContrast<3||f.strokeWidth<=0)add(r,'invisible-packet-field-boundary',f.id,{stroke:f.stroke,width:f.strokeWidth,contrast:f.separatorContrast});
   if(r.fixtureId==='archimate'&&new Set(r.bodies.map(b=>b.fill)).size<3)add(r,'premature-category-fill-reuse',r.patternId,{semanticCategories:['Technology','Application','Business'],fills:r.bodies.map(b=>b.fill)});
   if(r.fixtureId==='archimate'&&r.colorset==='colorset2')for(const b of r.bodies)if(['rgb(219, 255, 204)','rgb(205, 243, 255)','rgb(255, 244, 204)'].includes(b.fill))add(r,'pastel-before-solid-capacity',b.id,{fill:b.fill,labels:b.labels});
 }
 const summary=reports.filter(r=>r.texts).map(r=>({id:r.fixtureId,theme:r.colorset,bodies:r.bodies.length,outlinedCandidates:r.bodies.filter(b=>b.outlined).length,nonOptimal:r.texts.filter(t=>!t.optimal).map(t=>t.label),arrowBad:r.arrows.filter(a=>a.minimumContrast<3).length,headBad:r.arrows.flatMap(a=>a.heads).filter(h=>h.minimumContrast<3).length,headStrokeEnvelopeContacts:r.arrows.flatMap(a=>a.heads).filter(h=>h.targetStrokeEnvelopeContactSamples>0).map(h=>({id:h.id,samples:h.targetStrokeEnvelopeContactSamples,nativeClearance:h.nativeClearance})),ungroupedBad:r.primitiveTraces.filter(t=>t.minimumContrast<3).length,invisibleOpenDetails:r.invisibleOpenDetails.length,invisibleSmallDetails:r.invisibleSmallDetails.length,findings:findings.filter(f=>f.fixtureId===r.fixtureId&&f.colorset===r.colorset).length}));
 fs.writeFileSync(path.join(out,'reviews',`${phase}-independent-browser-paint-geometry.json`),JSON.stringify({created:new Date().toISOString(),expectedRef,method:'Browser computed paint, native geometry hit tests, opacity compositing and independent WCAG luminance; no renderer imports. Explicit fixture role classifications exclude semantic data contours and layout surfaces from decorative-border rules. Shafts/heads/ports and ungrouped connector primitives sampled at <=1px; colored group head interiors sampled on a 1px grid. Only rendered fill surfaces are backings; a .0001-unit neighborhood separates zero-area contour contact from real narrow insets, and later opaque paint occludes earlier connector samples. Hollow symbol stroke and target interior clearance checked independently. Gallery CSS paint parity measured at rest; native SVG content scales and PNG natural/display ratios checked at desktop/mobile sizes. Publication binds exact HTTP bytes to Git blobs at the required expected commit SHA; working-tree SHA and CRLF-to-LF-only differences are separate diagnostics. Committed native SVG paint signatures are compared against actual published desktop/mobile mounts in both themes. Native Ditaa PNG and desktop/mobile semantic-family card screenshots support manual raster silhouette/shadow/direction and complete-head clearance inspection.',reports,galleryEvidence,galleryPaintParity,galleryAspectEvidence,publishedEvidence,publishedPaintParity,screenshotEvidence,galleryFailures,galleryAspectFailures,publicationFailures,negativeGates,positiveGates,measurementGates,negatives,findings,summary},null,2));
 console.log(JSON.stringify({phase,expectedRef,negativeGates,positiveGates,measurementGates,findingCount:findings.length,galleryPaintMismatches:galleryPaintParity.filter(p=>!p.matched),publishedPaintMismatches:publishedPaintParity.filter(p=>!p.matched),galleryFailures,galleryAspectFailures,publicationFailures,summary},null,2));
 await browser.close();server.close();
 if(process.argv.includes('--require-clean')&&(findings.length||galleryPaintParity.some(p=>!p.matched)||galleryFailures.length||galleryAspectFailures.length||publicationFailures.length))process.exitCode=1;
})().catch(e=>{console.error(e);server.close();process.exit(1)});
