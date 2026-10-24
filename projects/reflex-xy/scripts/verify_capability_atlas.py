#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["xy==0.0.8", "playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Independently audit the XY capability atlas, source ZIP, and real browser UI.

Use --pages-root projects/reflex-xy/artifacts --route capability-atlas for a
staging build, or defaults for the final Pages tree. --base-url accepts the
public Pages root. Browser instrumentation observes the actual ChartView returned
by renderStandalone; it never changes chart data, ranges, or input handlers.
"""
from __future__ import annotations

import argparse
import base64
import contextlib
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import importlib.metadata
import inspect
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile

import xy
from playwright.sync_api import sync_playwright

from verify_colorset_gallery import image_stats, inspect_svg, launch_browser, serve, normalized_color


def visible_label(page, label):
    return page.locator("body *:not(script):not(style)").evaluate_all("""(elements,label) => elements.some(element=>{
      const box=element.getBoundingClientRect(),style=getComputedStyle(element);
      return !element.children.length && element.textContent.includes(label) && box.width>0 && box.height>0 && style.display!=='none' && style.visibility!=='hidden' && Number(style.opacity)>0;
    })""", label)


OBSERVE_VIEWS = """window.__xyObservedViews=[];
Object.defineProperty(window,'xy',{configurable:true,set(library){
 const original=library.renderStandalone;
 library.renderStandalone=function(...args){const view=original.apply(this,args);window.__xyObservedViews.push(view);return view};
 Object.defineProperty(window,'xy',{value:library,writable:true,configurable:true});
}});"""

FOOTER_SLUGS={"scatter-encoding","line-gaps","stacked-area","grouped-bars","stacked-bars","normalized-bars","step-transitions","empirical-cdf","box-distributions","violin-distributions"}


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in {"a", "img", "link", "iframe"}:
            value = attrs.get("href") if tag in {"a", "link"} else attrs.get("src")
            if value and not value.startswith(("data:", "javascript:")):
                self.references.append(value)


def read_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "xy-capability-atlas-verifier/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def record_error(result, stage, message, **details):
    result["errors"].append({"stage": stage, "message": message, **details})


def inspect_api(gallery, result):
    api = json.loads((gallery / "api.json").read_text(encoding="utf-8"))
    expected = set(xy.__all__)
    actual = set(api["exports"])
    parameters = []
    for name in sorted(expected & actual):
        try:
            signature = inspect.signature(getattr(xy, name))
        except (TypeError, ValueError):
            continue
        names = [parameter.name for parameter in signature.parameters.values()
                 if not parameter.name.startswith("_") and parameter.name not in {"self", "cls"}]
        declared = [parameter["name"] for parameter in api["exports"][name].get("parameters", [])]
        if names != declared:
            parameters.append({"api": name, "installed": names, "catalogued": declared})
    parser = References()
    parser.feed((gallery / "api.html").read_text(encoding="utf-8"))
    result["api"] = {"count": len(actual), "expected_count": len(expected),
                     "missing": sorted(expected - actual), "extra": sorted(actual - expected),
                     "parameter_mismatches": parameters,
                     "missing_html_anchors": sorted(expected - parser.ids)}
    manifest_ids={row["id"] for row in json.loads((gallery/"manifest.json").read_text(encoding="utf-8"))["items"]}
    coverage=api.get("coverage",{})
    invalid_coverage=[]
    for name in sorted(expected):
        value=coverage.get(name)
        if not value or not value.get("coverage") or any(example not in manifest_ids for example in value.get("examples",[])):
            invalid_coverage.append(name)
    result["api"]["invalid_coverage"]=invalid_coverage
    if expected != actual or parameters or expected - parser.ids or invalid_coverage:
        record_error(result, "api", "The installed public API and catalogue differ.")
    return api


def inspect_assets(gallery, manifest, palettes, result):
    registry = json.loads((gallery / "source/patterns.json").read_text(encoding="utf-8"))
    expected = {row["id"] for row in registry["patterns"]}
    actual = [row["id"] for row in manifest["items"]]
    result["registry"] = {"expected": len(expected), "actual": len(actual),
                          "missing": sorted(expected - set(actual)), "extra": sorted(set(actual) - expected)}
    if set(actual) != expected or len(actual) != len(expected):
        record_error(result, "registry", "Manifest IDs do not uniquely equal the source registry.")
    groups = {}
    for item in manifest["items"]:
        try:
            svg = inspect_svg(gallery / item["svg"], palettes[item["colorset"]])
            transparent = [paint for paint in svg["unknown_paints"] if re.fullmatch(r"#[0-9a-f]{6}00", paint)]
            svg["transparent_paints"] = transparent
            svg["unknown_paints"] = [paint for paint in svg["unknown_paints"] if paint not in transparent]
            row = {"id": item["id"], "scope": item["paint_scope"], **svg}
            result["svg"].append(row)
            if svg["pattern_id"] != item["id"] or svg["colorset"] != item["colorset"]:
                record_error(result, "svg-metadata", "SVG identity differs from the manifest.", id=item["id"])
            if item["paint_scope"] == "exact" and svg["unknown_paints"]:
                record_error(result, "svg-paint", "Exact-paint SVG contains undeclared colors.", id=item["id"], paints=svg["unknown_paints"])
            if item["paint_scope"] not in {"exact", "derived"}:
                record_error(result, "svg-scope", "Unknown paint scope.", id=item["id"])
            if item.get("svg_compat_repairs",0):
                original=gallery/item["original_svg_text"]
                row["original_svg_bytes"]=original.stat().st_size
                row["original_svg_sha256"]=hashlib.sha256(original.read_bytes()).hexdigest()
            png = image_stats((gallery / item["png"]).read_bytes(), palettes[item["colorset"]])
            result["png"].append({"id": item["id"], **png})
            expected_png = (item.get("png_width", item["width"]), item.get("png_height", item["height"]))
            if not png["nonblank"] or (png["width"], png["height"]) != expected_png:
                record_error(result, "png", "Native PNG is blank or has incorrect dimensions.", id=item["id"])
            groups.setdefault(item["slug"], []).append(row)
        except Exception as error:
            record_error(result, "asset", str(error), id=item["id"])
    for slug, pair in groups.items():
        same = len(pair) == 2 and pair[0]["geometry_sha256"] == pair[1]["geometry_sha256"]
        result["paired_geometry"].append({"slug": slug, "same_geometry_and_text": same})
        if not same:
            record_error(result, "paired-geometry", "Palette variants change geometry or text.", slug=slug)


def inspect_links(gallery, root, route, base_url, result):
    documents = {}
    for name in ("index.html", "api.html", "hosts.html"):
        parser = References()
        parser.feed((gallery / name).read_text(encoding="utf-8"))
        documents[name] = parser
    checked = set()
    for name, parser in documents.items():
        for reference in parser.references:
            if reference.startswith(("http://", "https://")):
                url = urllib.parse.urldefrag(reference)[0]
                if url in checked:
                    continue
                checked.add(url)
                try:
                    read_url(url)
                    result["links"].append({"url": url, "exists": True, "external": True})
                except Exception as error:
                    result["links"].append({"url": url, "exists": False, "error": str(error)})
                continue
            parsed = urllib.parse.urlsplit(reference)
            target = (gallery / parsed.path).resolve() if parsed.path else gallery / name
            if target.is_dir():
                target /= "index.html"
            key = str(target) + "#" + parsed.fragment
            if key in checked:
                continue
            checked.add(key)
            exists = target.is_file()
            cached_public = base_url and target.is_relative_to(gallery) and target.relative_to(gallery).as_posix() in result.get("public_downloaded_assets", [])
            if cached_public:
                # These bytes were freshly fetched with a successful HTTP
                # response in this same run; reuse them for fragment checks.
                data = target.read_bytes() if target.suffix == ".html" else b""
            elif base_url:
                url = urllib.parse.urljoin(base_url, route.strip("/") + "/" + name)
                url = urllib.parse.urljoin(url, reference)
                try:
                    data = read_url(urllib.parse.urldefrag(url)[0])
                    exists = True
                except Exception as error:
                    exists = False
                    data = b""
            elif exists:
                data = target.read_bytes() if target.suffix == ".html" else b""
            else:
                data = b""
            if parsed.fragment and target.suffix == ".html" and exists:
                linked = References()
                linked.feed(data.decode("utf-8"))
                exists = urllib.parse.unquote(parsed.fragment) in linked.ids
            result["links"].append({"reference": reference, "document": name, "exists": exists})
    broken = [row for row in result["links"] if not row["exists"]]
    if broken:
        record_error(result, "links", "Atlas contains broken assets, source links, or API anchors.", count=len(broken))


def inspect_hosts(gallery, result):
    host = json.loads((gallery / "host-report.json").read_text(encoding="utf-8"))
    valid_formats = {"png", "jpeg", "webp", "svg", "pdf", "html"}
    formats = {row["format"] for row in host["exports"]}
    honest = host["core"]["live_frontend_acknowledgement_tested"] is False and host["reflex"]["frontend_callback_delivery_tested"] is False
    result["host"] = {"passed": host["passed"], "formats": sorted(formats),
                      "selection_count": host["core"]["selection"]["count"],
                      "reflex_status": host["reflex"]["status"], "frontend_scope_honest": honest}
    if not host["passed"] or formats != valid_formats or not honest or host["core"]["selection"]["count"] != 2:
        record_error(result, "hosts", "Host report failed or confuses compile/construction with frontend delivery.")
    directory = gallery / "host-artifacts"
    for row in host["exports"]:
        path = directory / row["path"]
        if path.stat().st_size != row["bytes"]:
            record_error(result, "host-export", "Export byte count differs from report.", path=row["path"])
    before = (directory / "before-append.html").read_text(encoding="utf-8")
    after = (directory / "after-append.html").read_text(encoding="utf-8")
    if before == after or not (directory / "reflex-example/pyproject.toml").is_file():
        record_error(result, "host-source", "Streaming snapshots or portable Reflex app source are missing.")
    data=json.loads((gallery/"data-report.json").read_text(encoding="utf-8"))
    data_passed=data["passed"] and data["ingest"]["shared_float64_storage"] and data["ingest"]["identity_deduplication"] and data["registry"]["initial_registry_restored"] and not data["structural_probe"]["rendered"]
    result["data_tools"]={"passed":data_passed,"apis":data["apis"],"optional_dataframes_status":data["optional_dataframes"]["status"],"structural_probe_scope":data["structural_probe"]["scope"]}
    if not data_passed:
        record_error(result,"data-tools","Column/registry report failed or overstates rendering scope.")


def inspect_portable(gallery, output, result):
    destination = output / "portable-source"
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(gallery / "source.zip") as archive:
        files = archive.namelist()
        for name in files:
            target = (destination / name).resolve()
            if not target.is_relative_to(destination) or Path(name).is_absolute():
                raise ValueError(f"Unsafe source ZIP entry: {name}")
        archive.extractall(destination)
    manifest = json.loads((gallery / "manifest.json").read_text(encoding="utf-8"))
    source_identity = {name: (destination / name).read_bytes() == (gallery / "source" / name).read_bytes() for name in manifest["source_files"] if (destination / name).is_file()}
    required = {"build.py", "advanced.py", "core_marks.py", "polar_annotations.py", "utilities.py", "host_examples.py", "xy_colorsets.py", "xy_svg_compat.py", "colorsets.json", "patterns.json", "gallery.html", "atlas.css"}
    missing = sorted(required - set(files))
    missing.extend(sorted(set(manifest["source_files"]) - set(files)))
    result["portable"] = {"zip_files": files, "missing": missing, "source_identity": source_identity}
    if not all(source_identity.values()):
        record_error(result, "portable", "Source ZIP bytes differ from the adjacent downloadable sources.")
    if missing:
        record_error(result, "portable", "Source ZIP is not a complete standalone bundle.", missing=missing)
        return
    target = output / "portable-gallery"
    process = subprocess.run([sys.executable, str(destination / "build.py"), "--output-dir", str(target)],
                             cwd=destination, capture_output=True, text=True, timeout=240)
    (output / "portable-build.log").write_text(process.stdout + "\n" + process.stderr, encoding="utf-8")
    result["portable"]["returncode"] = process.returncode
    if process.returncode:
        record_error(result, "portable", "Source-only rebuild failed; inspect portable-build.log.")
        return
    rebuilt = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    original = json.loads((gallery / "manifest.json").read_text(encoding="utf-8"))
    result["portable"]["matching_ids"] = {row["id"] for row in rebuilt["items"]} == {row["id"] for row in original["items"]}
    if not result["portable"]["matching_ids"]:
        record_error(result, "portable", "Rebuilt source bundle changes the mechanism registry.")


def ranges(page):
    return page.evaluate("() => __xyObservedViews.map(view => JSON.parse(JSON.stringify(view.view.ranges)))")


def chart_canvases(page):
    page.wait_for_selector("canvas", state="visible", timeout=45000)
    page.wait_for_function("()=>window.__xyObservedViews && __xyObservedViews.length > 0", timeout=15000)
    count = page.evaluate("window.__xyObservedViews.length")
    return [page.evaluate_handle("index=>__xyObservedViews[index].canvas", index).as_element() for index in range(count)]


def chart_point(page, index=0, x=0.5, y=0.5):
    return page.evaluate("""({index,x,y}) => {
        const box=__xyObservedViews[index].canvas.getBoundingClientRect();
        return {x:box.left+box.width*x,y:box.top+box.height*y};
    }""", {"index": index, "x": x, "y": y})


def layout_features(page, item, result):
    slug = item["slug"]
    if slug in FOOTER_SLUGS:
        layout=page.evaluate("()=>({viewport:innerWidth,plot:__xyObservedViews[0].canvas.getBoundingClientRect().toJSON(),legend:[...document.querySelectorAll('[data-xy-slot=legend]')].map(e=>e.getBoundingClientRect().toJSON()),titles:[...document.querySelectorAll('[data-xy-slot=axis_title]')].map(e=>e.getBoundingClientRect().toJSON())})")
        passed=len(layout['legend'])==1 and layout['legend'][0]['top']>=layout['plot']['bottom']+45 and layout['legend'][0]['bottom']<=item['height'] and layout['legend'][0]['right']<=layout['viewport'] and all(t['bottom']+4<=layout['legend'][0]['top'] for t in layout['titles'])
        result['features'].append({'id':item['id'],'viewport_width':layout['viewport'],'feature':'reserved footer legend clears marks and axis labels','passed':passed,'layout':layout})
    if slug == "sankey-flow":
        labels=page.locator('body *:not(script):not(style)').evaluate_all("es=>es.filter(e=>!e.children.length&&['Input','Lab','Field','Output','Loss'].includes(e.textContent.trim())).map(e=>({text:e.textContent.trim(),color:getComputedStyle(e).color,box:e.getBoundingClientRect().toJSON()}))")
        passed=len(labels)==5 and all(row['color']=='rgb(255, 255, 255)' for row in labels)
        result['features'].append({'id':item['id'],'viewport_width':page.viewport_size['width'],'feature':'Sankey all five labels use readable white text','labels':labels,'passed':passed})


def target_features(page, item, result, allowed, output):
    layout_features(page,item,result)
    slug=item['slug']
    if slug == "navigation-x-only":
        before = ranges(page)
        point = chart_point(page)
        page.mouse.move(point["x"], point["y"])
        page.mouse.wheel(0, -220)
        page.wait_for_timeout(220)
        after = ranges(page)
        passed = before[0]["x"] != after[0]["x"] and before[0]["y"] == after[0]["y"]
        history = page.evaluate("__xyObservedViews[0]._historyPast.length")
        page.get_by_role("button", name=re.compile("^Zoom controls")).click()
        page.locator('button[title="Back to previous view"]').click()
        page.wait_for_function("()=>__xyObservedViews.every(view=>view._viewAnim===null)", timeout=5000)
        back = ranges(page)
        page.locator('button[title="Go to next view"]').click()
        page.wait_for_function("()=>__xyObservedViews.every(view=>view._viewAnim===null)", timeout=5000)
        forward = ranges(page)
        page.locator("button").filter(has_text=re.compile("^Reset View$")).click()
        page.wait_for_function("()=>__xyObservedViews.every(view=>view._viewAnim===null)", timeout=5000)
        reset = ranges(page)
        result["features"].append({"id": item["id"], "feature": "x-only wheel navigation, actual back/forward/reset controls", "before": before, "after": after, "history_entries": history, "back": back, "forward": forward, "reset": reset, "passed": passed and history > 0 and back == before and forward == after and reset == before})
    elif slug == "layout-facets-linked":
        before = ranges(page)
        point = chart_point(page)
        page.mouse.move(point["x"], point["y"])
        page.mouse.wheel(0, -220)
        page.wait_for_timeout(250)
        after = ranges(page)
        passed = len(after) == 3 and before[0]["x"] != after[0]["x"] and all(row["x"] == after[0]["x"] for row in after)
        title_color = page.locator(".xy-facet-title").evaluate("element=>getComputedStyle(element).color")
        result["features"].append({"id": item["id"], "feature": "same-document linked facet x ranges", "before": before, "after": after, "title_color": title_color, "passed": passed and normalized_color(title_color) in allowed})
    elif slug == "controls-minimal":
        before = ranges(page)
        point = chart_point(page)
        page.mouse.move(point["x"], point["y"])
        page.mouse.wheel(0, -180)
        page.wait_for_timeout(100)
        after = ranges(page)
        toolbar = page.locator('[data-xy-slot="modebar"]:visible').count()
        result["features"].append({"id": item["id"], "feature": "disabled navigation and hidden modebar", "passed": before == after and toolbar == 0})
    elif slug == "selection-box-lasso":
        point = chart_point(page)
        page.mouse.move(point["x"], point["y"])
        page.wait_for_timeout(150)
        tooltip = page.locator('[data-xy-slot="tooltip"]')
        tooltip_text = tooltip.inner_text() if tooltip.count() and tooltip.is_visible() else ""
        points = [chart_point(page, x=x, y=y) for x, y in ((.18,.18),(.75,.18),(.75,.75),(.18,.75),(.18,.18))]
        page.mouse.move(**points[0])
        page.mouse.down()
        for value in points[1:]:
            page.mouse.move(**value, steps=8)
        page.mouse.up()
        page.wait_for_timeout(150)
        selection = page.evaluate("__xyObservedViews[0]._stateSelection")
        page.get_by_role("button", name=re.compile("^Selection controls")).click()
        page.locator("button").filter(has_text=re.compile("^Box Select$")).click()
        start,end=chart_point(page,x=.2,y=.2),chart_point(page,x=.7,y=.7)
        page.mouse.move(**start)
        page.mouse.down()
        page.mouse.move(**end,steps=15)
        page.mouse.up()
        page.wait_for_timeout(150)
        boxed=page.evaluate("__xyObservedViews[0]._stateSelection")
        result["features"].append({"id": item["id"], "feature": "real lasso/box gestures, mode switch, and formatted hover", "lasso": selection, "box": boxed, "tooltip": tooltip_text, "passed": bool(selection) and bool(boxed) and selection != boxed and "Column" in tooltip_text and "Row" in tooltip_text})
    elif slug == "axes-category-labels":
        rectangles=page.locator('[data-xy-slot="axis_title"], [data-xy-slot="tick_label"]').evaluate_all("elements=>elements.map(e=>({text:e.textContent,box:e.getBoundingClientRect().toJSON()}))")
        title=next(row["box"] for row in rectangles if row["text"]=="Study group")
        ticks=[row["box"] for row in rectangles if row["text"] in {"Control","Treatment A","Treatment B","Follow-up"}]
        passed=len(ticks)==4 and all(row["bottom"]+4<=title["top"] for row in ticks)
        result["features"].append({"id":item["id"],"feature":"rotated category ticks clear the axis title","passed":passed,"title_top":title["top"],"tick_bottom":max(row["bottom"] for row in ticks)})
    elif slug == "scatter-encoding":
        page.get_by_role("button", name="Export options", exact=True).click()
        with page.expect_download(timeout=15000) as download_info:
            page.locator("button").filter(has_text=re.compile("^Export CSV$")).click()
        download=download_info.value
        target=output/"downloads"/(item["id"]+".csv")
        target.parent.mkdir(exist_ok=True)
        download.save_as(target)
        text=target.read_text(encoding="utf-8-sig")
        result["features"].append({"id":item["id"],"feature":"actual browser CSV export","bytes":target.stat().st_size,"header":text.splitlines()[0],"passed":len(text.splitlines())>10})


def browser_audit(root, route, public_base, manifest, output, result, palettes, only=None):
    context_manager = contextlib.nullcontext(public_base) if public_base else serve(root)
    with context_manager as base, sync_playwright() as playwright:
        browser = launch_browser(playwright, result)
        try:
            context = browser.new_context(viewport={"width": 1280, "height": 960}, device_scale_factor=1, reduced_motion="no-preference")
            context.add_init_script(OBSERVE_VIEWS)

            def request_filter(request_route):
                url = request_route.request.url
                if url.startswith(("http://", "https://")) and not url.startswith(base):
                    result["external_browser_requests"].append(url)
                    request_route.abort()
                else:
                    request_route.continue_()

            context.route("**/*", request_filter)

            def attach(page):
                page.on("console", lambda message: result["console_errors"].append(message.text) if message.type == "error" else None)
                page.on("pageerror", lambda error: result["page_errors"].append(str(error)))

            gallery_url = urllib.parse.urljoin(base, route.strip("/") + "/")
            page = context.new_page()
            attach(page)
            page.goto(gallery_url, wait_until="load", timeout=45000)
            ids = page.locator("article[data-pattern-id]").evaluate_all("elements=>elements.map(element=>element.dataset.patternId)")
            if set(ids) != {row["id"] for row in manifest["items"]} or len(ids) != len(manifest["items"]):
                record_error(result, "gallery-dom", "Gallery DOM differs from the manifest IDs.")
            for viewport_name, viewport in (("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})):
                page.set_viewport_size(viewport)
                for palette in ("all", "colorset1", "colorset2"):
                    page.locator(f'button[data-palette="{palette}"]').click()
                    visible = page.locator("article[data-pattern-id]:visible").count()
                    expected = len(ids) if palette == "all" else len(ids) // 2
                    overflow = page.evaluate("({width:innerWidth,scroll:document.documentElement.scrollWidth})")
                    result["gallery_filters"].append({"viewport": viewport_name, "palette": palette, "visible": visible, "expected": expected, "passed": visible == expected and overflow["scroll"] <= overflow["width"] + 1})
                page.locator("#search").fill("no-such-xy-capability-9837")
                empty_passed = page.locator("#empty").is_visible() and page.locator("article[data-pattern-id]:visible").count() == 0
                result["gallery_filters"].append({"viewport": viewport_name, "state": "empty search", "passed": empty_passed})
                page.locator("#search").fill("symlog")
                count = page.locator("article[data-pattern-id]:visible").count()
                result["gallery_filters"].append({"viewport": viewport_name, "state": "API search", "passed": count > 0})
                page.locator("#search").fill("")
                page.locator('button[data-palette="all"]').click()
                category = page.locator("#category option").nth(1).get_attribute("value")
                page.locator("#category").select_option(category)
                visible_categories = page.locator("section.family:visible").count()
                result["gallery_filters"].append({"viewport": viewport_name, "state": "category", "passed": visible_categories == 1})
                page.locator("#category").select_option("all")
                page.evaluate("scrollTo({top:0,behavior:'instant'})")
                page.screenshot(path=str(output / f"atlas-{viewport_name}.png"), full_page=False)
            for identifier in ("xy-scatter-encoding-cs1", "xy-axes-secondary-cs2"):
                page.locator(f'article[id="{identifier}"] [data-explore]').click()
                iframe = page.locator("iframe")
                iframe.wait_for(state="visible", timeout=15000)
                frame = iframe.element_handle().content_frame()
                frame.wait_for_selector("canvas", state="visible", timeout=45000)
                result["explore"].append({"id": identifier, "count": iframe.count(), "passed": iframe.count() == 1})
            page.close()
            api_page=context.new_page()
            attach(api_page)
            api_page.goto(urllib.parse.urljoin(gallery_url,"api.html"),wait_until="load")
            api_page.locator("#api-search").fill("scatter")
            found=api_page.locator("article.api-entry:visible").count()
            api_page.locator("#api-search").fill("no-such-xy-api-9837")
            empty=api_page.locator("article.api-entry:visible").count()
            result["features"].append({"feature":"public API catalogue search","matches":found,"empty_matches":empty,"passed":0<found<105 and empty==0})
            api_page.close()
            selected_items=[item for item in manifest["items"] if not only or item["slug"] in only]
            result["selected_browser_items"]=[item["id"] for item in selected_items]
            for viewport_name, viewport in (("desktop", {"width": 1280, "height": 960}), ("mobile", {"width": 390, "height": 844})):
                for index, item in enumerate(selected_items):
                    chart_page = context.new_page()
                    attach(chart_page)
                    chart_page.set_viewport_size(viewport)
                    try:
                        chart_page.goto(urllib.parse.urljoin(gallery_url, item["html"]), wait_until="load", timeout=45000)
                        canvases = chart_canvases(chart_page)
                        early_animation = canvases[0].screenshot(type="png") if item["slug"] == "animation-reveal" and viewport_name == "desktop" else None
                        chart_page.wait_for_timeout(180 if item["slug"] != "animation-reveal" else 1200)
                        stats = [image_stats(canvas.screenshot(type="png")) for canvas in canvases if canvas.is_visible()]
                        for value in stats:
                            # A solid exact-color area can legitimately have only two
                            # WebGL plot colors. Axes live in separate DOM layers.
                            value["nonblank"] = value["width"] >= 100 and value["height"] >= 100 and max(value["stddev"]) >= 3 and value["distinct_colors"] >= 2
                        labels = {label: visible_label(chart_page, label) for label in item["expect_labels"]}
                        overflow = chart_page.evaluate("({viewport:innerWidth,scroll:document.documentElement.scrollWidth})")
                        outside = chart_page.locator("[data-xy-slot]").evaluate_all("""elements=>elements.filter(element=>{const b=element.getBoundingClientRect(),s=getComputedStyle(element);return !element.children.length&&element.textContent.trim()&&b.width>1&&b.height>1&&s.display!=='none'&&s.visibility==='visible'&&Number(s.opacity)>0&&(b.top< -1||b.left< -1||b.right>innerWidth+1)}).map(element=>({slot:element.dataset.xySlot,text:element.textContent,bounds:element.getBoundingClientRect().toJSON()}))""")
                        fixed_facet = item["interaction"] == "facet"
                        row = {"id": item["id"], "viewport": viewport_name, "canvases": stats,
                               "labels": labels, "overflow": overflow, "outside_text": outside,
                               "fixed_facet_scroll": fixed_facet,
                               "passed": bool(stats) and all(value["nonblank"] for value in stats) and all(labels.values()) and (fixed_facet or (overflow["scroll"] <= overflow["viewport"] + 1 and not outside))}
                        if viewport_name == "desktop":
                            if early_animation is not None:
                                final_animation = canvases[0].screenshot(type="png")
                                result["features"].append({"id": item["id"], "feature": "entrance animation changes real plot pixels", "early_sha256": hashlib.sha256(early_animation).hexdigest(), "final_sha256": hashlib.sha256(final_animation).hexdigest(), "passed": early_animation != final_animation})
                            target_features(chart_page, item, result, palettes[item["colorset"]], output)
                            if item["interaction"] == "cartesian" and item["slug"] not in {"navigation-x-only", "selection-box-lasso"}:
                                before = ranges(chart_page)
                                point = chart_point(chart_page)
                                chart_page.mouse.move(**point)
                                chart_page.mouse.wheel(0, -160)
                                chart_page.wait_for_timeout(150)
                                row["wheel_changes_ranges"] = ranges(chart_page) != before
                                if not row["wheel_changes_ranges"]:
                                    row["passed"] = False
                        elif item['slug'] in FOOTER_SLUGS or item['slug']=='sankey-flow':
                            # Only the layout/contrast assertions run on mobile;
                            # avoid replaying desktop export/control probes.
                            layout_features(chart_page,item,result)
                        screenshot = output / "screenshots" / f'{viewport_name}-{item["id"]}.png'
                        screenshot.parent.mkdir(parents=True, exist_ok=True)
                        chart_page.screenshot(path=str(screenshot), full_page=True)
                        row["screenshot"] = str(screenshot)
                        result["charts"].append(row)
                    except Exception as error:
                        result["charts"].append({"id": item["id"], "viewport": viewport_name, "passed": False, "error": str(error)})
                    finally:
                        chart_page.close()
                    if (index + 1) % 10 == 0:
                        print(f"Verified {viewport_name}: {index + 1}/{len(selected_items)}", flush=True)
                        (output / "checkpoint.json").write_text(json.dumps({"charts": result["charts"], "features": result["features"]}, indent=2), encoding="utf-8")
            context.close()
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages-root", type=Path, default=Path("dist/pages"))
    parser.add_argument("--route", default="examples/reflex-xy-capabilities")
    parser.add_argument("--base-url")
    parser.add_argument("--output-dir", type=Path, default=Path("projects/reflex-xy/artifacts/capability-atlas-review"))
    parser.add_argument("--skip-portable", action="store_true", help="Use only after a prior unchanged source ZIP rebuild already passed.")
    parser.add_argument("--only", help="Comma-separated semantic slugs for a focused browser recheck; native, links, API, host, and source gates remain complete.")
    args = parser.parse_args()
    root = args.pages_root.resolve()
    gallery = root / args.route
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "passed": False, "errors": [], "svg": [], "png": [], "paired_geometry": [], "links": [],
              "browser_launch_attempts": [], "console_errors": [], "page_errors": [], "external_browser_requests": [],
              "gallery_filters": [], "explore": [], "charts": [], "features": []}
    try:
        if importlib.metadata.version("xy") != "0.0.8":
            raise ValueError("Use the declared xy==0.0.8 environment for this audit.")
        if args.base_url:
            public = args.base_url.rstrip("/") + "/"
            url = urllib.parse.urljoin(public, args.route.strip("/") + "/")
            gallery = output / "public-assets"
            gallery.mkdir(parents=True, exist_ok=True)
            manifest_bytes = read_url(url + "manifest.json")
            (gallery / "manifest.json").write_bytes(manifest_bytes)
            manifest = json.loads(manifest_bytes)
            paths = {"index.html", "api.html", "api.json", "hosts.html", "host-report.json", "data-report.json", "source.zip", "atlas.css"}
            paths.update("source/" + name for name in manifest["source_files"])
            paths.update(row[key] for row in manifest["items"] for key in ("svg", "png", "html"))
            paths.update(row["original_svg_text"] for row in manifest["items"] if row.get("original_svg_text"))
            paths.update(manifest.get("export_samples",[]))
            host = json.loads(read_url(url + "host-report.json"))
            paths.update("host-artifacts/" + path for path in host["artifacts"])
            def download_asset(relative):
                path = (gallery / relative).resolve()
                if not path.is_relative_to(gallery):
                    raise ValueError(f"Public asset path escapes output: {relative}")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(read_url(urllib.parse.urljoin(url, relative)))
                return relative
            with ThreadPoolExecutor(max_workers=8) as pool:
                for count,relative in enumerate(pool.map(download_asset,sorted(paths)),1):
                    if count%40==0:
                        print(f'Downloaded public assets: {count}/{len(paths)}',flush=True)
            result["public_downloaded_assets"]=sorted(paths)
            local_manifest = json.loads((root / args.route / "manifest.json").read_text(encoding="utf-8"))
            result["public_manifest_matches_local"] = manifest == local_manifest
            if not result["public_manifest_matches_local"]:
                record_error(result, "public-manifest", "Published manifest differs from the verified local release.")
            identity={}
            for name in manifest["source_files"]:
                local=(root/args.route/"source"/name).read_bytes()
                remote=(gallery/"source"/name).read_bytes()
                identity[name]={"byte_identical":local==remote,"lf_normalized_identical":local.replace(b"\r\n",b"\n")==remote.replace(b"\r\n",b"\n"),"public_sha256":hashlib.sha256(remote).hexdigest()}
            result["public_source_identity"]=identity
            if any(not row["lf_normalized_identical"] for row in identity.values()):
                record_error(result,"public-source","Published portable source differs from the verified release beyond line endings.")
        else:
            public = None
            manifest = json.loads((gallery / "manifest.json").read_text(encoding="utf-8"))
        palette_document = json.loads((Path(__file__).resolve().parents[3] / "docs/colorsets.json").read_text(encoding="utf-8"))
        palettes = {name: set(value["allowed"]) for name, value in palette_document["colorsets"].items()}
        result["manifest_count"] = len(manifest["items"])
        published_palette = json.loads((gallery / "source/colorsets.json").read_text(encoding="utf-8"))
        if published_palette != palette_document:
            record_error(result, "palette", "Portable palette snapshot differs from the canonical contract.")
        inspect_assets(gallery, manifest, palettes, result)
        inspect_api(gallery, result)
        inspect_links(gallery, root, args.route, public, result)
        inspect_hosts(gallery, result)
        if not args.skip_portable:
            inspect_portable(gallery, output, result)
        selected=set(args.only.split(",")) if args.only else None
        if selected and not selected.issubset({item["slug"] for item in manifest["items"]}):
            raise ValueError("The browser case filter contains unknown semantic slugs.")
        browser_audit(root, args.route, public, manifest, output, result, palettes, selected)
        bad_charts = [row for row in result["charts"] if not row["passed"]]
        bad_features = [row for row in result["features"] if not row["passed"]]
        if bad_charts:
            record_error(result, "browser-charts", "Chart rendering, labels, interaction, or mobile bounds failed.", count=len(bad_charts))
        if bad_features:
            record_error(result, "browser-features", "A targeted client mechanism failed.", count=len(bad_features))
        if any(not row["passed"] for row in result["gallery_filters"] + result["explore"]):
            record_error(result, "gallery-ui", "A filter, search, category, or Explore state failed.")
        if result["console_errors"] or result["page_errors"] or result["external_browser_requests"]:
            record_error(result, "browser-runtime", "The browser reported errors or attempted external requests.")
    except Exception as error:
        record_error(result, "execution", str(error))
    result["passed"] = not result["errors"]
    report = output / "atlas-verification.json"
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "charts": len(result["charts"]), "svg": len(result["svg"]), "errors": result["errors"], "report": str(report)}))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
