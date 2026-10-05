#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright", "pillow"]
# ///
"""Check measured scene topology, complete motion geometry and refusal bounds."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from playwright.sync_api import sync_playwright

from arrow_quality import ARROW_AUDIT

SCRIPT = Path(__file__).with_name("scaffold_compact_scene.py")


class CompactSceneTest(unittest.TestCase):
    def create(self, folder, nodes, *extra, width=960, height=540):
        command = ["uv", "run", "--script", str(SCRIPT)]
        for identity, label in nodes:
            command.extend(["--node", f"{identity}={label}"])
        command.extend([*extra, "--width", str(width), "--height", str(height),
                        "--project-root", str(folder), "--contract", str(folder/"scene.json"),
                        "--html", str(folder/"scene.html"), "--review", str(folder/"review.json")])
        return subprocess.run(command, capture_output=True, text=True)

    def inspect(self, folder, labels, edges, width=960, height=540):
        scene = json.loads((folder/"scene.json").read_text())
        review = json.loads((folder/"review.json").read_text())
        self.assertEqual(len(scene["interactions"]), edges)
        self.assertEqual(review["retainedNodes"], len(labels))
        self.assertEqual(review["gapPx"], 52)
        self.assertLess(review["occupiedBounds"]["width"], width-48)
        with sync_playwright() as api:
            browser = api.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((folder/"scene.html").as_uri())
            times = [7.9]
            for relation in scene["interactions"]:
                times.extend(relation["start"] + (relation["end"]-relation["start"])*p
                             for p in [0, .3, .8, .998])
            for at in times:
                page.evaluate("t=>window.renderConceptFrame('compact-scene',t)", at)
                geometry = page.evaluate("""() => {
                  const nodes=[...document.querySelectorAll('.video-element')].map(n=>n.getBoundingClientRect());
                  const overlap=(a,b)=>a.left<b.right-.1&&a.right>b.left+.1&&a.top<b.bottom-.1&&a.bottom>b.top+.1;
                  const text=[...document.querySelectorAll('.video-element text')].map(n=>({
                    label:n.textContent,font:parseFloat(getComputedStyle(n).fontSize),b:n.getBoundingClientRect().toJSON()}));
                  const visible=n=>+getComputedStyle(n).opacity>0&&+getComputedStyle(n.parentNode).opacity>0;
                  const pulses=[...document.querySelectorAll('[data-relationship-pulse]')].filter(visible);
                  const heads=[...document.querySelectorAll('[data-arrow-head]')].filter(visible);
                  const clearance=(a,b)=>Math.hypot(Math.max(b.left-a.right,a.left-b.right,0),
                    Math.max(b.top-a.bottom,a.top-b.bottom,0));
                  let collisions=0;
                  for(const path of document.querySelectorAll('[data-arrow-shaft]')){
                    const length=path.getTotalLength();
                    for(let at=0;at<=length;at+=2){const p=path.getPointAtLength(at);
                      collisions+=nodes.filter(b=>p.x>b.left+.1&&p.x<b.right-.1&&p.y>b.top+.1&&p.y<b.bottom-.1).length;}
                  }
                  return {text,heads:heads.length,routeCollisions:collisions,
                    minimumTokenClearance:pulses.length?Math.min(...pulses.flatMap(n=>nodes.map(b=>clearance(n.getBoundingClientRect(),b)))):null,
                    tokenCollisions:pulses.reduce((s,n)=>s+nodes.filter(b=>overlap(n.getBoundingClientRect(),b)).length,0),
                    headCollisions:heads.reduce((s,n)=>s+nodes.filter(b=>overlap(n.getBoundingClientRect(),b)).length,0)};
                }""")
                self.assertEqual(sorted(t["label"] for t in geometry["text"]), sorted(labels))
                self.assertTrue(all(t["font"] == 18 for t in geometry["text"]))
                self.assertEqual(geometry["routeCollisions"], 0)
                self.assertEqual(geometry["tokenCollisions"], 0)
                self.assertEqual(geometry["headCollisions"], 0)
                if geometry["minimumTokenClearance"] is not None:
                    self.assertGreaterEqual(geometry["minimumTokenClearance"], 2.8)
            page.evaluate("()=>window.renderConceptFrame('compact-scene',7.9)")
            audit = page.evaluate(ARROW_AUDIT, {"selector": "#stage", "canvas": "#f7f7f7"})
            self.assertEqual(audit["headCount"], edges)
            self.assertEqual(audit["issues"], [])
            self.assertEqual(errors, [])
            browser.close()

    def test_loop_and_branch_keep_full_motion_envelope(self):
        with tempfile.TemporaryDirectory(prefix="compact-video-", dir=Path.cwd()) as name:
            folder=Path(name)
            result=self.create(folder, [("sensor","Sensor"),("controller","Controller"),("motor","Motor")],
                               "--feedback", "--branch", "controller=Alarm", "--meaning",
                               'sensor:controller=Measured "sensor" input reaches the controller.')
            self.assertEqual(result.returncode, 0, result.stderr)
            data=json.loads((folder/"scene.json").read_text())
            self.assertEqual(data["interactions"][0]["meaning"], 'Measured "sensor" input reaches the controller.')
            self.inspect(folder, ["Sensor","Controller","Motor","Alarm"], 4)

    def test_two_node_baseline_and_six_node_boundary(self):
        cases=[([("input","Input"),("result","Result")], [], 640, 360),
               ([(f"node-{i}",f"Concept {i}") for i in range(6)],
                ["--feedback","--branch","node-0=Complete wide branch label"],1600,600)]
        for nodes, extra, width, height in cases:
            with self.subTest(nodes=len(nodes)), tempfile.TemporaryDirectory(prefix="compact-video-", dir=Path.cwd()) as name:
                folder=Path(name)
                result=self.create(folder,nodes,*extra,width=width,height=height)
                self.assertEqual(result.returncode,0,result.stderr)
                labels=[label for _,label in nodes]+(["Complete wide branch label"] if extra else [])
                self.inspect(folder,labels,len(nodes)-1+(2 if extra else 0),width,height)

    def test_unreadable_canvas_and_nonfinite_duration_refuse_delivery(self):
        for extra in [[],["--duration","nan"],["--meaning","missing:two=An undeclared relationship."]]:
            with self.subTest(extra=extra), tempfile.TemporaryDirectory(prefix="compact-video-", dir=Path.cwd()) as name:
                folder=Path(name)
                result=self.create(folder,[("one","Complete first concept"),("two","Complete second concept")],
                                   *extra,width=100,height=100)
                self.assertNotEqual(result.returncode,0)
                self.assertTrue(all(not (folder/path).exists() for path in ["scene.json","scene.html","review.json"]))


if __name__ == "__main__":
    unittest.main()
