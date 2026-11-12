/* D3 operational-dashboard starter adapted into a read-only linked inspector. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const text = (id, value) => { $(id).textContent = String(value); };
  const cap = value => value[0].toUpperCase() + value.slice(1);
  const fmt = value => new Intl.NumberFormat("en-US").format(value);
  const units = {p95:"ms",error:"%",rps:"req/s"};
  const labels = {p95:"P95 latency",error:"Error rate",rps:"Traffic"};
  let data = structuredClone(window.SERVICE_DATA);
  const state = {selected:"payments",tab:"dependencies",team:"all",query:"",metric:"p95",trace:false,mobileAll:false,compare:false,layout:new URLSearchParams(location.search).get("layout") === "overview" ? "overview" : "focus",sort:"name",descending:false,alertFilter:false,epoch:0,busy:false};
  let refreshHandler = async () => { await new Promise(resolve => setTimeout(resolve, 80)); return {...structuredClone(data),revision:data.revision+1}; };
  const selected = () => data.services.find(service => service.id === state.selected) ?? data.services[0];
  const visible = () => data.services.filter(service => (state.team === "all" || service.team === state.team) && `${service.name} ${service.id} ${service.team}`.toLowerCase().includes(state.query.toLowerCase()));
  const relatedEdges = () => data.edges.filter(edge => edge.source === state.selected || edge.target === state.selected);
  function button(label, handler, className="", focusKey=label) {
    const node=document.createElement("button");node.textContent=label;node.className=className;node.dataset.focusKey=focusKey;
    node.addEventListener("click",event=>{
      const scope=node.closest("#adjacency,#related,#services-body,#incident-list"),restore=document.activeElement===node;
      handler(event);
      if(restore&&scope){
        const replacement=[...scope.querySelectorAll("button")].find(button=>button.dataset.focusKey===focusKey);
        if(replacement)replacement.focus({preventScroll:true});
        else{$("selected-name").tabIndex=-1;$("selected-name").focus({preventScroll:true});}
      }
    });return node;
  }
  function choose(id, announce=true) {
    if (!data.services.some(service => service.id === id)) return;
    state.selected=id;
    if(announce) text("selection-announcement",`${selected().name} selected. ${labels[state.metric]} ${selected()[state.metric]} ${units[state.metric]}.`);
    render();
  }
  function tab(name, focus=false) {
    state.tab=name;
    for(const node of document.querySelectorAll("[data-tab]")) { const active=node.dataset.tab===name;node.setAttribute("aria-selected",String(active));node.tabIndex=active?0:-1;if(active&&focus)node.focus(); }
    for(const name of ["dependencies","metrics","records"]) $(`${name}-panel`).hidden=state.layout!=="overview"&&state.tab!==name;
    if(name==="dependencies")renderMap();renderChart();
  }
  const network=d3.select("#network");
  network.append("defs").append("marker").attr("id","arrow").attr("viewBox","0 -4 8 8").attr("refX",7).attr("markerWidth",6).attr("markerHeight",6).attr("orient","auto").append("path").attr("d","M0,-4L8,0L0,4").attr("fill","#828282");
  const map=network.append("g").attr("class","map-content");
  const linksLayer=map.append("g"),nodesLayer=map.append("g");
  const zoom=d3.zoom().scaleExtent([0.75,2.3]).filter(event => !event.button && (event.type!=="wheel" || event.ctrlKey)).on("zoom",event=>map.attr("transform",event.transform));
  network.call(zoom).on("dblclick.zoom",null);
  function edgePath(edge) {
    const a=data.services.find(service=>service.id===edge.source),b=data.services.find(service=>service.id===edge.target);
    const dx=b.x-a.x,dy=b.y-a.y;
    if(Math.abs(dx)>=Math.abs(dy)){const x0=a.x+(dx>0?140:0),x1=b.x+(dx>0?-7:147),y0=a.y+28,y1=b.y+28,m=(x0+x1)/2;return `M${x0},${y0}C${m},${y0} ${m},${y1} ${x1},${y1}`;}
    const y0=a.y+(dy>0?56:0),y1=b.y+(dy>0?-7:63),x0=a.x+70,x1=b.x+70,m=(y0+y1)/2;return `M${x0},${y0}C${x0},${m} ${x1},${m} ${x1},${y1}`;
  }
  function renderMap(){
    const list=visible(),ids=new Set(list.map(service=>service.id));
    const edges=data.edges.filter(edge=>ids.has(edge.source)&&ids.has(edge.target));
    text("graph-summary",`${list.length} services · ${edges.length} directed relationships`);
    text("visible-count",`${list.length} of ${data.services.length} services visible`);
    $("clear-filters").hidden=state.team==="all"&&!state.query;
    $("empty").hidden=!!list.length;$("network").style.display=list.length?"":"none";
    network.classed("trace-on",state.trace);
    linksLayer.selectAll("path.edge").data(edges,edge=>edge.id).join(enter=>enter.append("path").attr("class","edge").attr("marker-end","url(#arrow)")).attr("d",edgePath).attr("class",edge=>`edge ${edge.kind}${edge.source===state.selected||edge.target===state.selected?" related-edge":""}`);
    const nodes=nodesLayer.selectAll("g.graph-node").data(list,service=>service.id).join(enter=>{const node=enter.append("g").attr("role","button");node.append("title");node.append("rect").attr("class","node-box").attr("width",140).attr("height",56).attr("rx",7);node.append("text").attr("class","node-label").attr("x",12).attr("y",22);node.append("text").attr("class","node-detail").attr("x",12).attr("y",41);node.append("text").attr("class","state-symbol").attr("x",123).attr("y",22);return node;});
    nodes.attr("transform",service=>`translate(${service.x},${service.y})`).attr("class",service=>`graph-node ${service.status}${service.id===state.selected?" selected":""}`).attr("tabindex",service=>service.id===state.selected?0:-1).attr("aria-pressed",service=>String(service.id===state.selected)).attr("aria-label",service=>`${service.name}, ${service.status}, ${service.p95} milliseconds`).on("click",(_,service)=>choose(service.id)).on("keydown",(event,service)=>{
      if(["Enter"," "].includes(event.key)){event.preventDefault();choose(service.id);}
      if(["ArrowRight","ArrowDown","ArrowLeft","ArrowUp"].includes(event.key)){event.preventDefault();const direction=["ArrowRight","ArrowDown"].includes(event.key)?1:-1;const next=list[(list.indexOf(service)+direction+list.length)%list.length];choose(next.id);nodesLayer.selectAll("g.graph-node").filter(d=>d.id===next.id).node()?.focus();}
    });
    if(!ids.has(state.selected))nodes.attr("tabindex",(_,index)=>index===0?0:-1);
    nodes.select("title").text(service=>`${service.name} · ${service.team} · ${service.status} · ${service.p95} ms`);
    nodes.select(".node-label").text(service=>service.name).each(function(service){const letters=[...service.name];while(this.getComputedTextLength()>102&&letters.length>2){letters.pop();this.textContent=letters.join("")+"…";}});
    nodes.select(".node-detail").text(service=>`${service.p95} ms · ${service.team}`);
    nodes.select(".state-symbol").text(service=>service.status==="degraded"?"!":service.status==="watch"?"△":"·");
    const near=new Set([state.selected,...relatedEdges().flatMap(e=>[e.source,e.target])]);const mobileList=list.filter(s=>state.mobileAll||state.query||state.team!=="all"||near.has(s.id));text("mobile-scope-summary",`${mobileList.length} of ${list.length} services · ${state.mobileAll?"all relationships":"selected service and direct neighbors"}`);$("mobile-scope").textContent=state.mobileAll?"Show direct neighbors":"Browse all services";$("mobile-scope").setAttribute("aria-expanded",String(state.mobileAll));
    $("adjacency").replaceChildren(...mobileList.map(service=>{const node=button(service.name,()=>choose(service.id));node.setAttribute("aria-pressed",String(service.id===state.selected));const label=document.createElement("span");const targets=data.edges.filter(edge=>edge.source===service.id).map(edge=>data.services.find(s=>s.id===edge.target).name);label.textContent=`${cap(service.status)} · ${service.p95} ms${targets.length?" → "+targets.join(", "):" · no outgoing calls"}`;node.append(label);return node;}));
    if(!list.length){const empty=document.createElement("p");empty.textContent="No services match. Clear the filters to restore the list.";$("adjacency").append(empty);}
  }
  function renderInspector(){
    const service=selected();text("selected-name",service.name);text("selected-owner",service.owner);text("selected-state",cap(service.status));$("selected-state").className=`status-badge ${service.status}`;
    text("selected-latency",`${service.p95} ms`);text("selected-errors",`${service.error.toFixed(2)}%`);text("selected-traffic",`${fmt(service.rps)} req/s`);$("outside-filter").hidden=visible().some(s=>s.id===state.selected);$("trace").setAttribute("aria-pressed",String(state.trace));
    $("related").replaceChildren(...relatedEdges().map(edge=>{const outgoing=edge.source===state.selected,id=outgoing?edge.target:edge.source,target=data.services.find(s=>s.id===id),li=document.createElement("li"),node=button(`${outgoing?"→":"←"} ${target.name}`,()=>choose(id));const detail=document.createElement("small");detail.textContent=`${outgoing?"Calls":"Called by"} · ${fmt(edge.rps)} ${edge.kind==="event"?"events/s":"req/s"}`;node.append(detail);li.append(node);return li;}));
  }
  function renderChart(){
    const service=selected(),metric=state.metric,width=Math.max(280,Math.min(840,$("metrics-panel").clientWidth-40||840)),height=width<460?260:330,margin={left:50,right:16,top:34,bottom:44};
    text("chart-heading",`${service.name} ${labels[metric].toLowerCase()}`);text("chart-title",`${service.name}: hourly ${labels[metric]}, ${units[metric]}`);text("value-unit",`${labels[metric]} (${units[metric]})`);text("values-caption",`${service.name}: exact hourly observations in ${units[metric]}`);
    const svg=d3.select("#timeseries").attr("viewBox",`0 0 ${width} ${height}`);svg.selectAll("g,path,line,circle,text:not(title):not(desc)").remove();
    const x=d3.scaleLinear().domain([0,23]).range([margin.left,width-margin.right]);
    const maximum=d3.max(data.services.flatMap(s=>s.history),point=>point[metric]);
    const y=d3.scaleLinear().domain([0,maximum*1.12]).nice().range([height-margin.bottom,margin.top]);
    svg.append("g").attr("class","grid").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(4).tickSize(-(width-margin.left-margin.right)).tickFormat(""));
    svg.append("g").attr("class","axis").attr("transform",`translate(0,${height-margin.bottom})`).call(d3.axisBottom(x).tickValues(width<460?[0,6,12,18,23]:[0,4,8,12,16,20,23]).tickFormat(hour=>`${String(hour).padStart(2,"0")}:00`));
    svg.append("g").attr("class","axis").attr("transform",`translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(value=>metric==="error"?`${value.toFixed(1)}%`:fmt(value)));
    svg.append("text").attr("x",margin.left).attr("y",18).attr("font-size",11).attr("fill","#696969").text(units[metric]);
    const line=d3.line().x(point=>x(point.hour)).y(point=>y(point[metric]));
    if(state.compare&&service.id!=="orders"){svg.append("path").datum(data.services.find(s=>s.id==="orders").history).attr("class","comparison-line").attr("d",line);svg.append("text").attr("x",width-185).attr("y",18).attr("font-size",11).text("— Selected   - - Orders");}
    svg.append("path").datum(service.history).attr("class","metric-line").attr("d",line);
    svg.selectAll("circle.observation").data(service.history).join("circle").attr("class","observation").attr("cx",p=>x(p.hour)).attr("cy",p=>y(p[metric])).attr("r",2.5).attr("fill","#9e1b32").append("title").text(p=>`${String(p.hour).padStart(2,"0")}:00 UTC · ${p[metric]} ${units[metric]}`);
    if(metric==="p95"){svg.append("line").attr("x1",margin.left).attr("x2",width-margin.right).attr("y1",y(250)).attr("y2",y(250)).attr("stroke","#4f4f4f").attr("stroke-dasharray","4 4");svg.append("text").attr("x",margin.left+7).attr("y",y(250)-6).attr("font-size",10).text("250 ms objective");}
    text("chart-story",metric==="p95"&&service.p95>250?`${service.name} exceeded the 250 ms latency objective in the latest observation.`:`${service.name}: latest ${labels[metric].toLowerCase()} is ${service[metric]} ${units[metric]}. The scale is shared across services.`);
    $("values-body").replaceChildren(...service.history.map(point=>{const row=document.createElement("tr");for(const value of [`${String(point.hour).padStart(2,"0")}:00`,point[metric]]){const cell=document.createElement("td");cell.textContent=String(value);row.append(cell);}return row;}));
  }
  function renderTable(){
    const rows=[...visible()].sort((a,b)=>typeof a[state.sort]==="number"?(a[state.sort]-b[state.sort])*(state.descending?-1:1):String(a[state.sort]).localeCompare(String(b[state.sort]))*(state.descending?-1:1));
    for(const node of document.querySelectorAll("[data-sort]"))node.closest("th").setAttribute("aria-sort",node.dataset.sort===state.sort?(state.descending?"descending":"ascending"):"none");
    $("services-body").replaceChildren(...rows.map(service=>{const row=document.createElement("tr");row.setAttribute("aria-selected",String(service.id===state.selected));const first=document.createElement("td");first.append(button(service.name,()=>choose(service.id)));row.append(first);for(const value of [cap(service.status),service.p95,service.error.toFixed(2),service.team]){const cell=document.createElement("td");cell.textContent=String(value);row.append(cell);}return row;}));
  }
  function renderAlerts(){
    const incidents=data.incidents.filter(incident=>!state.alertFilter||incident.service===state.selected);$("alert-filter").setAttribute("aria-pressed",String(state.alertFilter));text("alert-summary",`${incidents.length} active alert${incidents.length===1?"":"s"} · ${state.alertFilter?selected().name:"all services"}`);
    $("incident-list").replaceChildren(...incidents.map(incident=>{const row=document.createElement("article");row.className="incident-row";const time=document.createElement("time");time.textContent=incident.time;const severity=document.createElement("span");severity.className=`severity ${incident.severity.toLowerCase()}`;severity.textContent=incident.severity;const title=button(incident.title,()=>choose(incident.service),"incident-title");const sub=document.createElement("small");sub.textContent=`${incident.id} · ${data.services.find(s=>s.id===incident.service).name}`;title.append(sub);const status=document.createElement("span");status.className="incident-state";status.textContent=incident.status;row.append(time,severity,title,status);return row;}));
    if(!incidents.length){const empty=document.createElement("p");empty.textContent="No active alerts for this service.";$("incident-list").append(empty);}
  }
  function renderSummary(){
    const stat=(id,value,unit)=>{const node=$(id),span=document.createElement("span");span.className="stat-unit";span.textContent=unit;node.replaceChildren(document.createTextNode(fmt(value)),span);};
    stat("kpi-services",data.services.length,"services");stat("kpi-traffic",data.services.find(s=>s.id==="gateway")?.rps??0,"req/s");stat("kpi-latency",data.services.find(s=>s.id==="payments")?.p95??0,"ms");stat("kpi-alerts",data.incidents.length,"alerts");
    text("kpi-severity",["High","Medium","Low"].map(severity=>[severity,data.incidents.filter(i=>i.severity===severity).length]).filter(([,count])=>count).map(([severity,count])=>`${count} ${severity.toLowerCase()}`).join(" · ")||"No active alerts");
    text("kpi-health",["healthy","watch","degraded"].map(status=>`${data.services.filter(s=>s.status===status).length} ${status}`).join(" · "));
    const excess=(data.services.find(s=>s.id==="payments")?.p95??0)-250;text("kpi-objective",excess>0?`${excess} ms above the 250 ms objective`:"Within the 250 ms objective");
    const stamp=new Date(data.updatedAt);text("updated",`Updated ${stamp.toLocaleDateString("en-US",{month:"short",day:"numeric",timeZone:"UTC"})}, ${String(stamp.getUTCHours()).padStart(2,"0")}:${String(stamp.getUTCMinutes()).padStart(2,"0")} UTC`);
  }
  function render(){renderSummary();renderMap();renderInspector();renderChart();renderTable();renderAlerts();}
  function exportedSnapshot(){const services=visible(),ids=new Set(services.map(service=>service.id));return {exportSchemaVersion:1,synthetic:true,revision:data.revision,updatedAt:data.updatedAt,scope:{team:state.team,query:state.query,view:state.tab,metric:state.metric},selectedId:state.selected,selectionOutsideFilter:!ids.has(state.selected),services,edges:data.edges.filter(edge=>ids.has(edge.source)&&ids.has(edge.target))};}
  async function refresh(){
    const epoch=++state.epoch;state.busy=true;$("refresh").disabled=true;$("cancel-refresh").hidden=false;$("error").hidden=true;text("refresh-status","Refreshing…");
    try {const next=await refreshHandler();if(epoch!==state.epoch)return;setData(next);text("refresh-status","Snapshot refreshed");}
    catch(error){if(epoch!==state.epoch)return;$("error").hidden=false;text("refresh-status","Refresh failed; previous snapshot retained");}
    finally {if(epoch===state.epoch){state.busy=false;$("refresh").disabled=false;$("cancel-refresh").hidden=true;}}
  }
  function setData(next){if(!next||next.schemaVersion!==1||!Array.isArray(next.services)||!next.services.length||!Array.isArray(next.edges)||!Array.isArray(next.incidents))throw new Error("Invalid snapshot");const ids=new Set(next.services.map(s=>s.id));if(ids.size!==next.services.length||next.edges.some(e=>!ids.has(e.source)||!ids.has(e.target))||next.services.some(s=>!s.id||![s.x,s.y,s.p95,s.error,s.rps].every(Number.isFinite)||!Array.isArray(s.history)||s.history.length!==24||s.history.some(p=>![p.hour,p.p95,p.error,p.rps].every(Number.isFinite))))throw new Error("Invalid service identity or history");data=structuredClone(next);if(!ids.has(state.selected))state.selected=data.services[0].id;render();}
  $("mobile-scope").onclick=()=>{state.mobileAll=!state.mobileAll;renderMap();};
  $("refresh").onclick=refresh;$("retry").onclick=refresh;
  $("cancel-refresh").onclick=()=>{++state.epoch;state.busy=false;$("refresh").disabled=false;$("cancel-refresh").hidden=true;text("refresh-status","Refresh canceled; previous snapshot retained");};
  $("search").addEventListener("input",event=>{state.query=event.target.value;render();});$("team").onchange=event=>{state.team=event.target.value;render();};
  $("clear-filters").onclick=()=>{state.query="";state.team="all";$("search").value="";$("team").value="all";render();$("search").focus();};
  $("trace").onclick=()=>{state.trace=!state.trace;renderMap();renderInspector();};
  $("metric").onchange=event=>{state.metric=event.target.value;renderChart();};$("show-metrics").onclick=()=>tab("metrics",true);$("compare").onchange=event=>{state.compare=event.target.checked;renderChart();};
  $("options-toggle").onclick=()=>{const open=$("options").hidden;$("options").hidden=!open;$("options-toggle").setAttribute("aria-expanded",String(open));};
  $("options").addEventListener("keydown",event=>{if(event.key==="Escape"){event.preventDefault();$("options").hidden=true;$("options-toggle").setAttribute("aria-expanded","false");$("options-toggle").focus();}});
  $("layout").value=state.layout;document.body.classList.toggle("overview",state.layout==="overview");$("layout").onchange=event=>{state.layout=event.target.value;document.body.classList.toggle("overview",state.layout==="overview");tab(state.tab);};
  $("alert-filter").onclick=()=>{state.alertFilter=!state.alertFilter;renderAlerts();};
  for(const node of document.querySelectorAll("[data-tab]")){node.onclick=()=>tab(node.dataset.tab);node.addEventListener("keydown",event=>{if(["ArrowLeft","ArrowRight","Home","End"].includes(event.key)){event.preventDefault();const names=["dependencies","metrics","records"],i=names.indexOf(state.tab),next=event.key==="Home"?0:event.key==="End"?2:(i+(event.key==="ArrowRight"?1:2))%3;tab(names[next],true);}});}
  for(const node of document.querySelectorAll("[data-sort]"))node.onclick=()=>{if(state.sort===node.dataset.sort)state.descending=!state.descending;else{state.sort=node.dataset.sort;state.descending=false;}renderTable();};
  $("zoom-in").onclick=()=>network.call(zoom.scaleBy,1.2);$("zoom-out").onclick=()=>network.call(zoom.scaleBy,1/1.2);$("fit").onclick=()=>network.call(zoom.transform,d3.zoomIdentity);
  $("export").onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(exportedSnapshot(),null,2)],{type:"application/json"})),a=document.createElement("a");a.href=url;a.download="service-observatory.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  window.ServiceObservatory={setData,getState:()=>structuredClone(state),getData:()=>structuredClone(data),getExport:()=>structuredClone(exportedSnapshot()),setRefreshHandler:handler=>{refreshHandler=handler;},setConnection:label=>text("connection",label),select:choose,tab};
  window.addEventListener("resize",()=>{if(!$("metrics-panel").hidden||state.layout==="overview")renderChart();});
  tab(state.tab);render();
})();
