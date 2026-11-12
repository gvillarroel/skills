import {App} from '@modelcontextprotocol/ext-apps';
const app=new App({name:'Assistant UI Limits Probe',version:'1.0.0'}, {}, {strict:true});
const out=(id:string,value:unknown)=>{document.getElementById(id)!.textContent=typeof value==='string'?value:JSON.stringify(value,null,2);};
let value=0;
const log=(action:string,result:unknown)=>{out('result',{action,result});};
app.ontoolresult=result=>{if(result.structuredContent){value=Number((result.structuredContent as any).value??0);out('value',value);}};
app.onhostcontextchanged=context=>{out('context',app.getHostContext());if(context.theme)document.documentElement.dataset.theme=context.theme;};
async function action(kind:string){
  try {
    if(kind==='increment'||kind==='invalid'){
      const result=await app.callServerTool({name:'ui_probe_increment',arguments:{value:kind==='invalid'?-1:value}});
      if(!result.isError){value=Number((result.structuredContent as any).value);out('value',value);log(kind,result);}
      else {console.error('Probe input was rejected',result);log(kind,{error:'The input was rejected. Check the value and try again.',valuePreserved:value});}
    } else if(kind==='fullscreen'||kind==='pip')log(kind,await app.requestDisplayMode({mode:kind}));
    else if(kind==='context')log(kind,await app.updateModelContext({content:[{type:'text',text:'Synthetic probe selection: record 7. No reply requested.'}]}));
    else if(kind==='link')log(kind,await app.openLink({url:'https://example.com/'}));
    else if(kind==='download')log(kind,await app.downloadFile({contents:[{type:'resource',resource:{uri:'ui-probe://result.txt',mimeType:'text/plain',text:'Synthetic UI probe download.\n'}}]}));
    else if(kind==='sandbox'){
      let parentDom='';try{parentDom=window.parent.document.title;}catch(error){parentDom=(error as Error).name;}
      log(kind,{parentDom,openaiBridge:typeof (window as any).openai,secureContext:window.isSecureContext,localValue:value});
    }
  }catch(error){console.error('UI probe action failed',error);log(kind,{error:'The requested action failed. Please retry.',valuePreserved:value});}
}
for(const button of document.querySelectorAll<HTMLButtonElement>('button[data-action]'))button.onclick=()=>void action(button.dataset.action!);
await app.connect();
out('ready','Connected to actual host');out('caps',app.getHostCapabilities());out('context',app.getHostContext());
const modes=app.getHostContext()?.availableDisplayModes??[];
for(const mode of ['fullscreen','pip']){const button=document.querySelector<HTMLButtonElement>(`[data-action="${mode}"]`)!;button.disabled=!modes.includes(mode as any);}
document.querySelector<HTMLButtonElement>('[data-action="download"]')!.disabled=!app.getHostCapabilities()?.downloadFile;
document.querySelector<HTMLButtonElement>('[data-action="link"]')!.disabled=!app.getHostCapabilities()?.openLinks;
