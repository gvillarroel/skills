import { App } from '@modelcontextprotocol/ext-apps';

const app = new App({name:'Desktop UI probe',version:'1.0.0'}, {}, {strict:true});
const byId = (id:string) => document.getElementById(id)!;
let savedValue = 0;
app.ontoolresult = result => {
  if (!result.isError) {
    savedValue = Number((result.structuredContent as {value:number}).value);
    byId('value').textContent = String(savedValue);
  }
};
app.onhostcontextchanged = context => {
  if (context.theme) document.documentElement.dataset.theme = context.theme;
};
const readiness = app.connect();
const run = async (operation:string) => {
  await readiness;
  if (operation === 'update') {
    const result = await app.callServerTool({name:'increment', arguments:{value:savedValue}});
    if (result.isError) {byId('error').textContent='Tool rejected'; return 'rejected';}
    savedValue = Number((result.structuredContent as {value:number}).value);
    byId('value').textContent=String(savedValue); return savedValue;
  }
  if (operation === 'context') return app.updateModelContext({content:[{type:'text',text:'Selected row: seven'}]});
  if (operation === 'message') return app.sendMessage({role:'user',content:[{type:'text',text:'Explain selected row seven'}]});
  if (operation === 'fullscreen') return app.requestDisplayMode({mode:'fullscreen'});
  if (operation === 'pip') return app.requestDisplayMode({mode:'pip'});
  if (operation === 'link') return app.openLink({url:'https://example.com/review'});
  if (operation === 'download') return app.downloadFile({contents:[{type:'resource_link',uri:'https://example.com/result.csv',name:'result.csv',mimeType:'text/csv'}]});
  if (operation === 'unknown-tool') return app.callServerTool({name:'unregistered',arguments:{}});
  if (operation === 'parent-dom') {
    try {return window.parent.document.body.textContent;} catch(error) {return (error as Error).name;}
  }
  if (operation === 'file-write') {
    try {(byId('upload') as HTMLInputElement).value='C:/private/file.txt'; return 'unexpected';}
    catch(error) {return (error as Error).name;}
  }
  if (operation === 'fetch') {
    try {await fetch('https://example.com/blocked');return 'unexpected';}catch{return 'blocked';}
  }
  return app.getHostCapabilities();
};
(window as any).probeRun = run;
byId('increment').onclick = () => {void run('update');};
byId('details').onclick = () => {byId('options').hidden=!byId('options').hidden;};
readiness.then(()=>{byId('ready').textContent='ready';}).catch(error=>{
  byId('error').textContent='Unable to connect to the host. Please retry.';
  console.error('Host connection failed',error);
});
