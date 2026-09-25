#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Audit the generated map with Chromium, including actual control interactions."""

import argparse
import json
import math
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright


def audit(path, screenshot=None):
    checks, errors, network, evidence = [], [], [], []

    def check(name, condition, detail=None):
        checks.append({"check": name, "ok": bool(condition), **({"detail": detail} if detail is not None else {})})

    def capture(page, suffix):
        if screenshot:
            destination = screenshot if not suffix else screenshot.with_name(screenshot.stem + suffix + screenshot.suffix)
            destination.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(destination), full_page=True)
            evidence.append(str(destination))

    start = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1500, "height": 1200}, reduced_motion="reduce")
        context.route("http://**/*", lambda route: route.abort())
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http:", "https:")) else None)
        page.goto(path.resolve().as_uri(), wait_until="load")
        page.wait_for_function("document.documentElement.dataset.ready === 'true'")
        source = page.locator("#hierarchy-data").text_content()
        data = json.loads(source)
        nodes = data["nodes"]
        by_id = {n["id"]: n for n in nodes}
        root = by_id[data["rootId"]]
        snapshot = lambda: page.evaluate("hierarchyLens.snapshot()")
        geometry = lambda: page.locator("#map .mark").evaluate_all("els => els.map(e => [e.dataset.nodeId, e.getAttribute('d'), e.getAttribute('r')])")
        initial = geometry()
        check("root-at-center", page.locator("#map circle.mark").get_attribute("data-node-id") == root["id"])
        check("root-count", root["count"] == len(nodes))
        check("unique-rendered-ids", len(initial) == len({row[0] for row in initial}))
        check("no-invalid-geometry", all("NaN" not in str(row) and "Infinity" not in str(row) for row in initial))
        check("hierarchy-conservation", all(n["count"] == 1 + sum(by_id[c]["count"] for c in n["children"]) for n in nodes))
        check("angular-containment", all(n["x1"] > n["x0"] and (n["parentId"] is None or by_id[n["parentId"]]["x0"]-1e-9 <= n["x0"] < n["x1"] <= by_id[n["parentId"]]["x1"]+1e-9) for n in nodes))
        check("visible-labels", page.locator("#map .center-text").count() >= 3)
        capture(page, "")
        for index, dim in enumerate(data["dimensions"]):
            page.locator("#lenses button").nth(index).click()
            check("lens-geometry-" + dim["key"], geometry() == initial)
            check("lens-selected-" + dim["key"], snapshot()["state"]["lens"] == dim["key"])
            if dim["type"] == "categorical":
                first = page.locator("#legend button").first
                if first.count():
                    first.click()
                    check("highlight-geometry-" + dim["key"], geometry() == initial)
                    check("highlight-active-" + dim["key"], first.get_attribute("aria-pressed") == "true")
                    page.locator("#clear").click()
            else:
                expected = max((n["values"][dim["key"]] for n in nodes if n["values"][dim["key"]] is not None), default=0)
                check("numeric-domain-" + dim["key"], snapshot()["domain"] == [0, expected])
                missing_marks = page.locator("#map .mark[fill='url(#missing-hatch)']").count()
                check("missing-hatch-" + dim["key"], missing_marks == sum(by_id[row[0]]["values"][dim["key"]] is None for row in initial))
                page.locator("#scale").select_option("log")
                check("log-geometry-" + dim["key"], geometry() == initial)
                if dim["aggregation"] == "sum":
                    page.locator("#scope").select_option("subtree")
                    values = [n["values"][dim["key"]] for n in nodes if n["values"][dim["key"]] is not None]
                    total = math.fsum(values) if values else None
                    actual = root["aggregates"][dim["key"]]["value"]
                    check("root-sum-" + dim["key"], actual is None if total is None else actual is not None and math.isclose(actual, total, rel_tol=1e-12, abs_tol=1e-9))
                    check("coverage-" + dim["key"], root["aggregates"][dim["key"]]["known"] == len(values))
                    check("scope-geometry-" + dim["key"], geometry() == initial)
                domain = snapshot()["domain"]
                if len(initial) > 1:
                    page.locator("#map path.mark").first.click(force=True)
                    check("focus-fixed-domain-" + dim["key"], snapshot()["domain"] == domain)
                    capture(page, ".focus")
                    page.locator("#reset").click()
                capture(page, ".numeric")
                exported = ET.fromstring(page.evaluate("hierarchyLens.exportSvg()"))
                exported_text = " ".join(exported.itertext())
                check("export-metric-context-" + dim["key"], dim["unit"] in exported_text and dim["period"] in exported_text)
        if len(nodes) > 1:
            target = nodes[-1]
            page.locator("#search").fill(target["id"])
            result = page.locator("#search-results button").filter(has_text=target["id"]).first
            result.click()
            check("search-reaches-record", page.locator("#detail-id").text_content() == target["id"])
            check("search-focuses-parent", snapshot()["state"]["focus"] == target["parentId"])
            page.locator("#clear").click()
            if snapshot()["state"]["focus"] != data["rootId"]:
                page.locator("#reset").click()
            first = page.locator("#map .mark").first
            first.focus()
            page.keyboard.press("ArrowRight")
            check("keyboard-next", page.evaluate("document.activeElement.dataset.nodeId") == snapshot()["visible"][1])
            page.keyboard.press("Enter")
            check("keyboard-focus", snapshot()["state"]["focus"] == initial[1][0])
            page.keyboard.press("Escape")
            check("keyboard-up", snapshot()["state"]["focus"] == data["rootId"])
        page.locator("#rings").select_option("3")
        check("ring-limit", all(by_id[identity]["depth"] <= 3 for identity in snapshot()["visible"]))
        page.locator("#rings").select_option("5")
        with page.expect_download() as download_info:
            page.locator("#export-svg").click()
        check("svg-download", download_info.value.suggested_filename.endswith(".svg"))
        with page.expect_download() as download_info:
            page.locator("#export-png").click()
        png = Path(download_info.value.path()).read_bytes()
        check("png-download", download_info.value.suggested_filename.endswith(".png") and png[:8] == b"\x89PNG\r\n\x1a\n" and int.from_bytes(png[16:20], "big") == 2560 and int.from_bytes(png[20:24], "big") == 2700)
        check("desktop-no-overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(180)
        check("mobile-no-overflow", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        check("mobile-controls", page.locator("#search").is_visible() and page.locator("#lenses").is_visible())
        check("mobile-label-size", page.locator("#map .label").evaluate_all("els => els.every(e => parseFloat(e.getAttribute('font-size')) * Math.min(document.querySelector('#chart').getBoundingClientRect().width,document.querySelector('#chart').getBoundingClientRect().height)/1000 >= 11.9)"))
        capture(page, ".mobile")
        check("offline", not network, network)
        check("browser-errors", not errors, errors)
        browser.close()
    return {"ok": all(c["ok"] for c in checks), "nodes": len(nodes), "checks": checks,
            "seconds": round(time.monotonic()-start, 2), "screenshots": evidence}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.html, args.screenshot)
    except Exception as error:
        result = {"ok": False, "error": str(error)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "checks"} | {"failed": [c for c in result.get("checks", []) if not c["ok"]]}))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
