#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independent data, input-safety, browser and export checks for the treemap builder."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from playwright.sync_api import sync_playwright

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import build_treemap
import check_palette_contract
import check_self_contained_html

ARTIFACTS: Path
REPORT: list[dict] = []


def hierarchy(counts=(3, 3, 3)):
    names = ["Planning", "Delivery", "Support"]
    leaves = [[("Forecast", 29), ("Schedule", 24), ("Risks", 18), ("Change", 11)],
              [("Implementation", 30), ("Review", 21), ("Release", 15), ("Handoff", 9)],
              [("Diagnose", 25), ("Documentation", 19), ("Training", 13), ("Escalation", 7)]]
    return {"name": "Operations portfolio", "children": [
        {"name": name, "children": [{"name": label, "value": value} for label, value in rows[:count]]}
        for name, rows, count in zip(names, leaves, counts)]}


BROWSER_CHECK = r"""() => {
  const svg=document.querySelector('svg'), problems=[], colors=[];
  const hex=value=>{const channels=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return channels?'#'+channels.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value;};
  const luminance=value=>[1,3,5].map(i=>parseInt(value.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  const nodes=[...svg.querySelectorAll('.treemap-node')].map(group=>{
    const rect=group.querySelector(group.getAttribute('data-text-backing')), style=getComputedStyle(rect), b=rect.getBBox();
    const text=group.querySelector('text'), tb=text?.getBBox(), fill=hex(style.fill);
    const expected=(luminance(fill)+.05)/.05>=1.05/(luminance(fill)+.05)?'#000000':'#ffffff';
    if(+style.fillOpacity!==1 || style.stroke!=='none')problems.push('A treemap face is translucent or bordered');
    if(b.width<0 || b.height<0)problems.push('A face has negative geometry');
    if(text && (hex(getComputedStyle(text).fill)!==expected || getComputedStyle(text).stroke!=='none'))problems.push('A direct label has incorrect paint');
    if(tb && (tb.x<-.1 || tb.y<-.1 || tb.x+tb.width>b.width+.1 || tb.y+tb.height>b.height+.1))problems.push('A direct label escapes its face');
    return {name:group.dataset.name,value:+group.dataset.value,branch:group.dataset.branch,leaf:group.classList.contains('treemap-leaf'),fill,tone:rect.dataset.toneIndex,label:text?[...text.childNodes].map(n=>n.textContent).join(' '):null,width:b.width,height:b.height,x:group.__data__?.x0,y:group.__data__?.y0};
  });
  for(const shape of svg.querySelectorAll('rect,text')){
    const s=getComputedStyle(shape);colors.push(hex(s.fill));
    if(shape.localName==='rect' && (+shape.getAttribute('width')<0 || +shape.getAttribute('height')<0))problems.push('A rectangle has negative dimensions');
  }
  return {problems,nodes,colors,title:svg.querySelector('title')?.textContent,desc:svg.querySelector('desc')?.textContent,
    colorset:svg.dataset.colorset,pattern:svg.dataset.patternId,keyCount:+svg.dataset.keyCount,
    overflow:document.documentElement.scrollWidth>innerWidth+2,unsafe:window.__unsafe===true};
}"""


class TreemapBuilderTests(unittest.TestCase):
    def test_deterministic_offline_runtime_and_input_preservation(self):
        data = hierarchy()
        first = build_treemap.build_document(data)
        self.assertEqual(first, build_treemap.build_document(data))
        self.assertEqual(data, hierarchy())
        runtime = build_treemap.D3_RUNTIME.read_text(encoding="utf-8")
        self.assertIn(f'<script id="d3-runtime">{runtime}</script>', first)
        self.assertIn("d3.hierarchy(config.data).sum", first)
        self.assertIn("d3.treemap()", first)

    def test_invalid_data_and_safe_total_are_rejected(self):
        for value in [0, -1, True, "10", float("nan"), float("inf"), 2**53]:
            with self.subTest(value=str(value)):
                data = hierarchy()
                data["children"][0]["children"][0]["value"] = value
                with self.assertRaises(ValueError):
                    build_treemap.validate_data(data)
        for change in ["internal-value", "empty", "duplicate", "deep", "control", "total"]:
            data = hierarchy()
            if change == "internal-value": data["value"] = 2
            elif change == "empty": data["children"][0]["children"] = []
            elif change == "duplicate": data["children"][0]["children"][1]["name"] = "Forecast"
            elif change == "deep": data["children"][0]["children"][0]["children"] = []
            elif change == "control": data["name"] = "Bad\nname"
            else:
                for branch in data["children"]:
                    for leaf in branch["children"]: leaf["value"] = 2**52
            with self.subTest(change=change), self.assertRaises(ValueError):
                build_treemap.validate_data(data)

    def test_cli_rejects_writing_to_skill_and_input(self):
        data = ARTIFACTS / "input-safety.json"
        data.write_text(json.dumps(hierarchy()), encoding="utf-8")
        for output in [SKILL_ROOT / "rejected-output.html", data, ARTIFACTS / "bad.svg"]:
            with self.subTest(output=str(output)), patch.object(sys, "argv", ["build_treemap.py", "--data", str(data), "--output", str(output)]), redirect_stderr(StringIO()):
                self.assertEqual(build_treemap.main(), 1)
        self.assertFalse((SKILL_ROOT / "rejected-output.html").exists())
        self.assertEqual(json.loads(data.read_text(encoding="utf-8")), hierarchy())

    def test_static_palette_and_self_contained_contracts(self):
        for colorset in build_treemap.FAMILIES:
            artifact = ARTIFACTS / f"changed-{colorset}.html"
            artifact.write_text(build_treemap.build_document(hierarchy(), colorset=colorset), encoding="utf-8")
            self.assertEqual(check_self_contained_html.check_file(artifact), [])
            self.assertTrue(check_palette_contract.validate_artifact(artifact, colorset=colorset)["ok"])

    def test_changed_data_boundaries_replay_reduced_motion_and_export(self):
        cases = [("changed", hierarchy()), ("boundary", hierarchy((1, 2, 4))) ]
        tiny = hierarchy()
        tiny["children"][0]["children"][-1]["value"] = 1e-12
        cases.append(("tiny", tiny))
        unsafe = hierarchy()
        unsafe["children"][0]["children"][0]["name"] = '</script><script>window.__unsafe=true</script> #007298 __D3__'
        cases.append(("literal", unsafe))
        with sync_playwright() as playwright:
            options = {} if Path(playwright.chromium.executable_path).exists() else {"channel": "msedge"}
            browser = playwright.chromium.launch(**options)
            for colorset in build_treemap.FAMILIES:
                allowed = json.loads(build_treemap.CONTRACT.read_text(encoding="utf-8"))["colorsets"][colorset]["allowed"]
                for name, data in cases:
                    artifact = ARTIFACTS / f"{name}-{colorset}.html"
                    artifact.write_text(build_treemap.build_document(data, colorset=colorset), encoding="utf-8")
                    for width in [960, 420]:
                        for motion in ["no-preference", "reduce"]:
                            context = browser.new_context(viewport={"width": width, "height": 720}, reduced_motion=motion)
                            page = context.new_page()
                            errors, network = [], []
                            page.on("pageerror", lambda error: errors.append(str(error)))
                            page.on("request", lambda request: network.append(request.url) if request.url.startswith(("http:", "https:")) else None)
                            page.goto(artifact.as_uri())
                            page.wait_for_timeout(650)
                            stable = None
                            for replay in range(3):
                                if replay:
                                    page.get_by_role("button", name="Replay").click()
                                    page.wait_for_timeout(650)
                                result = page.evaluate(BROWSER_CHECK)
                                self.assertEqual(errors + network + result["problems"], [])
                                self.assertFalse(result["overflow"])
                                self.assertFalse(result["unsafe"])
                                self.assertTrue(result["title"] and result["desc"])
                                self.assertEqual(result["colorset"], colorset)
                                self.assertEqual(set(result["colors"]) - set(allowed), set())
                                leaves = [item for item in result["nodes"] if item["leaf"]]
                                if colorset == "colorset1":
                                    headers = [item for item in result["nodes"] if not item["leaf"]]
                                    self.assertEqual([item["fill"] for item in headers], ["#9e1b32", "#333e48", "#4f4f4f"])
                                expected = {(leaf["name"], leaf["value"]) for branch in data["children"] for leaf in branch["children"]}
                                self.assertEqual({(item["name"], item["value"]) for item in leaves}, expected)
                                if name in {"changed", "boundary"}:
                                    self.assertEqual(result["keyCount"], 0)
                                    for item in leaves:
                                        self.assertIn(item["name"], item["label"])
                                        self.assertIn(str(item["value"]), item["label"])
                                    for branch in data["children"]:
                                        siblings = [item for item in leaves if item["branch"] == branch["name"]]
                                        self.assertEqual(len({item["fill"] for item in siblings}), min(3, len(siblings)))
                                        self.assertEqual([int(item["tone"]) for item in siblings], [1] if len(siblings) == 1 else ([0, 2] if len(siblings) == 2 else ([0, 1, 2] if len(siblings) == 3 else [0, 1, 1, 2])))
                                elif name == "tiny":
                                    self.assertGreater(result["keyCount"], 0)
                                if stable is not None: self.assertEqual(result["nodes"], stable)
                                stable = result["nodes"]
                                REPORT.append({"case": name, "colorset": colorset, "width": width, "motion": motion, "replay": replay, "passed": True})
                            if motion == "reduce": page.screenshot(path=str(ARTIFACTS / f"{name}-{colorset}-{width}.png"))
                            context.close()
                # Production export must render the data rather than a scripted placeholder.
                html = ARTIFACTS / f"changed-{colorset}.html"
                svg = html.with_suffix(".svg")
                subprocess.run(["uv", "run", "--script", str(SKILL_ROOT / "scripts/render_d3_svg.py"), str(html), "--output", str(svg), "--viewport", "960x720", "--wait-ms", "650"], check=True)
                self.assertTrue(check_palette_contract.validate_artifact(svg, colorset=colorset, require_extended=colorset == "colorset2")["ok"])
                self.assertNotIn("<script", svg.read_text(encoding="utf-8"))
                for width in [960, 420]:
                    page = browser.new_page(viewport={"width": width, "height": 720}, reduced_motion="reduce")
                    page.goto(svg.as_uri())
                    page.wait_for_timeout(650)
                    result = page.evaluate(BROWSER_CHECK)
                    self.assertEqual(result["problems"], [])
                    self.assertEqual(result["keyCount"], 0)
                    self.assertEqual(len([n for n in result["nodes"] if n["leaf"]]), 9)
                    REPORT.append({"case": "export", "colorset": colorset, "width": width, "passed": True})
                    page.close()
            browser.close()


def main():
    global ARTIFACTS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    ARTIFACTS = args.artifacts.resolve()
    if ARTIFACTS.is_relative_to(SKILL_ROOT): parser.error("Artifacts must be outside the skill resource")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TreemapBuilderTests))
    (ARTIFACTS / "test-report.json").write_text(json.dumps({"passed": result.wasSuccessful(), "testsRun": result.testsRun, "states": REPORT}, indent=2) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
