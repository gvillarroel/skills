// Validate with: claude plugin validate <plugin> --strict --json
import { DATA } from "../assets/data.ts";
const PANE="service-observatory";
const escape=(value:unknown)=>String(value).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll('"',"&quot;");
function rows(list=DATA.services){return list.map(s=>`${s.name}: ${s.status}; P95 ${s.p95} ms; error ${s.error}%; ${s.rps} req/s [id: ${s.id}]`).join("\n");}
function details(id:string,view:string){
  const s=DATA.services.find(s=>s.id===id)!;
  if(view==="metrics")return `${s.name} · P95 ${s.p95} ms · objective 250 ms\nHourly P95 (ms; UTC):\n${s.history.map(p=>`${String(p.hour).padStart(2,"0")}:00 ${p.p95}`).join(" | ")}`;
  if(view==="records")return rows();
  const edges=DATA.edges.filter(e=>e.source===id||e.target===id);
  return `${s.name} · ${s.status} · ${s.owner}\nP95 ${s.p95} ms · Error ${s.error}% · ${s.rps} req/s\n`+edges.map(e=>`${e.source===id?"Calls":"Called by"} ${DATA.services.find(s=>s.id===(e.source===id?e.target:e.source))!.name}: ${e.rps} ${e.kind==="event"?"events/s":"req/s"}`).join("\n");
}
export function svg(id:string,view:string){
  const s=DATA.services.find(s=>s.id===id)!;
  const title=view==="metrics"?`${s.name} hourly P95 latency (ms; UTC)`:`Direct dependencies of ${s.name}`;
  let content="";
  if(view==="metrics"){
    const x=(h:number)=>55+h*31,y=(v:number)=>290-v*.7;
    content=`<path d="M55 45V290H785" fill="none" stroke="#696969"/><path d="M55 ${y(250)}H785" stroke="#696969" stroke-dasharray="4 4"/><text x="60" y="${y(250)-8}">250 ms objective</text><path d="${s.history.map((p,i)=>`${i?"L":"M"}${x(p.hour)} ${y(p.p95)}`).join(" ")}" fill="none" stroke="#9e1b32" stroke-width="3"/>`;
    for(const h of [0,6,12,18,23])content+=`<text x="${x(h)}" y="315" text-anchor="middle">${String(h).padStart(2,"0")}:00</text>`;
    for(const v of [0,100,200,300])content+=`<text x="46" y="${y(v)+4}" text-anchor="end">${v}</text>`;
  }else{
    const neighbors=DATA.edges.filter(e=>e.source===id||e.target===id),left=neighbors.filter(e=>e.target===id),right=neighbors.filter(e=>e.source===id);
    const box=(name:string,x:number,y:number,active=false)=>`<rect x="${x}" y="${y}" width="165" height="54" rx="4" fill="#ffffff" stroke="${active?"#9e1b32":"#696969"}" stroke-width="${active?3:1}"/><text x="${x+12}" y="${y+31}">${escape(name)}</text>`;
    content=box(s.name,330,150,true);
    for(const [side,edges]of [["left",left],["right",right]]as const)edges.forEach((e,i)=>{const x=side==="left"?25:650,y=70+i*80,name=DATA.services.find(s=>s.id===(side==="left"?e.source:e.target))!.name;content+=`<path d="${side==="left"?`M190 ${y+27}L323 177`:`M495 177L643 ${y+27}`}" stroke="#696969" fill="none" marker-end="url(#arrow)"${e.kind==="event"?' stroke-dasharray="5 4"':""}/>`+box(name,x,y);});
    content+='<text x="28" y="330">Arrow = direction of calls · dashed = event · direct relationships only</text>';
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 350" role="img" aria-labelledby="title desc"><title id="title">${escape(title)}</title><desc id="desc">Synthetic data. Use the native selectors to change service or view. Exact values are provided as text.</desc><defs><marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#696969"/></marker></defs><rect width="840" height="350" fill="#f7f7f7"/><g font-family="Arial,sans-serif" font-size="14" fill="#333e48"><text x="25" y="30" font-size="20">${escape(title)}</text>${content}</g></svg>`;
}
export function register(on){
  let selected="payments",view="dependencies",advanced=false;
  on("session.start",async($,event,next)=>{await $.command.register({name:"service-observatory",description:"Inspect synthetic dependencies and metrics",argumentHint:"[service-id | all | help]"});return next(event);});
  on("command.run",{command:"service-observatory"},async($,event)=>{
    const args=(event.args??"").trim();
    if(args==="all")return {text:rows()};
    if(args==="help")return {text:"Use /service-observatory to open the pane, /service-observatory payments for direct details, or /service-observatory all for exact values."};
    if(args){if(!DATA.services.some(s=>s.id===args))return {text:"Unknown service. Use /service-observatory all for the available IDs and values."};return {text:details(args,"dependencies")};}
    try{const placement=await $.ui.open({id:PANE,title:"Service Observatory"});if(placement?.isPlaced)return {};}catch{}
    return {text:`The native pane is unavailable. Synthetic read-only snapshot:\n${details(selected,view)}\nUse /service-observatory all for all exact values.`};
  });
  on("ui.render",{component:"Pane"},($,event,next)=>{
    if(event.requestId!==PANE||!["terminal","desktop","vscode"].includes(event.surface))return next(event);
    const {Box,Text,Select,Button}=$.ui.resolve(event);
    const children=[Text({bold:true,children:"Service Observatory · synthetic data · read-only"}),
      Select({key:"service",label:"Service",value:selected,options:DATA.services.map(s=>({value:s.id,label:`${s.name} · ${s.status}`})),onSelect:id=>{if(DATA.services.some(s=>s.id===id)){selected=id;$.ui.invalidate("ui.render");}}}),
      Select({key:"view",label:"View",value:view,options:[{value:"dependencies",label:"Direct dependencies"},{value:"metrics",label:"Hourly P95"},{value:"records",label:"Exact service values"}],onSelect:value=>{if(["dependencies","metrics","records"].includes(value)){view=value;$.ui.invalidate("ui.render");}}})];
    if(view!=="records"&&event.surface!=="terminal"&&(event.props?.bodyColumns??80)>=60){
      const {Svg}=$.ui.resolve(event);const width=Math.min(840,(event.props?.bodyColumns??80)*8);
      children.push(Svg({source:svg(selected,view),alt:view==="metrics"?"Hourly P95 latency; exact values follow":"Directed direct dependencies; exact relationships follow",width,height:Math.round(width*350/840)}));
    }
    children.push(Text({children:details(selected,view)}));
    children.push(Button({key:"options",label:advanced?"Hide options":"More options",onPress:()=>{advanced=!advanced;$.ui.invalidate("ui.render");}}));
    if(advanced)children.push(Text({children:"Native SVG is an image preview. Pan, brush and hover require a separate browser artifact. The terminal uses exact text relationships and values. Changes to this view do not start model work."}));
    children.push(Button({key:"close",label:"Close",onPress:async()=>{await $.ui.close({id:PANE});}}));
    return Box({flexDirection:"column",children});
  });
}
