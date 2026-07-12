#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Capture and verify deterministic navigation states for the Heatwave Tree."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


def close(first: Any, second: Any, tolerance: float = 1e-6) -> bool:
    if isinstance(first, (int, float)) and isinstance(second, (int, float)):
        return math.isclose(float(first), float(second), abs_tol=tolerance, rel_tol=tolerance)
    if isinstance(first, list) and isinstance(second, list) and len(first) == len(second):
        return all(close(a, b, tolerance) for a, b in zip(first, second))
    return first == second


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture navigable SVG review states.")
    parser.add_argument("svg", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    svg = args.svg.resolve()
    output_dir = args.output_dir.resolve()
    report_path = args.report.resolve()
    manifest_path = (
        args.manifest.resolve()
        if args.manifest is not None
        else output_dir / "capture-manifest.json"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    for pattern in ("[0-9][0-9]-*.png", "99-script-free.png"):
        for stale in output_dir.glob(pattern):
            stale.unlink()

    checks: list[dict[str, Any]] = []
    captures: list[dict[str, Any]] = []
    browser_errors: list[str] = []

    def record(check_id: str, passed: bool, details: Any = None) -> None:
        checks.append({"id": check_id, "passed": bool(passed), "details": details})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.on("console", lambda message: browser_errors.append(f"console {message.type}: {message.text}") if message.type == "error" else None)
        page.on("pageerror", lambda error: browser_errors.append(f"pageerror: {error}"))
        page.goto(svg.as_uri(), wait_until="load", timeout=60_000)
        page.wait_for_function("window.svgSync && window.svgSync.ready")
        page.evaluate("() => window.svgSync.ready")
        plan = page.evaluate("() => window.svgSync.getPlan()")
        navigation = plan["navigation"]
        anchors = {item["id"]: item for item in navigation["anchors"]}

        def capture_state(capture_id: str, anchor_id: str, path: Path) -> None:
            camera = page.evaluate("() => window.svgSync.getCamera()")
            semantic = page.evaluate("() => window.svgSync.snapshot()")
            page.screenshot(path=str(path), animations="disabled")
            captures.append(
                {
                    "step": len(captures),
                    "id": capture_id,
                    "filename": path.name,
                    "path": str(path),
                    "anchorId": camera["anchorId"] or anchor_id,
                    "expectedAnchorId": anchor_id,
                    "tier": camera["tier"],
                    "scenarioId": semantic["scenarioId"],
                    "cameraRevision": camera["revision"],
                    "routeStopId": camera["stopId"],
                    "routeTimeMs": camera["timeMs"],
                }
            )

        api_methods = page.evaluate(
            """() => Object.fromEntries([
              'getCamera','setCamera','navigateTo','seekCamera','fitOverview',
              'nextAnchor','previousAnchor','playCamera','pauseCamera','resetCamera'
            ].map((name) => [name, typeof window.svgSync[name]]))"""
        )
        record("camera-api", all(value == "function" for value in api_methods.values()), api_methods)

        viewport_box = page.evaluate(
            """() => {
              const root = document.documentElement;
              const matrix = root.getScreenCTM();
              const [x, y, width, height] = window.svgSync.getPlan().navigation.viewport.map(Number);
              const points = [
                new DOMPoint(x, y), new DOMPoint(x + width, y),
                new DOMPoint(x, y + height), new DOMPoint(x + width, y + height)
              ].map((point) => point.matrixTransform(matrix));
              const left = Math.min(...points.map((point) => point.x));
              const top = Math.min(...points.map((point) => point.y));
              const right = Math.max(...points.map((point) => point.x));
              const bottom = Math.max(...points.map((point) => point.y));
              return {x:left, y:top, width:right-left, height:bottom-top};
            }"""
        )
        world_lod = page.evaluate(
            """() => ({
              nodeCount: document.querySelectorAll('[data-world-module-id]').length,
              trunkCount: document.querySelectorAll('[data-tree-role="trunk"]').length,
              paintedModuleFrames: [...document.querySelectorAll('.sync-module > .module-frame')]
                .filter((item) => {
                  const style = getComputedStyle(item);
                  return Number(style.fillOpacity) > 0.01 || Number(style.strokeOpacity) > 0.01;
                }).length,
              districtTabStops: document.querySelectorAll('.district-nav-control[tabindex="0"]').length,
              moduleNodeTabStops: document.querySelectorAll('.world-module-nav-control[tabindex="0"]').length
            })"""
        )
        record(
            "world-semantic-zoom",
            world_lod == {
                "nodeCount": 36,
                "trunkCount": 7,
                "paintedModuleFrames": 0,
                "districtTabStops": 8,
                "moduleNodeTabStops": 0,
            },
            world_lod,
        )
        peer_sizes = {
            tuple(round(float(value), 6) for value in anchor["viewBox"][2:4])
            for anchor in navigation["anchors"]
            if anchor["kind"] == "district" and anchor["targetId"] != plan["world"]["rootDistrictId"]
        }
        record("peer-district-camera-scale", len(peer_sizes) == 1, sorted(peer_sizes))

        overview_path = output_dir / "00-world.png"
        capture_state("world", "world", overview_path)

        district_anchors = [item for item in navigation["anchors"] if item["kind"] == "district"]
        for index, anchor in enumerate(district_anchors, start=1):
            before_semantic = page.evaluate("() => window.svgSync.serializeSnapshot()")
            camera = page.evaluate("anchor => window.svgSync.navigateTo(anchor, {updateHash:false})", anchor["id"])
            after_semantic = page.evaluate("() => window.svgSync.serializeSnapshot()")
            actual_view_box = page.locator("#composition-world-viewport").get_attribute("viewBox")
            parsed_view_box = [float(value) for value in (actual_view_box or "").split()]
            district_lod = page.evaluate(
                """anchor => ({
                  activeNodes: [...document.querySelectorAll('.world-module-nav-control[tabindex="0"]')]
                    .map((item) => item.closest('[data-world-module-id]')?.getAttribute('data-world-module-id'))
                    .filter(Boolean).sort(),
                  activeFocusControls: document.querySelectorAll('[data-module-focus-id][tabindex="0"]').length,
                  activeDistrictControls: document.querySelectorAll('.district-nav-control[tabindex="0"]').length,
                  paintedModuleFrames: [...document.querySelectorAll('.sync-module > .module-frame')]
                    .filter((item) => {
                      const style = getComputedStyle(item);
                      return Number(style.fillOpacity) > 0.01 || Number(style.strokeOpacity) > 0.01;
                    }).length,
                  expectedNodes: [...anchor.moduleIds].sort()
                })""",
                anchor,
            )
            record(
                f"anchor-{anchor['id']}",
                camera["anchorId"] == anchor["id"]
                and close(camera["viewBox"], anchor["viewBox"])
                and close(parsed_view_box, anchor["viewBox"])
                and before_semantic == after_semantic,
                {"camera": camera, "semanticUnchanged": before_semantic == after_semantic, "lod": district_lod},
            )
            record(
                f"district-lod-{anchor['targetId']}",
                district_lod["activeNodes"] == district_lod["expectedNodes"]
                and district_lod["activeFocusControls"] == 0
                and district_lod["activeDistrictControls"] == 0
                and district_lod["paintedModuleFrames"] == 0,
                district_lod,
            )
            screenshot = output_dir / f"{index:02d}-{anchor['targetId']}.png"
            capture_state(anchor["targetId"], anchor["id"], screenshot)

        module_targets = [
            "city-pulse-hub",
            "substation-lineage",
            "cohort-exposure-tree",
            "policy-learning-feedback",
            "grid-reliability-bullet",
            "surge-bed-bullet",
        ]
        module_by_id = {item["id"]: item for item in plan["modules"]}
        module_evidence: list[dict[str, Any]] = []
        capture_offset = len(district_anchors) + 1
        for anchor in [item for item in navigation["anchors"] if item["kind"] == "module"]:
            module_id = anchor["targetId"]
            anchor_id = anchor["id"]
            before_semantic = page.evaluate("() => window.svgSync.serializeSnapshot()")
            camera = page.evaluate("anchor => window.svgSync.navigateTo(anchor, {updateHash:false})", anchor_id)
            after_semantic = page.evaluate("() => window.svgSync.serializeSnapshot()")
            frame = page.locator(f"[data-module-id='{module_id}'] .module-frame").bounding_box()
            coverage = 0.0
            if frame and viewport_box:
                intersection_width = max(0.0, min(frame["x"] + frame["width"], viewport_box["x"] + viewport_box["width"]) - max(frame["x"], viewport_box["x"]))
                intersection_height = max(0.0, min(frame["y"] + frame["height"], viewport_box["y"] + viewport_box["height"]) - max(frame["y"], viewport_box["y"]))
                coverage = intersection_width * intersection_height / max(1.0, frame["width"] * frame["height"])
            detail = page.evaluate(
                """moduleId => {
                  const module = document.querySelector(`[data-module-id="${CSS.escape(moduleId)}"]`);
                  const visible = (item) => {
                    let current = item;
                    while (current && current !== module.parentElement) {
                      const style = getComputedStyle(current);
                      if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) <= .01) return false;
                      if (current === module) break;
                      current = current.parentElement;
                    }
                    const box = item.getBoundingClientRect();
                    return box.width > 0 && box.height > 0;
                  };
                  return {
                    visibleTextCount: [...module.querySelectorAll('text')].filter(visible).length,
                    ellipsisCount: [...module.querySelectorAll('.structural-node text')]
                      .filter((item) => (item.textContent || '').includes('…')).length,
                    activeModules: [...document.querySelectorAll('.sync-module[data-camera-active="true"]')]
                      .map((item) => item.getAttribute('data-module-id')).sort(),
                    activeFocusControls: [...document.querySelectorAll('[data-module-focus-id][tabindex="0"]')]
                      .map((item) => item.closest('[data-module-id]')?.getAttribute('data-module-id')).filter(Boolean).sort(),
                    activeNodeControls: document.querySelectorAll('.world-module-nav-control[tabindex="0"]').length,
                    activeDistrictControls: document.querySelectorAll('.district-nav-control[tabindex="0"]').length
                  };
                }""",
                module_id,
            )
            expected_focus = [module_id] * len(module_by_id[module_id].get("focusGroups", []))
            passed = (
                camera["tier"] == "module"
                and camera["anchorId"] == anchor_id
                and coverage >= 0.95
                and before_semantic == after_semantic
                and detail["visibleTextCount"] >= 3
                and detail["ellipsisCount"] == 0
                and detail["activeModules"] == [module_id]
                and detail["activeFocusControls"] == expected_focus
                and detail["activeNodeControls"] == 0
                and detail["activeDistrictControls"] == 0
            )
            module_evidence.append(
                {"moduleId": module_id, "passed": passed, "coverage": coverage, **detail}
            )
            if module_id in module_targets:
                screenshot = output_dir / f"{capture_offset:02d}-module-{module_id}.png"
                capture_state(f"module-{module_id}", anchor_id, screenshot)
                capture_offset += 1
        record(
            "all-module-anchors",
            all(item["passed"] for item in module_evidence),
            {
                "moduleCount": len(module_evidence),
                "minimumCoverage": min(item["coverage"] for item in module_evidence),
                "failures": [item for item in module_evidence if not item["passed"]],
            },
        )
        travel_stops = [
            stop
            for stop in navigation["route"]["stops"]
            if float(stop["arrivalMs"]) > float(stop["startMs"])
        ]
        for route_index, stop in enumerate(travel_stops, start=1):
            midpoint = (float(stop["startMs"]) + float(stop["arrivalMs"])) / 2.0
            page.evaluate("time => window.svgSync.seekCamera(time)", midpoint)
            screenshot = output_dir / f"{capture_offset + route_index - 1:02d}-route-{stop['id']}-mid.png"
            capture_state(f"route-{stop['id']}-mid", "", screenshot)
        hud_clearance = page.evaluate(
            """() => {
              const panel = document.querySelector('.navigation-hud-panel').getBoundingClientRect();
              const escapes = [...document.querySelectorAll('#navigation-hud text')]
                .filter((item) => Number(getComputedStyle(item).opacity) > .01)
                .map((item) => ({item, box:item.getBoundingClientRect()}))
                .filter(({box}) => box.left < panel.left - 2 || box.top < panel.top - 2 ||
                  box.right > panel.right + 2 || box.bottom > panel.bottom + 2)
                .map(({item, box}) => ({text:(item.textContent || '').trim(), left:box.left, right:box.right}));
              return {escapeCount:escapes.length, escapes};
            }"""
        )
        record("navigation-hud-clearance", hud_clearance["escapeCount"] == 0, hud_clearance)

        sample_times = sorted(
            {
                0.0,
                float(navigation["route"]["durationMs"]),
                *[
                    float(stop["startMs"])
                    for stop in navigation["route"]["stops"]
                ],
                *[
                    (float(stop["startMs"]) + float(stop["arrivalMs"])) / 2
                    for stop in navigation["route"]["stops"]
                    if float(stop["arrivalMs"]) > float(stop["startMs"])
                ],
                *[
                    float(stop["arrivalMs"])
                    for stop in navigation["route"]["stops"]
                ],
            }
        )
        ascending = {
            str(time): page.evaluate("time => window.svgSync.seekCamera(time).viewBox", time)
            for time in sample_times
        }
        shuffled = {
            str(time): page.evaluate("time => window.svgSync.seekCamera(time).viewBox", time)
            for time in reversed(sample_times)
        }
        record(
            "camera-history-independent-seek",
            all(close(ascending[key], shuffled[key]) for key in ascending),
            {"sampleCount": len(sample_times)},
        )
        record(
            "camera-loop-seam",
            close(ascending[str(0.0)], ascending[str(float(navigation["route"]["durationMs"]))]),
            {"start": ascending[str(0.0)], "end": ascending[str(float(navigation["route"]["durationMs"]))]},
        )

        page.evaluate("() => { window.svgSync.reset(); window.svgSync.fitOverview(); }")
        semantic_before = page.evaluate("() => window.svgSync.snapshot()")
        camera_before = page.evaluate("() => window.svgSync.getCamera()")
        page.evaluate("() => window.svgSync.setState({'heat-index-anomaly': 9})")
        semantic_after = page.evaluate("() => window.svgSync.snapshot()")
        page.evaluate("() => window.svgSync.navigateTo('district-atmosphere-signal', {updateHash:false})")
        atmosphere_values = page.evaluate(
            """() => [...document.querySelectorAll("[data-district-id='atmosphere-signal'] [data-bind='heat-index-anomaly']")]
              .map((item) => ({value:item.dataset.currentValue, revision:item.dataset.syncRevision}))"""
        )
        page.evaluate("() => window.svgSync.navigateTo('district-health-care', {updateHash:false})")
        health_values = page.evaluate(
            """() => [...document.querySelectorAll("[data-district-id='health-care'] [data-bind='heat-index-anomaly']")]
              .map((item) => ({value:item.dataset.currentValue, revision:item.dataset.syncRevision}))"""
        )
        semantic_after_navigation = page.evaluate("() => window.svgSync.snapshot()")
        camera_after = page.evaluate("() => window.svgSync.getCamera()")
        records = atmosphere_values + health_values
        record(
            "distant-synchronization",
            bool(atmosphere_values)
            and bool(health_values)
            and all(float(item["value"]) == 9 for item in records)
            and all(str(item["revision"]) == str(semantic_after["revision"]) for item in records)
            and semantic_after_navigation == semantic_after
            and semantic_after["revision"] == semantic_before["revision"] + 1
            and camera_after["revision"] > camera_before["revision"],
            {
                "atmosphere": atmosphere_values,
                "health": health_values,
                "semanticRevision": semantic_after["revision"],
                "cameraRevision": camera_after["revision"],
            },
        )

        minimap = page.evaluate(
            """() => {
              const item = document.querySelector('[data-minimap-viewport]');
              return ['x','y','width','height'].map((name) => Number(item.getAttribute(name)));
            }"""
        )
        record("minimap-finite", all(math.isfinite(float(value)) and float(value) >= 0 for value in minimap), minimap)

        deep = context.new_page()
        deep.goto(svg.as_uri() + "#view=district-power-grid", wait_until="load", timeout=60_000)
        deep.wait_for_function("window.svgSync && window.svgSync.ready")
        deep_anchor = deep.evaluate("() => window.svgSync.getCamera().anchorId")
        deep_label = deep.locator("[data-navigation-current-label]").text_content()
        record("deep-link", deep_anchor == "district-power-grid" and "Power Grid" in (deep_label or ""), {"anchor": deep_anchor, "label": deep_label})
        deep.close()

        reduced = browser.new_context(viewport={"width": 1920, "height": 1080}, reduced_motion="reduce")
        reduced_page = reduced.new_page()
        reduced_page.goto(svg.as_uri(), wait_until="load", timeout=60_000)
        reduced_page.wait_for_function("window.svgSync && window.svgSync.ready")
        reduced_state = reduced_page.evaluate(
            """() => {
              const before = window.svgSync.getCamera();
              const played = window.svgSync.playCamera();
              const moved = window.svgSync.navigateTo('district-health-care', {updateHash:false});
              const control = document.querySelector('[data-camera-action="tour"]');
              return {before, played, moved, disabled: control?.getAttribute('aria-disabled'), tabIndex: control?.tabIndex};
            }"""
        )
        record(
            "reduced-motion-navigation",
            reduced_state["played"]["playing"] is False
            and reduced_state["moved"]["anchorId"] == "district-health-care"
            and reduced_state["disabled"] == "true"
            and reduced_state["tabIndex"] == -1,
            reduced_state,
        )
        reduced.close()

        script_free = browser.new_context(viewport={"width": 1920, "height": 1080}, java_script_enabled=False)
        static_page = script_free.new_page()
        static_page.goto(svg.as_uri(), wait_until="load", timeout=60_000)
        static_path = output_dir / "99-script-free.png"
        static_page.screenshot(path=str(static_path), animations="disabled")
        static_evidence = static_page.evaluate(
            """() => ({
              districts: document.querySelectorAll('.world-district').length,
              modules: document.querySelectorAll('.sync-module').length,
              visibleModuleFrames: [...document.querySelectorAll('.sync-module > .module-frame')]
                .filter((item) => Number(getComputedStyle(item).fillOpacity) > .01).length,
              hudPresent: Boolean(document.querySelector('[data-navigation-hud]')),
              hudVisible: getComputedStyle(document.querySelector('[data-navigation-hud]')).display !== 'none',
              headerTextCount: [...document.querySelectorAll('#composition-header > text')]
                .filter((item) => getComputedStyle(item).display !== 'none').length,
              initialViewBox: (document.querySelector('#composition-world-viewport').getAttribute('viewBox') || '')
                .split(/\\s+/).map(Number),
              visibleInteractive: [...document.querySelectorAll('.interactive-control')]
                .filter((item) => getComputedStyle(item).display !== 'none').length
            })"""
        )
        expected_static_view = anchors[navigation["initialAnchorId"]]["viewBox"]
        record(
            "script-free-overview",
            static_evidence["districts"] == 8
            and static_evidence["modules"] == 36
            and static_evidence["visibleModuleFrames"] == 36
            and static_evidence["hudPresent"] is True
            and static_evidence["hudVisible"] is False
            and static_evidence["headerTextCount"] >= 3
            and close(static_evidence["initialViewBox"], expected_static_view)
            and static_evidence["visibleInteractive"] == 0,
            static_evidence,
        )
        captures.append(
            {
                "step": len(captures),
                "id": "script-free",
                "filename": static_path.name,
                "path": str(static_path),
                "anchorId": "world",
                "tier": "world",
                "scenarioId": plan["initialScenario"],
                "cameraRevision": None,
                "routeStopId": None,
                "routeTimeMs": 0,
            }
        )
        script_free.close()

        record("browser-errors", not browser_errors, browser_errors)
        context.close()
        browser.close()

    report = {
        "ok": all(item["passed"] for item in checks),
        "artifact": str(svg),
        "checks": checks,
        "captures": captures,
        "browserErrors": browser_errors,
        "metrics": {
            "checkCount": len(checks),
            "passedCount": sum(1 for item in checks if item["passed"]),
            "captureCount": len(captures),
            "districtCount": 8,
            "moduleCount": 36,
        },
    }
    manifest = {
        "version": 1,
        "artifact": str(svg),
        "captureCount": len(captures),
        "captures": captures,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report["captureManifest"] = str(manifest_path)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "ok": report["ok"],
                **report["metrics"],
                "report": str(report_path),
                "manifest": str(manifest_path),
            }
        )
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
