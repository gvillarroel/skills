#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Independently drive the built MCP Apps component through the standard bridge."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.parse
import urllib.request

from playwright.sync_api import sync_playwright

from artifact_contract import require
from validate_mcp_http import MCP
from validate_native_browser import OBSERVE


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    html = (args.evidence_dir / "widget.html").read_text(encoding="utf-8")
    initial = json.loads((args.evidence_dir / "render-colorset1.json").read_text(encoding="utf-8"))
    client = MCP(args.mcp_url, None)
    client.send("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
        "clientInfo": {"name": "independent-xy-widget-acceptance", "version": "0.1.0"}})
    client.send("notifications/initialized", notification=True)
    report = {"passed": False, "live_chatgpt_installation": "not_tested", "cases": [], "calls": []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel="msedge", chromium_sandbox=True)
        for downloads_supported in [True, False]:
            context = browser.new_context(viewport={"width": 1100, "height": 1000})
            context.add_init_script(OBSERVE)
            page = context.new_page()
            row = {"download_file_supported": downloads_supported, "errors": [], "checks": []}
            page.on("pageerror", lambda error: row["errors"].append(str(error)))

            def rpc(method: str, params: dict):
                report["calls"].append({"method": method, "params": params})
                if method == "ui/initialize":
                    capabilities = {"serverTools": {}, "openLinks": {}}
                    if downloads_supported:
                        capabilities["downloadFile"] = {}
                    return {"protocolVersion": params["protocolVersion"],
                        "hostInfo": {"name": "independent-protocol-host", "version": "0.1.0"},
                        "hostCapabilities": capabilities,
                        "hostContext": {"theme": "light", "displayMode": "inline",
                            "availableDisplayModes": ["inline", "fullscreen"],
                            "containerDimensions": {"width": 1100, "maxHeight": 2000}}}
                if method == "tools/call":
                    return client.send(method, params)
                if method == "ui/download-file":
                    for resource in params["contents"]:
                        with urllib.request.urlopen(resource["uri"], timeout=30) as response:
                            require(response.status == 200 and response.read(), "Host download payload unavailable")
                    return {}
                if method == "ui/open-link":
                    require(urllib.parse.urlsplit(params["url"]).netloc == urllib.parse.urlsplit(args.mcp_url).netloc,
                            "Navigation escaped the chart service")
                    return {}
                if method == "ui/request-display-mode":
                    return {"mode": "fullscreen"}
                return {}

            page.expose_function("independentRpc", rpc)
            try:
                page.set_content('<!doctype html><html><body style="margin:0"><iframe id="hosted" style="width:100%;height:1300px;border:0"></iframe></body></html>')
                page.evaluate("""({html,initial})=>{
                  const hosted=document.getElementById('hosted');
                  window.addEventListener('message',async event=>{
                    if(event.source!==hosted.contentWindow||event.data?.jsonrpc!=='2.0')return;
                    const message=event.data;
                    if(message.method==='ui/notifications/initialized'){
                      hosted.contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:initial},'*');return;
                    }
                    if(message.id!==undefined){
                      try{const result=await independentRpc(message.method,message.params??{});hosted.contentWindow.postMessage({jsonrpc:'2.0',id:message.id,result},'*')}
                      catch(error){hosted.contentWindow.postMessage({jsonrpc:'2.0',id:message.id,error:{code:-32603,message:String(error)}},'*')}
                    }else if(message.method)void independentRpc(message.method,message.params??{});
                  });hosted.srcdoc=html;
                }""", {"html": html, "initial": initial})
                widget = page.locator("#hosted").element_handle().content_frame()
                widget.locator('#colorset1[aria-pressed="true"]').wait_for(timeout=45000)
                native_element = widget.locator("#chart").element_handle()
                native = native_element.content_frame()
                native.wait_for_function("()=>window.__xyObservedViews?.length>0", timeout=30000)
                def fit():
                    native.wait_for_function("""()=>{
                      const canvas=window.__xyObservedViews?.[0]?.canvas;
                      return canvas&&canvas.getBoundingClientRect().width>200&&
                       canvas.getBoundingClientRect().width<=innerWidth+1;
                    }""", timeout=15000)
                    return native.evaluate("()=>({viewport:innerWidth,canvas:__xyObservedViews[0].canvas.getBoundingClientRect().toJSON(),document:document.documentElement.scrollWidth})")
                row["desktop_layout"] = fit()
                row["checks"].append("actual_native_canvas_fits_desktop")
                widget.locator("#colorset2").click()
                widget.locator('#colorset2[aria-pressed="true"]').wait_for(timeout=100000)
                native = native_element.content_frame()
                native.wait_for_function("()=>window.__xyObservedViews?.length>0", timeout=30000)
                fit()
                widget.locator("#svg").click()
                widget.locator("#preview").wait_for(state="visible")
                widget.wait_for_function("()=>document.getElementById('preview').complete&&document.getElementById('preview').naturalWidth>0")
                widget.get_by_role("link", name="Download SVG", exact=True).click()
                expected_method = "ui/download-file" if downloads_supported else "ui/open-link"
                page.wait_for_timeout(100)
                require(any(call["method"] == expected_method for call in report["calls"]), "Download bridge did not use supported host path")
                row["checks"].append("palette_recolor_native_svg_and_download_bridge")
                widget.locator("#interactive").click()
                page.set_viewport_size({"width": 390, "height": 1000})
                row["mobile_layout"] = fit()
                row["checks"].append("actual_native_canvas_resizes_to_mobile")
                page.screenshot(path=args.output_dir / f"mobile-download-{downloads_supported}.png", full_page=True)
                previous_url = widget.locator("#chart").get_attribute("src")
                page.evaluate("""()=>document.getElementById('hosted').contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:{isError:true,content:[{type:'text',text:'Independent intentional render error'}]}},'*')""")
                widget.locator("#error").wait_for(state="visible")
                require("Independent intentional render error" in widget.locator("#error").inner_text(), "Host tool failure was not reported")
                require(widget.locator("#chart").get_attribute("src") == previous_url, "Host tool failure discarded the previous chart")
                row["checks"].append("host_error_preserves_previous_chart")
                require(not row["errors"], "Widget or native chart JavaScript error")
                row["passed"] = True
            except Exception as error:
                row["passed"] = False
                row["failure"] = f"{type(error).__name__}: {error}"
                page.screenshot(path=args.output_dir / f"failure-download-{downloads_supported}.png", full_page=True)
            context.close()
            report["cases"].append(row)
            print(json.dumps(row), flush=True)
        browser.close()
    report["passed"] = all(row["passed"] for row in report["cases"])
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
