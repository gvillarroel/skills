#!/usr/bin/env -S node --experimental-strip-types
// Run: node evaluations/contracts/validate-hyperframes-assets.ts <run-dir> [dependency-project].
// Requires Puppeteer Core from the generated project or an explicit evaluator dependency project.
import path from 'node:path';
import {readFileSync, writeFileSync, existsSync, mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import http from 'node:http';
const run = path.resolve(process.argv[2]);
const workspace = path.join(run,'workspace'), out = path.join(workspace,'deliverables');
const project = path.join(out,'project');
const dependencyProject = path.resolve(process.argv[3] || project);
const vehicle = process.argv[4] === 'vehicle';
const reference = process.argv[4] === 'reference';
const duration = reference ? 16 : 8, fps = reference ? 30 : 12;
const width = reference ? 1920 : 960, height = reference ? 1080 : 540;
const sourceUnit = vehicle ? 'm/s' : 'L/s', quantityUnit = vehicle ? 'm' : 'L';
const target = vehicle ? 4 : 5, maximum = vehicle ? 6 : 5;
const finalValue = reference ? 45 : vehicle ? 26 : 31;
const require = createRequire(path.join(dependencyProject,'package.json'));
const puppeteer = require('puppeteer-core');
const brief = JSON.parse(readFileSync(path.join(project,'brief.json'),'utf8'));
const manifest = JSON.parse(readFileSync(path.join(project,'manifest.json'),'utf8'));
const findings = [], observations = [];
const fail = message => findings.push(message);
const close = (actual, expected, message) => {if(!Number.isFinite(actual)||Math.abs(actual-expected)>1e-7) fail(`${message}: ${actual} != ${expected}`);};
const source = Object.entries(brief.sources).find(([,s]:any)=>s.unit===sourceUnit)?.[0];
const quantity = Object.entries(brief.derived).find(([,s]:any)=>s.unit===quantityUnit)?.[0];
if(!source || !quantity) fail('Missing inlet-rate or stored-volume quantity with the required units.');
if(brief.palette.mode!==(vehicle?'colorset2':'colorset1')) fail('Wrong palette.');
if(!manifest.assets?.length) fail('No imported asset provenance.');
for(const asset of manifest.assets || []) {
  const file=path.join(project,asset.projectSource || 'missing');
  if(!existsSync(file)||createHash('sha256').update(readFileSync(file)).digest('hex')!==asset.sha256) fail('Retained SVG source differs from its provenance hash.');
  if(!asset.purpose||!asset.producer||!asset.moments?.length) fail('Incomplete asset intent/provenance.');
}
const server=http.createServer((request,response)=>{
  const name=decodeURIComponent(new URL(request.url!,'http://localhost').pathname).slice(1)||'index.html';
  const file=path.resolve(project,name);
  if(!file.startsWith(project+path.sep)||!existsSync(file)){response.writeHead(404).end();return;}
  const mime={'.html':'text/html','.js':'text/javascript','.ttf':'font/ttf','.json':'application/json'};
  response.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');response.end(readFileSync(file));
});
await new Promise<void>(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser;
try {
  const executablePath=['C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','/usr/bin/chromium'].find(p=>existsSync(p));
  browser=await puppeteer.launch({executablePath,headless:true,userDataDir:path.join(run,'evaluator-browser'),args:['--no-sandbox']});
  const page=await browser.newPage(); await page.setViewport({width,height});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const origin=`http://127.0.0.1:${(server.address() as any).port}`;
  await page.goto(origin+'/index.html',{waitUntil:'networkidle0'});
  // Independent analytic oracle for the declared piecewise speed/rate ramp.
  const volumeAt=t=>reference ? (t<=4?2*t:t<=6?8+2*(t-4)+3*(t-4)**2/4:t<=10?15+5*(t-6):t<=12?35+5*(t-10)-(t-10)**2:41+(t-12)) : (t<=2?2*t:t<=4?4+2*(t-2)+(target-2)*(t-2)**2/4:4+(2+target)+target*(t-4));
  const rateAt=t=>reference ? (t<=4?2:t<=6?2+3*(t-4)/2:t<=10?5:t<=12?5-2*(t-10):1) : (t<=2?2:t<=4?2+(target-2)*(t-2)/2:target);
  for(const t of reference ? [0,4,5,6,10,11,12,16,4,0,16] : [0,2,3,4,8,3,0,8]) {
    const frame=await page.evaluate(t=>window.explainer.seek(t),t);
    if(source) close(frame.state[source],rateAt(t),`Rate at ${t}`);
    if(quantity) close(frame.state[quantity],volumeAt(t),`Accumulation at ${t}`);
    observations.push({time:t,state:frame.state});
  }
  const importedIds=(manifest.assets||[]).flatMap(a=>a.markIds||[]);
  const input=await page.evaluate(({source,quantity,importedIds,maximum,duration})=>{
    const api=window.explainer;
    api.clearInputs();api.seek(4);
    const nodes=[...document.querySelectorAll('[data-mark]')];
    const geometry=n=>JSON.stringify(['x','y','x1','y1','x2','y2','cx','cy','width','height','r','rx','ry','d','transform'].map(k=>n.getAttribute(k)));
    const before=new Map(nodes.map(n=>[n.dataset.mark,geometry(n)]));
    const zero=api.setInputs({[source]:0});
    const changed=nodes.filter(n=>geometry(n)!==before.get(n.dataset.mark)).map(n=>({id:n.dataset.mark,view:n.dataset.view,kind:n.tagName}));
    const z8=api.seek(duration);
    api.setInputs({[source]:maximum});const m8=api.seek(duration);
    const allImported=importedIds.every(id=>document.querySelector(`[data-mark="${id}"]`));
    const state={zero:zero.state[quantity],zeroEnd:z8.state[quantity],maxEnd:m8.state[quantity]};
    api.clearInputs();api.seek(duration);
    return {state,changed,allImported};
  },{source,quantity,importedIds,maximum,duration});
  close(input.state.zero,0,'Zero-input quantity at t=4');close(input.state.zeroEnd,0,'Zero-input final quantity');close(input.state.maxEnd,maximum*duration,'Maximum-input final counterfactual');
  if(new Set(input.changed.map(m=>m.view)).size<2) fail('A real input did not change geometry in two views.');
  if(!input.changed.some(m=>importedIds.includes(m.id))) fail('Imported art has no driven visible geometry.');
  if(!input.allImported) fail('Imported geometry is missing from the live DOM.');
  observations.push({input});
  if(!vehicle) {
    // Inspect actual consecutive DOM positions. Correct rate integration can
    // still make equally spaced markers appear to reverse at the delivery fps.
    const transport = await page.evaluate(({source,maximum,fps})=>{
      const api=window.explainer;api.clearInputs();api.setInputs({[source]:maximum});api.seek(4);
      const nodes=[...document.querySelectorAll('[data-mark]')].filter(n=>/-tracer-\d+$/.test(n.dataset.mark));
      const before=new Map(nodes.map(n=>[n.dataset.mark,Number(n.getAttribute('cx'))]));
      const positions=[...before.values()].sort((a,b)=>a-b);
      const median=values=>values.sort((a,b)=>a-b)[Math.floor(values.length/2)];
      const spacing=median(positions.slice(1).map((v,i)=>v-positions[i]));
      api.seek(4+1/fps);
      const steps=nodes.map(n=>Number(n.getAttribute('cx'))-before.get(n.dataset.mark)).filter(d=>d>=0);
      const step=median(steps);api.clearInputs();
      return {count:nodes.length,spacing,logicalStep:step,maximumUnambiguousStep:spacing/2};
    },{source,maximum,fps});
    if(transport.count>1 && (!Number.isFinite(transport.logicalStep)||transport.logicalStep<=0||transport.logicalStep>transport.maximumUnambiguousStep+1e-7)) fail('Repeated transport markers alias or lose direction at the requested frame rate.');
    observations.push({transportSampling:transport});
  }
  await page.goto(origin+'/preview.html',{waitUntil:'networkidle0'});
  const controls=await page.evaluate(({source,quantity,duration})=>{
    const control=document.querySelector(`[data-source="${source}"]`), api=document.getElementById('film').contentWindow.explainer;
    control.value='0';control.dispatchEvent(new Event('input',{bubbles:true}));
    const zero=api.seek(duration).state[quantity];document.getElementById('reset').click();const restored=api.seek(duration).state[quantity];
    return {zero,restored};
  },{source,quantity,duration});
  close(controls.zero,0,'Actual preview input');close(controls.restored,finalValue,'Actual preview reset');
  await page.goto(origin+'/index.html',{waitUntil:'networkidle0'});await page.evaluate(t=>window.explainer.seek(t),duration);
  await page.screenshot({path:path.join(run,'independent-final.png')});
  findings.push(...errors);
  const movie=path.join(out,'explanation.mp4');
  const info=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-of','json',movie],{encoding:'utf8'}));
  const video=info.streams.find(s=>s.codec_type==='video');
  if(video.width!==width||video.height!==height||Number(video.nb_read_frames)!==duration*fps||video.avg_frame_rate!==`${fps}/1`||video.codec_name!=='h264'||video.pix_fmt!=='yuv420p') fail('Actual movie fails its requested media contract.');
  execFileSync('ffmpeg',['-v','error','-i',movie,'-f','null','-'],{stdio:'pipe'});
  const report={ok:!findings.length,case:reference?'sol-quality':vehicle?'vehicle-assets':'asset-direction',findings,observations,media:{width:video.width,height:video.height,frames:video.nb_read_frames,fps:video.avg_frame_rate},manualReviewRequired:true};
  writeFileSync(path.join(run,'independent.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({ok:report.ok,findings:findings.length,run}));
  if(findings.length) process.exitCode=1;
} catch(error) {
  writeFileSync(path.join(run,'independent.json'),JSON.stringify({ok:false,findings:[String(error)]},null,2)+'\n');
  console.error(String(error));process.exitCode=2;
} finally {if(browser)await browser.close();await new Promise<void>(resolve=>server.close(()=>resolve()));}
