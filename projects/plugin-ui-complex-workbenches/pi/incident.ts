// Run: pi --offline --no-session -e ./incident.ts
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';
import {services,edges,byId,maximum,windowPoints} from '../model.mjs';
const views=['matrix','values','relations'];
export function renderPage(id='svc-037',view='matrix',width=80,rows=32,page=0){
  const selected=byId(id)??services[36],limit=Math.max(20,width-4),body:string[]=[];
  if(view==='matrix'){
    body.push('FULL DAY / 2-hour maximum P95 bins / UTC', 'Service                00  04  08  12  16  20');
    for(const s of services){let cells='';for(let h=0;h<24;h+=2){const v=maximum(s,[h,h+2]);cells+=v===null?'?':v>=350?'!':v>=250?'#':v>=150?'o':'.';cells+=' ';}body.push(`${s.name.padEnd(22)} ${cells}`);}
  }else if(view==='values'){
    body.push('EXACT P95 / 16:00-20:00 UTC / 15-minute samples');
    for(const p of windowPoints(selected,[16,20]))body.push(`${new Date(p.time).toISOString().slice(11,16)} UTC  ${p.p95===null?'Missing':`${p.p95} ms`}  ${p.error===null?'Missing':`${p.error}% errors`}`);
  }else{
    body.push('ALL DIRECT RELATIONSHIPS / arrows show calls');
    for(const e of edges.filter(e=>e.source===selected.id||e.target===selected.id))body.push(`${byId(e.source).name} -> ${byId(e.target).name}: ${e.rate} ${e.kind==='event'?'events/s':'req/s'}`);
  }
  const wrapped:string[]=[];for(const text of body){let line='';for(const word of text.split(' ')){if((line+' '+word).length>limit&&line){wrapped.push(line);line='';}line+=(line?' ':'')+word;}if(line)wrapped.push(line);}
  const budget=Math.max(8,rows-4),size=Math.max(1,budget-5),pages=Math.max(1,Math.ceil(wrapped.length/size)),current=Math.max(0,Math.min(page,pages-1));
  const context=view==='values'?'16:00-20:00 UTC | P95 ms / errors %':view==='matrix'?'2h max P95 ms UTC | .<150 o<250 #<350 !>=350':'Calls: -> direction | rates req/s or events/s';
  return {page:current,pages,lines:['INCIDENT ANALYSIS | SYNTHETIC | READ-ONLY',`${selected.name} | ${view} | 96 services / 205 edges`,context,...wrapped.slice(current*size,(current+1)*size),`Page ${current+1}/${pages} | N/P: page`, 'Left/Right: view | Up/Down: service | Esc: close']};
}
export default function(pi:ExtensionAPI){
 let selected='svc-037',view='matrix';
 pi.registerCommand('incident-analysis',{description:'Inspect a 96-service matrix, quarter-hour values or directed relationships. [service-id] [matrix|values|relations]',handler:async(args,ctx)=>{
  const [id,requested]=args.trim().split(/\s+/);
  if(id){if(!byId(id)||requested&&!views.includes(requested)){const text='Use /incident-analysis svc-037 values or /incident-analysis without arguments.';if(ctx.hasUI)ctx.ui.notify(text,'warning');else pi.sendMessage({customType:'incident-analysis',content:text,display:true},{triggerTurn:false});return;}selected=id;if(requested)view=requested;}
  if(!id&&ctx.mode==='tui'){
   const {Key,matchesKey,truncateToWidth}=await import('@earendil-works/pi-tui');let page=0;
   await ctx.ui.custom((tui,theme,keys,done)=>({render:width=>{const next=renderPage(selected,view,width,tui.terminal.rows,page);page=next.page;return next.lines.map(s=>truncateToWidth('  '+s,width));},invalidate(){},handleInput(input){if(matchesKey(input,Key.escape)||matchesKey(input,Key.enter)){done(undefined);return;}if(matchesKey(input,'n'))page++;if(matchesKey(input,'p'))page=Math.max(0,page-1);if(matchesKey(input,Key.right)||matchesKey(input,Key.left)){view=views[(views.indexOf(view)+(matchesKey(input,Key.right)?1:views.length-1))%views.length];page=0;}if(matchesKey(input,Key.down)||matchesKey(input,Key.up)){selected=services[(services.findIndex(s=>s.id===selected)+(matchesKey(input,Key.down)?1:95))%96].id;page=0;}tui.requestRender();}}));return;
  }
  if(!id&&ctx.hasUI){const chosen=await ctx.ui.select('Inspect a service',services.map(s=>`${s.id} | ${s.name}`));if(!chosen)return;const next=await ctx.ui.select('Analysis view',views);if(!next)return;selected=chosen.split(' | ')[0];view=next;}
  const first=renderPage(selected,view,100,200,0);const content=first.lines.join('\n');if(ctx.hasUI)ctx.ui.notify(content,'info');else pi.sendMessage({customType:'incident-analysis',content,display:true},{triggerTurn:false});
 }});
}
