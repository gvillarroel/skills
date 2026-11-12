// Run: pi --extension ./observatory.ts
import type {ExtensionAPI} from "@earendil-works/pi-coding-agent";
import {DATA} from "./data.ts";
const levels=" .:-=+*#%@";
export function renderDashboard(id="payments",view="dependencies",width=80,includeHints=true){
  const s=DATA.services.find(s=>s.id===id)??DATA.services[0],limit=Math.max(30,width-4);
  const wrap=(text:string)=>{const words=text.split(" "),lines:string[]=[];let line="";for(const word of words){if(line.length+word.length+1>limit){lines.push(line);line="";}line+=(line?" ":"")+word;}if(line)lines.push(line);return lines;};
  const header=["SERVICE OBSERVATORY | SYNTHETIC | READ-ONLY",`Dependencies / Metrics / Values / Table | ${s.name} [${s.status.toUpperCase()}]`,`${s.owner} | P95 ${s.p95} ms | ${s.error}% errors | ${s.rps} req/s`,""];
  if(view==="metrics"){
    const max=350,chartWidth=Math.max(20,Math.min(56,limit-15));
    header.push("P95 every 3 hours + latest (ms; UTC), scale 0..350");
    for(const point of s.history.filter(p=>p.hour%3===0||p.hour===23))header.push(`${String(point.hour).padStart(2,"0")}:00 ${"#".repeat(Math.round(point.p95/max*chartWidth)).padEnd(chartWidth)} ${point.p95}`);
    header.push("Objective: 250 ms. Bars use one shared zero-based scale.");
    header.push(`All 24 hourly values: /service-observatory ${s.id} values`);
  }else if(view==="values"){
    header.push("EXACT HOURLY P95 VALUES (ms; Nov 11, UTC)");
    for(let hour=0;hour<12;hour++)header.push([s.history[hour],s.history[hour+12]].map(p=>`${String(p.hour).padStart(2,"0")}:00 ${String(p.p95).padStart(3)} ms`).join("     "));
  }else if(view==="records"){
    header.push("SERVICE              P95 ms  ERROR %  STATE");
    for(const record of DATA.services)header.push(`${record.name.padEnd(20)} ${String(record.p95).padStart(6)} ${record.error.toFixed(2).padStart(7)}  ${record.status}`);
  }else{
    header.push("DIRECT RELATIONSHIPS (arrows show call direction)");
    for(const edge of DATA.edges.filter(e=>e.source===s.id||e.target===s.id)){
      const source=DATA.services.find(s=>s.id===edge.source)!.name,target=DATA.services.find(s=>s.id===edge.target)!.name;
      header.push(...wrap(`${source} ${edge.kind==="event"?"--event-->":"->"} ${target}: ${edge.rps} ${edge.kind==="event"?"events/s":"req/s"}`));
    }
    const spark=s.history.map(p=>levels[Math.min(9,Math.floor(p.p95/350*9))]).join("");
    header.push("",`24 h P95 trend: ${spark} | 0..350 ms`,"Exact hourly values: choose Values.");
  }
  return [...header.flatMap(wrap),...(includeHints?["","Left/Right: view | Up/Down: service | Enter/Esc: close"]:[])].flatMap(wrap);
}
export function renderDashboardPage(id="payments",view="dependencies",width=80,rows=32,page=0){
  const all=renderDashboard(id,view,width),budget=Math.max(6,rows-4);
  if(all.length<=budget)return {lines:all,page:0,pages:1};
  const service=DATA.services.find(s=>s.id===id)??DATA.services[0];
  const context=["SERVICE OBSERVATORY | SYNTHETIC",`${service.name} | ${view} | ${service.status}`];
  const body=renderDashboard(id,view,width,false),size=Math.max(1,budget-context.length-2);
  const pages=Math.ceil(body.length/size),current=Math.max(0,Math.min(page,pages-1)),start=current*size;
  return {lines:[...context,...body.slice(start,start+size),`Page ${current+1}/${pages} | rows ${start+1}-${Math.min(start+size,body.length)} of ${body.length} | N/P: page`,"Left/Right: view | Up/Down: service | Esc: close"],page:current,pages};
}
export default function(pi:ExtensionAPI){
  let selected="payments",view="dependencies";
  pi.registerCommand("service-observatory",{description:"Inspect synthetic service dependencies and metrics; [service-id] [dependencies|metrics|values|records]",handler:async(args,ctx)=>{
    const [id,requestedView]=args.trim().split(/\s+/);
    if(id){
      if(!DATA.services.some(s=>s.id===id)||requestedView&&!["dependencies","metrics","values","records"].includes(requestedView)){const message="Use /service-observatory payments metrics, or /service-observatory without arguments to choose a service.";if(ctx.hasUI)ctx.ui.notify(message,"warning");else pi.sendMessage({customType:"service-observatory",content:message,display:true},{triggerTurn:false});return;}
      selected=id;if(requestedView)view=requestedView;
    }else if(ctx.mode==="tui"){
      const {Key,matchesKey,truncateToWidth}=await import("@earendil-works/pi-tui");
      let page=0;
      await ctx.ui.custom((tui,theme,keybindings,done)=>({
        render:width=>{
          const result=renderDashboardPage(selected,view,width,tui.terminal.rows,page);page=result.page;
          return result.lines.map(line=>truncateToWidth(`  ${line}`,width));
        },
        invalidate(){},
        handleInput(input){
          if(matchesKey(input,Key.escape)||matchesKey(input,Key.enter)){done(undefined);return;}
          if(matchesKey(input,Key.pageDown)||matchesKey(input,"n"))page++;
          if(matchesKey(input,Key.pageUp)||matchesKey(input,"p"))page=Math.max(0,page-1);
          const views=["dependencies","metrics","values","records"];
          if(matchesKey(input,Key.right)||matchesKey(input,Key.left)){const direction=matchesKey(input,Key.right)?1:3;view=views[(views.indexOf(view)+direction)%4];page=0;}
          if(matchesKey(input,Key.up)||matchesKey(input,Key.down)){const direction=matchesKey(input,Key.down)?1:DATA.services.length-1;selected=DATA.services[(DATA.services.findIndex(s=>s.id===selected)+direction)%DATA.services.length].id;page=0;}
          tui.requestRender();
        }
      }));return;
    }else if(ctx.hasUI){
      const choices=DATA.services.map(s=>`${s.id} | ${s.name} | ${s.status}`);
      const choice=await ctx.ui.select(`Inspect a service (current: ${selected})`,choices);
      if(!choice)return;const candidate=choice.split(" | ")[0];
      const next=await ctx.ui.select("Choose an analysis view",["dependencies","metrics","values","records"]);
      if(!next)return;selected=candidate;view=next;
    }
    const content=renderDashboard(selected,view,80).join("\n");
    if(ctx.hasUI)ctx.ui.notify(content,"info");else pi.sendMessage({customType:"service-observatory",content,display:true},{triggerTurn:false});
  }});
}
