#!/usr/bin/env -S node --experimental-strip-types
// Node.js >=24; requires puppeteer-core from the project or an explicit evaluator runtime.
// node evaluations/contracts/validate-hyperframes-explainer-case.ts <case> <workspace> <report> [dependency-project]
// Evaluator-owned numerical expectations, independent of the skill's expression engine.
import path from 'node:path';
import {existsSync, readFileSync, writeFileSync, mkdirSync} from 'node:fs';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
const [caseName, workArg, reportArg, dependencyArg] = process.argv.slice(2);
const work = path.resolve(workArg), project = path.join(work, 'out/project');
const reportPath = path.resolve(reportArg);
const findings = [], observations = [];
const isContract=caseName==='contract';
let browser;
try {
  const brief = JSON.parse(readFileSync(path.join(project, 'brief.json'), 'utf8'));
  const requiredPalette = caseName === 'generalization' ? 'colorset2' : 'colorset1';
  if (brief.palette.mode !== requiredPalette) findings.push('Wrong requested palette.');
  const specification=isContract ? {duration:16,width:1920,height:1080,fps:30} : {duration:8,width:960,height:540,fps:12};
  if (Object.entries(specification).some(([key,value])=>brief.output[key]!==value))
    findings.push('Brief changed the exact movie specification.');
  if (isContract) {
    for (const name of ['preflight','build']) if (!JSON.parse(readFileSync(path.join(work,`out/${name}.json`),'utf8')).ok)
      findings.push(`Contract ${name} report failed.`);
    const supplied=JSON.parse(readFileSync(path.join(work,'skills/hyperframes-explainer/assets/templates/brief.json'),'utf8'));
    if (JSON.stringify(supplied)!==JSON.stringify(brief)) findings.push('The contract changed supplied brief semantics.');
    for (const name of ['index.html','preview.html','manifest.json','assets/vendor/gsap.min.js','assets/fonts/space-grotesk.ttf'])
      if (!existsSync(path.join(project,name))) findings.push(`Missing working preview asset: ${name}`);
  } else {
  const probe = spawnSync('ffprobe', ['-v', 'error', '-count_frames', '-show_streams', '-of', 'json', path.join(work,'out/video.mp4')], {encoding:'utf8'});
  if (probe.status !== 0) throw Error('Independent ffprobe failed.');
  const info = JSON.parse(probe.stdout), video = info.streams.find(s=>s.codec_type==='video');
  if (video.width!==960 || video.height!==540 || video.nb_read_frames!=='96' || video.avg_frame_rate!=='12/1' || video.codec_name!=='h264' || video.pix_fmt!=='yuv420p')
    findings.push('Independent media specification check failed.');
  const decoded=spawnSync('ffmpeg',['-v','error','-i',path.join(work,'out/video.mp4'),'-f','null','-'],{encoding:'utf8'});
  if (decoded.status || decoded.stderr.trim()) findings.push('Independent full decode failed.');
  }
  const dependencyProject=dependencyArg ? path.resolve(dependencyArg) : project;
  const requireProject = createRequire(path.join(dependencyProject,'package.json'));
  const puppeteer=requireProject('puppeteer-core');
  const executablePath=[process.env.HYPERFRAMES_BROWSER_PATH,'C:/Program Files/Google/Chrome/Application/chrome.exe',
    '/usr/bin/google-chrome','/usr/bin/chromium'].filter(Boolean).find(p=>existsSync(p!));
  const profile=path.join(path.dirname(reportPath),'.cache/independent-browser'); mkdirSync(profile,{recursive:true});
  browser=await puppeteer.launch({executablePath,headless:true,userDataDir:profile,args:['--no-sandbox']});
  const page=await browser.newPage(); await page.setViewport({width:specification.width,height:specification.height});
  await page.goto(pathToFileURL(path.join(project,'index.html')).href,{waitUntil:'load'});
  const times=isContract ? [0,4,5,6,10,11,12,16,6,0] : caseName==='naturalistic' ? [0,2,3.5,5,8,3.5,0] : [0,2,3,4,8,3,0];
  const signatures=new Map();
  for (const time of times) {
    const actual=await page.evaluate(async t=>{
      await document.fonts.ready; const api=window.explainer; api.clearInputs(); api.seek(t);
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      const numericLabels=api.brief.marks.filter(m=>m.kind==='text' && Object.hasOwn(m,'value')).map(m=>{
        const element=document.querySelector(`[data-mark="${m.id}"]`);
        let label=m.text || '', labelSource='combined';
        if (!label) {
          const bounds=element.getBoundingClientRect(), x=bounds.x+bounds.width/2, y=bounds.y+bounds.height/2;
          const neighbors=api.brief.marks.filter(n=>n.kind==='text' && n.view===m.view && !Object.hasOwn(n,'value')).map(n=>{
            const node=document.querySelector(`[data-mark="${n.id}"]`), box=node.getBoundingClientRect();
            return {label:node.textContent.trim(),distance:Math.hypot(box.x+box.width/2-x,box.y+box.height/2-y)};
          }).filter(n=>/^[AB]$/.test(n.label)).sort((a,b)=>a.distance-b.distance);
          if (neighbors[0]?.distance<=api.brief.output.height*.2 && (!neighbors[1] || neighbors[1].distance-neighbors[0].distance>10)) {
            label=neighbors[0].label; labelSource='adjacent-static';
          }
        }
        return {id:m.id,label,labelSource,unit:m.unit,text:element.textContent};
      });
      return {labels:numericLabels,
        signature:document.getElementById('stage').outerHTML,
        geometry:api.brief.marks.filter(m=>m.kind!=='text').map(m=>({id:m.id,view:m.view,kind:m.kind,
          html:document.querySelector(`[data-mark="${m.id}"]`).outerHTML}))};
    },time);
    const numeric=text=>Number(text.match(/[-+]?\d+(?:\.\d+)?/g)?.at(-1));
    const values=actual.labels.map(v=>({...v,value:numeric(v.text)}));
    let expected;
    if (isContract) {
      const rate=time<=4 ? 2 : time<=6 ? time-2 : time<=10 ? 4 : time<=12 ? 4-1.5*(time-10) : 1;
      const volume=time<=4 ? 2*time : time<=6 ? 8+2*(time-4)+(time-4)**2/2 : time<=10 ? 14+4*(time-6) : time<=12 ? 30+4*(time-10)-.75*(time-10)**2 : 35+(time-12);
      expected={rate,volume};
      const rates=values.filter(v=>v.unit==='L/s'), volumes=values.filter(v=>v.unit==='L');
      if (!rates.length || !volumes.length || rates.some(v=>Math.abs(v.value-rate)>.11) || volumes.some(v=>Math.abs(v.value-volume)>.11))
        findings.push(`Independent contract rate/volume values differ at ${time} s.`);
    } else if (caseName==='naturalistic') {
      const a=time<=2 ? 32 : time>=5 ? 12 : 32-(time-2)*20/3;
      expected={a,b:40-a};
      const aLabels=values.filter(v=>/\bA\b/i.test(v.label) && !/\bB\b/i.test(v.label));
      const bLabels=values.filter(v=>/\bB\b/i.test(v.label) && !/\bA\b/i.test(v.label));
      if (!aLabels.length || !bLabels.length || aLabels.some(v=>Math.abs(v.value-a)>.11) || bLabels.some(v=>Math.abs(v.value-(40-a))>.11))
        findings.push(`Independent A/B values differ at ${time} s.`);
      if (aLabels.length && bLabels.length && Math.abs(aLabels[0].value+bLabels[0].value-40)>.11) findings.push('Visible total is not conserved.');
    } else {
      const speed=time<=2 ? 2 : time>=4 ? 6 : 2+2*(time-2);
      const distance=time<=2 ? 2*time : time<=4 ? 4+2*(time-2)+(time-2)**2 : 12+6*(time-4);
      expected={speed,distance};
      const speeds=values.filter(v=>v.unit==='m/s'), distances=values.filter(v=>v.unit==='m');
      if (!speeds.length || !distances.length || speeds.some(v=>Math.abs(v.value-speed)>.11) || distances.some(v=>Math.abs(v.value-distance)>.11))
        findings.push(`Independent speed/distance values differ at ${time} s.`);
    }
    if (signatures.has(time) && signatures.get(time)!==actual.signature) findings.push(`Reverse seek is not reproducible at ${time} s.`);
    signatures.set(time,actual.signature);
    observations.push({time,expected,actual:values,geometry:actual.geometry});
  }
  const start=observations.find(s=>s.time===(isContract?4:2)), end=observations.find(s=>s.time===(isContract?6:caseName==='naturalistic'?5:4));
  const changed=end.geometry.filter(m=>start.geometry.find(n=>n.id===m.id)?.html!==m.html);
  if (changed.length<2 || new Set(changed.map(m=>m.view)).size<2) findings.push('The initiating event does not change two visible geometric representations.');
  const screenshot=path.join(path.dirname(reportPath),`${caseName}-independent.png`); mkdirSync(path.dirname(screenshot),{recursive:true});
  await page.evaluate(()=>window.explainer.seek(4)); await page.screenshot({path:screenshot});
  observations.forEach(s=>delete s.geometry);
  mkdirSync(path.dirname(reportPath),{recursive:true});
  writeFileSync(reportPath,JSON.stringify({ok:!findings.length,case:caseName,findings,observations,changedGeometry:changed.map(m=>m.id),screenshot,dependencyProject},null,2));
  console.log(JSON.stringify({ok:!findings.length,case:caseName,findings,report:reportPath}));
  if (findings.length) process.exitCode=1;
} catch(error) {
  mkdirSync(path.dirname(reportPath),{recursive:true}); writeFileSync(reportPath,JSON.stringify({ok:false,findings:[String(error)]},null,2));
  console.error(String(error)); process.exitCode=2;
} finally {if(browser) await browser.close();}
