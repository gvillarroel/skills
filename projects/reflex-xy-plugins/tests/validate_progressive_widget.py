#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Independently validate simple-first MCP Apps UI and retained native behavior."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

from PIL import Image
from playwright.sync_api import sync_playwright

from artifact_contract import require
from validate_mcp_http import MCP
from validate_native_browser import OBSERVE


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-url", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    client = MCP(args.mcp_url, None)
    client.send("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
        "clientInfo": {"name": "independent-progressive-ui", "version": "0.2.0"}})
    client.send("notifications/initialized", notification=True)
    initial = client.send("tools/call", {"name": "xy_render_chart", "arguments": {
        "spec_json": json.dumps({"preset": "scatter", "title": "Measured response"})}})
    require(not initial.get("isError"), "Initial native chart failed")
    require(initial["structuredContent"]["palette"] == "colorset1", "Fresh chart default is not Colorset 1")
    tools = client.send("tools/list")["tools"]
    ui_uri = next(tool for tool in tools if tool["name"] == "xy_render_chart")["_meta"]["ui"]["resourceUri"]
    resource = client.send("resources/read", {"uri": ui_uri})["contents"][0]
    html = resource["text"]
    report = {"passed": False, "scope": "progressive-ui-0.2.0", "live_host_installation": "not_tested",
        "widget_sha256": hashlib.sha256(html.encode()).hexdigest(), "cases": [], "calls": [], "downloads": []}
    (args.output_dir / "widget.html").write_text(html, encoding="utf-8")
    original_url = initial["structuredContent"]["downloads"]["html"]
    original = fetch(original_url)
    compact = fetch(original_url + "&preview=compact")
    compact_text = compact.decode()
    styles = [match for match in re.finditer(r"<style\b[^>]*>([\s\S]*?)</style>", compact_text)
        if re.sub(r"[\s\"']", "", match[1]) == ".xy[data-xy-slot=modebar]{display:none!important}"]
    require(len(styles) == 1, "Compact response does not contain one narrowly scoped toolbar rule")
    bridges = list(re.finditer(r"<script\b[^>]*data-xy-compact-preview-bridge[^>]*>([\s\S]*?)</script>", compact_text))
    require(len(bridges) == 1, "Compact response lacks its single fixed visibility bridge")
    bridge = bridges[0][1]
    require(all(token in bridge for token in ["window.parent", "reflex-xy-preview-tools", "boolean", "disabled"]), "Compact visibility bridge lacks its required boundary")
    require(not re.search(r"\b(?:eval|Function|fetch|location|innerHTML)\b|document\.write", bridge), "Compact bridge contains an unexpected capability")
    stripped = compact_text
    for match in sorted(styles + bridges, key=lambda match: match.start(), reverse=True):
        stripped = stripped[:match.start()] + stripped[match.end():]
    normalize_gap = lambda text: re.sub(r"\s+(?=</(?:head|body)>)", "", text)
    require(normalize_gap(stripped) == normalize_gap(original.decode()), "Compact preview changed native HTML beyond its toolbar CSS and fixed bridge")
    require(fetch(original_url) == original, "Requesting compact preview mutated the stored original HTML")
    report["compact_response"] = {"original_sha256": hashlib.sha256(original).hexdigest(),
        "compact_sha256": hashlib.sha256(compact).hexdigest(), "only_toolbar_css_and_fixed_bridge_added": True,
        "original_download_unchanged": True}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel="msedge", chromium_sandbox=True)
        for download_supported in [True, False]:
            context = browser.new_context(viewport={"width": 1100, "height": 1000})
            context.add_init_script(OBSERVE)
            page = context.new_page()
            row = {"download_file_supported": download_supported, "errors": [], "checks": []}
            page.on("pageerror", lambda error: row["errors"].append(str(error)))

            def rpc(method: str, params: dict):
                report["calls"].append({"method": method, "params": params})
                if method == "ui/initialize":
                    caps = {"serverTools": {}, "openLinks": {}}
                    if download_supported:
                        caps["downloadFile"] = {}
                    return {"protocolVersion": params["protocolVersion"],
                        "hostInfo": {"name": "independent-ui-host", "version": "0.2.0"},
                        "hostCapabilities": caps,
                        "hostContext": {"theme": "light", "displayMode": "inline",
                            "availableDisplayModes": ["inline", "fullscreen"],
                            "containerDimensions": {"width": 1100, "maxHeight": 2000}}}
                if method == "tools/call":
                    return client.send(method, params)
                if method in {"ui/download-file", "ui/open-link"}:
                    url = params["contents"][0]["uri"] if method == "ui/download-file" else params["url"]
                    require(urllib.parse.urlsplit(url).netloc == urllib.parse.urlsplit(args.mcp_url).netloc,
                            "Save action escaped the configured origin")
                    data = fetch(url)
                    suffix = Path(urllib.parse.urlsplit(url).path).suffix
                    if suffix == ".png":
                        with Image.open(io.BytesIO(data)) as image:
                            require(image.format == "PNG" and image.width >= 320, "Save image did not return native PNG")
                    report["downloads"].append({"method": method, "url": url, "suffix": suffix,
                        "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
                    return {}
                if method == "ui/request-display-mode":
                    return {"mode": "fullscreen"}
                return {}

            page.expose_function("independentRpc", rpc)
            try:
                page.set_content('<!doctype html><html><body style="margin:0"><iframe id="hosted" style="width:100%;height:1500px;border:0"></iframe></body></html>')
                page.evaluate("""({html,initial})=>{
                  const hosted=document.getElementById('hosted');window.__failNextTool=false;
                  window.addEventListener('message',async event=>{
                    if(event.source!==hosted.contentWindow||event.data?.jsonrpc!=='2.0')return;
                    const message=event.data;
                    if(message.method==='ui/notifications/initialized'){
                      hosted.contentWindow.postMessage({jsonrpc:'2.0',method:'ui/notifications/tool-result',params:initial},'*');return;
                    }
                    if(message.id!==undefined){try{
                      if(message.method==='tools/call'){
                        await new Promise(resolve=>setTimeout(resolve,700));
                        if(window.__failNextTool){window.__failNextTool=false;throw Error('Independent intentional update failure')}
                      }
                      const result=await independentRpc(message.method,message.params??{});
                      hosted.contentWindow.postMessage({jsonrpc:'2.0',id:message.id,result},'*');
                    }catch(error){hosted.contentWindow.postMessage({jsonrpc:'2.0',id:message.id,error:{code:-32603,message:String(error)}},'*')}}
                    else if(message.method)void independentRpc(message.method,message.params??{});
                  });hosted.srcdoc=html;
                }""", {"html": html, "initial": initial})
                widget = page.locator("#hosted").element_handle().content_frame()
                widget.locator("#save-image").wait_for(state="visible")
                widget.wait_for_function("()=>document.querySelector('main').getAttribute('aria-busy')==='false'")
                require(widget.locator("#save-image").is_enabled(), "Primary save action is unavailable")
                more = widget.locator("#more-summary")
                panel = widget.locator("#advanced-panel")
                require(not panel.is_visible(), "Advanced options start expanded")
                initial_actions = widget.locator("button,summary,input,select,a[href]").evaluate_all("""elements=>elements.filter(element=>{
                    const style=getComputedStyle(element),box=element.getBoundingClientRect();
                    return box.width>0&&box.height>0&&style.visibility!=='hidden'&&style.display!=='none';
                }).map(element=>({id:element.id,text:element.textContent.trim()}))""")
                require(len(initial_actions) <= 3 and {item["id"] for item in initial_actions} <= {"save-image", "more-summary", "expand"},
                        "First view exposes advanced controls")
                row["initial_actions"] = initial_actions
                for selector in ["#palette-select", "#view-select", "#export-format", "#download-format", "#chart-tools"]:
                    require(not widget.locator(selector).is_visible(), f"Initial technical control is visible: {selector}")
                row["checks"].append("simple_first_view_at_most_three_actions")
                native_element = widget.locator("#chart").element_handle()
                def ready_native():
                    widget.wait_for_function("()=>!document.getElementById('chart').dataset.pendingSrc", timeout=15000)
                    current = widget.locator("#chart").element_handle().content_frame()
                    current.wait_for_url(widget.locator("#chart").get_attribute("src"), wait_until="load", timeout=30000)
                    current.wait_for_function("()=>window.__xyObservedViews?.length>0", timeout=30000)
                    current.wait_for_function("()=>{const box=__xyObservedViews[0].canvas.getBoundingClientRect();return box.width>100&&box.height>100}", timeout=15000)
                    return current
                native = ready_native()
                require("preview=compact" in widget.locator("#chart").get_attribute("src"), "Initial native frame is not compact")
                canvas = native.evaluate_handle("__xyObservedViews[0].canvas").as_element()
                canvas.hover()
                require(native.locator('[data-xy-slot="modebar"]').count() >= 1, "Native toolbar is absent from the source")
                require(native.locator('[data-xy-slot="modebar"]').evaluate_all("elements=>elements.every(element=>getComputedStyle(element).display==='none')"), "Compact native toolbar still appears on hover")
                native.evaluate("window.postMessage({type:'reflex-xy-preview-tools',visible:true},'*')")
                widget.evaluate("""()=>{
                  const child=document.getElementById('chart').contentWindow;
                  child.postMessage({type:'other-message',visible:true},'*');
                  child.postMessage({type:'reflex-xy-preview-tools',visible:'true'},'*');
                }""")
                page.wait_for_timeout(100)
                require(native.evaluate("!document.getElementById('xy-compact-preview-style').disabled"), "An untrusted message changed compact toolbar visibility")
                point = native.evaluate("""()=>{
                    const view=__xyObservedViews[0],box=view.canvas.getBoundingClientRect(),ranges=view.view.ranges;
                    return {x:(2-ranges.x[0])/(ranges.x[1]-ranges.x[0])*box.width,
                            y:(ranges.y[1]-5)/(ranges.y[1]-ranges.y[0])*box.height};
                }""")
                canvas.hover(position=point)
                native.locator('[data-xy-slot="tooltip"]').wait_for(state="visible", timeout=10000)
                before = native.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                canvas.hover()
                page.mouse.wheel(0, -220)
                native.wait_for_function("before=>JSON.stringify(__xyObservedViews[0].view.ranges)!==JSON.stringify(before)", arg=before)
                zoomed = native.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                canvas.dblclick()
                native.wait_for_function("before=>JSON.stringify(__xyObservedViews[0].view.ranges)===JSON.stringify(before)", arg=before, timeout=10000)
                row["native_ranges"] = {"before": before, "zoomed": zoomed}
                row["checks"].append("compact_native_hover_wheel_and_double_click_reset")
                page.screenshot(path=args.output_dir / f"initial-desktop-{download_supported}.png")
                start_downloads = len(report["downloads"])
                widget.locator("#save-image").click()
                page.wait_for_timeout(100)
                require(len(report["downloads"]) == start_downloads + 1 and report["downloads"][-1]["suffix"] == ".png", "Primary action did not save PNG")
                more.focus()
                more.press("Tab")
                require(widget.evaluate("document.activeElement.id") not in {"palette-select", "view-select", "export-format", "download-format", "chart-tools"}, "Collapsed controls entered the tab order")
                more.focus()
                closed_trigger = more.bounding_box()
                more.press("Enter")
                require(panel.is_visible(), "Enter did not expand More options")
                require("expanded" in more.aria_snapshot(), "Disclosure expanded state is absent from accessibility tree")
                opened_trigger = more.bounding_box()
                require(all(abs(closed_trigger[key] - opened_trigger[key]) <= 1 for key in ["x", "y", "width", "height"]), "Opening options moved its trigger")
                row["disclosure_trigger"] = {"closed": closed_trigger, "opened": opened_trigger}
                previous_url = widget.locator("#chart").get_attribute("src")
                previous_png = initial["structuredContent"]["downloads"]["png"]
                widget.locator("#palette-select").select_option("colorset2")
                require(widget.locator("main").get_attribute("aria-busy") == "true", "Palette loading is not announced")
                require(widget.locator("#chart").get_attribute("src") == previous_url, "Pending update discarded the old native frame")
                require(widget.locator("#save-image").is_enabled(), "Pending update disabled saving the displayed chart")
                widget.locator("#save-image").click()
                page.wait_for_timeout(100)
                require(report["downloads"][-1]["url"].split("&download=", 1)[0] == previous_png, "Pending save selected an unshown chart")
                widget.wait_for_function("()=>document.querySelector('main').getAttribute('aria-busy')==='false'", timeout=100000)
                require(widget.locator("#palette-select").input_value() == "colorset2", "Explicit palette update failed")
                previous_url = widget.locator("#chart").get_attribute("src")
                page.evaluate("window.__failNextTool=true")
                widget.locator("#palette-select").select_option("colorset1")
                widget.locator("#error").wait_for(state="visible", timeout=10000)
                require(widget.locator("#chart").get_attribute("src") == previous_url, "Failed update discarded the previous chart")
                require(widget.locator("#palette-select").input_value() == "colorset2", "Failed palette selection does not match the displayed chart")
                require(widget.locator("#save-image").is_enabled(), "Failed update disabled saving the previous chart")
                widget.locator("#palette-select").select_option("colorset1")
                widget.wait_for_function("()=>document.querySelector('main').getAttribute('aria-busy')==='false'", timeout=100000)
                require(widget.locator("#palette-select").input_value() == "colorset1", "Retry did not restore Colorset 1")
                row["checks"].append("palette_loading_error_retry_and_previous_save_preservation")
                widget.locator("#view-select").select_option("svg")
                widget.wait_for_function("()=>document.getElementById('preview').complete&&document.getElementById('preview').naturalWidth>0")
                widget.locator("#view-select").focus()
                widget.locator("#view-select").press("Escape")
                require(not panel.is_visible(), "Escape did not close options")
                require(widget.evaluate("document.activeElement.id") == "more-summary", "Escape did not return focus to More options")
                require(widget.locator("#preview").is_visible(), "Closing options changed the selected image view")
                more.press("Space")
                require(panel.is_visible() and widget.locator("#view-select").input_value() == "svg", "Space/reopening lost disclosure or view state")
                widget.locator("#view-select").select_option("interactive")
                native = ready_native()
                canvas = native.evaluate_handle("__xyObservedViews[0].canvas").as_element()
                unzoomed = native.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                canvas.hover()
                page.mouse.wheel(0, -220)
                native.wait_for_function("before=>JSON.stringify(__xyObservedViews[0].view.ranges)!==JSON.stringify(before)", arg=unzoomed)
                toolbar_ranges = native.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                toolbar_url = widget.locator("#chart").get_attribute("src")
                widget.locator("#chart-tools").check()
                canvas.hover()
                native.wait_for_function("()=>[...document.querySelectorAll('[data-xy-slot=modebar]')].some(element=>getComputedStyle(element).display!=='none')")
                require(widget.locator("#chart").get_attribute("src") == toolbar_url, "Showing toolbar navigated the native frame")
                require(native.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))") == toolbar_ranges, "Showing toolbar reset the chart zoom")
                widget.locator("#chart-tools").uncheck()
                native.wait_for_function("()=>[...document.querySelectorAll('[data-xy-slot=modebar]')].every(element=>getComputedStyle(element).display==='none')")
                require(widget.locator("#chart").get_attribute("src") == toolbar_url, "Hiding toolbar navigated the native frame")
                require(native.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))") == toolbar_ranges, "Hiding toolbar reset the chart zoom")
                row["toolbar_toggle_ranges"] = toolbar_ranges
                for value in ["svg", "html", "source", "spec"]:
                    widget.locator("#export-format").select_option(value)
                    widget.locator("#download-format").click()
                    page.wait_for_timeout(70)
                required = {".png", ".svg", ".html", ".py", ".json"}
                require(required <= {item["suffix"] for item in report["downloads"]}, "An existing native export became inaccessible")
                row["checks"].append("keyboard_disclosure_retained_view_toolbar_and_all_five_exports")
                page.set_viewport_size({"width": 390, "height": 1000})
                native = ready_native()
                layout_expression = """()=>({viewport:innerWidth,viewportHeight:innerHeight,scroll:{x:scrollX,y:scrollY},root:document.querySelector('.xy')?.getBoundingClientRect().toJSON(),canvas:__xyObservedViews[0].canvas.getBoundingClientRect().toJSON(),canvases:[...document.querySelectorAll('canvas')].map(canvas=>({box:canvas.getBoundingClientRect().toJSON(),width:canvas.width,height:canvas.height,display:getComputedStyle(canvas).display})),viewWidth:__xyObservedViews[0].width,document:document.documentElement.scrollWidth,ranges:__xyObservedViews[0].view.ranges})"""
                row["mobile_layout_before_fit"] = native.evaluate(layout_expression)
                native.wait_for_function("()=>{const root=document.querySelector('.xy').getBoundingClientRect(),canvas=__xyObservedViews[0].canvas.getBoundingClientRect();return root.width>=innerWidth-2&&canvas.right<=innerWidth+1&&canvas.width>=innerWidth-120}", timeout=15000)
                page.wait_for_timeout(700)
                row["mobile_layout"] = native.evaluate(layout_expression)
                require(row["mobile_layout"]["root"]["width"] >= row["mobile_layout"]["viewport"] - 2,
                        "Native chart shrank after its initial responsive fit")
                targets = widget.locator("button,summary,select,label.check-label").evaluate_all("""elements=>elements.filter(element=>{
                    const box=element.getBoundingClientRect(),style=getComputedStyle(element);return box.width>0&&box.height>0&&style.display!=='none'&&style.visibility!=='hidden';
                }).map(element=>({id:element.id||element.textContent.trim(),width:element.getBoundingClientRect().width,height:element.getBoundingClientRect().height}))""")
                require(all(item["width"] >= 44 and item["height"] >= 44 for item in targets), "An authored mobile target is smaller than 44 pixels")
                require(widget.evaluate("document.documentElement.scrollWidth<=innerWidth+1"), "Outer widget overflows on mobile")
                row["mobile_targets"] = targets
                row["checks"].append("mobile_inner_chart_fit_and_authored_44px_targets")
                page.screenshot(path=args.output_dir / f"advanced-mobile-{download_supported}.png")
                row["mobile_after_capture"] = native.evaluate(layout_expression)
                page.wait_for_timeout(500)
                native.locator('.xy').screenshot(path=args.output_dir / f"native-mobile-{download_supported}.png")
                widget.locator("#export-format").focus()
                widget.locator("#export-format").press("Escape")
                page.wait_for_timeout(700)
                row["mobile_collapsed_layout"] = native.evaluate(layout_expression)
                row["mobile_widget_scroll"] = widget.evaluate("()=>({x:scrollX,y:scrollY,viewport:innerWidth,document:document.documentElement.scrollWidth,frame:document.getElementById('chart').getBoundingClientRect().toJSON()})")
                require(row["mobile_collapsed_layout"]["root"]["width"] >= row["mobile_collapsed_layout"]["viewport"] - 2,
                        "Collapsing options shrank the native chart")
                require(row["mobile_collapsed_layout"]["ranges"] == toolbar_ranges,
                        "Responsive disclosure change reset native zoom")
                row["parent_scroll_after_export_focus"] = page.evaluate("()=>({x:scrollX,y:scrollY})")
                # Focusing an export below the browser viewport can scroll the host
                # page. Return to the chart before a first-view visual capture.
                page.evaluate("window.scrollTo(0,0)")
                page.wait_for_timeout(500)
                page.screenshot(path=args.output_dir / f"simple-mobile-{download_supported}.png")
                row["mobile_collapsed_after_capture"] = native.evaluate(layout_expression)
                require(not row["errors"], "JavaScript error in the component or native chart")
                row["passed"] = True
            except Exception as error:
                row["passed"] = False
                row["failure"] = f"{type(error).__name__}: {error}"
                try:
                    row["widget_failure_state"] = widget.evaluate("""()=>{const frame=document.getElementById('chart');return {view:document.getElementById('view-select').value,frame:{src:frame.src,hidden:frame.hidden,pending:frame.dataset.pendingSrc,box:frame.getBoundingClientRect().toJSON(),display:getComputedStyle(frame).display}}}""")
                    actual = widget.locator("#chart").element_handle().content_frame()
                    row["native_failure_state"] = actual.evaluate("""()=>({url:location.href,viewport:innerWidth,root:document.querySelector('.xy')?.getBoundingClientRect().toJSON(),views:(window.__xyObservedViews??[]).map(view=>({canvas:view.canvas.getBoundingClientRect().toJSON(),connected:view.canvas.isConnected,display:getComputedStyle(view.canvas).display,ranges:view.view.ranges}))})""")
                except Exception as diagnostic_error:
                    row["diagnostic_error"] = str(diagnostic_error)
                page.screenshot(path=args.output_dir / f"failure-{download_supported}.png", full_page=True)
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
