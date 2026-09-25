#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Verify pixel ownership, text-free exports, and actual offline interactions."""

import argparse
import json
import math
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright


def connected(points):
    points = set(points)
    visited, frontier = set(), [next(iter(points))]
    while frontier:
        x,y = frontier.pop()
        if (x,y) in visited:
            continue
        visited.add((x,y))
        frontier.extend(p for p in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)] if p in points and p not in visited)
    return len(visited) == len(points)


def audit(path, screenshot=None):
    checks, errors, network, evidence = [], [], [], []

    def check(name, condition, detail=None):
        checks.append({"check": name, "ok": bool(condition), **({"detail": detail} if detail is not None else {})})

    def capture(page, suffix=""):
        if screenshot:
            output = screenshot.with_name(screenshot.stem + suffix + screenshot.suffix)
            output.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(output), full_page=True)
            evidence.append(str(output))

    started = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1400, "height": 1100}, reduced_motion="reduce")
        context.route("http://**/*", lambda route: route.abort())
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("request", lambda r: network.append(r.url) if r.url.startswith(("http:", "https:")) else None)
        page.goto(path.resolve().as_uri())
        page.wait_for_function("document.documentElement.dataset.ready === 'true'")
        data = json.loads(page.locator("#hierarchy-data").text_content())
        nodes, grid = data["nodes"], data["pixels"]
        size = grid["size"]
        organic = grid.get("mode") == "organic"
        snapshot = lambda: page.evaluate("hierarchyPixels.snapshot()")
        image = lambda: page.locator("#art").evaluate("c=>c.toDataURL()")
        original = snapshot()
        owner_map = page.evaluate("JSON.stringify(JSON.parse(document.querySelector('#hierarchy-data').textContent).pixels)")
        counts, first = [0] * len(nodes), {}
        correct, nonoverlap = True, True
        for y, row in enumerate(grid["rows"]):
            end = 0
            for x, width, owner in row:
                nonoverlap &= x >= end and width > 0 and x+width <= size
                end = x + width
                counts[owner] += width
                first.setdefault(owner, [x, y])
                n = nodes[owner]
                for col in range(x, x+width):
                    if organic:
                        cell = grid["cells"][owner]
                        correct &= cell["node"] == owner and cell["x"] <= col < cell["x"]+grid["cellPixels"] and cell["y"] <= y < cell["y"]+grid["cellPixels"]
                    else:
                        dx, dy = col+.5-size/2, y+.5-size/2
                        depth = int(math.hypot(dx, dy)/(size*.47)*(data["maxDepth"]+1))
                        angle = math.atan2(dx, -dy) % math.tau
                        correct &= depth == n["depth"] and n["x0"]-1e-10 <= angle <= n["x1"]+1e-10
        check("exact-record-coverage", counts == grid["coverage"] and all(counts))
        check("disjoint-square-pixels", nonoverlap)
        check("every-pixel-inside-owner-cell" if organic else "every-pixel-inside-owner-depth-and-angle", correct)
        if organic:
            cells = grid["cells"]
            check("equal-area-square-records", all(c == grid["cellPixels"]**2 for c in counts))
            check("unique-complete-cells", len(cells) == len(nodes) and len({(c["tileX"],c["tileY"]) for c in cells}) == len(nodes))
            check("connected-body", connected((c["tileX"],c["tileY"]) for c in cells))
            check("every-generation-connected", all(connected((c["tileX"],c["tileY"]) for c in cells if nodes[c["node"]]["depth"] <= depth) for depth in range(data["maxDepth"]+1)))
            birth = sorted(cells,key=lambda c:c["birth"])
            check("outward-generation-order", [c["birth"] for c in birth] == list(range(len(nodes))) and [nodes[c["node"]]["depth"] for c in birth] == sorted(n["depth"] for n in nodes))
            occupied = {(c["tileX"],c["tileY"]) for c in cells}
            xs,ys = zip(*occupied)
            background = {(x,y) for x in range(min(xs)-1,max(xs)+2) for y in range(min(ys)-1,max(ys)+2)}-occupied
            check("no-enclosed-holes", connected(background))
        check("root-at-center", page.evaluate("([x,y])=>hierarchyPixels.ownerAt(x,y)", [size//2, size//2]) == data["rootId"])
        check("native-grid-dimensions", page.locator("#art").evaluate("c=>[c.width,c.height]") == [size, size])
        check("crisp-rendering", page.locator("#art").evaluate("c=>getComputedStyle(c).imageRendering") in {"pixelated", "crisp-edges"})
        check("no-visible-text-in-image", page.locator("#art").text_content() == "" and page.locator("#art text, #art foreignObject").count() == 0)
        capture(page)
        seen_colors = []
        for index, dim in enumerate(data["dimensions"]):
            page.locator("#lenses button").nth(index).click()
            seen_colors.append(image())
            check("selected-lens-"+dim["key"], snapshot()["state"]["lens"] == dim["key"])
            check("fixed-ownership-"+dim["key"], page.evaluate("JSON.stringify(JSON.parse(document.querySelector('#hierarchy-data').textContent).pixels)") == owner_map)
            capture(page, "."+str(index+1))
            page.locator("#info").click()
            if dim["type"] == "categorical":
                if page.locator("#legend button").count():
                    page.locator("#legend button").first.click()
                    check("category-highlights-"+dim["key"], page.locator("#legend button").first.get_attribute("aria-pressed") == "true")
                    page.locator("#reset").click()
            else:
                values = [n["values"][dim["key"]] for n in nodes if n["values"][dim["key"]] is not None]
                check("global-domain-"+dim["key"], snapshot()["domain"] == [0, max(values, default=0)])
                colors = page.evaluate("points=>{const c=document.querySelector('#art').getContext('2d');return points.map(([x,y])=>Array.from(c.getImageData(x,y,1,1).data).slice(0,3));}", [first[i] for i in range(len(nodes))])
                check("missing-checker-and-zero-"+dim["key"], all(colors[i] in [[114,120,130],[64,70,80]] if n["values"][dim["key"]] is None else colors[i] == [23,29,54] if n["values"][dim["key"]] == 0 else colors[i] not in [[114,120,130],[64,70,80],[23,29,54]] for i,n in enumerate(nodes)))
                positive = sorted(v for v in values if v > 0)
                expected = [positive[math.floor((i+1)*(len(positive)-1)/7)] if positive else 0 for i in range(6)]
                check("quantile-thresholds-"+dim["key"], snapshot()["thresholds"] == expected)
                page.locator("#scale").select_option("linear")
                check("linear-thresholds-"+dim["key"], all(math.isclose(t, max(values, default=0)*(i+1)/7) for i,t in enumerate(snapshot()["thresholds"])))
                page.locator("#scale").select_option("log")
                check("log-thresholds-"+dim["key"], all(math.isclose(t, math.expm1(math.log1p(max(values, default=0))*(i+1)/7), rel_tol=1e-12, abs_tol=1e-9) for i,t in enumerate(snapshot()["thresholds"])))
                if dim["aggregation"] == "sum":
                    page.locator("#scope").select_option("subtree")
                    expected_total = math.fsum(values) if values else None
                    root = nodes[0]["aggregates"][dim["key"]]
                    check("observed-total-"+dim["key"], root["value"] == expected_total and root["known"] == len(values))
                    check("subtree-domain-"+dim["key"], snapshot()["domain"] == [0, expected_total or 0])
                    page.locator("#scope").select_option("individual")
                page.locator("#scale").select_option("quantile")
            page.locator("#close").click()
        if len(nodes) > 1:
            target = nodes[-1]
            page.locator("#info").click()
            page.locator("#search").fill(target["id"])
            before = snapshot()
            page.locator("#results button").filter(has_text=target["id"]).first.click()
            check("search-reaches-exact-record", snapshot()["state"]["selected"] == target["id"])
            check("focus-fixed-scale", snapshot()["domain"] == before["domain"] and snapshot()["thresholds"] == before["thresholds"])
            capture(page, ".focus")
            page.locator("#reset").click()
            page.locator("#close").click()
            page.locator("#art").focus()
            page.keyboard.press("ArrowRight")
            check("keyboard-next-record", snapshot()["state"]["selected"] == nodes[1]["id"])
            page.keyboard.press("Escape")
            check("keyboard-reset", snapshot()["state"]["selected"] == data["rootId"] and snapshot()["state"]["zoom"] == 1)
            if organic:
                cell = grid["cells"][1]
                x,y = cell["x"],cell["y"]
            else:
                branch = nodes[1]
                angle = (branch["x0"]+branch["x1"])/2
                radius = (branch["depth"]+.5)*size*.47/(data["maxDepth"]+1)
                x = math.floor(size/2+radius*math.sin(angle))
                y = math.floor(size/2-radius*math.cos(angle))
            box = page.locator("#art").bounding_box()
            page.mouse.click(box["x"]+(x+.5)*box["width"]/size, box["y"]+(y+.5)*box["height"]/size)
            check("pixel-hit-testing", snapshot()["state"]["selected"] == nodes[1]["id"], {"expected": nodes[1]["id"], "selected": snapshot()["state"]["selected"]})
            page.keyboard.press("Escape")
        if organic:
            page.locator("#info").click()
            base_image = image()
            page.locator("#pixel-size").select_option("1")
            check("native-display-scale", math.isclose(page.locator("#art").bounding_box()["width"], size, abs_tol=.1))
            check("display-scale-preserves-pixels", image() == base_image)
            page.locator("#pixel-size").select_option("3")
            page.locator("#close").click()
        page.locator("#immersive").click()
        check("image-only-mode", not page.locator(".top").is_visible() and not page.locator(".dock").is_visible() and page.locator("#art").is_visible())
        page.keyboard.press("1")
        check("keyboard-lens-in-image-mode", snapshot()["state"]["lens"] == data["dimensions"][0]["key"])
        capture(page, ".image-only")
        page.keyboard.press("Escape")
        check("controls-restored", page.locator(".dock").is_visible())
        page.locator("#lenses button").nth(next((i for i,d in enumerate(data["dimensions"]) if d["key"] == data["initialLens"]),0)).click()
        with page.expect_download() as event:
            page.locator("#export-svg").click()
        svg = ET.fromstring(Path(event.value.path()).read_bytes())
        tags = [e.tag.rsplit('}',1)[-1] for e in svg.iter()]
        check("export-text-free-rectangles", not set(tags).intersection({"text", "textPath", "foreignObject", "image", "filter", "linearGradient"}) and tags.count("rect") > 1)
        check("svg-crisp-edges", svg.get("shape-rendering") == "crispEdges")
        metadata = json.loads(svg.find("{http://www.w3.org/2000/svg}metadata").text)
        check("export-data-and-context", metadata["grid"] == size and len(metadata["records"]) == len(nodes) and metadata["provenance"] == data["provenance"] and metadata["thresholds"] == snapshot()["thresholds"])
        if organic:
            check("export-growth-context", metadata["layout"]["cells"] == grid["cells"] and metadata["layout"]["seed"] == grid["seed"] and metadata["encodings"]["adjacency"] == "spatial packing, not reporting edges")
        with page.expect_download() as event:
            page.locator("#export-png").click()
        png = Path(event.value.path()).read_bytes()
        expected_size = size if organic else 2048
        check("png-native-export" if organic else "png-2048-export", png[:8] == b"\x89PNG\r\n\x1a\n" and int.from_bytes(png[16:20], "big") == expected_size and int.from_bytes(png[20:24], "big") == expected_size)
        if screenshot:
            out = screenshot.with_name(screenshot.stem+".export.png")
            out.write_bytes(png)
            evidence.append(str(out))
        check("desktop-no-overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        page.set_viewport_size({"width":390,"height":844})
        page.wait_for_timeout(80)
        check("mobile-no-overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        check("mobile-visible-controls", page.locator("#lenses").is_visible() and page.locator("#info").is_visible())
        capture(page, ".mobile")
        page.reload()
        page.wait_for_function("document.documentElement.dataset.ready === 'true'")
        check("deterministic-reload", snapshot() == original)
        if {d["type"] for d in data["dimensions"]} == {"numeric", "categorical"} and any(n["values"][d["key"]] is not None for n in nodes for d in data["dimensions"] if d["type"] == "numeric"):
            check("lenses-change-pixels", len(set(seen_colors)) > 1)
        check("offline", not network, network)
        check("browser-errors", not errors, errors)
        browser.close()
    return {"ok":all(c["ok"] for c in checks),"nodes":len(nodes),"grid":size,"checks":checks,"seconds":round(time.monotonic()-started,2),"screenshots":evidence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html",type=Path)
    parser.add_argument("--report",type=Path,required=True)
    parser.add_argument("--screenshot",type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.html,args.screenshot)
    except Exception as error:
        result = {"ok":False,"error":str(error)}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}|{"failed":[c for c in result.get('checks',[]) if not c['ok']]}))
    return 0 if result["ok"] else 1


if __name__ == '__main__':
    raise SystemExit(main())
