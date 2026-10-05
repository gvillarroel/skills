#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright", "pillow"]
# ///
"""Verify compositor arrow direction, independent lanes and token clearance."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import subprocess

from playwright.sync_api import sync_playwright

import build_composite_scene
from arrow_quality import ARROW_AUDIT
import validate_scene_contract


def fixture(folder: Path, route: str = "straight", reverse: bool = False):
    elements = []
    for index, x in enumerate([100, 340]):
        name = "input" if index == 0 else "result"
        source = folder / f"{name}.svg"
        source.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 36"><rect width="100" height="36" fill="#ffffff"/><text x="50" y="24" text-anchor="middle" font-size="18" fill="#000000">{name}</text></svg>', encoding="utf-8")
        (folder / f"{name}-report.json").write_text(json.dumps({"passed": True, "scope": "Small synthetic geometry fixture."}), encoding="utf-8")
        elements.append({"id": name, "assetId": name, "producerSkill": "repo-native",
            "fallbackReason": "Small isolated regression-test label asset.", "kind": "svg",
            "src": source.name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "validationReport": f"{name}-report.json",
            "intrinsic": {"width": 100, "height": 36}, "background": "#ffffff",
            "bounds": {"x": x/640, "y": 160/360, "width": 100/640, "height": 36/360},
            "zIndex": 10, "fit": "contain", "overflow": "visible", "clock": "static",
            "ports": [{"id": "in", "x": 0, "y": .5}, {"id": "out", "x": 1, "y": .5}], "states": []})
    return {"schemaVersion": 1, "id": "compact-test", "canvas": {"width": 640,
            "height": 360, "aspectRatio": "16:9", "fps": 30, "durationSeconds": 3,
            "background": "#f7f7f7", "safeArea": {"top": 10, "right": 10, "bottom": 10, "left": 10}},
        "masterClock": {"mode": "deterministic", "loop": False}, "elements": elements,
        "events": [], "tracks": [], "interactions": [{"id": "flow", "type": "signal-route",
            "channel": "signal", "source": {"element": "result" if reverse else "input", "port": "in" if reverse else "out"},
            "target": {"element": "input" if reverse else "result", "port": "out" if reverse else "in"},
            "start": 0, "end": 2, "emits": [], "consumes": [], "meaning": "A directed signal between explicit ports.",
            "connector": {"path": route, "color": "#333e48", "width": 3, "zIndex": 20, "persistAfter": True},
            "validationChecks": ["Complete target head and moving token remain outside the node envelopes."]}]}


class CompositorTest(unittest.TestCase):
    def inspect(self, route="straight", reverse=False, waypoints=None):
        with tempfile.TemporaryDirectory(prefix="compact-route-", dir=Path.cwd()) as name:
            folder = Path(name)
            scene = fixture(folder, route, reverse)
            if waypoints is not None:
                scene["interactions"][0]["connector"]["waypoints"] = waypoints
            source = folder / "scene.json"
            source.write_text(json.dumps(scene), encoding="utf-8")
            output = folder / "scene.html"
            result = build_composite_scene.build(argparse.Namespace(output=output, contract=source,
                project_root=folder, force=False, allow_missing_hashes=False, require_producer_reports=False, report=None))
            self.assertTrue(result["passed"])
            with sync_playwright() as api:
                browser = api.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 640, "height": 360})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(output.as_uri())
                for seconds in [0, .25, .8, 1.5, 1.998, 2.5]:
                    state = page.evaluate("t => window.renderConceptFrame('compact-test', t)", seconds)
                    arrow = state["interactionStates"]["flow"]
                    self.assertAlmostEqual(abs(arrow["target"]["x"] - arrow["arrowTip"]["x"]), 6, delta=.15)
                    geometry = page.evaluate("""() => {
                      const token=document.querySelector('[data-relationship-pulse]');
                      const rect=token.getBoundingClientRect();
                      const boxes=[...document.querySelectorAll('.video-element')].map(n=>n.getBoundingClientRect());
                      const overlaps=boxes.filter(b=>rect.left<b.right&&rect.right>b.left&&rect.top<b.bottom&&rect.bottom>b.top);
                      return {visible: +getComputedStyle(token).opacity>0, overlaps: overlaps.length};
                    }""")
                    if geometry["visible"]:
                        self.assertEqual(geometry["overlaps"], 0)
                audit = page.evaluate(ARROW_AUDIT, {"selector": "#stage"})
                self.assertEqual(audit["shaftCount"], 1)
                self.assertEqual(audit["headCount"], 1)
                self.assertEqual(audit["issues"], [])
                self.assertEqual(errors, [])
                browser.close()

    def test_cli_samples_held_state_on_real_stage_backing(self):
        with tempfile.TemporaryDirectory(prefix="compact-cli-", dir=Path.cwd()) as name:
            folder=Path(name)
            scene=fixture(folder)
            scene["interactions"][0]["connector"]["color"]="#9e1b32"
            source,output=folder/"scene.json",folder/"scene.html"
            source.write_text(json.dumps(scene),encoding="utf-8")
            build_composite_scene.build(argparse.Namespace(output=output,contract=source,project_root=folder,
                force=False,allow_missing_hashes=False,require_producer_reports=False,report=None))
            report=folder/"arrows.json"
            result=subprocess.run(["uv","run","--script",str(Path(__file__).with_name("arrow_quality.py")),
                str(output),"--selector","#stage","--width","640","--height","360","--time","2.5",
                "--report",str(report)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            audit=json.loads(report.read_text())
            self.assertEqual(audit["headCount"],1)
            self.assertEqual(audit["issues"],[])

    def test_straight_and_reverse_curve_heads(self):
        self.inspect()
        self.inspect("curve", True)

    def test_feedback_polyline(self):
        self.inspect(waypoints=[{"x": 230/640, "y": 178/360}, {"x": 230/640, "y": 246/360},
                                {"x": 310/640, "y": 246/360}, {"x": 310/640, "y": 178/360}])

    def test_invalid_waypoints_rejected(self):
        with tempfile.TemporaryDirectory(prefix="compact-schema-", dir=Path.cwd()) as name:
            folder = Path(name)
            for invalid in [[{"x": 1.1, "y": .5}], [{"x": float("nan"), "y": .5}], [{}], "bad"]:
                scene = fixture(folder)
                scene["interactions"][0]["connector"]["waypoints"] = invalid
                self.assertFalse(validate_scene_contract.validate_contract(scene, folder)["passed"])

    def test_overcompressed_route_refuses_lost_signal_travel(self):
        with tempfile.TemporaryDirectory(prefix="compact-refusal-", dir=Path.cwd()) as name:
            folder = Path(name)
            scene = fixture(folder)
            scene["elements"][1]["bounds"]["x"] = 248/640
            scene["interactions"][0]["connector"]["width"] = 4
            source, output = folder/"scene.json", folder/"scene.html"
            source.write_text(json.dumps(scene), encoding="utf-8")
            build_composite_scene.build(argparse.Namespace(output=output, contract=source,
                project_root=folder, force=False, allow_missing_hashes=False, require_producer_reports=False, report=None))
            with sync_playwright() as api:
                browser = api.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width":640,"height":360})
                page.goto(output.as_uri())
                failure = page.evaluate("""async () => {
                  try { await window.renderConceptFrame('compact-test',.5); return null; }
                  catch(error) { return error.message; }
                }""")
                self.assertIn("Route lacks space for a complete head and moving signal", failure)
                browser.close()


if __name__ == "__main__":
    unittest.main()
