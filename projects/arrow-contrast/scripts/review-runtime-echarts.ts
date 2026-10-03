// Run: node --experimental-strip-types projects/arrow-contrast/scripts/review-runtime-echarts.ts --echarts-run <id> --slidev-run <id>
// Uses Vite/Vue/ECharts and Playwright installed in the owning acceptance fixtures.
// Reads accepted Pi artifacts without modifying their sealed workspace bytes.
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {measureNativeArrows} from './native-arrow-probe.ts';
const root=new URL('../../../',import.meta.url);
const require=createRequire(new URL('skills/slidev-echarts/assets/examples/slidev-echarts/package.json',root));
const {chromium}=require('playwright');
const {build}=await import(pathToFileURL(require.resolve('vite')).href);
const {default:vue}=await import(pathToFileURL(require.resolve('@vitejs/plugin-vue')).href);
const {viteSingleFile}=require('vite-plugin-singlefile');
const echartsRun=process.argv[process.argv.indexOf('--echarts-run')+1];
const componentOnly=process.argv.includes('--component-only');
if(!componentOnly&&!/^20261003-arrow-echarts-animated-svg-final-\d+$/.test(echartsRun))throw Error('Pass exact accepted ECharts run ID');
const slidevRun=process.argv.includes('--slidev-run')?process.argv[process.argv.indexOf('--slidev-run')+1]:null;
if(!/^20261003-arrow-slidev-echarts-final-\d+$/.test(slidevRun))throw Error('Pass exact accepted Slidev run ID');
for(const id of (componentOnly?[slidevRun]:[echartsRun,slidevRun]))if(!JSON.parse(readFileSync(new URL(`evaluations/runs/${id}/evaluation-result.json`,root),'utf8')).passed)throw Error('Run failed strict gates: '+id);
const art=new URL('projects/arrow-contrast/artifacts/runtime-echarts/',root);mkdirSync(art,{recursive:true});
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:640,height:360}}),errors=[];
page.on('pageerror',error=>errors.push(error.message));
const states=[];
for(const family of (componentOnly?[]:['graph','routes']))for(const palette of ['cs1','cs2'])for(const mode of ['static','animated-final','animated-reduce']){
  await page.emulateMedia({reducedMotion:mode==='animated-reduce'?'reduce':'no-preference'});
  const extension=mode==='static'?'static':'animated';
  const source=new URL(`evaluations/runs/${echartsRun}/workspace/${family}-${palette}.${extension}.svg`,root);
  await page.goto(source.href);
  if(mode==='animated-final')await page.evaluate(()=>{for(const a of document.getAnimations())a.finish();});
  const result=await page.locator('svg').evaluate(measureNativeArrows,family),expected=family==='graph'?1:3;
  const id=`${family}-${palette}-${mode}`;await page.screenshot({path:fileURLToPath(new URL(id+'.png',art))});
  states.push({id,runId:echartsRun,...result,passed:result.shaftCount===expected&&result.headCount===expected&&result.records.every(r=>r.minimumContrast>=3&&r.points.length&&r.points.every(p=>!p.covered.length))});
}
// Build an external harness around the exact generated component. The skill
// copy and accepted component remain read-only; Vite writes only to artifacts.
const app=new URL('component-app/',art);mkdirSync(app,{recursive:true});
const component=fileURLToPath(new URL(`evaluations/runs/${slidevRun}/workspace/ArrowRoutes.vue`,root)).replaceAll('\\','/');
writeFileSync(new URL('index.html',app),'<!doctype html><html><body><div id="app"></div><script type="module" src="./main.js"></script></body></html>');
writeFileSync(new URL('main.js',app),`import {createApp,ref,h} from 'vue';import ArrowRoutes from ${JSON.stringify(component)};createApp({setup(){const step=ref(0);window.setArrowStep=v=>step.value=v;return()=>h(ArrowRoutes,{step:step.value});}}).mount('#app');`);
const nodeModules=new URL('skills/slidev-echarts/assets/examples/slidev-echarts/node_modules/',root);
await build({configFile:false,root:fileURLToPath(app),base:'./',plugins:[vue(),viteSingleFile()],resolve:{alias:{vue:fileURLToPath(new URL('vue',nodeModules)),echarts:fileURLToPath(new URL('echarts',nodeModules))}},build:{outDir:fileURLToPath(new URL('built/',app)),emptyOutDir:false}});
for(const motion of ['no-preference','reduce'])for(const width of [640,1000])for(const step of [0,1]){
  await page.setViewportSize({width,height:400});await page.emulateMedia({reducedMotion:motion});
  await page.goto(new URL('built/index.html',app).href);await page.locator('svg').waitFor();
  await page.evaluate(value=>window.setArrowStep(value),step);await page.waitForTimeout(200);
  const result=await page.locator('svg').evaluate(measureNativeArrows,'routes'),id=`component-${motion}-${width}-${step}`;
  await page.screenshot({path:fileURLToPath(new URL(id+'.png',art))});
  states.push({id,runId:slidevRun,...result,passed:result.shaftCount===3&&result.headCount===3&&result.records.every(r=>r.minimumContrast>=3&&r.points.length&&r.points.every(p=>!p.covered.length))});
}
await browser.close();
const report={date:'2026-10-03',passed:errors.length===0&&states.every(s=>s.passed),errors,states,scope:'Independent actual browser inspection of exact accepted Pi artifacts: four native charts, static/reduced/final animation, and generated Vue component compiled and rendered at two widths, click steps and motion preferences. Local samples exclude antialias edge blends. Finishing an animation samples its readable final state; it does not certify every reveal frame.'};
writeFileSync(new URL(`evaluations/arrow-contrast/${componentOnly?'slidev-runtime-component':'echarts-runtime-artifacts'}-20261003.json`,root),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,states:states.length,errors,failures:states.filter(s=>!s.passed)},null,2));
if(!report.passed)process.exitCode=1;
