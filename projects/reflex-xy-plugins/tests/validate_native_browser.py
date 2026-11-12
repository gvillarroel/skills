#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Inspect actual exported XY HTML offline with native wheel and reset controls."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import re
import threading
import urllib.parse

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

from artifact_contract import require


OBSERVE = """window.__xyObservedViews=[];
Object.defineProperty(window,'xy',{configurable:true,set(library){
 const original=library.renderStandalone;
 library.renderStandalone=function(...args){const view=original.apply(this,args);window.__xyObservedViews.push(view);return view};
 Object.defineProperty(window,'xy',{value:library,writable:true,configurable:true});
}});"""


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@contextmanager
def serve(root: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--cases", default="line-colorset1,line-colorset2,scatter-colorset1,scatter-colorset2,literal-untrusted-title")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"passed": False, "cases": [], "browser_attempts": [], "live_host_installation": "not_tested"}
    with serve(args.artifact_root.resolve()) as base, sync_playwright() as playwright:
        browser = None
        for options in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
            try:
                browser = playwright.chromium.launch(headless=True, chromium_sandbox=True, **options)
                report["browser"] = options.get("channel", "bundled chromium")
                break
            except Exception as error:
                report["browser_attempts"].append(str(error).splitlines()[0])
        require(browser, "No Chromium browser is available")
        for name in args.cases.split(","):
            for width in [1200, 390]:
                row = {"case": name, "viewport_width": width, "errors": [], "external_requests": []}
                context = browser.new_context(viewport={"width": width, "height": 900})
                context.add_init_script(OBSERVE)
                page = context.new_page()
                page.on("pageerror", lambda error: row["errors"].append(str(error)))
                def route(request_route):
                    url = request_route.request.url
                    if urllib.parse.urlsplit(url).scheme in {"http", "https"} and not url.startswith(base):
                        row["external_requests"].append(url)
                        request_route.abort()
                    else:
                        request_route.continue_()
                context.route("**/*", route)
                try:
                    page.goto(base + name + "/chart.html", wait_until="networkidle")
                    page.wait_for_function("()=>window.__xyObservedViews?.length>0", timeout=30000)
                    require(page.evaluate("!globalThis.__xyInjected"), "Untrusted chart title executed JavaScript")
                    canvas = page.evaluate_handle("__xyObservedViews[0].canvas").as_element()
                    page.wait_for_timeout(200)
                    image = Image.open(io.BytesIO(canvas.screenshot(type="png"))).convert("RGB")
                    statistics = ImageStat.Stat(image)
                    row["chart_paint"] = {"width": image.width, "height": image.height,
                        "standard_deviation": statistics.stddev,
                        "distinct_colors": len(Counter(image.get_flattened_data()))}
                    require(max(statistics.stddev) > 3 and row["chart_paint"]["distinct_colors"] >= 10, "Rendered chart is blank")
                    before = page.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                    box = canvas.bounding_box()
                    page.mouse.move(box["x"] + box["width"] * .5, box["y"] + box["height"] * .5)
                    page.mouse.wheel(0, -220)
                    page.wait_for_timeout(350)
                    after = page.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                    require(before != after, "Native wheel zoom did not change chart ranges")
                    page.get_by_role("button", name=re.compile("^Zoom controls")).click()
                    page.locator("button").filter(has_text=re.compile("^Reset View$")).click()
                    page.wait_for_function("()=>__xyObservedViews.every(view=>view._viewAnim===null)", timeout=5000)
                    reset = page.evaluate("JSON.parse(JSON.stringify(__xyObservedViews[0].view.ranges))")
                    require(reset == before, "Native reset control did not restore the initial ranges")
                    row["ranges"] = {"before": before, "zoomed": after, "reset": reset}
                    require(not row["errors"], "JavaScript error in actual XY HTML")
                    require(not row["external_requests"], "Standalone chart attempted external requests")
                    page.screenshot(path=args.output_dir / f"{name}-{width}.png", full_page=True)
                    row["passed"] = True
                except Exception as error:
                    row["passed"] = False
                    row["failure"] = f"{type(error).__name__}: {error}"
                report["cases"].append(row)
                context.close()
                print(json.dumps({key: row[key] for key in ["case", "viewport_width", "passed"]}), flush=True)
        browser.close()
    report["passed"] = all(row["passed"] for row in report["cases"])
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "cases": len(report["cases"])}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
