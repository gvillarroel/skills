// Run with: pi --extension ./inspect-flow.ts
import type {ExtensionAPI} from "@earendil-works/pi-coding-agent";
// Adapt the small domain model; preserve the mode, cancellation and output flow.
const DATA={
  nodes:[{id:"ingest",state:"healthy"},{id:"enrich",state:"degraded"},{id:"store",state:"healthy"}],
  edges:[{source:"ingest",target:"enrich",rate:110},{source:"enrich",target:"store",rate:110}],
  metrics:{enrich:{hours:[0,4,8,12,16,20],latency:[90,100,95,130,160,180],objective:150}}
};
function describe(node:string,view:string){
  const record=DATA.nodes.find(n=>n.id===node)!;
  if(view==="metrics"){
    const metric=DATA.metrics[node as keyof typeof DATA.metrics];
    if(!metric)return `${node}: no latency observations were supplied.`;
    return `${node}: latency (ms; UTC), objective ${metric.objective} ms\n`+metric.hours.map((hour,i)=>`${String(hour).padStart(2,"0")}:00 ${"#".repeat(Math.round(metric.latency[i]/10))} ${metric.latency[i]} ms`).join("\n")+"\nBars round to 10 ms per cell; numbers are exact.";
  }
  return `${node} [${record.state}] · synthetic · read-only\n`+DATA.edges.filter(e=>e.source===node||e.target===node).map(e=>`${e.source} -> ${e.target}: ${e.rate} jobs/hour`).join("\n");
}
export default function(pi:ExtensionAPI){
  let selected="enrich",active="dependencies";
  const ids=DATA.nodes.map(n=>n.id),views=["dependencies","metrics"];
  pi.registerCommand("workflow-view",{description:"Inspect a synthetic workflow; /workflow-view [node] [dependencies|metrics]",handler:async(args,ctx)=>{
    const output=(message:string,warning=false)=>{
      if(ctx.hasUI)ctx.ui.notify(message,warning?"warning":"info");
      else pi.sendMessage({customType:"workflow-view",content:message,display:true},{triggerTurn:false});
    };
    const tokens=args.trim().split(/\s+/).filter(Boolean);
    let nextNode=selected,nextView=active;
    if(tokens.length){
      if(tokens.length>2||!ids.includes(tokens[0])||tokens[1]&&!views.includes(tokens[1])){output("Use /workflow-view enrich metrics, or /workflow-view to choose.",true);return;}
      nextNode=tokens[0];nextView=tokens[1]??active;
    }else if(ctx.hasUI){
      // Built-in dialogs work in TUI and RPC. A custom terminal factory would
      // require a separate ctx.mode === "tui" branch and its own paint tests.
      const node=await ctx.ui.select(`Workflow node (current: ${selected})`,ids);
      if(!node)return;
      const view=await ctx.ui.select(`View for ${node}`,views);
      if(!view)return;
      nextNode=node;nextView=view;
    }
    // Commit both choices only after every awaited dialog has completed.
    selected=nextNode;active=nextView;output(describe(selected,active));
  }});
}
