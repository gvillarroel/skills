import { App } from "@modelcontextprotocol/ext-apps";

const ui = window.ServiceObservatory;
const app = new App({name:"Service Observatory",version:"1.0.0"},{},{strict:true});
app.ontoolresult = result => {
  if (!result.isError && result.structuredContent?.snapshot) ui.setData(result.structuredContent.snapshot);
};
app.onhostcontextchanged = context => {
  document.documentElement.dataset.hostTheme = context.theme ?? "light";
};
ui.setConnection("Connecting to host…");
document.getElementById("refresh").disabled=true;
// An embedded app must never silently simulate a successful server refresh.
ui.setRefreshHandler(async () => {
  await ready;
  const result = await app.callServerTool({name:"refresh_observatory",arguments:{}});
  if(result.isError || !result.structuredContent?.snapshot) throw new Error("Refresh unavailable");
  return result.structuredContent.snapshot;
});
const ready = app.connect();
ready.then(() => {
  const actionsAvailable=Boolean(app.getHostCapabilities()?.serverTools);
  document.getElementById("refresh").disabled=false;
  document.getElementById("refresh").hidden=!actionsAvailable;
  ui.setConnection(actionsAvailable?"Connected · synthetic source":"Snapshot · refresh unavailable");
  const context = app.getHostContext();
  document.documentElement.dataset.hostTheme = context?.theme ?? "light";
  if(context?.availableDisplayModes?.includes("fullscreen")) {
    const button = document.createElement("button");
    button.textContent = "Expand workspace";
    button.id = "expand-workspace";
    button.onclick = async () => {
      try {
        const result = await app.requestDisplayMode({mode:"fullscreen"});
        ui.setConnection(result.mode === "fullscreen" ? "Expanded workspace" : "Expansion unavailable; inline view retained");
      } catch { ui.setConnection("Expansion unavailable; inline view retained"); }
    };
    document.querySelector(".header-actions").append(button);
  }
  document.body.dataset.bridge="ready";
}).catch(() => { ui.setConnection("Host connection unavailable; initial snapshot retained");document.body.dataset.bridge="failed"; });
// This data view also works before or without a host connection. A sandboxed
// component must not assume ordinary browser downloads are permitted.
const exportButton = document.getElementById("export");
  exportButton.textContent = "View filtered data";
  exportButton.onclick = () => {
    let details = document.getElementById("export-data");
    if(!details) {
      details = document.createElement("details");details.id="export-data";
      const summary=document.createElement("summary");summary.textContent="Filtered service data (JSON)";
      const pre=document.createElement("pre");pre.tabIndex=0;
      details.append(summary,pre);document.querySelector(".app").append(details);
    }
    details.querySelector("pre").textContent=JSON.stringify(ui.getExport(),null,2);
    details.open=true;details.querySelector("pre").focus();
  };
