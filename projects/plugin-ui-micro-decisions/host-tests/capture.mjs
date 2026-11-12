// Run: node projects/plugin-ui-micro-decisions/host-tests/capture.mjs --host pi --label baseline-1
// Install the exact dependencies in this directory's package.json first.
// Captures real installed Pi/Claude Code processes through ConPTY. No shell or model prompts.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
let nativeRequire=createRequire(import.meta.url);
try{nativeRequire.resolve('node-pty');}catch{nativeRequire=createRequire(new URL('../../plugin-ui-rich-interfaces/host-tests/package.json',import.meta.url));}
const {chromium}=nativeRequire('playwright');
const {WebSocketServer}=nativeRequire('ws');
const pty=nativeRequire('node-pty');

const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,'..'),require=createRequire(import.meta.url);
const option=name=>process.argv[process.argv.indexOf(name)+1];
const host=option('--host'),label=option('--label');
if(host!=='pi'||!/^[a-z0-9-]+$/.test(label??''))throw new Error('Use --host pi --label <fresh-lowercase-id>');
const output=path.join(root,'artifacts/reviews/target-hosts',`${host}-${label}`);
await fs.mkdir(output,{recursive:false});
const working=path.join(output,'workspace');await fs.mkdir(working);
const state=path.join(output,'state');await fs.mkdir(state);
const piEntry=path.join(process.env.APPDATA,'npm/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js');
const claudeEntry=path.join(process.env.LOCALAPPDATA,'Microsoft/WinGet/Links/claude.exe');
const executable=host==='pi'?process.execPath:await fs.realpath(claudeEntry);
const args=host==='pi'?[piEntry,'--offline','--no-session','--no-context-files','--no-extensions','--no-skills','--no-prompt-templates','--no-themes','--no-mcp','--no-tools','--no-approve','-e',path.join(root,'pi/taxonomy-choice.ts')]:['--plugin-dir',path.join(root,'claude'),'--setting-sources','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--tools',''];
const environment={...process.env,TERM:'xterm-256color',COLORTERM:'truecolor',PI_CODING_AGENT_DIR:state,CLAUDE_CONFIG_DIR:state};
for(const name of Object.keys(environment))if(/API_KEY|ACCESS_TOKEN|AUTH_TOKEN|ANTHROPIC_AUTH_TOKEN/.test(name))delete environment[name];
const versionRun=spawnSync(executable,host==='pi'?[piEntry,'--version']:['--version'],{env:environment,cwd:working,encoding:'utf8',timeout:20000,windowsHide:true});
if(versionRun.status!==0)throw new Error(`Version probe failed: ${versionRun.stderr}`);
const version=versionRun.stdout.trim(),token=crypto.randomBytes(24).toString('hex');
const sourceFiles=host==='pi'?['pi/taxonomy-choice.ts']:['claude/hooks/register.ts','claude/assets/data.ts'];
const sourceDigests={};for(const file of sourceFiles)sourceDigests[file]=crypto.createHash('sha256').update(await fs.readFile(path.join(root,file))).digest('hex');
const assets={
  '/':path.join(here,'terminal.html'),
  '/xterm.js':nativeRequire.resolve('@xterm/xterm'),
  '/xterm.css':path.join(path.dirname(nativeRequire.resolve('@xterm/xterm/package.json')),'css/xterm.css')
};
const server=http.createServer(async(req,res)=>{
  const route=new URL(req.url,'http://127.0.0.1').pathname,target=assets[route];
  if(!target){res.writeHead(404);res.end();return;}
  res.setHeader('Content-Type',route.endsWith('.js')?'text/javascript':route.endsWith('.css')?'text/css':'text/html');
  res.setHeader('Cache-Control','no-store');res.end(await fs.readFile(target));
});
const sockets=new WebSocketServer({noServer:true});let child,raw='',exit,viewport={cols:80,rows:32};
const events=[],checks=[],captures=[];
const broadcast=message=>{for(const peer of sockets.clients)if(peer.readyState===1)peer.send(JSON.stringify(message));};
server.on('upgrade',(req,socket,head)=>{
  if(new URL(req.url,'http://127.0.0.1').searchParams.get('token')!==token){socket.destroy();return;}
  sockets.handleUpgrade(req,socket,head,peer=>sockets.emit('connection',peer,req));
});
sockets.on('connection',peer=>{
  if(child){peer.send(JSON.stringify({type:'output',data:raw}));return;}
  child=pty.spawn(executable,args,{name:'xterm-256color',cols:viewport.cols,rows:viewport.rows,cwd:working,env:environment,useConpty:true});
  events.push({type:'start',at:new Date().toISOString(),pid:child.pid,executable,args});
  child.onData(data=>{raw+=data;events.push({type:'output',at:Date.now(),data});broadcast({type:'output',data});});
  child.onExit(value=>{exit=value;events.push({type:'exit',...value});broadcast({type:'exit',code:value.exitCode});});
  peer.send(JSON.stringify({type:'receipt',host:host==='pi'?'Pi':'Claude Code',pid:child.pid,version,...viewport}));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser,failure;
const check=(name,passed,detail)=>{checks.push({name,passed:Boolean(passed),detail});};
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function capture(page,name){
  await pause(200);
  const text=await page.evaluate(()=>window.readScreen());
  await fs.writeFile(path.join(output,`${name}.txt`),text);
  const file=path.join(output,`${name}.png`);await page.screenshot({path:file,fullPage:true});
  captures.push({name,file,cols:viewport.cols,rows:viewport.rows,textFile:`${name}.txt`});return text;
}
async function waitScreen(page,phrase,timeout=20000){
  await page.waitForFunction(text=>window.readScreen?.().includes(text),phrase,{timeout});
}
function input(data,meaning){
  if(!child||exit)throw new Error('Terminal process is not running');
  events.push({type:'input',at:Date.now(),meaning,sha256:crypto.createHash('sha256').update(data).digest('hex')});child.write(data);
}
async function resize(page,cols,rows){
  viewport={cols,rows};events.push({type:'resize',...viewport});child.resize(cols,rows);broadcast({type:'resize',cols,rows});
  await page.setViewportSize({width:Math.max(670,Math.ceil(cols*9.7+70)),height:Math.max(650,rows*20+170)});await pause(400);
}
try{
  browser=await chromium.launch({channel:'msedge',headless:true});
  const page=await browser.newPage({viewport:{width:880,height:870},deviceScaleFactor:1});
  await page.goto(`http://127.0.0.1:${server.address().port}/?token=${token}`);
  await page.waitForFunction(()=>Boolean(window.hostReceipt));
  if(host==='pi'){
    await waitScreen(page,'pi');await pause(500);await capture(page,'startup');
    input('/taxonomy-choice\r','Open one taxonomy placement question');await waitScreen(page,'Where does Ontology');let text=await capture(page,'question-80');
    check('One question exposes two placement alternatives',text.includes('Knowledge modeling')&&text.includes('Data integration')&&text.includes('Concept definition')&&text.includes('Schema mapping'));
    const colors=await page.evaluate(()=>[...document.querySelectorAll('.xterm-rows > div')].map(row=>({text:row.textContent,spans:[...row.querySelectorAll('span')].map(s=>({text:s.textContent,color:getComputedStyle(s).color,weight:getComputedStyle(s).fontWeight}))})).filter(r=>r.text.includes('Knowledge modeling')||r.text.trim().endsWith('Ontology alignment')));
    const parent=colors.flatMap(r=>r.spans).find(s=>s.text.includes('Knowledge modeling'));const term=colors.flatMap(r=>r.spans).find(s=>s.text==='Ontology alignment');check('Selected parent and unresolved concept have distinct semantic colors',Boolean(parent&&term&&parent.color!==term.color),{parent,term});
    await resize(page,60,16);text=await capture(page,'question-60x16');check('Both alternatives and the decision keys fit 60x16',text.includes('Knowledge modeling')&&text.includes('Data integration')&&text.includes('Enter use')&&text.includes('Esc defer'));
    input('e','Inspect decision-relevant evidence');await waitScreen(page,'Relates equivalent');await capture(page,'evidence-60x16');input('\x1b','Return to the same question');await waitScreen(page,'Concept definition');input('\x1b[B','Select the alternative parent');await pause(150);text=await capture(page,'selected-b-60x16');check('Keyboard choice highlights the second option',text.includes('● B'));
    input('\r','Return the selected placement to native command context');await waitScreen(page,'Placement chosen');text=await capture(page,'returned-60x16');check('Completed native interaction returns the selected placement',/Data\s+integration/.test(text)&&text.includes('Placement chosen')&&!text.includes('Where does Ontology'));
    const successColors=await page.evaluate(()=>[...document.querySelectorAll('.xterm-rows span')].filter(s=>s.textContent.includes('Placement chosen')).map(s=>({text:s.textContent,color:getComputedStyle(s).color,weight:getComputedStyle(s).fontWeight})));check('Confirmation uses a distinct semantic success color',successColors.some(s=>s.color!==parent?.color&&s.color!==term?.color),successColors);
    input('/taxonomy-choice\r','Reopen a task-local example');await waitScreen(page,'Where does Ontology');input('\x1b','Defer without choosing a parent');await waitScreen(page,'Decision deferred');text=await capture(page,'deferred-60x16');check('Escape returns an explicit deferral',text.includes('Decision deferred'));
    input('\x04','Exit the idle host');for(let i=0;i<30&&!exit;i++)await pause(100);check('Native host exits without a model turn',exit?.exitCode===0);
  }else{
    await pause(1800);let text=await capture(page,'startup-gate');
    if(/choose the text style|choose a theme/i.test(text)){
      input('\r','Accept the already selected presentation theme in task-local state');await pause(1000);text=await capture(page,'after-theme');
    }
    const gate=/sign in|log in|login|choose the text style|choose a theme|trust this folder|trust this workspace/i.test(text);
    check('Installed Claude Code starts a visible interactive terminal',text.trim().length>40);
    check('Native pane can be reached without an unfulfilled first-run/account gate',!gate,{gate});
    if(!gate){input('/service-observatory\r','Invoke the exact registered native command');await pause(1000);await capture(page,'command-result');}
  }
}catch(error){failure=String(error);if(browser){const pages=browser.contexts().flatMap(c=>c.pages());if(pages[0])try{await capture(pages[0],'failure');}catch{}}}
finally{
  if(child&&!exit)try{child.kill();}catch{}
  await pause(150);
  await fs.writeFile(path.join(output,'terminal.ansi'),raw);
  await fs.writeFile(path.join(output,'events.json'),JSON.stringify(events,null,2));
  const report={host,version,platform:os.version(),executable,args,sourceDigests,pid:child?.pid,capturedAt:new Date().toISOString(),checks,captures,failure,exit,passed:!failure&&checks.every(c=>c.passed),scope:'Actual installed terminal process and native extension over Windows ConPTY, rendered by xterm.js. Does not establish Desktop Code, ChatGPT or a stock Windows Terminal frontend.'};
  await fs.writeFile(path.join(output,'review.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  await browser?.close();for(const peer of sockets.clients)peer.terminate();await new Promise(resolve=>sockets.close(resolve));server.closeAllConnections();await new Promise(resolve=>server.close(resolve));
  // node-pty's Windows worker can retain a handle after a normal child exit.
  // All child, browser and HTTP/WebSocket resources have been closed above.
  if(process.platform==='win32')setTimeout(()=>process.exit(report.passed?0:1),50);
  if(!report.passed)process.exitCode=1;
}
