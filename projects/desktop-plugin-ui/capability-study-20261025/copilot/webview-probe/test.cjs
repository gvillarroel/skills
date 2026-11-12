// Launch only after foreground coordination. No model or account API is used.
const vscode=require('vscode');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const artifacts=path.resolve(__dirname,'../../../artifacts/capability-study-20261025/copilot');
const rows=[];const panels=[];
function panel(options={}){
  const item=vscode.window.createWebviewPanel('copilot-ui-contract-study','Copilot UI Contract Study',vscode.ViewColumn.One,options);
  panels.push(item);return item;
}
function nextMessage(item,timeout=9000){return new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>{subscription.dispose();reject(new Error('Synthetic webview message timeout'));},timeout);
  const subscription=item.webview.onDidReceiveMessage(message=>{clearTimeout(timer);subscription.dispose();resolve(message);});
});}
async function check(id,fn){try{rows.push({id,passed:true,actual:await fn()});}catch(error){rows.push({id,passed:false,error:String(error)});}}
function html(script,body='<button id="action">Increment synthetic value</button>'){
  return `<!doctype html><html lang="en"><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-study'; style-src 'unsafe-inline';"><style>body{font-family:var(--vscode-font-family);color:var(--vscode-editor-foreground);background:var(--vscode-editor-background)}button{min-height:40px}</style></head><body>${body}<script nonce="study">const api=acquireVsCodeApi();${script}</script></body></html>`;
}
exports.run=async()=>{
  try{
    await check('runtime-and-copilot-extension-inventory',async()=>({vscode:vscode.version,
      copilotExtension:vscode.extensions.getExtension('github.copilot-chat')?.packageJSON.version??null,
      layer:'real-vscode-extension-host; availability is not signed-in chat acceptance'}));
    await check('default-scripts-do-not-run',async()=>{
      const item=panel();let count=0;const subscription=item.webview.onDidReceiveMessage(()=>count++);
      item.webview.html=html("api.postMessage({ran:true});");
      await new Promise(resolve=>setTimeout(resolve,1000));subscription.dispose();
      assert.equal(count,0);item.dispose();return {received:count,enableScripts:false};
    });
    await check('enabled-script-button-and-validated-actions',async()=>{
      const item=panel({enableScripts:true,localResourceRoots:[]});let value=7;let messages=0;
      const results=[];
      const done=new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>{subscription.dispose();reject(new Error('Synthetic action timeout'));},9000);
        const subscription=item.webview.onDidReceiveMessage(message=>{
          messages++;
          if(message?.kind==='increment'&&message.delta===1){value++;results.push({accepted:true,value});}
          else results.push({accepted:false,reason:'Unsupported synthetic action'});
          if(messages===2){clearTimeout(timer);subscription.dispose();resolve();}
        });
      });
      item.webview.html=html("document.getElementById('action').onclick=()=>api.postMessage({kind:'increment',delta:1});document.getElementById('action').click();api.postMessage({kind:'execute-command',command:'not-run'});");
      await done;assert.equal(value,8);assert.equal(results[1].accepted,false);item.dispose();
      return {value,results,privilegedCommandsExecuted:0};
    });
    await check('json-state-survives-content-reload',async()=>{
      const item=panel({enableScripts:true,localResourceRoots:[]});let got=nextMessage(item);
      item.webview.html=html("api.setState({syntheticValue:7});api.postMessage({phase:'stored'});");
      await got;got=nextMessage(item);
      item.webview.html=html("api.postMessage({phase:'restored',state:api.getState()});");
      const message=await got;assert.equal(message.state.syntheticValue,7);item.dispose();return message;
    });
    await check('new-panel-does-not-inherit-disposed-panel-state',async()=>{
      const item=panel({enableScripts:true,localResourceRoots:[]});const got=nextMessage(item);
      item.webview.html=html("api.postMessage({hasState:api.getState()!==undefined});");
      const message=await got;assert.equal(message.hasState,false);item.dispose();return message;
    });
    await check('theme-language-and-document-boundary',async()=>{
      const item=panel({enableScripts:true,localResourceRoots:[]});const got=nextMessage(item);
      item.webview.html=html("let topDocument;try{window.top.document;topDocument='accessible';}catch(error){topDocument=error.name;}api.postMessage({lang:document.documentElement.lang,classes:document.body.className,editorForeground:getComputedStyle(document.body).getPropertyValue('--vscode-editor-foreground').trim(),topDocument,requireType:typeof require,processType:typeof process});");
      const message=await got;assert.equal(message.lang,'en');assert.ok(message.editorForeground);assert.equal(message.topDocument,'SecurityError');
      assert.equal(message.requireType,'undefined');assert.equal(message.processType,'undefined');item.dispose();return message;
    });
    await check('csp-refuses-unapproved-inline-script',async()=>{
      const item=panel({enableScripts:true,localResourceRoots:[]});const got=nextMessage(item);
      item.webview.html=html("window.unapproved=false;document.addEventListener('securitypolicyviolation',event=>api.postMessage({directive:event.effectiveDirective,unapproved:window.unapproved}));")+'<script>window.unapproved=true;</script>';
      const message=await got;assert.equal(message.unapproved,false);assert.match(message.directive,/^script-src/);item.dispose();return message;
    });
    await check('panel-disposal-callback',async()=>{
      const item=panel();let disposed=false;item.onDidDispose(()=>disposed=true);item.dispose();
      await new Promise(resolve=>setTimeout(resolve,150));assert.equal(disposed,true);return {disposed};
    });
  }finally{
    for(const item of panels)item.dispose();fs.mkdirSync(artifacts,{recursive:true});
    const number=fs.readdirSync(artifacts).filter(name=>/^webview-contract-\d+\.json$/.test(name)).length+1;
    const destination=path.join(artifacts,`webview-contract-${String(number).padStart(3,'0')}.json`);
    fs.writeFileSync(destination,JSON.stringify({timestampUtc:new Date().toISOString(),passed:rows.every(row=>row.passed),
      modelPrompts:0,layer:'real-vscode-extension-host',rows,
      limits:'Ordinary VS Code webview only; no Copilot chat/MCP App/canvas paint or account/permission acceptance is established.'},null,2));
  }
  if(rows.some(row=>!row.passed))throw new Error('One or more synthetic webview contract checks failed.');
};
