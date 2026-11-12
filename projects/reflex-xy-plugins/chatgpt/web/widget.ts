import { App, applyHostStyleVariables } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";
import { embeddedPreviewHtml } from "../src/preview.js";
interface ChartOutput {render_id:string;title:string;palette:"colorset1"|"colorset2";width:number;height:number;factory:string;rows:number;marks:number;warnings:string[];expires_at:string;downloads:Record<"html"|"svg"|"png"|"source"|"spec",string>;}
type Format="html"|"svg"|"png"|"source"|"spec";
const app=new App({name:"reflex-xy-widget",version:"0.3.1"},{availableDisplayModes:["inline","fullscreen"]},{autoResize:true,strict:true});
const $=<T extends HTMLElement>(id:string)=>document.getElementById(id) as T;
const main=document.querySelector("main")!;const frame=$<HTMLIFrameElement>("chart");const preview=$<HTMLImageElement>("preview");
const panel=$("advanced-panel"),more=$<HTMLButtonElement>("more-summary"),palette=$<HTMLSelectElement>("palette-select"),view=$<HTMLSelectElement>("view-select"),format=$<HTMLSelectElement>("export-format"),chartTools=$<HTMLInputElement>("chart-tools");
const specEditor=$<HTMLTextAreaElement>("spec-editor"),applyData=$<HTMLButtonElement>("apply-data");let editorDirty=false;
let latest:ChartOutput|undefined,renderKey="",origin="",busy=false,saving=false,connected=false,currentEpoch=0,previewHtml="",previewReady=false,previewTimer:ReturnType<typeof setTimeout>|undefined;
function message(text="",error=false){$("status").textContent=error?"":text;$("status").hidden=error||!text;$("error").hidden=!error;$("error").textContent=error?text:"";}
function setBusy(value:boolean){
  busy=value;main.setAttribute("aria-busy",String(value));palette.disabled=view.disabled=value||!latest||!connected;
  chartTools.disabled=value||!latest||!connected||view.value!=="interactive";
  applyData.disabled=value||!latest||!connected;
  format.disabled=!latest||!connected;$<HTMLButtonElement>("download-format").disabled=!latest||!connected;
  // Keep the previous image available while a replacement is rendering.
  const save=$<HTMLButtonElement>("save-image");save.disabled=!latest||!connected;save.setAttribute("aria-disabled",String(saving));save.setAttribute("aria-busy",String(saving));
}
function safeUrl(value:unknown):string{
  if(typeof value!=="string"||value.length>2048)throw Error("Invalid chart artifact URL.");const url=new URL(value);
  if(!["http:","https:"].includes(url.protocol)||url.origin!==origin||!/^\/artifacts\/[a-f0-9]{32}\/(chart\.(html|svg|png|py)|spec\.json)$/.test(url.pathname)||!url.searchParams.has("token"))throw Error("Unexpected chart artifact origin or path.");return url.href;
}
function showView(){
  const inactive=view.value!=="interactive";frame.hidden=!latest;frame.dataset.inactive=String(inactive);frame.inert=inactive;frame.setAttribute("aria-hidden",String(inactive));preview.hidden=view.value!=="svg"||!latest;
  const pending=frame.dataset.pendingRender;if(!frame.hidden&&!inactive&&pending){const bounds=frame.getBoundingClientRect();frame.width=String(Math.ceil(bounds.width));requestAnimationFrame(()=>{if(!frame.hidden&&view.value==="interactive"&&frame.dataset.pendingRender===pending){delete frame.dataset.pendingRender;previewReady=false;frame.srcdoc=previewHtml;clearTimeout(previewTimer);previewTimer=setTimeout(()=>{if(!previewReady&&latest?.render_id===pending){view.value="svg";showView();message("Interactive preview is unavailable in this host. Showing the chart image. Download HTML for the full browser interactions.",true);}},15000);}});}setBusy(busy);
}
function exportHelp(){
  const help:Record<string,string>={svg:"SVG saves the chart's original view and stays sharp when resized. Enable Show chart tools for in-chart controls.",html:"HTML opens the original chart with browser interactions. Future Python updates require a live backend.",source:"Edit this Python source to regenerate the original chart.",spec:"JSON preserves the original chart specification."};$("export-help").textContent=help[format.value]??"";
}
async function download(kind:Format){
  if(!latest||(kind==="png"&&saving))return;if(Date.now()>=Date.parse(latest.expires_at)){message("This download link has expired. Ask for a fresh chart.",true);return;}
  if(kind==="png"){saving=true;setBusy(busy);}
  try{
    if(!app.getHostCapabilities()?.downloadFile)throw Error("This host does not support saving files from embedded apps. Use a host with file downloads enabled.");
    const response=await app.callServerTool({name:"xy_get_chart_artifact",arguments:{render_id:latest.render_id,render_key:renderKey,format:kind}},{timeout:100000});
    if(response.isError)throw Error(response.content?.filter(c=>c.type==="text").map(c=>c.text).join("\n")||"The export is unavailable.");
    const artifact=response._meta?.artifact as {name?:unknown;mime_type?:unknown;blob?:unknown}|undefined;
    const name=`chart.${kind==="source"?"py":kind==="spec"?"json":kind}`;
    // The specification uses spec.json; all names and MIME types are fixed by
    // the server contract, never accepted from a chart's editable content.
    const expectedName=kind==="spec"?"spec.json":name;
    const mime={html:"text/html; charset=utf-8",svg:"image/svg+xml",png:"image/png",source:"text/plain; charset=utf-8",spec:"application/json; charset=utf-8"}[kind];
    if(artifact?.name!==expectedName||artifact.mime_type!==mime||typeof artifact.blob!=="string"||artifact.blob.length>Math.ceil(16*1024*1024/3)*4||artifact.blob.length%4!==0||/[^A-Za-z0-9+/=]/.test(artifact.blob))throw Error("The server returned an invalid embedded export.");
    const result=await app.downloadFile({contents:[{type:"resource",resource:{uri:`file:///${expectedName}`,mimeType:mime,blob:artifact.blob}}]});
    if(result.isError)throw Error("The download was not completed. Try again or ask for a fresh chart.");if(!busy)message();
  }
  catch(error){message(error instanceof Error?error.message:"Cannot save this file.",true);}finally{if(kind==="png"){saving=false;setBusy(busy);}}
}
function update(result:CallToolResult, resetEditor=false){
  if(result.isError)throw Error(result.content?.filter(c=>c.type==="text").map(c=>c.text).join("\n")||"Chart rendering failed.");
  const data=result.structuredContent as unknown as ChartOutput,meta=result._meta as Record<string,unknown>|undefined;
  if(!data||!/^[a-f0-9]{32}$/.test(data.render_id)||!["colorset1","colorset2"].includes(data.palette)||!Number.isInteger(data.width)||!Number.isInteger(data.height)||data.width<320||data.width>2000||data.height<240||data.height>1400||typeof meta?.artifact_origin!=="string"||typeof meta.render_key!=="string")throw Error("The server returned an invalid chart result.");
  const parsedOrigin=new URL(meta.artifact_origin);if(!["http:","https:"].includes(parsedOrigin.protocol)||parsedOrigin.origin!==meta.artifact_origin)throw Error("Invalid artifact origin.");origin=parsedOrigin.origin;for(const value of Object.values(data.downloads))safeUrl(value);
  const native=meta.native_preview as {html?:unknown;svg?:unknown}|undefined;
  if(typeof native?.html!=="string"||typeof native.svg!=="string"||new TextEncoder().encode(native.html+native.svg).length>8*1024*1024||!/^\s*(?:<\?xml[^>]*>\s*)?<svg\b/i.test(native.svg))throw Error("The server returned an invalid embedded chart preview.");
  const nextPreviewHtml=embeddedPreviewHtml(native.html);
  latest=data;renderKey=meta.render_key;previewHtml=nextPreviewHtml;frame.dataset.pendingRender=data.render_id;$("title").textContent=data.title;palette.value=data.palette;frame.title=`${data.title} — interactive chart`;frame.style.height=`${data.height+24}px`;preview.alt=data.title;preview.src=`data:image/svg+xml;charset=utf-8,${encodeURIComponent(native.svg)}`;
  if(typeof meta.spec_json==="string"&&(!editorDirty||resetEditor)){try{const editable=JSON.parse(meta.spec_json);specEditor.value=JSON.stringify(editable,null,2);editorDirty=false;$("data-help").textContent=`${editable.description==="Sample data"?"This chart starts with sample data. ":""}Edit the JSON chart specification, then apply it. A failed update keeps your last valid chart.`;}catch{throw Error("The server returned an invalid editable specification.");}}
  $("expiry").textContent=`Links expire at ${new Date(data.expires_at).toLocaleTimeString()}. Save a file to keep it.`;
  const exportWarnings=(data.warnings??[]).filter(warning=>!/^Standalone HTML is an interactive snapshot; Python callbacks and future updates need a live host\.$/.test(warning));
  $("warnings").textContent=exportWarnings.join(" ");$("warnings").hidden=!exportWarnings.length;
  exportHelp();message();setBusy(false);showView();
}
app.ontoolresult=result=>{try{++currentEpoch;update(result);}catch(error){message(error instanceof Error?error.message:"Invalid chart result.",true);setBusy(false);}};
app.ontoolinput=()=>{message("Creating chart…");setBusy(true);};app.ontoolcancelled=()=>{message("Creating the chart was cancelled. You can ask to try again.",true);setBusy(false);};
app.onhostcontextchanged=context=>{if(context.styles?.variables)applyHostStyleVariables(context.styles.variables);if(context.availableDisplayModes)$("expand").hidden=!context.availableDisplayModes.includes("fullscreen");};app.onteardown=async()=>{clearTimeout(previewTimer);frame.removeAttribute("srcdoc");frame.src="about:blank";preview.removeAttribute("src");return {};};
palette.onchange=async()=>{
  if(!latest||busy||latest.palette===palette.value)return;const colorset=palette.value;palette.value=latest.palette;const restoreFocus=document.activeElement===palette;let focusMoved=false;
  const watchFocus=(event:FocusEvent)=>{if(event.target!==palette&&event.target!==document.body)focusMoved=true;};document.addEventListener("focusin",watchFocus);
  const epoch=++currentEpoch;setBusy(true);message("Updating chart…");
  try{const result=await app.callServerTool({name:"xy_recolor_chart",arguments:{render_id:latest.render_id,render_key:renderKey,colorset}},{timeout:100000});if(epoch===currentEpoch)update(result);}catch(error){if(epoch===currentEpoch)message(error instanceof Error?error.message:"Cannot change this chart's palette.",true);}finally{document.removeEventListener("focusin",watchFocus);if(epoch===currentEpoch){setBusy(false);if(restoreFocus&&!focusMoved&&document.hasFocus()&&document.activeElement===document.body)palette.focus();}}
};
specEditor.oninput=()=>{editorDirty=true;};
applyData.onclick=async()=>{
  if(busy||!latest||!connected)return;
  let spec:unknown;
  try{if(new TextEncoder().encode(specEditor.value).length>196608)throw Error("Chart input exceeds 192 KiB.");spec=JSON.parse(specEditor.value);if(!spec||typeof spec!=="object"||Array.isArray(spec))throw Error("Use a JSON chart object.");}
  catch(error){message(error instanceof SyntaxError?"The chart specification is not valid JSON. Correct it and apply again.":error instanceof Error?error.message:"Invalid chart specification.",true);return;}
  const epoch=++currentEpoch;setBusy(true);message("Updating chart…");
  try{const result=await app.callServerTool({name:"xy_render_chart",arguments:{spec_json:JSON.stringify(spec)}},{timeout:100000});if(epoch===currentEpoch)update(result,true);}
  catch(error){if(epoch===currentEpoch)message(error instanceof Error?error.message:"Cannot apply this chart data.",true);}
  finally{if(epoch===currentEpoch){setBusy(false);if(document.hasFocus()&&document.activeElement===document.body)applyData.focus();}}
};
function sendChartTools(){frame.contentWindow?.postMessage({type:"reflex-xy-preview-tools",visible:chartTools.checked},"*");}
window.addEventListener("message",event=>{if(event.source===frame.contentWindow&&event.data?.type==="reflex-xy-preview-ready"){previewReady=true;clearTimeout(previewTimer);sendChartTools();}});
$("save-image").onclick=()=>void download("png");$("download-format").onclick=()=>void download(format.value as Format);format.onchange=()=>exportHelp();view.onchange=()=>showView();chartTools.onchange=()=>sendChartTools();frame.onload=()=>sendChartTools();
function toggleOptions(expanded=!Boolean(more.getAttribute("aria-expanded")==="true")){more.setAttribute("aria-expanded",String(expanded));panel.hidden=!expanded;}
more.onclick=()=>toggleOptions();main.addEventListener("keydown",event=>{if(event instanceof KeyboardEvent&&event.key==="Escape"&&!panel.hidden){toggleOptions(false);more.focus();event.preventDefault();}});
$("expand").onclick=async()=>{try{await app.requestDisplayMode({mode:"fullscreen"});}catch{message("This host could not expand the chart.",true);}};
frame.onerror=()=>{view.value="svg";showView();message("Interactive preview is unavailable in this host. Showing the chart image.",true);};preview.onerror=()=>{if(view.value==="svg")message("This host could not display the embedded chart image. Save the image to view it.",true);};
void app.connect().then(()=>{connected=true;const context=app.getHostContext();if(context?.styles?.variables)applyHostStyleVariables(context.styles.variables);$("expand").hidden=!context?.availableDisplayModes?.includes("fullscreen");setBusy(false);if(!latest)message("Creating chart…");}).catch(()=>{message("This chart needs a compatible app host. You can still use its file links in the conversation.",true);setBusy(false);});
